import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger("image_service")


class ImageGenerationState:
    def __init__(self, total_scenes: int = 0):
        self.images: dict[int, dict] = {}
        self.created_at: float = time.time()
        self.total_scenes: int = total_scenes

    def set_image(self, scene_number: int, data: dict):
        if scene_number > self.total_scenes:
            self.total_scenes = scene_number
        self.images[scene_number] = data

    def get_image(self, scene_number: int) -> Optional[dict]:
        return self.images.get(scene_number)

    def get_all_images(self) -> list[dict]:
        return [v for k, v in sorted(self.images.items())]

    def is_done(self) -> bool:
        return self.total_scenes > 0 and len(self.images) >= self.total_scenes and all(
            img.get("status") in ("completed", "failed") for img in self.images.values()
        )


_image_states: dict[str, ImageGenerationState] = {}

_latest_image_cleanup: float = time.time()


def get_image_state(pipeline_id: str, total_scenes: int = 0) -> ImageGenerationState:
    _maybe_cleanup_images()
    if pipeline_id not in _image_states:
        _image_states[pipeline_id] = ImageGenerationState(total_scenes=total_scenes)
    return _image_states[pipeline_id]


def remove_image_state(pipeline_id: str):
    _image_states.pop(pipeline_id, None)


def _maybe_cleanup_images():
    global _latest_image_cleanup
    now = time.time()
    if now - _latest_image_cleanup < 300:
        return
    _latest_image_cleanup = now
    stale = [
        pid
        for pid, state in list(_image_states.items())
        if state.is_done() and now - state.created_at > 60
    ]
    for pid in stale:
        _image_states.pop(pid, None)
    if stale:
        logger.info("Cleaned up %d stale image states", len(stale))


class ImageGenerationService:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._pipeline = None

    def _load_model(self):
        if self._pipeline is not None:
            return
        try:
            import torch
            from diffusers import StableDiffusionPipeline

            device = "mps" if torch.backends.mps.is_available() else "cpu"
            dtype = torch.float16 if device != "cpu" else torch.float32

            logger.info("Loading Stable Diffusion for scene image generation...")
            self._pipeline = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=dtype,
                safety_checker=None,
            )
            self._pipeline.to(device)
            logger.info("SD model loaded on %s for image generation", device)
        except Exception as e:
            logger.error("Failed to load image model: %s", e)
            raise

    def get_image_path(self, pipeline_id: str, scene_number: int) -> Optional[Path]:
        path = (
            self.output_dir
            / pipeline_id
            / "scene_images"
            / f"scene_{scene_number:03d}.png"
        )
        return path if path.exists() else None

    async def generate_scene_image_with_prompts(
        self,
        pipeline_id: str,
        scene_number: int,
        positive_prompt: str,
        negative_prompt: str,
        seed: int = 42,
        output_path: Path | None = None,
        width: int = 1024,
        height: int = 576,
    ) -> dict:
        """Generate an image using custom positive/negative prompts with a fixed seed."""
        import torch

        if output_path is None:
            img_dir = self.output_dir / pipeline_id / "scene_images"
            img_dir.mkdir(parents=True, exist_ok=True)
            output_path = img_dir / f"scene_{scene_number:03d}.png"

        self._load_model()

        generator = torch.Generator(device="mps" if torch.backends.mps.is_available() else "cpu")
        generator.manual_seed(seed)

        logger.info("Generating scene %d with seed %d", scene_number, seed)
        result = self._pipeline(
            positive_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=40,
            guidance_scale=8.0,
            height=height,
            width=width,
            generator=generator,
        ).images[0]

        result.save(str(output_path))
        logger.info("Scene image %d saved to %s", scene_number, output_path)

        return {
            "scene_number": scene_number,
            "status": "completed",
            "image_url": f"/api/v1/pipeline/{pipeline_id}/image/{scene_number}",
            "progress": 1.0,
            "error": None,
            "seed": seed,
        }

    async def generate_scene_image_with_character_reference(
        self,
        pipeline_id: str,
        scene_number: int,
        positive_prompt: str,
        negative_prompt: str,
        character_key: str,
        characters_dir: Path,
        seed: int = 42,
        output_path: Path | None = None,
        width: int = 1024,
        height: int = 576,
        strength: float = 0.45,
    ) -> dict:
        """Generate a scene image using img2img with a character hero reference.

        This maintains character consistency across scenes by using the
        hero image as a starting point. The strength parameter controls
        how much the scene can deviate from the hero:
          - 0.3 = very faithful to hero face, less scene flexibility
          - 0.45 = balanced (recommended)
          - 0.6 = more scene flexibility, less character fidelity
        """
        import torch
        from PIL import Image

        if output_path is None:
            img_dir = self.output_dir / pipeline_id / "scene_images"
            img_dir.mkdir(parents=True, exist_ok=True)
            output_path = img_dir / f"scene_{scene_number:03d}.png"

        self._load_model()

        # Find hero image for this character
        hero_path = characters_dir / f"{character_key}_hero.png"
        if not hero_path.exists():
            # Try alternate names
            for ext in ['.png', '.jpg', '.jpeg']:
                alt = characters_dir / f"{character_key}_hero{ext}"
                if alt.exists():
                    hero_path = alt
                    break

        if not hero_path.exists():
            logger.warning(f"No hero image for {character_key} at {hero_path}, falling back to txt2img")
            return await self.generate_scene_image_with_prompts(
                pipeline_id, scene_number, positive_prompt, negative_prompt,
                seed, output_path, width, height,
            )

        # Load hero image and resize to target dimensions
        hero = Image.open(hero_path).convert("RGB")
        hero = hero.resize((width, height), Image.LANCZOS)

        generator = torch.Generator(device="mps" if torch.backends.mps.is_available() else "cpu")
        generator.manual_seed(seed)

        logger.info(f"Generating scene {scene_number} (img2img, hero={hero_path.name}, strength={strength})")

        result = self._pipeline(
            positive_prompt,
            negative_prompt=negative_prompt,
            image=hero,
            strength=strength,
            num_inference_steps=40,
            guidance_scale=8.0,
            generator=generator,
        ).images[0]

        result.save(str(output_path))
        logger.info(f"Scene image {scene_number} saved to {output_path}")

        return {
            "scene_number": scene_number,
            "status": "completed",
            "image_url": f"/api/v1/pipeline/{pipeline_id}/image/{scene_number}",
            "progress": 1.0,
            "error": None,
            "seed": seed,
            "hero": str(hero_path.name),
            "strength": strength,
        }

    async def generate_hero_image(
        self,
        character_key: str,
        character_name: str,
        character_anchors: list[str],
        emotional_state: str = "neutral",
        output_path: Path | None = None,
        seed: int = 42,
        width: int = 768,
        height: int = 768,
    ) -> dict:
        """Generate a hero reference image for a character.

        Creates a clear, simple portrait that will be used as the
        reference for all scenes featuring this character.
        """
        import torch

        if output_path is None:
            raise ValueError("output_path is required for hero image generation")

        self._load_model()

        anchor_str = ", ".join(character_anchors)
        if emotional_state == "neutral":
            prompt = f"simple clear portrait photo of {anchor_str}, front-facing, soft natural lighting, neutral expression, plain background, high quality photograph, real person, realistic, photorealistic"
        else:
            prompt = f"simple clear portrait photo of {anchor_str}, front-facing, soft natural lighting, {emotional_state} expression, plain background, high quality photograph, real person, realistic, photorealistic"

        negative = "cartoon, anime, illustration, painting, 3d render, cgi, video game, blurry, low quality, distorted, deformed, disfigured, bad anatomy, extra limbs, extra fingers, watermark, signature, text, oversaturated, hdr, plastic skin, duplicate, cloned, multiple scenes, collage"

        generator = torch.Generator(device="mps" if torch.backends.mps.is_available() else "cpu")
        generator.manual_seed(seed)

        logger.info(f"Generating hero image for {character_name} ({character_key})")

        result = self._pipeline(
            prompt,
            negative_prompt=negative,
            num_inference_steps=40,
            guidance_scale=8.0,
            height=height,
            width=width,
            generator=generator,
        ).images[0]

        result.save(str(output_path))
        logger.info(f"Hero image saved to {output_path}")

        return {
            "character_key": character_key,
            "character_name": character_name,
            "status": "completed",
            "path": str(output_path),
            "seed": seed,
        }

    async def generate_scene_image(
        self,
        pipeline_id: str,
        scene_number: int,
        cinematic_prompt: str,
        negative_prompt: str = "",
    ) -> dict:
        state = get_image_state(pipeline_id)
        img_dir = self.output_dir / pipeline_id / "scene_images"
        img_dir.mkdir(parents=True, exist_ok=True)
        output_path = img_dir / f"scene_{scene_number:03d}.png"

        try:
            state.set_image(scene_number, {
                "scene_number": scene_number,
                "status": "generating",
                "progress": 0.1,
            })

            self._load_model()

            if output_path.exists():
                logger.info("Image already exists for scene %d", scene_number)
                result = {
                    "scene_number": scene_number,
                    "status": "completed",
                    "image_url": f"/api/v1/pipeline/{pipeline_id}/image/{scene_number}",
                    "progress": 1.0,
                    "error": None,
                }
                state.set_image(scene_number, result)
                return result

            state.set_image(scene_number, {
                "scene_number": scene_number,
                "status": "generating",
                "progress": 0.3,
            })

            enhanced_prompt = (
                f"{cinematic_prompt}, cinematic, highly detailed, 4k, "
                f"professional lighting, photorealistic, film still, shot on Arri Alexa"
            )
            full_negative = (
                f"{negative_prompt}, cartoon, painting, illustration, "
                f"blurry, low quality, distorted, deformed"
            )

            import torch
            result = self._pipeline(
                enhanced_prompt,
                negative_prompt=full_negative,
                num_inference_steps=30,
                guidance_scale=7.5,
                height=576,
                width=1024,
            ).images[0]

            result.save(str(output_path))
            logger.info("Scene image %d saved to %s", scene_number, output_path)

            result_data = {
                "scene_number": scene_number,
                "status": "completed",
                "image_url": f"/api/v1/pipeline/{pipeline_id}/image/{scene_number}",
                "progress": 1.0,
                "error": None,
            }
            state.set_image(scene_number, result_data)
            return result_data

        except Exception as e:
            logger.exception("Failed to generate image for scene %d", scene_number)
            result = {
                "scene_number": scene_number,
                "status": "failed",
                "error": str(e),
                "progress": 0,
            }
            state.set_image(scene_number, result)
            return result
