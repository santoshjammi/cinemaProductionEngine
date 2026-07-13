"""Movie OS v1 — Shared LLM client for all creative agents.

Provides a unified interface to local LLMs (Ollama) with:
- Model selection and fallback
- Prompt templating
- Retry logic
- Grammar-aware generation
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import requests


logger = logging.getLogger("movie_os.llm.client")


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    endpoint: str = "http://localhost:11434"
    model: str = "qwen3.6:latest"
    fallback_model: str = "deepseek-coder-v2:latest"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    timeout: int = 180
    retry_attempts: int = 3
    backoff_factor: int = 2


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    model_used: str
    tokens_used: int = 0
    success: bool = True
    error: Optional[str] = None


class LLMClient:
    """Unified LLM client for all creative agents.

    Wraps Ollama API with retry logic, fallback models, and grammar-aware prompting.
    All creative agents should use this client instead of calling Ollama directly.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.endpoint = self.config.endpoint.rstrip("/")

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate content using local LLM with retry logic.

        Args:
            system_prompt: System message defining the AI's role
            user_prompt: User message with the actual task
            temperature: Sampling temperature (uses config default if None)
            max_tokens: Max tokens to generate (uses config default if None)

        Returns:
            LLMResponse with generated content
        """
        temp = temperature if temperature is not None else self.config.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.max_tokens

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        last_error = None

        # Try primary model first, then fallback
        for model in [self.config.model, self.config.fallback_model]:
            for attempt in range(1, self.config.retry_attempts + 1):
                try:
                    logger.info(f"LLM request (attempt {attempt}/{self.config.retry_attempts}) to {model}")

                    payload = {
                        "model": model,
                        "messages": messages,
                        "temperature": temp,
                        "stream": False,
                        "options": {
                            "num_predict": max_tok,
                            "top_p": self.config.top_p,
                        },
                    }

                    response = self.session.post(
                        f"{self.endpoint}/api/chat",
                        json=payload,
                        timeout=self.config.timeout,
                    )

                    # Handle older Ollama versions that don't support /api/chat
                    if response.status_code == 404:
                        logger.info("Chat endpoint not found, falling back to /api/generate")
                        return self._generate_legacy_chat_to_generate(payload, temp, max_tok)

                    response.raise_for_status()
                    data = response.json()
                    content = data.get("message", {}).get("content", "")

                    if not content:
                        logger.warning("LLM returned empty content")
                        last_error = "Empty response"
                        continue

                    logger.info(f"LLM response received ({len(content)} chars) using {model}")
                    return LLMResponse(
                        content=content,
                        model_used=model,
                        success=True,
                    )

                except requests.exceptions.Timeout as e:
                    logger.warning(f"LLM timeout (attempt {attempt}): {e}")
                    last_error = e
                except requests.exceptions.ConnectionError as e:
                    logger.warning(f"LLM connection error (attempt {attempt}): {e}")
                    last_error = e
                except requests.exceptions.HTTPError as e:
                    logger.error(f"LLM HTTP error (attempt {attempt}): {e}")
                    raise
                except json.JSONDecodeError as e:
                    logger.error(f"LLM JSON error (attempt {attempt}): {e}")
                    last_error = e

                # Exponential backoff
                if attempt < self.config.retry_attempts:
                    import time
                    time.sleep(self.config.backoff_factor ** attempt)

        return LLMResponse(
            content="",
            model_used=self.config.model,
            success=False,
            error=f"All retry attempts failed: {last_error}",
        )

    def _generate_legacy(self, payload: dict, temperature: float, max_tokens: int) -> LLMResponse:
        """Fallback for older Ollama versions using /api/generate."""
        # Convert messages format to legacy format
        system = payload["messages"][0].get("content", "")
        user = payload["messages"][1].get("content", "")

        legacy_payload = {
            "model": payload["model"],
            "prompt": f"{system}\n\n{user}",
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "top_p": payload["options"]["top_p"],
            },
        }

        # Try /api/chat first (newer Ollama), fall back to /api/generate
        for endpoint in ["/api/chat", "/api/generate"]:
            try:
                response = self.session.post(
                    f"{self.endpoint}{endpoint}",
                    json=legacy_payload,
                    timeout=self.config.timeout,
                )
                response.raise_for_status()
                
                if endpoint == "/api/chat":
                    data = response.json()
                    content = data.get("message", {}).get("content", "")
                else:
                    data = response.json()
                    content = data.get("response", "")
                
                return LLMResponse(
                    content=content,
                    model_used=payload["model"],
                    success=bool(content),
                )
            except Exception as e:
                logger.debug(f"Endpoint {endpoint} failed: {e}")
                continue
        
        return LLMResponse(
            content="",
            model_used=payload["model"],
            success=False,
            error="All Ollama endpoints failed",
        )

    def is_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = self.session.get(f"{self.endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """List available models in Ollama."""
        try:
            response = self.session.get(f"{self.endpoint}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            logger.warning(f"Could not list models: {e}")
            return []


# Singleton instance for global use
_llm_client: Optional[LLMClient] = None


def get_llm_client(config: Optional[LLMConfig] = None) -> LLMClient:
    """Get or create the global LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(config)
    return _llm_client


def reset_llm_client():
    """Reset the global LLM client (useful for testing)."""
    global _llm_client
    _llm_client = None
