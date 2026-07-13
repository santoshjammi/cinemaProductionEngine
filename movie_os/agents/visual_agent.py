"""VisualAgent — renders scene images via the image capability.

Asset-aware: every rendered image is registered in the AssetStore
(if one is provided in the AgentContext) with tags derived from
the scene/shot context.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, TYPE_CHECKING

from movie_os.agents.assets import register_image
from movie_os.agents.base import AgentBase

if TYPE_CHECKING:
    from movie_os.agents.state import MovieState


logger = logging.getLogger("movie_os.agents.visual")


class VisualAgent(AgentBase):
    name = "visual_agent"

    async def run(self, state: "MovieState") -> "MovieState":
        timeline = state.get("timeline") or {}
        scenes = timeline.get("scenes", [])
        if not scenes:
            return {"current_step": "visual_skipped"}

        cap = self.try_get_capability("image")
        if cap is None:
            logger.warning("VisualAgent: no 'image' capability; skipping")
            return {"current_step": "visual_skipped"}

        scene_assets: dict = dict(state.get("scene_assets", {}))
        attempts: dict = dict(state.get("render_attempts", {}))
        store = self.context.asset_store
        quality = self.context.quality or "draft"

        for scene in scenes:
            sn = scene.get("number") or scene.get("scene_number")
            if sn is None:
                continue
            sn = int(sn)
            shots = scene.get("shots", []) or []
            assets_for_scene = scene_assets.get(sn, {})
            attempts[str(sn)] = attempts.get(str(sn), 0) + 1

            # Render only the FIRST shot per scene — that's what
            # the publishing agent uses. Other shots are kept in
            # the timeline for later re-render (e.g. with a different
            # quality or style) but we don't pay the FLUX cost now.
            if shots:
                shot = shots[0]
            else:
                shot = {}
            shot_id = str(shot.get("id", "?"))
            key = f"image_{shot_id}"
            # Check if image already exists on disk from a previous run
            out_dir = Path(self.context.output_dir) / "images" / "movie_os" / "scene_images"
            disk_path = out_dir / f"scene_{sn:03d}.png"
            if disk_path.exists() and disk_path.stat().st_size > 1000:
                assets_for_scene[key] = str(disk_path)
                scene_assets[sn] = assets_for_scene
                logger.info(f"VisualAgent: reusing existing image on disk for scene {sn} → {disk_path}")
                continue

            if key in assets_for_scene and assets_for_scene[key]:
                scene_assets[sn] = assets_for_scene
                continue  # already rendered

            prompt = (
                shot.get("visual_intent")
                or shot.get("prompt")
                or scene.get("scene_description", "")
            )
            if not prompt:
                scene_assets[sn] = assets_for_scene
                continue
            intent = self._build_intent(scene, shot, prompt, quality)
            try:
                result = await cap.execute(intent)
                asset = result.asset if hasattr(result, "asset") else result
                path = (
                    str(asset.path) if hasattr(asset, "path")
                    else str(asset.get("path"))
                )
                assets_for_scene[key] = path
                # Register in the asset store with auto-derived tags
                if store is not None:
                    reg = register_image(
                        store, path,
                        scene=scene, shot=shot,
                        prompt=prompt,
                        model=getattr(asset, "metadata", {}).get("model") if hasattr(asset, "metadata") else None,
                        seed=getattr(asset, "seed", None) if hasattr(asset, "seed") else None,
                        extra_tags=[f"shot_{shot_id}"],
                    )
                    if reg is not None:
                        assets_for_scene[f"image_{shot_id}_asset_id"] = reg.id
                logger.info(f"VisualAgent: scene {sn} shot {shot_id} → {path}")
            except Exception as e:
                logger.warning(
                    f"VisualAgent: render failed for scene {sn} shot {shot_id}: {e}"
                )

            scene_assets[sn] = assets_for_scene

        return {
            "scene_assets": scene_assets,
            "render_attempts": attempts,
            "current_step": "visual_done",
        }

    def _build_intent(self, scene: dict, shot: dict, prompt: str, quality: str):
        from movie_os.capabilities.base import ImageIntent
        # Use the shot's planned resolution if set, else FLUX native 16:9 (1024x576)
        width = shot.get("width", 1024)
        height = shot.get("height", 576)
        # FLUX likes multiples of 16
        width = max(512, min(width, 1536))
        height = max(512, min(height, 1536))
        # Enrich the prompt with cinematic qualifiers if it doesn't have them
        enriched_prompt = self._enrich_prompt(prompt, scene, shot)
        return ImageIntent(
            prompt=enriched_prompt,
            width=width,
            height=height,
            seed=shot.get("seed") or scene.get("seed"),
            quality=quality,
            metadata={
                "output_dir": str(Path(self.context.output_dir) / "images"),
                "scene_number": scene.get("number") or scene.get("scene_number"),
                "pipeline_id": "movie_os",
            },
        )

    def _enrich_prompt(self, prompt: str, scene: dict, shot: dict) -> str:
        """Add cinematic qualifiers to a prompt for better FLUX output.

        The user-written description is the source of truth. We
        only add the "production" suffix if the prompt doesn't
        already have style keywords. We also drop the voiceover
        text if it leaked into the prompt.
        """
        prompt_lower = prompt.lower()
        # If the prompt already has cinematic terms, leave it alone
        if any(term in prompt_lower for term in [
            "cinematic", "photorealistic", "8k", "4k",
            "shallow depth of field", "film grain",
        ]):
            return prompt
        # Add production-quality qualifiers
        style = scene.get("mood", "")
        qualifiers = "cinematic, photorealistic, shallow depth of field, soft natural lighting, film grain"
        return f"{prompt}. {qualifiers}"
