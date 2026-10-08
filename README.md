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
| [`.claude/skills/`](.claude/skills/) | Six repo-local AICT review and human-handoff workflows; inventory below |

## AICT Skill Inventory

Added 2026-10-08. These skills are local workflow instructions for Claude Code,
not deployed ServiceNow functionality or approval of inventory changes.

| Skill | Use It For | Boundary |
|---|---|---|
| [AICT Browser Update Handoff](.claude/skills/aict-browser-update-handoff/SKILL.md) | Confirm asset/employee IDs, inspect the live form, prefill explicitly requested changes, and verify a human save | Never click Save/Update; stop on auto-save behavior, identity ambiguity, or baseline drift |
| [Stakeholder Confirmation](.claude/skills/aict-stakeholder-confirmation/SKILL.md) | Validate the four requested roles, retain gaps/conflicts, and draft outreach | Assignee/team membership is not sponsor or D&A role proof; no message sends |
| [Model Documentation Readiness](.claude/skills/aict-model-documentation-readiness/SKILL.md) | Review model KB, product/technical evidence, approval, freshness, and AICT/SURF links | SharePoint documentation is not automatically a published KB; no live access/publication claims |
| [Inventory Change Plan](.claude/skills/aict-inventory-change-plan/SKILL.md) | Produce before/after owner-change plans and human-applied remediation steps | No writes; candidate identity and supplied freshness markers require live confirmation |
| [Workbook Safety and Recovery](.claude/skills/aict-workbook-safety-recovery/SKILL.md) | Inspect edited headers, duplicate/missing IDs, hidden data, and workbook readability | Stop on invalid or protected input; no automatic repair, revert, or source replacement |
| [Review Sharing Export](.claude/skills/aict-review-sharing-export/SKILL.md) | Create a separate allowlisted review workbook without source tabs/comments/metadata | Hiding is not redaction; human content review and sharing approval remain required |

Each skill includes examples, failure handling, and evaluation scenario checklists.
Those checklists are not claims of executed live agent evaluations.

### Claude Code Marketplace

[The marketplace manifest](.claude-plugin/marketplace.json) lists one
`eai-pmo-tools` plugin in `eai-pmo-marketplace`.
[The plugin manifest](.claude-plugin/plugin.json) loads all six existing skills
from `.claude/skills`; there are no duplicate skill copies or automatic hooks.

From this repository root, validate and optionally register/install locally:

```bash
claude plugin validate .
claude plugin marketplace add .
claude plugin install eai-pmo-tools@eai-pmo-marketplace
```

Run those registration/install commands yourself to change your Claude settings.
The manifests do not install Python dependencies, configure browser tools, or
authenticate ServiceNow. Install the helper package as described below separately.
Plugin skills use the `eai-pmo-tools:` namespace, for example:
`/eai-pmo-tools:aict-stakeholder-confirmation`.

After you review, commit, and publish the manifests to the GitHub repository,
teammates with repository access can use:

```bash
claude plugin marketplace add peterswimm-snow/eai-pmo-tools
claude plugin install eai-pmo-tools@eai-pmo-marketplace
```

The remote installation path is not available until those changes are published.

## Script Inventory

| Command / Module | Available Actions | Inputs And Outputs |
|---|---|---|
| [`pmo-aict-change-plan`](reporting/src/eai_pmo_tools/aict_change_plan.py) | Prepare an offline browser-update handoff for supported owner fields | JSON request to a new JSON plan; exact Surf origin, `u_employee` references, allowlisted fields, and caller-supplied baseline checks |
| [`pmo-aict-review`](reporting/src/eai_pmo_tools/aict_review.py) | `stakeholders`, `documentation` | Explicit-dated JSON evidence to a new per-model gap/confirmation/readiness report; outreach drafts are not sent |
| [`pmo-aict-workbooks`](reporting/src/eai_pmo_tools/aict_workbooks.py) | `inspect`, `sharing-export` | Local XLSX inspection or a new one-tab review copy using an explicit column/host allowlist |
| [`eai_pmo_tools.devx`](reporting/src/eai_pmo_tools/devx.py) | Read through existing authenticated `devx-cli` commands | Structured stdout parser and `query_table` wrapper; not a native AICT update or automatic reconciliation command |

The three AICT helpers do not invoke DevX, retrieve credentials, write ServiceNow,
open a browser, or send messages. Reads/prefill described by skills use the
agent's available tools separately. No browser driver or native DevX AICT update
command is installed by these helpers.

### Install And Run

From this repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,inventory]"
.venv/bin/pmo-aict-change-plan --help
.venv/bin/pmo-aict-review --help
.venv/bin/pmo-aict-workbooks --help
```

Use the documented JSON schema in the corresponding skill; choose output paths
that do not already exist. The helpers refuse to overwrite input or output files.

```bash
.venv/bin/pmo-aict-change-plan --request request.json --output change-plan-new.json
.venv/bin/pmo-aict-review stakeholders --input evidence.json --output stakeholders-new.json
.venv/bin/pmo-aict-review documentation --input evidence.json --output documentation-new.json
.venv/bin/pmo-aict-workbooks inspect inventory.xlsx --sheet "Proposed Changes"
.venv/bin/pmo-aict-workbooks sharing-export inventory.xlsx --sheet "Proposed Changes" --columns approved-columns.json --output review-new.xlsx
.venv/bin/python -m pytest tests/test_aict_change_plan.py tests/test_aict_review.py tests/test_aict_workbooks.py tests/test_devx.py -q
```

The sharing configuration is a JSON file, not inline flags:

```json
{
	"columns": ["Model / Sub-component", "AICT ID", "On Hold (MLMD)", "AICT URL"],
	"trusted_hosts": ["surf.service-now.com"]
}
```

Hosts must be explicitly approved for the intended audience. The sharing exporter
rejects formula cells in selected data and query/fragment-bearing hyperlinks,
including classic ServiceNow links with `?sys_id=`. Review and supply an approved
canonical link; do not strip parameters and guess a destination. It creates only
allowlisted values and approved hyperlink targets, not a copy with hidden columns.
Selected free text still needs human sensitivity review.

### Inventory Evidence Rules

- An MLMD number identifies a legacy use-case record, not a new AICT governance or asset ID.
- A name match is a candidate, not confirmed model/version/component equivalence.
- Keep AI System versus AI Model classes and their source URLs distinct.
- Business sponsor (VP+), business lead (hands-on), D&A lead (Vijay+1), and D&A owner (hands-on) require separate evidence; do not infer these from assignees.
- AICT asset, governance, product-model, and operational SURF CI records are distinct. A generic platform CI does not prove model-specific CI coverage.
- Different lifecycle, governance, execution-health, and on-hold fields are not interchangeable.
- Missing references mean unknown coverage, not proof that records or documents do not exist.
- Private source snapshots and personal workbooks are not bundled with these skills or tests; tests use synthetic/local temporary inputs.

Offline test coverage is executable; live permissions, actual browser locators,
record updates, stakeholder assertions, document access, and publication states
are not certified by passing those tests.

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

**One exception, by necessity, not by choice:** `devx-cli`'s own ServiceNow auth is interactive browser-based OAuth per person (`devx-cli auth --add`) with no env-var injection point, so it can't be routed through this wrapper — see `reporting/src/eai_pmo_tools/devx.py`'s docstring. Every other credential this repo's tools ever need must go through 1Password. The offline AICT helpers need no credentials; the ServiceNow data-pull code relies on the already-authenticated devx-cli session.

## Status

Reporting remains a starter scaffold; see [reporting/README.md](reporting/README.md)
for confirmed sources versus manual-input placeholders. The six repo-local AICT
skills and three offline helper CLIs above have synthetic test coverage. Production
deployment, native DevX writes, automated browser execution, and model inventory
or stakeholder certification are not included.
