"""Leadership Weekly Readout — see ../../generators/leadership-readout.md for the full spec.

STUB — not yet built out. Widest pull of the five reports; depends on
risks/milestones (unverified) and DevX delivery history (manual-input
only). The .pptx this produces must include speaker notes on every slide
— don't forget that requirement when this is implemented.
"""

from __future__ import annotations

from typing import Any


def assemble(cached_pull: dict[str, Any], devx_delivery_history: str | None = None) -> dict[str, Any]:
    raise NotImplementedError(
        "Leadership Readout assembly isn't built out yet — see this module's "
        "docstring and reporting/generators/leadership-readout.md."
    )
