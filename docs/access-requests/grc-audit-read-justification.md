# Access Request: GRC Audit Read Role

**Requestor:** Peter Lewis Swimm
**Team:** RTB team (Enterprise AI)
**Instance:** surf (surf.service-now.com)
**Role requested:** `sn_audit.internal_grc_read` (read-only)
**Fallback if insufficient:** `sn_grc.reader` (broader GRC-suite read-only role)

## Business justification

The Enterprise AI RTB/SCRM program is standing up a **Weekly Reporting Suite** — five automated status reports (Executive Dashboard, Leadership Readout, Operations & Model Health, **Governance & Portfolio**, Core Team Action) distributed to program leadership, Enterprise AI, Governance, and PMO stakeholders. This work is tracked under the "AI-Assisted Team Operating Model and Workflow Automation" epic (story STRY2795985, scrum task STSK0760141 — "Define weekly status report template and cadence").

The **Governance & Portfolio report** is required to include an Audit Findings section (compliance status, control exceptions, audit readiness) alongside AI model inventory and AI Control Tower reconciliation data, which are already accessible. The underlying ServiceNow table for this section, `grc_audit`, currently returns `User Not Authorized` for the requestor's account — GRC Audit Management is installed on this instance, but no read role is currently assigned.

**What's being requested:** read-only access to query `grc_audit` programmatically (via `devx-cli`, an internal ServiceNow dev-workflow CLI) so this table's data can be pulled into the weekly Governance & Portfolio report, the same way incidents, defects, stories, risks, and milestones already are for the other four reports in this suite.

**Why this specific role:** `sn_audit.internal_grc_read` is scoped to the `sn_audit` application (GRC Audit Management, which owns the `grc_audit` table) and is named specifically for internal GRC read access — the narrowest fit identified. `sn_grc.reader` is listed only as a fallback, since it grants read access across the entire GRC suite rather than just Audit Management, and should only be used if the narrower role doesn't cover `grc_audit`.

**Scope and limits:**
- Read-only. No create, update, or delete access is requested or required.
- No elevated GRC roles (e.g. `grc_audit_owner`, `sn_grc.compliance_assurance_manager`) are requested — this is reporting/visibility only, not audit management or case ownership.
- Access is for automated weekly reporting, not ad hoc individual record access.

**Impact if not granted:** the Governance & Portfolio report's Audit Findings section ships as an explicit "access pending" placeholder rather than live data — reducing the report's value to Governance and PMO stakeholders but not blocking the rest of the suite, which is otherwise fully automated as of 2026-10-02.

## Reference

- Epic: AI-Assisted Team Operating Model and Workflow Automation
- Story: STRY2795985
- Related scrum task: STSK0760141 (weekly status report template and cadence)
- Technical detail: `reporting/data-sources.md` in this repo, "Which role to request" section
