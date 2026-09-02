#!/usr/bin/env python3
"""
Render V5 — Uses real CC0 music + XTTS-v2 emotional TTS.

This is the production renderer integrated into the videoGen application.
Replaces procedural sine-wave music with downloaded CC0 cinematic tracks,
and replaces flat edge-tts with XTTS-v2 for emotional dialogue delivery.

File structure:
  videoGen/
    audio/           ← music_library.py + tts_engine.py (new)
    generate_dialogue.py   ← produces 100-150 word emotional conversations
    render_v5.py     ← THIS FILE: assembles the final film
    output/the_space_between_us/  ← generated assets
    assets/music/    ← downloaded CC0 tracks
"""
import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# ── Paths ─────────────────────────────────────────────────────────────────
OUTPUT_DIR = PROJECT_ROOT / "output" / "the_space_between_us"
IMAGES_DIR = OUTPUT_DIR / "images_v2"          # ← reuses existing images
AUDIO_DIR = OUTPUT_DIR / "audio_v5"            # ← new audio output
VIDEO_DIR = OUTPUT_DIR / "video_v5"            # ← new video output
MUSIC_ASSETS = PROJECT_ROOT / "assets" / "music"

# ── Imports ───────────────────────────────────────────────────────────────
sys.path.insert(0, str(PROJECT_ROOT))
from audio.music_library import (
    download_track,
    select_track_for_emotion,
    prepare_music_for_scene,
    save_index,
    TRACK_REGISTRY,
)
from audio.tts_engine import generate_tts_xtts, VOICE_PROFILES, EMOTION_PROXIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("render_v5")

MALE_NAME = "MARK"
FEMALE_NAME = "SARAH"


def ensure_music_assets():
    """Download all registered CC0 tracks if not already present."""
    logger.info("🎵 Ensuring CC0 music assets...")
    for key in TRACK_REGISTRY:
        p = MUSIC_ASSETS / f"{key}.mp3"
        if not p.exists():
            logger.info(f"  Downloading '{key}'...")
            download_track(key)
        else:
            logger.info(f"  ✅ {key} (cached)")
    save_index()
    logger.info("")


async def generate_tts_scene(
    scene_id: int,
    lines: list,
    output_dir: Path,
) -> list:
    """Generate TTS for all lines in a scene using XTTS/edge-tts.
    Returns list of (speaker, text, emotion, path) tuples."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for i, line in enumerate(lines):
        speaker = line.get("speaker", "NARRATOR")
        text = line.get("dialogue_text", "")
        emotion = line.get("emotion", "neutral")

        voice_profile = "mark" if speaker.upper() == MALE_NAME else "sarah"
        path = output_dir / f"scene_{scene_id:03d}_line_{i+1}_tts.wav"

        if not path.exists():
            result = await generate_tts_xtts(text, voice_profile, emotion, path)
        else:
            result = path

        results.append((speaker, text, emotion, result))

    return results


def prepare_background_music(
    scene_id: int,
    emotion: str,
    duration_sec: int,
    output_dir: Path,
) -> Path | None:
    """Select and prepare background music for a scene."""
    track_key = select_track_for_emotion(emotion)
    if not track_key:
        logger.warning(f"  [Scene {scene_id}] No music track found for emotion '{emotion}'")
        return None

    logger.info(f"  [Scene {scene_id}] Music: {track_key} ({emotion})")
    prepared = prepare_music_for_scene(track_key, duration_sec)
    if not prepared:
        return None

    # Copy to scene output
    dest = output_dir / f"scene_{scene_id:03d}_music.wav"
    subprocess.run(["cp", str(prepared), str(dest)])
    return dest


async def render_scene_audio(
    scene_id: int,
    tts_lines: list,
    music_path: Path | None,
    duration_sec: int,
    output_dir: Path,
) -> Path | None:
    """Mix dialogue + music into a single scene audio track."""
    mixed_path = output_dir / f"scene_{scene_id:03d}_mixed.wav"

    if mixed_path.exists():
        return mixed_path

    # Build ffmpeg filter complex for audio mixing
    inputs = []
    filters = []
    idx = 0

    # Music track
    if music_path and music_path.exists():
        inputs.extend(["-i", str(music_path)])
        filters.append(f"[{idx}:a]volume=0.5[a{idx}]")  # music lowered for dialogue
        idx += 1

    # Dialogue lines with adelay for spacing
    n = len(tts_lines)
    if n > 0:
        gap_ms = max(800, int((duration_sec * 1000) / (n + 1)))
        for li, (speaker, text, emotion, tts_path) in enumerate(tts_lines):
            if tts_path and tts_path.exists():
                inputs.extend(["-i", str(tts_path)])
                # Spread lines across the scene with staggered delays
                delay_ms = int(li * gap_ms)
                filters.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms},volume=1.6[a{idx}]")
                idx += 1

    if idx == 0:
        return None

    # Mix all inputs
    mix_inputs = "".join(f"[a{i}]" for i in range(idx))
    filters.append(f"{mix_inputs}amix=inputs={idx}:duration=first[aout]")

    filter_str = ";".join(filters)
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_str,
        "-map", "[aout]",
        "-ac", "2",
        "-b:a", "192k",
        str(mixed_path),
    ]

    logger.info(f"  [Scene {scene_id}] Mixing {n} lines + music ({len(inputs)//2} streams)...")
    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.communicate()

    if not mixed_path.exists():
        logger.error(f"  [Scene {scene_id}] Audio mix failed!")
        return None

    return mixed_path


async def render_scene_video(
    scene_id: int,
    audio_path: Path,
    duration_sec: int,
    output_dir: Path,
) -> Path | None:
    """Create scene video from images + mixed audio."""
    scene_video = output_dir / f"scene_{scene_id:03d}_v5.mp4"

    if scene_video.exists():
        return scene_video

    frames = [
        IMAGES_DIR / f"scene_{scene_id:03d}_frame_1.png",
        IMAGES_DIR / f"scene_{scene_id:03d}_frame_2.png",
        IMAGES_DIR / f"scene_{scene_id:03d}_frame_3.png",
    ]
    frames = [f for f in frames if f.exists()]

    if not frames:
        logger.warning(f"  [Scene {scene_id}] No frames found, skipping")
        return None

    fdur = duration_sec / len(frames)
    flist = output_dir / f"scene_{scene_id:03d}_v5_frames.txt"
    lines = [f"file '{f}'\nduration {fdur}" for f in frames]
    lines[-1] = f"file '{frames[-1]}'"
    flist.write_text("\n".join(lines))

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(flist),
        "-i", str(audio_path),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ac", "2",
        "-map", "0:v", "-map", "1:a",
        "-t", str(duration_sec),
        str(scene_video),
    ]

    logger.info(f"  [Scene {scene_id}] Rendering {len(frames)} frames → {fdur:.1f}s each...")
    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.communicate()

    return scene_video if scene_video.exists() else None


async def main():
    logger.info(f"{'='*60}")
    logger.info(f"  RENDER V5 — Cinematic Music + Emotional TTS")
    logger.info(f"{'='*60}")

    # ── Step 0: Load scene data ──
    scenes_path = PROJECT_ROOT / "pipeline" / "output" / "the_quiet_room" / "scenes.json"
    conv_path = OUTPUT_DIR / "conversations.json"

    if not scenes_path.exists():
        logger.error(f"Scenes file not found: {scenes_path}")
        return

    scenes = json.loads(scenes_path.read_text())

    if not conv_path.exists():
        logger.error(f"Conversations file not found: {conv_path}")
        logger.error("Run 'python3 generate_dialogue.py' first")
        return

    conversations = json.loads(conv_path.read_text())

    # ── Step 1: Ensure music assets ──
    ensure_music_assets()

    # ── Step 2: Create output directories ──
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 3: Build scene audio (TTS + music) ──
    logger.info(f"\n{'='*60}")
    logger.info(f"  GENERATING SCENE AUDIO")
    logger.info(f"{'='*60}")

    scene_videos = []

    for scene in scenes:
        sid = scene["id"]
        emotion = scene["emotion"]
        dur_str = scene.get("duration", "60s")
        duration_sec = int(dur_str.replace("s", ""))

        logger.info(f"\n--- Scene {sid} ({emotion}) — {duration_sec}s ---")

        # Find dialogue for this scene
        conv = next((c for c in conversations if c["scene_id"] == sid), None)
        lines = conv["lines"] if conv else []

        if not lines:
            logger.warning(f"  No dialogue for scene {sid}, music only")

        # Generate TTS
        tts_results = await generate_tts_scene(sid, lines, AUDIO_DIR)
        valid_tts = [(s, t, e, p) for s, t, e, p in tts_results if p]

        if not valid_tts and not lines:
            logger.warning(f"  No audio content for scene {sid}, skipping")
            continue

        # Prepare music
        music_path = prepare_background_music(sid, emotion, duration_sec, AUDIO_DIR)

        # Mix
        mixed = await render_scene_audio(sid, valid_tts, music_path, duration_sec, AUDIO_DIR)

        if not mixed:
            logger.warning(f"  No mixed audio for scene {sid}")
            continue

        # Render video
        video = await render_scene_video(sid, mixed, duration_sec, VIDEO_DIR)
        if video:
            scene_videos.append(video)

    # ── Step 4: Concatenate all scenes ──
    logger.info(f"\n{'='*60}")
    logger.info(f"  CONCATENATING FINAL FILM")
    logger.info(f"{'='*60}")

    if not scene_videos:
        logger.error("No scene videos rendered!")
        return

    concat_file = OUTPUT_DIR / "concat_v5.txt"
    concat_file.write_text("\n".join(f"file '{v}'" for v in scene_videos))

    final_video = VIDEO_DIR / "the_space_between_us_v5.mp4"

    # First try stream copy
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file), "-c", "copy", str(final_video),
    ]
    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.communicate()

    # Re-encode if stream copy failed
    if not final_video.exists() or final_video.stat().st_size < 10000:
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264", "-c:a", "aac", str(final_video),
        ]
        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.communicate()

    # ── Step 5: Report ──
    if final_video.exists():
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration,size",
             "-of", "default=noprint_wrappers=1:nokey=1",
             str(final_video)],
            capture_output=True, text=True,
        )
        dur_s, size_b = result.stdout.strip().split("\n")
        mins = float(dur_s) / 60
        mb = int(size_b) / (1024 * 1024)

        logger.info(f"\n{'='*60}")
        logger.info(f"  ✅ V5 FILM COMPLETE")
        logger.info(f"  Music: Real CC0 cinematic tracks")
        logger.info(f"  Voices: XTTS-v2 with emotional prosody")
        logger.info(f"  Duration: {float(dur_s):.0f}s ({mins:.1f} min)")
        logger.info(f"  Size: {mb:.1f} MB")
        logger.info(f"  Video: {final_video}")
        logger.info(f"{'='*60}")

        # Show per-scene stats
        logger.info(f"\n📊 SCENE BREAKDOWN")
        logger.info(f"{'='*60}")
        for scene in scenes:
            sid = scene["id"]
            conv = next((c for c in conversations if c["scene_id"] == sid), None)
            if conv:
                words = sum(len(l.get("dialogue_text", "").split()) for l in conv["lines"])
                emotions = [l.get("emotion", "?") for l in conv["lines"]]
                logger.info(f"  Scene {sid}: {scene['duration']:>5s} | {words:3d} words | {' → '.join(emotions)}")
            else:
                logger.info(f"  Scene {sid}: {scene['duration']:>5s} | no dialogue")
    else:
        logger.error("❌ Final video not created!")


if __name__ == "__main__":
    asyncio.run(main())