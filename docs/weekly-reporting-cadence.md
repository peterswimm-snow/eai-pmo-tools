# Weekly Reporting Cadence

Ref. STSK0760141 ("Define weekly status report template and cadence", under STRY2795985). The templates themselves live in `reporting/generators/`; this doc is just the *schedule and agreement* around them.

## Cadence

- **Friday:** written update distributed (Executive Dashboard and/or Leadership Readout, per audience — see `reporting/README.md`).
- **Monday:** Green/Yellow/Red review meeting, using the RAG status produced by the same reports.

This mirrors the cadence already documented in the Claude Code skill (`eai-rtb-delivery-control-tower/SKILL.md`'s "Weekly Workflow" section: Friday AM health report, Monday project sync, Wednesday defect triage, daily war-room readiness) — keep the two in sync if either changes.

## RAG definition

**Not yet formally defined** — the existing skill references RAG status conceptually (schedule risk, milestone variance) but no explicit Red/Amber/Green thresholds exist yet. Agree and document these before the cadence can run unattended:
- What defect/incident counts or ages push a workstream to Amber or Red?
- What milestone slippage (days) pushes a workstream to Amber or Red?

## Owners

- Report generation: Peter Lewis Swimm (RTB team).
- Monday RAG review facilitation: TBD — confirm with Katy Ramachandran / Mili Merchant per the Leadership Readout audience list.
