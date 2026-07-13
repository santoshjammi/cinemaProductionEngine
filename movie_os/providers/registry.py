"""Provider registry — the lookup table for (capability, label) → provider.

This is the registry the built-in `default_provider_factory` consults.
Each provider module registers a `make()` function here. Adding a new
provider means:
  1. Implement the provider class (subclassing the appropriate ABC)
  2. Define a `make(settings)` factory function
  3. Register it here

Public API:
    from movie_os.providers import registry

    # Register a provider
    registry.register("image", "flux_comfyui", make_flux_comfyui)

    # Build a provider from config
    provider = registry.make("image", "flux_comfyui", settings={}, cost=0.0)

    # List registered providers
    for entry in registry.list():
        print(entry)
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from movie_os.capabilities.base import (
    ImageIntent, VideoIntent, VoiceIntent, MusicIntent,
    StoryIntent, TranslationIntent, ResearchIntent,
)


logger = logging.getLogger("movie_os.providers.registry")


# The factory function signature: (settings: dict, cost_per_call_usd: float) -> Provider
# (We don't need capability/label here — those are the keys in the registry.)
ProviderMaker = Callable[[dict, float], Any]


# The registry: capability -> label -> maker
_providers: dict[str, dict[str, ProviderMaker]] = {}


def register(capability: str, label: str, maker: ProviderMaker) -> None:
    """Register a provider factory.

    Args:
        capability: "image", "video", "voice", "music", "story", etc.
        label: the provider's label (e.g., "sdxl_local", "flux_comfyui")
        maker: a function (settings, cost) -> provider_instance
    """
    if capability not in _providers:
        _providers[capability] = {}
    _providers[capability][label] = maker
    logger.info(f"Registered provider: {capability}.{label} -> {maker.__name__}")


def unregister(capability: str, label: str) -> None:
    """Remove a provider from the registry."""
    if capability in _providers and label in _providers[capability]:
        del _providers[capability][label]
        logger.info(f"Unregistered provider: {capability}.{label}")


def make(
    capability: str,
    label: str,
    settings: dict,
    cost_per_call_usd: float = 0.0,
) -> Any:
    """Build a provider instance from the registry.

    Returns None if the (capability, label) isn't registered.
    """
    if capability not in _providers:
        return None
    if label not in _providers[capability]:
        return None
    maker = _providers[capability][label]
    try:
        return maker(settings, cost_per_call_usd)
    except Exception as e:
        logger.error(f"Provider maker failed for {capability}.{label}: {e}")
        return None


def has(capability: str, label: str) -> bool:
    """Check if a (capability, label) is registered."""
    return capability in _providers and label in _providers[capability]


def list_providers(capability: str | None = None) -> list[dict]:
    """List registered providers.

    Args:
        capability: if given, only list providers for this capability.
            Otherwise, list all.

    Returns a list of {"capability": str, "label": str} dicts.
    """
    if capability:
        return [
            {"capability": capability, "label": label}
            for label in _providers.get(capability, {})
        ]
    return [
        {"capability": cap, "label": label}
        for cap, labels in _providers.items()
        for label in labels
    ]


def reset() -> None:
    """Clear the registry. Used for testing."""
    _providers.clear()


# ---------------------------------------------------------------------------
# Auto-registration — each provider module registers itself on import
# ---------------------------------------------------------------------------

def register_builtin_providers() -> None:
    """Register all the providers bundled with the Movie OS package.

    Called once when the providers package is first imported.
    Idempotent — safe to call multiple times.
    """
    if _providers:  # already registered
        return

    # Image providers
    try:
        from movie_os.providers.image.sdxl_local import make as make_sdxl
        register("image", "sdxl_local", make_sdxl)
    except Exception as e:
        logger.debug(f"sdxl_local provider not registered: {e}")

    try:
        from movie_os.providers.image.flux_comfyui import make as make_flux
        register("image", "flux_comfyui", make_flux)
    except Exception as e:
        logger.debug(f"flux_comfyui provider not registered: {e}")

    # Voice providers
    try:
        from movie_os.providers.voice.edge_tts import make as make_edge_tts
        register("voice", "edge_tts", make_edge_tts)
    except Exception as e:
        logger.debug(f"edge_tts provider not registered: {e}")

    # Music providers
    try:
        from movie_os.providers.music.procedural import make as make_music_proc
        register("music", "procedural", make_music_proc)
    except Exception as e:
        logger.debug(f"procedural music provider not registered: {e}")

    # SFX providers
    try:
        from movie_os.providers.sfx.procedural import make as make_sfx_proc
        register("sfx", "procedural", make_sfx_proc)
    except Exception as e:
        logger.debug(f"procedural sfx provider not registered: {e}")

    # Story providers
    try:
        from movie_os.providers.story.lmstudio import make as make_lmstudio
        register("story", "lmstudio", make_lmstudio)
    except Exception as e:
        logger.debug(f"lmstudio story provider not registered: {e}")
