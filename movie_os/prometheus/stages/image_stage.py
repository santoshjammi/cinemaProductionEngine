"""Stage 2: Image Generation — uses FluxComfyUIProvider to generate images for each scene.

Takes storyboard artifacts as input and produces production-quality images
for each scene using the configured image provider chain (FluxComfyUI, SDXL fallback).
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

from movie_os.capabilities.base import ImageIntent
from movie_os.runtime_paths import build_run_path

logger = logging.getLogger("movie_os.prometheus.stages.image")


class ImageGenerationStage:
    """Generate production images from storyboard descriptions."""

    def __init__(
        self,
        certificate: Any | None = None,
        brief: dict[str, Any] | None = None,
    ):
        self.certificate = certificate
        self.brief = brief or {}
        self._image_provider: Any | None = None
        # Character-consistency reference (two-shot Mark+Sarah), resolved
        # lazily from the CharacterRegistry so it's config-driven, not hardcoded.
        self._character_reference: str | None = None

    def _resolve_character_reference(self) -> str | None:
        """Resolve the character-composite reference filename (relative to
        ComfyUI's input dir) for this brief.

        Priority:
          1. `brief['character_consistency']` (injected by the GENESIS
             character-preparation step) — the explicit, resolved set.
          2. Auto-detection from the brief (characters_present / speakers),
             with the psychology default (Mark & Sarah) as fallback.
        Returns None if no characters/hero images are available.
        """
        if self._character_reference is not None:
            return self._character_reference
        try:
            from movie_os.character_consistency import ensure_character_consistency
            result = ensure_character_consistency(self.brief)
            self._character_reference = result.get("reference_filename") or ""
        except Exception as e:
            logger.warning(f"[ImageGenerationStage] Character consistency unavailable: {e}")
            self._character_reference = ""
        return self._character_reference or None

    @property
    def image_provider(self) -> Any:
        """Return the configured image provider (FluxComfyUIProvider or similar)."""
        if self._image_provider is not None:
            return self._image_provider
        # Default to the real FLUX provider (ComfyUI must be running on 8189).
        # Port 8189 is the FLUX-capable ComfyUI (v0.33.1, ComfyUI-Installs)
        # which exposes UNETLoader/VAELoader/DualCLIPLoader and sees the FLUX
        # models. Port 8188 (Comfy Desktop v0.24.0) lacks those loader nodes
        # and returns prompt_outputs_failed_validation on every FLUX render.
        try:
            from movie_os.providers.image.flux_comfyui import FluxComfyUIProvider
            self._image_provider = FluxComfyUIProvider(
                comfyui_url="http://127.0.0.1:8190",
                model="flux1-dev-fp8.safetensors",
            )
            return self._image_provider
        except Exception as e:
            logger.warning(f"[ImageGenerationStage] Could not init FluxComfyUIProvider: {e}")
            return None

    def set_image_provider(self, provider: Any) -> None:
        """Inject an image provider (useful for testing with a mock)."""
        self._image_provider = provider

    async def run(self) -> dict[str, Any]:
        """Execute the image generation stage."""
        storyboard_context = self.brief.get('storyboard_artifacts', [])
        brief_scenes = {s.get('scene_number') or s.get('number'): s for s in self.brief.get('scenes', [])}

        if not storyboard_context:
            logger.warning("[ImageGenerationStage] No storyboard input — creating placeholder images")
            storyboard_context = [{"id": 1, "description": "Wide establishing shot"}]

        provider = self.image_provider
        artifacts = []

        for item in storyboard_context:
            item_meta = item.get('metadata', {}) if isinstance(item, dict) else {}
            scene_id = (item.get('id') or item.get('scene_number') or item.get('number')
                        or item_meta.get('scene_id') or 1)
            description = item.get('description', '') or item.get('scene_description', '')
            storyboard_meta = item_meta
            camera_angle = storyboard_meta.get('camera_angle', 'medium')
            lighting = storyboard_meta.get('lighting', 'natural')

            # Enrich with the brief's rich scene data (lighting, composition,
            # camera, atmosphere) + character anchors for consistency.
            scene = brief_scenes.get(scene_id, {})
            scene_shot = scene.get("shot", {}) if isinstance(scene.get("shot", {}), dict) else {}
            prompt = self._build_prompt(scene, description, camera_angle, lighting, scene_shot)

            if provider is not None:
                # Use the real FluxComfyUIProvider
                try:
                    # Idempotency: reuse an existing rendered image for this scene.
                    existing = build_run_path(self.brief, "images", f"scene_{scene_id:03d}.png")
                    if existing.exists() and existing.stat().st_size > 10000:
                        artifact_path = str(existing)
                        logger.info(f"[ImageGenerationStage] Reusing existing image for scene {scene_id}: {artifact_path}")
                    else:
                        char_ref = self._resolve_character_reference()
                        cc = self.brief.get("character_consistency") or {}
                        intent = ImageIntent(
                            prompt=prompt,
                            negative_prompt=self._build_negative_prompt(),
                            width=self.brief.get('resolution', 1024),
                            height=int(self.brief.get('resolution', 1024) * 9 / 16),
                            # production = flux1-dev fp8, 20 steps → SHARP faces.
                            # draft (schnell, 4 steps) produces soft/blurry images.
                            quality="production",
                            # Per-scene seed so each scene gets a DISTINCT image
                            # (provider defaults to seed=42 otherwise → all identical).
                            seed=1000 + scene_id,
                            # CHARACTER CONSISTENCY (img2img): anchor every scene to
                            # the character composite (resolved from the brief's
                            # character_consistency block, or auto-detected) so all
                            # characters keep the same identity across scenes. The
                            # reference filename is relative to ComfyUI's input dir.
                            reference_image_paths=(
                                [char_ref] if char_ref else None
                            ),
                            ipadapter_strength=0.6,
                            metadata={
                                "scene_number": scene_id,
                                "output_dir": str(existing.parent),
                                "pipeline_id": self.brief.get("production", {}).get("run_id", "prometheus"),
                                # Use img2img (not IPAdapter — the IPAdapter custom
                                # node + CLIP vision model are not installed).
                                "use_img2img": True,
                                "use_ipadapter": False,
                                # Config-driven denoise from the character_consistency block.
                                "denoise": cc.get("denoise", 0.4),
                            },
                        )
                        # FluxComfyUIProvider.render is async — await directly since we're in async context
                        asset = await provider.render(intent)
                        artifact_path = str(asset.path) if hasattr(asset, 'path') else str(existing)
                        logger.info(f"[ImageGenerationStage] Generated image for scene {scene_id}: {artifact_path}")
                except Exception as e:
                    logger.warning(f"[ImageGenerationStage] FluxComfyUI failed for scene {scene_id}: {e}")
                    artifact_path = str(build_run_path(self.brief, "images", f"scene_{scene_id:03d}.png"))
            else:
                # No provider — use placeholder path
                artifact_path = str(build_run_path(self.brief, "images", f"scene_{scene_id:03d}.png"))

            artifacts.append({
                "type": "image",
                "path": artifact_path,
                "url": None,
                "metadata": {
                    "scene_id": scene_id,
                    "prompt": prompt,
                    "camera_angle": camera_angle,
                    "lighting": lighting,
                    "width": self.brief.get('resolution', 1080),
                    "height": int(self.brief.get('resolution', 1080) * 9 / 16),
                },
            })

        return {
            "artifacts": artifacts,
            "stage_name": "ImageGeneration",
            "images_generated": len(artifacts),
        }

    def _build_prompt(self, scene: dict, description: str, camera_angle: str, lighting: str, scene_shot: dict[str, Any] | None = None) -> str:
        """Build a rich cinematic prompt from the brief scene + character anchors.

        STYLE: REALISTIC CINEMATIC (adult drama / conversation piece).
        The content is a serious two-person conversation between a man and a
        woman. We push a grounded, photorealistic, cinematic look with warm
        natural lighting and sharp, expressive faces — appropriate for adult
        dialogue, NOT a cartoon. We keep it bright and well-lit (not dim/grainy)
        so faces are crisp and the emotion reads clearly.

        IMPORTANT: The brief's scene data often contains "dim, moody, grainy,
        vintage" language (from atmosphere/lighting philosophy) that produces
        DARK BLURRY images. We EXCLUDE that language and replace it with bright,
        sharp, high-clarity cinematic directives.
        """
        # Character anchors (verbatim) for consistency across scenes.
        anchors = (
            "MARK: a tall, lean man in his late 30s with warm brown skin, short black hair "
            "with a silver streak at the left temple. "
            "SARAH: a woman of medium height in her early 30s with light tan skin and long dark wavy hair."
        )
        # Realistic cinematic style block: grounded, photorealistic, warm.
        style = (
            "cinematic film still, photorealistic, realistic adult drama, "
            "natural warm lighting, shallow depth of field, "
            "sharp expressive faces, subtle skin texture, "
            "professional cinematography, high production value, "
            "crisp clean image, high detail"
        )
        # Engagement hook: both characters clearly in frame, sharp faces.
        quality = (
            "BOTH MARK and SARAH clearly visible in frame, sharp focused detailed faces, "
            "crystal-clear high resolution, bright vibrant well-lit, "
            "professional lighting, crisp clean image, "
            "natural skin tones, warm inviting atmosphere, "
            "glowing healthy skin, balanced exposure"
        )

        parts = [description] if description else []
        # NOTE: Do NOT append scene['lighting']/'atmosphere' — those contain
        # "dim", "grainy", "moody", "retro" language that yields dark blurry faces.
        if scene.get('composition'):
            c = scene['composition']
            if isinstance(c, dict) and c.get('framing'):
                parts.append(c['framing'][:200])
        if scene.get('camera_intent'):
            ci = scene['camera_intent']
            if isinstance(ci, dict) and ci.get('philosophy'):
                parts.append(ci['philosophy'][:150])
        # camera_angle defaults to 'medium' when brief data is empty — prefer a
        # two-shot/close framing that shows both people.
        if camera_angle in ("", "medium", "natural"):
            camera_angle = "two-shot medium close-up"
        shot_function = str((scene_shot or {}).get("function", "")).lower()
        if "reaction" in shot_function:
            camera_angle = "reaction close-up"
        if "speaker coverage" in shot_function:
            camera_angle = "over-the-shoulder two-shot"
        parts.append(f"{camera_angle} shot, {lighting} lighting" if lighting else f"{camera_angle} shot")
        if scene_shot:
            parts.append(f"speaker {scene_shot.get('speaker', '')}".strip())
            if scene_shot.get("performance_intent"):
                parts.append(f"performance intent {scene_shot['performance_intent']}")
            if scene_shot.get("lip_sync_required"):
                parts.append("visible lip sync")
        parts.append(style)
        parts.append(quality)
        parts.append(anchors)
        parts.append("cinematic, photorealistic, high quality, natural color grade, "
                     "bright vivid colors, high-definition, sharp detail")
        return ", ".join(p for p in parts if p)

    def _build_negative_prompt(self) -> str:
        """Negative prompt: forbid cartoon/3D-animation + dark/blurry output."""
        return ("3D animation, cartoon, Pixar, DreamWorks, anime, illustration, "
                "stylized, cel-shaded, glossy plastic skin, "
                "blurry, out of focus, soft focus, low resolution, grainy, "
                "dark, dimly lit, underexposed, vintage, retro, hazy, foggy, noise, "
                "distorted, deformed, ugly, bad anatomy, extra limbs, watermark, text")

    def create_initial_state(self, name: str = "ImageGeneration") -> dict[str, Any]:
        """Create initial stage state for pipeline bookkeeping."""
        return {
            "name": name,
            "class_name": "ImageGenerationStage",
            "stage": {
                "name": name,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "artifacts": [],
                "error": None,
            },
        }
