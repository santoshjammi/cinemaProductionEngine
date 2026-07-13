#!/usr/bin/env python3
"""Generate remaining scenes (3-5) directly using the services, bypassing the API."""
import sys
import asyncio
import os

sys.path.insert(0, "backend")
os.environ["COQUI_TOS_AGREED"] = "1"

from app.services.video_service import VideoGenerationService, get_generation_state
from app.services.tts_service import TTSService
from app.services.image_service import ImageGenerationService

PIPELINE_ID = "9232e735-4079-498f-8c84-ca7e0975d715"
OUTPUT_DIR = "output/videos"

video_service = VideoGenerationService(OUTPUT_DIR)
tts_service = TTSService(OUTPUT_DIR)
image_service = ImageGenerationService(OUTPUT_DIR)

# The dialogues for scenes 3-5
DIALOGUES = {
    3: "People assume men stop initiating intimacy because they lose attraction. Sometimes that's true. But often... what disappears first isn't desire. It's emotional safety. Rejection changes people slowly. Especially the quiet kind. The kind that never becomes a fight. A sigh. A delayed response. A tired expression. A moment that says: Not tonight. And after enough of those moments... vulnerability starts feeling dangerous.",
    4: "So he adapts. He stops trying as often. Stops risking embarrassment. Stops reaching first. Not out of punishment. Out of self-protection. Because eventually the brain learns something dangerous: avoiding rejection hurts less than hoping for connection.",
    5: "The tragedy of emotional withdrawal is that it often happens between two people who still love each other. But love without emotional safety slowly becomes performance. And eventually... people stop reaching for places where they no longer feel emotionally wanted. Not all distance is anger. Sometimes distance is grief.",
}

EFFECTS = {3: "zoom-out", 4: "pan-right", 5: "pan-left"}


async def main():
    for scene_num in [3, 4, 5]:
        print(f"\n=== Scene {scene_num} ===")

        # 1. Generate TTS audio
        print(f"Generating TTS for scene {scene_num}...")
        dialogue_text = DIALOGUES[scene_num]
        result = await tts_service.generate_speech(
            pipeline_id=PIPELINE_ID,
            scene_number=scene_num,
            text=dialogue_text,
        )
        print(f"TTS result: {result['status']}")

        if result["status"] != "completed":
            print(f"TTS failed for scene {scene_num}: {result.get('error')}")
            continue

        # 2. Get audio duration
        audio_duration = tts_service.get_audio_duration(PIPELINE_ID, scene_num)
        print(f"Audio duration: {audio_duration:.1f}s")

        # 3. Get image path
        image_path = image_service.get_image_path(PIPELINE_ID, scene_num)
        if image_path is None:
            print(f"No image for scene {scene_num}")
            continue
        print(f"Image: {image_path}")

        # 4. Generate Ken Burns clip matching audio duration
        effect = EFFECTS[scene_num]
        print(f"Generating Ken Burns clip ({effect}, {audio_duration:.1f}s)...")
        clip_path = video_service.generate_ken_burns_clip(
            PIPELINE_ID, scene_num, image_path, audio_duration, effect
        )
        print(f"Clip: {clip_path}")

        # 5. Merge audio with video
        print(f"Merging audio with video...")
        merged = tts_service.merge_audio_with_video(PIPELINE_ID, scene_num)
        print(f"Merged: {merged}")

    # 6. Assemble final video
    print("\n=== Assembling final video ===")
    result = video_service.assemble_final_video(PIPELINE_ID, 5)
    print(f"Final: {result}")

    # Verify
    import subprocess
    final_path = f"{OUTPUT_DIR}/{PIPELINE_ID}/final.mp4"
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,sample_rate,duration:format=duration,size",
         "-of", "default=noprint_wrappers=1", final_path],
        capture_output=True, text=True,
    )
    print(f"\n=== Final video verification ===")
    print(probe.stdout)


if __name__ == "__main__":
    asyncio.run(main())