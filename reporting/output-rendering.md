# Weekly Reporting Suite — Output Rendering

How every generator turns its assembled content into actual files. This skill does not own any rendering code — it delegates to the existing `anthropic-skills:docx` and `anthropic-skills:pptx` skills via the `Skill` tool, so byte-generation never drifts out of sync with those skills' own gotcha sheets.

## Mechanism

- **Email draft → `.docx`:** invoke `Skill(skill="docx", args=...)` with the assembled email sections (in the order the generator's reference file specifies). The email is **always** a Word draft to be copied or attached manually — never sent — because no email-send connector is authorized this session. State this plainly to the user when handing over the file.
- **Slide narrative → `.pptx`:** invoke `Skill(skill="pptx", args=...)` with the slide-by-slide content (title + body + any table/chart data) the generator's reference file specifies. Where a generator's spec requires speaker notes (Leadership Readout), use the pptx skill's `addNotes` mechanism per slide — this is easy to miss and must be checked, not assumed.

## Shared styling

- `assets/pptx-theme.json` — shared brand theme (colors/fonts) passed to the pptx skill's theme-application step. Maintain once here; every generator applies the same theme rather than re-describing styling per file.
- `assets/docx-style-guide.md` — shared Word styling rules (heading levels, table shading, font) applied to every `.docx` draft.

## Output location and naming

Land output under a new workspace-root folder, one dated subfolder per run:

```
Weekly Reports/
  <YYYY-MM-DD>/
    <YYYY-MM-DD>_ExecutiveDashboard.docx
    <YYYY-MM-DD>_ExecutiveDashboard.pptx
    <YYYY-MM-DD>_LeadershipReadout.docx
    <YYYY-MM-DD>_LeadershipReadout.pptx
    <YYYY-MM-DD>_OpsModelHealth.docx
    <YYYY-MM-DD>_OpsModelHealth.pptx
    <YYYY-MM-DD>_GovernancePortfolio.docx
    <YYYY-MM-DD>_GovernancePortfolio.pptx
    <YYYY-MM-DD>_CoreTeamAction.docx
    <YYYY-MM-DD>_CoreTeamAction.pptx
    _data/raw-pulls.json          # orchestrator-run cache only (Phase 1 of the orchestrator), not created for single-generator runs
```

- `<YYYY-MM-DD>` is the report week's date (the date the report is generated for, not necessarily "today" — confirm with the user if ambiguous).
- `ReportCode` is fixed per generator (`ExecutiveDashboard`, `LeadershipReadout`, `OpsModelHealth`, `GovernancePortfolio`, `CoreTeamAction`) — no spaces, so filenames sort and script cleanly.
- `Weekly Reports/` is tracked in `PROJECT_PORTFOLIO.md` as a program-wide output folder, not a single ServiceNow-anchored workstream.

## Gap handling in rendered output

Any section backed by a TBD ServiceNow table (see `data-sources.md`) or a permanent manual-input gap (DevX metrics, model-monitoring metrics) must render as a visible, explicit placeholder in both the `.docx` and `.pptx` — e.g. "⚠ Data source not yet verified — see data-sources.md" or "⚠ Manual input required — ask [owner] for this week's figures." Never leave the section blank and never fabricate numbers to fill it.
