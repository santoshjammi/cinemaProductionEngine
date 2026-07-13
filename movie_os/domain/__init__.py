"""Movie OS domain models — the vocabulary of the system.

Public API:

    from movie_os.domain import (
        # Story hierarchy
        Story, Act, Sequence, Scene, Shot, Frame,
        AspectRatio, Resolution,
        # Character DNA
        CharacterDNA, PhysicalAppearance, PsychologicalProfile,
        SpeechProfile, VoiceProfile, Wardrobe, ExpressionRange,
        Relationship, CharacterHistory, DevelopmentArc, CharacterReference,
        Gender,
        # Environment DNA
        EnvironmentDNA, LightingProfile, ColorPalette, SoundAmbience,
        CameraPosition, EnvironmentVariant, EnvironmentReference,
        TimeOfDay, Weather, ArchitecturalStyle,
        # Asset / Render / Reference
        Asset, Render, Reference,
        AssetType, AssetStatus, RenderBackend,
        # Prompt
        PromptTemplate, PromptMetadata, Variable, Constraint, Example,
        VariableType, PromptRole,
        # Shot planning (Phase 7)
        ShotPlanner, plan_scene,
    )
"""

from .story import (
    Story,
    Act,
    Sequence,
    Scene,
    Shot,
    Frame,
    AspectRatio,
    Resolution,
)
from .character import (
    CharacterDNA,
    PhysicalAppearance,
    PsychologicalProfile,
    SpeechProfile,
    VoiceProfile,
    Wardrobe,
    ExpressionRange,
    Relationship,
    CharacterHistory,
    DevelopmentArc,
    CharacterReference,
    Gender,
)
from .environment import (
    EnvironmentDNA,
    LightingProfile,
    ColorPalette,
    SoundAmbience,
    CameraPosition,
    EnvironmentVariant,
    EnvironmentReference,
    TimeOfDay,
    Weather,
    ArchitecturalStyle,
)
from .asset import (
    Asset,
    Render,
    Reference,
    AssetType,
    AssetStatus,
    RenderBackend,
)
from .prompt import (
    PromptTemplate,
    PromptMetadata,
    Variable,
    Constraint,
    Example,
    VariableType,
    PromptRole,
)
from .shot_planner import ShotPlanner, plan_scene

__all__ = [
    # Story
    "Story", "Act", "Sequence", "Scene", "Shot", "Frame",
    "AspectRatio", "Resolution",
    # Character
    "CharacterDNA", "PhysicalAppearance", "PsychologicalProfile",
    "SpeechProfile", "VoiceProfile", "Wardrobe", "ExpressionRange",
    "Relationship", "CharacterHistory", "DevelopmentArc", "CharacterReference",
    "Gender",
    # Environment
    "EnvironmentDNA", "LightingProfile", "ColorPalette", "SoundAmbience",
    "CameraPosition", "EnvironmentVariant", "EnvironmentReference",
    "TimeOfDay", "Weather", "ArchitecturalStyle",
    # Asset
    "Asset", "Render", "Reference",
    "AssetType", "AssetStatus", "RenderBackend",
    # Prompt
    "PromptTemplate", "PromptMetadata", "Variable", "Constraint", "Example",
    "VariableType", "PromptRole",
    # Shot planning
    "ShotPlanner", "plan_scene",
]
