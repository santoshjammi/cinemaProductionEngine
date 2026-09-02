"""Genesis2 — Creative Intelligence Engine data models.

Every phase produces structured knowledge objects. Every object contains:
purpose, creative_intent, reasoning, confidence, dependencies, validation, metadata.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
import re
from typing import Any, Optional

from pydantic import BaseModel, Field, SerializeAsAny, model_validator


# ---------------------------------------------------------------------------
# Core primitives
# ---------------------------------------------------------------------------

class ConfidenceLevel(str, Enum):
    EXPLICIT = "explicit"
    INFERRED = "inferred"
    CONFIRMED = "confirmed"
    ASSUMED = "assumed"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value):
        """Handle non-standard confidence values like 'High', '0.8', etc."""
        if isinstance(value, str):
            v = value.lower().strip()
            if v in ("high", "explicit", "certain", "definite"):
                return cls.EXPLICIT
            if v in ("medium", "inferred", "likely"):
                return cls.INFERRED
            if v in ("confirmed", "verified", "validated"):
                return cls.CONFIRMED
            if v in ("low", "assumed", "possible"):
                return cls.ASSUMED
        if isinstance(value, (int, float)):
            if value >= 0.8:
                return cls.EXPLICIT
            if value >= 0.6:
                return cls.INFERRED
            if value >= 0.4:
                return cls.ASSUMED
        return cls.UNKNOWN


class PhaseStatus(str, Enum):
    PENDING = "pending"
    DRAFTING = "drafting"
    REVIEWING = "reviewing"
    CRITIQUING = "critiquing"
    IMPROVING = "improving"
    VALIDATING = "validating"
    FREEZING = "freezing"
    COMPLETED = "completed"
    FAILED = "failed"


def _coerce_clean_string(value: Any) -> str:
    """Coerce a non-string value to a readable string, stripping Python-internal
    artifacts (raw Enum reprs, ``__objclass__``, memory addresses) that an LLM
    may have embedded.  For dicts, prefer the most meaningful string content."""
    s = str(value)
    # Strip Python-internal / Enum-internal fragments and memory addresses.
    s = re.sub(r"__objclass__[^,}]*", "", s)
    s = re.sub(r"__[a-zA-Z_]+__\s*[:=]?\s*[^,}\]]*", "", s)
    s = re.sub(r"0x[0-9a-fA-F]+", "", s)
    s = re.sub(r"\s{2,}", " ", s)
    s = s.strip(" \t{}'\"")
    return s


class KnowledgeObject(BaseModel):
    """Base for all knowledge objects produced by phases."""
    knowledge_type: str = ""
    purpose: str = ""
    creative_intent: str = ""
    reasoning: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    dependencies: list[str] = Field(default_factory=list)
    validation: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _set_knowledge_type(self) -> "KnowledgeObject":
        """Auto-populate the stable, machine-readable subtype discriminator.

        ``knowledge_type`` is set from the concrete class name so persisted
        knowledge can be reconstructed to the correct subtype on reload without
        brittle field-presence heuristics (P0-03R-SER-01 §8).
        """
        if not self.knowledge_type:
            self.knowledge_type = type(self).__name__
        return self

    @model_validator(mode="before")
    @classmethod
    def _normalize_types(cls, data: Any) -> Any:
        """Normalize LLM output types before Pydantic validation.

        Real LLMs often output ints where strings are expected, dicts where
        strings are expected, etc. This validator normalizes common patterns
        so the strict Pydantic models accept real LLM output.
        """
        if not isinstance(data, dict):
            return data
        # Fields that expect strings but LLMs may return as dicts or ints
        _STRING_FIELDS = {
            "purpose", "creative_intent", "reasoning",
            "theme", "genre", "subgenre", "mood", "core_question",
            "audience", "message", "conflict", "transformation",
            "premise", "setting", "tone", "pacing",
            "act", "sequence",
            "history", "culture", "technology", "environment",
            "architecture", "economy", "politics", "social_structure",
            "identity", "name", "role", "speech_style", "personality",
            "color", "lighting", "composition", "textures", "atmosphere",
            "camera_intent", "lens_suggestions", "movement_philosophy",
            "environmental_storytelling",
            "overall_assessment",
            "internal_conflict", "external_conflict", "weakness", "strength",
            "transformation_arc", "backstory",
            "lens_suggestions",
            "social_structure", "speech_patterns", "voice_direction",
            "dialogue_rhythm", "conversation_intent", "subtext",
            "emotional_state",
        }
        # Fields that expect lists but LLMs may return as strings or dicts
        _LIST_FIELDS = {"goals", "success_criteria", "recommended_actions",
                        "improvement_areas", "visual_motifs", "lighting_scheme",
                        "scenes", "dialogues", "validation", "rules"}
        # Fields that expect list[dict] but LLMs may return as a single dict
        _LIST_DICT_FIELDS = {"timeline", "key_events", "character_specs", "location_specs",
                             "camera_specs", "lighting_specs", "animation_specs",
                             "audio_specs", "music_specs", "editing_specs", "rendering_specs",
                             "cross_references", "version_history"}

        result = dict(data)
        for key, value in data.items():
            if value is None:
                result[key] = value
            elif key in _STRING_FIELDS:
                if isinstance(value, (dict, int, float)):
                    # A dict/int for a string field — coerce to a readable
                    # string, stripping Python-internal artifacts (raw Enum
                    # reprs, __objclass__, memory addresses) that the LLM may
                    # have embedded.
                    result[key] = _coerce_clean_string(value)
                elif isinstance(value, list):
                    # LLM returned a list for a string field — join the string parts
                    parts = []
                    for v in value:
                        if isinstance(v, str):
                            parts.append(v)
                        elif isinstance(v, dict):
                            # extract first string value
                            for vv in v.values():
                                if isinstance(vv, str):
                                    parts.append(vv)
                                    break
                            else:
                                parts.append(str(v))
                        else:
                            parts.append(str(v))
                    result[key] = ", ".join(parts) if parts else ""
            elif key in _LIST_FIELDS:
                if isinstance(value, str):
                    result[key] = [value]
                elif isinstance(value, dict):
                    result[key] = [str(value)]
                elif isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
                    # Skip items that are already structured knowledge objects
                    # (carry a knowledge_type discriminator).  Mangling these to
                    # strings destroys nested-model semantics on reload.
                    if any("knowledge_type" in v for v in value):
                        result[key] = value
                        continue
                    # General dict-to-string normalization: extract first string value
                    result[key] = []
                    for v in value:
                        # Try common keys first
                        for k in ("check", "criterion", "rule", "element", "symbol", "character",
                                   "emotion", "description", "name", "text", "value", "content"):
                            if k in v and isinstance(v[k], str):
                                result[key].append(v[k])
                                break
                        else:
                            # Fallback: take any string value
                            for vv in v.values():
                                if isinstance(vv, str):
                                    result[key].append(vv)
                                    break
                            else:
                                result[key].append(str(v))
            elif key in _LIST_DICT_FIELDS:
                if isinstance(value, dict):
                    if value:
                        result[key] = [value]
                    else:
                        result[key] = []
                elif isinstance(value, list) and value and all(isinstance(v, str) for v in value):
                    # Convert list of strings to list of dicts with a default key
                    result[key] = [{"event": v} for v in value]
            # Normalize lists of {criterion: ...} dicts to list of strings
            elif isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
                if any("criterion" in v for v in value):
                    result[key] = [str(v.get("criterion", str(v))) for v in value]
                # Normalize {check, status} dicts to just the check text
                elif any("check" in v for v in value):
                    result[key] = [str(v.get("check", str(v))) for v in value]
        return result


# ---------------------------------------------------------------------------
# Phase 01: Creative Understanding
# ---------------------------------------------------------------------------

class CreativeUnderstanding(KnowledgeObject):
    theme: str = ""
    genre: str = ""
    subgenre: str = ""
    audience: str = ""
    mood: str = ""
    core_question: str = ""
    message: str = ""
    conflict: str = ""
    transformation: str = ""
    success_criteria: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 02: Story Foundation
# ---------------------------------------------------------------------------

class StoryBeat(KnowledgeObject):
    name: str = ""
    description: str = ""
    position: str = ""  # beginning, middle, end
    emotional_intent: str = ""

    @classmethod
    def _from_llm(cls, data: dict) -> "StoryBeat":
        """Create from LLM output, coercing types."""
        if isinstance(data.get("position"), (int, float)):
            data["position"] = str(data["position"])
        return cls(**data)


class StoryFoundation(KnowledgeObject):
    premise: str = ""
    dramatic_question: str = ""  # the central question the HOOK poses, PLOT deepens, CLIMAX answers
    acts: list[dict[str, Any]] = Field(default_factory=list)
    major_events: list[str] = Field(default_factory=list)
    emotional_journey: list[str] = Field(default_factory=list)
    story_beats: list[StoryBeat] = Field(default_factory=list)
    narrative_rhythm: str = ""
    foreshadowing: list[str] = Field(default_factory=list)
    symbolism: list[str] = Field(default_factory=list)
    motifs: list[str] = Field(default_factory=list)

    @classmethod
    def _from_llm(cls, data: dict) -> "StoryFoundation":
        """Create from LLM output, coercing types."""
        def _to_strings(items: list) -> list[str]:
            result = []
            for item in items:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    # Try common keys like 'element', 'symbol', 'character'
                    for key in ("element", "symbol", "character", "emotion", "description", "name"):
                        if key in item and isinstance(item[key], str):
                            result.append(item[key])
                            break
                    else:
                        result.append(str(item))
                else:
                    result.append(str(item))
            return result

        for field in ("emotional_journey", "foreshadowing", "symbolism", "motifs", "major_events"):
            if field in data and isinstance(data[field], list):
                data[field] = _to_strings(data[field])

        beats = [StoryBeat._from_llm(b) for b in data.pop("story_beats", [])]

        # Coerce acts: if any act is a string, wrap it into a dict
        acts = data.get("acts", [])
        if isinstance(acts, list):
            coerced_acts = []
            for a in acts:
                if isinstance(a, str):
                    coerced_acts.append({"name": a, "description": a, "events": []})
                elif isinstance(a, dict):
                    coerced_acts.append(a)
                else:
                    coerced_acts.append({"name": str(a), "description": str(a), "events": []})
            data["acts"] = coerced_acts

        return cls(**data, story_beats=beats)


# ---------------------------------------------------------------------------
# Phase 03: Character Psychology
# ---------------------------------------------------------------------------

class Character(KnowledgeObject):
    name: str = ""
    role: str = ""  # protagonist, antagonist, supporting
    identity: str = ""
    history: str = ""
    goals: list[str] = Field(default_factory=list)
    fear: str = ""
    need: str = ""
    want: str = ""
    weakness: str = ""
    strength: str = ""
    internal_conflict: str = ""
    external_conflict: str = ""
    speech_style: str = ""
    personality: str = ""
    transformation: str = ""


class CharacterPsychology(KnowledgeObject):
    protagonist: Character = Field(default_factory=Character)
    antagonist: Optional[Character] = None
    supporting_characters: list[Character] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 04: World Development
# ---------------------------------------------------------------------------

class WorldDevelopment(KnowledgeObject):
    history: str = ""
    culture: str = ""
    technology: str = ""
    environment: str = ""
    rules: list[str] = Field(default_factory=list)
    architecture: str = ""
    economy: str = ""
    politics: str = ""
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    social_structure: str = ""


# ---------------------------------------------------------------------------
# Phase 05: Narrative Expansion
# ---------------------------------------------------------------------------

class Scene(KnowledgeObject):
    scene_number: int = 0
    act: str = ""
    sequence: str = ""
    objective: str = ""
    conflict: str = ""
    outcome: str = ""
    emotional_objective: str = ""
    narrative_beat: str = ""  # hook | plot | turning_point | climax — which beat this scene serves


class NarrativeExpansion(KnowledgeObject):
    acts: list[dict[str, Any]] = Field(default_factory=list)
    sequences: list[dict[str, Any]] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 06: Scene Planning
# ---------------------------------------------------------------------------

class ScenePlan(KnowledgeObject):
    scene_number: int = 0
    title: str = ""
    purpose: str = ""
    conflict: str = ""
    emotion: str = ""
    visual_goal: str = ""
    audio_goal: str = ""
    character_goal: str = ""
    transition: str = ""
    duration: str = ""
    dependencies: list[str] = Field(default_factory=list)
    narrative_beat: str = ""  # hook | plot | turning_point | climax — which beat this scene serves


class ScenePlanning(KnowledgeObject):
    scenes: list[ScenePlan] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 07: Dialogue Planning
# ---------------------------------------------------------------------------

class DialogueLine(BaseModel):
    """A single spoken (or inner-voice) line of dialogue.

    speaker: character name (e.g. 'MARK', 'SARAH', or 'MARK_INNER' for the
             suffering character's whispering inner voice).
    text: the line as spoken.
    delivery_intent: performance direction for how the line should be spoken.
    emotion: emotional tag used for TTS prosody (e.g. 'whisper', 'quiet').
    line_id: deterministic identity assigned after generation.

    P0-04: the canonical line performance contract.  Only the mandatory fields
    are modeled as required; the rest are optional and populated when authored
    or semantically enriched.  Existing authored performance must be preserved,
    never regenerated.  ``voice_identity`` separates the stable character voice
    id from the per-line acting state.
    """
    line_id: str = ""
    speaker: str = ""
    text: str = ""
    delivery_intent: str = ""
    emotion: str = "neutral"

    # --- Canonical performance contract (P0-04) ---
    # Objective / narrative function
    objective: str = ""
    narrative_function: str = ""
    # Emotional state (normalized primary + optional secondary)
    emotional_state_primary: str = ""
    emotional_state_secondary: str = ""
    # Subtext (actor-actionable, short)
    subtext: str = ""
    # Delivery dimensions (normalized values, empty = not specified)
    pace: str = ""
    volume: str = ""
    energy: str = ""
    tension: str = ""
    warmth: str = ""
    hesitation: str = ""
    certainty: str = ""
    # Emphasis / pauses / interruption / overlap
    emphasis_phrases: list[str] = Field(default_factory=list)
    pause_before_ms: Optional[int] = None
    pause_after_ms: Optional[int] = None
    interruption_type: str = ""
    interruption_target_line_id: str = ""
    overlap_allowed: bool = False
    # Physical performance
    physical_gaze: str = ""
    physical_posture: str = ""
    physical_action: str = ""
    # Listener response expectation
    listener_character_id: str = ""
    listener_reaction_intent: str = ""
    # Voice identity binding
    character_voice_id: str = ""
    presentation_mode: str = "EXTERNAL"  # EXTERNAL | INTERNAL



class DialoguePlan(KnowledgeObject):
    scene_number: int = 0
    conversation_intent: str = ""
    subtext: str = ""
    emotional_state: str = ""
    silence_opportunities: list[str] = Field(default_factory=list)
    dialogue_rhythm: str = ""
    speech_patterns: str = ""
    voice_direction: str = ""
    # Expanded dialogue: 3-4 spoken exchanges per scene, plus an inner voice
    # line for the suffering character so their silence is audible.
    lines: list[DialogueLine] = Field(default_factory=list)
    inner_voice: list[DialogueLine] = Field(default_factory=list)


class DialoguePlanning(KnowledgeObject):
    dialogues: list[DialoguePlan] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 08: Visual Language
# ---------------------------------------------------------------------------

class VisualLanguage(KnowledgeObject):
    color: str = ""
    lighting: str = ""
    composition: str = ""
    textures: str = ""
    atmosphere: str = ""
    camera_intent: str = ""
    lens_suggestions: str = ""
    movement_philosophy: str = ""
    environmental_storytelling: str = ""


# ---------------------------------------------------------------------------
# Phase 09: Production Specifications
# ---------------------------------------------------------------------------

class ProductionSpecifications(KnowledgeObject):
    character_specs: list[dict[str, Any]] = Field(default_factory=list)
    location_specs: list[dict[str, Any]] = Field(default_factory=list)
    camera_specs: list[dict[str, Any]] = Field(default_factory=list)
    lighting_specs: list[dict[str, Any]] = Field(default_factory=list)
    animation_specs: list[dict[str, Any]] = Field(default_factory=list)
    audio_specs: list[dict[str, Any]] = Field(default_factory=list)
    music_specs: list[dict[str, Any]] = Field(default_factory=list)
    editing_specs: list[dict[str, Any]] = Field(default_factory=list)
    rendering_specs: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 10: Validation
# ---------------------------------------------------------------------------

class ValidationIssue(KnowledgeObject):
    category: str = ""  # missing_info, contradiction, timeline_error, etc.
    severity: str = ""  # error, warning, info
    location: str = ""
    description: str = ""
    suggestion: str = ""


class Validation(KnowledgeObject):
    issues: list[ValidationIssue] = Field(default_factory=list)
    passed: bool = False
    score: float = 0.0


# ---------------------------------------------------------------------------
# Phase 11: Creative Critique
# ---------------------------------------------------------------------------

class CritiqueFinding(KnowledgeObject):
    question: str = ""
    answer: str = ""
    severity: str = ""  # critical, major, minor
    recommendation: str = ""


class CreativeCritique(KnowledgeObject):
    findings: list[CritiqueFinding] = Field(default_factory=list)
    overall_assessment: str = ""
    recommended_actions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 12: Knowledge Integration
# ---------------------------------------------------------------------------

class KnowledgeGraphNode(KnowledgeObject):
    id: str = ""
    type: str = ""
    label: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphEdge(KnowledgeObject):
    source_id: str = ""
    target_id: str = ""
    relationship: str = ""


class KnowledgeIntegration(KnowledgeObject):
    package: dict[str, Any] = Field(default_factory=dict)
    knowledge_graph: dict[str, Any] = Field(default_factory=dict)
    asset_registry: list[dict[str, Any]] = Field(default_factory=list)
    dependencies: list[dict[str, Any]] = Field(default_factory=list)
    cross_references: list[dict[str, Any]] = Field(default_factory=list)
    version_history: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase Result (unified container)
# ---------------------------------------------------------------------------

class PhaseResult(BaseModel):
    phase_number: int
    phase_name: str
    status: PhaseStatus = PhaseStatus.PENDING
    # SerializeAsAny preserves concrete subclass fields when the containing
    # PhaseResult is serialized. Without it, Pydantic dumps using the declared
    # base type (KnowledgeObject) and silently drops subclass-specific semantic
    # fields (color, lighting, ...). This is P0-03R-SER-01: polymorphic
    # serialization must preserve runtime semantics. The knowledge_type
    # discriminator (on KnowledgeObject) enables subtype-faithful reload.
    knowledge: SerializeAsAny[Optional[KnowledgeObject]] = None
    draft_count: int = 0
    errors: list[str] = Field(default_factory=list)
    validation_issues: list[ValidationIssue] = Field(default_factory=list)
    critique_findings: list[CritiqueFinding] = Field(default_factory=list)
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: str = ""

    @model_validator(mode="before")
    @classmethod
    def _rehydrate_knowledge_subtype(cls, data: Any) -> Any:
        """Reconstruct the concrete KnowledgeObject subtype on reload.

        Pydantic deserializes ``knowledge`` to the declared base type unless we
        rehydrate using the persisted ``knowledge_type`` discriminator.  This
        dispatcher rebuilds the concrete subclass (e.g. VisualLanguage) so
        subclass-only semantic fields survive JSON -> model (P0-03R-SER-01 §7).
        """
        if not isinstance(data, dict):
            return data
        k = data.get("knowledge")
        if not isinstance(k, dict):
            return data
        ktype = k.get("knowledge_type") or ""
        data = dict(data)
        if ktype:
            cls_map = {
                "CreativeUnderstanding": CreativeUnderstanding,
                "StoryFoundation": StoryFoundation,
                "StoryBeat": StoryBeat,
                "CharacterPsychology": CharacterPsychology,
                "Character": Character,
                "WorldDevelopment": WorldDevelopment,
                "Scene": Scene,
                "NarrativeExpansion": NarrativeExpansion,
                "ScenePlan": ScenePlan,
                "ScenePlanning": ScenePlanning,
                "DialoguePlan": DialoguePlan,
                "DialoguePlanning": DialoguePlanning,
                "VisualLanguage": VisualLanguage,
                "ProductionSpecifications": ProductionSpecifications,
                "ValidationIssue": ValidationIssue,
                "Validation": Validation,
                "CritiqueFinding": CritiqueFinding,
                "CreativeCritique": CreativeCritique,
                "KnowledgeGraphNode": KnowledgeGraphNode,
                "KnowledgeGraphEdge": KnowledgeGraphEdge,
                "KnowledgeIntegration": KnowledgeIntegration,
            }
            target = cls_map.get(ktype)
            if target is not None:
                data["knowledge"] = target(**k)
        return data


# ---------------------------------------------------------------------------
# Production Knowledge Package (final output)
# ---------------------------------------------------------------------------

class ProductionKnowledgePackage(BaseModel):
    episode_id: str = ""
    run_id: str = ""
    policy_snapshot_id: str = ""
    synopsis: str = ""
    constraints: dict[str, Any] = Field(default_factory=dict)
    creative_understanding: Optional[CreativeUnderstanding] = None
    story_foundation: Optional[StoryFoundation] = None
    character_psychology: Optional[CharacterPsychology] = None
    world_development: Optional[WorldDevelopment] = None
    narrative_expansion: Optional[NarrativeExpansion] = None
    scene_planning: Optional[ScenePlanning] = None
    dialogue_planning: Optional[DialoguePlanning] = None
    visual_language: Optional[VisualLanguage] = None
    production_specifications: Optional[ProductionSpecifications] = None
    validation: Optional[Validation] = None
    creative_critique: Optional[CreativeCritique] = None
    knowledge_integration: Optional[KnowledgeIntegration] = None
    phase_results: list[PhaseResult] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "2.0.0"
