"""GENESIS character-preparation step — makes characters ready for consistency.

Runs after GENESIS produces the brief (alongside performance enrichment) and
injects `brief['character_consistency']` so the image stage knows exactly which
characters to anchor and how tightly.

This is the "ground where we get the characters for the story ready": it
resolves the characters that appear in the brief (or the psychology default),
verifies each has a hero image in the character config, and records the
resolved set + img2img settings in the brief. Downstream, the image stage
consumes this block (falling back to auto-detection if absent).

The character → hero-image mapping itself lives in `config/characters.yaml`
(agnostic of niche/video) — this step just wires the brief to it.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from movie_os.character_consistency import (
    load_character_config,
    resolve_character_keys,
    is_psychology_video,
)

logger = logging.getLogger("movie_os.genesis2.character_prep")


def prepare_characters(
    brief: dict[str, Any],
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Resolve the characters for a brief and inject `character_consistency`.

    Mutates `brief` in place (sets `brief['character_consistency']`) and
    returns the injected block.

    The block:
        {
            "characters": ["mark", "sarah"],   # resolved config keys
            "source": "brief" | "psychology_default" | "none",
            "denoise": 0.4,
            "width": 1024,
            "height": 576,
        }
    """
    config = load_character_config(config_path)
    keys = resolve_character_keys(brief, config)

    if not keys:
        block = {
            "characters": [],
            "source": "none",
            "denoise": 0.4,
            "width": 1024,
            "height": 576,
        }
        logger.warning("[CharacterPrep] No characters resolved — consistency disabled")
    else:
        img2img = config.get("img2img") or {}
        source = "brief" if detect_explicit(brief) else (
            "psychology_default" if is_psychology_video(brief) else "brief"
        )
        block = {
            "characters": keys,
            "source": source,
            "denoise": float(img2img.get("denoise", 0.4)),
            "width": int(img2img.get("width", 1024)),
            "height": int(img2img.get("height", 576)),
        }
        logger.info(
            "[CharacterPrep] Resolved %d characters (%s): %s",
            len(keys), source, keys,
        )

    brief["character_consistency"] = block
    return block


def detect_explicit(brief: dict[str, Any]) -> bool:
    """Return True if the brief explicitly names characters (vs. defaulting)."""
    for scene in brief.get("scenes", []) or []:
        if scene.get("characters_present"):
            return True
    for d in brief.get("dialogues", []) or []:
        for line in (d.get("lines", []) or []) + (d.get("inner_voice", []) or []):
            if line.get("speaker"):
                return True
    return False
