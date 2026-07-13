#!/usr/bin/env python3
"""Generate video scene-by-scene from VID01.md using edge-tts + Ken Burns.

Flow per scene:
  1. Generate TTS audio (edge-tts, en-US-GuyNeural)
  2. Get audio duration
  3. Generate Ken Burns clip matching audio duration
  4. Merge audio + video clip

Then assemble final video from all merged clips.
"""
import sys
import os
import asyncio
import subprocess
from pathlib import Path

sys.path.insert(0, "backend")
os.environ.setdefault("COQUI_TOS_AGREED", "1")

from app.services.video_service import VideoGenerationService
from app.services.tts_service import TTSService
from app.services.image_service import ImageGenerationService

OUTPUT_DIR = "output/videos"
PID = "vid01-edge-tts"

SCENES = [
    {
        "num": 1,
        "text": "Nobody notices the exact night it happens. The night a man stops reaching for the woman he loves. Not because he stopped loving her. But because somewhere along the way... intimacy stopped feeling safe.",
        "effect": "ken-burns",
    },
    {
        "num": 2,
        "text": "From the outside, nothing looks wrong. They still talk. Still laugh sometimes. Still share a bed. Still remember groceries and birthdays and school meetings. But emotional distance rarely arrives like an explosion. It arrives quietly. Through hesitation. Through accumulated silence. Through moments too small to defend... but too painful to forget.",
        "effect": "zoom-in",
    },
    {
        "num": 3,
        "text": "People assume men stop initiating intimacy because they lose attraction. Sometimes that's true. But often... what disappears first isn't desire. It's emotional safety. Rejection changes people slowly. Especially the quiet kind. The kind that never becomes a fight. A sigh. A delayed response. A tired expression. A moment that says: Not tonight. And after enough of those moments... vulnerability starts feeling dangerous.",
        "effect": "zoom-out",
    },
    {
        "num": 4,
        "text": "So he adapts. He stops trying as often. Stops risking embarrassment. Stops reaching first. Not out of punishment. Out of self-protection. Because eventually the brain learns something dangerous: avoiding rejection hurts less than hoping for connection.",
        "effect": "pan-right",
    },
    {
        "num": 5,
        "text": "The tragedy of emotional withdrawal is that it often happens between two people who still love each other. But love without emotional safety slowly becomes performance. And eventually... people stop reaching for places where they no longer feel emotionally wanted. Not all distance is anger. Sometimes distance is grief.",
        "effect": "pan-left",
    },
]

# Cinematic image prompts (from VID01.md)
IMAGE_PROMPTS = {
    1: "Dark bedroom at night, phone glow illuminating half of a man's face, his wife asleep beside him under white sheets, his hand almost reaching toward her then stopping and pulling back, shallow depth of field, muted blue and amber tones, intimate close-up, melancholic mood, cinematic lighting, 35mm film aesthetic",
    2: "Montage of domestic life: man driving alone in car at dusk staring blankly, working late in dim office, eating dinner quietly across from wife at kitchen table, folding laundry mechanically, scrolling phone in dark room with blue screen glow, emotional void between two physically close people, muted desaturated tones, medium shots, observational documentary style",
    3: "Man sitting alone in parked car at night staring at windshield, close-up of phone showing unread messages, reheating coffee alone in dim kitchen, pausing outside closed bedroom door, shower scene with no music water running down face, avoiding mirror reflection, tight close-ups, shallow focus, raw vulnerability, cold blue-green color grade",
    4: "Man gaming alone in dark living room with TV blue glow on face, late-night phone scrolling in bed beside sleeping wife, pretending to sleep eyes open in darkness, emotionally flat conversation at kitchen table with no eye contact, empty mechanical routines, flat lighting, wide shots showing isolation within shared spaces",
    5: "Dark bedroom at night parallel to opening, both husband and wife awake lying inches apart but emotionally worlds apart, his hand resting near hers on the white sheet not touching, the gap between their hands, tragic stillness, muted blue moonlight through curtains, intimate close-up on hands, 35mm film grain, cinematic melancholy",
}

video_service = VideoGenerationService(OUTPUT_DIR)
tts_service = TTSService(OUTPUT_DIR)
image_service = ImageGenerationService(OUTPUT_DIR)


async def generate_scene(scene: dict):
    num = scene["num"]
    text = scene["text"]
    effect = scene["effect"]

    print(f"\n{'='*60}")
    print(f"SCENE {num} — effect: {effect}")
    print(f"{'='*60}")

    # Step 1: Generate TTS audio
    print(f"[1/4] Generating TTS audio...")
    result = await tts_service.generate_speech(PID, num, text)
    if result["status"] != "completed":
        print(f"  TTS FAILED: {result.get('error')}")
        return False
    audio_dur = tts_service.get_audio_duration(PID, num)
    print(f"  Audio duration: {audio_dur:.1f}s")

    # Step 2: Get or generate image
    image_path = image_service.get_image_path(PID, num)
    if image_path is None:
        print(f"[2/4] Generating image with SD v1.5...")
        image_path = await image_service.generate_scene_image(
            PID, num, IMAGE_PROMPTS[num]
        )
        if image_path is None:
            print("  Image generation FAILED")
            return False
    else:
        print(f"[2/4] Image already exists: {image_path.name}")

    # Step 3: Generate Ken Burns clip matching audio duration
    print(f"[3/4] Generating Ken Burns clip ({effect}, {audio_dur:.1f}s)...")
    clip_path = video_service.generate_ken_burns_clip(
        PID, num, image_path, audio_dur, effect
    )
    if clip_path is None:
        print("  Ken Burns FAILED")
        return False
    print(f"  Clip: {clip_path.name}")

    # Step 4: Merge audio with video
    print(f"[4/4] Merging audio + video...")
    merged = tts_service.merge_audio_with_video(PID, num)
    if merged is None:
        print("  Merge FAILED")
        return False
    print(f"  Merged: {merged.name}")

    # Verify
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,sample_rate,duration",
         "-of", "default=noprint_wrappers=1", str(merged)],
        capture_output=True, text=True,
    )
    print(f"  Verification:\n{probe.stdout}")
    return True


def assemble_final():
    print(f"\n{'='*60}")
    print("ASSEMBLING FINAL VIDEO")
    print(f"{'='*60}")

    final_dir = Path(OUTPUT_DIR) / PID
    final_clips_dir = final_dir / "final_clips"
    output_path = final_dir / "final.mp4"

    clips = sorted(final_clips_dir.glob("scene_*.mp4"))
    if not clips:
        print("No clips to assemble!")
        return

    concat_file = final_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

    print(f"Concatenating {len(clips)} clips...")
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy", str(output_path),
        ],
        check=True, capture_output=True,
    )

    # Verify final
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,sample_rate,duration:format=duration,size",
         "-of", "default=noprint_wrappers=1", str(output_path)],
        capture_output=True, text=True,
    )
    print(f"\nFinal video:\n{probe.stdout}")
    print(f"File: {output_path}")
    print(f"Size: {output_path.stat().st_size / (1024*1024):.1f} MB")


async def main():
    print("VID01 Video Generation — edge-tts (en-US-GuyNeural)")
    print(f"Pipeline ID: {PID}")
    print(f"Output dir: {OUTPUT_DIR}/{PID}/")

    # Generate each scene one-by-one
    for scene in SCENES:
        success = await generate_scene(scene)
        if not success:
            print(f"\nScene {scene['num']} FAILED — stopping.")
            return

    # Assemble final video
    assemble_final()
    print("\nDone! Play with:")
    print(f"  open {OUTPUT_DIR}/{PID}/final.mp4")


if __name__ == "__main__":
    asyncio.run(main())