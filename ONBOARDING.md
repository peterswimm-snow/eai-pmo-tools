# eai-pmo-tools — Onboarding for Product Managers

This repo powers the **SCRM AI/ML Weekly Reporting Suite** for the Enterprise AI RTB program, plus the team's shared operating-model docs (onboarding, portfolio taxonomy, reporting cadence). If you're a PM who needs program visibility, reads or distributes these weekly reports, or wants to understand where the numbers in them come from — this is your starting point.

## What this gives you

Five weekly reports, each aimed at a different audience, generated as `.docx` (email draft) + `.pptx` (deck) pairs:

| Report | For | What's in it |
|---|---|---|
| Executive Dashboard | VP/Enterprise AI Leadership | Portfolio RAG, top-5 risks, decisions needed — business language, no tech detail |
| Leadership Weekly Readout | Program leadership, Accenture Delivery | Widest view: all four workstreams, model health, delivery progress, dependencies |
| Operations & Model Health | Ops teams, model owners, engineering leads | Incidents, defects, defect aging, SLA/Sev1-Sev2 flags |
| **Governance & Portfolio** | Enterprise AI, Governance, PMO | Model inventory, AI Control Tower reconciliation, compliance status, audit findings |
| Core Team Action Report | Core delivery team | Owners, due dates, blockers, grouped by workstream |

Full specs for each (exact sections, slide outlines) live in [`reporting/generators/`](reporting/generators/). You generally won't need to read those day-to-day — they're the implementation detail behind the reports you receive.

## Read a report with the right amount of trust

Not every number in these reports is live ServiceNow data yet. Before you act on a report:

- **Live and confirmed** (as of 2026-10-02): incidents, stories, defects, epics, scrum tasks, change requests, problems, risks, milestones, AI model inventory, and AI Control Tower reconciliation data. These are real, current ServiceNow records.
- **Manual-input placeholders, every week, by design**: DevX's own release/deployment/delivery metrics, and separately, model-performance monitoring metrics (accuracy/precision/recall/retraining). No automated source exists for either yet — if a report shows one of these, it's whatever figure was supplied that week, not a live pull. Don't assume it refreshed itself.
- **Pending access**: Audit Findings in the Governance & Portfolio report is flagged "access pending" until a ServiceNow role request clears (tracked in [`docs/access-requests/`](docs/access-requests/)). Until then, that one section is a placeholder, not a zero.

The full, current breakdown of what's live vs. placeholder is [`reporting/data-sources.md`](reporting/data-sources.md) — if you're ever unsure whether a number is real, that file has the answer.

## The reporting cadence

- **Friday:** written update goes out (Executive Dashboard and/or Leadership Readout, depending on audience).
- **Monday:** Green/Yellow/Red review meeting, using the same reports' RAG status.

Details and open questions (RAG thresholds aren't formally defined yet) are in [`docs/weekly-reporting-cadence.md`](docs/weekly-reporting-cadence.md).

## The portfolio you're reporting on

Four workstreams, each with a ServiceNow anchor — this is the taxonomy every report groups and scopes by:

| Workstream | ServiceNow anchor |
|---|---|
| SalesCRM | STRY2793791, STRY2795373 |
| ML Risk Model for SPM | STRY2793790, STRY2793795, STRY2793796 |
| Enterprise RTB Managed Delivery | PRJ0124654 |
| ML Control Plane (AutoML, Feature Store, replatform) | EARB00013238 and related stories |

Full detail, plus an open question about where Downsell fits, is in [`docs/portfolio-taxonomy.md`](docs/portfolio-taxonomy.md).

## Getting set up

Most PMs don't need to run any code — reports are generated through Claude Code using the `eai-rtb-delivery-control-tower` skill. What you actually need:

1. **GitHub access** to this repo (`peterswimm-snow/eai-pmo-tools`) — read access is enough to browse specs, docs, and past reports; ask for write access if you'll be editing the taxonomy or cadence docs yourself.
2. **Nothing else**, if you're only consuming reports.

If you want to query ServiceNow data yourself (not required for most PMs):
- Install `devx-cli` and authenticate once (`devx-cli auth --add`) — browser-based OAuth under your own ServiceNow account, no separate credential to manage.
- See [`docs/onboarding-checklist.md`](docs/onboarding-checklist.md) for the fuller technical checklist (that one also covers DevEx CLI and M365 Copilot for engineering-side onboarding — most of it isn't PM-relevant, but the DevEx CLI section is if you go this route).

This repo requires 1Password CLI for any credential a tool needs (see the root `README.md`) — but as a report consumer you won't hit this; it only matters if you're contributing code.

## Where to go for more

- [`README.md`](README.md) — repo overview and the 1Password secrets policy
- [`reporting/README.md`](reporting/README.md) — the reporting suite's own index
- [`reporting/data-sources.md`](reporting/data-sources.md) — what's live vs. placeholder, in detail
- [`docs/access-requests/`](docs/access-requests/) — pending ServiceNow access requests and their justifications
- Owner: Peter Lewis Swimm (RTB team) — ask here first if a report looks wrong or a data source you expect isn't showing up.
