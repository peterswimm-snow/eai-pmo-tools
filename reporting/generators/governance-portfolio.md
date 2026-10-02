# Generator: Governance & Portfolio

## Audience
Enterprise AI, Governance, PMO.

## Trigger phrases
"governance report", "AICT reconciliation", "portfolio governance weekly".

## Data pull
From `data-sources.md` — **updated 2026-10-02: most sources are now confirmed, with one real access-permission gap remaining:**
- Model inventory → **confirmed**, table `alm_ai_digital_asset` (rich real data: AI Dataset/AI System Digital Asset subclasses, model/vendor/install-status fields).
- AI Control Tower reconciliation data → **confirmed**, table `sn_ai_governance_asset_governance_details` (risk_score, asset_state, lifecycle_phase, governed flag, references `alm_ai_digital_asset`). **Do not confuse this with `sn_aict_trace_coll_*`** — that's an unrelated trace-collector/observability app with a similar-looking prefix.
- Audit findings → table `grc_audit` is real (GRC Audit Management is installed) but currently returns `✗ User Not Authorized` for Peter's own ServiceNow account (confirmed via `devx-cli whoami` — there's no separate service account). **This is a role gap, not a missing table.** Request the `sn_audit.internal_grc_read` role (fallback: `sn_grc.reader`) — see `data-sources.md`'s "Which role to request" section for how that candidate was identified and the full fallback list. Until granted, render this section as an access-pending placeholder, not a fabricated one.
- ServiceNow Portfolio/Risk data → risks are confirmed, table `sn_risk_risk`.

Only audit findings remains genuinely blocked; everything else in this report can now pull real data.

## Email sections (in order, 10 total)
1. Governance Summary
2. Inventory Changes — from `alm_ai_digital_asset` (compare install_status/asset_state week over week)
3. New Models — `alm_ai_digital_asset` records created this week
4. Retired Models — `alm_ai_digital_asset` records with `asset_state` = Retired this week
5. AICT Reconciliation — from `sn_ai_governance_asset_governance_details` (governed flag, risk_score, lifecycle_phase vs. `asset_state`)
6. Audit Findings — **placeholder: access pending** on `grc_audit` until the GRC Audit role is granted
7. Compliance Status — derived from `sn_ai_governance_asset_governance_details`'s `governed`/`risk_score`/`asset_status` fields
8. Control Exceptions — assets where `governed` is false or `risk_score` is high
9. Open Governance Actions — can draw from confirmed risk/defect data where relevant
10. Upcoming Reviews — placeholder until a review-calendar source is identified (not yet searched)

## PPT slides (7)
1. Governance Summary
2. Inventory Health
3. AICT Alignment
4. Compliance Status
5. Audit Readiness
6. Control Exceptions
7. Governance Roadmap

## Requirements (verbatim from spec)
- Highlight mismatched inventories — compare `alm_ai_digital_asset.install_status` against `sn_ai_governance_asset_governance_details.asset_state`/`governed` for the same `asset` reference.
- Flag missing ownership — `alm_ai_digital_asset.managed_by` empty.
- Flag compliance gaps — `governed` = false or missing `risk_score` in `sn_ai_governance_asset_governance_details`.

## Output naming
`<date>_GovernancePortfolio.docx` / `.pptx` — see `output-rendering.md`.

## Known gaps banner
"⚠ Audit Findings (section 6) is pending ServiceNow access — `grc_audit` exists but Peter's own account isn't authorized yet (role requested: `sn_audit.internal_grc_read`). Everything else in this report is live data as of 2026-10-02." This replaces the earlier "almost nothing is automatable" banner — don't carry that stale framing forward.
