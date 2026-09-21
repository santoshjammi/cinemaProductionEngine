"""Structured Media Validation (SAI-104 / TASK-024).

Validates workflow / image / audio / scene-video / final-video assets and
returns *structured evidence* (not just booleans): probe dimensions, duration,
codec, checksum where available, and an explicit pass/fail with a reason.

Fail-closed: a missing or unreadable asset is reported as an error, never a
silent pass. This is what lets the film stage trust that every input is real.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("movie_os.prometheus.media_validation")

_SUPPORTED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
_SUPPORTED_AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".ogg"}
_SUPPORTED_VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}
_SUPPORTED_WORKFLOW_EXT = {".json"}


@dataclass
class MediaCheck:
    """Structured evidence for one media artifact."""

    kind: str                 # workflow | image | audio | scene_video | final_video
    path: str
    exists: bool = False
    size_bytes: int = 0
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None
    codec: str | None = None
    checksum_sha256: str | None = None
    passed: bool = False
    reason: str = "not validated"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha256(path: str) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def _probe_media(path: str) -> tuple[int | None, int | None, float | None, str | None]:
    """Return (width, height, duration_s, codec) via ffprobe, or Nones."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "stream=codec_type,codec_name,width,height:format=duration",
                "-of", "json", path,
            ],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(r.stdout or "{}")
        width = height = None
        codec = None
        duration = None
        for st in data.get("streams", []):
            if st.get("codec_type") == "video":
                width = st.get("width"); height = st.get("height"); codec = st.get("codec_name")
        dur_raw = data.get("format", {}).get("duration")
        if dur_raw is not None:
            try:
                duration = float(dur_raw)
            except (TypeError, ValueError):
                duration = None
        return width, height, duration, codec
    except Exception as e:
        logger.warning(f"[media_validation] ffprobe failed on {path}: {e}")
        return None, None, None, None


def _validate_workflow(path: str) -> MediaCheck:
    check = MediaCheck(kind="workflow", path=path)
    p = Path(path)
    if not p.exists():
        check.reason = "missing"
        return check
    check.exists = True
    check.size_bytes = p.stat().st_size
    try:
        data = json.loads(p.read_text())
        if isinstance(data, dict) and data:
            check.passed = True
            check.reason = f"valid JSON with {len(data)} top-level keys"
        else:
            check.reason = "empty JSON object"
    except Exception as e:
        check.reason = f"invalid JSON: {e}"
    return check


def _validate_media(path: str, kind: str, min_duration: float | None = None) -> MediaCheck:
    check = MediaCheck(kind=kind, path=path)
    p = Path(path)
    if not p.exists():
        check.reason = "missing"
        return check
    check.exists = True
    check.size_bytes = p.stat().st_size
    check.checksum_sha256 = _sha256(path)
    width, height, dur, codec = _probe_media(path)
    check.width, check.height, check.duration_seconds, check.codec = width, height, dur, codec

    if kind == "image":
        if width and height and width > 0 and height > 0:
            check.passed = True
            check.reason = f"{width}x{height} image"
        else:
            check.reason = "image has no valid dimensions (corrupt?)"
    else:  # audio / scene_video / final_video
        if dur is not None and dur > 0:
            if min_duration is not None and dur < min_duration:
                check.reason = f"duration {dur:.1f}s below min {min_duration}s"
            else:
                check.passed = True
                check.reason = f"{dur:.1f}s, codec={codec or 'n/a'}"
        else:
            check.reason = "media has no readable duration"
    return check


def validate_artifact(asset: dict[str, Any]) -> MediaCheck:
    """Validate one artifact dict (path + type). Returns structured evidence."""
    path = str(asset.get("path") or asset.get("file") or "")
    kind = str(asset.get("type") or asset.get("kind") or "").lower()
    p = Path(path).suffix.lower()

    if kind == "workflow" or p in _SUPPORTED_WORKFLOW_EXT:
        return _validate_workflow(path)
    if kind in ("image", "scene_image") or p in _SUPPORTED_IMAGE_EXT:
        return _validate_media(path, "image")
    if kind in ("audio", "voice", "music", "ambience", "foley") or p in _SUPPORTED_AUDIO_EXT:
        return _validate_media(path, "audio")
    if kind in ("scene_video", "screengrab") or p in _SUPPORTED_VIDEO_EXT:
        return _validate_media(path, "scene_video")
    if kind in ("final_video", "film", "final") or path.endswith("_final.mp4"):
        return _validate_media(path, "final_video")
    # Unknown kind — fail closed.
    check = MediaCheck(kind=kind or "unknown", path=path)
    check.reason = f"unsupported kind '{kind}' / extension '{p}'"
    return check


def validate_collection(assets: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate a whole artifact collection; returns a structured report."""
    checks = [validate_artifact(a) for a in assets]
    passed = sum(1 for c in checks if c.passed)
    failed = sum(1 for c in checks if not c.passed)
    return {
        "total": len(checks),
        "passed": passed,
        "failed": failed,
        "all_passed": failed == 0,
        "checks": [c.to_dict() for c in checks],
    }
