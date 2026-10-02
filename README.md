# eai-pmo-tools

Tools and reference material for Enterprise AI RTB/SCRM program management — part of the **AI-Assisted Team Operating Model and Workflow Automation** epic (story STRY2795985).

## What's here

| Area | Purpose |
|---|---|
| [`docs/onboarding-checklist.md`](docs/onboarding-checklist.md) | GitHub, DevEx CLI, and Microsoft 365 Copilot setup checklist for new team members (ref. STSK0760136) |
| [`docs/portfolio-taxonomy.md`](docs/portfolio-taxonomy.md) | Shared workstream taxonomy and report-out structure (ref. STSK0760142) |
| [`docs/weekly-reporting-cadence.md`](docs/weekly-reporting-cadence.md) | Friday/Monday reporting cadence and RAG review template (ref. STSK0760141) |
| [`docs/devx-cli-table-discovery.md`](docs/devx-cli-table-discovery.md) | How to find an unknown ServiceNow table/role via `devx-cli` when no dedicated command covers it |
| [`reporting/`](reporting/) | The Weekly Reporting Suite: five report generators (Executive Dashboard, Leadership Readout, Operations & Model Health, Governance & Portfolio, Core Team Action) plus an orchestrator, and the Python starter code that backs them |

## Relationship to the Claude Code skill

The detailed report specs (audience, email sections, slide outlines, data-source mapping) are authored once in [`.claude/skills/eai-rtb-delivery-control-tower/references/`](../.claude/skills/eai-rtb-delivery-control-tower/references/) in the parent workspace, since that's what Claude Code loads when generating a report inside a session. This repo holds:
- The same specs, mirrored under `reporting/generators/`, so they're readable/versionable outside a Claude session and reviewable by the rest of the team.
- Starter Python code (`reporting/src/`) for the parts that don't require a Claude session — pulling and caching ServiceNow data via `devx-cli` — so the reporting pipeline can eventually run standalone (e.g. from a scheduled job), not only interactively.

If you change a generator's spec, update both locations, or point one at the other via a symlink once the team settles on a single source of truth.

## Related ServiceNow records

- Epic: AI-Assisted Team Operating Model and Workflow Automation
- Story: STRY2795985 — Establish the shared AI-assisted team operating model
- Scrum tasks: STSK0760136 (onboarding checklist), STSK0760137 (Amy tool access), STSK0760138 (M365 Copilot license), STSK0760140 (Teams space), STSK0760141 (weekly report template/cadence), STSK0760142 (portfolio taxonomy), STSK0760143 (dashboard consolidation), STSK0760144 (PR-merge-to-ticket automation scoping), STSK0760139 (AI-assisted workflow brown bag)

## Secrets — 1Password CLI required

No tool in this repo may read a plaintext secret from a committed file, a hardcoded value, or an unprotected `.env`. This mirrors the convention already in use in `../Enterprise_RTB/` (see its `run_with_1password.sh`):

- Copy `.env.1password.example` to `.env` and put `op://Vault/Item/field` references in it — never a real value.
- Run anything that needs a secret through `./run_with_1password.sh <command...>`, which resolves those references via the 1Password CLI (`op`) before the command starts.
- `.env` (and any `.env.*` besides the example) is gitignored — if `git status` ever shows one as trackable, stop and check before committing.

**One exception, by necessity, not by choice:** `devx-cli`'s own ServiceNow auth is interactive browser-based OAuth per person (`devx-cli auth --add`) with no env-var injection point, so it can't be routed through this wrapper — see `reporting/src/eai_pmo_tools/devx.py`'s docstring. Every other credential this repo's tools ever need must go through 1Password; as of 2026-10-02 none are needed yet, since the only tool here (the ServiceNow data-pull code) relies entirely on the already-authenticated devx-cli session.

## Status

Starter scaffold — see `reporting/README.md` for what's confirmed-working vs. still a manual-input placeholder in the underlying data sources.
