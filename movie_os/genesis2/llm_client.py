"""LLM Client for Genesis2 — unified interface using the new provider system.

Wraps LLMFactory to provide the same interface as the old LLMClient,
with auto-detection of available backends (Ollama → Mock).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .llm_factory import LLMFactory, create_llm
from .llm_providers import LLMConfig, LLMProvider, MockLLMProvider

logger = logging.getLogger("movie_os.genesis2.llm")


class LLMClient:
    """Unified LLM client for Genesis2 phases.

    Uses LLMFactory for provider creation with auto-detection:
    - Tries Ollama server first
    - Falls back to Ollama at http://localhost:11434
    - Falls back to MockLLMProvider if neither is available

    Supports model tier routing: different models for planner, reviewer,
    spec_generator, validator, and integrator roles.
    """

    def __init__(
        self,
        config: LLMConfig | None = None,
        model: str | None = None,
        reviewer_model: str | None = None,
        validator_model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        timeout: int | None = None,
    ):
        """Initialize the LLM client.

        Args:
            config: LLMConfig for provider selection and settings.
            model: Override model name (planner tier).
            reviewer_model: Override model for reviewer tier.
            validator_model: Override model for validator tier.
            temperature: Override temperature.
            max_tokens: Override max tokens.
            timeout: Override timeout in seconds.
        """
        if config is None:
            config = LLMConfig()

        # Apply overrides
        if model is not None:
            config.model = model
        if temperature is not None:
            config.temperature = temperature
        if max_tokens is not None:
            config.max_tokens = max_tokens
        if timeout is not None:
            config.timeout = timeout

        self._config = config
        self._provider: LLMProvider | None = None
        self._reviewer_model = reviewer_model
        self._validator_model = validator_model

    def _get_provider(self) -> LLMProvider:
        """Get or create the LLM provider (lazy initialization)."""
        if self._provider is None:
            self._provider = create_llm(self._config)
        return self._provider

    def generate(self, prompt: str, tier: str = "planner") -> str:
        """Generate a response, optionally using a different model per tier.

        Tier routing:
        - planner: uses self._config.model
        - reviewer: uses reviewer_model if set, else model
        - spec_generator: uses self._config.model
        - validator: uses validator_model if set, else model
        - integrator: uses self._config.model
        """
        provider = self._get_provider()

        # Build config with appropriate model for tier
        tier_config = LLMConfig(
            provider=self._config.provider,
            model=self._config.model,
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens,
            timeout=self._config.timeout,
            url=self._config.url,
            ollama_url=self._config.ollama_url,
            num_ctx=self._config.num_ctx,
        )

        if tier == "reviewer" and self._reviewer_model:
            tier_config.model = self._reviewer_model
        elif tier == "validator" and self._validator_model:
            tier_config.model = self._validator_model

        return provider.generate(prompt, tier_config)

    def generate_json(self, prompt: str, tier: str = "planner") -> dict[str, Any]:
        """Generate and parse JSON response."""
        response = self.generate(prompt, tier)
        from .llm_providers import _extract_json
        return _extract_json(response)

    def is_available(self) -> bool:
        """Check if any LLM backend is available."""
        provider = self._get_provider()
        return provider.is_available()


class MockLLMClient(MockLLMProvider):
    """Mock LLM client for testing Genesis2 phases.

    Extends MockLLMProvider to maintain the same interface as the old
    MockLLMClient (with tier parameter on generate).
    """

    def __init__(self, responses: dict[str, str] | None = None):
        super().__init__(responses)
        self._default = json.dumps({
            "purpose": "mock purpose",
            "creative_intent": "mock intent",
            "reasoning": "mock reasoning",
            "confidence": "confirmed",
            "theme": "mock theme",
            "genre": "Drama",
            "mood": "neutral",
            "core_question": "What matters?",
            "audience": "adults",
            "success_criteria": ["truth"],
            "scenes": [{"purpose": "establish", "scene_number": 1}],
            "dialogues": [{"speaker": "John", "text": "Hello", "purpose": "character_reveal"}],
            "color_palette": "muted blues",
            "visual_motifs": ["mirrors"],
            "lighting_scheme": "low key",
            "package": {"integrated": True, "summary": "All phases complete"},
        })

    def generate(self, prompt: str, config: LLMConfig | None = None, tier: str = "planner") -> str:
        """Return a canned response (ignores tier, same as old behavior)."""
        self._call_log.append(prompt[:100])
        for key, response in self._responses.items():
            if key.lower() in prompt.lower():
                return response
        # Phase-specific defaults based on prompt content
        if "Phase 03" in prompt or "Character Psychology" in prompt:
            return json.dumps({
                "purpose": "mock purpose", "creative_intent": "mock intent", "reasoning": "mock reasoning",
                "confidence": "confirmed",
                "protagonist": {"name": "John", "identity": "a man", "goals": ["find truth"]},
                "antagonist": None, "supporting_characters": [],
            })
        if "Phase 06" in prompt or "Scene Planning" in prompt:
            return json.dumps({
                "purpose": "mock purpose", "creative_intent": "mock intent", "reasoning": "mock reasoning",
                "confidence": "confirmed",
                "scenes": [{"purpose": "establish", "scene_number": 1, "conflict": "none", "emotion": "neutral"}],
            })
        if "Phase 07" in prompt or "Dialogue Planning" in prompt:
            return json.dumps({
                "purpose": "mock purpose", "creative_intent": "mock intent", "reasoning": "mock reasoning",
                "confidence": "confirmed",
                "dialogues": [{"speaker": "John", "text": "Hello", "purpose": "character_reveal", "conversation_intent": "reveal"}],
            })
        if "Phase 08" in prompt or "Visual Language" in prompt:
            return json.dumps({
                "purpose": "mock purpose", "creative_intent": "mock intent", "reasoning": "mock reasoning",
                "confidence": "confirmed",
                "color": "muted blues and warm ambers",
                "visual_motifs": ["mirrors", "rain"],
                "lighting_scheme": "low key with highlights",
            })
        if "Phase 10" in prompt or "Validation" in prompt:
            return json.dumps({
                "purpose": "mock purpose", "creative_intent": "mock intent", "reasoning": "mock reasoning",
                "confidence": "confirmed",
                "validation_results": {"passed": True, "issues": []},
                "cross_phase_issues": [],
            })
        if "Phase 11" in prompt or "Creative Critique" in prompt:
            return json.dumps({
                "purpose": "mock purpose", "creative_intent": "mock intent", "reasoning": "mock reasoning",
                "confidence": "confirmed",
                "critique_summary": "Strong foundation",
                "improvement_areas": ["pacing"],
            })
        if "Phase 12" in prompt or "Knowledge Integration" in prompt:
            if "Critique the following" in prompt:
                return json.dumps({"findings": [{"question": "Is the knowledge integrated?", "answer": "Yes", "severity": "minor", "recommendation": "None"}]})
            return json.dumps({
                "purpose": "mock purpose", "creative_intent": "mock intent", "reasoning": "mock reasoning",
                "confidence": "confirmed",
                "package": {"integrated": True, "summary": "All phases complete"},
            })
        return self._default

    def generate_json(self, prompt: str, config: LLMConfig | None = None, tier: str = "planner") -> dict[str, Any]:
        """Return a canned JSON response (ignores tier, same as old behavior)."""
        return super().generate_json(prompt, config)


# Re-export _extract_json for backward compatibility
from .llm_providers import _extract_json  # noqa: E402, F401
