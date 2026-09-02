"""Character consistency — data-driven, agnostic of niche or video characters.

The mechanism is generic: given a set of characters (each with a hero
reference image), it composites them into a single anchor image and the
image stage uses that composite as the img2img reference so every character
keeps the same identity across all scenes.

The character → hero-image mapping lives in `config/characters.yaml` — the
single place to wire in ANY video's characters. This module:

  1. Loads the character config (data-driven, not hardcoded).
  2. Normalizes character keys (case-insensitive, strips `_INNER` suffix).
  3. Auto-detects the characters that appear in a brief (from
     `scenes[].characters_present` and dialogue speakers).
  4. Defaults to Mark & Sarah for psychology videos that don't name characters.
  5. Builds an N-character composite (2, 3, 4+ characters) as the img2img anchor.

The image stage consumes `brief['character_consistency']` (injected by the
GENESIS character-preparation step) and falls back to auto-detection.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("movie_os.character_consistency")

# Canonical config path — the single place to wire in any video's characters.
DEFAULT_CONFIG_PATH = Path("config/characters.yaml")

# ComfyUI's LoadImage reads from its input directory; the composite must live
# there (referenced by filename, not absolute path).
COMFYUI_INPUT_DIR = Path("/Users/santosh/ComfyUI-Shared/input")
COMPOSITE_FILENAME = "character_ref_composite.png"

# Psychology niche markers — if a video is psychology and names no characters,
# default to Mark & Sarah.
PSYCHOLOGY_NICHES = {"psychology", "relationship & emotional psychology", "relationship"}


# --------------------------------------------------------------------------- #
# Config loading                                                              #
# --------------------------------------------------------------------------- #

def load_character_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load the character config YAML. Returns {} if missing/invalid."""
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not path.exists():
        logger.warning("Character config not found: %s", path)
        return {}
    try:
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return data
    except Exception as e:
        logger.warning("Failed to load character config %s: %s", path, e)
        return {}


# --------------------------------------------------------------------------- #
# Key normalization                                                           #
# --------------------------------------------------------------------------- #

def normalize_key(speaker: str) -> str:
    """Normalize a brief speaker name to a config key.

    "MARK", "Mark", "mark", "MARK_INNER" → "mark". Strips the `_INNER` suffix
    (inner voice belongs to the same character) and lowercases.
    """
    if not speaker:
        return ""
    key = speaker.strip().upper()
    if key.endswith("_INNER"):
        key = key[: -len("_INNER")]
    return key.lower()


# --------------------------------------------------------------------------- #
# Character detection from a brief                                            #
# --------------------------------------------------------------------------- #

def detect_characters_from_brief(brief: dict[str, Any]) -> list[str]:
    """Detect the characters that appear in a brief.

    Sources (in priority order):
      1. `brief['character_consistency']['characters']` (explicit, injected by
         the GENESIS character-preparation step).
      2. `scenes[].characters_present` (names like "Mark", "Sarah").
      3. Dialogue speakers (MARK, SARAH, MARK_INNER).
    Returns a list of normalized config keys.
    """
    keys: list[str] = []

    # 1. Explicit character_consistency block (highest priority).
    cc = brief.get("character_consistency") or {}
    for c in cc.get("characters", []) or []:
        if isinstance(c, str):
            k = normalize_key(c)
        elif isinstance(c, dict):
            k = normalize_key(c.get("key") or c.get("name") or "")
        else:
            continue
        if k and k not in keys:
            keys.append(k)

    # 2. scenes[].characters_present
    for scene in brief.get("scenes", []) or []:
        for name in scene.get("characters_present", []) or []:
            k = normalize_key(str(name))
            if k and k not in keys:
                keys.append(k)

    # 3. Dialogue speakers
    for d in brief.get("dialogues", []) or []:
        for line in (d.get("lines", []) or []) + (d.get("inner_voice", []) or []):
            k = normalize_key(str(line.get("speaker", "")))
            if k and k not in keys:
                keys.append(k)

    return keys


def is_psychology_video(brief: dict[str, Any]) -> bool:
    """Return True if the brief is a psychology video."""
    niche = str(
        brief.get("contract", {}).get("classification", {}).get("niche", "")
        or brief.get("ontology_selection", {}).get("niche", "")
        or brief.get("metadata", {}).get("niche", "")
    ).lower()
    return niche in PSYCHOLOGY_NICHES or "psycholog" in niche


def resolve_character_keys(brief: dict[str, Any], config: dict[str, Any]) -> list[str]:
    """Resolve the ordered list of character config keys for a brief.

    Priority:
      1. Explicit `brief['character_consistency']['characters']`.
      2. Auto-detected from the brief (characters_present / speakers).
      3. Psychology default (Mark & Sarah) if the video is psychology.
    Filters to keys that exist in the config (have a hero image).
    """
    detected = detect_characters_from_brief(brief)
    if detected:
        keys = detected
    elif is_psychology_video(brief):
        keys = list(config.get("psychology_default", []) or [])
        logger.info("Psychology video with no explicit characters — defaulting to %s", keys)
    else:
        keys = []

    # Keep only keys that exist in the config.
    available = set((config.get("characters") or {}).keys())
    return [k for k in keys if k in available]


# --------------------------------------------------------------------------- #
# Composite building                                                          #
# --------------------------------------------------------------------------- #

def build_composite(
    config: dict[str, Any],
    keys: list[str],
    out_dir: Path | None = None,
    width: int = 1024,
    height: int = 576,
) -> Path | None:
    """Composite the hero images of the given characters into one anchor.

    Characters are laid out left-to-right, each occupying an equal slice.
    Returns the absolute path of the composite (saved into ComfyUI's input
    dir so LoadImage can read it by filename), or None if any hero image is
    missing.
    """
    chars = config.get("characters") or {}
    heroes: list[tuple[str, Path]] = []
    for key in keys:
        entry = chars.get(key) or {}
        hero = entry.get("hero_image")
        if not hero:
            logger.warning("Character '%s' has no hero_image in config", key)
            continue
        p = Path(hero)
        if not p.exists():
            logger.warning("Hero image for '%s' not found: %s", key, p)
            continue
        heroes.append((key, p))

    if not heroes:
        logger.warning("No usable hero images for characters %s", keys)
        return None

    try:
        from PIL import Image
    except ImportError:
        logger.error("Pillow not available — cannot build composite")
        return None

    n = len(heroes)
    slice_w = width // n
    composite = Image.new("RGB", (width, height))
    for i, (key, hero_path) in enumerate(heroes):
        img = Image.open(hero_path).convert("RGB").resize((slice_w, height), Image.LANCZOS)
        composite.paste(img, (i * slice_w, 0))
        logger.info("  composite[%d] = %s (%s)", i, key, hero_path)

    target_dir = out_dir or COMFYUI_INPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    out_path = target_dir / COMPOSITE_FILENAME
    composite.save(out_path)
    logger.info("Built %d-character composite: %s", n, out_path)
    return out_path


# --------------------------------------------------------------------------- #
# Public entry point                                                          #
# --------------------------------------------------------------------------- #

def ensure_character_consistency(
    brief: dict[str, Any] | None = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Idempotent entry point: resolve characters + build the composite.

    Args:
        brief: The movie brief (used to detect characters / psychology default).
        config_path: Optional override for the character config path.

    Returns a dict consumed by the image stage:
        {
            "reference_filename": "character_ref_composite.png" or None,
            "characters": [keys...],
            "denoise": 0.4,
            "width": 1024,
            "height": 576,
        }
    """
    brief = brief or {}
    config = load_character_config(config_path)
    keys = resolve_character_keys(brief, config)

    if not keys:
        logger.warning("No characters resolved for consistency — img2img anchor disabled")
        return {
            "reference_filename": None,
            "characters": [],
            "denoise": 0.4,
            "width": 1024,
            "height": 576,
        }

    img2img = config.get("img2img") or {}
    width = int(img2img.get("width", 1024))
    height = int(img2img.get("height", 576))
    denoise = float(img2img.get("denoise", 0.4))

    built = build_composite(config, keys, width=width, height=height)
    return {
        "reference_filename": COMPOSITE_FILENAME if built else None,
        "characters": keys,
        "denoise": denoise,
        "width": width,
        "height": height,
    }
