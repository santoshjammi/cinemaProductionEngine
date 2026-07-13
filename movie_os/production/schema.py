"""Movie OS v1 — Production file schemas (Pydantic models).

Every structured production file has a Pydantic schema for validation.
This ensures all productions follow the canonical structure.

Schemas:
  - ProductionSchema: production.yaml
  - DNASchema: dna.yaml
  - CreativeBriefSchema: creative_brief.md (parsed as YAML frontmatter)
  - DirectorNotesSchema: director_notes.md (parsed as YAML frontmatter)
  - OutlineSchema: outline.md
  - ScreenplaySchema: screenplay.md (structured Markdown parser)
  - MusicScoreSchema: music_score.yaml
  - ProductionRulesSchema: production_rules.yaml
  - ManifestSchema: manifest.yaml
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ContentCategory(str, Enum):
    """Content categories (production types)."""
    PSYCHOLOGICAL_STORY = "psychological_story"
    KIDS_STORY = "kids_story"
    DEVOTIONAL = "devotional"
    DOCUMENTARY = "documentary"
    EXPLAINER = "explainer"
    SHORT = "short"
    HISTORICAL = "historical"
    CONVERSATION = "conversation"
    CASE_STUDY = "case_study"


class ProductionStatus(str, Enum):
    """Production lifecycle status."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    IN_PRODUCTION = "in_production"
    EVALUATING = "evaluating"
    REVISING = "revising"
    PUBLISHED = "published"


class ScenePhase(str, Enum):
    """Screenplay scene phases (HOOK-PLOT-CLIMAX framework)."""
    HOOK = "hook"
    PLOT = "plot"
    CLIMAX = "climax"
    RESOLUTION = "resolution"


# ---------------------------------------------------------------------------
# Production Schema — production.yaml
# ---------------------------------------------------------------------------

class ProductionSchema(BaseModel):
    """Schema for production.yaml — top-level production metadata."""

    schema: str = Field(default="movie_os.production.v1", description="Schema identifier")
    version: str = Field(default="1.0.0", description="Schema version")
    id: str = Field(..., description="Unique production ID (e.g., 'ew001')")
    title: str = Field(..., description="Production title")
    content_type: ContentCategory = Field(default=ContentCategory.PSYCHOLOGICAL_STORY)
    grammar: str = Field(default="psychological_cinema", description="Production grammar to use")
    status: ProductionStatus = Field(default=ProductionStatus.DRAFT)

    # Series hierarchy
    series: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None

    # Metadata
    created_by: str = ""
    updated_at: str = ""
    tags: list[str] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    environments: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_id_format(self) -> "ProductionSchema":
        if not self.id or len(self.id) < 2:
            raise ValueError("production.id must be at least 2 characters")
        return self


# ---------------------------------------------------------------------------
# DNA Schema — dna.yaml
# ---------------------------------------------------------------------------

class DNASchema(BaseModel):
    """Schema for dna.yaml — core identity of the production."""

    schema: str = Field(default="movie_os.dna.v1", description="Schema identifier")
    version: str = Field(default="1.0.0")
    id: str = ...
    territory: str = ...  # e.g., "emotional_withdrawal"
    cluster: str = ...  # e.g., "fear_based_withdrawal"
    mechanism: str = ...  # e.g., "anticipated_rejection"
    archetype: str = ...  # e.g., "married_husband"
    theme: str = ...  # e.g., "love_becomes_dangerous"
    premise: str = ...  # One-sentence story premise
    ending: str = ...  # e.g., "quiet_realization"


# ---------------------------------------------------------------------------
# Creative Brief Schema — creative_brief.md (YAML frontmatter)
# ---------------------------------------------------------------------------

class CreativeBriefSchema(BaseModel):
    """Schema for creative_brief.md — why we're making this production."""

    schema: str = Field(default="movie_os.creative_brief.v1")
    version: str = Field(default="1.0.0")
    target_audience: str = ...
    primary_emotion: str = ...
    desired_viewer_outcome: list[str] = Field(default_factory=list)  # e.g., ["recognition", "hope"]
    desired_retention: float = 0.0  # Target retention percentage
    target_runtime_seconds: int = 0
    reference_works: list[str] = Field(default_factory=list)
    production_goals: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Director Notes Schema — director_notes.md (YAML frontmatter)
# ---------------------------------------------------------------------------

class DirectorNotesSchema(BaseModel):
    """Schema for director_notes.md — creative north star."""

    schema: str = Field(default="movie_os.director_notes.v1")
    version: str = Field(default="1.0.0")
    pacing_philosophy: str = ...
    visual_language: list[str] = Field(default_factory=list)
    acting_style: list[str] = Field(default_factory=list)
    emotional_constraints: list[str] = Field(default_factory=list)
    cinematic_intent: str = ...


# ---------------------------------------------------------------------------
# Outline Schema — outline.md
# ---------------------------------------------------------------------------

class SceneOutline(BaseModel):
    """A single scene in the outline."""
    scene_number: int = ...
    title: str = ...
    phase: ScenePhase = ...  # hook, plot, climax, resolution
    purpose: str = ...  # Narrative purpose of this scene
    location: str = ...
    characters: list[str] = Field(default_factory=list)
    emotion: str = ...
    summary: str = ...


class OutlineSchema(BaseModel):
    """Schema for outline.md — story structure (HOOK-PLOT-CLIMAX)."""

    schema: str = Field(default="movie_os.outline.v1")
    version: str = Field(default="1.0.0")
    acts: list[SceneOutline] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Screenplay Schema — screenplay.md (structured Markdown parser)
# ---------------------------------------------------------------------------

class ScreenplayDialogue(BaseModel):
    """A single dialogue line in a scene."""
    character: str = ...
    line: str = ...
    delivery: str = ""  # e.g., "whispered", "laughing", "hesitant"
    subtext: str = ""  # What the character really means


class ScreenplayBeat(BaseModel):
    """An emotional beat within a scene."""
    type: str = ...  # e.g., "pause", "silence", "beat", "action_beat"
    duration_seconds: float = 0.0
    description: str = ""


class ScreenplayScene(BaseModel):
    """A single scene in the screenplay (Movie OS structured format)."""
    schema: str = Field(default="movie_os.screenplay_scene.v1")
    scene_number: int = ...
    title: str = ...
    phase: ScenePhase = ...  # hook, plot, climax, resolution
    purpose: str = ...  # Narrative purpose
    location: str = ...
    time_of_day: str = ""  # e.g., "morning", "night"
    characters: list[str] = Field(default_factory=list)
    emotion: str = ...
    mood: str = ...

    # Structured sections
    dialogue: list[ScreenplayDialogue] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    beats: list[ScreenplayBeat] = Field(default_factory=list)
    silence: list[ScreenplayBeat] = Field(default_factory=list)
    narration: list[str] = Field(default_factory=list)

    # Director notes
    director_notes: list[str] = Field(default_factory=list)
    camera_intent: str = ""  # e.g., "close-up, shallow DOF"
    music_intent: str = ""  # e.g., "fear_theme, intensity 0.4"


class ScreenplaySchema(BaseModel):
    """Schema for screenplay.md — canonical creative artifact."""

    schema: str = Field(default="movie_os.screenplay.v1")
    version: str = Field(default="1.0.0")
    title: str = ...
    characters: list[dict[str, Any]] = Field(default_factory=list)  # character definitions
    acts: list[ScreenplayScene] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_acts(self) -> "ScreenplaySchema":
        if not self.acts:
            raise ValueError("screenplay must have at least one act/scene")
        return self


# ---------------------------------------------------------------------------
# Music Score Schema — music_score.yaml
# ---------------------------------------------------------------------------

class MusicTheme(BaseModel):
    """A single music theme in the score."""
    name: str = ...  # e.g., "main_theme", "fear_theme"
    instruments: list[str] = Field(default_factory=list)
    mood: str = ...
    key: str = ""  # e.g., "C_major", "D_minor"
    tempo: int = 0
    description: str = ""


class CharacterMotif(BaseModel):
    """A musical motif for a character."""
    character: str = ...
    primary_instrument: str = ...
    motif_pattern: str = ...
    description: str = ""


class MusicTransition(BaseModel):
    """A transition between themes."""
    from_theme: str = ...
    to_theme: str = ...
    method: str = ...  # e.g., "crossfade", "cut", "fade"
    duration_seconds: float = 0.0


class MusicScoreSchema(BaseModel):
    """Schema for music_score.yaml — global music themes and motifs."""

    schema: str = Field(default="movie_os.music_score.v1")
    version: str = Field(default="1.0.0")
    title: str = ...
    composer_notes: str = ""
    themes: dict[str, MusicTheme] = Field(default_factory=dict)
    character_motifs: dict[str, CharacterMotif] = Field(default_factory=dict)
    transitions: list[MusicTransition] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Production Rules Schema — production_rules.yaml
# ---------------------------------------------------------------------------

class VoiceRules(BaseModel):
    """Voice configuration for this production."""
    primary_voice: str = ""
    secondary_voices: list[str] = Field(default_factory=list)


class SubtitleRules(BaseModel):
    """Subtitle configuration for this production."""
    enabled: bool = False
    language: str = "en"


class CameraRules(BaseModel):
    """Camera restrictions for this production."""
    allow_handheld: bool = True
    allowed_lens_mm: list[int] = Field(default_factory=list)  # e.g., [35, 50]
    max_camera_movement: str = "slow_pan"


class OutputRules(BaseModel):
    """Output targets for this production."""
    aspect_ratio: str = "16:9"
    resolution: str = "1280x720"
    format: str = "mp4"


class ProductionRulesSchema(BaseModel):
    """Schema for production_rules.yaml — production-specific creative overrides."""

    schema: str = Field(default="movie_os.production_rules.v1")
    version: str = Field(default="1.0.0")
    voice: VoiceRules = Field(default_factory=VoiceRules)
    subtitles: SubtitleRules = Field(default_factory=SubtitleRules)
    camera: CameraRules = Field(default_factory=CameraRules)
    output: OutputRules = Field(default_factory=OutputRules)


# ---------------------------------------------------------------------------
# Manifest Schema — manifest.yaml
# ---------------------------------------------------------------------------

class ManifestSchema(BaseModel):
    """Schema for manifest.yaml — production metadata."""

    schema: str = Field(default="movie_os.manifest.v1")
    version: str = Field(default="1.0.0")
    production_id: str = ...
    generated_at: str = ""
    assets: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Grammar Schema — grammars/{type}/grammar.yaml
# ---------------------------------------------------------------------------

class GrammarDefaults(BaseModel):
    """Default creative rules for a grammar."""
    scene_duration_max_seconds: int = 60
    dialogue_density: str = "high"  # low, medium, high
    pacing: str = "deliberate"
    camera_language: str = "intimate_closeups"
    lighting_key: str = "natural_shadows"
    music_style: str = ""
    voice_style: str = ""
    transitions: str = "crossfade"
    color_grading: str = ""


class GrammarEvaluationCriteria(BaseModel):
    """Evaluation criteria for a grammar."""
    criteria: list[str] = Field(default_factory=list)
    minimum_scores: dict[str, float] = Field(default_factory=dict)


class GrammarSchema(BaseModel):
    """Schema for grammars/{type}/grammar.yaml — production grammar rules."""

    schema: str = Field(default="movie_os.grammar.v1")
    version: str = Field(default="1.0.0")
    name: str = ...  # e.g., "psychological_cinema"
    description: str = ...
    defaults: GrammarDefaults = Field(default_factory=GrammarDefaults)
    evaluation: GrammarEvaluationCriteria = Field(default_factory=GrammarEvaluationCriteria)


# ---------------------------------------------------------------------------
# Schema version registry
# ---------------------------------------------------------------------------

SCHEMA_VERSIONS = {
    "movie_os.production.v1": ProductionSchema,
    "movie_os.dna.v1": DNASchema,
    "movie_os.creative_brief.v1": CreativeBriefSchema,
    "movie_os.director_notes.v1": DirectorNotesSchema,
    "movie_os.outline.v1": OutlineSchema,
    "movie_os.screenplay.v1": ScreenplaySchema,
    "movie_os.music_score.v1": MusicScoreSchema,
    "movie_os.production_rules.v1": ProductionRulesSchema,
    "movie_os.manifest.v1": ManifestSchema,
    "movie_os.grammar.v1": GrammarSchema,
}


def get_schema(schema_id: str) -> type[BaseModel]:
    """Get the Pydantic model for a schema ID."""
    if schema_id not in SCHEMA_VERSIONS:
        raise ValueError(f"Unknown schema: {schema_id}. Available: {list(SCHEMA_VERSIONS.keys())}")
    return SCHEMA_VERSIONS[schema_id]


def validate_schema(data: dict[str, Any], schema_id: str) -> BaseModel:
    """Validate data against a schema and return the validated model."""
    model = get_schema(schema_id)
    return model.model_validate(data)


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    # Enums
    "ContentCategory",
    "ProductionStatus",
    "ScenePhase",
    # Schemas
    "ProductionSchema",
    "DNASchema",
    "CreativeBriefSchema",
    "DirectorNotesSchema",
    "OutlineSchema",
    "ScreenplaySchema",
    "ScreenplayScene",
    "ScreenplayDialogue",
    "ScreenplayBeat",
    "MusicScoreSchema",
    "MusicTheme",
    "CharacterMotif",
    "ProductionRulesSchema",
    "ManifestSchema",
    "GrammarSchema",
    "GrammarDefaults",
    # Utilities
    "SCHEMA_VERSIONS",
    "get_schema",
    "validate_schema",
]
