#!/usr/bin/env python3
"""Quality Verification Stage — validates every image and audio asset
before it is allowed into the final film.

This is a mandatory gate in the render pipeline. An asset that fails
verification is flagged and (optionally) regenerated, never silently
passed through.

Checks:
  IMAGES:
    - file exists, non-zero size
    - valid PNG/JPEG, correct dimensions (>= 512px on short side)
    - not a solid-color / blank frame (stddev of pixels above threshold)
    - not a corrupted/truncated file (PIL open succeeds)
  AUDIO:
    - file exists, non-zero size
    - decodable by ffprobe, has a real duration
    - not silent (RMS level above threshold)
    - not clipped to death (peak not pinned at 0dB for whole file)
"""
from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("quality_gate")

# Thresholds
MIN_IMAGE_SHORT_SIDE = 512
MIN_IMAGE_STDDEV = 8.0          # below this = blank/solid frame
MIN_AUDIO_DURATION_S = 0.5
MIN_AUDIO_RMS = 0.005           # below this = effectively silent
MAX_AUDIO_PEAK = 0.999          # above this sustained = clipped


def _probe_audio(path: Path) -> dict | None:
    """Return {duration, rms, peak} via ffmpeg volumedetect, or None."""
    r = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None
    out = r.stderr
    dur = rms = peak = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            try:
                h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = int(h) * 3600 + int(m) * 60 + float(s)
            except Exception:
                pass
        if "mean_volume:" in line:
            try:
                rms = float(line.split("mean_volume:")[1].strip().split(" ")[0])
            except Exception:
                pass
        if "max_volume:" in line:
            try:
                peak = float(line.split("max_volume:")[1].strip().split(" ")[0])
            except Exception:
                pass
    return {"duration": dur, "rms_db": rms, "peak_db": peak}


def verify_image(path: Path) -> dict:
    """Verify a single image. Returns {ok, checks, errors}."""
    result = {"ok": True, "checks": {}, "errors": []}
    if not path.exists():
        return {"ok": False, "checks": {}, "errors": ["file missing"]}
    size = path.stat().st_size
    result["checks"]["size_bytes"] = size
    if size == 0:
        result["ok"] = False
        result["errors"].append("zero-byte file")
        return result

    try:
        from PIL import Image, ImageStat
        with Image.open(path) as im:
            im.load()
            w, h = im.size
            result["checks"]["dimensions"] = f"{w}x{h}"
            if min(w, h) < MIN_IMAGE_SHORT_SIDE:
                result["ok"] = False
                result["errors"].append(f"too small: {w}x{h}")
            # Blank-frame detection
            gray = im.convert("L")
            stat = ImageStat.Stat(gray)
            stddev = stat.stddev[0]
            result["checks"]["stddev"] = round(stddev, 2)
            if stddev < MIN_IMAGE_STDDEV:
                result["ok"] = False
                result["errors"].append(f"blank/solid frame (stddev={stddev:.1f})")
    except Exception as e:
        result["ok"] = False
        result["errors"].append(f"corrupt/unreadable: {e}")
    return result


def verify_audio(path: Path) -> dict:
    """Verify a single audio file. Returns {ok, checks, errors}."""
    result = {"ok": True, "checks": {}, "errors": []}
    if not path.exists():
        return {"ok": False, "checks": {}, "errors": ["file missing"]}
    size = path.stat().st_size
    result["checks"]["size_bytes"] = size
    if size == 0:
        result["ok"] = False
        result["errors"].append("zero-byte file")
        return result

    probe = _probe_audio(path)
    if probe is None or probe.get("duration") is None:
        result["ok"] = False
        result["errors"].append("undecodable by ffmpeg")
        return result

    dur = probe["duration"]
    result["checks"]["duration_s"] = round(dur, 2)
    if dur < MIN_AUDIO_DURATION_S:
        result["ok"] = False
        result["errors"].append(f"too short: {dur:.2f}s")

    rms_db = probe.get("rms_db")
    peak_db = probe.get("peak_db")
    result["checks"]["rms_db"] = rms_db
    result["checks"]["peak_db"] = peak_db

    if rms_db is not None:
        rms_lin = 10 ** (rms_db / 20)
        if rms_lin < MIN_AUDIO_RMS:
            result["ok"] = False
            result["errors"].append(f"silent (rms={rms_db:.1f}dB)")
    if peak_db is not None and peak_db >= 0.0:
        # peak at 0dB sustained = clipped
        result["ok"] = False
        result["errors"].append(f"clipped (peak={peak_db:.1f}dB)")
    return result


def verify_scene_assets(scene_id: int, frames: list[Path], mixed: Path | None) -> dict:
    """Verify all assets for one scene. Returns {ok, images, audio, errors}."""
    report = {"scene_id": scene_id, "ok": True, "images": [], "audio": None, "errors": []}

    for f in frames:
        v = verify_image(f)
        report["images"].append({"path": str(f), **v})
        if not v["ok"]:
            report["ok"] = False
            report["errors"].append(f"image {f.name}: {'; '.join(v['errors'])}")

    if mixed is not None:
        av = verify_audio(mixed)
        report["audio"] = {"path": str(mixed), **av}
        if not av["ok"]:
            report["ok"] = False
            report["errors"].append(f"audio {mixed.name}: {'; '.join(av['errors'])}")

    return report


def verify_all(scenes: list, scene_assets: dict) -> dict:
    """Verify all scenes. Returns {ok, scenes: [...], summary}."""
    reports = []
    all_ok = True
    for scene in scenes:
        sid = scene["id"]
        assets = scene_assets.get(sid, {})
        rep = verify_scene_assets(sid, assets.get("frames", []), assets.get("mixed"))
        reports.append(rep)
        if not rep["ok"]:
            all_ok = False
    return {
        "ok": all_ok,
        "scenes": reports,
        "summary": {
            "total_scenes": len(scenes),
            "passed": sum(1 for r in reports if r["ok"]),
            "failed": sum(1 for r in reports if not r["ok"]),
        },
    }


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    # CLI: verify a single image or audio file
    for p in sys.argv[1:]:
        path = Path(p)
        if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            print(json.dumps(verify_image(path), indent=2))
        else:
            print(json.dumps(verify_audio(path), indent=2))
