# Weekly Reporting Suite

Five report generators plus an orchestrator, producing `.docx` email drafts and `.pptx` decks for the SCRM AI/ML program from ServiceNow (`devx-cli`) and DevX data.

These specs are mirrored from `.claude/skills/eai-rtb-delivery-control-tower/references/` in the parent workspace — that's the canonical copy Claude Code loads in-session. Keep both in sync, or replace one with a symlink once the team settles on a single source of truth.

## Generators

| Generator | Audience | Spec |
|---|---|---|
| Executive Dashboard | Senthil Kumar Venkatachalam, Luke Hagstrand, Enterprise AI Leadership | [`generators/executive-dashboard.md`](generators/executive-dashboard.md) |
| Leadership Weekly Readout | Katy Ramachandran, Mili Merchant, Accenture Delivery Leadership, Enterprise AI Leadership, Program Management | [`generators/leadership-readout.md`](generators/leadership-readout.md) |
| Operations & Model Health | Operations Teams, Model Owners, Engineering Leads | [`generators/ops-model-health.md`](generators/ops-model-health.md) |
| Governance & Portfolio | Enterprise AI, Governance, PMO | [`generators/governance-portfolio.md`](generators/governance-portfolio.md) |
| Core Team Action Report | Core SCRM AI/ML Delivery Team | [`generators/core-team-action.md`](generators/core-team-action.md) |

[`orchestrator.md`](orchestrator.md) runs all five in one pass, pulling shared ServiceNow data once. [`data-sources.md`](data-sources.md) is the single table mapping every data category to a tool and a confirmed/TBD status — **read this before trusting any generator's output**, since several categories (risks, milestones, problems, AI Control Tower, model inventory, audit findings) are unverified, and DevX's own delivery/metrics data plus model-monitoring metrics have no tooling at all and must stay manual-input placeholders.

## What's actually runnable today vs. not

**Verified 2026-10-02 against the real "surf" instance** — see `data-sources.md` for the full method and results.

- **Confirmed and automatable:** incidents, stories, defects, epics, scrum tasks via `devx-cli`'s record-list commands, plus — via the generic `devx-cli query` passthrough — change requests (`change_request`), problems (`problem`), risks (`sn_risk_risk`), milestones (`sn_milestones_milestone`), model inventory (`alm_ai_digital_asset`), and AI Control Tower reconciliation (`sn_ai_governance_asset_governance_details`). See `src/eai_pmo_tools/` for the starter wrapper.
- **Blocked by permissions, not missing:** audit findings (`grc_audit`) — the table is real (GRC Audit Management is installed) but the authenticated user gets `User Not Authorized`. Needs a role grant, not a different table name.
- **Not automatable at all today:** DevX's own release/deployment/engineering-delivery/sprint/repo-activity metrics, and model-performance monitoring metrics. No connector exists for either.
- **Rendering `.docx`/`.pptx`:** inside a Claude Code session, done via the `docx`/`pptx` skills (see [`output-rendering.md`](output-rendering.md)). The standalone Python code in `src/` only covers the data-pull/cache side for now — it does not render documents (see `src/eai_pmo_tools/render.py`'s docstring for why, and what it would take to add that).

## Starter code (`src/eai_pmo_tools/`)

```
src/eai_pmo_tools/
├── __init__.py
├── devx.py            # subprocess wrapper around devx-cli, returns parsed JSON
├── data_sources.py     # category -> devx-cli command mapping, mirrors data-sources.md
├── cache.py            # writes/reads the Phase-1 shared-pull cache (raw-pulls.json)
├── render.py           # NOT YET IMPLEMENTED — see docstring
└── generators/          # one thin module per generator, each just assembling
                         # cached data into the section structure its .md spec defines
```

Run `pytest` from the repo root to run the starter tests in `tests/`.
