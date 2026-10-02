"""Governance & Portfolio — see ../../generators/governance-portfolio.md for the full spec.

Updated 2026-10-02: most data sources are now CONFIRMED (model inventory via
`alm_ai_digital_asset`, AI Control Tower reconciliation via
`sn_ai_governance_asset_governance_details`, risks via `sn_risk_risk`) — this
generator is no longer the least automatable of the five. Only audit
findings (`grc_audit`) remains blocked, by a permissions gap rather than a
missing table — see data_sources.QUERY_CATEGORIES["audit_findings"].
"""

from __future__ import annotations

from typing import Any

from .. import data_sources

ACCESS_PENDING = (
    "⚠ Access pending — grc_audit exists but the authenticated user isn't "
    "authorized yet. Requires a GRC Audit role grant, not a different table."
)


def assemble(cached_pull: dict[str, Any]) -> dict[str, Any]:
    """Build the email-section/slide content for this report from a Phase-1 cache.

    `cached_pull` is expected to carry `model_inventory` (alm_ai_digital_asset
    records) and `ai_control_tower` (sn_ai_governance_asset_governance_details
    records, joined on `asset`), plus optionally `audit_findings` if that
    access gap has since been closed.
    """
    assets = cached_pull.get("model_inventory", [])
    governance_details = cached_pull.get("ai_control_tower", [])

    by_asset_sys_id = {g.get("asset"): g for g in governance_details}

    new_models = [a for a in assets if a.get("is_new_this_week")]
    retired_models = [a for a in assets if a.get("asset_state") == "retired" or a.get("install_status") == "Retired"]
    missing_ownership = [a for a in assets if not a.get("managed_by")]

    control_exceptions = [
        g for g in governance_details
        if not g.get("governed") or not g.get("risk_score") or g.get("risk_score") == "To be determined"
    ]

    mismatched_inventory = [
        a for a in assets
        if (g := by_asset_sys_id.get(a.get("sys_id"))) is not None
        and a.get("install_status") == "Deployed"
        and g.get("asset_state") == "retired"
    ]

    return {
        "governance_summary": {
            "total_assets": len(assets),
            "governed_count": sum(1 for g in governance_details if g.get("governed")),
            "control_exceptions_count": len(control_exceptions),
        },
        "inventory_changes": assets,  # caller diffs week-over-week; this generator doesn't own history
        "new_models": new_models,
        "retired_models": retired_models,
        "aict_reconciliation": governance_details,
        "audit_findings": cached_pull.get("audit_findings", ACCESS_PENDING),
        "compliance_status": {
            "governed": [g for g in governance_details if g.get("governed")],
            "not_governed": [g for g in governance_details if not g.get("governed")],
        },
        "control_exceptions": control_exceptions,
        "mismatched_inventory": mismatched_inventory,  # spec requirement: "highlight mismatched inventories"
        "missing_ownership": missing_ownership,  # spec requirement: "flag missing ownership"
        "open_governance_actions": [],  # TODO: wire to defects/risks tagged governance once that convention exists
        "upcoming_reviews": "Not yet sourced — no review-calendar table identified.",
    }
