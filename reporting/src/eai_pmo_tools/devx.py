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
import re
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

    return parse_output(result.stdout)


def parse_output(stdout: str) -> Any:
    """Decode structured output without reconstructing terminal display wrapping."""
    text = re.sub(r"\x1b\[[0-9;]*m", "", stdout).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    count = re.search(r"Returned (\d+) record\(s\)", text)
    if count is None:
        raise DevxCliError("devx-cli returned non-JSON output")
    prefix = text[:count.start()]
    if re.search(r"not authorized|invalid table|not authenticated", prefix, re.I):
        raise DevxCliError("devx-cli reported an access or query error")
    for candidate in re.finditer(r"[\[{]", text[count.end():]):
        try:
            data, end = json.JSONDecoder().raw_decode(text[count.end() + candidate.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(data, list) and len(data) == int(count.group(1)):
            return data
    if int(count.group(1)) == 0 and not re.search(r"not authorized|invalid table|not authenticated", text, re.I):
        return []
    raise DevxCliError("devx-cli record count or structured output is incomplete")


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


def query_table(
    table: str,
    encoded_query: str | None = None,
    limit: int = 50,
    *,
    fields: str | None = None,
    offset: int | None = None,
    display_value: str | None = None,
) -> Any:
    """Generic Table API passthrough via devx-cli's `query` command.

    This is the only path to categories with no dedicated devx-cli command
    (risks, milestones, problems, AI Control Tower, model inventory, audit
    findings — see ../../data-sources.md). Table names for most of these
    are unverified on this instance — discover through `sys_db_object` and
    confirm a candidate with a bounded read before trusting results,
    and do not silently treat an empty/erroring response as "no records."
    """
    args = ["query", "--table", table]
    if encoded_query:
        args += ["--query", encoded_query]
    args += ["--limit", str(limit)]
    if fields is not None:
        args += ["--fields", fields]
    if offset is not None:
        args += ["--offset", str(offset)]
    if display_value is not None:
        args += ["--display-value", display_value]
    return run(args)
