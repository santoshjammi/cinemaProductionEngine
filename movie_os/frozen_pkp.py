"""Frozen Production Knowledge Package boundary for canonical runtime.

This is the runtime-authoritative PKP representation used between GENESIS and
PROMETHEUS. It is derived from the docs PKP schema and validated for the fields
the current runtime actually requires.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator


def _canon(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(data: Any) -> str:
    return hashlib.sha256(_canon(data).encode("utf-8")).hexdigest()


class FrozenPKP(BaseModel):
    pkp_id: str
    version: str
    episode_id: str
    policy_snapshot_id: str
    status: str = "FROZEN"
    created_at: str
    frozen_at: str
    content_hash: str

    canonical_bible_bindings: dict[str, Any] = Field(default_factory=dict)
    canonical_registry_bindings: dict[str, Any] = Field(default_factory=dict)

    episode_contract_id: str
    episode_contract_version: str = "1.0"
    episode_contract_hash: str
    policy_snapshot_hash: str

    continuity: dict[str, Any] = Field(default_factory=dict)
    characters: dict[str, Any] = Field(default_factory=dict)
    story: dict[str, Any] = Field(default_factory=dict)
    screenplay: dict[str, Any] = Field(default_factory=dict)
    dialogue: dict[str, Any] = Field(default_factory=dict)
    scene_states: dict[str, Any] = Field(default_factory=dict)
    visual_bible: dict[str, Any] = Field(default_factory=dict)
    shots: dict[str, Any] = Field(default_factory=dict)
    voices: dict[str, Any] = Field(default_factory=dict)
    sound: dict[str, Any] = Field(default_factory=dict)
    assets: dict[str, Any] = Field(default_factory=dict)
    execution_constraints: dict[str, Any] = Field(default_factory=dict)
    validation_requirements: dict[str, Any] = Field(default_factory=dict)
    production: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _immutable(self):
        object.__setattr__(self, "status", self.status)
        return self

    def compute_content_hash(self) -> str:
        return _hash(self.model_dump(exclude={"content_hash"}))

    def freeze(self) -> "FrozenPKP":
        data = self.model_dump()
        data["status"] = "FROZEN"
        data["frozen_at"] = datetime.now(timezone.utc).isoformat()
        data["content_hash"] = _hash({k: v for k, v in data.items() if k != "content_hash"})
        return FrozenPKP.model_validate(data)

    def mutate(self, **changes: Any) -> "FrozenPKP":
        if self.status == "FROZEN":
            raise ValueError("Frozen PKP is immutable; create a new version instead")
        data = self.model_dump()
        data.update(changes)
        return FrozenPKP.model_validate(data)


def validate_frozen_pkp(
    data: dict[str, Any],
    *,
    expected_episode_id: str | None = None,
    expected_policy_snapshot_id: str | None = None,
) -> FrozenPKP:
    pkp = FrozenPKP.model_validate(data)
    if pkp.status != "FROZEN":
        raise ValueError("frozen PKP required")
    if expected_episode_id and pkp.episode_id != expected_episode_id:
        raise ValueError("PKP episode mismatch")
    if expected_policy_snapshot_id and pkp.policy_snapshot_id != expected_policy_snapshot_id:
        raise ValueError("PKP policy_snapshot_id mismatch")
    if pkp.content_hash != pkp.compute_content_hash():
        raise ValueError("PKP content hash mismatch")
    canonical_bible = pkp.canonical_bible_bindings or {}
    registry_bindings = pkp.canonical_registry_bindings or {}
    required_bindings = {"Mark", "Sarah"}
    if set(canonical_bible.keys()) != required_bindings:
        raise ValueError("canonical bible bindings required for Mark and Sarah")
    for name in required_bindings:
        entry = canonical_bible.get(name) or {}
        if not entry.get("character_bible_ref"):
            raise ValueError(f"missing character bible ref for {name}")
        if not entry.get("visual_identity_registry_ref"):
            raise ValueError(f"missing visual identity registry ref for {name}")
        if not entry.get("voice_registry_ref"):
            raise ValueError(f"missing voice registry ref for {name}")
        if not entry.get("continuity_registry_ref"):
            raise ValueError(f"missing continuity registry ref for {name}")
    if registry_bindings.get("character_bible_refs") != [canonical_bible["Mark"]["character_bible_ref"], canonical_bible["Sarah"]["character_bible_ref"]]:
        raise ValueError("canonical registry bindings must preserve bible order")
    if registry_bindings.get("visual_identity_registry_refs") != [canonical_bible["Mark"]["visual_identity_registry_ref"], canonical_bible["Sarah"]["visual_identity_registry_ref"]]:
        raise ValueError("canonical registry bindings must preserve visual order")
    if registry_bindings.get("voice_registry_refs") != [canonical_bible["Mark"]["voice_registry_ref"], canonical_bible["Sarah"]["voice_registry_ref"]]:
        raise ValueError("canonical registry bindings must preserve voice order")
    if registry_bindings.get("continuity_registry_ref") != canonical_bible["Mark"]["continuity_registry_ref"]:
        raise ValueError("canonical continuity registry binding mismatch")
    return pkp


def build_frozen_pkp(
    *,
    episode_id: str,
    policy_snapshot_id: str,
    episode_contract_id: str,
    episode_contract_hash: str,
    policy_snapshot_hash: str,
    production: dict[str, Any],
    story: dict[str, Any],
    continuity: dict[str, Any],
    characters: dict[str, Any],
    screenplay: dict[str, Any],
    dialogue: dict[str, Any],
    scene_states: dict[str, Any],
    visual_bible: dict[str, Any],
    shots: dict[str, Any],
    voices: dict[str, Any],
    sound: dict[str, Any],
    assets: dict[str, Any],
    execution_constraints: dict[str, Any],
    validation_requirements: dict[str, Any],
    canonical_bible_bindings: dict[str, Any],
    canonical_registry_bindings: dict[str, Any],
) -> FrozenPKP:
    base = {
        "pkp_id": f"PKP-{episode_id}-v1",
        "version": "1",
        "episode_id": episode_id,
        "policy_snapshot_id": policy_snapshot_id,
        "status": "FROZEN",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "episode_contract_id": episode_contract_id,
        "episode_contract_hash": episode_contract_hash,
        "policy_snapshot_hash": policy_snapshot_hash,
        "continuity": continuity,
        "characters": characters,
        "story": story,
        "screenplay": screenplay,
        "dialogue": dialogue,
        "scene_states": scene_states,
        "visual_bible": visual_bible,
        "shots": shots,
        "voices": voices,
        "sound": sound,
        "assets": assets,
        "execution_constraints": execution_constraints,
        "validation_requirements": validation_requirements,
        "production": production,
        "canonical_bible_bindings": canonical_bible_bindings,
        "canonical_registry_bindings": canonical_registry_bindings,
    }
    base["content_hash"] = ""
    pkp = FrozenPKP.model_validate(base)
    content_hash = _hash({k: v for k, v in pkp.model_dump().items() if k != "content_hash"})
    return pkp.model_copy(update={"content_hash": content_hash})


def freeze_from_brief(
    *,
    episode_id: str,
    policy_snapshot_id: str,
    episode_contract_id: str,
    episode_contract_hash: str,
    policy_snapshot_hash: str,
    production: dict[str, Any],
    brief: dict[str, Any],
) -> FrozenPKP:
    scenes = brief.get("scenes") or []
    dialogues = brief.get("dialogues") or []
    if not scenes:
        raise ValueError("Cannot freeze PKP; brief lacks required scenes")
    if not dialogues:
        raise ValueError("Cannot freeze PKP; brief lacks required dialogue scenes")

    def _canon_slug(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")

    def _canon_voice_ref(name: str) -> str:
        slug = _canon_slug(name)
        if slug == "mark":
            return "assets/canon/mark/voice_reference/mark_brian_reference.mp3"
        if slug == "sarah":
            return "assets/canon/sarah/voice_reference/sarah_ava_reference.mp3"
        return f"assets/canon/{slug}/voice_reference"

    def _canon_visual_ref(name: str) -> str:
        slug = _canon_slug(name)
        return f"assets/canon/{slug}/visual_reference"

    character_names: list[str] = []
    for c in brief.get("characters", []) or []:
        if isinstance(c, dict):
            name = c.get("name") or c.get("id")
        else:
            name = str(c)
        if name:
            character_names.append(str(name))
    for scene in scenes:
        for nm in scene.get("characters_present", []) or []:
            if nm and nm not in character_names:
                character_names.append(str(nm))
    for d in dialogues:
        for line in d.get("lines", []) or []:
            speaker = line.get("speaker") if isinstance(line, dict) else None
            if speaker and speaker not in character_names:
                character_names.append(str(speaker))
    if not character_names:
        character_names = ["MARK", "SARAH"]
    visual_refs = []
    voice_refs = []
    for name in character_names:
        visual_ref = _canon_visual_ref(name)
        if visual_ref not in visual_refs:
            visual_refs.append(visual_ref)
        voice_ref = _canon_voice_ref(name)
        if voice_ref not in voice_refs:
            voice_refs.append(voice_ref)

    screenplay_scenes = []
    scene_states = []
    shots = []
    lines = []
    for scene in scenes:
        scene_id = scene.get("number") or scene.get("scene_number") or scene.get("id")
        title = str(scene.get("title") or f"Scene {scene_id}")
        beat = str(scene.get("narrative_beat") or scene.get("act") or "scene").strip() or "scene"
        entry_state = scene.get("entry_state") or f"{title}: establishes the starting emotional state"
        turning_point = scene.get("turning_point") or f"{title}: the {beat} shifts the relationship"
        exit_state = scene.get("exit_state") or f"{title}: leaves the characters changed for the next scene"
        next_scene_cause = scene.get("next_scene_cause")
        emotional_progression = scene.get("emotional_progression") or ["steady", "uneasy", "changed"]
        scene_dialogue = next((d for d in dialogues if d.get("scene_number") == scene_id), None)
        if not scene_dialogue:
            raise ValueError(f"Cannot freeze PKP; missing dialogue for scene {scene_id}")
        scene_lines = []
        line_emotions = []
        for idx, line in enumerate(scene_dialogue.get("lines", [])):
            if not line.get("text"):
                raise ValueError(f"Cannot freeze PKP; missing dialogue text in scene {scene_id}")
            emotion = line.get("emotion") or line.get("delivery_intent") or "neutral"
            line_id = f"{scene_id}-{idx + 1}"
            scene_lines.append({
                "line_id": line_id,
                "speaker": line.get("speaker"),
                "text": line.get("text"),
                "delivery_intent": emotion,
            })
            line_emotions.append(emotion)
            lines.append(scene_lines[-1])
            shots.append({
                "shot_id": f"{scene_id}-{idx + 1}",
                "scene_id": scene_id,
                "function": "speaker coverage" if idx == 0 else "reaction",
                "duration": line.get("duration", 4),
                "framing": line.get("framing", "medium"),
                "speaker": line.get("speaker"),
                "lip_sync_required": True,
                "continuity": scene.get("continuity", "maintain identity"),
                "performance_intent": emotion,
                "visual_intent": scene.get("visual_intent") or brief.get("visual_intent") or "cinematic dialogue",
                "audio_intent": emotion,
            })
        screenplay_scenes.append({
            "scene_id": scene_id,
            "narrative_function": scene.get("narrative_beat") or scene.get("title") or "scene",
            "entry_state": entry_state,
            "turning_point": turning_point,
            "exit_state": exit_state,
            "next_scene_cause": next_scene_cause or "causal bridge",
            "emotional_progression": emotional_progression,
            "dialogue_causality": {
                "cause": entry_state,
                "turning_point": turning_point,
                "effect": exit_state,
                "next_scene_cause": next_scene_cause or "causal bridge",
            },
            "dialogue": scene_lines,
        })
        scene_states.append({
            "scene_id": scene_id,
            "entry": entry_state,
            "turning_point": turning_point,
            "exit": exit_state,
            "next_scene_cause": next_scene_cause or "causal bridge",
            "emotional_progression": emotional_progression,
            "dialogue_emotions": line_emotions,
        })

    context = brief.get("context", {}) if isinstance(brief.get("context", {}), dict) else {}
    context_characters = context.get("characters", []) if isinstance(context, dict) else []
    if not brief.get("characters") and context_characters:
        brief["characters"] = [c.get("name") for c in context_characters if isinstance(c, dict) and c.get("name")]

    def _resolve_character_refs(name: str) -> dict[str, Any]:
        key = str(name).strip().upper()
        if key == "MARK":
            return {
                "character_id": "MARK",
                "display_name": "Mark",
                "approved_identity": "white American software engineer, co-lead, 40",
                "visual_reference_ids": ["MSVI-MARK"],
                "voice_reference_ids": ["MSVR-MARK"],
            }
        if key == "SARAH":
            return {
                "character_id": "SARAH",
                "display_name": "Sarah",
                "approved_identity": "white American business operations professional, co-lead, 36",
                "visual_reference_ids": ["MSVI-SARAH"],
                "voice_reference_ids": ["MSVR-SARAH"],
            }
        return {
            "character_id": key,
            "display_name": str(name),
            "approved_identity": "",
            "visual_reference_ids": [],
            "voice_reference_ids": [],
        }

    canonical_chars = [_resolve_character_refs(c) for c in (brief.get("characters", []) or [])]
    visual_reference_ids = []
    voice_reference_ids = []
    for c in canonical_chars:
        visual_reference_ids.extend(c.get("visual_reference_ids", []))
        voice_reference_ids.extend(c.get("voice_reference_ids", []))

    canonical_bible_bindings = {
        "Mark": {
            "character_bible_ref": "docs/10_psychology/10_mark_sarah/01_MARK_CHARACTER_BIBLE.md",
            "visual_identity_registry_ref": "movie_os/data/characters/MARK/character.yaml",
            "voice_registry_ref": "movie_os/data/voices/MARK/voice.yaml",
            "continuity_registry_ref": "movie_os/data/continuity/mark_sarah_continuity.yaml",
        },
        "Sarah": {
            "character_bible_ref": "docs/10_psychology/10_mark_sarah/01_SARAH_CHARACTER_BIBLE.md",
            "visual_identity_registry_ref": "movie_os/data/characters/SARAH/character.yaml",
            "voice_registry_ref": "movie_os/data/voices/SARAH/voice.yaml",
            "continuity_registry_ref": "movie_os/data/continuity/mark_sarah_continuity.yaml",
        },
    }
    canonical_registry_bindings = {
        "character_bible_refs": [canonical_bible_bindings["Mark"]["character_bible_ref"], canonical_bible_bindings["Sarah"]["character_bible_ref"]],
        "visual_identity_registry_refs": [canonical_bible_bindings["Mark"]["visual_identity_registry_ref"], canonical_bible_bindings["Sarah"]["visual_identity_registry_ref"]],
        "voice_registry_refs": [canonical_bible_bindings["Mark"]["voice_registry_ref"], canonical_bible_bindings["Sarah"]["voice_registry_ref"]],
        "continuity_registry_ref": canonical_bible_bindings["Mark"]["continuity_registry_ref"],
    }

    return build_frozen_pkp(
        episode_id=episode_id,
        policy_snapshot_id=policy_snapshot_id,
        episode_contract_id=episode_contract_id,
        episode_contract_hash=episode_contract_hash,
        policy_snapshot_hash=policy_snapshot_hash,
        production=production,
        story={
            "logline": brief.get("logline", ""),
            "synopsis": brief.get("synopsis", ""),
            "beat_graph": brief.get("scenes", []),
            "ending": brief.get("ending", ""),
            "primary_mechanism": brief.get("primary_mechanism", "fear-based withdrawal"),
            "intended_resolution": brief.get("intended_resolution", "meaningful progress"),
        },
        continuity={
            "universe_id": brief.get("universe_id", "MARK_SARAH"),
            "continuity_version": brief.get("continuity_version", "1"),
            "relevant_prior_events": brief.get("continuity", []),
        },
        characters={"character_ids": canonical_chars, "visual_reference_ids": visual_reference_ids, "voice_reference_ids": voice_reference_ids},
        screenplay={"scenes": screenplay_scenes, "exact_dialogue_text": [l["text"] for l in lines]},
        dialogue={"line_ids": [l["line_id"] for l in lines], "intent": [l["delivery_intent"] for l in lines], "subtext": [], "delivery": [], "consequence": []},
        scene_states={"scenes": scene_states},
        visual_bible={"style": brief.get("style", "cinematic"), "locations": [], "wardrobe": [], "lighting": [], "identity_controls": canonical_chars},
        shots={"shots": shots},
        voices={"voice_ids": voice_reference_ids, "line_directions": [], "pronunciation": []},
        sound={"ambience": [], "music_intent": brief.get("music_intent", ""), "silence_strategy": []},
        assets={"required_references": visual_reference_ids + voice_reference_ids, "reusable_assets": []},
        execution_constraints={"allowed_fallbacks": [], "forbidden_substitutions": ["dialogue rewrite", "narration insertion"]},
        validation_requirements={"standards": brief.get("standards", []), "blocking_gates": ["frozen_pkp", "dialogue_immutable"]},
        canonical_bible_bindings=canonical_bible_bindings,
        canonical_registry_bindings=canonical_registry_bindings,
    )
