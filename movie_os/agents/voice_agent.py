"""VoiceAgent — synthesizes narration audio per scene.

Asset-aware: every generated voice clip is registered in the
AssetStore (if one is provided).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from movie_os.agents.assets import register_audio
from movie_os.agents.base import AgentBase

if TYPE_CHECKING:
    from movie_os.agents.state import MovieState


logger = logging.getLogger("movie_os.agents.voice")


class VoiceAgent(AgentBase):
    name = "voice_agent"

    async def run(self, state: "MovieState") -> "MovieState":
        timeline = state.get("timeline") or {}
        scenes = timeline.get("scenes", [])
        if not scenes:
            return {"current_step": "voice_skipped"}

        cap = self.try_get_capability("voice")
        if cap is None:
            return {"current_step": "voice_skipped"}

        scene_assets: dict = dict(state.get("scene_assets", {}))
        store = self.context.asset_store

        for scene in scenes:
            sn = scene.get("number") or scene.get("scene_number")
            if sn is None:
                continue
            sn = int(sn)
            voiceover = scene.get("voiceover", "")
            if not voiceover:
                continue
            assets_for_scene = scene_assets.get(sn, {})
            if "voice" in assets_for_scene:
                continue
            from movie_os.capabilities.base import VoiceIntent
            output_dir = Path(self.context.output_dir) / "voice"
            output_dir.mkdir(parents=True, exist_ok=True)
            intent = VoiceIntent(
                text=voiceover,
                voice=scene.get("voice", "en-US-GuyNeural"),
                rate=scene.get("voice_rate", "+0%"),
                prosody_override=scene.get("prosody"),
                vocal_fracture=scene.get("vocal_fracture", False),
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
                assets_for_scene["voice"] = path
                if store is not None:
                    reg = register_audio(
                        store, path, scene=scene,
                        extra_tags=["voice", "narration"],
                        metadata={"voice": intent.voice, "rate": intent.rate},
                    )
                    if reg is not None:
                        assets_for_scene["voice_asset_id"] = reg.id
                scene_assets[sn] = assets_for_scene
                logger.info(f"VoiceAgent: scene {sn} → {path}")
            except Exception as e:
                logger.warning(f"VoiceAgent: scene {sn} failed: {e}")

        return {"scene_assets": scene_assets, "current_step": "voice_done"}
