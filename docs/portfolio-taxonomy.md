# Portfolio Taxonomy & Report-Out Structure

Stub — ref. STSK0760142 ("Define portfolio taxonomy and report-out structure", under STRY2795985). Fill in and remove this notice once the team agrees the taxonomy below is final.

## Workstreams (current known anchors — from `PROJECT_PORTFOLIO.md` in the parent workspace)

| Workstream | ServiceNow anchor | Local folder |
|---|---|---|
| SalesCRM | STRY2793791, STRY2795373 | `SalesCRM/` |
| ML Risk Model for SPM | STRY2793790, STRY2793795, STRY2793796 | `ML_Risk_Model_for_SPM/` |
| Enterprise RTB Managed Delivery | PRJ0124654 | `Enterprise_RTB/` |
| Downsell Renewal Risk Analysis | (feeds ML Risk Model) | `Downsell/` |
| ML Control Plane (AutoML, Feature Store, replatform) | EARB00013238 and related stories | `ML Control Plane/` |

## Report-out structure

This taxonomy is what the Weekly Reporting Suite (`reporting/`) uses to scope and group data — see `reporting/data-sources.md`'s "workstream scoping" note. Reports that say "group by workstream" (e.g. Core Team Action) or "include all portfolios" (e.g. Leadership Readout) should use exactly this list, not an ad hoc one.

**Open question for the team:** should Downsell be reported as its own row, or folded into ML Risk Model for SPM's section since it only feeds that model? Resolve this before the taxonomy is considered final.
