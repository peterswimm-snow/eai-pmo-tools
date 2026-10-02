"""Core Team Action Report — see ../../generators/core-team-action.md for the full spec.

The most automatable generator: stories, scrum tasks, defects, and epics
are all confirmed data sources. Only DevX sprint/repo-activity metrics are
a manual-input placeholder.
"""

from __future__ import annotations

from typing import Any

PLACEHOLDER = "⚠ Manual input required — no DevX sprint/repo-activity metrics tool is connected."


def assemble(cached_pull: dict[str, Any], devx_sprint_metrics: str | None = None) -> dict[str, Any]:
    """Build the email-section/slide content for this report from a Phase-1 cache.

    `cached_pull` is expected to have the keys this report needs — stories,
    scrum_tasks, defects, epics — as produced by the orchestrator's shared
    pull (see ../../orchestrator.md Phase 1). `devx_sprint_metrics` is
    whatever free-text the user supplied for the one manual-input gap this
    report has (Phase 2) — pass None to render the placeholder instead.
    """
    stories = cached_pull.get("stories", [])
    scrum_tasks = cached_pull.get("scrum_tasks", [])
    defects = cached_pull.get("defects", [])
    epics = cached_pull.get("epics", [])

    overdue = [t for t in scrum_tasks if t.get("overdue")]
    unassigned = [t for t in scrum_tasks + stories if not t.get("assigned_to")]

    return {
        "this_weeks_objectives": [e.get("short_description") for e in epics],
        "open_deliverables": _group_by_workstream(stories + scrum_tasks),
        "assigned_owners": {
            t.get("number"): t.get("assigned_to") for t in scrum_tasks + stories
        },
        "unassigned_items": unassigned,  # flag these explicitly — never drop silently
        "due_this_week": [t for t in scrum_tasks if t.get("due_this_week")],
        "overdue_items": overdue,  # flag explicitly per the spec's "flag overdue" requirement
        "blockers": [d for d in defects if d.get("priority") == "P1"],
        "completed_work": [t for t in scrum_tasks if t.get("state") == "Closed"],
        "upcoming_milestones": cached_pull.get("milestones", PLACEHOLDER),
        "devx_sprint_metrics": devx_sprint_metrics or PLACEHOLDER,
    }


def _group_by_workstream(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        workstream = item.get("workstream", "Unscoped")
        grouped.setdefault(workstream, []).append(item)
    return grouped
