# Onboarding & Enrollment Checklist

For new RTB team members (originally compiled for Amy Gorman — ref. STSK0760136, under STRY2795985). Covers GitHub, DevEx CLI, and Microsoft 365 Copilot. Owner for each item follows the "real owner" noted in the linked scrum task, not necessarily the ServiceNow `assigned_to` field.

## 1. GitHub

- [ ] Confirm GitHub account exists / is created for the new team member.
- [ ] Request access to this org's repos, starting with `eai-pmo-tools` (this repo).
- [ ] Confirm the new team member can clone, branch, and open a PR against `eai-pmo-tools`.
- [ ] Share this repo's README and `docs/portfolio-taxonomy.md` as first reading.

## 2. DevEx CLI

- [ ] Install `devx-cli` (`@dt-devx/devx-cli`).
- [ ] Authenticate to the "surf" ServiceNow instance (`devx-cli auth --list` to confirm which instances are already saved; follow the CLI's own auth flow for a new one — never guess flag names, always check `--help` first).
- [ ] Run a read-only smoke test, e.g. `devx-cli story:get --number <a known story>`, to confirm access before relying on it for reporting.
- [ ] Review `reporting/data-sources.md` in this repo for which record categories are confirmed-queryable today vs. still unverified.

## 3. Microsoft 365 Copilot

- [ ] Confirm license request is submitted (ref. STSK0760138 — owned by Peter Lewis Swimm, not the new hire).
- [ ] Confirm license is active before relying on Copilot for any team workflow.
- [ ] No further action needed from the new team member until the license is confirmed active.

## 4. Team coordination

- [ ] Confirm access to the shared Teams coordination space (ref. STSK0760140).
- [ ] Review the weekly reporting cadence (`docs/weekly-reporting-cadence.md`) — Friday written update, Monday RAG review.
- [ ] Review the portfolio taxonomy (`docs/portfolio-taxonomy.md`) so workstream references in reports/tickets are unambiguous.

## 5. Reference materials to send alongside this checklist

- One-pager covering the AI-Assisted Team Operating Model epic's scope (not yet drafted — see STRY2795985 acceptance criteria).
- Link to this repo.
- Link to the dashboard/project-board consolidation once available (ref. STSK0760143).
