"""LLM Factory — creates the right LLM provider based on config.

Supports:
- Explicit provider selection (ollama, mock)
- Auto-detect: tries Ollama first, falls back to mock
- Drop-in replacement for MockLLMClient
"""

from __future__ import annotations

import logging
from typing import Any

from .llm_providers import (
    LLMConfig,
    LLMProvider,
    OllamaProvider,
    MockLLMProvider,
)

logger = logging.getLogger("movie_os.genesis2.llm_factory")


class LLMFactory:
    """Factory for creating LLM providers."""

    @classmethod
    def create(cls, config: LLMConfig | None = None) -> LLMProvider:
        """Create an LLM provider based on config.

        Args:
            config: LLM configuration. If None, uses defaults (Ollama provider).

        Returns:
            An LLMProvider instance.
        """
        cfg = config or LLMConfig()

        if cfg.provider == "ollama":
            return OllamaProvider(
                model=cfg.model,
                url=cfg.ollama_url,
                timeout=cfg.timeout,
            )
        elif cfg.provider == "huggingface":
            # HF provider not yet implemented — fall back to mock
            logger.warning("HuggingFace provider not yet implemented, using mock")
            return MockLLMProvider()
        else:
            return MockLLMProvider()

    @classmethod
    def create_auto(cls, config: LLMConfig | None = None) -> LLMProvider:
        """Create an LLM provider with auto-detection.

        Tries Ollama first, then falls back to mock.

        Args:
            config: LLM configuration. If None, uses defaults.

        Returns:
            An LLMProvider instance (best available).
        """
        cfg = config or LLMConfig()

        # Try Ollama first
        try:
            ollama = OllamaProvider(
                model=cfg.model,
                url=cfg.ollama_url or cfg.url,
                timeout=cfg.timeout,
            )
            if ollama.is_available():
                logger.info("Auto-detect: Ollama available at %s", cfg.ollama_url or cfg.url)
                return ollama
        except Exception as e:
            logger.debug("Ollama check failed: %s", e)

        # Fall back to mock
        logger.warning("Auto-detect: No backend available, using mock")
        return MockLLMProvider()

    @classmethod
    def create_from_config(cls, config: LLMConfig | None = None) -> LLMProvider:
        """Create an LLM provider — explicit if provider is set, auto-detect otherwise.

        This is the main entry point for the pipeline.
        """
        cfg = config or LLMConfig()
        if cfg.provider == "auto":
            return cls.create_auto(cfg)
        return cls.create(cfg)


# Convenience function for direct use
def create_llm(config: LLMConfig | None = None) -> LLMProvider:
    """Create an LLM provider with auto-detection.

    This is the recommended entry point for the GENESIS pipeline.
    """
    return LLMFactory.create_from_config(config)
