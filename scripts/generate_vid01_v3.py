#!/usr/bin/env python3
"""Regenerate VID01 images with chain-of-verification.

For each scene:
  1. Generate 4 candidate images (different seeds)
  2. Score each with CLIP against the prompt
  3. Pick the best candidate
  4. If score < 0.28, refine prompt and try again (max 2 rounds)
  5. Save best image

Then generate the final video with edge-tts + Ken Burns.
"""
import sys
import os
import asyncio
import subprocess
from pathlib import Path

sys.path.insert(0, "backend")
os.environ.setdefault("COQUI_TOS_AGREED", "1")

from app.services.cinematic_prompts import get_vid01_prompts
from app.services.image_verifier import VerifiedImageGenerator
from app.services.video_service import VideoGenerationService
from app.services.tts_service import TTSService

OUTPUT_DIR = "output/videos"
PID = "vid01-v3"

# Voiceover text per scene
VOICEOVERS = [
    "Nobody notices the exact night it happens. The night a man stops reaching for the woman he loves. Not because he stopped loving her. But because somewhere along the way... intimacy stopped feeling safe.",
    "From the outside, nothing looks wrong. They still talk. Still laugh sometimes. Still share a bed. Still remember groceries and birthdays and school meetings. But emotional distance rarely arrives like an explosion. It arrives quietly. Through hesitation. Through accumulated silence. Through moments too small to defend... but too painful to forget.",
    "People assume men stop initiating intimacy because they lose attraction. Sometimes that's true. But often... what disappears first isn't desire. It's emotional safety. Rejection changes people slowly. Especially the quiet kind. The kind that never becomes a fight. A sigh. A delayed response. A tired expression. A moment that says: Not tonight. And after enough of those moments... vulnerability starts feeling dangerous.",
    "So he adapts. He stops trying as often. Stops risking embarrassment. Stops reaching first. Not out of punishment. Out of self-protection. Because eventually the brain learns something dangerous: avoiding rejection hurts less than hoping for connection.",
    "The tragedy of emotional withdrawal is that it often happens between two people who still love each other. But love without emotional safety slowly becomes performance. And eventually... people stop reaching for places where they no longer feel emotionally wanted. Not all distance is anger. Sometimes distance is grief.",
]

EFFECTS = ["ken-burns", "zoom-in", "zoom-out", "pan-right", "pan-left"]

video_service = VideoGenerationService(OUTPUT_DIR)
tts_service = TTSService(OUTPUT_DIR)


async def main():
    print("=" * 70)
    print("VID01 v3 — Chain-of-Verification Image Generation")
    print("=" * 70)
    print(f"Pipeline: {PID}")
    print(f"Candidates per round: 4")
    print(f"Min CLIP score: 0.28")
    print(f"Max refine rounds: 2")
    print()

    prompts = get_vid01_prompts()
    gen = VerifiedImageGenerator(OUTPUT_DIR)

    # Phase 1: Generate verified images
    results = []
    for prompt_data in prompts:
        scene_num = prompt_data["scene_number"]
        positive = prompt_data["positive_prompt"]
        negative = prompt_data["negative_prompt"]

        print(f"\n{'='*60}")
        print(f"Scene {scene_num}: {prompt_data['title']}")
        print(f"  Prompt: {positive[:120]}...")
        print(f"  Characters: {prompt_data['characters']}")
        print()

        # Remove old image if exists
        old_img = Path(OUTPUT_DIR) / PID / "scene_images" / f"scene_{scene_num:03d}.png"
        if old_img.exists():
            old_img.unlink()

        result = gen.generate_verified_image(
            pipeline_id=PID,
            scene_number=scene_num,
            positive_prompt=positive,
            negative_prompt=negative,
            num_candidates=4,
            min_score=0.28,
            max_refine_rounds=2,
        )

        print(f"\n  Result: score={result['clip_score']:.4f} seed={result['seed']} rounds={result['rounds']}")
        results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("IMAGE GENERATION SUMMARY")
    print(f"{'='*60}")
    for r in results:
        status = "OK" if r["clip_score"] >= 0.28 else "LOW"
        print(f"  Scene {r['scene_number']}: CLIP={r['clip_score']:.4f} [{status}] (rounds={r['rounds']}, seed={r['seed']})")

    # Phase 2: Generate video
    print(f"\n{'='*60}")
    print("VIDEO GENERATION")
    print(f"{'='*60}")

    for i in range(len(VOICEOVERS)):
        scene_num = i + 1
        vo = VOICEOVERS[i]
        effect = EFFECTS[i]
        print(f"\n--- Scene {scene_num} ({effect}) ---")

        # TTS
        print(f"  TTS...", end=" ")
        tts_result = await tts_service.generate_speech(PID, scene_num, vo)
        if tts_result["status"] != "completed":
            print(f"FAILED: {tts_result.get('error')}")
            return
        audio_dur = tts_service.get_audio_duration(PID, scene_num)
        print(f"{audio_dur:.1f}s")

        # Ken Burns
        image_path = Path(OUTPUT_DIR) / PID / "scene_images" / f"scene_{scene_num:03d}.png"
        if not image_path.exists():
            print(f"  No image found!")
            return
        print(f"  Ken Burns ({effect}, {audio_dur:.1f}s)...", end=" ")
        clip = video_service.generate_ken_burns_clip(PID, scene_num, image_path, audio_dur, effect)
        print(f"{clip.name}")

        # Merge
        print(f"  Merge...", end=" ")
        merged = tts_service.merge_audio_with_video(PID, scene_num)
        print(f"{merged.name}")

    # Assemble
    print(f"\n--- Assembling final video ---")
    final_dir = Path(OUTPUT_DIR) / PID
    final_clips = sorted((final_dir / "final_clips").glob("scene_*.mp4"))
    concat_file = final_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for c in final_clips:
            f.write(f"file '{c.resolve()}'\n")

    output_path = final_dir / "final.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(output_path)],
        check=True, capture_output=True,
    )

    # Verify
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,sample_rate,duration:format=duration,size",
         "-of", "default=noprint_wrappers=1", str(output_path)],
        capture_output=True, text=True,
    )
    print(f"\n{probe.stdout}")
    print(f"File: {output_path}")
    print(f"Size: {output_path.stat().st_size / (1024*1024):.1f} MB")
    print(f"\nPlay: open {output_path}")


if __name__ == "__main__":
    asyncio.run(main())