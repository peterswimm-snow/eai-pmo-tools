"""Category -> devx-cli command mapping.

Mirrors ../../data-sources.md. If you change one, change the other — this
module is the executable version of that table, not a separate source of
truth.

Verified 2026-10-02 against the real "surf" instance by querying each
candidate table directly (and searching ServiceNow's own table dictionary,
`sys_db_object`, for names with no known candidate). Most categories are
now CONFIRMED; only audit findings remains blocked, and that's a
permissions gap (`grc_audit` exists, the authenticated user just isn't
authorized to read it yet), not a missing-table problem.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from . import devx


class Status(Enum):
    CONFIRMED = "confirmed"
    ACCESS_DENIED = "access_denied"  # table is real; authenticated user lacks the role
    UNVERIFIED_TABLE = "unverified_table"
    NO_CANDIDATE_TABLE = "no_candidate_table"
    MANUAL_INPUT_ONLY = "manual_input_only"


@dataclass(frozen=True)
class Category:
    name: str
    status: Status
    note: str = ""
    table: str | None = None


# Confirmed, reliable devx-cli *-list commands.
CONFIRMED_COMMANDS = {
    "incidents": "incident",
    "stories": "story",
    "defects": "defect",
    "epics_agile": "epic-agile",
    "epics_safe": "epic-safe",
    "features": "feature",
    "scrum_tasks": "scrum-task",
}

# Reachable via the generic `query` passthrough. Status reflects what was
# actually observed on 2026-10-02 via `devx-cli query --table <name> --limit 1`
# (and sys_db_object searches for anything with no known candidate) — not a
# guess.
QUERY_CATEGORIES = {
    "change_requests": Category(
        "change_requests", Status.CONFIRMED,
        "Full real records returned (e.g. CHG0542211)",
        table="change_request",
    ),
    "problems": Category(
        "problems", Status.CONFIRMED,
        "Real records returned (e.g. PRB0104539)",
        table="problem",
    ),
    "risks": Category(
        "risks", Status.CONFIRMED,
        "Real records returned (e.g. RK0025664). pm_risk is invalid, do not use.",
        table="sn_risk_risk",
    ),
    "milestones": Category(
        "milestones", Status.CONFIRMED,
        "Real records returned (e.g. MS010931). pm_project_milestone and "
        "sn_safe_milestone are invalid, do not use.",
        table="sn_milestones_milestone",
    ),
    "model_inventory": Category(
        "model_inventory", Status.CONFIRMED,
        "Real, rich data: AI Dataset/AI System Digital Asset subclasses, "
        "model/vendor/install_status fields.",
        table="alm_ai_digital_asset",
    ),
    "ai_control_tower": Category(
        "ai_control_tower", Status.CONFIRMED,
        "Real data: risk_score, asset_state, governed flag, lifecycle_phase, "
        "references alm_ai_digital_asset via `asset`. NOT the sn_aict_trace_coll_* "
        "tables — those are an unrelated trace-collector/observability app "
        "despite the similar-looking 'aict' prefix.",
        table="sn_ai_governance_asset_governance_details",
    ),
    "audit_findings": Category(
        "audit_findings", Status.ACCESS_DENIED,
        "Table is real (GRC Audit Management is installed) but devx-cli query "
        "returns 'User Not Authorized' for whichever account devx-cli is "
        "authenticated as (run `devx-cli whoami` to check -- devx-cli "
        "authenticates as the individual user running it, not a shared "
        "service account, so this must be requested per-person). Requested "
        "role: sn_audit.internal_grc_read (fallback: sn_grc.reader) -- see "
        "data-sources.md 'Which role to request'. Re-verify once granted; "
        "this is not a missing-table issue.",
        table="grc_audit",
    ),
}

# No tool or passthrough exists for these anywhere. Permanent manual-input
# placeholders, not a "find the right tool" gap.
MANUAL_ONLY_CATEGORIES = {
    "devx_delivery_metrics": Category(
        "devx_delivery_metrics",
        Status.MANUAL_INPUT_ONLY,
        "DevX release/deployment/engineering-delivery/sprint/repo-activity metrics; no tool exists",
    ),
    "model_monitoring_metrics": Category(
        "model_monitoring_metrics",
        Status.MANUAL_INPUT_ONLY,
        "Model accuracy/precision/recall/retraining; distinct from devx_delivery_metrics, no tool exists",
    ),
}


def pull_confirmed(category: str, story: str | None = None, limit: int = 50):
    """Pull a confirmed category (incidents/stories/defects/epics/features/scrum_tasks)."""
    if category not in CONFIRMED_COMMANDS:
        raise ValueError(
            f"{category!r} is not a confirmed category — see QUERY_CATEGORIES "
            "or MANUAL_ONLY_CATEGORIES, and data-sources.md for why."
        )
    return devx.list_records(CONFIRMED_COMMANDS[category], story=story, limit=limit)


def pull_via_query(category: str, encoded_query: str | None = None, limit: int = 50):
    """Attempt a QUERY_CATEGORIES pull.

    Raises clearly rather than letting a confusing devx-cli error bubble up:
    - NO_CANDIDATE_TABLE / no table: run the discovery procedure first.
    - ACCESS_DENIED: the table is real — this needs a role grant, not a
      different table name. Calling devx-cli anyway would just reproduce
      the same "User Not Authorized" error less helpfully.
    - UNVERIFIED_TABLE: warns before calling, since the table name hasn't
      been confirmed against real data yet.
    """
    cat = QUERY_CATEGORIES.get(category)
    if cat is None:
        raise ValueError(f"{category!r} is not a query-passthrough category.")
    if cat.status is Status.NO_CANDIDATE_TABLE or cat.table is None:
        raise ValueError(
            f"{category!r} has no candidate table identified yet ({cat.note}). "
            "Run the discovery procedure in data-sources.md before calling this."
        )
    if cat.status is Status.ACCESS_DENIED:
        raise PermissionError(
            f"{category!r} (table {cat.table!r}) is access-denied for the current "
            f"authenticated user: {cat.note}"
        )
    if cat.status is Status.UNVERIFIED_TABLE:
        import warnings

        warnings.warn(
            f"{category!r} uses an unverified table ({cat.table!r}; {cat.note}). "
            f"Confirm with `devx-cli query --table {cat.table} --limit 1` before trusting results.",
            stacklevel=2,
        )
    return devx.query_table(cat.table, encoded_query=encoded_query, limit=limit)
