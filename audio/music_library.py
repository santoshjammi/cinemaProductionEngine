"""
Music Library — downloads and manages CC0 cinematic tracks by mood.

Tracks are stored in videoGen/assets/music/ and selected by mood/emotion
for each scene. Uses Freesound CC0 tracks only — zero licensing cost.

Tracks are indexed by emotion tag so the pipeline auto-selects the right
score for each scene's emotional tone.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("music_library")

# Base directory for music assets
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "music"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Index file that maps emotions to available tracks
INDEX_PATH = ASSETS_DIR / "index.json"

# ─── Track Registry ───────────────────────────────────────────────────────
# Mood-tagged CC0 tracks from Freesound. Each entry:
#   key: friendly name (used for logging / selection)
#   url: direct download URL (from Freesound CC0 tracks)
#   moods: list of emotion tags this track fits
#   duration_sec: approximate duration for planning
#   source: attribution / credit

TRACK_REGISTRY: Dict[str, dict] = {
    "cinematic_ambient_piano": {
        "filename": "cinematic_ambient_piano.mp3",
        "moods": ["sad", "melancholic", "calm", "reflective", "hopeful"],
        "duration_sec": 120,
        "source": "YouTube Audio Library — Cinematic Ambient Piano (royalty-free)",
    },
    "solitude_piano": {
        "filename": "solitude_piano.mp3",
        "moods": ["sad", "melancholic", "calm", "peaceful", "lonely"],
        "duration_sec": 240,
        "source": "YouTube — Solitude Piano Ambient (royalty-free)",
    },
    "isolation_ambient": {
        "filename": "isolation_ambient.mp3",
        "moods": ["sad", "melancholic", "tense", "fearful", "dark", "lonely"],
        "duration_sec": 3600,
        "source": "YouTube — ISOLATION Cinematic Ambient (royalty-free)",
    },
    "circle_of_life_sad": {
        "filename": "circle_of_life_sad.mp3",
        "moods": ["sad", "melancholic", "reflective", "emotional", "grief"],
        "duration_sec": 243,
        "source": "YouTube — Circle of Life Ambient (royalty-free)",
    },
}

# ─── Download helpers ──────────────────────────────────────────────────────


def download_track(track_key: str, force: bool = False) -> Optional[Path]:
    """Check if a track file exists locally. Returns path on success, None on failure."""
    info = TRACK_REGISTRY.get(track_key)
    if not info:
        logger.error(f"Unknown track key: {track_key}")
        return None

    filename = info.get("filename", f"{track_key}.mp3")
    dest = ASSETS_DIR / filename

    if dest.exists() and not force:
        logger.info(f"  ✅ {track_key} (found locally)")
        return dest

    if not dest.exists():
        logger.warning(f"  ⬜ {track_key} not found at {dest}")
        logger.warning(f"  Run: cd {ASSETS_DIR} && place {filename} here from your CC0 source")
        return None

    return dest


def download_all(force: bool = False) -> Dict[str, Optional[Path]]:
    """Check all registered tracks."""
    results = {}
    for key in TRACK_REGISTRY:
        results[key] = download_track(key, force)
    return results


# ─── Selection / Index ────────────────────────────────────────────────────


def _build_index() -> dict:
    """Build or rebuild the track index from registry + files on disk."""
    index = {"tracks": {}}
    for key, info in TRACK_REGISTRY.items():
        path = ASSETS_DIR / f"{key}.mp3"
        index["tracks"][key] = {
            "path": str(path),
            "available": path.exists(),
            "moods": info["moods"],
            "duration_sec": info["duration_sec"],
            "source": info["source"],
        }
    return index


def save_index():
    """Persist the current track index to disk."""
    index = _build_index()
    INDEX_PATH.write_text(json.dumps(index, indent=2))
    logger.info(f"Index saved to {INDEX_PATH}")


def load_index() -> dict:
    """Load track index from disk, building it if missing."""
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text())
    idx = _build_index()
    save_index()
    return idx


def select_track_for_emotion(emotion: str) -> Optional[str]:
    """
    Pick the best available track for a given emotion/mood.
    Returns the track key, or None if nothing available.
    """
    index = load_index()
    emotion = emotion.lower().strip()

    # Exact emotion match first
    for key, info in index.get("tracks", {}).items():
        if info.get("available") and emotion in info.get("moods", []):
            logger.info(f"  [Music] '{emotion}' → {key}")
            return key

    # Fallback: try mood superset
    sad_fallback = ["cinematic_ambient_piano", "solitude_piano", "isolation_ambient", "circle_of_life_sad"]
    calm_fallback = ["cinematic_ambient_piano", "solitude_piano"]
    tense_fallback = ["isolation_ambient"]

    if emotion in ("sad", "melancholic", "grief", "lonely"):
        for key in sad_fallback:
            info = index.get("tracks", {}).get(key, {})
            if info.get("available"):
                return key
    elif emotion in ("calm", "peaceful", "hopeful"):
        for key in calm_fallback:
            info = index.get("tracks", {}).get(key, {})
            if info.get("available"):
                return key
    elif emotion in ("tense", "fearful", "anxious"):
        for key in tense_fallback:
            info = index.get("tracks", {}).get(key, {})
            if info.get("available"):
                return key

    # Last resort: first available track
    for key, info in index.get("tracks", {}).items():
        if info.get("available"):
            logger.warning(f"  [Music] No mood match for '{emotion}', falling back to {key}")
            return key

    logger.warning(f"  [Music] No tracks available for emotion '{emotion}'")
    return None


def get_track_path(track_key: str) -> Optional[Path]:
    """Get the filesystem path for a downloaded track."""
    info = TRACK_REGISTRY.get(track_key)
    if not info:
        return None
    filename = info.get("filename", f"{track_key}.mp3")
    p = ASSETS_DIR / filename
    return p if p.exists() else None


# ─── Loop / Stretch helpers ──────────────────────────────────────────────


def prepare_music_for_scene(
    track_key: str, target_duration_sec: int
) -> Optional[Path]:
    """
    Prepare a music file for the given scene duration.
    Downloads if needed, loops/stretches to match duration.
    Returns path to the prepared file.
    """
    src = get_track_path(track_key)
    if not src:
        # Try downloading
        src = download_track(track_key)
        if not src:
            return None

    prepared = ASSETS_DIR / f"{track_key}_prepared.wav"
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        str(src),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    actual_duration = float(result.stdout.strip() or 60)

    if actual_duration >= target_duration_sec:
        # Trim to target
        cmd = [
            "ffmpeg", "-y", "-i", str(src), "-t", str(target_duration_sec),
            "-c", "copy", str(prepared),
        ]
    else:
        # Loop until target duration
        loop_count = int(target_duration_sec / actual_duration) + 1
        concat_file = ASSETS_DIR / "_concat.txt"
        concat_file.write_text("\n".join([f"file '{src}'"] * loop_count))
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file), "-t", str(target_duration_sec),
            "-c", "copy", str(prepared),
        ]

    subprocess.run(cmd, capture_output=True)
    return prepared if prepared.exists() else None


# ─── Status ───────────────────────────────────────────────────────────────


def status_report() -> str:
    """Return a human-readable report of available tracks."""
    index = load_index()
    lines = ["🎵 Music Library Status"]
    lines.append("=" * 50)
    for key, info in sorted(index.get("tracks", {}).items()):
        icon = "✅" if info.get("available") else "⬜"
        moods = ", ".join(info.get("moods", []))
        lines.append(f"  {icon} {key:35s} [{moods}]")
    return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Downloading all CC0 tracks...")
    download_all()
    save_index()
    print(status_report())