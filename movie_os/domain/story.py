"""Story hierarchy — the core narrative structure.

Story → Act → Sequence → Scene → Shot → Frame

This is how films are actually structured. Each level has its own metadata
and its own responsibilities:

    Story      — the whole work (title, territory, ending, target duration)
    Act        — a major dramatic movement (3-act: setup, confrontation, resolution)
    Sequence   — a group of scenes that form a thematic unit
    Scene      — a single dramatic beat in a single location/time
    Shot       — a single camera setup (angle, lens, framing, duration)
    Frame      — a single static image (the master cinematic frame)

The lower levels inherit context from the upper levels. A Shot knows
which Scene it belongs to. A Frame knows which Shot it belongs to.
The renderer walks top-down, building up context for each prompt.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class AspectRatio(str, Enum):
    """Common cinematic aspect ratios."""
    RATIO_16_9 = "16:9"      # YouTube, default
    RATIO_9_16 = "9:16"      # Shorts, Reels, TikTok
    RATIO_1_1 = "1:1"        # Instagram feed
    RATIO_21_9 = "21:9"      # Ultrawide cinematic
    RATIO_4_3 = "4:3"        # Classic TV, some Instagram


class Resolution(str, Enum):
    """Render resolution presets."""
    SD_480 = "854x480"
    HD_720 = "1280x720"
    FHD_1080 = "1920x1080"
    QHD_1440 = "2560x1440"
    UHD_4K = "3840x2160"
    MASTER_4K = "4096x2304"   # film mastering, will be cropped to platform


# ---------------------------------------------------------------------------
# Story hierarchy
# ---------------------------------------------------------------------------

class Story(BaseModel):
    """The whole work — top of the narrative hierarchy."""
    model_config = ConfigDict(use_enum_values=True)

    id: UUID = Field(default_factory=uuid4)
    title: str
    logline: str = ""                                # one-sentence pitch
    synopsis: str = ""                               # full synopsis
    language: str = "en"
    target_audience: str = ""
    territory: str = ""                              # e.g., "emotional_withdrawal"
    cluster: str = ""
    archetype: str = ""
    ending: str = ""                                 # quiet_realization, devastating_truth, etc.

    # Structural intent
    target_duration_seconds: float = 300.0          # 5 min default
    aspect_ratio: AspectRatio = AspectRatio.RATIO_16_9
    resolution: Resolution = Resolution.HD_720

    # Hierarchy (the actual content)
    acts: list["Act"] = Field(default_factory=list)

    # Provenance
    dna: dict[str, Any] = Field(default_factory=dict)
    context_file: Optional[Path] = None
    source: dict[str, str] = Field(default_factory=dict)

    @property
    def total_duration_seconds(self) -> float:
        return sum(s.total_duration_seconds for a in self.acts for s in a.sequences for scene in s.scenes for s2 in scene.shots for s2 in s2.shots)


class Act(BaseModel):
    """A major dramatic movement (setup, confrontation, resolution)."""
    model_config = ConfigDict(use_enum_values=True)

    id: UUID = Field(default_factory=uuid4)
    number: int                                       # 1, 2, 3
    title: str                                        # "Observation", "Inner Reality", "Psychological Truth"
    viewer_response: str = ""                        # "I know this feeling."
    sequences: list["Sequence"] = Field(default_factory=list)


class Sequence(BaseModel):
    """A group of scenes that form a thematic unit."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    scenes: list["Scene"] = Field(default_factory=list)


class Scene(BaseModel):
    """A single dramatic beat in a single location/time."""
    model_config = ConfigDict(use_enum_values=True)

    id: UUID = Field(default_factory=uuid4)
    number: int
    title: str
    phase: str = ""                                  # hook, warmth, normalcy, crack, collapse, almost, retreat, duality, climax
    beat: str = ""                                   # opening_hook, contrast_memory, etc.
    emotional_state: str = ""
    energy: int = 5                                  # 1-10

    # Content
    voiceover: str = ""
    dialogues: list[dict[str, Any]] = Field(default_factory=list)  # populated by scene-level agents
    scene_description: str = ""                      # what we see
    scene_description_alt: str = ""                  # v5.2 — 2nd visual for hard cut (irreversible_moment)
    visual_cause_of_emotion: str = ""                # the micro-behavior

    # Camera
    shot_language: dict[str, Any] = Field(default_factory=dict)

    # Characters & environment
    characters_present: list[str] = Field(default_factory=list)
    environment_id: Optional[UUID] = None

    # Audio
    music_cue: dict[str, Any] = Field(default_factory=dict)  # {zone, volume}
    ambient_cue: dict[str, Any] = Field(default_factory=dict)
    silence_engine: dict[str, Any] = Field(default_factory=dict)  # v5.0
    vocal_fracture: bool = False
    irreversible_moment: bool = False
    pre_moment: bool = False
    post_moment: bool = False
    shows_duality: bool = False

    # Hierarchy
    shots: list["Shot"] = Field(default_factory=list)

    # Rendering
    ken_burns_effect: str = "ken-burns"
    duration_hint: str = "20-30s"
    target_duration_seconds: float = 0.0

    @property
    def total_duration_seconds(self) -> float:
        if self.target_duration_seconds > 0:
            return self.target_duration_seconds
        return sum(s.duration_seconds for s in self.shots)


class Shot(BaseModel):
    """A single camera setup — angle, lens, framing, duration.

    One scene can have 1+ shots. The Shot is the unit of motion: what
    pans, zooms, or cuts happen within the scene.
    """
    model_config = ConfigDict(use_enum_values=True)

    id: UUID = Field(default_factory=uuid4)
    number: int
    shot_size: str = "medium"                        # close-up, medium, wide, extreme_wide
    camera_movement: str = "static"                 # static, push-in, pan-right, pan-left, dolly, handheld
    lens_mm: int = 50
    duration_seconds: float = 8.0

    # The visual goal of this shot
    visual_intent: str = ""                          # "establish the room", "isolate her hand", "his face when she says no"
    prompt_context: dict[str, Any] = Field(default_factory=dict)  # extra context for the image prompt

    # Output
    frames: list["Frame"] = Field(default_factory=list)


class Frame(BaseModel):
    """A single static image — the master cinematic frame.

    A Shot can have 1+ frames (e.g., for a hard cut, the irreversible
    moment has 2 frames per the v5.2 enhancement).
    """
    model_config = ConfigDict(use_enum_values=True)

    id: UUID = Field(default_factory=uuid4)
    number: int
    description: str = ""                            # the visual moment
    visual_cause_of_emotion: str = ""

    # Render config
    workflow: str = "default"                        # which ComfyUI workflow
    model: str = "sdxl"                              # which model
    seed: Optional[int] = None
    reference_image_ids: list[UUID] = Field(default_factory=list)
    prompt_override: Optional[str] = None

    # Output
    asset_id: Optional[UUID] = None
    rendered_path: Optional[Path] = None


# Resolve forward references
Story.model_rebuild()
Act.model_rebuild()
Sequence.model_rebuild()
Scene.model_rebuild()
Shot.model_rebuild()
Frame.model_rebuild()
