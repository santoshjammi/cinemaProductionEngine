"""CapabilityRegistry — the central dispatcher.

The pipeline doesn't know about specific providers. It asks the
registry: "give me the image capability". The registry returns
whichever provider is currently selected (by config or default).

Adding a new provider = register it. Removing = unregister. Swapping
= change the config selection, no code change.

Usage:

    from movie_os.capabilities import CapabilityRegistry, ImageCapability
    from movie_os.providers.image.sdxl_local import SDXLLocalProvider

    # In-code registration
    registry = CapabilityRegistry()
    registry.register(SDXLLocalProvider())

    # Or via config
    registry = CapabilityRegistry.from_config("config/providers.yaml")

    # Use a capability
    image_cap = registry.get("image")
    result = await image_cap.execute(intent)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Optional

import yaml

from .base import Capability


logger = logging.getLogger("movie_os.capabilities.registry")


# A ProviderFactory takes (capability, label, settings, cost) and returns
# a Provider instance (or None if it can't instantiate one).
ProviderFactory = Callable[[str, str, dict, float], Any]


class CapabilityNotFoundError(KeyError):
    """Raised when a requested capability is not in the registry."""
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name


class CapabilityRegistry:
    """The central registry of capabilities.

    Capabilities are registered either:
      - In code: `registry.register(MyProvider())`
      - From config: `CapabilityRegistry.from_config("providers.yaml")`
    """

    def __init__(self):
        self._capabilities: dict[str, Capability] = {}
        self._default_selection: dict[str, str] = {}  # capability_name -> provider_name
        self._provider_labels: dict[str, str] = {}     # "capability.provider" -> label

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, capability: Capability, label: str | None = None) -> None:
        """Register a capability.

        If a capability with this name already exists, the new one
        replaces it. If `label` is given, it's stored for config-driven
        selection later.
        """
        name = capability.name
        if not name:
            raise ValueError("Capability.name must be set")
        self._capabilities[name] = capability
        if label:
            full_label = f"{name}.{label}"
            self._provider_labels[full_label] = label
        logger.info(f"Registered capability: {name} ({capability.__class__.__name__})")

    def unregister(self, name: str) -> None:
        """Remove a capability from the registry."""
        if name in self._capabilities:
            del self._capabilities[name]
            logger.info(f"Unregistered capability: {name}")

    def set_default(self, capability_name: str, provider_label: str = "default") -> None:
        """Set the default provider for a capability."""
        if capability_name not in self._capabilities:
            raise CapabilityNotFoundError(capability_name)
        self._default_selection[capability_name] = provider_label

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def get(self, name: str) -> Capability:
        """Get a capability by name.

        Raises CapabilityNotFoundError if the capability is not registered.
        """
        if name not in self._capabilities:
            raise CapabilityNotFoundError(name)
        return self._capabilities[name]

    def try_get(self, name: str) -> Optional[Capability]:
        """Get a capability by name, or None if not registered."""
        return self._capabilities.get(name)

    def has(self, name: str) -> bool:
        """Check if a capability is registered."""
        return name in self._capabilities

    def list(self) -> list[str]:
        """List all registered capability names."""
        return sorted(self._capabilities.keys())

    def all(self) -> dict[str, Capability]:
        """Get all capabilities as a dict."""
        return dict(self._capabilities)

    def info(self) -> list[dict[str, Any]]:
        """Get info about all registered capabilities."""
        return [
            {
                "name": cap.name,
                "class": cap.__class__.__name__,
                "description": cap.description,
                "version": cap.version,
            }
            for cap in self._capabilities.values()
        ]

    # ------------------------------------------------------------------
    # Config-driven construction
    # ------------------------------------------------------------------

    @classmethod
    def from_config(
        cls,
        config: Any,
        provider_factory: Optional["ProviderFactory"] = None,
    ) -> "CapabilityRegistry":
        """Build a registry from a MovieOSConfig.

        Args:
            config: A MovieOSConfig object (or a path to a config file —
                if a string/Path is passed, it will be loaded first).
            provider_factory: An optional callable that takes
                (capability_name, provider_label, provider_settings) and
                returns a Provider instance. If None, the registry
                registers the capability stubs without a provider
                (useful for Phase 0 — Phase 4+ will pass a real factory).

        Returns:
            A populated CapabilityRegistry.

        Note:
            In Phase 0, providers don't exist yet. This method:
              1. Reads the config's default selection per capability
              2. Registers a stub capability for each enabled capability
              3. If provider_factory is given, instantiates providers
                 and assigns them to the capabilities
            Phase 4+ will add a real ProviderFactory that knows how to
            import and instantiate the concrete provider classes.
        """
        # Lazy import to avoid circular dependency
        from movie_os.config import load_config, MovieOSConfig

        if isinstance(config, (str, Path)):
            config = load_config(config)
        elif isinstance(config, dict):
            config = load_config_from_dict(config) if False else MovieOSConfig.model_validate(config)
        elif not isinstance(config, MovieOSConfig):
            raise TypeError(
                f"config must be a MovieOSConfig, dict, or path. Got {type(config)}"
            )

        registry = cls()

        # Lazy imports to avoid circular dependency
        from .image import ImageCapability
        from .video import VideoCapability
        from .voice import VoiceCapability
        from .music import MusicCapability
        from .sfx import SFXCapability
        from .story import StoryCapability
        from .translation import TranslationCapability
        from .research import ResearchCapability

        capability_classes = {
            "image": ImageCapability,
            "video": VideoCapability,
            "voice": VoiceCapability,
            "music": MusicCapability,
            "sfx": SFXCapability,
            "story": StoryCapability,
            "translation": TranslationCapability,
            "research": ResearchCapability,
        }

        for cap_name, cap_class in capability_classes.items():
            # Check if the capability is enabled
            cap_cfg = getattr(config.capabilities, cap_name, None)
            if cap_cfg is None or not cap_cfg.enabled:
                logger.info(f"Capability '{cap_name}' is disabled — skipping")
                continue

            # Get the default provider
            default = config.provider_for(cap_name)
            if default is None:
                logger.info(
                    f"No provider configured for '{cap_name}' — "
                    f"registering capability stub without provider"
                )
                registry.register(cap_class(), label="stub")
                continue

            label, provider_option = default
            if not provider_option.enabled:
                logger.info(
                    f"Default provider '{label}' for '{cap_name}' is disabled — "
                    f"registering capability stub without provider"
                )
                registry.register(cap_class(), label="stub")
                continue

            # Try to instantiate the provider via the factory
            provider = None
            if provider_factory is not None:
                try:
                    provider = provider_factory(
                        capability=cap_name,
                        label=label,
                        settings=provider_option.settings,
                        cost_per_call_usd=provider_option.cost_per_call_usd,
                    )
                except Exception as e:
                    logger.warning(
                        f"Provider factory failed for '{cap_name}:{label}': {e}. "
                        f"Registering capability without provider."
                    )

            # Register the capability (with or without a real provider)
            cap_instance = cap_class(provider=provider)
            registry.register(cap_instance, label=label)
            registry.set_default(cap_name, label)

        return registry

    def __repr__(self) -> str:
        caps = ", ".join(self.list())
        return f"CapabilityRegistry([{caps}])"


# Global default registry — for simple use cases
_default_registry: CapabilityRegistry | None = None


def get_default_registry() -> CapabilityRegistry:
    """Get the global default registry, creating it on first call."""
    global _default_registry
    if _default_registry is None:
        _default_registry = CapabilityRegistry()
    return _default_registry


def set_default_registry(registry: CapabilityRegistry) -> None:
    """Set the global default registry (useful for testing)."""
    global _default_registry
    _default_registry = registry
