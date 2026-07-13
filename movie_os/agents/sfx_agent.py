"""SFXAgent — generates per-scene sound effects.

Asset-aware: every SFX asset is registered in the AssetStore
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


logger = logging.getLogger("movie_os.agents.sfx")


class SFXAgent(AgentBase):
    name = "sfx_agent"

    async def run(self, state: "MovieState") -> "MovieState":
        timeline = state.get("timeline") or {}
        scenes = timeline.get("scenes", [])
        if not scenes:
            return {"current_step": "sfx_skipped"}

        cap = self.try_get_capability("sfx")
        if cap is None:
            return {"current_step": "sfx_skipped"}

        scene_assets: dict = dict(state.get("scene_assets", {}))
        store = self.context.asset_store

        for scene in scenes:
            sn = scene.get("number") or scene.get("scene_number")
            if sn is None:
                continue
            sn = int(sn)
            sfx_layers = scene.get("sfx_layers", []) or []
            if not sfx_layers:
                continue
            assets_for_scene = scene_assets.get(sn, {})
            if "sfx" in assets_for_scene:
                continue
            output_dir = Path(self.context.output_dir) / "sfx"
            output_dir.mkdir(parents=True, exist_ok=True)
            sfx_paths = []
            for layer in sfx_layers:
                try:
                    from movie_os.capabilities.base import SFXIntent
                    intent = SFXIntent(
                        effect_type=layer if isinstance(layer, str) else layer.get("type", "ambient"),
                        duration_seconds=scene.get("target_duration_seconds", 5.0),
                        metadata={
                            "output_dir": str(output_dir),
                            "scene_number": sn,
                            "pipeline_id": "movie_os",
                        },
                    )
                    result = await cap.execute(intent)
                    asset = result.asset if hasattr(result, "asset") else result
                    path = (
                        str(asset.path) if hasattr(asset, "path")
                        else str(asset.get("path"))
                    )
                    sfx_paths.append(path)
                    if store is not None:
                        register_audio(
                            store, path, asset_type=AssetType.SFX,
                            scene=scene,
                            extra_tags=["sfx", intent.effect_type],
                            metadata={"effect_type": intent.effect_type},
                        )
                except Exception as e:
                    logger.warning(f"SFXAgent: layer {layer} failed: {e}")
            if sfx_paths:
                assets_for_scene["sfx"] = sfx_paths
                scene_assets[sn] = assets_for_scene

        return {"scene_assets": scene_assets, "current_step": "sfx_done"}
