#!/usr/bin/env python3
"""Regenerate VID01 images using cinematic prompt engineering + SD v1.5.

Uses:
- 5-aspect skeleton (Subject/Motion/Scene/Spatial/Camera)
- Identity anchoring (verbatim character attributes per scene)
- Fixed seed for visual consistency
- 40 inference steps, guidance scale 8.0
- 1024x576 cinematic aspect ratio
"""
import sys
import os
import asyncio
import shutil
from pathlib import Path

sys.path.insert(0, "backend")
os.environ.setdefault("COQUI_TOS_AGREED", "1")

from app.services.cinematic_prompts import get_vid01_prompts
from app.services.image_service import ImageGenerationService

OUTPUT_DIR = "output/videos"
PID = "vid01-v2"

image_service = ImageGenerationService(OUTPUT_DIR)

# Copy existing images as backup
BACKUP_DIR = Path(OUTPUT_DIR) / "vid01-edge-tts" / "scene_images_backup"
if not BACKUP_DIR.exists():
    old_images = Path(OUTPUT_DIR) / "vid01-edge-tts" / "scene_images"
    if old_images.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        for f in old_images.glob("*.png"):
            shutil.copy2(f, BACKUP_DIR / f.name)
        print(f"Backed up {len(list(BACKUP_DIR.glob('*.png')))} old images to {BACKUP_DIR}")


async def generate_all_images():
    prompts = get_vid01_prompts()

    # Use a fixed seed for all scenes for character consistency
    FIXED_SEED = 42

    for prompt_data in prompts:
        scene_num = prompt_data["scene_number"]
        positive = prompt_data["positive_prompt"]
        negative = prompt_data["negative_prompt"]

        print(f"\n{'='*70}")
        print(f"Scene {scene_num}: {prompt_data['title']}")
        print(f"Characters: {prompt_data['characters']}")
        print(f"Emotional beat: {prompt_data['emotional_beat']}")
        print(f"\nPrompt ({len(positive)} chars):")
        print(f"  {positive[:200]}...")
        print(f"\nNegative:")
        print(f"  {negative[:150]}...")

        # Generate directly using SD pipeline with our custom prompts
        img_dir = Path(OUTPUT_DIR) / PID / "scene_images"
        img_dir.mkdir(parents=True, exist_ok=True)
        output_path = img_dir / f"scene_{scene_num:03d}.png"

        if output_path.exists():
            print(f"  Already exists, skipping")
            continue

        print(f"\n  Generating with SD v1.5 (seed={FIXED_SEED}, 40 steps)...")
        await image_service.generate_scene_image_with_prompts(
            pipeline_id=PID,
            scene_number=scene_num,
            positive_prompt=positive,
            negative_prompt=negative,
            seed=FIXED_SEED,
            output_path=output_path,
        )
        print(f"  Saved: {output_path}")


if __name__ == "__main__":
    print("="*70)
    print("VID01 Image Regeneration — Cinematic Prompt Engineering")
    print("="*70)
    print(f"Pipeline: {PID}")
    print(f"Output: {OUTPUT_DIR}/{PID}/scene_images/")
    print()
    asyncio.run(generate_all_images())
    print(f"\nDone! Images in: {OUTPUT_DIR}/{PID}/scene_images/")