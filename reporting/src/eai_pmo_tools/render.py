"""Document rendering — NOT YET IMPLEMENTED outside a Claude Code session.

Inside a Claude Code session, each generator renders its `.docx`/`.pptx`
output by invoking the `docx` and `pptx` skills directly (see
../../output-rendering.md) — there is no Python rendering code to call,
by design, so rendering never drifts out of sync with those skills' own
conventions (speaker notes, theming, page size, etc.).

To run this pipeline standalone (e.g. from a scheduled job with no Claude
session attached), this module would need a real implementation using a
library such as `python-docx` / `python-pptx`, re-deriving the section/
slide shapes already defined in each `generators/*.md` spec. That's
deliberately out of scope for this starter scaffold — do not add a partial
implementation here without also deciding whether the two rendering paths
(skill-based vs. standalone) are expected to stay byte-for-byte consistent,
since that's real design work, not a stub.
"""

from __future__ import annotations

from typing import Any


def render_docx(*_args: Any, **_kwargs: Any) -> None:
    raise NotImplementedError(
        "Standalone .docx rendering isn't implemented — use the `docx` skill "
        "inside a Claude Code session instead. See this module's docstring."
    )


def render_pptx(*_args: Any, **_kwargs: Any) -> None:
    raise NotImplementedError(
        "Standalone .pptx rendering isn't implemented — use the `pptx` skill "
        "inside a Claude Code session instead. See this module's docstring."
    )
