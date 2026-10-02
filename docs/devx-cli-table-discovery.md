# devx-cli Table & Role Discovery

How to find a ServiceNow table, role, or ACL name via `devx-cli` when no dedicated command covers it — lessons from actually doing this against the real "surf" instance while building `reporting/data-sources.md`, not assumed from documentation.

(This is also captured as a Claude Code skill at `.claude/skills/devx-cli-table-discovery/` in the parent workspace, for discoverability inside a Claude Code session. This file is the git-tracked copy, kept in sync the same way the `reporting/generators/*.md` specs are mirrored from that workspace's skill references.)

## Verify the real command set before assuming a command exists

`devx-cli`'s command set loads dynamically per instance/version. A command name remembered from a different context (another skill's description, another instance) may not exist on the one you're actually targeting. Before relying on a command:

```bash
devx-cli commands --refresh
devx-cli <command> --help
```

Concretely hit this while building this repo: assumed `dev:table-schema-get` and `dev:global-file-search` existed, based on a different, local-dev-focused skill's description. Neither exists in the real "surf" record-query command set — it has only the specific `*:list`/`*:get`/`*:create`/`*:update` commands plus one generic passthrough: `query`.

## Finding an unknown table name

`devx-cli query` (the generic Table API passthrough) needs a real table name. When you don't have one, search ServiceNow's own table dictionary rather than guessing silently:

```bash
devx-cli query --table sys_db_object --query "nameLIKE<keyword>" --fields "name,label" --limit 20
```

Then confirm any candidate actually works and has real data:

```bash
devx-cli query --table <candidate> --fields "sys_id" --limit 1
```

Three distinct outcomes — don't collapse them:
- Real JSON records returned → confirmed, use it.
- `✗ Invalid table <name>` → wrong name, try another candidate.
- `✗ User Not Authorized` → the table is **real**, but the authenticated user lacks the role. A permissions gap, not a naming problem — stop guessing table names and go find the role instead.

## Finding which role to request

`sys_security_acl` (where ACL-to-role mappings actually live) is commonly itself access-denied — don't expect to read it directly. Search the role dictionary by keyword instead:

```bash
devx-cli query --table sys_user_role --query "nameLIKE<keyword>" --fields "name,description" --limit 20
```

Prefer the narrowest-scoped role whose name/description matches the specific app/table over a broad suite-wide reader role; use the broad one only as a documented fallback. See `docs/access-requests/grc-audit-read-justification.md` for a worked example of this.

## Check who you're actually authenticated as

`devx-cli auth` is interactive browser-based OAuth **per person** — no username/password/token env var, no separate service/integration account. Confirm the real identity before designing any automation around it:

```bash
devx-cli whoami
```

Any access request or permission gap applies to that specific person's account, not a shared identity — see the root `README.md`'s 1Password section for why this also means devx-cli's own auth can't be wrapped through `run_with_1password.sh`.

## Naming traps

A table or scoped-app prefix can look like a match and be something else entirely — see `reporting/data-sources.md`'s note on `sn_aict_trace_coll_*` (an unrelated trace-collector app) versus the real AI Governance tables used for this repo's Governance & Portfolio report. Never trust a name alone — pull a sample record and check its actual fields before building anything on top of a candidate table.
