"""Asset helpers — convenient wrappers for agents.

Agents shouldn't need to know about AssetStore internals. This
module provides simple functions that:
  - take a generated file path
  - auto-derive tags from the scene/shot context
  - call asset_store.create() with sensible defaults
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from movie_os.asset_store import AssetStore, AssetType


logger = logging.getLogger("movie_os.agents.assets")


def register_image(
    store: AssetStore | None,
    file_path: str | Path,
    *,
    scene: dict | None = None,
    shot: dict | None = None,
    prompt: str | None = None,
    model: str | None = None,
    seed: int | None = None,
    extra_tags: list[str] | None = None,
) -> Any:
    """Register an image asset in the store.

    Tags are auto-derived: scene_number, shot_size, energy, phase,
    irreversible_moment (if set), plus any explicit extra_tags.
    """
    if store is None:
        return None
    tags = _derive_tags(scene, shot, extra_tags)
    try:
        asset = store.create(
            AssetType.IMAGE,
            file_path,
            tags=tags,
            prompt=prompt,
            model=model,
            seed=seed,
            metadata={
                "scene_number": scene.get("number") or scene.get("scene_number") if scene else None,
                "shot_size": shot.get("shot_size") if shot else None,
            },
        )
        return asset
    except Exception as e:
        logger.warning(f"register_image: {e}")
        return None


def register_audio(
    store: AssetStore | None,
    file_path: str | Path,
    *,
    asset_type: AssetType = AssetType.AUDIO,
    scene: dict | None = None,
    extra_tags: list[str] | None = None,
    metadata: dict | None = None,
) -> Any:
    """Register an audio asset (voice, music, or sfx)."""
    if store is None:
        return None
    tags = _derive_tags(scene, None, extra_tags)
    try:
        return store.create(
            asset_type,
            file_path,
            tags=tags,
            metadata=metadata or {},
        )
    except Exception as e:
        logger.warning(f"register_audio: {e}")
        return None


def register_video(
    store: AssetStore | None,
    file_path: str | Path,
    *,
    scene_count: int = 0,
    total_duration: float = 0.0,
    extra_tags: list[str] | None = None,
) -> Any:
    """Register the final composed video."""
    if store is None:
        return None
    tags = list(extra_tags or []) + ["final", "composed"]
    try:
        return store.create(
            AssetType.VIDEO,
            file_path,
            tags=tags,
            metadata={
                "scene_count": scene_count,
                "total_duration_seconds": total_duration,
            },
        )
    except Exception as e:
        logger.warning(f"register_video: {e}")
        return None


def _derive_tags(scene: dict | None, shot: dict | None, extra: list[str] | None) -> list[str]:
    """Build a tag list from scene/shot context."""
    tags: list[str] = list(extra or [])
    if scene is not None:
        sn = scene.get("number") or scene.get("scene_number")
        if sn is not None:
            tags.append(f"scene_{int(sn)}")
        if scene.get("irreversible_moment"):
            tags.append("irreversible_moment")
        if scene.get("phase"):
            tags.append(f"phase_{scene['phase']}")
        if scene.get("act"):
            tags.append(f"act_{scene['act']}")
        energy = scene.get("energy")
        if energy is not None:
            tags.append(f"energy_{int(energy)}")
        if scene.get("mood"):
            tags.append(f"mood_{scene['mood']}")
    if shot is not None:
        ss = shot.get("shot_size")
        if ss:
            tags.append(f"shot_{ss}")
    return sorted(set(tags))
