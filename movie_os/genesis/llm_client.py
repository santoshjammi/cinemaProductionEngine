"""LLM Client — talks to LMStudio (local) or OpenAI (cloud) with fallback.

All Genesis agents use this client for LLM calls. Tests use MockLLMClient
which returns canned responses — no real LLM calls in tests.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any, Optional


logger = logging.getLogger("movie_os.genesis.llm")


class LLMClient:
    """LLM client that talks to LMStudio or OpenAI-compatible APIs."""

    def __init__(
        self,
        url: str = "http://127.0.0.1:1234",
        api_key: str | None = None,
        model: str = "qwen3-coder",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 120.0,
    ):
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def generate(self, prompt: str, system: str = "") -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt.
            system: Optional system prompt.

        Returns:
            The LLM response text.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }

        url = f"{self.url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                result = json.loads(raw)
                return result["choices"][0]["message"]["content"]
        except urllib.error.URLError as e:
            logger.error(f"LLM call failed: {e}")
            raise RuntimeError(f"LLM unavailable at {self.url}: {e}") from e
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"LLM response parse error: {e}")
            raise RuntimeError(f"LLM response parse error: {e}") from e

    def generate_json(self, prompt: str, system: str = "") -> dict[str, Any]:
        """Generate a response and parse it as JSON.

        Tries to extract JSON from the response, handling markdown
        code fences and extra text.
        """
        response = self.generate(prompt, system)
        return self._extract_json(response)

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        """Extract JSON from an LLM response that may have markdown fences."""
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from ```json ... ``` fences
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            return json.loads(text[start:end].strip())

        # Try extracting from ``` ... ``` fences
        if "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            return json.loads(text[start:end].strip())

        # Try finding the first { and last }
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            return json.loads(text[first : last + 1])

        raise ValueError(f"Could not extract JSON from LLM response: {text[:200]}...")


class MockLLMClient:
    """Mock LLM client for testing — returns canned responses.

    Register responses by agent name or use a default fallback.
    """

    def __init__(self, responses: dict[str, str] | None = None):
        self._responses = responses or {}
        self._default = '{"status": "mock", "content": {}}'
        self._call_log: list[str] = []

    def set_response(self, key: str, response: str) -> None:
        """Set a canned response for a given agent/prompt key."""
        self._responses[key] = response

    def set_default(self, response: str) -> None:
        """Set the default fallback response."""
        self._default = response

    def generate(self, prompt: str, system: str = "") -> str:
        """Return a canned response based on the prompt content."""
        self._call_log.append(prompt[:100])
        # Try to match by keywords in the prompt
        for key, response in self._responses.items():
            if key.lower() in prompt.lower():
                return response
        return self._default

    def generate_json(self, prompt: str, system: str = "") -> dict[str, Any]:
        """Return a canned JSON response."""
        response = self.generate(prompt, system)
        return LLMClient._extract_json(response)

    @property
    def call_count(self) -> int:
        return len(self._call_log)

    @property
    def call_log(self) -> list[str]:
        return self._call_log