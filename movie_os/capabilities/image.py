"""ImageCapability — generates still images from a prompt.

This is the primary creative capability. The capability dispatches to
a registered ImageProvider (e.g., SDXLLocalProvider, FluxComfyUIProvider).
The provider chooses the model, the workflow, the references.

For Phase 0, the providers are stubs. The actual implementation comes
in Phase 4 (wrap existing) and Phase 5 (ComfyUI + FLUX).
"""

from __future__ import annotations

import logging
from typing import Any

from .base import (
    Capability,
    ImageCapabilityError,
    ImageIntent,
    ImageResult,
)


logger = logging.getLogger("movie_os.capabilities.image")


class ImageCapability(Capability[ImageIntent, ImageResult]):
    """Generate an image from a prompt + references.

    Providers that satisfy this capability:
      - SDXLLocalProvider  (local, free, current default)
      - FluxComfyUIProvider (Phase 5)
      - HiDreamProvider    (future)

    The capability doesn't know which provider is registered. It just
    dispatches via the registry.
    """

    name = "image"
    description = "Generate a still image from a prompt and optional references."
    version = "0.1.0"

    def __init__(self, provider: Any = None):
        """Initialize with an optional provider.

        If no provider is given, the capability will look up the
        default from the registry at execute time.
        """
        self._provider = provider

    @property
    def provider(self) -> Any:
        """The currently configured provider (may be looked up lazily)."""
        if self._provider is None:
            from .registry import get_default_registry
            registry = get_default_registry()
            # The provider is registered under a label like "image.sdxl_local"
            # We look it up via the default selection.
            if registry.has("image"):
                self._provider = registry.get("image")
        return self._provider

    def can_handle(self, intent: ImageIntent) -> bool:
        return bool(intent.prompt)

    async def execute(self, intent: ImageIntent) -> ImageResult:
        if not intent.prompt:
            raise ImageCapabilityError("ImageIntent.prompt is required")

        provider = self.provider
        if provider is None:
            raise ImageCapabilityError(
                "No image provider registered. Register one with "
                "registry.register(MyImageProvider()) before calling execute()."
            )

        logger.info(
            f"ImageCapability executing via {provider.__class__.__name__}: "
            f"{intent.width}x{intent.height}, quality={intent.quality}"
        )

        # Delegate to the provider
        if hasattr(provider, "render"):
            asset = await provider.render(intent)
        elif hasattr(provider, "generate"):
            asset = await provider.generate(intent)
        else:
            raise ImageCapabilityError(
                f"Provider {provider.__class__.__name__} has neither render() nor generate()"
            )

        clip_score = None
        if hasattr(asset, "metadata") and asset.metadata:
            clip_score = asset.metadata.get("clip_score")

        return ImageResult(
            asset=asset,
            clip_score=clip_score,
            backend=asset.backend if hasattr(asset, "backend") else None,
        )
