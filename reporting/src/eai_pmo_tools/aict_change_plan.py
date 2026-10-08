"""Offline AICT owner-change plans; never perform remote reads or writes."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import shlex
import sys
from typing import Any


TRUSTED_INSTANCE = "https://surf.service-now.com"
ASSET_TABLE = "alm_ai_system_digital_asset"
OWNER_FIELDS = frozenset({"u_business_owner", "u_technical_owner"})


class PlanError(ValueError):
    """The supplied evidence cannot safely support a change plan."""


def _object(value: Any, required: set[str], optional: set[str] | None = None) -> dict:
    if not isinstance(value, dict):
        raise PlanError("Expected a JSON object")
    if not required <= value.keys() or value.keys() - required - (optional or set()):
        raise PlanError("Missing required keys or unknown keys")
    return value


def _sys_id(value: Any) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-fA-F]{32}", value) is None:
        raise PlanError("Expected a nonempty 32-hex sys_id")
    return value.lower()


def _text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 4096:
        raise PlanError("Expected nonempty text of at most 4096 characters")
    if any(ord(character) < 32 for character in value):
        raise PlanError("Control characters are not allowed")
    return value


def validate_baseline(request: dict) -> dict[str, str]:
    """Compare caller-provided raw snapshots and opaque freshness markers."""
    if request.get("instance_url") != TRUSTED_INSTANCE:
        raise PlanError("Instance must exactly match the trusted HTTPS origin")
    if request.get("table") != ASSET_TABLE:
        raise PlanError("Only the AI system digital asset table is allowed")
    asset_id = _sys_id(request.get("asset_sys_id"))
    governance_id = request.get("governance_sys_id")
    if governance_id is not None and _sys_id(governance_id) == asset_id:
        raise PlanError("Asset and governance sys_ids must be distinct")
    freshness = _object(request.get("freshness"), {"expected", "observed"})
    if _text(freshness["expected"]) != _text(freshness["observed"]):
        raise PlanError("Freshness marker changed; re-read and rebuild the plan")
    snapshots = []
    for name in ("baseline", "current"):
        snapshot = request.get(name)
        if not isinstance(snapshot, dict) or not snapshot or snapshot.keys() - OWNER_FIELDS:
            raise PlanError("Snapshots require only allowlisted owner fields")
        snapshots.append({field: _sys_id(value) for field, value in snapshot.items()})
    if snapshots[0] != snapshots[1]:
        raise PlanError("Baseline changed; re-read and rebuild the plan")
    return snapshots[0]


def _evidence(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PlanError("Evidence must be a nonempty list of source descriptions")
    return [_text(item) for item in value]


def build_plan(request: Any) -> dict[str, Any]:
    """Build a human handoff from supplied evidence, without validating it live."""
    request = _object(
        request,
        {"instance_url", "table", "asset_sys_id", "freshness", "baseline", "current",
         "changes", "conflicts"},
        {"governance_sys_id"},
    )
    baseline = validate_baseline(request)
    if not isinstance(request["conflicts"], list):
        raise PlanError("Conflicts must be a list; use an empty list if none are known")
    conflicts = [_text(item) for item in request["conflicts"]]
    if not isinstance(request["changes"], list) or not request["changes"]:
        raise PlanError("At least one change is required")
    changes = []
    seen_fields = set()
    for supplied_change in request["changes"]:
        change = _object(
            supplied_change,
            {"field", "old_sys_id", "new_sys_id", "proposal_role", "evidence",
             "candidate_mapping"},
            {"identity_validation"},
        )
        field = change["field"]
        if not isinstance(field, str) or field not in OWNER_FIELDS or field in seen_fields:
            raise PlanError("Owner field is not allowlisted or is duplicated")
        seen_fields.add(field)
        old_id, new_id = _sys_id(change["old_sys_id"]), _sys_id(change["new_sys_id"])
        if baseline.get(field) != old_id:
            raise PlanError("Old owner does not match the supplied baseline")
        if old_id == new_id:
            raise PlanError("No-op changes are not change proposals")
        if change["proposal_role"] not in ("requested", "validated"):
            raise PlanError("Proposal role must be requested or validated")
        if not isinstance(change["candidate_mapping"], list):
            raise PlanError("Candidate mapping must be a list")
        candidates = []
        for supplied_candidate in change["candidate_mapping"]:
            candidate = _object(supplied_candidate, {"employee_sys_id", "evidence"})
            candidates.append({
                "employee_sys_id": _sys_id(candidate["employee_sys_id"]),
                "evidence": _evidence(candidate["evidence"]),
                "requires_identity_validation": True,
            })
        identity = None
        if "identity_validation" in change:
            supplied_identity = _object(
                change["identity_validation"],
                {"table", "employee_sys_id", "match_count", "evidence"},
            )
            if supplied_identity["table"] != "u_employee":
                raise PlanError("Owner references must resolve against u_employee")
            if (type(supplied_identity["match_count"]) is not int
                    or supplied_identity["match_count"] != 1):
                raise PlanError("Identity lookup must have exactly one employee match")
            if _sys_id(supplied_identity["employee_sys_id"]) != new_id:
                raise PlanError("Identity evidence must identify the proposed new owner")
            identity = {
                "table": "u_employee", "employee_sys_id": new_id, "match_count": 1,
                "evidence": _evidence(supplied_identity["evidence"]),
                "basis": "caller_supplied_not_live_verified",
            }
        if change["proposal_role"] == "validated" and identity is None:
            raise PlanError("Validated proposals require unique u_employee evidence")
        changes.append({
            "field": field, "reference_table": "u_employee",
            "before": old_id, "after": new_id,
            "proposal_role": change["proposal_role"],
            "requires_identity_validation": change["proposal_role"] == "requested",
            "evidence": _evidence(change["evidence"]),
            "candidate_mapping": candidates, "identity_validation": identity,
        })
    pending = any(change["requires_identity_validation"] for change in changes)
    readiness = ("blocked_by_conflicts" if conflicts else
                 "requires_identity_validation" if pending else "ready_for_human_review")
    asset_id = _sys_id(request["asset_sys_id"])
    fields = ",".join(["sys_id", "sys_updated_on", *sorted(seen_fields)])
    query = shlex.join([
        "devx-cli", "query", "--table", ASSET_TABLE, "--query", f"sys_id={asset_id}",
        "--fields", fields, "--limit", "1", "--display-value", "False",
    ])
    employee_queries = [shlex.join([
        "devx-cli", "query", "--table", "u_employee", "--query",
        f"sys_id={change['after']}", "--fields", "sys_id", "--limit", "2",
        "--display-value", "False",
    ]) for change in changes]
    return {
        "schema_version": 1,
        "mode": "offline_human_save_only",
        "instance_url": TRUSTED_INSTANCE,
        "target": {"table": ASSET_TABLE, "asset_sys_id": asset_id},
        "governance_sys_id": (_sys_id(request["governance_sys_id"])
                              if request.get("governance_sys_id") is not None else None),
        "governance_id_is_not_update_target": True,
        "record_url": f"{TRUSTED_INSTANCE}/{ASSET_TABLE}.do?sys_id={asset_id}",
        "freshness": deepcopy(request["freshness"]),
        "freshness_basis": "caller_supplied_marker_equality_not_live_recency",
        "baseline": baseline,
        "changes": changes,
        "conflicts": conflicts,
        "readiness": readiness,
        "owner_implies_vp_plus": False,
        "handoff": {
            "browser_inspect": "Confirm instance, asset table and sys_id; inspect live locators. "
                               "Do not treat governance IDs or cached selectors as asset identity.",
            "before_prefill": "Re-read raw owners and freshness marker immediately before filling; "
                              "stop on drift, conflicts, ambiguity, or missing permission.",
            "browser_prefill": "Only on an explicit fill request and after identity validation; "
                               "use live reference controls to select the unique u_employee. "
                               "Stop if reference resolution fails or the form auto-saves.",
            "human_save": "Human reviews and clicks Save/Update. Assistant never saves, submits, "
                          "presses a submit shortcut, or issues network writes.",
            "devx_verification": "After the human confirms saving, check devx-cli whoami for the "
                                 "exact trusted instance, then run only the read-only queries "
                                 "below; compare raw sys_ids to every after value. Report "
                                 "mismatches or denied reads, not assumed success.",
            "authentication": "User enters secrets directly in their own authentication UI; "
                              "never pass credentials to the assistant or this helper.",
            "read_only_commands": ["devx-cli whoami", query, *employee_queries],
        },
        "limitations": [
            "No live lookup, freshness check, browser inspection, prefill, save, or verification executed.",
            "Validated means caller supplied unique employee evidence, not independent verification.",
            "Candidate mappings remain unvalidated evidence; never automatically promote a candidate.",
            "Owner references do not establish VP+ status, approval authority, or governance ownership.",
            "Only nonempty old/new owner references are supported; clearing owners is not supported.",
        ],
    }


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise PlanError("Duplicate JSON keys are not allowed")
        result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path, help="Input JSON request file")
    parser.add_argument("--output", required=True, type=Path, help="New JSON output file; never overwrite")
    args = parser.parse_args(argv)
    try:
        if args.request.resolve() == args.output.resolve():
            raise PlanError("Output cannot be the source request")
        if args.output.exists() or args.output.is_symlink():
            raise PlanError("Output already exists; choose a new path")
        request = json.loads(args.request.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        rendered = json.dumps(build_plan(request), indent=2, ensure_ascii=True) + "\n"
        with args.output.open("x", encoding="utf-8") as output:
            output.write(rendered)
    except PlanError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    except (OSError, ValueError, RecursionError):
        print(json.dumps({"error": "Cannot read request or create a valid new output file"}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())