"""Movie OS capabilities — the abstraction layer.

Public API:

    from movie_os.capabilities import (
        # Base
        Capability,
        # Registry
        CapabilityRegistry, CapabilityNotFoundError,
        get_default_registry, set_default_registry,
        # Intents and results
        ImageIntent, ImageResult,
        VideoIntent, VideoResult,
        VoiceIntent, VoiceResult,
        MusicIntent, MusicResult,
        SFXIntent, SFXResult,
        StoryIntent, StoryResult,
        TranslationIntent, TranslationResult,
        ResearchIntent, ResearchResult,
        # Capability classes (use these to register providers)
        ImageCapability,
        VideoCapability,
        VoiceCapability,
        MusicCapability,
        SFXCapability,
        StoryCapability,
        TranslationCapability,
        ResearchCapability,
    )

Typical usage:

    from movie_os.capabilities import (
        CapabilityRegistry, ImageCapability, ImageIntent,
    )
    from my_providers import SDXLLocalProvider, FluxComfyUIProvider

    registry = CapabilityRegistry()
    sdxl = SDXLLocalProvider()
    flux = FluxComfyUIProvider()
    image_cap = ImageCapability(provider=sdxl)
    image_cap_alt = ImageCapability(provider=flux)
    registry.register(image_cap, label="sdxl_local")
    registry.register(image_cap_alt, label="flux_comfyui")
    registry.set_default("image", "flux_comfyui")

    # Later, anywhere in the code:
    image_cap = registry.get("image")
    result = await image_cap.execute(ImageIntent(prompt="..."))
"""

from .base import (
    Capability,
    ImageCapabilityError,
    VideoCapabilityError,
    VoiceCapabilityError,
    MusicCapabilityError,
    SFXCapabilityError,
    StoryCapabilityError,
    TranslationCapabilityError,
    ResearchCapabilityError,
    # Intents
    ImageIntent, VideoIntent, VoiceIntent, MusicIntent, SFXIntent,
    StoryIntent, TranslationIntent, ResearchIntent,
    # Results
    ImageResult, VideoResult, VoiceResult, MusicResult, SFXResult,
    StoryResult, TranslationResult, ResearchResult,
)
from .registry import (
    CapabilityRegistry,
    CapabilityNotFoundError,
    get_default_registry,
    set_default_registry,
)
from .image import ImageCapability
from .video import VideoCapability
from .voice import VoiceCapability
from .music import MusicCapability
from .sfx import SFXCapability
from .story import StoryCapability
from .translation import TranslationCapability
from .research import ResearchCapability

__all__ = [
    # Base
    "Capability",
    # Errors
    "ImageCapabilityError", "VideoCapabilityError", "VoiceCapabilityError",
    "MusicCapabilityError", "SFXCapabilityError",
    "StoryCapabilityError", "TranslationCapabilityError",
    "ResearchCapabilityError",
    # Intents
    "ImageIntent", "VideoIntent", "VoiceIntent", "MusicIntent", "SFXIntent",
    "StoryIntent", "TranslationIntent", "ResearchIntent",
    # Results
    "ImageResult", "VideoResult", "VoiceResult", "MusicResult", "SFXResult",
    "StoryResult", "TranslationResult", "ResearchResult",
    # Registry
    "CapabilityRegistry", "CapabilityNotFoundError",
    "get_default_registry", "set_default_registry",
    # Capabilities
    "ImageCapability", "VideoCapability", "VoiceCapability",
    "MusicCapability", "SFXCapability", "StoryCapability",
    "TranslationCapability", "ResearchCapability",
]
