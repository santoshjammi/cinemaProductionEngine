"""Movie OS Providers — concrete plug-in implementations.

This package holds the implementations of the Provider ABCs. Each
provider is a real backend (SDXL local, edge-tts, LMStudio, etc.)
that satisfies the contract defined in `movie_os.capabilities`.

Public API:
    from movie_os.providers import (
        # ABCs
        ImageProvider, VideoProvider, VoiceProvider, MusicProvider,
        SFXProvider, StoryProvider, TranslationProvider, ResearchProvider,
        # Concrete implementations
        SDXLLocalProvider,
        EdgeTTSProvider,
        ProceduralMusicProvider,
        ProceduralSFXProvider,
        LMStudioStoryProvider,
        # Helpers
        make_asset, run_sync,
        # Built-in factory
        default_provider_factory,
    )

    # Register all built-in providers
    from movie_os.providers import registry
    registry.register_builtin_providers()
"""

from .base import (
    ImageProvider, VideoProvider, VoiceProvider, MusicProvider,
    SFXProvider, StoryProvider, TranslationProvider, ResearchProvider,
    ProviderFactory, default_provider_factory, make_asset, run_sync,
)
from . import registry

# Auto-register built-in providers on import
registry.register_builtin_providers()

# Re-export concrete provider classes for convenience
from .image.sdxl_local import SDXLLocalProvider
from .image.flux_comfyui import FluxComfyUIProvider
from .voice.edge_tts import EdgeTTSProvider
from .music.procedural import ProceduralMusicProvider
from .sfx.procedural import ProceduralSFXProvider
from .story.lmstudio import LMStudioStoryProvider

__all__ = [
    # ABCs
    "ImageProvider", "VideoProvider", "VoiceProvider", "MusicProvider",
    "SFXProvider", "StoryProvider", "TranslationProvider", "ResearchProvider",
    # Concrete providers
    "SDXLLocalProvider", "FluxComfyUIProvider", "EdgeTTSProvider",
    "ProceduralMusicProvider", "ProceduralSFXProvider",
    "LMStudioStoryProvider",
    # Helpers
    "ProviderFactory", "default_provider_factory", "make_asset", "run_sync",
    "registry",
]
