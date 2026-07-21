"""HuggingFace LLM Client — runs local HF models via transformers.

Supports tiered model routing: different models for discovery, PKP,
reviewer, and chief architect agents. Loads models on first use per tier.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from .llm_client import LLMClient

logger = logging.getLogger("movie_os.genesis.llm_hf")


class HFClient(LLMClient):
    """LLM client that runs HuggingFace models locally via transformers.

    Models are loaded lazily per tier and cached for reuse.
    """

    def __init__(
        self,
        models: dict[str, str] | None = None,
        device: str = "auto",
        load_in_8bit: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 120.0,
    ):
        self.models = models or {
            "discovery": "Qwen/Qwen2.5-1.5B-Instruct",
            "pkp": "Qwen/Qwen2.5-7B-Instruct",
            "reviewer": "Qwen/Qwen2.5-14B-Instruct",
            "chief": "Qwen/Qwen2.5-14B-Instruct",
        }
        self.device = device
        self.load_in_8bit = load_in_8bit
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._pipelines: dict[str, Any] = {}

    def _get_pipeline(self, tier: str):
        """Lazy-load a pipeline for the given tier."""
        if tier not in self._pipelines:
            model_name = self.models.get(tier)
            if not model_name:
                raise RuntimeError(f"No model configured for tier '{tier}'")
            self._pipelines[tier] = self._load_model(model_name)
        return self._pipelines[tier]

    def _load_model(self, model_name: str):
        """Load a transformers pipeline for the given model."""
        from transformers import pipeline as hf_pipeline

        device = self.device
        if device == "auto":
            import torch
            device = 0 if torch.cuda.is_available() else -1

        logger.info("Loading HF model: %s (device=%s)", model_name, device)
        pipe = hf_pipeline(
            "text-generation",
            model=model_name,
            device=device,
            torch_dtype="auto",
            model_kwargs={"load_in_8bit": self.load_in_8bit} if self.load_in_8bit else {},
        )
        return pipe

    def generate(self, prompt: str, system: str = "") -> str:
        """Generate a response using the default (pkp) model."""
        return self.generate_for_tier(prompt, system, "pkp")

    def generate_for_tier(self, prompt: str, system: str, tier: str) -> str:
        """Generate a response using the model for a specific tier."""
        pipe = self._get_pipeline(tier)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        result = pipe(
            messages,
            max_new_tokens=self.max_tokens,
            temperature=self.temperature,
            do_sample=True,
            return_full_text=False,
        )
        return result[0]["generated_text"].strip()

    def generate_json(self, prompt: str, system: str = "") -> dict[str, Any]:
        """Generate and parse JSON using the default model."""
        response = self.generate(prompt, system)
        return self._extract_json(response)

    def generate_json_for_tier(self, prompt: str, system: str, tier: str) -> dict[str, Any]:
        """Generate and parse JSON using a specific tier's model."""
        response = self.generate_for_tier(prompt, system, tier)
        return self._extract_json(response)

    def is_available(self) -> bool:
        """Check if transformers is importable."""
        try:
            import transformers
            return True
        except ImportError:
            return False
