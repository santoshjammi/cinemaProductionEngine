#!/usr/bin/env python3
"""Generate final video from already-verified images using edge-tts + Ken Burns."""
import sys, os, asyncio, subprocess
from pathlib import Path

sys.path.insert(0, "backend")
os.environ.setdefault("COQUI_TOS_AGREED", "1")

from app.services.video_service import VideoGenerationService
from app.services.tts_service import TTSService

OUTPUT_DIR = "output/videos"
PID = "vid01-v3"

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
    print("VID01 v3 — Video generation from verified images")
    print(f"Pipeline: {PID}")
    print()

    for i in range(5):
        scene_num = i + 1
        print(f"--- Scene {scene_num} ({EFFECTS[i]}) ---")

        # TTS
        print(f"  TTS...", end=" ", flush=True)
        r = await tts_service.generate_speech(PID, scene_num, VOICEOVERS[i])
        if r["status"] != "completed":
            print(f"FAILED: {r.get('error')}")
            return
        dur = tts_service.get_audio_duration(PID, scene_num)
        print(f"{dur:.1f}s")

        # Ken Burns
        img = Path(OUTPUT_DIR) / PID / "scene_images" / f"scene_{scene_num:03d}.png"
        print(f"  Ken Burns ({EFFECTS[i]}, {dur:.1f}s)...", end=" ", flush=True)
        clip = video_service.generate_ken_burns_clip(PID, scene_num, img, dur, EFFECTS[i])
        print(f"{clip.name}")

        # Merge
        print(f"  Merge...", end=" ", flush=True)
        merged = tts_service.merge_audio_with_video(PID, scene_num)
        print(f"{merged.name}")

    # Assemble
    print(f"\n--- Assembling ---")
    final_dir = Path(OUTPUT_DIR) / PID
    clips = sorted((final_dir / "final_clips").glob("scene_*.mp4"))
    concat = final_dir / "concat.txt"
    with open(concat, "w") as f:
        for c in clips:
            f.write(f"file '{c.resolve()}'\n")

    out = final_dir / "final.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(out)],
        check=True, capture_output=True,
    )
    print(f"Done: {out} ({out.stat().st_size / (1024*1024):.1f} MB)")
    print(f"Play: open {out}")


if __name__ == "__main__":
    asyncio.run(main())