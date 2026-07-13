"""OpenMontageAdapter — translates OpenMontage scene_plan to SceneIntent.

OpenMontage (https://github.com/calesthio/OpenMontage) uses its own scene
description format defined in ``schemas/artifacts/scene_plan.schema.json``.
This adapter translates that format into videoGen's ``SceneIntent`` so
OpenMontage can use videoGen as a render backend.

The translation is **lossy in one direction**: OpenMontage's format is
more general (it handles talking_head, broll, animation, etc.) while
videoGen specializes in psychological cinema stills. The adapter maps
the relevant fields and drops the rest.

The reverse direction (SceneIntent → OpenMontage scene) is also supported
for the case where videoGen wants to hand off to OpenMontage's Remotion
composer for final assembly.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .scene_intent import SceneIntent

logger = logging.getLogger("om_adapter")


# Translation tables — OpenMontage vocabulary → videoGen vocabulary

OM_TO_VIDEOGEN_TRANSLATIONS: dict[str, dict[str, str]] = {
    # OpenMontage shot_size → videoGen shot_size
    "shot_size": {
        "extreme_wide": "extreme_wide",
        "wide": "wide",
        "medium_wide": "medium_wide",
        "medium": "medium",
        "medium_close": "medium_close",
        "close_up": "close_up",
        "extreme_close_up": "extreme_close_up",
        "over_shoulder": "over_shoulder",
        "insert": "extreme_close_up",
        "establishing": "wide",
    },
    # OpenMontage camera_movement → videoGen movement
    "camera_movement": {
        "static": "static",
        "pan_left": "pan_left",
        "pan_right": "pan_right",
        "tilt_up": "static",
        "tilt_down": "static",
        "dolly_in": "slow_push_in",
        "dolly_out": "slow_pull_out",
        "tracking_left": "parallax_drift",
        "tracking_right": "parallax_drift",
        "crane_up": "static",
        "crane_down": "static",
        "handheld": "handheld_drift",
        "steadicam": "static",
        "whip_pan": "static",
        "orbital": "parallax_drift",
        "zoom_in": "slow_push_in",
        "zoom_out": "slow_pull_out",
        "rack_focus": "static",
    },
    # OpenMontage lighting_key → videoGen lighting_key
    "lighting_key": {
        "high_key": "high_key",
        "low_key": "low_key",
        "natural": "natural",
        "golden_hour": "golden_hour",
        "blue_hour": "blue_hour",
        "tungsten_warm": "tungsten_warm",
        "neon": "low_key",
        "silhouette": "silhouette",
        "rim_lit": "rim_lit",
        "volumetric": "volumetric",
        "overcast_soft": "overcast_soft",
    },
    # OpenMontage depth_of_field → videoGen depth_of_field
    "depth_of_field": {
        "shallow": "shallow",
        "medium": "medium",
        "deep": "deep",
    },
    # OpenMontage color_temperature → videoGen lighting bias
    "color_temperature": {
        "cool": "cool_blue_undertones",
        "neutral": "natural_shadows",
        "warm": "warm_amber",
        "mixed": "natural_shadows",
    },
    # OpenMontage narrative_role → videoGen beat (best-effort mapping)
    "narrative_role": {
        "establish_context": "opening_hook",
        "introduce_subject": "outside_version",
        "build_tension": "first_fracture",
        "deliver_payload": "irreversible_moment",
        "transition": "defensive_retreat",
        "emotional_beat": "internal_collapse",
        "evidence": "outside_version",
        "comparison": "contrast_memory",
        "resolution": "final_truth",
        "call_to_action": "final_truth",
    },
}


# videoGen-specific fields that OpenMontage doesn't have.
# The adapter fills these with sensible defaults for psychological cinema.
VIDEOGEN_DEFAULTS: dict[str, Any] = {
    "style_anchor": "cinematic photorealism, 35mm film grain, photorealistic, cinematic still, cinematic film still, shallow depth of field",
    "territory": "emotional_withdrawal",
    "archetype": "slow_withdrawal",
    "emotional_state": "restrained",
    "soundtrack_zone": "act_2",
    "music_volume": 0.25,
    "ambient_sfx_profile": "internal_collapse",
    "ambient_volume": 0.30,
    "narration_prosody_register": "default",
    "vocal_fracture": False,
    "breath_pre_pad_ms": 0,
    "subtitle_phrase_pacing": True,
    "subtitle_max_words_per_caption": 6,
}


class OpenMontageAdapter:
    """Translates OpenMontage scene_plan format ↔ videoGen SceneIntent.

    Two methods:
    - ``to_scene_intent(om_scene)`` — OpenMontage scene → videoGen SceneIntent
    - ``from_scene_intent(intent)`` — videoGen SceneIntent → OpenMontage scene

    The first direction is used when OpenMontage is the orchestrator and
    videoGen is the render backend. The second is used when videoGen wants
    to hand off to OpenMontage's Remotion composer for final assembly.
    """

    def __init__(
        self,
        territory: str = "emotional_withdrawal",
        archetype: str = "slow_withdrawal",
        output_dir: str | Path = "output/videos",
        character_references: dict[str, Path] | None = None,
        character_anchors: dict[str, list[str]] | None = None,
    ):
        """Initialize the adapter with territory-specific defaults.

        Args:
            territory: The videoGen territory (e.g. emotional_withdrawal)
            archetype: The videoGen archetype (e.g. slow_withdrawal)
            output_dir: Where rendered assets should be written
            character_references: Map of character_key → hero image path
            character_anchors: Map of character_key → list of anchor strings
        """
        self.territory = territory
        self.archetype = archetype
        self.output_dir = Path(output_dir)
        self.character_references = character_references or {}
        self.character_anchors = character_anchors or {}

    def to_scene_intent(
        self,
        om_scene: dict,
        index: int = 0,
        pipeline_id: str = "vid01",
    ) -> SceneIntent:
        """Translate an OpenMontage scene to a videoGen SceneIntent.

        Args:
            om_scene: A scene dict conforming to OpenMontage's scene_plan.schema.json
            index: The 1-11 position in the videoGen 3-act grid (if known)
            pipeline_id: The pipeline ID for output path construction

        Returns:
            A SceneIntent ready to be rendered by any videoGen RenderBackend

        The translation maps:
        - om_scene["id"] → scene_id
        - om_scene["description"] → scene_description (in raw_scene)
        - om_scene["shot_language"] → camera_language
        - om_scene["narrative_role"] → beat (best-effort)
        - om_scene["hero_moment"] → irreversible_moment (if True)
        - om_scene["character_actions"] → micro_behaviors + emotional_state
        - om_scene["texture_keywords"] → environmental_imperfections
        - om_scene["required_assets"] → render_hints

        Fields that OpenMontage doesn't have get videoGen defaults
        (territory, archetype, style_anchor, soundtrack_zone, etc.).
        """
        om_id = om_scene.get("id", f"scene-{index:03d}")
        om_desc = om_scene.get("description", "")
        om_shot = om_scene.get("shot_language", {}) or {}
        om_narrative_role = om_scene.get("narrative_role", "")
        om_hero_moment = om_scene.get("hero_moment", False)
        om_character_actions = om_scene.get("character_actions", []) or []
        om_texture_keywords = om_scene.get("texture_keywords", []) or []
        om_start = om_scene.get("start_seconds", 0.0)
        om_end = om_scene.get("end_seconds", 5.0)
        om_required_assets = om_scene.get("required_assets", []) or []

        # Translate shot_language
        camera_language = {
            "shot_size": self._translate("shot_size", om_shot.get("shot_size", "medium")),
            "movement": self._translate("camera_movement", om_shot.get("camera_movement", "static")),
            "lighting_key": self._translate("lighting_key", om_shot.get("lighting_key", "low_key")),
            "depth_of_field": self._translate("depth_of_field", om_shot.get("depth_of_field", "shallow")),
            "lens_mm": om_shot.get("lens_mm", 50),
        }
        # Color temperature → bias (not a separate field in SceneIntent, used in style)
        color_temp = om_shot.get("color_temperature", "cool")

        # Translate narrative_role → beat
        beat = self._translate("narrative_role", om_narrative_role, default="internal_collapse")

        # Translate character_actions → emotional_state + micro_behaviors
        emotional_state = "restrained"
        micro_behaviors: list[str] = []
        characters_present: list[str] = []
        for action in om_character_actions:
            char_id = action.get("character_id", "")
            if char_id and char_id not in characters_present:
                characters_present.append(char_id)
            emotion = action.get("emotion", "").lower()
            if emotion:
                emotional_state = self._translate_emotion(emotion)
            action_seq = action.get("action_sequence", [])
            for act in action_seq:
                behavior = self._translate_action_to_behavior(act)
                if behavior and behavior not in micro_behaviors:
                    micro_behaviors.append(behavior)

        # hero_moment → irreversible_moment
        irreversible_moment = bool(om_hero_moment)

        # texture_keywords → environmental_imperfections
        environmental_imperfections = [
            kw for kw in om_texture_keywords
            if kw not in ("grain", "clean", "anamorphic")  # these are style, not imperfection
        ]

        # Determine act from index
        if index <= 4:
            act = "act_1_observation"
        elif index <= 8:
            act = "act_2_inner_reality"
        else:
            act = "act_3_psychological_truth"

        # Determine phase from beat
        phase_map = {
            "opening_hook": "hook",
            "contrast_memory": "warmth",
            "outside_version": "normalcy",
            "first_fracture": "crack",
            "internal_collapse": "collapse",
            "irreversible_moment": "almost",
            "defensive_retreat": "retreat",
            "her_truth": "duality",
            "final_truth": "climax",
        }
        phase = phase_map.get(beat, "collapse")

        # Energy from index (matches canonical_video_spec pacing_curve)
        energy_curve = [3, 7, 7, 4, 3, 2, 2, 5, 2, 3, 1]
        energy = energy_curve[index - 1] if 1 <= index <= 11 else 5

        # Determine soundtrack zone from act
        soundtrack_zone = {
            "act_1_observation": "act_1",
            "act_2_inner_reality": "act_2",
            "act_3_psychological_truth": "act_3",
        }.get(act, "act_2")

        # Music volume by zone
        music_volume = {"act_1": 0.35, "act_2": 0.25, "act_3": 0.15}.get(soundtrack_zone, 0.25)

        # If irreversible_moment, override soundtrack
        if irreversible_moment:
            soundtrack_zone = "silent"
            music_volume = 0.0

        # Duration
        duration = max(3.0, om_end - om_start)

        # Output path
        output_path = self.output_dir / pipeline_id / "scene_images" / f"scene_{index:03d}.png"

        # Character references and anchors
        char_refs: list[Path] = []
        char_anchors: list[str] = []
        for char_key in characters_present:
            if char_key in self.character_references:
                char_refs.append(self.character_references[char_key])
            if char_key in self.character_anchors:
                char_anchors.extend(self.character_anchors[char_key])

        # Prosody register based on act + energy
        prosody_register = "default"
        if irreversible_moment:
            prosody_register = "irreversible_moment"
        elif act == "act_3_psychological_truth":
            prosody_register = "fractured" if energy > 1 else "emotionally_exhausted"
        elif act == "act_2_inner_reality" and energy <= 3:
            prosody_register = "vulnerable"

        # Build the SceneIntent
        intent = SceneIntent(
            scene_id=f"{pipeline_id}-{om_id}",
            title=om_scene.get("description", "")[:60],
            emotional_state=emotional_state,
            emotional_subtext=om_scene.get("information_role", ""),
            visual_symbolism=self._extract_symbols(om_desc, om_texture_keywords),
            what_is_NOT_shown="",
            camera_language=camera_language,
            soundtrack_zone=soundtrack_zone,
            music_volume=music_volume,
            ambient_sfx_profile=beat if beat in (
                "opening_hook", "contrast_memory", "outside_version",
                "first_fracture", "internal_collapse", "irreversible_moment",
                "defensive_retreat", "her_truth", "final_truth",
            ) else "internal_collapse",
            ambient_volume=0.42 if irreversible_moment else 0.30,
            silence_after_seconds=3.0 if irreversible_moment else 0.0,
            silence_instead=False,
            narration_text="",
            narration_prosody_register=prosody_register,
            vocal_fracture=irreversible_moment,
            breath_pre_pad_ms=400 if irreversible_moment else 0,
            character_references=char_refs,
            character_anchors=char_anchors,
            characters_present=characters_present,
            style_anchor=VIDEOGEN_DEFAULTS["style_anchor"],
            negative_prompts=[],
            micro_behaviors=micro_behaviors or ["unfinished_movements"],
            environmental_imperfections=environmental_imperfections or ["kitchen_mess", "fabric_wear"],
            resolution=(1024, 576),
            output_path=output_path,
            in_transition=om_scene.get("transition_in", "cut"),
            out_transition=om_scene.get("transition_out", "cut"),
            irreversible_moment=irreversible_moment,
            pre_moment=False,
            post_moment=False,
            shows_duality=(beat == "her_truth"),
            duration_seconds=duration,
            beat=beat,
            act=act,
            phase=phase,
            energy=energy,
            archetype=self.archetype,
            territory=self.territory,
            index=index,
            raw_scene={
                "scene_description": om_desc,
                "visual_cause_of_emotion": "",
                "ken_burns_effect": camera_language.get("movement", "static"),
            },
        )

        # Also look for required_assets with source="generate" — those are image generation requests
        for asset_req in om_required_assets:
            if asset_req.get("source") == "generate" and asset_req.get("type") == "image":
                # The description from required_assets is often more specific than scene description
                intent.raw_scene["scene_description"] = asset_req.get("description", om_desc)
                break

        logger.debug(
            "OM→SceneIntent: scene %s → %s (beat=%s, energy=%d, irreversible=%s)",
            om_id, intent.scene_id, beat, energy, irreversible_moment,
        )
        return intent

    def from_scene_intent(self, intent: SceneIntent) -> dict:
        """Translate a videoGen SceneIntent to an OpenMontage scene dict.

        Used when videoGen wants to hand off to OpenMontage's Remotion
        composer for final assembly (e.g. for subtitle choreography,
        dynamic motion, or component-based rendering).

        Returns a dict conforming to OpenMontage's scene_plan.schema.json.
        """
        # Reverse translation tables
        reverse_shot_size = {v: k for k, v in OM_TO_VIDEOGEN_TRANSLATIONS["shot_size"].items()}
        reverse_movement = {v: k for k, v in OM_TO_VIDEOGEN_TRANSLATIONS["camera_movement"].items()}
        reverse_lighting = {v: k for k, v in OM_TO_VIDEOGEN_TRANSLATIONS["lighting_key"].items()}
        reverse_dof = {v: k for k, v in OM_TO_VIDEOGEN_TRANSLATIONS["depth_of_field"].items()}

        cam = intent.camera_language or {}
        om_scene = {
            "id": intent.scene_id,
            "type": "generated",
            "description": intent.raw_scene.get("scene_description", ""),
            "start_seconds": 0.0,
            "end_seconds": intent.duration_seconds,
            "shot_language": {
                "shot_size": reverse_shot_size.get(cam.get("shot_size", "medium"), "medium"),
                "camera_movement": reverse_movement.get(cam.get("movement", "static"), "static"),
                "lens_mm": cam.get("lens_mm", 50),
                "lighting_key": reverse_lighting.get(cam.get("lighting_key", "low_key"), "low_key"),
                "depth_of_field": reverse_dof.get(cam.get("depth_of_field", "shallow"), "shallow"),
                "color_temperature": "cool",
            },
            "shot_intent": intent.emotional_subtext or intent.emotional_state,
            "narrative_role": "emotional_beat",
            "hero_moment": intent.irreversible_moment,
            "texture_keywords": intent.environmental_imperfections + ["grain"],
            "required_assets": [
                {
                    "type": "image",
                    "description": intent.raw_scene.get("scene_description", ""),
                    "source": "generate",
                }
            ],
            "framing": cam.get("framing", "rule_of_thirds"),
            "movement": cam.get("movement", "static"),
        }
        return om_scene

    def to_asset_manifest(
        self,
        assets: list,
        total_cost: float = 0.0,
    ) -> dict:
        """Build an OpenMontage asset_manifest from rendered SceneAssets.

        Args:
            assets: List of SceneAsset dataclasses
            total_cost: Total cost in USD

        Returns a dict conforming to OpenMontage's asset_manifest.schema.json.
        """
        om_assets = []
        for a in assets:
            om_assets.append({
                "id": a.scene_id,
                "type": "image",
                "path": str(a.image_path),
                "source_tool": a.backend,
                "scene_id": a.scene_id,
                "model": a.metadata.get("model", ""),
                "seed": a.metadata.get("seed", 0),
                "cost_usd": a.cost_usd,
                "duration_seconds": a.duration_seconds,
                "resolution": f"{a.metadata.get('resolution', '1024x576')}",
                "quality_score": a.metadata.get("clip_score", 0.0),
                "generation_summary": f"Rendered by {a.backend}",
            })
        return {
            "version": "1.0",
            "assets": om_assets,
            "total_cost_usd": total_cost,
            "metadata": {
                "renderer": "videogen",
                "territory": self.territory,
                "archetype": self.archetype,
            },
        }

    # ---------- PRIVATE HELPERS ----------

    def _translate(
        self,
        category: str,
        om_value: str,
        default: str = "",
    ) -> str:
        """Translate an OpenMontage vocabulary value to videoGen vocabulary."""
        table = OM_TO_VIDEOGEN_TRANSLATIONS.get(category, {})
        return table.get(om_value, default or om_value)

    def _translate_emotion(self, om_emotion: str) -> str:
        """Translate an OpenMontage emotion string to a videoGen emotional_state."""
        emotion_map = {
            "sad": "grief",
            "lonely": "yearning",
            "afraid": "defensive",
            "tired": "exhausted",
            "angry": "defensive",
            "happy": "warmth",
            "neutral": "restrained",
            "tense": "restrained",
            "vulnerable": "wounded",
            "ashamed": "shame",
            "guilty": "shame",
            "resigned": "resigned",
            "numb": "numb",
            "hopeful": "yearning",
        }
        return emotion_map.get(om_emotion.lower(), "restrained")

    def _translate_action_to_behavior(self, action: str) -> str | None:
        """Translate an OpenMontage action_sequence string to a videoGen micro_behavior."""
        action_lower = action.lower()
        if "reach" in action_lower and ("stop" in action_lower or "withdraw" in action_lower or "pull" in action_lower):
            return "unfinished_movements"
        if "hesitat" in action_lower or "pause" in action_lower:
            return "hesitation"
        if "look away" in action_lower or "looks away" in action_lower or "look down" in action_lower or "looks down" in action_lower or "avoid" in action_lower:
            return "redirected_attention"
        if "almost" in action_lower and ("touch" in action_lower or "contact" in action_lower):
            return "almost_touching"
        if "almost" in action_lower and ("speak" in action_lower or "say" in action_lower):
            return "almost_speaking"
        if ("open" in action_lower or "opens" in action_lower) and "mouth" in action_lower and ("speak" in action_lower or "say" in action_lower or "close" in action_lower):
            return "almost_speaking"
        if "withdraw" in action_lower or "retreat" in action_lower or "fold" in action_lower:
            return "emotional_withdrawal"
        return None

    def _extract_symbols(self, description: str, texture_keywords: list[str]) -> list[str]:
        """Extract visual_symbolism tokens from an OpenMontage description.

        This is a best-effort heuristic. The description is free text, so
        we look for known symbolic phrases.
        """
        symbols: list[str] = []
        desc_lower = description.lower()
        if "not touching" in desc_lower or "gap between" in desc_lower or "distance" in desc_lower:
            symbols.append("physical_distance")
        if "low light" in desc_lower or "dark" in desc_lower or "shadow" in desc_lower or "night" in desc_lower:
            symbols.append("low_light")
        if "look down" in desc_lower or "looking at hands" in desc_lower or "not meeting eyes" in desc_lower:
            symbols.append("downward_eye_contact")
        if "almost" in desc_lower and ("reach" in desc_lower or "touch" in desc_lower):
            symbols.append("unfinished_gesture")
        if "wrinkled" in desc_lower or "unwashed" in desc_lower or "messy" in desc_lower or "dust" in desc_lower:
            symbols.append("imperfection")
        if "midnight" in desc_lower or "can't sleep" in desc_lower or "sitting up" in desc_lower:
            symbols.append("nighttime_honesty")
        if "door" in desc_lower and ("not quite" in desc_lower or "cracked" in desc_lower or "ajar" in desc_lower):
            symbols.append("transition_object")
        # Add texture keywords as symbols
        for kw in texture_keywords:
            if kw not in ("grain", "clean", "anamorphic"):
                symbols.append(kw)
        return symbols or ["physical_distance", "low_light"]