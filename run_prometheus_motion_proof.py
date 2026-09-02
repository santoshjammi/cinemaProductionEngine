#!/usr/bin/env python3
"""PROMETHEUS real-motion proof for EP-0001.

Proves that real motion (SVD) materially improves the video over the Ken Burns
baseline, using exactly 3 representative shots. Generates SVD motion clips for
the 3 selected shots, then splices them into the existing multishot video,
replacing only those 3 Ken Burns segments.

Does NOT modify GENESIS, does NOT animate all shots, does NOT build a broad
motion architecture.
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
logger = logging.getLogger("run_prometheus_motion_proof")

RUN_ROOT = ROOT / "productions/EP-0001/runs/RUN-20260828-161752"
IMG_DIR = RUN_ROOT / "images" / "RUN-20260828-161752" / "scene_images"
RENDER_DIR = RUN_ROOT / "render"
MOTION_DIR = RENDER_DIR / "motion_proof"

# The 3 representative shots (segment index in the multishot video, 1-based).
# Segment order: SC01-SH01, SC01-SH02, SC01-SH05, SC02-SH07, SC02-SH08,
#                SC02-SH10, SC03-SH13, SC03-SH16, SC03-SH30
SELECTED = [
    {"shot_id": "SC01-SH02", "image": "shot_SC01-SH02.png", "segment": 2, "type": "MARK_SPEAKING_CLOSEUP"},
    {"shot_id": "SC02-SH07", "image": "scene_002.png",       "segment": 4, "type": "SARAH_SPEAKING_CLOSEUP"},
    {"shot_id": "SC03-SH30", "image": "shot_SC03-SH30.png",  "segment": 9, "type": "EMOTIONAL_REACTION"},
]

BASELINE = RENDER_DIR / "The Email Mark Wouldnt Open_multishot.mp4"
OUTPUT = RENDER_DIR / "The Email Mark Wouldnt Open_motion.mp4"


def _probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=10)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


async def generate_svd_clip(image: Path, out_path: Path, motion_bucket_id: int = 127) -> Path | None:
    """Generate a real-motion SVD clip from a still image."""
    from movie_os.providers.video.svd_local import render_with_svd
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
    try:
        clip = await render_with_svd(
            image_path=str(image),
            output_dir=str(out_path.parent),
            width=576,
            height=1024,
            motion_bucket_id=motion_bucket_id,
            noise_aug_strength=0.02,
            decode_chunk_size=8,
            fps=7,
        )
        if clip and Path(clip).exists() and Path(clip).stat().st_size > 10000:
            # Rename to the requested output path.
            if Path(clip) != out_path:
                shutil.copy2(str(clip), str(out_path))
            return out_path
    except Exception as e:
        logger.error(f"  [motion] SVD failed for {image.name}: {e}")
    return None


def _loop_clip_to_duration(clip: Path, target_dur: float, out_path: Path) -> Path | None:
    """Loop the SVD clip to fill the target segment duration."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
    clip_dur = _probe_duration(clip)
    if clip_dur <= 0:
        return None
    # Loop the clip enough times to cover target_dur, then trim exactly.
    loops = max(1, int(target_dur / clip_dur) + 1)
    concat = out_path.parent / f"{out_path.stem}_concat.txt"
    concat.write_text("\n".join(f"file '{clip.resolve()}'" for _ in range(loops)))
    subprocess.run(
        f'ffmpeg -y -f concat -safe 0 -i "{concat}" -t {target_dur} '
        f'-c:v libx264 -pix_fmt yuv420p -preset medium -crf 18 -r 24 '
        f'-c:a aac -b:a 192k "{out_path}"',
        shell=True, capture_output=True, timeout=300)
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
    return None


def _split_baseline_segments(baseline: Path, workdir: Path) -> list[Path]:
    """Split the baseline multishot video into its 9 segments."""
    workdir.mkdir(parents=True, exist_ok=True)
    # Get segment boundaries from the concat file used to build the baseline.
    # The 9 segments have durations ~6.7s each (dialogue-driven). We re-derive
    # by splitting on scene boundaries using the known shot durations.
    # Simplest robust approach: split into 9 equal-ish segments by detecting
    # scene cuts via ffprobe scene detection is unreliable; instead we use the
    # known per-shot durations from the driver (SC01: 6.7, SC02: 6.4, SC03: 7.0).
    # We re-derive exact boundaries by re-rendering each segment from its image
    # is overkill. Instead, split the baseline by time using the shot durations.
    # Shot durations (from the multishot driver log):
    #   SC01-SH01 6.7, SC01-SH02 6.7, SC01-SH05 6.7,
    #   SC02-SH07 6.4, SC02-SH08 6.4, SC02-SH10 6.4,
    #   SC03-SH13 7.0, SC03-SH16 7.0, SC03-SH30 7.0
    shot_durs = [6.7, 6.7, 6.7, 6.4, 6.4, 6.4, 7.0, 7.0, 7.0]
    segments = []
    cursor = 0.0
    for i, d in enumerate(shot_durs):
        seg = workdir / f"seg_{i+1:02d}.mp4"
        subprocess.run(
            f'ffmpeg -y -ss {cursor:.3f} -i "{baseline}" -t {d:.3f} '
            f'-c copy "{seg}"',
            shell=True, capture_output=True, timeout=120)
        segments.append(seg)
        cursor += d
    return segments


async def main():
    print("=" * 60)
    print("  PROMETHEUS — EP-0001 real-motion proof (3 shots)")
    print("=" * 60)
    print(f"  Baseline : {BASELINE.name} ({_probe_duration(BASELINE):.1f}s)")
    print(f"  Selected : {[s['shot_id'] for s in SELECTED]}")

    # 1. Generate SVD motion clips for the 3 selected shots.
    print("\n[1/3] Generating SVD motion clips...")
    motion_clips: dict[str, Path] = {}
    for s in SELECTED:
        img = IMG_DIR / s["image"]
        clip = MOTION_DIR / f"{s['shot_id']}_svd.mp4"
        logger.info(f"  [motion] generating {s['shot_id']} ({s['type']})...")
        c = await generate_svd_clip(img, clip)
        if c:
            motion_clips[s["shot_id"]] = c
            logger.info(f"  [motion] {s['shot_id']} clip: {c.name} ({_probe_duration(c):.1f}s)")
        else:
            logger.warning(f"  [motion] {s['shot_id']} FAILED")

    if len(motion_clips) < 3:
        print(f"\n  Only {len(motion_clips)}/3 motion clips generated — cannot complete proof.")
        return {"ok": False, "clips": len(motion_clips)}

    # 2. Split baseline into 9 segments.
    print("\n[2/3] Splitting baseline into segments...")
    workdir = RENDER_DIR / "motion_proof" / "segments"
    segments = _split_baseline_segments(BASELINE, workdir)
    print(f"  segments: {len(segments)}")

    # 3. Replace the 3 selected segments with motion clips (looped to duration).
    print("\n[3/3] Splicing motion clips into timeline...")
    final_segments: list[Path] = []
    for i, seg in enumerate(segments, start=1):
        sel = next((s for s in SELECTED if s["segment"] == i), None)
        if sel and sel["shot_id"] in motion_clips:
            seg_dur = _probe_duration(seg)
            motion_looped = MOTION_DIR / f"{sel['shot_id']}_looped.mp4"
            ml = _loop_clip_to_duration(motion_clips[sel["shot_id"]], seg_dur, motion_looped)
            if ml:
                final_segments.append(ml)
                logger.info(f"  [splice] segment {i} ({sel['shot_id']}) -> real motion ({seg_dur:.1f}s)")
            else:
                final_segments.append(seg)
                logger.warning(f"  [splice] segment {i} motion loop failed, keeping Ken Burns")
        else:
            final_segments.append(seg)

    # Concatenate final segments.
    concat = RENDER_DIR / "motion_proof" / "concat_final.txt"
    concat.write_text("\n".join(f"file '{v.resolve()}'" for v in final_segments))
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" -c copy "{OUTPUT}"',
                   shell=True, capture_output=True, timeout=120)
    if not OUTPUT.exists() or OUTPUT.stat().st_size < 10000:
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" '
                       f'-c:v libx264 -pix_fmt yuv420p -crf 20 -r 24 '
                       f'-c:a aac -b:a 192k "{OUTPUT}"',
                       shell=True, capture_output=True, timeout=300)

    ok = OUTPUT.exists() and OUTPUT.stat().st_size > 10000
    print(f"\n  FINAL: {OUTPUT} ({OUTPUT.stat().st_size//1024}KB) ok={ok}")
    print(f"  Duration: {_probe_duration(OUTPUT):.1f}s")
    return {"ok": ok, "path": str(OUTPUT), "clips": len(motion_clips)}


if __name__ == "__main__":
    asyncio.run(main())
