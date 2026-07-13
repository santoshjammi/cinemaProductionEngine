"""PublishingAgent — composes the final video from scene assets.

For each scene, picks the first rendered image, applies Ken Burns,
mixes voice + music + sfx, and concatenates everything into a
single mp4. Registers the final video in the AssetStore.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from movie_os.agents.assets import register_video
from movie_os.agents.base import AgentBase
from movie_os.agents.compositor import (
    concat_clips,
    probe_duration,
    render_scene_clip,
)

if TYPE_CHECKING:
    from movie_os.agents.state import MovieState


logger = logging.getLogger("movie_os.agents.publishing")


class PublishingAgent(AgentBase):
    name = "publishing_agent"

    async def run(self, state: "MovieState") -> "MovieState":
        out_dir = Path(self.context.output_dir) / "final"
        out_dir.mkdir(parents=True, exist_ok=True)
        segments_dir = out_dir / "segments"
        segments_dir.mkdir(exist_ok=True)

        timeline = state.get("timeline") or {}
        scene_assets = state.get("scene_assets", {}) or {}
        scenes = timeline.get("scenes", [])

        clip_paths: list[Path] = []
        total_duration = 0.0
        for scene in scenes:
            sn = scene.get("number") or scene.get("scene_number")
            if sn is None:
                continue
            sn = int(sn)
            assets = scene_assets.get(sn, {}) or {}
            # Pick the first image we rendered for this scene
            image_path = self._pick_image(assets)
            if not image_path or not Path(image_path).exists():
                logger.warning(f"PublishingAgent: scene {sn} has no image, skipping")
                continue

            voice = assets.get("voice")
            duration = float(scene.get("target_duration_seconds", 10.0))
            if voice and Path(voice).exists():
                voice_dur = probe_duration(voice)
                if voice_dur > 0:
                    # Match voiceover duration exactly plus a small cushion (0.3s) to prevent clipping
                    duration = voice_dur + 0.3
            music = assets.get("music")
            sfx_paths = assets.get("sfx", []) or []
            music_cue = scene.get("music_cue", {}) or {}
            # Default to 0.6 for audible background music; respect
            # the scene's volume setting if higher.
            music_volume = 0.6
            if isinstance(music_cue, dict):
                music_volume = max(music_volume, music_cue.get("volume", 0.0))
                if music_cue.get("zone") == "none":
                    music = None  # silence

            # Pick a sfx (use first) — skip if not implemented
            sfx = None  # sfx not yet supported in compositor

            ken_burns = scene.get("ken_burns_effect", "ken-burns")
            segment_path = segments_dir / f"scene_{sn:03d}.mp4"
            try:
                render_scene_clip(
                    image_path=image_path,
                    duration_seconds=duration,
                    output_path=segment_path,
                    voice_path=voice if voice and Path(voice).exists() else None,
                    music_path=music if music and Path(music).exists() else None,
                    music_volume=music_volume,
                    ken_burns=ken_burns,
                )
                clip_paths.append(segment_path)
                total_duration += duration
            except Exception as e:
                logger.error(f"PublishingAgent: scene {sn} render failed: {e}")

        if not clip_paths:
            logger.warning("PublishingAgent: no clips to compose")
            return {
                "current_step": "publishing_done",
                "finished_at": datetime.utcnow().isoformat(),
                "final_video": None,
                "publishing_manifest": None,
            }

        # Concat all clips
        final_path = out_dir / "final.mp4"
        try:
            concat_clips(clip_paths, final_path)
            actual_duration = probe_duration(final_path)
            logger.info(
                f"PublishingAgent: wrote {final_path} "
                f"({actual_duration:.1f}s, {len(clip_paths)} scenes)"
            )
            # Register in the asset store
            store = self.context.asset_store
            if store is not None and final_path.exists():
                reg = register_video(
                    store, final_path,
                    scene_count=len(clip_paths),
                    total_duration=actual_duration,
                    extra_tags=["9scene_full"] if len(clip_paths) >= 9 else None,
                )
                asset_id = reg.id if reg else None
            else:
                asset_id = None
            return {
                "current_step": "publishing_done",
                "finished_at": datetime.utcnow().isoformat(),
                "final_video": str(final_path),
                "final_video_duration": actual_duration,
                "final_video_asset_id": asset_id,
            }
        except Exception as e:
            logger.error(f"PublishingAgent: concat failed: {e}")
            return {
                "current_step": "publishing_failed",
                "finished_at": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    def _pick_image(self, assets: dict) -> str | None:
        """Pick the first rendered image from a scene's assets."""
        for key in sorted(assets):
            if key.startswith("image_") and not key.endswith("_asset_id"):
                return assets[key]
        return None
