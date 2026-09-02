"""
Cinematic Music Selector — application module for videoGen.

Selects CC0 music tracks from the assets/music/ library, matching
Hans Zimmer / Jóhann Jóhannsson / Randy Newman style scores to emotional arcs.

Usage:
    from movie_os.audio.music_selector import get_track_for_scene
    path = get_track_for_scene(scene_id=4)
    # Returns Path to the best-matching CC0 track
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger("movie_os.audio.music_selector")

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "music"
INDEX_PATH = ASSETS_DIR / "index.json"

# Scene-to-track mapping — picks the right CC0 track for each scene's emotional arc
SCENE_TRACK_MAP = {
    # Hook — vast, melancholic orchestral (Zimmer Interstellar style)
    1: "scott_buckley_sad",
    # Establishment — intimate piano (Randy Newman Marriage Story style)
    2: "cinematic_ambient_piano",
    # Dialogue — tense + beautiful strings (Jóhannsson Arrival style)
    3: "dark_rain_piano_strings",
    # Emotional peak — emotional strings + piano (climax build)
    4: "circle_of_life_sad",
    # Montage — ambient isolation (dark, lonely)
    5: "isolation_ambient",
    # Reflection — vulnerable piano solo (Zimmer piano motif)
    6: "lucas_king_hurt",
    # Transition — dark tension (building toward climax)
    7: "piano_strings_loop",
    # Climax — epic orchestral sweep (Zimmer elevation)
    8: "savfk_sad_state",
}


def _load_index() -> dict:
    """Load the music asset index."""
    if INDEX_PATH.exists():
        try:
            return json.loads(INDEX_PATH.read_text())
        except Exception as e:
            logger.warning(f"Cannot load music index: {e}")
    return {"tracks": {}}


def get_track_for_scene(
    scene_id: int,
    emotion: str = "melancholic",
    scene_class: str = "dialogue",
) -> Optional[Path]:
    """
    Select the best CC0 music track for a scene.

    Args:
        scene_id: Scene number (1-based)
        emotion: Scene emotion tag
        scene_class: Scene class (hook, dialogue, climax, etc.)

    Returns:
        Path to the selected CC0 track, or None if no track found.
    """
    track_key = SCENE_TRACK_MAP.get(scene_id)

    # Try explicit scene mapping first
    if track_key:
        # Check index.json first
        index = _load_index()
        if track_key in index.get("tracks", {}):
            track_info = index["tracks"][track_key]
            path = Path(track_info["path"])
            if path.exists():
                logger.info(f"Music scene {scene_id}: {track_key} "
                           f"({', '.join(track_info.get('moods', [])[:2])})")
                return path

        # Fall back to direct file lookup
        direct_path = ASSETS_DIR / f"{track_key}.mp3"
        if direct_path.exists():
            logger.info(f"Music scene {scene_id}: {track_key} (direct)")
            return direct_path

    # Fallback: scan index for best mood match
    index = _load_index()
    best_match = None
    best_score = 0

    for key, info in index.get("tracks", {}).items():
        path = Path(info["path"])
        if not path.exists():
            continue
        moods = info.get("moods", [])
        score = 0
        if emotion in moods:
            score += 2
        if scene_class in ["climax", "emotional_peak"] and "emotional" in moods:
            score += 2
        if scene_class in ["dialogue", "establishment"] and "calm" in moods:
            score += 1
        if score > best_score:
            best_score = score
            best_match = path

    if best_match:
        logger.info(f"Music scene {scene_id}: fallback to {best_match.name}")
        return best_match

    return None


def list_available_tracks() -> list[str]:
    """List all available CC0 music tracks with metadata."""
    index = _load_index()
    available = []
    for key, info in index.get("tracks", {}).items():
        path = Path(info["path"])
        if path.exists():
            moods = ", ".join(info.get("moods", []))
            dur = info.get("duration_sec", 0)
            available.append(f"{key}: {dur}s — {moods}")
    # Also check for unindexed .mp3 files (newly added tracks)
    for f in sorted(ASSETS_DIR.glob("*.mp3")):
        key = f.stem
        if key not in index.get("tracks", {}):
            size_mb = f.stat().st_size / (1024 * 1024)
            available.append(f"{key}: {size_mb:.0f}MB (unindexed)")
    return available


def get_track_duration(track_path: Path) -> Optional[float]:
    """Get duration of a music track in seconds."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(track_path)],
            capture_output=True, text=True, timeout=10
        )
        if r.stdout.strip():
            return float(r.stdout.strip())
    except Exception as e:
        logger.warning(f"Cannot get duration for {track_path}: {e}")
    return None