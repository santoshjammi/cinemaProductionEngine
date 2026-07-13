"""YAML-driven video generation pipeline.

Reads a manifest YAML, generates verified images per scene using SDXL,
then produces Ken Burns clips with edge-tts narration, and assembles the
final video.

Usage:
    python generate_from_yaml.py <manifest.yaml> [--output-dir output/videos]
"""
import sys
import os
import asyncio
import hashlib
import logging
import subprocess
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, "backend")
os.environ.setdefault("COQUI_TOS_AGREED", "1")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("yaml_pipeline")


class SDXLGenerator:
    """SDXL image generator with CLIP verification."""

    def __init__(self, manifest: dict, output_dir: str):
        self.manifest = manifest
        self.output_dir = Path(output_dir)
        self._pipe = None
        self._clip = None
        self._device = "mps"

    def _load_sdxl(self):
        if self._pipe is not None:
            return
        import torch
        from diffusers import StableDiffusionXLPipeline

        model_cfg = self.manifest["model"]
        logger.info(f"Loading SDXL: {model_cfg['name']}...")
        self._pipe = StableDiffusionXLPipeline.from_pretrained(
            model_cfg["name"],
            torch_dtype=torch.float16,
            variant="fp16",
        )
        self._pipe.to(self._device)
        logger.info("SDXL loaded on MPS")

    def _load_clip(self):
        if self._clip is not None:
            return
        import torch
        from transformers import CLIPModel, CLIPProcessor

        vcfg = self.manifest.get("verification", {})
        model_name = vcfg.get("model", "openai/clip-vit-base-patch32")
        logger.info(f"Loading CLIP: {model_name}...")
        self._clip_proc = CLIPProcessor.from_pretrained(model_name)
        self._clip = CLIPModel.from_pretrained(model_name)
        self._clip.to(self._device)
        logger.info("CLIP loaded")

    def _score_image(self, image_path: Path, prompt: str) -> float:
        import torch
        from PIL import Image

        self._load_clip()
        img = Image.open(image_path).convert("RGB")
        # CLIP has a 77-token limit. Use a shortened version of the prompt for scoring.
        # Keep the first ~200 chars which contain the most important visual elements.
        score_prompt = prompt[:200] if len(prompt) > 200 else prompt
        inputs = self._clip_proc(
            text=[score_prompt], images=img, return_tensors="pt", padding=True,
            truncation=True, max_length=77,
        ).to(self._device)
        with torch.no_grad():
            outputs = self._clip(**inputs)
            sim = outputs.logits_per_image.item() / 100.0
            score = max(0.0, min(1.0, (sim + 1.0) / 2.0))
        return score

    def _build_prompt(self, scene: dict) -> tuple[str, str]:
        """Build SDXL prompt from scene definition.

        CRITICAL: SDXL's first text encoder (CLIP ViT-L/14) has a hard
        77-token limit. Anything beyond token 77 is SILENTLY DROPPED.
        This means the most important content (scene description, subject)
        MUST come first. Shot language and style go last — they're
        supplementary and less harmful to lose.

        Priority order (highest first):
          1. PHOTOREALISM ANCHOR (cinematic, 35mm film, photorealistic) — must survive truncation
          2. Scene description (the actual subject — what to draw, CAPPED at ~50 words)
          3. Character anchors (who is in the scene, condensed)
          4. Visual cause of emotion (body language)
          5. Shot language (camera, lighting — condensed to save tokens)
          6. Color bias (style anchor — shortest)

        v1.1.1 FIX: Photorealism must NEVER be truncated. The style anchor
        is prepended to the prompt (taking priority over scene description)
        so that even if the scene description is very long, the model still
        understands the visual aesthetic. Without this, scenes with >70-word
        descriptions default to illustration/cartoon style.
        """
        from transformers import CLIPTokenizer
        if not hasattr(self, '_tokenizer'):
            self._tokenizer = CLIPTokenizer.from_pretrained(
                "openai/clip-vit-large-patch14"
            )

        vs = self.manifest["visual_system"]
        chars = self.manifest.get("characters", {})

        # v1.1.1 FIX: PHOTOREALISM ANCHOR — goes FIRST, never gets truncated.
        # This is the most important word in the prompt. The visual aesthetic
        # is established before any scene content.
        STYLE_ANCHOR = "cinematic photorealism, 35mm film grain, photorealistic, cinematic still, cinematic film still, shallow depth of field"

        # Layer 1: Scene description (MOST IMPORTANT subject — goes second)
        scene_desc = scene.get("scene_description", "").strip()

        # v1.1.1 FIX: Cap scene description to keep within budget.
        # Long descriptions push style/truncation critical content out.
        # v1.1.3: increased from 50 to 65 words now that character anchors
        # are condensed.
        words = scene_desc.split()
        if len(words) > 65:
            scene_desc = " ".join(words[:65])

        # EXPERT FEEDBACK 02 FIX 2: Inject specific environmental messiness
        # Not generic "environmental detail" — specific clutter and imperfection
        # v1.1.1 FIX: shortened from 20 words to 10 to save budget for style
        messiness_cues = "unwashed mug, dim shadows, grain, asymmetry, imperfect framing, inhabited"
        scene_desc = f"{scene_desc}, {messiness_cues}"

        # EXPERT FEEDBACK 01 FIX 1+5: "lived-in" cues
        # v1.1.1 FIX: shortened
        lived_in_suffix = "accidentally observed, not staged, documentary"
        scene_desc = f"{scene_desc}, {lived_in_suffix}"

        # EXPERT FIX 2: For warmth/contrast scenes, inject warmth cues
        beat = scene.get("beat", "")
        phase = scene.get("phase", "")
        sl = scene.get("shot_language", {})
        if beat in ("contrast_memory",) or phase in ("warmth",):
            scene_desc = f"{scene_desc}, warm golden amber light, candid intimate"
            # Override color bias for warmth scenes
            bias = "warm amber golden tones"  # NOT cool blue for warmth scenes
        else:
            palette = vs.get("color_palette", {})
            bias = palette.get("dominant", "")

        # Layer 2: Character anchors (condensed — just key traits)
        char_parts = []
        for char_key in scene.get("characters_present", []):
            char = chars.get(char_key, {})
            anchors = char.get("anchors", [])
            if anchors:
                # Use short form: "man mid-30s dark hair stubble grey shirt"
                char_parts.append(" ".join(anchors))
        char_str = ", ".join(char_parts)

        # Layer 3: Visual cause of emotion
        vc = scene.get("visual_cause_of_emotion", "").strip()

        # Layer 4: Shot language (CONDENSED — save tokens)
        # Use shortest possible forms
        shot_map = {
            "extreme_wide": "extreme wide shot",
            "wide": "wide shot",
            "medium_wide": "medium-wide",
            "medium": "medium shot",
            "medium_close": "medium close-up",
            "close_up": "close-up",
            "extreme_close_up": "extreme close-up",
            "over_shoulder": "over-shoulder",
        }
        light_map = {
            "high_key": "high-key lighting",
            "low_key": "low-key lighting, deep shadows",
            "natural": "natural light",
            "golden_hour": "golden hour light",
            "blue_hour": "blue hour twilight",
            "tungsten_warm": "warm tungsten lamp glow",
            "neon": "neon lighting",
            "silhouette": "backlit silhouette",
            "rim_lit": "rim lighting",
            "volumetric": "volumetric light",
            "overcast_soft": "soft overcast light",
            "practical_phone": "phone screen glow",
            "moonlight": "moonlight through curtains",
        }
        dof_map = {
            "shallow": "shallow DoF bokeh",
            "medium": "medium DoF",
            "deep": "deep focus",
        }

        shot_parts = []
        shot_parts.append(shot_map.get(sl.get("shot_size", "medium"), sl.get("shot_size", "medium")))
        shot_parts.append(light_map.get(sl.get("lighting_key", "low_key"), sl.get("lighting_key", "low_key")))
        if sl.get("lens_mm"):
            shot_parts.append(f"{sl['lens_mm']}mm lens")
        if sl.get("depth_of_field"):
            shot_parts.append(dof_map.get(sl["depth_of_field"], sl["depth_of_field"]))
        shot_str = ", ".join(shot_parts)

        # Assemble in PRIORITY ORDER
        # v1.1.2 FIX: STYLE_ANCHOR + CHAR_ANCHORS go FIRST so they can NEVER
        # be truncated. Character consistency is non-negotiable. The visual
        # aesthetic is non-negotiable. Only the scene description and the
        # ancillary layers (vc, shot_str, bias) can be popped.
        layers = [
            STYLE_ANCHOR,     # 1. Photorealism anchor — CANNOT be truncated
            char_str,          # 2. Character consistency — CANNOT be truncated
            scene_desc,        # 3. What to draw (subject — TRUNCATABLE)
            vc,                # 4. Body language / emotion cause
            shot_str,          # 5. Camera/lighting (condensed)
            bias,              # 6. Color style
        ]
        positive = ", ".join(filter(None, layers))

        # Verify token count and warn if over 77
        token_count = len(self._tokenizer(positive)["input_ids"])
        if token_count > 77:
            # v1.1.2 FIX: Trim from the end, but NEVER remove STYLE_ANCHOR (layer 0)
            # or CHAR_ANCHORS (layer 1). Only pop layers 2 onwards.
            # Minimum protected layers: STYLE_ANCHOR + char_str + scene_desc (3 layers)
            while token_count > 77 and len(layers) > 3:
                layers.pop()  # Remove last layer (vc/shot/bias)
                positive = ", ".join(filter(None, layers))
                token_count = len(self._tokenizer(positive)["input_ids"])

            # If still over 77, truncate scene_desc (but keep STYLE_ANCHOR + char_str)
            if token_count > 77:
                # v1.1.2 FIX: ALWAYS preserve char_str. STYLE_ANCHOR is also
                # protected. Only scene_desc gets truncated to fit the budget.
                style_len = len(self._tokenizer(STYLE_ANCHOR)["input_ids"])
                char_len = len(self._tokenizer(char_str)["input_ids"]) if char_str else 0
                overhead = 4
                max_desc_tokens = 77 - style_len - char_len - overhead
                if max_desc_tokens > 10:
                    desc_tokens = self._tokenizer(scene_desc)["input_ids"][:max_desc_tokens]
                    scene_desc_trimmed = self._tokenizer.decode(desc_tokens).replace("<|startoftext|>", "").replace("<|endoftext|>", "").strip()
                    # v1.1.2: ALWAYS include char_str (character consistency)
                    layers = [STYLE_ANCHOR, scene_desc_trimmed]
                    if char_str:
                        layers.insert(1, char_str)  # Insert char_str at position 1
                    positive = ", ".join(filter(None, layers))
                    token_count = len(self._tokenizer(positive)["input_ids"])

            # v1.1.1 SAFETY NET: if still over 77 (shouldn't happen, but tokenizer
            # decode can produce more tokens than we budgeted for due to
            # subword boundary effects), hard-truncate by characters
            if token_count > 77:
                positive = positive[:280]  # ~77 tokens worth of text
                token_count = len(self._tokenizer(positive)["input_ids"])

            logger.info(f"  Token count: {token_count}/77 (trimmed to fit CLIP limit)")

        negative = vs.get("negative_prompt", "")
        # v1.1.1 FIX: aggressively block illustration/cartoon styles.
        # The previous run was rendering as illustration because the style
        # anchor was truncated out. The negative prompt catches what the
        # positive prompt couldn't fit.
        negative = (
            f"{negative}, "
            "cartoon, anime, illustration, painting, drawing, "
            "comic book, comic, graphic novel, storyboard, "
            "2d art, line art, ink drawing, pencil sketch, "
            "vector art, digital illustration, painted, watercolor, "
            "cel shaded, manga, webtoon, "
            "3d render, cgi, video game, "
            "staged, perfect, smooth, airbrushed, digital art, concept art, clean, polished"
        )
        return positive, negative

    def generate_scene_image(self, pipeline_id: str, scene: dict) -> dict:
        """Generate a verified image for a single scene.

        If hero reference images exist in the niche's characters/ directory,
        uses img2img from the hero to maintain character consistency.
        Otherwise, falls back to txt2img with character anchors.
        """
        import torch

        self._load_sdxl()

        gen_cfg = self.manifest.get("generation", {})
        num_candidates = gen_cfg.get("num_candidates", 4)
        min_score = gen_cfg.get("min_clip_score", 0.30)
        max_rounds = gen_cfg.get("max_refine_rounds", 2)
        seeds = gen_cfg.get("candidate_seeds", [42, 137, 1024, 7777])
        refine_seeds = gen_cfg.get("refinement_seeds", [314, 2718, 9999, 5678])
        char_strength = gen_cfg.get("character_reference_strength", 0.45)

        res = self.manifest["model"]["resolution"]
        width, height = res["width"], res["height"]
        steps = gen_cfg.get("num_inference_steps", 30)
        guidance = gen_cfg.get("guidance_scale", 7.5)

        scene_num = scene["scene_number"]
        title = scene.get("title", f"Scene {scene_num}")
        characters_in_scene = scene.get("characters_present", [])

        img_dir = self.output_dir / pipeline_id / "scene_images"
        cand_dir = self.output_dir / pipeline_id / "candidates"
        img_dir.mkdir(parents=True, exist_ok=True)
        cand_dir.mkdir(parents=True, exist_ok=True)

        output_path = img_dir / f"scene_{scene_num:03d}.png"

        # Skip if already exists
        if output_path.exists():
            logger.info(f"  Scene {scene_num}: already exists, skipping")
            return {"scene_number": scene_num, "status": "completed", "clip_score": 1.0}

        positive, negative = self._build_prompt(scene)

        # Check for hero reference images
        hero_paths = self._find_hero_references(characters_in_scene)

        use_img2img = bool(hero_paths)
        if use_img2img:
            logger.info(f"  Character references: {[h.name for h in hero_paths]}")

        logger.info(f"\n{'='*60}")
        logger.info(f"Scene {scene_num}: {title}")
        logger.info(f"  Mode: {'img2img (character consistent)' if use_img2img else 'txt2img'}")
        logger.info(f"  Prompt ({len(positive)} chars): {positive[:200]}...")
        logger.info(f"  Candidates: {num_candidates}, Min score: {min_score}")

        current_pos = positive
        current_neg = negative
        best_image = None
        best_score = 0.0
        best_seed = 0

        for round_num in range(max_rounds + 1):
            round_seeds = seeds if round_num == 0 else refine_seeds

            logger.info(f"  Round {round_num + 1}/{max_rounds + 1}")

            candidates = []
            for i in range(num_candidates):
                seed = round_seeds[i % len(round_seeds)]
                gen = torch.Generator(device=self._device)
                gen.manual_seed(seed)

                cand_path = cand_dir / f"scene_{scene_num:03d}_r{round_num}_c{i}.png"

                logger.info(f"    Candidate {i+1}/{num_candidates} (seed={seed})...")

                if use_img2img and hero_paths:
                    # Use first character's hero as reference
                    hero_img = self._load_hero_image(hero_paths[0], width, height)
                    if hero_img is not None:
                        result = self._pipe(
                            prompt=current_pos,
                            negative_prompt=current_neg,
                            image=hero_img,
                            strength=char_strength,
                            num_inference_steps=steps,
                            guidance_scale=guidance,
                            height=height,
                            width=width,
                            generator=gen,
                        ).images[0]
                    else:
                        result = self._pipe(
                            prompt=current_pos,
                            negative_prompt=current_neg,
                            num_inference_steps=steps,
                            guidance_scale=guidance,
                            height=height,
                            width=width,
                            generator=gen,
                        ).images[0]
                else:
                    result = self._pipe(
                        prompt=current_pos,
                        negative_prompt=current_neg,
                        num_inference_steps=steps,
                        guidance_scale=guidance,
                        height=height,
                        width=width,
                        generator=gen,
                    ).images[0]

                result.save(str(cand_path))
                candidates.append(cand_path)

            # Score with CLIP
            self._load_clip()
            scored = []
            for c in candidates:
                score = self._score_image(c, current_pos)
                scored.append((c, score))
                logger.info(f"      {c.name}: {score:.4f}")

            scored.sort(key=lambda x: x[1], reverse=True)
            round_best_path, round_best_score = scored[0]

            if round_best_score > best_score:
                best_score = round_best_score
                best_image = round_best_path
                best_seed = round_seeds[round_num * num_candidates % len(seeds)]

            logger.info(f"    Best: {round_best_score:.4f} (threshold: {min_score})")

            if round_best_score >= min_score:
                logger.info(f"    ACCEPTED")
                break

            # Refine
            if round_num < max_rounds:
                logger.info(f"    Refining prompt...")
                if len(current_pos) > 300:
                    current_pos = current_pos[:297].rsplit(", ", 1)[0]
                current_pos = f"{current_pos}, sharp focus, well-composed, clear subject"
                current_neg = f"{current_neg}, duplicate, cloned, overlapping, messy, chaotic"

        # Save best
        if best_image:
            import shutil
            shutil.copy2(best_image, output_path)
            logger.info(f"  Saved: {output_path.name} (score={best_score:.4f})")

            for c in cand_dir.glob(f"scene_{scene_num:03d}_*.png"):
                c.unlink()

        return {
            "scene_number": scene_num,
            "status": "completed" if best_image else "failed",
            "clip_score": best_score,
            "seed": best_seed,
            "rounds": round_num + 1,
            "prompt": current_pos,
            "used_character_reference": use_img2img,
        }

    def _find_hero_references(self, character_keys: list[str]) -> list[Path]:
        """Find hero reference images in the niche's characters/ directory."""
        # Get the niche directory from the manifest path
        manifest_path = self.manifest.get("__manifest_path__", "")
        if not manifest_path:
            return []

        niche_dir = Path(manifest_path).parent
        chars_dir = niche_dir / "characters"

        if not chars_dir.exists():
            return []

        heroes = []
        for char_key in character_keys:
            for ext in ['.png', '.jpg', '.jpeg']:
                hero = chars_dir / f"{char_key}_hero{ext}"
                if hero.exists():
                    heroes.append(hero)
                    break

        return heroes

    def _load_hero_image(self, hero_path: Path, width: int, height: int):
        """Load and resize hero image for img2img."""
        from PIL import Image
        try:
            img = Image.open(hero_path).convert("RGB")
            img = img.resize((width, height), Image.LANCZOS)
            return img
        except Exception as e:
            logger.error(f"Failed to load hero image {hero_path}: {e}")
            return None


class VideoAssembler:
    """Ken Burns + TTS + final assembly."""

    def __init__(self, manifest: dict, output_dir: str):
        self.manifest = manifest
        self.output_dir = Path(output_dir)

    async def generate_scene_video(self, pipeline_id: str, scene: dict, image_path: Path) -> dict:
        import sys
        sys.path.insert(0, "backend")
        from app.services.video_service import VideoGenerationService
        from app.services.tts_service import TTSService

        video_svc = VideoGenerationService(str(self.output_dir))
        tts_svc = TTSService(str(self.output_dir))

        scene_num = scene["scene_number"]
        vo = scene.get("voiceover", "").strip()
        effect = scene.get("ken_burns_effect", "ken-burns")

        # TTS
        if vo:
            result = await tts_svc.generate_speech(pipeline_id, scene_num, vo)
            if result["status"] != "completed":
                return {"error": f"TTS failed: {result.get('error')}"}
            audio_dur = tts_svc.get_audio_duration(pipeline_id, scene_num)
        else:
            audio_dur = 8.0

        # Ken Burns
        clip = video_svc.generate_ken_burns_clip(
            pipeline_id, scene_num, image_path, audio_dur, effect,
        )
        if clip is None:
            return {"error": "Ken Burns failed"}

        # Merge
        if vo:
            merged = tts_svc.merge_audio_with_video(pipeline_id, scene_num)
            if merged is None:
                return {"error": "Merge failed"}

        return {
            "scene_number": scene_num,
            "audio_duration": audio_dur,
            "effect": effect,
            "clip": str(clip),
        }

    def assemble_final(self, pipeline_id: str, num_scenes: int) -> Path:
        final_dir = self.output_dir / pipeline_id
        final_clips = sorted((final_dir / "final_clips").glob("scene_*.mp4"))
        if not final_clips:
            # Fallback to clips without audio
            final_clips = sorted((final_dir / "clips").glob("scene_*.mp4"))

        concat = final_dir / "concat.txt"
        with open(concat, "w") as f:
            for c in final_clips:
                f.write(f"file '{c.resolve()}'\n")

        out = final_dir / "final.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", str(concat), "-c", "copy", str(out)],
            check=True, capture_output=True,
        )
        return out


async def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_from_yaml.py <manifest.yaml>")
        sys.exit(1)

    manifest_path = sys.argv[1]
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    # Derive pipeline ID from manifest filename
    pid = Path(manifest_path).stem.replace("_sdxl", "").lower()
    output_dir = "output/videos"

    print(f"{'='*60}")
    print(f"YAML-Driven Video Generation")
    print(f"{'='*60}")
    print(f"Manifest: {manifest_path}")
    print(f"Pipeline: {pid}")
    print(f"Model: {manifest['model']['name']}")
    print(f"Scenes: {len(manifest['scenes'])}")
    print(f"Resolution: {manifest['model']['resolution']['width']}x{manifest['model']['resolution']['height']}")
    print(f"Steps: {manifest['generation']['num_inference_steps']}")
    print(f"Candidates per scene: {manifest['generation']['num_candidates']}")
    print(f"CLIP min score: {manifest['generation']['min_clip_score']}")
    print()

    # Phase 1: Generate verified images
    # Inject manifest path so generator can find character hero references
    manifest["__manifest_path__"] = str(manifest_path)
    generator = SDXLGenerator(manifest, output_dir)
    image_results = []
    for scene in manifest["scenes"]:
        result = generator.generate_scene_image(pid, scene)
        image_results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("IMAGE GENERATION SUMMARY")
    print(f"{'='*60}")
    for r in image_results:
        score = r.get("clip_score", 0)
        status = "OK" if score >= manifest["generation"]["min_clip_score"] else "LOW"
        print(f"  Scene {r['scene_number']}: CLIP={score:.4f} [{status}]")

    # Phase 2: Generate video
    print(f"\n{'='*60}")
    print("VIDEO GENERATION")
    print(f"{'='*60}")

    assembler = VideoAssembler(manifest, output_dir)
    for scene in manifest["scenes"]:
        scene_num = scene["scene_number"]
        img = Path(output_dir) / pid / "scene_images" / f"scene_{scene_num:03d}.png"
        if not img.exists():
            print(f"  Scene {scene_num}: No image, skipping")
            continue

        print(f"\n--- Scene {scene_num}: {scene.get('title', '')} ---")
        result = await assembler.generate_scene_video(pid, scene, img)
        if "error" in result:
            print(f"  ERROR: {result['error']}")
        else:
            print(f"  Audio: {result.get('audio_duration', 0):.1f}s")
            print(f"  Effect: {result.get('effect', '')}")
            print(f"  Clip: {Path(result['clip']).name}")

    # Phase 3: Assemble
    print(f"\n--- Assembling final video ---")
    final = assembler.assemble_final(pid, len(manifest["scenes"]))

    # Verify
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,sample_rate,duration:format=duration,size",
         "-of", "default=noprint_wrappers=1", str(final)],
        capture_output=True, text=True,
    )
    print(f"\n{probe.stdout}")
    print(f"File: {final}")
    print(f"Size: {final.stat().st_size / (1024*1024):.1f} MB")
    print(f"\nPlay: open {final}")


if __name__ == "__main__":
    asyncio.run(main())