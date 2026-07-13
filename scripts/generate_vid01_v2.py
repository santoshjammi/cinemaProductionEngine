#!/usr/bin/env python3
"""Generate final VID01 video using new cinematic images + edge-tts audio."""
import sys, os, asyncio, subprocess
from pathlib import Path

sys.path.insert(0, "backend")
os.environ.setdefault("COQUI_TOS_AGREED", "1")

from app.services.video_service import VideoGenerationService
from app.services.tts_service import TTSService

OUTPUT_DIR = "output/videos"
PID = "vid01-v2"

video_service = VideoGenerationService(OUTPUT_DIR)
tts_service = TTSService(OUTPUT_DIR)

SCENES = [
    {"num": 1, "text": "Nobody notices the exact night it happens. The night a man stops reaching for the woman he loves. Not because he stopped loving her. But because somewhere along the way... intimacy stopped feeling safe.", "effect": "ken-burns"},
    {"num": 2, "text": "From the outside, nothing looks wrong. They still talk. Still laugh sometimes. Still share a bed. Still remember groceries and birthdays and school meetings. But emotional distance rarely arrives like an explosion. It arrives quietly. Through hesitation. Through accumulated silence. Through moments too small to defend... but too painful to forget.", "effect": "zoom-in"},
    {"num": 3, "text": "People assume men stop initiating intimacy because they lose attraction. Sometimes that's true. But often... what disappears first isn't desire. It's emotional safety. Rejection changes people slowly. Especially the quiet kind. The kind that never becomes a fight. A sigh. A delayed response. A tired expression. A moment that says: Not tonight. And after enough of those moments... vulnerability starts feeling dangerous.", "effect": "zoom-out"},
    {"num": 4, "text": "So he adapts. He stops trying as often. Stops risking embarrassment. Stops reaching first. Not out of punishment. Out of self-protection. Because eventually the brain learns something dangerous: avoiding rejection hurts less than hoping for connection.", "effect": "pan-right"},
    {"num": 5, "text": "The tragedy of emotional withdrawal is that it often happens between two people who still love each other. But love without emotional safety slowly becomes performance. And eventually... people stop reaching for places where they no longer feel emotionally wanted. Not all distance is anger. Sometimes distance is grief.", "effect": "pan-left"},
]

async def main():
    print(f"VID01 v2 — Cinematic Images + Edge TTS")
    print(f"Pipeline: {PID}")
    print()

    for scene in SCENES:
        num = scene["num"]
        print(f"=== Scene {num} ===")

        # 1. TTS
        print(f"  TTS...", end=" ")
        result = await tts_service.generate_speech(PID, num, scene["text"])
        if result["status"] != "completed":
            print(f"FAILED: {result.get('error')}")
            return
        audio_dur = tts_service.get_audio_duration(PID, num)
        print(f"{audio_dur:.1f}s")

        # 2. Ken Burns
        image_path = Path(OUTPUT_DIR) / PID / "scene_images" / f"scene_{num:03d}.png"
        print(f"  Ken Burns ({scene['effect']}, {audio_dur:.1f}s)...", end=" ")
        clip = video_service.generate_ken_burns_clip(PID, num, image_path, audio_dur, scene["effect"])
        print(f"{clip.name}")

        # 3. Merge
        print(f"  Merging...", end=" ")
        merged = tts_service.merge_audio_with_video(PID, num)
        print(f"{merged.name}")

    # 4. Assemble
    print(f"\n=== Assembling final video ===")
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