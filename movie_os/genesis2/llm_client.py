"""LLM Client for Genesis2 — reuses the existing genesis LLM infrastructure."""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger("movie_os.genesis2.llm")


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from an LLM response. Reuses the legacy implementation."""
    from movie_os.genesis.llm_client import LLMClient as LegacyClient
    return LegacyClient._extract_json(text)


class LLMClient:
    """LLM client that wraps the existing genesis Ollama client.

    Supports model tier routing: different models for planner, reviewer,
    spec_generator, validator, and integrator roles.
    """

    def __init__(
        self,
        model: str = "qwen2.5:32b",
        reviewer_model: str | None = None,
        validator_model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 120.0,
    ):
        self.model = model
        self.reviewer_model = reviewer_model or model
        self.validator_model = validator_model or model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._clients: dict[str, Any] = {}

    def _get_client(self, model: str | None = None):
        """Lazy-import and create the underlying Ollama client for a specific model."""
        model_key = model or self.model
        if model_key not in self._clients:
            try:
                from movie_os.genesis.llm_ollama import OllamaClient
                self._clients[model_key] = OllamaClient(
                    model=model_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                )
            except ImportError:
                from movie_os.genesis.llm_client import MockLLMClient
                self._clients[model_key] = MockLLMClient()
        return self._clients[model_key]

    def generate(self, prompt: str, tier: str = "planner") -> str:
        """Generate a response, optionally using a different model per tier.

        Tier routing:
        - planner: uses self.model (Qwen, thinking ON)
        - reviewer: uses self.reviewer_model (Gemma, thinking ON)
        - spec_generator: uses self.model (Qwen, thinking OFF)
        - validator: uses self.validator_model (Gemma, thinking OFF)
        - integrator: uses self.model (Qwen, thinking OFF)
        """
        model_map = {
            "planner": self.model,
            "reviewer": self.reviewer_model,
            "spec_generator": self.model,
            "validator": self.validator_model,
            "integrator": self.model,
        }
        model = model_map.get(tier, self.model)
        client = self._get_client(model)
        return client.generate(prompt)

    def generate_json(self, prompt: str, tier: str = "planner") -> dict[str, Any]:
        """Generate and parse JSON response."""
        response = self.generate(prompt, tier)
        return _extract_json(response)


class MockLLMClient:
    """Mock LLM client for testing Genesis2 phases."""

    def __init__(self, responses: dict[str, str] | None = None):
        self._responses = responses or {}
        self._default = '{"purpose": "mock", "creative_intent": "mock", "reasoning": "mock", "confidence": "inferred"}'

    def set_response(self, key: str, response: str) -> None:
        self._responses[key] = response

    def set_default(self, response: str) -> None:
        self._default = response

    def generate(self, prompt: str, tier: str = "planner") -> str:
        for key, response in self._responses.items():
            if key.lower() in prompt.lower():
                return response
        return self._default

    def generate_json(self, prompt: str, tier: str = "planner") -> dict[str, Any]:
        response = self.generate(prompt, tier)
        return _extract_json(response)
