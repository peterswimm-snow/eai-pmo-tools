"""Executive Dashboard — see ../../generators/executive-dashboard.md for the full spec.

STUB — not yet built out. Depends on risks/milestones (unverified tables,
see data_sources.QUERY_CATEGORIES) and DevX delivery metrics (manual-input
only). Follow core_team_action.py's shape once those are confirmed or you
decide to render their placeholders.
"""

from __future__ import annotations

from typing import Any


def assemble(cached_pull: dict[str, Any], devx_delivery_metrics: str | None = None) -> dict[str, Any]:
    raise NotImplementedError(
        "Executive Dashboard assembly isn't built out yet — see this module's "
        "docstring and reporting/generators/executive-dashboard.md."
    )
