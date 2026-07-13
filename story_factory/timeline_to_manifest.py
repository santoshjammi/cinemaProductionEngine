"""Master Timeline → Pipeline Manifest adapter.

The existing psychological pipeline expects a manifest YAML with a specific
shape (narrative_arc, model, characters, scenes, etc). The Master Timeline
is a richer, platform-agnostic format.

This adapter reads a Master Timeline and produces the manifest format the
pipeline expects, so the pipeline doesn't need to change.

It also supports a shortcut: if the Master Timeline contains the full
narrative_arc structure (from the existing playbook), the adapter copies
it through. If not, it derives a default 3-act/9-beat arc from the scenes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml

from .master_timeline import MasterTimeline


def populate_shots_and_frames(
    timeline: MasterTimeline,
    character_registry: Optional[Any] = None,
) -> MasterTimeline:
    """Phase 7 — auto-generate Shots and Frames for each Scene.

    For each scene, the ShotPlanner decides how many shots (1-3) and
    the FramePlanner decides how many frames per shot (1 normally,
    2 for the irreversible moment).

    This is called automatically by timeline_to_manifest. The Master
    Timeline's scenes get their `shots` field populated.

    Args:
        timeline: The Master Timeline to enrich
        character_registry: Optional CharacterRegistry — if provided,
            frames will include character hero image references for
            IPAdapter consistency.

    Returns:
        The same timeline, mutated in place.
    """
    try:
        from movie_os.domain import ShotPlanner
    except ImportError:
        # movie_os not available — skip shot generation
        return timeline

    planner = ShotPlanner(character_registry=character_registry)
    for scene in timeline.scenes:
        existing_shots = getattr(scene, "shots", None)
        if existing_shots:
            continue
        try:
            shots = planner.plan_shots(scene)
            for shot in shots:
                shot.frames = planner.plan_frames(shot, scene)
            scene.shots = shots
        except AttributeError:
            # Old master_timeline.Scene doesn't support shots/frames
            continue
    return timeline


# Default 3-act / 9-beat arc — mirrors the playbook
DEFAULT_NARRATIVE_ARC: dict[str, Any] = {
    "act_1": {
        "title": "Observation",
        "viewer_response": "I know this feeling.",
        "scenes": [
            {"phase": "hook", "beat": "opening_hook", "scene_count": 1,
             "mood": "tense_restraint", "energy": 3, "ken_burns": "ken-burns"},
            {"phase": "warmth", "beat": "contrast_memory", "scene_count": 2,
             "mood": "warm_nostalgic", "energy": 7, "ken_burns": "zoom-in"},
            {"phase": "normalcy", "beat": "outside_version", "scene_count": 1,
             "mood": "flat_normal", "energy": 4, "ken_burns": "pan-right"},
        ],
    },
    "act_2": {
        "title": "Inner Reality",
        "viewer_response": "I didn't realize this was underneath it.",
        "scenes": [
            {"phase": "crack", "beat": "first_fracture", "scene_count": 1,
             "mood": "quiet_unease", "energy": 3, "ken_burns": "ken-burns"},
            {"phase": "collapse", "beat": "internal_collapse", "scene_count": 1,
             "mood": "deepening_darkness", "energy": 2, "ken_burns": "zoom-out"},
            {"phase": "collapse", "beat": "irreversible_moment", "scene_count": 1,
             "mood": "silence", "energy": 1, "ken_burns": "ken-burns"},
            {"phase": "almost", "beat": "almost_moment", "scene_count": 1,
             "mood": "tension", "energy": 5, "ken_burns": "zoom-in"},
        ],
    },
    "act_3": {
        "title": "Psychological Truth",
        "viewer_response": "That truth hurts.",
        "scenes": [
            {"phase": "retreat", "beat": "defensive_retreat", "scene_count": 1,
             "mood": "numb_protection", "energy": 2, "ken_burns": "pan-left"},
            {"phase": "duality", "beat": "her_truth", "scene_count": 1,
             "mood": "quiet_grief", "energy": 3, "ken_burns": "pan-left"},
            {"phase": "climax", "beat": "final_truth", "scene_count": 1,
             "mood": "devastating_quiet", "energy": 1, "ken_burns": "ken-burns"},
        ],
    },
}


def timeline_to_manifest(
    timeline: MasterTimeline,
    *,
    playbook_file: str = "../psychological_cinema_standard.yaml",
    context_file: str = "context.md",
    story_file: str = "story.md",
    dna_file: str = "dna.yaml",
    include_dna_context_story_refs: bool = True,
    character_registry: Optional[Any] = None,
) -> dict[str, Any]:
    """Convert a Master Timeline to a pipeline manifest dict.

    The resulting dict has the same shape as the existing
    VID01_template_refined.yaml manifest, so the pipeline can read it
    without modification.

    Args:
        timeline: The Master Timeline to convert.
        playbook_file: Path (relative to manifest location) to the playbook.
        context_file: Path to the context file (relative).
        story_file: Path to the story file (relative).
        dna_file: Path to the DNA file (relative).
        include_dna_context_story_refs: Whether to reference the factory
            artifacts in the manifest (for traceability).
        character_registry: Optional CharacterRegistry — if provided,
            shots will include character hero image references for
            IPAdapter consistency (Phase 6+7 integration).

    Returns:
        A dict that can be written as YAML and consumed by the pipeline.
    """
    # Phase 7 — populate Shots and Frames for each Scene
    populate_shots_and_frames(timeline, character_registry=character_registry)

    # Build the characters block (pipeline format)
    characters = {}
    for c in timeline.characters:
        characters[c.key] = {
            "name": c.name,
            "role": c.role or "supporting",
            "anchors": c.anchors or [
                f"{c.name}, real person, lived-in appearance",
            ],
            "emotional_range": c.emotional_range or [
                "restraint: hand frozen mid-reach",
                "tired: heavy eyes, posture not straight",
            ],
        }

    # Convert scenes to the pipeline format
    pipeline_scenes = []
    for s in timeline.scenes:
        # Shot language: the new Pydantic Scene has shot_language as a dict,
        # the old master_timeline.Scene has it as a ShotLanguage object.
        sl = s.shot_language
        if isinstance(sl, dict):
            shot_size = sl.get("shot_size", "medium")
            lighting_key = sl.get("lighting_key", "natural_shadows")
            lens_mm = sl.get("lens_mm", 50)
            depth_of_field = sl.get("depth_of_field", "shallow")
        else:
            shot_size = sl.shot_size
            lighting_key = sl.lighting_key
            lens_mm = sl.lens_mm
            depth_of_field = sl.depth_of_field

        # `act` field: the new Pydantic Scene doesn't have it, but the old one does.
        # The Pydantic Scene infers the act from the phase (e.g., "hook" → act_1).
        act_value = getattr(s, "act", None) or _infer_act_from_phase(getattr(s, "phase", ""))

        scene_dict = {
            # Phase 0 Pydantic Scene uses .number, but old master_timeline.Scene uses .scene_number.
            # Handle both for backward compat.
            "scene_number": getattr(s, "scene_number", None) or getattr(s, "number", None),
            "title": s.title,
            "phase": getattr(s, "phase", ""),
            "beat": getattr(s, "beat", ""),
            "act": act_value,
            "mood": getattr(s, "emotional_state", ""),
            "energy": getattr(s, "energy", 5),
            "voiceover": getattr(s, "voiceover", ""),
            "scene_description": getattr(s, "scene_description", ""),
            "scene_description_alt": getattr(s, "scene_description_alt", ""),  # v5.2
            "visual_cause_of_emotion": getattr(s, "visual_cause_of_emotion", ""),
            "shot_language": {
                "shot_size": shot_size,
                "lighting_key": lighting_key,
                "lens_mm": lens_mm,
                "depth_of_field": depth_of_field,
            },
            "characters_present": getattr(s, "characters_present", []),
            "ken_burns_effect": getattr(s, "ken_burns_effect", "ken-burns"),
            "duration_hint": getattr(s, "duration_hint", "20-30s"),
        }

        # Silence engine fields — handle both Pydantic dict and old SilenceEngine object
        se = getattr(s, "silence_engine", None)
        if se:
            if isinstance(se, dict):
                silence_before = se.get("silence_before", 0.0)
                silence_after = se.get("silence_after", 0.0)
                silence_instead = se.get("silence_instead", False)
            else:
                silence_before = se.silence_before
                silence_after = se.silence_after
                silence_instead = se.silence_instead
            if silence_before > 0:
                scene_dict["silence_before"] = silence_before
            if silence_after > 0:
                scene_dict["silence_after"] = silence_after
            if silence_instead:
                scene_dict["silence_instead"] = True

        if getattr(s, "vocal_fracture", False):
            scene_dict["vocal_fracture"] = True
        if getattr(s, "irreversible_moment", False):
            scene_dict["irreversible_moment"] = True
        if getattr(s, "pre_moment", False):
            scene_dict["pre_moment"] = True
        if getattr(s, "post_moment", False):
            scene_dict["post_moment"] = True
        if getattr(s, "shows_duality", False):
            scene_dict["shows_duality"] = True

        # Music volume override (for irreversible_moment) — handle both shapes
        mc = getattr(s, "music_cue", None)
        if mc:
            if isinstance(mc, dict):
                mc_zone = mc.get("zone", "act_1")
                mc_volume = mc.get("volume", 0.3)
            else:
                mc_zone = mc.zone
                mc_volume = mc.volume
            if mc_zone == "none" or mc_volume == 0.0:
                scene_dict["_music_volume_override"] = 0.0

        # Phase 7 — Shots and Frames (auto-generated if not present)
        scene_shots = getattr(s, "shots", None)
        if scene_shots:
            scene_dict["shots"] = [_shot_to_dict(shot) for shot in scene_shots]

        # v5.1 fade engine hooks — is_last_scene handled by pipeline
        pipeline_scenes.append(scene_dict)

    # Build the manifest
    # Top-level territory / archetype / cluster — the pipeline reads these
    # for territory-specific configuration (e.g., adapter archetype).
    # The story_factory block below keeps the full provenance for debugging.
    manifest = {
        "manifest_version": "4.0",
        "story_file": story_file,
        "context_files": [context_file],
        "playbook_file": playbook_file,
        # Top-level territory / archetype so the pipeline can read them
        # without digging into the story_factory block.
        "territory": timeline.metadata.get("territory", ""),
        "archetype": timeline.metadata.get("archetype", ""),
        "cluster": timeline.metadata.get("cluster", ""),
        "ending": timeline.metadata.get("ending", ""),
        "narrative_arc": DEFAULT_NARRATIVE_ARC,
        "model": {
            "name": "stabilityai/stable-diffusion-xl-base-1.0",
            "type": "sdxl",
            "dtype": "float16",
            "variant": "fp16",
            "device": "mps",
            "resolution": {"width": 1024, "height": 576},
        },
        "generation": {
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "num_candidates": 4,
            "min_clip_score": 0.30,
            "max_refine_rounds": 2,
            "candidate_seeds": [42, 137, 1024, 7777],
            "refinement_seeds": [314, 2718, 9999, 5678],
            "character_reference_strength": 0.45,
        },
        "characters": characters,
        "visual_system": {
            "style": "cinematic photorealism, 35mm film grain, muted desaturated tones",
            "color_palette": {
                "dominant": "cool blue undertones",
                "practical_lights": "warm amber",
                "shadows": "deep but not crushed",
                "highlights": "soft, rolled off",
            },
            "texture": "shallow depth of field, natural film grain, soft contrast",
            "negative_prompt": "cartoon, anime, illustration, painting, 3d render, cgi, "
                "video game, blurry, low quality, distorted, deformed, disfigured, "
                "bad anatomy, extra limbs, extra fingers, watermark, signature, text, "
                "oversaturated, hdr, plastic skin, duplicate, cloned, overlapping subjects",
        },
        "scenes": pipeline_scenes,
    }

    # Optional traceability refs
    if include_dna_context_story_refs:
        manifest["story_factory"] = {
            "version": "1.0",
            "dna_file": dna_file,
            "context_file": context_file,
            "story_file": story_file,
            "master_timeline_id": timeline.metadata.get("id", ""),
            "territory": timeline.metadata.get("territory", ""),
            "cluster": timeline.metadata.get("cluster", ""),
            "ending": timeline.metadata.get("ending", ""),
        }

    return manifest


def save_manifest(manifest: dict[str, Any], path: str | Path) -> None:
    """Write a manifest dict to a YAML file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(
            manifest,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=100,
        )


# ---------------------------------------------------------------------------
# Phase 7 — Shot and Frame serialization
# ---------------------------------------------------------------------------

def _infer_act_from_phase(phase: str) -> str:
    """Infer the act name from a phase string (for the new Pydantic Scene).

    The new Scene model uses `phase` (e.g., "hook", "warmth") but the old
    Scene model (and the manifest) need an `act` (e.g., "act_1_observation").
    This helper bridges the two.
    """
    mapping = {
        "hook": "act_1_observation",
        "warmth": "act_1_observation",
        "normalcy": "act_1_observation",
        "crack": "act_2_inner_reality",
        "collapse": "act_2_inner_reality",
        "almost": "act_2_inner_reality",
        "retreat": "act_3_psychological_truth",
        "duality": "act_3_psychological_truth",
        "climax": "act_3_psychological_truth",
    }
    return mapping.get(phase, "act_1_observation")


def _shot_to_dict(shot) -> dict[str, Any]:
    """Serialize a Shot to a manifest dict."""
    return {
        "shot_number": shot.number,
        "shot_size": shot.shot_size,
        "camera_movement": shot.camera_movement,
        "lens_mm": shot.lens_mm,
        "duration_seconds": shot.duration_seconds,
        "visual_intent": shot.visual_intent,
        "prompt_context": shot.prompt_context,
        "frames": [_frame_to_dict(f) for f in shot.frames],
    }


def _frame_to_dict(frame) -> dict[str, Any]:
    """Serialize a Frame to a manifest dict."""
    return {
        "frame_number": frame.number,
        "description": frame.description,
        "visual_cause_of_emotion": frame.visual_cause_of_emotion,
        "workflow": frame.workflow,
        "model": frame.model,
        "reference_image_ids": [str(uid) for uid in frame.reference_image_ids],
    }
