"""Helpers for production-scoped runtime artifact paths.

P0-01 only: keep the existing engines, but route canonical production artifacts
under a single episode/run root so the runtime is traceable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _slug(value: str, fallback: str) -> str:
    cleaned = "".join(ch for ch in (value or fallback) if ch.isalnum() or ch in "-_.")
    return cleaned or fallback


def get_production_context(brief: dict[str, Any] | None = None) -> dict[str, str]:
    brief = brief or {}
    production = brief.get("production", {}) if isinstance(brief, dict) else {}
    episode_id = _slug(str(production.get("episode_id", "EP-0001")), "EP-0001")
    run_id = _slug(str(production.get("run_id", "RUN-0001")), "RUN-0001")
    production_root = Path("productions") / episode_id
    run_root = production_root / "runs" / run_id
    return {
        "episode_id": episode_id,
        "run_id": run_id,
        "production_root": str(production_root),
        "run_root": str(run_root),
    }


def build_run_path(brief: dict[str, Any] | None, subdir: str, filename: str) -> Path:
    ctx = get_production_context(brief)
    return Path(ctx["run_root"]) / subdir / filename
