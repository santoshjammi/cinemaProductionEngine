"""Asset, Render, Reference — the output objects of the Movie OS.

These are the persistent records of everything the system produces.
When a frame is rendered, a Render record is created. When the
rendering succeeds, an Asset is produced. References link assets
to other assets (e.g., a generated image references its seed,
workflow, and source frame).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MUSIC = "music"
    SFX = "sfx"
    SUBTITLE = "subtitle"
    METADATA = "metadata"
    PROMPT = "prompt"
    WORKFLOW = "workflow"


class AssetStatus(str, Enum):
    PENDING = "pending"           # requested, not started
    GENERATING = "generating"     # in progress
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"             # reused from a previous run


class RenderBackend(str, Enum):
    SDXL_LOCAL = "sdxl_local"
    FLUX_COMFYUI = "flux_comfyui"
    EDGE_TTS = "edge_tts"
    VOICEBOX = "voicebox"
    KOKORO = "kokoro"
    SVD_LOCAL = "svd_local"
    PROCEDURAL = "procedural"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Reference — a link from one asset to another
# ---------------------------------------------------------------------------

class Reference(BaseModel):
    """A reference relationship between assets (e.g., img2img uses hero)."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    target_id: UUID                                   # the asset being referenced
    reference_type: str = "inspiration"              # "inspiration", "control", "ipadapter", "img2img"
    strength: float = 1.0                           # 0.0-1.0
    notes: str = ""


# ---------------------------------------------------------------------------
# Asset — the output of a render
# ---------------------------------------------------------------------------

class Asset(BaseModel):
    """A produced asset (image, video, audio, etc.)."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    type: AssetType
    status: AssetStatus = AssetStatus.PENDING

    # The file
    path: Optional[Path] = None
    url: Optional[str] = None                        # alternative: remote URL
    mime_type: str = ""
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None

    # Provenance
    render_id: Optional[UUID] = None                 # which Render produced this
    backend: RenderBackend = RenderBackend.UNKNOWN
    workflow: str = ""
    model: str = ""
    seed: Optional[int] = None

    # Quality
    clip_score: Optional[float] = None
    quality_grade: Optional[str] = None              # "draft", "production", "high_quality"
    notes: str = ""

    # References (img2img, IPAdapter, etc.)
    references: list[Reference] = Field(default_factory=list)

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: Optional[float] = None          # for video/audio


# ---------------------------------------------------------------------------
# Render — the request to produce an asset
# ---------------------------------------------------------------------------

class Render(BaseModel):
    """A request to render an asset. The Render is the recipe; the Asset is the result."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    type: AssetType

    # What we're rendering (e.g., a Frame, a Scene's voiceover, a Shot's audio bed)
    target_type: str = ""                            # "frame", "voiceover", "music", "sfx"
    target_id: Optional[UUID] = None

    # The request payload
    prompt: str = ""
    negative_prompt: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)  # model-specific

    # The execution
    backend: RenderBackend = RenderBackend.UNKNOWN
    workflow: str = ""
    model: str = ""
    seed: Optional[int] = None

    # Cost / limits
    cost_estimate_usd: float = 0.0
    max_duration_seconds: float = 600.0
    budget_priority: int = 5                          # 1-10

    # Result
    asset_id: Optional[UUID] = None
    status: AssetStatus = AssetStatus.PENDING
    error: str = ""
    attempts: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
