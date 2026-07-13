"""Provider base classes — the plug-in contract for every AI backend.

A Provider is the concrete implementation of a Capability. Where a
Capability asks "generate an image" without caring about the model,
a Provider is the actual code that talks to SDXL or FLUX or Stable
Video Diffusion.

Design principles:
  - Provider ABCs are the contracts. Implementations satisfy them.
  - Providers take their config in __init__, not in render(). This
    way one provider instance can be reused across many calls.
  - Providers return Asset (or StoryResult for story) on success,
    raise on failure. No silent failures.
  - Providers are async (because the Capability is async), but the
    underlying work can be sync — wrap with asyncio.to_thread if needed.

Adding a new provider:
  1. Subclass the appropriate ABC (ImageProvider, VoiceProvider, etc.)
  2. Implement the render() method
  3. Add a `make(settings)` factory function in the same module
  4. Register the factory in the built-in provider factory
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable

from movie_os.capabilities.base import (
    ImageIntent, ImageResult,
    VideoIntent, VideoResult,
    VoiceIntent, VoiceResult,
    MusicIntent, MusicResult,
    StoryIntent, StoryResult,
    TranslationIntent, TranslationResult,
    ResearchIntent, ResearchResult,
)
from movie_os.domain.asset import Asset, AssetType, AssetStatus, RenderBackend


logger = logging.getLogger("movie_os.providers.base")


# ---------------------------------------------------------------------------
# Provider ABCs
# ---------------------------------------------------------------------------

class ImageProvider(ABC):
    """Contract for an image generation backend.

    Implementations: SDXLLocalProvider, FluxComfyUIProvider, HiDreamProvider
    (future). Each takes its config in __init__ and exposes render()
    for the actual work.
    """

    name: str = ""                                    # the canonical provider name
    backend: RenderBackend = RenderBackend.UNKNOWN

    @abstractmethod
    async def render(self, intent: ImageIntent) -> Asset:
        """Render an image from the intent. Returns the Asset (with path)."""
        ...

    def can_handle(self, intent: ImageIntent) -> bool:
        """Whether this provider accepts the intent. Default: always."""
        return True


class VideoProvider(ABC):
    """Contract for a video generation backend (image-to-video)."""

    name: str = ""
    backend: RenderBackend = RenderBackend.UNKNOWN

    @abstractmethod
    async def render(self, intent: VideoIntent) -> Asset:
        ...

    def can_handle(self, intent: VideoIntent) -> bool:
        return True


class VoiceProvider(ABC):
    """Contract for a TTS backend."""

    name: str = ""
    backend: RenderBackend = RenderBackend.UNKNOWN

    @abstractmethod
    async def render(self, intent: VoiceIntent) -> Asset:
        ...

    def can_handle(self, intent: VoiceIntent) -> bool:
        return True


class MusicProvider(ABC):
    """Contract for a music generation backend."""

    name: str = ""
    backend: RenderBackend = RenderBackend.UNKNOWN

    @abstractmethod
    async def render(self, intent: MusicIntent) -> Asset:
        ...

    def can_handle(self, intent: MusicIntent) -> bool:
        return True


class SFXProvider(ABC):
    """Contract for an SFX / ambient sound generation backend.

    SFX is technically a sub-capability of audio. The intent is
    similar to MusicIntent but with different defaults.
    """

    name: str = ""
    backend: RenderBackend = RenderBackend.UNKNOWN

    @abstractmethod
    async def render(self, intent: Any) -> Asset:
        ...

    def can_handle(self, intent: Any) -> bool:
        return True


class StoryProvider(ABC):
    """Contract for a story generation LLM backend."""

    name: str = ""
    backend: RenderBackend = RenderBackend.UNKNOWN

    @abstractmethod
    async def render(self, intent: StoryIntent) -> StoryResult:
        """Render story content. Returns a StoryResult (not an Asset)."""
        ...

    def can_handle(self, intent: StoryIntent) -> bool:
        return True


class TranslationProvider(ABC):
    """Contract for a translation backend."""

    name: str = ""
    backend: RenderBackend = RenderBackend.UNKNOWN

    @abstractmethod
    async def render(self, intent: TranslationIntent) -> TranslationResult:
        ...

    def can_handle(self, intent: TranslationIntent) -> bool:
        return True


class ResearchProvider(ABC):
    """Contract for a research backend (web search, knowledge retrieval)."""

    name: str = ""
    backend: RenderBackend = RenderBackend.UNKNOWN

    @abstractmethod
    async def render(self, intent: ResearchIntent) -> ResearchResult:
        ...

    def can_handle(self, intent: ResearchIntent) -> bool:
        return True


# ---------------------------------------------------------------------------
# ProviderFactory — builds providers from config
# ---------------------------------------------------------------------------

# A factory function takes (capability, label, settings, cost) and
# returns a provider instance. Used by the registry.
ProviderFactory = Callable[[str, str, dict, float], Any]


def default_provider_factory(
    capability: str,
    label: str,
    settings: dict,
    cost_per_call_usd: float,
) -> Any:
    """The built-in provider factory.

    Knows about all the providers bundled with the Movie OS package.
    Returns None if the (capability, label) isn't recognized.
    """
    from movie_os.providers import registry as provider_registry
    return provider_registry.make(capability, label, settings, cost_per_call_usd)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_asset(
    path: Any,
    asset_type: AssetType,
    backend: RenderBackend,
    *,
    seed: int | None = None,
    clip_score: float | None = None,
    metadata: dict | None = None,
    duration_seconds: float | None = None,
) -> Asset:
    """Helper to construct an Asset from a successful render."""
    from pathlib import Path
    asset = Asset(
        type=asset_type,
        status=AssetStatus.COMPLETED,
        path=Path(path) if path else None,
        backend=backend,
        seed=seed,
        clip_score=clip_score,
        metadata=metadata or {},
        duration_seconds=duration_seconds,
    )
    return asset


async def run_sync(func, *args, **kwargs):
    """Run a sync function in a thread, await the result.

    Use this when wrapping a sync provider implementation in an
    async ABC.
    """
    return await asyncio.to_thread(func, *args, **kwargs)
