#!/usr/bin/env python3
"""Generate hero reference images for character consistency.

Creates one high-quality portrait per character in the niche.
These hero images are then used as the reference (via img2img) for
all scene images, ensuring the same face/body appears across scenes.

Usage:
    python generate_heroes.py --niche EmotionalWithdrawal [--regenerate husband]
    python generate_heroes.py --niche EmotionalWithdrawal --seed 100
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, "backend")

import yaml


async def main():
    parser = argparse.ArgumentParser(description="Generate hero character images")
    parser.add_argument("--niche", required=True, help="Niche directory name (e.g., EmotionalWithdrawal)")
    parser.add_argument("--project-root", default="videoContentStructure/Psychology",
                        help="Root directory of niches")
    parser.add_argument("--regenerate", default=None, help="Regenerate specific character only")
    parser.add_argument("--seed", type=int, default=42, help="Base seed for hero generation")
    parser.add_argument("--width", type=int, default=768, help="Hero image width")
    parser.add_argument("--height", type=int, default=768, help="Hero image height")
    args = parser.parse_args()

    niche_dir = Path(args.project_root) / args.niche
    if not niche_dir.exists():
        print(f"Niche directory not found: {niche_dir}")
        return

    # Find a manifest in this niche
    manifests = list(niche_dir.glob("VID*_template*.yaml")) + list(niche_dir.glob("VID*_generated*.yaml"))
    if not manifests:
        print(f"No manifest found in {niche_dir}")
        return

    manifest_path = manifests[0]
    print(f"Using manifest: {manifest_path.name}")

    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    characters = manifest.get("characters", {})
    if not characters:
        print("No characters defined in manifest")
        return

    # Create characters directory
    chars_dir = niche_dir / "characters"
    chars_dir.mkdir(parents=True, exist_ok=True)

    # Setup image service
    from app.services.image_service import ImageGenerationService
    import os
    os.environ.setdefault("COQUI_TOS_AGREED", "1")

    output_dir = "output/videos"
    service = ImageGenerationService(output_dir)

    # Generate hero for each character
    seeds = {
        "husband": args.seed,
        "wife": args.seed + 100,
    }

    for char_key, char_data in characters.items():
        if args.regenerate and char_key != args.regenerate:
            continue

        name = char_data.get("name", char_key)
        anchors = char_data.get("anchors", [])
        if not anchors:
            print(f"  Skipping {char_key}: no anchors")
            continue

        hero_path = chars_dir / f"{char_key}_hero.png"
        seed = seeds.get(char_key, args.seed)

        if hero_path.exists() and not args.regenerate:
            print(f"  {char_key}_hero.png already exists, skipping (use --regenerate to overwrite)")
            continue

        print(f"\nGenerating hero for {name} ({char_key})...")
        print(f"  Anchors: {', '.join(anchors)}")

        try:
            result = await service.generate_hero_image(
                character_key=char_key,
                character_name=name,
                character_anchors=anchors,
                emotional_state="neutral",
                output_path=hero_path,
                seed=seed,
                width=args.width,
                height=args.height,
            )
            print(f"  Saved: {result['path']}")
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n=== Hero images saved to: {chars_dir} ===")
    print("Open the images to review. If the face/body doesn't look right:")
    print(f"  python scripts/generate_heroes.py --niche {args.niche} --regenerate husband --seed 50")
    print("Or edit the anchors in the manifest to be more specific.")


if __name__ == "__main__":
    asyncio.run(main())