"""Movie OS configuration schema (Pydantic).

This is the schema for the `config/movie_os.yaml` file. Every setting
that was previously a CLI flag, hardcoded constant, or magic number
lives here. The pipeline reads from this — not from code.

The schema is split into sections:

    project:       — name, output dir, log level
    providers:     — which provider to use per capability, and its settings
    capabilities:  — which capabilities are enabled, budget limits
    rendering:     — aspect ratio, resolution, quality, output formats
    pipeline:      — which steps to run, what to skip, auto-approve

Every field has a default. A minimal config can be a single line:
    version: "1.0"
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


SCHEMA_VERSION = "1.0"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class QualityMode(str, Enum):
    DRAFT = "draft"
    PRODUCTION = "production"
    HIGH_QUALITY = "high_quality"


class AspectRatio(str, Enum):
    RATIO_16_9 = "16:9"
    RATIO_9_16 = "9:16"
    RATIO_1_1 = "1:1"
    RATIO_21_9 = "21:9"
    RATIO_4_3 = "4:3"


class VideoCodec(str, Enum):
    H264 = "libx264"
    H265 = "libx265"
    VP9 = "libvpx-vp9"
    AV1 = "libsvtav1"


class AudioCodec(str, Enum):
    AAC = "aac"
    OPUS = "libopus"
    MP3 = "libmp3lame"


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class ProjectConfig(BaseModel):
    """Top-level project settings."""
    name: str = "movie_os"
    output_dir: Path = Path("output/videos")
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[Path] = None
    cache_dir: Path = Path(".movie_os_cache")


# ---------------------------------------------------------------------------
# Provider settings
# ---------------------------------------------------------------------------

class ProviderOption(BaseModel):
    """A single provider's settings (model-agnostic, just key-value)."""
    model_config = ConfigDict(extra="allow")         # accept any extra fields

    label: str = ""                                    # human-readable name
    enabled: bool = True
    cost_per_call_usd: float = 0.0
    # Any additional settings the provider needs (model name, URL, etc.)
    settings: dict[str, Any] = Field(default_factory=dict)


class ProviderGroup(BaseModel):
    """All providers for a single capability (e.g., all image providers)."""
    default: str = ""                                   # the label of the default (empty = no default)
    options: dict[str, ProviderOption] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _default_must_exist(self) -> "ProviderGroup":
        # Empty default is fine (means "no provider configured")
        if self.default and self.default not in self.options:
            raise ValueError(
                f"providers.{self.__class_name__}.default='{self.default}' "
                f"is not in options. Available: {list(self.options.keys())}"
            )
        return self

    def __class_name__(self) -> str:
        return getattr(self, "_owner_capability", "unknown")


# ---------------------------------------------------------------------------
# Provider groups per capability
# ---------------------------------------------------------------------------

class ImageProviderConfig(ProviderGroup):
    """Image generation providers."""
    _owner_capability = "image"


class VideoProviderConfig(ProviderGroup):
    """Video generation providers."""
    _owner_capability = "video"


class VoiceProviderConfig(ProviderGroup):
    """Voice synthesis providers."""
    _owner_capability = "voice"


class MusicProviderConfig(ProviderGroup):
    """Music generation providers."""
    _owner_capability = "music"


class StoryProviderConfig(ProviderGroup):
    """Story generation providers."""
    _owner_capability = "story"


class TranslationProviderConfig(ProviderGroup):
    """Translation providers."""
    _owner_capability = "translation"


class ResearchProviderConfig(ProviderGroup):
    """Research providers."""
    _owner_capability = "research"


class ProvidersConfig(BaseModel):
    """All providers, grouped by capability."""
    image: ImageProviderConfig = Field(default_factory=lambda: ImageProviderConfig(default="", options={}))
    video: VideoProviderConfig = Field(default_factory=lambda: VideoProviderConfig(default="", options={}))
    voice: VoiceProviderConfig = Field(default_factory=lambda: VoiceProviderConfig(default="", options={}))
    music: MusicProviderConfig = Field(default_factory=lambda: MusicProviderConfig(default="", options={}))
    story: StoryProviderConfig = Field(default_factory=lambda: StoryProviderConfig(default="", options={}))
    translation: TranslationProviderConfig = Field(default_factory=lambda: TranslationProviderConfig(default="", options={}))
    research: ResearchProviderConfig = Field(default_factory=lambda: ResearchProviderConfig(default="", options={}))


# ---------------------------------------------------------------------------
# Capability configuration
# ---------------------------------------------------------------------------

class CapabilityConfig(BaseModel):
    """A single capability's settings (enabled, budget, etc.)."""
    enabled: bool = True
    budget_usd: float = 0.0                            # 0 = unlimited (or local)
    timeout_seconds: float = 600.0
    max_retries: int = 3


class CapabilitiesConfig(BaseModel):
    """All capabilities and their settings."""
    image: CapabilityConfig = Field(default_factory=CapabilityConfig)
    video: CapabilityConfig = Field(default_factory=CapabilityConfig)
    voice: CapabilityConfig = Field(default_factory=CapabilityConfig)
    music: CapabilityConfig = Field(default_factory=CapabilityConfig)
    story: CapabilityConfig = Field(default_factory=CapabilityConfig)
    translation: CapabilityConfig = Field(default_factory=CapabilityConfig)
    research: CapabilityConfig = Field(default_factory=CapabilityConfig)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

class RenderingConfig(BaseModel):
    """How the final video is rendered."""
    aspect_ratio: AspectRatio = AspectRatio.RATIO_16_9
    resolution: str = "1280x720"                       # free-form string for flexibility
    quality: QualityMode = QualityMode.PRODUCTION
    output_format: str = "mp4"
    video_codec: VideoCodec = VideoCodec.H264
    audio_codec: AudioCodec = AudioCodec.AAC
    video_bitrate: str = "5M"
    audio_bitrate: str = "192k"
    fps: int = 24


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class PipelineStep(str, Enum):
    NARRATIVE = "narrative"
    IMAGES = "images"
    AUDIO = "audio"
    MUSIC = "music"
    SFX = "sfx"
    MIX = "mix"
    VIDEO = "video"
    CAPTIONS = "captions"
    PUBLISH = "publish"


class PipelineConfig(BaseModel):
    """Which steps the pipeline runs, in what order."""
    steps: list[PipelineStep] = Field(default_factory=lambda: [
        PipelineStep.NARRATIVE,
        PipelineStep.IMAGES,
        PipelineStep.AUDIO,
        PipelineStep.MUSIC,
        PipelineStep.SFX,
        PipelineStep.MIX,
        PipelineStep.VIDEO,
    ])
    skip: list[PipelineStep] = Field(default_factory=list)
    auto_approve: bool = False
    dry_run: bool = False
    resume_from: Optional[PipelineStep] = None
    parallel: bool = True


# ---------------------------------------------------------------------------
# Top-level config
# ---------------------------------------------------------------------------

class MovieOSConfig(BaseModel):
    """The full Movie OS configuration.

    This is the single source of truth for all runtime settings.
    Loaded from `config/movie_os.yaml` (or wherever the user points).
    """
    version: str = SCHEMA_VERSION
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
    capabilities: CapabilitiesConfig = Field(default_factory=CapabilitiesConfig)
    rendering: RenderingConfig = Field(default_factory=RenderingConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)

    # Extra (unknown) keys are allowed but ignored — forward compatibility
    model_config = ConfigDict(extra="ignore")

    def provider_for(self, capability: str) -> tuple[str, ProviderOption] | None:
        """Get the (label, settings) for the default provider of a capability.

        Returns None if the capability has no providers configured.
        """
        group = getattr(self.providers, capability, None)
        if not group or not group.options:
            return None
        label = group.default
        if not label or label not in group.options:
            return None
        return label, group.options[label]

    def all_provider_labels(self, capability: str) -> list[str]:
        """Get all available provider labels for a capability."""
        group = getattr(self.providers, capability, None)
        if not group:
            return []
        return list(group.options.keys())
