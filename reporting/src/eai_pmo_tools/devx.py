"""Thin subprocess wrapper around the devx-cli binary.

devx-cli loads its command set dynamically per ServiceNow instance/version,
so this module never hardcodes flag names beyond `--number`/`--query`/
`--limit`, which are stable across the commands used here as of this
writing. Always run `devx-cli <command> --help` yourself before adding a
new call if you're unsure a flag still applies.

This module intentionally passes no credentials of its own — it relies on
whatever `devx-cli` session is already active (`devx-cli whoami` to check,
`devx-cli auth --add` to start one). That auth is interactive browser-based
OAuth per person, with no username/password/token env var it accepts, so
it cannot be resolved from 1Password or any other secret store the way
this repo's own future secrets must be (see ../../.env.1password.example
and ../../run_with_1password.sh at the repo root). Don't try to "fix" that
by piping credentials into devx-cli yourself — there's no supported way to.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any


class DevxCliError(RuntimeError):
    """Raised when a devx-cli invocation fails or returns non-JSON output."""


def run(args: list[str]) -> Any:
    """Run `devx-cli <args>` and parse its JSON stdout.

    Raises DevxCliError on non-zero exit or unparseable output, rather than
    returning an empty/partial result silently.
    """
    try:
        result = subprocess.run(
            ["devx-cli", *args],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise DevxCliError("devx-cli not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        raise DevxCliError(
            f"devx-cli {' '.join(args)} failed: {exc.stderr.strip()}"
        ) from exc

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise DevxCliError(
            f"devx-cli {' '.join(args)} returned non-JSON output"
        ) from exc


def list_records(command: str, story: str | None = None, query: str | None = None, limit: int = 50) -> Any:
    """Call a `<command>:list` devx-cli command.

    Exactly one of `story` or `query` should usually be set — see each
    command's own `--help` for which filters it actually supports; not
    every `*-list` command accepts the same flags.
    """
    args = [f"{command}:list"]
    if story:
        args += ["--story", story]
    if query:
        args += ["--query", query]
    args += ["--limit", str(limit)]
    return run(args)


def query_table(table: str, encoded_query: str | None = None, limit: int = 50) -> Any:
    """Generic Table API passthrough via devx-cli's `query` command.

    This is the only path to categories with no dedicated devx-cli command
    (risks, milestones, problems, AI Control Tower, model inventory, audit
    findings — see ../../data-sources.md). Table names for most of these
    are unverified on this instance — confirm with
    `devx-cli dev:table-schema-get --table <table>` before trusting results,
    and do not silently treat an empty/erroring response as "no records."
    """
    args = ["query", "--table", table]
    if encoded_query:
        args += ["--query", encoded_query]
    args += ["--limit", str(limit)]
    return run(args)
