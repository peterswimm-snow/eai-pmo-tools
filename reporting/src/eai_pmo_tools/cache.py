"""Read/write the orchestrator's shared-pull cache.

See ../../orchestrator.md Phase 1 — every category used by more than one
generator is pulled once per run and cached here, so generators in Phase 3
read from this file instead of re-querying ServiceNow.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


def cache_path(report_date: date, reports_root: Path) -> Path:
    """Path to this run's raw-pulls.json, per the Weekly Reports/<date>/_data/ convention."""
    return reports_root / report_date.isoformat() / "_data" / "raw-pulls.json"


def write(report_date: date, reports_root: Path, data: dict) -> Path:
    path = cache_path(report_date, reports_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str))
    return path


def read(report_date: date, reports_root: Path) -> dict:
    path = cache_path(report_date, reports_root)
    if not path.exists():
        raise FileNotFoundError(
            f"No cache at {path} — run the orchestrator's Phase 1 pull first."
        )
    return json.loads(path.read_text())
