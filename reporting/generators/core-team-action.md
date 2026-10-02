# Generator: Core Team Action Report

## Audience
Core SCRM AI/ML Delivery Team.

## Trigger phrases
"team action report", "Monday action report", "core team weekly".

## Data pull
The **most automatable generator** — every ServiceNow source is confirmed:
- Stories, Scrum tasks, Defects, Epics → confirmed (`story-list`, `scrum-task-list`, `defect-list`, `epic-agile-list`/`epic-safe-list`).
- Milestones → confirmed, table `sn_milestones_milestone` (verified 2026-10-02).
- DevX sprint metrics / repo activity → **permanent manual-input gap** (the only gap in this report).

Because this is the only generator with zero TBD ServiceNow dependencies, build and test it first — it validates the whole data-pull → render pipeline before tackling the generators with real gaps.

## Email sections (in order, 9 total)
1. This Week's Objectives
2. Open Deliverables — grouped by workstream
3. Assigned Owners — every item must have one, no "unassigned" rows left unflagged
4. Due This Week
5. Blockers
6. Escalations
7. Completed Work
8. Upcoming Milestones — real dates from `sn_milestones_milestone`
9. Meeting Actions

## PPT slides (6)
1. Team Priorities
2. Deliverables Due
3. Blockers
4. Completed Work
5. Upcoming Milestones
6. Action Register

## Requirements (verbatim from spec)
- List the accountable owner for every item (section 3) — flag any item with no assigned owner rather than silently dropping it.
- Flag overdue tasks explicitly (red/bold, not just listed).
- Group by workstream (SalesCRM, ML Risk Model for SPM, Enterprise RTB Managed Delivery, Downsell) throughout, not just in section 2.

## Output naming
`<date>_CoreTeamAction.docx` / `.pptx` — see `output-rendering.md`.

## Known gaps banner
Only one: "⚠ DevX sprint/repo-activity metrics are manual-entry this week — no tool is connected for these." Everything else in this report should be fully live data; if any ServiceNow pull unexpectedly fails, flag it the same way rather than silently omitting.
