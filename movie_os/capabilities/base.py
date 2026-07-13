"""Capability ABC — the interface every AI capability satisfies.

A Capability is what the pipeline asks for ("generate image", "synthesize
voice"). It doesn't know about specific providers — it just defines the
contract. The registry dispatches the request to a registered provider.

This is the plug-in boundary. Adding a new image model (FLUX, SD3,
HiDream) means writing a new ImageProvider and registering it. No other
code changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

from movie_os.domain.asset import Asset, Render, RenderBackend


# Generic for the intent type — each capability defines its own
IntentT = TypeVar("IntentT")
ResultT = TypeVar("ResultT")


class Capability(ABC, Generic[IntentT, ResultT]):
    """Base class for all AI capabilities.

    A Capability is a high-level verb ("generate image", "synthesize
    voice", "plan story"). It dispatches to a provider internally.

    Subclasses must define:
        name: unique capability name (e.g., "image", "voice")
        description: human-readable description
        can_handle(intent): whether this capability accepts the intent
        execute(intent): perform the work, return a Result
    """

    name: str = ""
    description: str = ""
    version: str = "0.1.0"

    @abstractmethod
    def can_handle(self, intent: IntentT) -> bool:
        """Whether this capability can process the given intent."""
        ...

    @abstractmethod
    async def execute(self, intent: IntentT) -> ResultT:
        """Execute the capability. Returns the result."""
        ...


class ImageCapabilityError(RuntimeError):
    """Raised when an image capability fails."""


class VideoCapabilityError(RuntimeError):
    """Raised when a video capability fails."""


class VoiceCapabilityError(RuntimeError):
    """Raised when a voice capability fails."""


class MusicCapabilityError(RuntimeError):
    """Raised when a music capability fails."""


class SFXCapabilityError(RuntimeError):
    """Raised when an SFX capability fails."""


class SFXIntent:
    """Intent to generate a single SFX / ambient sound effect."""
    def __init__(
        self,
        effect_type: str,                                 # "thunder", "rain", "door", "heartbeat", etc.
        duration_seconds: float = 5.0,
        volume: float = 0.5,
        seed: int | None = None,
        output_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.effect_type = effect_type
        self.duration_seconds = duration_seconds
        self.volume = volume
        self.seed = seed
        self.output_path = output_path
        self.metadata = metadata or {}


class SFXResult:
    """Result of an SFX render."""
    def __init__(self, asset: Any = None, data: dict | None = None, error: str | None = None):
        self.asset = asset
        self.data = data or {}
        self.error = error


class StoryCapabilityError(RuntimeError):
    """Raised when a story capability fails."""


class TranslationCapabilityError(RuntimeError):
    """Raised when a translation capability fails."""


class ResearchCapabilityError(RuntimeError):
    """Raised when a research capability fails."""


# ---------------------------------------------------------------------------
# Intent types — what the capabilities consume
# ---------------------------------------------------------------------------

class ImageIntent:
    """Intent to generate an image.

    Carries the prompt, negative prompt, references, and the target
    resolution. The capability decides which model to use.
    """
    def __init__(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        seed: int | None = None,
        reference_image_paths: list[str] | None = None,
        ipadapter_strength: float = 0.6,
        workflow: str = "default",
        quality: str = "production",                   # "draft", "production", "high_quality"
        metadata: dict[str, Any] | None = None,
    ):
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.width = width
        self.height = height
        self.seed = seed
        self.reference_image_paths = reference_image_paths or []
        self.ipadapter_strength = ipadapter_strength
        self.workflow = workflow
        self.quality = quality
        self.metadata = metadata or {}


class VideoIntent:
    """Intent to animate an image into a video clip."""
    def __init__(
        self,
        image_path: str,
        motion_prompt: str = "",
        duration_seconds: float = 4.0,
        fps: int = 24,
        seed: int | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.image_path = image_path
        self.motion_prompt = motion_prompt
        self.duration_seconds = duration_seconds
        self.fps = fps
        self.seed = seed
        self.metadata = metadata or {}


class VoiceIntent:
    """Intent to synthesize a voice clip from text."""
    def __init__(
        self,
        text: str,
        voice: str = "en-US-GuyNeural",
        language: str = "en",
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        prosody_override: dict[str, Any] | None = None,
        vocal_fracture: bool = False,
        output_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.text = text
        self.voice = voice
        self.language = language
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        self.prosody_override = prosody_override
        self.vocal_fracture = vocal_fracture
        self.output_path = output_path
        self.metadata = metadata or {}


class MusicIntent:
    """Intent to generate a music track."""
    def __init__(
        self,
        zone: str,                                     # "act_1", "act_2", "act_3", "sting"
        duration_seconds: float = 30.0,
        volume: float = 0.3,
        mood: str = "",
        seed: int | None = None,
        output_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.zone = zone
        self.duration_seconds = duration_seconds
        self.volume = volume
        self.mood = mood
        self.seed = seed
        self.output_path = output_path
        self.metadata = metadata or {}


class StoryIntent:
    """Intent to generate story content (synopsis, scene structure, etc.)."""
    def __init__(
        self,
        task: str,                                      # "dna", "context", "story", "scenes"
        synopsis: str = "",
        dna: dict[str, Any] | None = None,
        context: str = "",
        story: str = "",
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.task = task
        self.synopsis = synopsis
        self.dna = dna or {}
        self.context = context
        self.story = story
        self.parameters = parameters or {}
        self.metadata = metadata or {}


class TranslationIntent:
    """Intent to translate text to another language."""
    def __init__(
        self,
        text: str,
        source_language: str = "en",
        target_language: str = "es",
        preserve_tone: bool = True,
        metadata: dict[str, Any] | None = None,
    ):
        self.text = text
        self.source_language = source_language
        self.target_language = target_language
        self.preserve_tone = preserve_tone
        self.metadata = metadata or {}


class ResearchIntent:
    """Intent to research a topic (web search, knowledge retrieval)."""
    def __init__(
        self,
        query: str,
        max_results: int = 8,
        sources: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.query = query
        self.max_results = max_results
        self.sources = sources or ["duckduckgo", "wikipedia"]
        self.metadata = metadata or {}


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

class ImageResult:
    """The result of an image generation."""
    def __init__(
        self,
        asset: Asset,
        clip_score: float | None = None,
        backend: RenderBackend = RenderBackend.UNKNOWN,
    ):
        self.asset = asset
        self.clip_score = clip_score
        self.backend = backend


class VideoResult:
    """The result of a video generation."""
    def __init__(self, asset: Asset, duration_seconds: float = 0.0):
        self.asset = asset
        self.duration_seconds = duration_seconds


class VoiceResult:
    """The result of a voice synthesis."""
    def __init__(self, asset: Asset, duration_seconds: float = 0.0):
        self.asset = asset
        self.duration_seconds = duration_seconds


class MusicResult:
    """The result of a music generation."""
    def __init__(self, asset: Asset, duration_seconds: float = 0.0):
        self.asset = asset
        self.duration_seconds = duration_seconds


class StoryResult:
    """The result of a story generation."""
    def __init__(self, content: Any, task: str = ""):
        self.content = content
        self.task = task


class TranslationResult:
    """The result of a translation."""
    def __init__(self, translated_text: str, source_language: str, target_language: str):
        self.translated_text = translated_text
        self.source_language = source_language
        self.target_language = target_language


class ResearchResult:
    """The result of a research query."""
    def __init__(self, summary: str, sources: list[dict[str, Any]]):
        self.summary = summary
        self.sources = sources
