"""Genesis2 — Creative Intelligence Engine data models.

Every phase produces structured knowledge objects. Every object contains:
purpose, creative_intent, reasoning, confidence, dependencies, validation, metadata.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


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


class KnowledgeObject(BaseModel):
    """Base for all knowledge objects produced by phases."""
    purpose: str = ""
    creative_intent: str = ""
    reasoning: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    dependencies: list[str] = Field(default_factory=list)
    validation: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


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


class NarrativeExpansion(KnowledgeObject):
    acts: list[dict[str, Any]] = Field(default_factory=list)
    sequences: list[dict[str, Any]] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 06: Scene Planning
# ---------------------------------------------------------------------------

class ScenePlan(KnowledgeObject):
    scene_number: int = 0
    purpose: str = ""
    conflict: str = ""
    emotion: str = ""
    visual_goal: str = ""
    audio_goal: str = ""
    character_goal: str = ""
    transition: str = ""
    duration: str = ""
    dependencies: list[str] = Field(default_factory=list)


class ScenePlanning(KnowledgeObject):
    scenes: list[ScenePlan] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 07: Dialogue Planning
# ---------------------------------------------------------------------------

class DialoguePlan(KnowledgeObject):
    scene_number: int = 0
    conversation_intent: str = ""
    subtext: str = ""
    emotional_state: str = ""
    silence_opportunities: list[str] = Field(default_factory=list)
    dialogue_rhythm: str = ""
    speech_patterns: str = ""
    voice_direction: str = ""


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
    knowledge: KnowledgeObject | None = None
    draft_count: int = 0
    errors: list[str] = Field(default_factory=list)
    validation_issues: list[ValidationIssue] = Field(default_factory=list)
    critique_findings: list[CritiqueFinding] = Field(default_factory=list)
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: str = ""


# ---------------------------------------------------------------------------
# Production Knowledge Package (final output)
# ---------------------------------------------------------------------------

class ProductionKnowledgePackage(BaseModel):
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
