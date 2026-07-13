"""MusicAgent — generates per-scene music beds and stings.

Asset-aware: every music asset is registered in the AssetStore
(if one is provided).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from movie_os.agents.assets import register_audio
from movie_os.agents.base import AgentBase
from movie_os.asset_store import AssetType

if TYPE_CHECKING:
    from movie_os.agents.state import MovieState


logger = logging.getLogger("movie_os.agents.music")


class MusicAgent(AgentBase):
    name = "music_agent"

    async def run(self, state: "MovieState") -> "MovieState":
        timeline = state.get("timeline") or {}
        scenes = timeline.get("scenes", [])
        if not scenes:
            return {"current_step": "music_skipped"}

        cap = self.try_get_capability("music")
        if cap is None:
            return {"current_step": "music_skipped"}

        scene_assets: dict = dict(state.get("scene_assets", {}))
        store = self.context.asset_store

        for scene in scenes:
            sn = scene.get("number") or scene.get("scene_number")
            if sn is None:
                continue
            sn = int(sn)
            music_cue = scene.get("music_cue", {}) or {}
            if isinstance(music_cue, dict) and music_cue.get("zone") == "none":
                continue
            assets_for_scene = scene_assets.get(sn, {})
            if "music" in assets_for_scene:
                continue
            from movie_os.capabilities.base import MusicIntent
            output_dir = Path(self.context.output_dir) / "music"
            output_dir.mkdir(parents=True, exist_ok=True)
            intent = MusicIntent(
                zone=music_cue.get("zone", "act_1") if isinstance(music_cue, dict) else "act_1",
                duration_seconds=scene.get("target_duration_seconds", 10.0),
                volume=music_cue.get("volume", 0.3) if isinstance(music_cue, dict) else 0.3,
                mood=scene.get("mood", "neutral"),
                metadata={
                    "output_dir": str(output_dir),
                    "scene_number": sn,
                    "pipeline_id": "movie_os",
                },
            )
            try:
                result = await cap.execute(intent)
                asset = result.asset if hasattr(result, "asset") else result
                path = (
                    str(asset.path) if hasattr(asset, "path")
                    else str(asset.get("path"))
                )
                assets_for_scene["music"] = path
                if store is not None:
                    reg = register_audio(
                        store, path, asset_type=AssetType.MUSIC,
                        scene=scene,
                        extra_tags=["music", "bed"],
                        metadata={"zone": intent.zone, "mood": intent.mood},
                    )
                    if reg is not None:
                        assets_for_scene["music_asset_id"] = reg.id
                scene_assets[sn] = assets_for_scene
            except Exception as e:
                logger.warning(f"MusicAgent: scene {sn} failed: {e}")

        return {"scene_assets": scene_assets, "current_step": "music_done"}
