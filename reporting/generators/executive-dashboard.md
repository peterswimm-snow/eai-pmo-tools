# Generator: Executive Dashboard

## Audience
Senthil Kumar Venkatachalam, Luke Hagstrand, Enterprise AI Leadership.

## Trigger phrases
"executive dashboard", "exec weekly report", "VP weekly email".

## Data pull
From `data-sources.md` (verified 2026-10-02):
- Incidents, Defects → confirmed (`incident-list`, `defect-list`), scoped to all four workstreams.
- Risks → confirmed, table `sn_risk_risk` via `devx-cli query`.
- Milestones → confirmed, table `sn_milestones_milestone` via `devx-cli query`.
- Stories → confirmed, used only for accomplishments context.
- DevX release/deployment/engineering-delivery metrics → **permanent manual-input gap**, ask once per orchestrator run (or directly if run standalone).

## Email sections (in order)
1. **Executive Summary** — 3–5 sentence portfolio-level narrative, business language only.
2. **Portfolio RAG Status** — one line per workstream (SalesCRM, ML Risk Model for SPM, Enterprise RTB Managed Delivery, Downsell): Red/Amber/Green + one-sentence reason.
3. **Major Accomplishments** — bullet list, this week only, drawn from closed defects/stories and any milestone completions.
4. **Strategic Risks** — **top 5 only**, ranked by severity, from `sn_risk_risk`.
5. **Executive Decisions Needed** — bullet list, decision-oriented phrasing ("Approve X", "Choose between A/B"), not status updates.
6. **Upcoming Milestones** — next 30 days, from `sn_milestones_milestone`.
7. **Leadership Actions** — explicit asks of the named audience, one line each.

## PPT slides
1. Executive Summary
2. Portfolio Health Dashboard (RAG table/chart)
3. Major Accomplishments
4. Strategic Risks (top 5)
5. Executive Decisions Required
6. 30-Day Outlook

## Requirements (verbatim from spec)
- Business language only — eliminate technical detail (no table names, no ServiceNow jargon, no raw metric names).
- Limit strategic risks to top 5.
- Decision-oriented summaries, not status narration.

## Output naming
`<date>_ExecutiveDashboard.docx` / `.pptx` — see `output-rendering.md`.

## Known gaps banner
Risk and milestone tables are confirmed as of 2026-10-02. Only one gap remains: "⚠ DevX delivery metrics are manual-entry this week — no tool is connected." Never omit a section silently if a future schema change breaks one of the confirmed queries — fall back to a placeholder and say so.
