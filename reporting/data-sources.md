# Weekly Reporting Suite — Data Sources

Single source of truth for "which tool pulls which category." Every generator reference and the orchestrator point here instead of re-deriving this mapping — when status changes, update it **only here**.

**Verified 2026-10-02** against the real "surf" ServiceNow instance via `devx-cli`. Verification method: `devx-cli query --table <candidate> --limit 1` (and `devx-cli query --table sys_db_object --query "nameLIKE<keyword>"` to search the table dictionary for candidates with no known name). A result of real records means confirmed; `✗ Invalid table` means the name is wrong; `✗ User Not Authorized` means the table is real but the current authenticated user lacks the role to read it — a permissions gap, not a missing-table gap, and worth escalating separately.

## Confirmed and reliable — record-list tools

| Category | Tool | Notes |
|---|---|---|
| Incidents | `incident-list` | devx-cli-backed, real "surf" instance |
| Stories | `story-list` | |
| Defects | `defect-list` | |
| Epics (Agile tier) | `epic-agile-list` | Verify which tier (Agile vs. SAFe) this program actually uses before assuming — check a known epic number first |
| Epics (SAFe tier) | `epic-safe-list` | |
| Features (SAFe) | `feature-list` | Only relevant where SAFe features exist in-scope |
| Scrum tasks | `scrum-task-list` | |

**Workstream scoping:** filter/tag results using the anchors in `PROJECT_PORTFOLIO.md`:
- SalesCRM → `STRY2793791`, `STRY2795373`
- ML Risk Model for SPM → `STRY2793790`, `STRY2793795`, `STRY2793796`
- Enterprise RTB Managed Delivery → `PRJ0124654`
- ML Control Plane (AutoML/Feature Store/replatform) → `EARB00013238` and related stories

## Confirmed and reliable — `devx-cli query` passthrough

`devx-cli query --table <table> --query <encoded_query> --fields <comma-separated> --limit <n>` is the real command (confirmed via `devx-cli query --help`); there is no `dev:table-schema-get` or `dev:global-file-search` command on this instance despite earlier assumptions — table discovery was instead done by querying `sys_db_object` (ServiceNow's own table dictionary) with `nameLIKE<keyword>`.

| Category | Table | Notes |
|---|---|---|
| Change requests | `change_request` | Full real records returned (e.g. `CHG0542211`) |
| Problems | `problem` | Real records returned (e.g. `PRB0104539`) |
| Risks | `sn_risk_risk` | Real records returned (e.g. `RK0025664`). `pm_risk` is **invalid** — do not use |
| Milestones | `sn_milestones_milestone` | Real records returned (e.g. `MS010931`). `pm_project_milestone` and `sn_safe_milestone` are **invalid** — do not use. `project_key_milestone_baseline` also returns real data but looks like PPM task-baseline records, not milestones proper — prefer `sn_milestones_milestone` |
| Model inventory | `alm_ai_digital_asset` | Real, rich data: subclasses "AI Dataset Digital Asset" / "AI System Digital Asset" (`sys_class_name`), with `model` (ref. `cmdb_model`), `model_category` (e.g. "Generative AI", "AI dataset"), `vendor`, `managed_by`, `install_status` (Deployed/Cancelled), `display_name`, `asset_tag`. This is the real model/AI-asset inventory — not a guess |
| AI Control Tower reconciliation / governance details | `sn_ai_governance_asset_governance_details` | Real data: `risk_score`, `asset_state` (e.g. "Retired"), `asset_status`, `governed` flag, `lifecycle_phase` (ref. `sn_ai_governance_lifecycle`), `asset` (ref. `alm_ai_digital_asset`) — this is the actual reconciliation/compliance-detail record per AI asset |
| AI governance lifecycle stages (supporting lookup) | `sn_ai_governance_lifecycle` | Real picklist-style table: Assess, Build, Build and test, Pre-deploy, Deploy, Offboard, Pre-offboarding, Assess offboarding, New |

**Important naming trap:** there is a *separate* real scoped app with tables prefixed `sn_aict_trace_coll_*` ("AICT" = AI trace-collector configuration for Azure/AWS/GCP observability, e.g. `sn_aict_trace_coll_collector_config`). This is **not** the "AI Control Tower" the report spec means — it's telemetry/tracing config, unrelated to model inventory or compliance reconciliation. Use `sn_ai_governance_*` + `alm_ai_digital_asset` for the Governance & Portfolio report, not anything prefixed `sn_aict_`.

## Confirmed to exist, but access-denied — and to whom

`devx-cli whoami` confirms `devx-cli` authenticates as **Peter Lewis Swimm's own ServiceNow account** on "surf" — there is no separate service/integration account in play. So "request access" below means requesting a role on Peter's own account, not provisioning a service account.

| Category | Table | Notes |
|---|---|---|
| Audit findings | `grc_audit` | Table is real (GRC Audit Management is installed) but `devx-cli query` returns `✗ User Not Authorized` for Peter's account. No distinct child "finding" table was identified (search for `*audit_finding*` and `*finding*` in `sys_db_object` found nothing specific to GRC); findings may live as related child records once access is granted. This is a role gap, not a missing-table problem |
| AI asset instance (alt. parent record to governance details) | `sn_ai_governance_asset_instance` | Same symptom — real table, `✗ User Not Authorized`. The governed-details table above (`sn_ai_governance_asset_governance_details`) is accessible and already carries most of what's needed, so this is a nice-to-have, not a blocker |

### Which role to request

`sys_security_acl` itself is access-denied to Peter's account too, so the exact ACL-to-role mapping for `grc_audit` couldn't be read directly. Instead, searched `sys_user_role` for candidate roles (`nameLIKEaudit`, `nameLIKEgrc`) and found real roles on this instance:

| Role | Description (from the instance) | Fit |
|---|---|---|
| `sn_audit.internal_grc_read` | (no description set) | **Best candidate** — scoped to the `sn_audit` app (GRC Audit Management, which owns `grc_audit`) and named specifically for internal GRC read access. Request this first. |
| `sn_grc.reader` | "Provides read rights to the GRC suite of applications and modules." | Broader fallback if the role above turns out not to cover `grc_audit` specifically — grants read across the whole GRC suite, which is more than strictly needed |
| `grc_audit_reviewer` | "Technical role providing read only access to review audit and associated control test instances assigned to the user." | Narrower — only covers audits *assigned to* the requesting user, which may be too restrictive for pulling all audits program-wide |
| `sn_grc_ai_gov.ai_risk_and_compliance_reader` | "AI Risk and Compliance Reader" | Worth requesting alongside the above since it's scoped specifically to AI risk/compliance — may also widen access to `sn_ai_governance_asset_instance` (the other access-denied table) |

**How to actually get it granted:** this isn't something `devx-cli` or Claude can do — role assignment is a ServiceNow admin/security action on Peter's own user record (`sys_user_has_role`). Request it the way this org normally handles ServiceNow access — a Service Catalog "request access"/role-request item if "surf" has one, or directly asking whoever administers roles on "surf" — naming `sn_audit.internal_grc_read` as the specific ask (with `sn_grc.reader` as the fallback if that doesn't cover it).

**Once granted:** re-run `devx-cli query --table grc_audit --fields "sys_id" --limit 1` to confirm. If it returns real records instead of `✗ User Not Authorized`, flip `audit_findings` from `ACCESS_DENIED`/"access-denied" to `CONFIRMED` in this file, `data_sources.py`, `generator-governance-portfolio.md`, and `SKILL.md` — all four currently say access-denied and all four need updating together, the same discipline used when the other tables flipped from unverified to confirmed on 2026-10-02.

### Discovery procedure for any future unknown table

1. `devx-cli commands --refresh` then `devx-cli query --help` — confirm the generic `query` command's real flags. Never hardcode flags from memory; they loaded differently than the earlier plan assumed.
2. `devx-cli query --table sys_db_object --query "nameLIKE<keyword>" --fields "name,label" --limit 20` — searches ServiceNow's own table dictionary by keyword. This is how every table above was actually found; there is no `dev:table-schema-get` command on this instance.
3. `devx-cli query --table <candidate> --fields "sys_id" --limit 1` — cheap existence/access check. `✗ Invalid table` = wrong name, try another candidate. `✗ User Not Authorized` = real table, permissions gap — escalate for a role, don't keep guessing names. A real JSON result = confirmed.
4. Record the result back into this file's tables above — this file is the single place that stops being "TBD" as each table is verified.
5. Any category still unresolved (wrong name with no better candidate found, or access denied with no role granted yet) renders as an explicit placeholder in the affected report — never a fabricated or silently empty section.

## Not automatable — permanent manual-input gaps

Not a "find the right tool" problem — no passthrough or tool exists for either, anywhere in this workspace.

| Category | Used by | Notes |
|---|---|---|
| DevX release/deployment/engineering-delivery/sprint/repo-activity metrics | Executive Dashboard, Leadership Readout, Ops & Model Health, Core Team Action | `devx-cli`'s `query` command is scoped to ServiceNow tables only — it has no equivalent for DevX's own metrics system. Ask the user for current figures once per orchestrator run and reuse across reports. |
| Model-performance monitoring metrics (accuracy, precision, recall, retraining activity) | Ops & Model Health | Distinct from the DevX gap above — do not conflate the two. No monitoring-system tool found in this workspace. |

## servicenow-mcp (alternative, currently broken)

`servicenow-mcp` (the local fork) separately exposes `list_incidents`, `list_stories`, `list_epics`, `list_scrum_tasks`, `list_change_requests`, `list_projects` — overlapping with the devx-cli tools above. Its OAuth is currently returning 401 Unauthorized. Do not route new weekly-reporting work through it until that's fixed; `devx-cli` is the reliable path for everything in this suite.
