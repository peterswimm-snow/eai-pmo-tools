# Generator: Leadership Weekly Readout

## Audience
Katy Ramachandran, Mili Merchant, Accenture Delivery Leadership, Enterprise AI Leadership, Program Management.

## Trigger phrases
"leadership readout", "leadership weekly update", "master weekly report".

## Data pull
Widest pull of the five generators — from `data-sources.md` (verified 2026-10-02):
- Incidents, Stories, Defects, Epics (Agile + SAFe) → confirmed.
- Risks → confirmed, table `sn_risk_risk`.
- Milestones → confirmed, table `sn_milestones_milestone`.
- DevX repos/release/delivery/deployment history → **permanent manual-input gap**.

Scope across **all four workstreams** per the "include all portfolios" requirement — do not narrow to a subset without the user asking.

## Email sections (in order, 11 total)
1. Executive Summary
2. Portfolio Health — per-workstream RAG + brief status, all four
3. Model Health Summary — acceptance status per model (from Core Responsibility #2's acceptance-criteria tracking in the main SKILL.md, not a separate pull)
4. Delivery Progress — stories/epics completed vs. planned this week
5. Defects and Incident Summary — counts, P1 aging, Sev1/Sev2 call-outs
6. Roadmap Progress — milestone status, from `sn_milestones_milestone`
7. Governance Highlights — brief pointer only; full detail belongs to the Governance & Portfolio report, don't duplicate it here
8. Cross-Team Dependencies — from epic/story dependency links where available
9. Risks and Mitigations — from `sn_risk_risk`
10. Decisions Needed
11. Next Week Priorities

## PPT slides (9, speaker notes **required** on every slide)
1. Executive Summary
2. Portfolio Health
3. Model Health
4. Roadmap Progress
5. Defects and Reliability
6. Governance Progress
7. Dependencies and Risks
8. Decisions Needed
9. Next Quarter Outlook

**Speaker notes are a hard requirement from the spec** — when calling `anthropic-skills:pptx`, confirm notes are attached per slide (its `addNotes` mechanism) before treating this report as complete. This is the easiest requirement in the whole suite to accidentally skip.

## Requirements (verbatim from spec)
- Include all portfolios.
- Action-oriented summaries.
- Highlight blockers explicitly.
- Produce speaker notes (see above).

## Output naming
`<date>_LeadershipReadout.docx` / `.pptx` — see `output-rendering.md`.

## Known gaps banner
Risk and milestone tables are confirmed as of 2026-10-02. Only: "⚠ DevX delivery history is manual-entry this week — no tool is connected." Do not silently drop sections 6 or 9 if a future schema change breaks the query.
