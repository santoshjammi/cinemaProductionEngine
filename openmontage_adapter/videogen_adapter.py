"""videogen_adapter — converts videoGen scene manifests to SceneIntents.

This is the bridge between videoGen's existing YAML manifests (in
``videoContentStructure/Psychology/<Territory>/VID##_template.yaml``) and
the render abstraction layer's ``SceneIntent``.

Usage:

    from openmontage_adapter import videogen_adapter

    intents = videogen_adapter.manifest_to_intents(
        manifest_path="videoContentStructure/Psychology/EmotionalWithdrawal/VID01_template_refined.yaml",
        territory="emotional_withdrawal",
        archetype="slow_withdrawal",
    )
    # intents is a list[SceneIntent] ready for the orchestrator
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from .scene_intent import SceneIntent

logger = logging.getLogger("videogen_adapter")


def manifest_to_intents(
    manifest_path: str | Path,
    territory: str = "emotional_withdrawal",
    archetype: str = "slow_withdrawal",
    output_dir: str | Path = "output/videos",
) -> list[SceneIntent]:
    """Convert a videoGen manifest YAML to a list of SceneIntents.

    Args:
        manifest_path: Path to the manifest YAML (e.g. VID01_template_refined.yaml)
        territory: The territory name
        archetype: The archetype name
        output_dir: Where rendered assets should be written

    Returns:
        A list of SceneIntent, one per scene in the manifest

    The manifest is expected to have:
    - ``scenes``: a list of scene dicts (per the v1.1 schema)
    - ``characters``: a dict of character_key → {anchors, ...}
    - ``visual_system``: a dict with style, negative_prompt, etc.
    - ``model.resolution``: {width, height}
    - ``generation``: num_candidates, min_clip_score, etc.
    """
    manifest_path = Path(manifest_path)
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)

    scenes = manifest.get("scenes", [])
    if not scenes:
        logger.warning("Manifest %s has no scenes", manifest_path)
        return []

    # Extract character references (hero images)
    manifest_dir = manifest_path.parent
    characters = manifest.get("characters", {})
    character_references: dict[str, Path] = {}
    character_anchors: dict[str, list[str]] = {}
    for char_key, char_def in characters.items():
        anchors = char_def.get("anchors", [])
        character_anchors[char_key] = anchors if isinstance(anchors, list) else [anchors]
        # Look for hero image: characters/<char_key>_hero.png
        hero_path = manifest_dir / "characters" / f"{char_key}_hero.png"
        if hero_path.exists():
            character_references[char_key] = hero_path

    # Extract visual system defaults
    vs = manifest.get("visual_system", {})
    style = vs.get("style", "cinematic photorealism, 35mm film grain")
    negative_prompt = vs.get("negative_prompt", "")

    # Extract model resolution
    model = manifest.get("model", {})
    res = model.get("resolution", {})
    resolution = (res.get("width", 1024), res.get("height", 576))

    # Extract generation params
    gen = manifest.get("generation", {})
    num_candidates = gen.get("num_candidates", 4)
    min_clip_score = gen.get("min_clip_score", 0.30)
    candidate_seeds = gen.get("candidate_seeds", [42, 137, 1024, 7777])
    img2img_strength = gen.get("character_reference_strength", 0.45)

    # Derive pipeline_id from manifest stem
    pipeline_id = manifest_path.stem.lower().replace("_sdxl", "").replace("_revised", "")

    # Convert each scene to a SceneIntent
    intents: list[SceneIntent] = []
    for scene in scenes:
        intent = _scene_to_intent(
            scene=scene,
            manifest=manifest,
            manifest_path=manifest_path,
            territory=territory,
            archetype=archetype,
            output_dir=output_dir,
            pipeline_id=pipeline_id,
            character_references=character_references,
            character_anchors=character_anchors,
            style=style,
            negative_prompt=negative_prompt,
            resolution=resolution,
            num_candidates=num_candidates,
            min_clip_score=min_clip_score,
            candidate_seeds=candidate_seeds,
            img2img_strength=img2img_strength,
        )
        intents.append(intent)

    logger.info("Converted manifest %s → %d SceneIntents", manifest_path.name, len(intents))
    return intents


def _scene_to_intent(
    scene: dict,
    manifest: dict,
    manifest_path: Path,
    territory: str,
    archetype: str,
    output_dir: str | Path,
    pipeline_id: str,
    character_references: dict[str, Path],
    character_anchors: dict[str, list[str]],
    style: str,
    negative_prompt: str,
    resolution: tuple,
    num_candidates: int,
    min_clip_score: float,
    candidate_seeds: list[int],
    img2img_strength: float,
) -> SceneIntent:
    """Convert a single videoGen scene dict to a SceneIntent."""
    scene_num = scene.get("scene_number", 0)
    beat = scene.get("beat", scene.get("phase", "internal_collapse"))
    act = scene.get("act", "act_2_inner_reality")
    phase = scene.get("phase", "collapse")
    energy = scene.get("energy", 5)

    # Determine soundtrack zone from act
    soundtrack_zone = {
        "act_1_observation": "act_1",
        "act_2_inner_reality": "act_2",
        "act_3_psychological_truth": "act_3",
    }.get(act, "act_2")

    # Music volume by zone
    music_volume = {"act_1": 0.35, "act_2": 0.25, "act_3": 0.15}.get(soundtrack_zone, 0.25)

    # Irreversible moment overrides
    irreversible = bool(scene.get("irreversible_moment", False))
    if irreversible:
        soundtrack_zone = "silent"
        music_volume = 0.0

    # Character references for this scene
    chars_present = scene.get("characters_present", [])
    char_refs: list[Path] = []
    char_anc: list[str] = []
    for char_key in chars_present:
        if char_key in character_references:
            char_refs.append(character_references[char_key])
        if char_key in character_anchors:
            char_anc.extend(character_anchors[char_key])

    # Determine prosody register
    prosody_register = "default"
    if irreversible:
        prosody_register = "irreversible_moment"
    elif act == "act_3_psychological_truth":
        if phase == "climax" and not scene.get("silence_instead"):
            prosody_register = "emotionally_exhausted"
        else:
            prosody_register = "fractured"
    elif act == "act_2_inner_reality" and energy <= 3:
        prosody_register = "vulnerable"

    # Output path
    output_path = Path(output_dir) / pipeline_id / "scene_images" / f"scene_{scene_num:03d}.png"

    # Parse duration_hint (may be "20-30s" or a number)
    duration_hint = scene.get("duration_hint", "5s")
    if isinstance(duration_hint, str):
        import re
        m = re.search(r"(\d+(?:\.\d+)?)", duration_hint)
        duration = float(m.group(1)) if m else 5.0
    else:
        duration = float(duration_hint)

    # Build the SceneIntent
    intent = SceneIntent(
        scene_id=f"{pipeline_id}-scene-{scene_num:03d}",
        title=scene.get("title", f"Scene {scene_num}"),
        emotional_state=_extract_emotional_state(scene),
        emotional_subtext=scene.get("voiceover", ""),
        visual_symbolism=_extract_symbols(scene),
        what_is_NOT_shown="",
        camera_language=scene.get("shot_language", {}),
        soundtrack_zone=soundtrack_zone,
        music_volume=music_volume,
        ambient_sfx_profile=beat if beat in (
            "opening_hook", "contrast_memory", "outside_version",
            "first_fracture", "internal_collapse", "irreversible_moment",
            "defensive_retreat", "her_truth", "final_truth",
        ) else "internal_collapse",
        ambient_volume=0.42 if irreversible else 0.30,
        silence_before_seconds=float(scene.get("silence_before", 0.0)),
        silence_after_seconds=float(scene.get("silence_after", 0.0)),
        silence_instead=bool(scene.get("silence_instead", False)),
        narration_text=scene.get("voiceover", ""),
        narration_prosody_register=prosody_register,
        vocal_fracture=bool(scene.get("irreversible_moment", False)) and bool(scene.get("voiceover", "").strip()),
        breath_pre_pad_ms=400 if irreversible else 0,
        break_words=_extract_break_words(scene.get("voiceover", "")),
        emphasis_words=_extract_emphasis_words(scene),
        subtitle_emphasis_words=_extract_emphasis_words(scene),
        subtitle_pause_after_words=_extract_break_words(scene.get("voiceover", "")),
        subtitle_phrase_pacing=True,
        subtitle_max_words_per_caption=5 if irreversible else 6,
        character_references=char_refs,
        character_anchors=char_anc,
        characters_present=chars_present,
        style_anchor=style,
        negative_prompts=[negative_prompt] if negative_prompt else [],
        micro_behaviors=scene.get("micro_behaviors", ["unfinished_movements"]),
        environmental_imperfections=scene.get("environmental_imperfections", ["kitchen_mess", "fabric_wear"]),
        resolution=resolution,
        output_path=output_path,
        inference_steps=30,
        guidance_scale=7.5,
        num_candidates=num_candidates,
        min_clip_score=min_clip_score,
        candidate_seeds=candidate_seeds,
        img2img_strength=img2img_strength,
        in_transition="fade_black" if irreversible else "cut",
        out_transition="cut",
        irreversible_moment=irreversible,
        pre_moment=bool(scene.get("pre_moment", False)),
        post_moment=bool(scene.get("post_moment", False)),
        shows_duality=bool(scene.get("shows_duality", False)),
        is_quiet_moment=False,
        duration_seconds=duration,
        beat=beat,
        act=act,
        phase=phase,
        energy=energy,
        archetype=archetype,
        territory=territory,
        index=scene_num,
        raw_scene=scene,
    )

    # If there's a tts_prosody_override in the scene, honor it
    if scene.get("tts_prosody_override"):
        override = scene["tts_prosody_override"]
        # Store in raw_scene for the pipeline to pick up
        intent.raw_scene["_tts_prosody_override"] = override

    return intent


# ---------- PRIVATE HELPERS ----------

_LOADED_WORDS = frozenset({
    "still", "almost", "dangerous", "tired", "grief", "afraid",
    "love", "lost", "alone", "home", "safe", "reaching", "remember",
    "quiet", "enough", "silence", "stayed", "stopped", "left",
})


def _extract_emotional_state(scene: dict) -> str:
    """Extract the primary emotional state from a scene dict."""
    mood = scene.get("mood", "").lower()
    if "warm" in mood or "nostalg" in mood:
        return "warmth"
    if "dark" in mood or "collapse" in mood:
        return "grief"
    if "numb" in mood or "resigned" in mood:
        return "resigned"
    if "quiet" in mood:
        return "restrained"
    if "tense" in mood or "restraint" in mood:
        return "restrained"
    if scene.get("irreversible_moment"):
        return "interrupted"
    if scene.get("shows_duality"):
        return "wounded"
    return "restrained"


def _extract_symbols(scene: dict) -> list[str]:
    """Extract visual_symbolism tokens from a scene dict."""
    symbols: list[str] = []
    desc = scene.get("scene_description", "").lower()
    if "not touching" in desc or "gap between" in desc or "distance" in desc:
        symbols.append("physical_distance")
    if "dark" in desc or "shadow" in desc or "night" in desc or "low light" in desc:
        symbols.append("low_light")
    if "look down" in desc or "looking at hands" in desc or "not meeting" in desc:
        symbols.append("downward_eye_contact")
    if "almost" in desc and ("reach" in desc or "touch" in desc):
        symbols.append("unfinished_gesture")
    if "wrinkled" in desc or "unwashed" in desc or "messy" in desc or "dust" in desc:
        symbols.append("imperfection")
    if "midnight" in desc or "can't sleep" in desc:
        symbols.append("nighttime_honesty")
    if "door" in desc and ("not quite" in desc or "cracked" in desc or "ajar" in desc):
        symbols.append("transition_object")
    return symbols or ["physical_distance", "low_light"]


def _extract_break_words(voiceover: str) -> list[str]:
    """Find loaded words in the voiceover that should be preceded by a break."""
    words = voiceover.lower().split()
    return [w.strip(".,!?;:") for w in words if w.strip(".,!?;:") in _LOADED_WORDS]


def _extract_emphasis_words(scene: dict) -> list[str]:
    """Extract emphasis words from a scene dict."""
    vo = scene.get("voiceover", "")
    return _extract_break_words(vo)