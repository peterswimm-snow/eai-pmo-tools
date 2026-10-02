# Generator: Operations & Model Health

## Audience
Operations Teams, Model Owners, Engineering Leads.

## Trigger phrases
"ops report", "model health report", "operations weekly".

## Data pull
From `data-sources.md` (verified 2026-10-02):
- Incidents, Defects → confirmed.
- Problems → confirmed, table `problem` (standard ServiceNow table) via `devx-cli query`.
- Change requests → confirmed, table `change_request` via `devx-cli query`.
- Model monitoring metrics (accuracy/precision/recall/retraining) → **permanent manual-input gap, distinct from the DevX gap below — do not conflate them.**
- DevX deployment data / test results → **permanent manual-input gap**.

## Email sections (in order, 11 total)
1. Weekly Operations Summary
2. Open Incidents — with Sev1/Sev2 explicitly flagged
3. Critical Defects — P1 only
4. Defect Aging — days-open buckets, flag anything past SLA
5. Model Performance — placeholder (manual-input gap) unless the user supplies current figures
6. Accuracy Trends — placeholder (manual-input gap)
7. Precision Trends — placeholder (manual-input gap)
8. Recall Trends — placeholder (manual-input gap)
9. Retraining Activities — placeholder (manual-input gap)
10. Open Risks — from `sn_risk_risk` (confirmed)
11. Next Week Activities

## PPT slides (8)
1. Operations Overview
2. Incident Trends
3. Defect Status
4. Model Stability
5. Performance Metrics
6. Retraining Activities
7. Issue Escalations
8. Operational Priorities

## Requirements (verbatim from spec)
- Include defect aging analysis (section 4).
- Flag SLA breaches explicitly, not just raw aging numbers.
- Flag Sev1 and Sev2 incidents explicitly in section 2.

## Output naming
`<date>_OpsModelHealth.docx` / `.pptx` — see `output-rendering.md`.

## Known gaps banner
Problems, changes, and risks are all confirmed as of 2026-10-02. This report's remaining gaps are sections 5–9 only: "⚠ Model performance metrics (sections 5–9) require manual input this week — no monitoring-system tool is connected, and DevX deployment/test data is manual-entry too." Never fill these with fabricated trend numbers.
