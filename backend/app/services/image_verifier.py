"""Chain-of-verification image generation pipeline.

Flow:
  1. Generate N candidate images per scene (different seeds)
  2. Score each candidate against the prompt using CLIP similarity
  3. Pick the highest-scoring candidate
  4. If best score < threshold, refine prompt and regenerate
  5. Save best candidate as the final scene image

Uses OpenAI CLIP (ViT-B/32) for image-text similarity scoring.
"""
import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger("image_verifier")


class CLIPVerifier:
    """CLIP-based image-text similarity scorer."""

    def __init__(self):
        self._model = None
        self._processor = None

    def _load(self):
        if self._model is not None:
            return
        import torch
        from transformers import CLIPModel, CLIPProcessor

        logger.info("Loading CLIP model (ViT-B/32)...")
        self._processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self._model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        self._model.to(device)
        self._device = device
        logger.info("CLIP model loaded on %s", device)

    def score_image(self, image, prompt: str) -> float:
        """Score how well an image matches a text prompt. Returns 0.0-1.0."""
        import torch
        from PIL import Image as PILImage

        self._load()

        if isinstance(image, (str, Path)):
            image = PILImage.open(image).convert("RGB")

        inputs = self._processor(
            text=[prompt],
            images=image,
            return_tensors="pt",
            padding=True,
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model(**inputs)
            # logits_per_image: cosine similarity * 100
            similarity = outputs.logits_per_image.item() / 100.0
            # Convert to probability-like score
            score = max(0.0, min(1.0, (similarity + 1.0) / 2.0))

        return score

    def score_candidates(self, candidates: list[Path], prompt: str) -> list[tuple[Path, float]]:
        """Score multiple candidate images against a prompt. Returns sorted by score descending."""
        scored = []
        for img_path in candidates:
            score = self.score_image(img_path, prompt)
            scored.append((img_path, score))
            logger.info("  Candidate %s: CLIP score %.4f", img_path.name, score)
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored


class VerifiedImageGenerator:
    """Generate images with chain-of-verification using SD v1.5 + CLIP."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._pipeline = None
        self._verifier = CLIPVerifier()

    def _load_model(self):
        if self._pipeline is not None:
            return
        import torch
        from diffusers import StableDiffusionPipeline

        device = "mps" if torch.backends.mps.is_available() else "cpu"
        dtype = torch.float16 if device != "cpu" else torch.float32

        logger.info("Loading Stable Diffusion v1.5 for image generation...")
        self._pipeline = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=dtype,
            safety_checker=None,
        )
        self._pipeline.to(device)
        self._device = device
        logger.info("SD v1.5 loaded on %s", device)

    def generate_verified_image(
        self,
        pipeline_id: str,
        scene_number: int,
        positive_prompt: str,
        negative_prompt: str,
        num_candidates: int = 4,
        min_score: float = 0.25,
        max_refine_rounds: int = 2,
        seeds: list[int] | None = None,
        width: int = 1024,
        height: int = 576,
    ) -> dict:
        """Generate image with chain-of-verification.

        Args:
            num_candidates: How many candidate images to generate per round
            min_score: Minimum CLIP score to accept (0.0-1.0)
            max_refine_rounds: How many times to refine prompt and retry
            seeds: Optional list of seeds to use (must be >= num_candidates)
        """
        import torch

        self._load_model()

        img_dir = self.output_dir / pipeline_id / "scene_images"
        candidate_dir = self.output_dir / pipeline_id / "candidates"
        img_dir.mkdir(parents=True, exist_ok=True)
        candidate_dir.mkdir(parents=True, exist_ok=True)

        output_path = img_dir / f"scene_{scene_number:03d}.png"

        if seeds is None:
            seeds = [42 + i * 100 for i in range(num_candidates * (max_refine_rounds + 1))]

        current_prompt = positive_prompt
        current_negative = negative_prompt
        best_image = None
        best_score = 0.0
        best_seed = 0

        for round_num in range(max_refine_rounds + 1):
            logger.info(
                "Scene %d — Round %d/%d — Generating %d candidates",
                scene_number, round_num + 1, max_refine_rounds + 1, num_candidates,
            )

            candidates: list[Path] = []
            round_start_seed_idx = round_num * num_candidates

            for i in range(num_candidates):
                seed_idx = round_start_seed_idx + i
                seed = seeds[seed_idx % len(seeds)]

                gen = torch.Generator(device=self._device)
                gen.manual_seed(seed)

                candidate_path = candidate_dir / f"scene_{scene_number:03d}_r{round_num}_c{i}.png"

                logger.info(
                    "  Generating candidate %d/%d (seed=%d)...",
                    i + 1, num_candidates, seed,
                )

                result = self._pipeline(
                    current_prompt,
                    negative_prompt=current_negative,
                    num_inference_steps=40,
                    guidance_scale=8.0,
                    height=height,
                    width=width,
                    generator=gen,
                ).images[0]

                result.save(str(candidate_path))
                candidates.append(candidate_path)

            # Score candidates
            logger.info("  Scoring %d candidates with CLIP...", len(candidates))
            scored = self._verifier.score_candidates(candidates, current_prompt)

            round_best_path, round_best_score = scored[0]
            logger.info(
                "  Best this round: %.4f (threshold: %.2f)",
                round_best_score, min_score,
            )

            if round_best_score > best_score:
                best_score = round_best_score
                best_image = round_best_path
                best_seed = seeds[round_start_seed_idx % len(seeds)]

            # Accept if above threshold
            if round_best_score >= min_score:
                logger.info("  ACCEPTED — score %.4f >= %.2f", round_best_score, min_score)
                break

            # Refine prompt for next round
            if round_num < max_refine_rounds:
                logger.info("  Score below threshold — refining prompt...")
                current_prompt, current_negative = self._refine_prompt(
                    current_prompt, current_negative, round_best_score,
                )
                logger.info("  Refined prompt: %s", current_prompt[:150])

        # Copy best candidate to final output
        if best_image:
            import shutil
            shutil.copy2(best_image, output_path)
            logger.info(
                "Scene %d final image: %s (score=%.4f, seed=%d)",
                scene_number, output_path.name, best_score, best_seed,
            )

            # Clean up candidates
            for c in candidate_dir.glob(f"scene_{scene_number:03d}_*.png"):
                c.unlink()

        return {
            "scene_number": scene_number,
            "status": "completed" if best_image else "failed",
            "image_url": f"/api/v1/pipeline/{pipeline_id}/image/{scene_number}",
            "progress": 1.0,
            "error": None if best_image else "No image generated",
            "clip_score": best_score,
            "seed": best_seed,
            "rounds": round_num + 1,
        }

    def _refine_prompt(
        self, prompt: str, negative: str, current_score: float,
    ) -> tuple[str, str]:
        """Refine the prompt based on the current score."""
        # If score is very low, simplify the prompt to its core elements
        if current_score < 0.15:
            # Strip to essentials — keep first 150 chars
            if len(prompt) > 150:
                prompt = prompt[:150].rsplit(", ", 1)[0]
            # Add quality boosters
            prompt = f"{prompt}, sharp focus, detailed, clear composition"
        else:
            # Score is moderate — add specificity
            prompt = f"{prompt}, well-composed, clear subject, proper framing"

        # Add more negative prompts to avoid common SD failures
        negative = (
            f"{negative}, duplicate, cloned, overlapping subjects, "
            f"messy composition, chaotic, multiple scenes, collage"
        )

        return prompt, negative