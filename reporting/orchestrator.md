# Weekly Reporting Suite — Orchestrator

Runs all five generators in one pass, pulling shared data once instead of once per report. Trigger phrases: "run the weekly reporting suite", "generate all weekly reports".

## Phase 0 — Scope

Confirm with the user (or default if unambiguous):
- Reporting week / as-of date (defaults to today unless the user says otherwise).
- In-scope workstreams — default is **all four** (SalesCRM, ML Risk Model for SPM, Enterprise RTB Managed Delivery, Downsell), per Skill 2's "include all portfolios" requirement.

## Phase 1 — Shared ServiceNow data pull (once)

Pull every category from `data-sources.md` that's used by more than one generator, scoped across all in-scope workstreams, **once**:

| Category | Used by |
|---|---|
| Incidents | Executive Dashboard, Leadership Readout, Ops & Model Health |
| Stories | Leadership Readout, Core Team Action |
| Defects | Executive Dashboard, Leadership Readout, Ops & Model Health, Core Team Action |
| Epics | Leadership Readout, Core Team Action |
| Scrum tasks | Core Team Action |
| Change requests | Ops & Model Health |
| Risks (`sn_risk_risk`, confirmed) | Executive Dashboard, Leadership Readout, Ops & Model Health |
| Milestones (`sn_milestones_milestone`, confirmed) | Executive Dashboard, Leadership Readout, Core Team Action |
| Problems (`problem`, confirmed) | Ops & Model Health |
| Model inventory (`alm_ai_digital_asset`, confirmed) | Governance & Portfolio |
| AI governance details (`sn_ai_governance_asset_governance_details`, confirmed) | Governance & Portfolio |

Cache the raw pulled results as JSON at `Weekly Reports/<date>/_data/raw-pulls.json` (see `output-rendering.md` for the folder convention). Every generator in Phase 3 reads from this cache instead of re-querying ServiceNow — this is the whole point of the orchestrator over running each generator standalone.

As of 2026-10-02 only audit findings (`grc_audit`) remains genuinely blocked — table confirmed to exist but access-denied to the authenticated user (see `data-sources.md`). Record that explicitly in the cache (e.g. `"audit_findings": {"status": "access_denied", "note": "grc_audit exists, needs GRC Audit role"}`) so the Governance & Portfolio generator renders the same access-pending placeholder rather than failing unpredictably.

## Phase 2 — Manual-input collection (once)

Ask the user once per run for whichever permanent-gap categories apply this run:
- DevX release/deployment/engineering-delivery/sprint/repo-activity metrics (needed by Executive Dashboard, Leadership Readout, Ops & Model Health, Core Team Action).
- Model-performance monitoring metrics (needed by Ops & Model Health only).

Share the answers across every report that needs them — do not ask the same question five times.

## Phase 3 — Generate each report

For each generator, in this order (most-automatable first, so failures surface early on the hardest ones rather than blocking everything):
1. Core Team Action Report
2. Ops & Model Health
3. Executive Dashboard
4. Leadership Readout
5. Governance & Portfolio

For each: load its `generator-*.md`, build the email sections and slide content from the Phase 1 cache + Phase 2 manual input, then render per `output-rendering.md` (`.docx` + `.pptx`).

## Phase 4 — Summary to the user

One line per report, never implying more automation than actually happened:
- **Generated** — all data sources resolved.
- **Partially generated (N gaps)** — name which sections are placeholders and why (unverified table vs. manual-input gap).
- **Blocked** — could not produce a meaningful report at all (expected for Governance & Portfolio until AICT/model-inventory tables are identified).
