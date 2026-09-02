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

    Supports configurable model routing with bounded fallback escalation.
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
        phase_models: dict[str, str] | None = None,
        task_models: dict[str, str] | None = None,
        fallback_models: list[str] | None = None,
        max_fallback_attempts: int | None = None,
    ):
        if config is None:
            config = LLMConfig()
        if model is not None:
            config.model = model
        if temperature is not None:
            config.temperature = temperature
        if max_tokens is not None:
            config.max_tokens = max_tokens
        if timeout is not None:
            config.timeout = timeout
        if phase_models is not None:
            config.phase_models = phase_models
        if task_models is not None:
            config.task_models = task_models
        if fallback_models is not None:
            config.fallback_models = fallback_models
        if max_fallback_attempts is not None:
            config.max_fallback_attempts = max_fallback_attempts

        self._config = config
        self._provider: LLMProvider | None = None
        self._reviewer_model = reviewer_model
        self._validator_model = validator_model
        self.call_history: list[dict[str, Any]] = []
        logger.info(
            "MODEL ROUTING default=%s reviewer=%s validator=%s phases=%s tasks=%s fallbacks=%s",
            self._config.model,
            self._reviewer_model or self._config.model,
            self._validator_model or self._config.model,
            self._config.phase_models,
            self._config.task_models,
            self._config.fallback_models,
        )

    def _get_provider(self) -> LLMProvider:
        if self._provider is None:
            self._provider = create_llm(self._config)
        return self._provider

    def _resolve_model(self, tier: str = "planner", phase_name: str | None = None, task_key: str | None = None) -> str:
        if task_key and task_key in self._config.task_models:
            return self._config.task_models[task_key]
        if phase_name and phase_name in self._config.phase_models:
            return self._config.phase_models[phase_name]
        if tier == "reviewer" and self._reviewer_model:
            return self._reviewer_model
        if tier == "validator" and self._validator_model:
            return self._validator_model
        return self._config.model

    def _attempt_models(self, tier: str, phase_name: str | None = None, task_key: str | None = None) -> list[str]:
        primary = self._resolve_model(tier=tier, phase_name=phase_name, task_key=task_key)
        attempts = [primary]
        for model in self._config.fallback_models[: max(0, int(self._config.max_fallback_attempts))]:
            if model and model not in attempts:
                attempts.append(model)
        return attempts

    def generate(
        self,
        prompt: str,
        tier: str = "planner",
        phase_name: str | None = None,
        task_key: str | None = None,
        *,
        response_format: Any | None = None,
    ) -> str:
        provider = self._get_provider()
        last_exc: Exception | None = None
        models = self._attempt_models(tier=tier, phase_name=phase_name, task_key=task_key)
        for attempt, model in enumerate(models, start=1):
            tier_config = LLMConfig(
                provider=self._config.provider,
                model=model,
                temperature=self._config.temperature,
                max_tokens=self._config.max_tokens,
                timeout=self._config.timeout,
                url=self._config.url,
                ollama_url=self._config.ollama_url,
                num_ctx=self._config.num_ctx,
                think=self._config.think,
            )
            tier_config.phase_models = dict(self._config.phase_models)
            tier_config.task_models = dict(self._config.task_models)
            tier_config.fallback_models = list(self._config.fallback_models)
            tier_config.max_fallback_attempts = self._config.max_fallback_attempts
            try:
                started = __import__("time").time()
                response = provider.generate(prompt, tier_config, response_format=response_format)
                duration_ms = int((__import__("time").time() - started) * 1000)
                self.call_history.append({
                    "model": model,
                    "phase": phase_name or tier,
                    "target_unit": task_key or phase_name or tier,
                    "context_sources": [],
                    "estimated_input_tokens": max(1, len(prompt) // 4),
                    "output_tokens": max(1, len(response) // 4),
                    "duration_ms": duration_ms,
                    "retries": attempt - 1,
                    "outcome": "pass" if attempt == 1 else "fallback_pass",
                })
                return response
            except Exception as exc:
                last_exc = exc
                self.call_history.append({
                    "model": model,
                    "phase": phase_name or tier,
                    "target_unit": task_key or phase_name or tier,
                    "context_sources": [],
                    "estimated_input_tokens": max(1, len(prompt) // 4),
                    "output_tokens": 0,
                    "duration_ms": 0,
                    "retries": attempt - 1,
                    "outcome": "retry" if attempt < len(models) else "fail",
                    "error": str(exc),
                })
                if attempt >= len(models):
                    raise
        assert last_exc is not None
        raise last_exc

    def generate_json(
        self,
        prompt: str,
        tier: str = "planner",
        phase_name: str | None = None,
        task_key: str | None = None,
        *,
        response_format: Any | None = None,
    ) -> dict[str, Any]:
        response = self.generate(prompt, tier=tier, phase_name=phase_name, task_key=task_key, response_format=response_format)
        from .llm_providers import _extract_json
        return _extract_json(response)

    def is_available(self) -> bool:
        return self._get_provider().is_available()


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

    def generate(self, prompt: str, config: LLMConfig | None = None, tier: str = "planner", phase_name: str | None = None, task_key: str | None = None, *args, **kwargs) -> str:
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

    def generate_json(self, prompt: str, config: LLMConfig | None = None, tier: str = "planner", *args, **kwargs) -> dict[str, Any]:
        """Return a canned JSON response (ignores tier and extra kwargs)."""
        return super().generate_json(prompt, config)


# Re-export _extract_json for backward compatibility
from .llm_providers import _extract_json  # noqa: E402, F401
