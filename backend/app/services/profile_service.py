"""Production profile loader for GENESIS.

Loads profile definitions from config/production_profiles.yaml and
provides lookups used by the pipeline orchestrator to derive scene
count and per-scene duration targets.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("production_profile_service")

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent.parent / "config" / "production_profiles.yaml"


def _load_raw() -> Dict[str, Any]:
    if not _CONFIG_PATH.exists():
        logger.warning("production_profiles.yaml not found at %s", _CONFIG_PATH)
        return {}
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def get_config() -> Dict[str, Any]:
    return _load_raw()


def get_default_profile_id() -> str:
    return get_config().get("default_profile", "youtube_longform")


def get_scene_classes() -> Dict[str, Dict[str, Any]]:
    return get_config().get("scene_classes", {})


def list_profiles() -> List[Dict[str, Any]]:
    cfg = get_config()
    default_id = cfg.get("default_profile", "youtube_longform")
    profiles = cfg.get("profiles", {}) or {}
    out: List[Dict[str, Any]] = []
    for pid, p in profiles.items():
        out.append({
            "id": pid,
            "label": p.get("label", pid),
            "default": pid == default_id,
            "runtime": p.get("runtime", {}),
            "scene_policy": p.get("scene_policy", {}),
        })
    out.sort(key=lambda x: (not x["default"], x["id"]))
    return out


def get_profile(profile_id: Optional[str] = None) -> Dict[str, Any]:
    cfg = get_config()
    profiles = cfg.get("profiles", {}) or {}
    if not profile_id:
        profile_id = cfg.get("default_profile", "youtube_longform")
    profile = profiles.get(profile_id)
    if profile is None:
        logger.warning("Profile '%s' not found, falling back to default", profile_id)
        profile_id = cfg.get("default_profile", "youtube_longform")
        profile = profiles.get(profile_id, {})
    return {
        "id": profile_id,
        "label": profile.get("label", profile_id),
        "runtime": profile.get("runtime", {}),
        "scene_policy": profile.get("scene_policy", {}),
        "scene_classes": get_scene_classes(),
        "exceptions": profile.get("exceptions", []),
    }


def derive_scene_count(profile_id: Optional[str] = None) -> int:
    """Return the preferred scene count (midpoint) for a profile."""
    p = get_profile(profile_id)
    policy = p.get("scene_policy", {})
    pref = policy.get("preferred_scene_count", [12, 16])
    if isinstance(pref, list) and len(pref) == 2:
        return (pref[0] + pref[1]) // 2
    return 14


def derive_scene_duration_range(profile_id: Optional[str] = None) -> tuple[int, int]:
    """Return the preferred per-scene duration range (seconds)."""
    p = get_profile(profile_id)
    policy = p.get("scene_policy", {})
    pref = policy.get("preferred_scene_duration_seconds", [75, 90])
    if isinstance(pref, list) and len(pref) == 2:
        return int(pref[0]), int(pref[1])
    return 75, 90