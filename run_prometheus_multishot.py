#!/usr/bin/env python3
"""PROMETHEUS multi-shot realization for EP-0001.

Realizes multiple meaningful visual shots per scene from the existing frozen
GENESIS shot plan (30 shots), selecting 2-3 representative shots per scene
(6-9 total visual assets), generating one image per selected shot, and
assembling a multi-shot timeline with the existing dialogue/music.

Does NOT regenerate story content, does NOT attempt all 30 shots, does NOT
implement lipsync.
"""
from __future__ import annotations

import asyncio
import json
import logging
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_prometheus_multishot")

PKP_PATH = ROOT / "productions/EP-0001/runs/RUN-20260828-161752/genesis/pkp/PKP-EP-0001-v1.yaml"
RUN_ROOT = ROOT / "productions/EP-0001/runs/RUN-20260828-161752"
IMG_DIR = RUN_ROOT / "images" / "RUN-20260828-161752" / "scene_images"
RENDER_DIR = RUN_ROOT / "render"
VOICE_DIR = RUN_ROOT / "voice"
MUSIC_DIR = RUN_ROOT / "music"

# Representative shot selection per scene (maximize composition/emotion/visibility difference).
SHOT_SELECTION = {
    1: ["SC01-SH01", "SC01-SH02", "SC01-SH05"],  # ESTABLISHING(wide) + SPEAKER_COVERAGE(Mark) + INSERT(letter)
    2: ["SC02-SH07", "SC02-SH08", "SC02-SH10"],  # SPEAKER_COVERAGE(Sarah) + LISTENER_REACTION(Mark) + TWO_SHOT
    3: ["SC03-SH13", "SC03-SH16", "SC03-SH30"],  # SPEAKER_COVERAGE(Sarah calm) + SPEAKER_COVERAGE(Mark vulnerable) + EMOTIONAL_HOLD
}

# Ken Burns motion per shot purpose (P0-06 §5: choose by composition, not random).
MOTION_BY_PURPOSE = {
    "ESTABLISHING": "pan_right",
    "SPEAKER_COVERAGE": "zoom_in",
    "LISTENER_REACTION": "zoom_out",
    "TWO_SHOT": "pan_left",
    "EMOTIONAL_HOLD": "zoom_in",
    "INSERT": "zoom_in",
}

# Character anchors (verbatim) for identity consistency.
ANCHORS = (
    "MARK: a tall, lean man in his late 30s with warm brown skin, short black hair "
    "with a silver streak at the left temple. "
    "SARAH: a woman of medium height in her early 30s with light tan skin and long dark wavy hair."
)
STYLE = (
    "cinematic film still, photorealistic, realistic adult drama, "
    "natural warm lighting, shallow depth of field, "
    "sharp expressive faces, subtle skin texture, "
    "professional cinematography, high production value, "
    "crisp clean image, high detail"
)
QUALITY = (
    "BOTH MARK and SARAH clearly visible in frame, sharp focused detailed faces, "
    "crystal-clear high resolution, bright vibrant well-lit, "
    "professional lighting, crisp clean image, "
    "natural skin tones, warm inviting atmosphere, "
    "glowing healthy skin, balanced exposure"
)
NEGATIVE = (
    "3D animation, cartoon, Pixar, DreamWorks, anime, illustration, "
    "stylized, cel-shaded, glossy plastic skin, "
    "blurry, out of focus, soft focus, low resolution, grainy, "
    "dark, dimly lit, underexposed, vintage, retro, hazy, foggy, noise, "
    "distorted, deformed, ugly, bad anatomy, extra limbs, watermark, text"
)


def _probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=10)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def _build_shot_prompt(shot: dict, scene: dict) -> str:
    """Build a cinematic prompt for a specific shot, reusing character canon."""
    purpose = shot.get("purpose", "")
    framing = shot.get("framing", {}).get("type", "")
    subject = shot.get("visual_subject", {}).get("primary", "")
    action = shot.get("visual_action", "")
    emotional = shot.get("emotional_intent", "")
    composition = shot.get("composition", {}).get("relationship", "")

    parts = []
    if purpose == "ESTABLISHING":
        parts.append("wide establishing shot of the home interior, both characters small in frame, spatial context")
    elif purpose == "INSERT":
        parts.append("extreme close-up insert of a termination letter on a table, shallow depth of field")
    elif purpose == "TWO_SHOT":
        parts.append("two-shot medium close-up of MARK and SARAH facing each other, natural dialogue exchange")
    elif purpose == "LISTENER_REACTION":
        parts.append(f"reaction close-up of {subject or 'the listener'}, isolated, processing emotion")
    elif purpose == "EMOTIONAL_HOLD":
        parts.append(f"emotional hold close-up of {subject or 'the character'}, lingering, after-effect")
    else:  # SPEAKER_COVERAGE
        parts.append(f"over-the-shoulder two-shot, {subject or 'the speaker'} delivering a line")

    if framing:
        parts.append(f"{framing.lower()} framing")
    if composition:
        parts.append(composition)
    if action:
        parts.append(action)
    if emotional:
        parts.append(f"emotional intent: {emotional}")
    parts.append(STYLE)
    parts.append(QUALITY)
    parts.append(ANCHORS)
    parts.append("cinematic, photorealistic, high quality, natural color grade, bright vivid colors, high-definition, sharp detail")
    return ", ".join(p for p in parts if p)


async def generate_shot_images(shots_by_id: dict, scenes: dict) -> dict[str, Path]:
    """Generate one image per selected shot. Reuses existing scene image for the
    first shot of each scene; generates new images for the others."""
    from movie_os.capabilities.base import ImageIntent
    from movie_os.providers.image.flux_comfyui import FluxComfyUIProvider

    provider = FluxComfyUIProvider(comfyui_url="http://127.0.0.1:8188", model="flux1-dev-fp8.safetensors")
    shot_images: dict[str, Path] = {}

    for scene_id, shot_ids in SHOT_SELECTION.items():
        # First shot of each scene reuses the existing scene image (identity anchor).
        first_shot = shot_ids[0]
        existing = IMG_DIR / f"scene_{scene_id:03d}.png"
        if existing.exists() and existing.stat().st_size > 10000:
            shot_images[first_shot] = existing
            logger.info(f"  [img] {first_shot} reuses existing scene_{scene_id:03d}.png")
        else:
            shot_images[first_shot] = existing  # will be generated below

        for shot_id in shot_ids[1:]:
            shot = shots_by_id[shot_id]
            scene = scenes.get(scene_id, {})
            prompt = _build_shot_prompt(shot, scene)
            out_path = IMG_DIR / f"shot_{shot_id}.png"
            if out_path.exists() and out_path.stat().st_size > 10000:
                shot_images[shot_id] = out_path
                logger.info(f"  [img] {shot_id} reuses existing {out_path.name}")
                continue
            intent = ImageIntent(
                prompt=prompt,
                negative_prompt=NEGATIVE,
                width=1024,
                height=576,
                quality="production",
                seed=2000 + scene_id * 10 + len(shot_ids),
                metadata={
                    "scene_number": scene_id,
                    "output_dir": str(IMG_DIR),
                    "pipeline_id": "RUN-20260828-161752",
                },
            )
            try:
                asset = await provider.render(intent)
                p = Path(asset.path)
                # Rename to shot-specific path.
                if p != out_path:
                    shutil.copy2(p, out_path)
                shot_images[shot_id] = out_path
                logger.info(f"  [img] generated {shot_id} -> {out_path.name}")
            except Exception as e:
                logger.warning(f"  [img] {shot_id} generation failed: {e}")
                shot_images[shot_id] = existing  # fall back to scene image

    return shot_images


def _render_shot_video(image: Path, audio: Path, duration_s: float, out_path: Path, motion: str) -> Path | None:
    """Ken Burns over a single image + audio for one shot."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
    dur = max(duration_s, 1.0)
    fps = 24
    frames = int(dur * fps)
    if motion == "zoom_in":
        z, x, y = f"1+0.08*on/{frames}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion == "zoom_out":
        z, x, y = f"1.08-0.08*on/{frames}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion == "pan_left":
        z, x, y = "1.15", f"(iw-iw/zoom)*(1-on/{frames})", "ih/2-(ih/zoom/2)"
    elif motion == "pan_right":
        z, x, y = "1.15", f"(iw-iw/zoom)*(on/{frames})", "ih/2-(ih/zoom/2)"
    elif motion == "pan_up":
        z, x, y = "1.15", "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(1-on/{frames})"
    else:
        z, x, y = "1.15", "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(on/{frames})"
    vf = (f"scale=1920:1080:force_original_aspect_ratio=decrease,"
          f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps={fps}")
    cmd = (f'ffmpeg -y -loop 1 -i "{image}" -i "{audio}" '
           f'-vf "{vf}" '
           f'-c:v libx264 -pix_fmt yuv420p -preset medium -crf 20 -r {fps} '
           f'-c:a aac -b:a 192k -ar 48000 '
           f'-map 0:v -map 1:a -t {duration_s} "{out_path}"')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if not out_path.exists() or out_path.stat().st_size < 10000:
        logger.error(f"  [video] shot render failed: {r.stderr[-500:]}")
        return None
    return out_path


def _compute_scene_duration(voice_paths: list[Path], min_duration_s: float = 8.0,
                            pause_s: float = 0.7, tail_s: float = 2.0) -> float:
    """Compute a natural scene duration from the dialogue (back-to-back lines
    + short pause), NOT from the music track length."""
    total = 0.0
    for p in voice_paths:
        if p and p.exists():
            total += _probe_duration(p) + pause_s
    if total <= 0:
        return min_duration_s
    return max(min_duration_s, total + tail_s)


def _mix_scene_audio(music: Path | None, voice_paths: list[Path], out_path: Path) -> Path | None:
    """Mix music (ducked) + dialogue placed back-to-back with natural pauses."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 1000:
        return out_path
    inputs, filters, idx = [], [], 0
    if music is not None and music.exists():
        inputs += ["-i", str(music)]
        filters.append(f"[{idx}:a]volume=-6dB,aresample=48000[m]")
        idx += 1
    cursor_ms = 0
    pause_ms = 700
    for vp in voice_paths:
        if not vp or not vp.exists():
            continue
        inputs += ["-i", str(vp)]
        filters.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                       f"adelay={cursor_ms}|{cursor_ms},volume=2.2[v{idx}]")
        idx += 1
        cursor_ms += int((_probe_duration(vp) + pause_ms / 1000.0) * 1000)
    if idx == 0:
        return None
    if music and music.exists():
        mix_inputs = "".join(f"[v{i}]" for i in range(1, idx))
        filters.append(f"{mix_inputs}amix=inputs={idx-1}:duration=first:dropout_transition=3[vout]")
        filters.append("[m][vout]amix=inputs=2:duration=first:dropout_transition=3[out]")
    else:
        mix_inputs = "".join(f"[v{i}]" for i in range(1, idx))
        filters.append(f"{mix_inputs}amix=inputs={idx-1}:duration=first:dropout_transition=3[out]")
    cmd = (["ffmpeg", "-y"] + inputs +
           ["-filter_complex", ";".join(filters), "-map", "[out]",
            "-c:a", "aac", "-b:a", "192k", str(out_path)])
    subprocess.run(cmd, capture_output=True, timeout=180)
    if not out_path.exists() or out_path.stat().st_size < 1000:
        return None
    norm_path = out_path.with_suffix(".norm.m4a")
    subprocess.run(f'ffmpeg -y -i "{out_path}" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:a aac -b:a 192k "{norm_path}"',
                   shell=True, capture_output=True, text=True, timeout=120)
    if norm_path.exists() and norm_path.stat().st_size > 0:
        shutil.move(str(norm_path), str(out_path))
    return out_path if out_path.exists() else None


async def main():
    print("=" * 60)
    print("  PROMETHEUS — EP-0001 multi-shot realization")
    print("=" * 60)

    pkp = json.loads(PKP_PATH.read_text(encoding="utf-8"))
    shots = pkp["shots"]["shots"]
    shots_by_id = {s["shot_id"]: s for s in shots}
    sp = pkp.get("screenplay", {})
    scenes = {sc.get("scene_id"): sc for sc in sp.get("scenes", [])}

    print(f"  PKP      : {pkp.get('pkp_id')}")
    print(f"  Shots    : {len(shots)} (selecting {sum(len(v) for v in SHOT_SELECTION.values())})")

    # 1. Generate per-shot images.
    print("\n[1/3] Generating per-shot images...")
    shot_images = await generate_shot_images(shots_by_id, scenes)
    print(f"  shot images: {len(shot_images)}")

    # 2. Build multi-shot timeline with existing dialogue/music.
    print("\n[2/3] Building multi-shot timeline...")
    voice_by_scene: dict[int, list[Path]] = {}
    for f in sorted(VOICE_DIR.glob("scene_*.mp3")):
        # filename like scene_001_line_1.mp3
        try:
            sid = int(f.name.split("_")[1])
        except (ValueError, IndexError):
            continue
        voice_by_scene.setdefault(sid, []).append(f)
    music_by_scene: dict[int, Path] = {}
    for f in sorted(MUSIC_DIR.glob("scene_*.mp3")):
        try:
            sid = int(f.name.split("_")[1])
        except (ValueError, IndexError):
            continue
        music_by_scene[sid] = f

    scene_videos: list[Path] = []
    for scene_id, shot_ids in SHOT_SELECTION.items():
        voice_paths = voice_by_scene.get(scene_id, [])
        if not voice_paths:
            logger.warning(f"  [timeline] scene {scene_id} has no voice clips")
            continue
        music = music_by_scene.get(scene_id)
        mixed = _mix_scene_audio(music, voice_paths, RENDER_DIR / f"scene_{scene_id:03d}_mixed.m4a")
        if not mixed:
            logger.warning(f"  [timeline] scene {scene_id} mix failed")
            continue
        # Scene duration is driven by the dialogue (back-to-back lines + pause),
        # NOT the music track length.
        scene_dur = _compute_scene_duration(voice_paths)
        # Split scene duration across selected shots proportionally.
        n_shots = len(shot_ids)
        shot_dur = scene_dur / n_shots
        for i, shot_id in enumerate(shot_ids):
            image = shot_images.get(shot_id)
            if not image or not image.exists():
                logger.warning(f"  [timeline] {shot_id} has no image, skipping")
                continue
            motion = MOTION_BY_PURPOSE.get(shots_by_id[shot_id].get("purpose", ""), "zoom_in")
            out_mp4 = RENDER_DIR / f"shot_{shot_id}.mp4"
            sv = _render_shot_video(image, mixed, shot_dur, out_mp4, motion)
            if sv:
                scene_videos.append(sv)
                logger.info(f"  [timeline] {shot_id} rendered ({shot_dur:.1f}s, {motion})")

    # 3. Concatenate into final MP4.
    print("\n[3/3] Assembling final MP4...")
    final_path = RENDER_DIR / "The Email Mark Wouldnt Open_multishot.mp4"
    final_path.parent.mkdir(parents=True, exist_ok=True)
    if scene_videos:
        concat = RENDER_DIR / "concat_multishot.txt"
        concat.write_text("\n".join(f"file '{v.resolve()}'" for v in scene_videos))
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" -c copy "{final_path}"',
                       shell=True, capture_output=True, timeout=120)
        if not final_path.exists() or final_path.stat().st_size < 10000:
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" '
                           f'-c:v libx264 -pix_fmt yuv420p -crf 20 -r 24 '
                           f'-c:a aac -b:a 192k "{final_path}"',
                           shell=True, capture_output=True, timeout=300)

    # Color grade.
    if final_path.exists() and final_path.stat().st_size > 10000:
        graded = final_path.with_suffix(".graded.mp4")
        subprocess.run(f'ffmpeg -y -i "{final_path}" -vf "eq=contrast=1.18:brightness=0.05:saturation=1.9,unsharp=5:5:0.8:5:5:0.0" '
                       f'-c:v libx264 -pix_fmt yuv420p -preset medium -crf 20 -c:a copy "{graded}"',
                       shell=True, capture_output=True, timeout=300)
        if graded.exists() and graded.stat().st_size > 10000:
            shutil.move(str(graded), str(final_path))

    ok = final_path.exists() and final_path.stat().st_size > 10000
    print(f"\n  FINAL: {final_path} ({final_path.stat().st_size//1024}KB) ok={ok}")
    print(f"  Visual assets: {len(shot_images)} | Scene videos: {len(scene_videos)}")
    return {"ok": ok, "path": str(final_path), "assets": len(shot_images), "videos": len(scene_videos)}


if __name__ == "__main__":
    asyncio.run(main())
