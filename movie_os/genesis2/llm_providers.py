"""LLM Provider Interface — Ollama and Mock providers.

Drop-in replacement for MockLLMClient with real local LLM inference.

- OllamaProvider: Calls http://127.0.0.1:11434/api/chat (Ollama API)
- MockLLMProvider: Returns canned responses for testing.
"""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger("movie_os.genesis2.llm_providers")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class LLMConfig(BaseModel):
    """Configuration for LLM providers."""

    provider: str = "ollama"  # "ollama" | "mock"
    model: str = "deepseek-coder-v2:latest"
    temperature: float = 0.3
    max_tokens: int = 8192
    timeout: int = 600
    url: str = "http://localhost:11434"
    ollama_url: str = "http://localhost:11434"
    # Context window for Ollama. Defaults to None (Ollama's model default,
    # which for deepseek-coder-v2 is 163840 — 54GB, very slow on M1 Max).
    # Set a smaller value (e.g. 8192) for reliable local inference.
    num_ctx: int | None = None
    think: bool = False


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """Abstract base for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, config: LLMConfig | None = None) -> str:
        """Generate text from a prompt."""
        ...

    def generate_json(self, prompt: str, config: LLMConfig | None = None) -> dict[str, Any]:
        """Generate text and extract JSON from the response."""
        text = self.generate(prompt, config)
        return _extract_json(text)

    def is_available(self) -> bool:
        """Check if the provider is reachable."""
        return True  # Default: assume available


# ---------------------------------------------------------------------------
# JSON extraction helpers
# ---------------------------------------------------------------------------

def _repair_truncated_json(s: str) -> dict[str, Any] | None:
    """Repair a JSON string truncated mid-value.

    The LLM response may be cut off inside a string value (e.g.
    '"description": "Mark starts to withdraw...'). Appending brackets can't
    fix an unterminated string. Strategy:
      1. Walk the string tracking string/bracket state, recording every
         "clean" boundary (where we're not inside an unterminated string).
      2. From the last clean boundary backwards, truncate and balance
         brackets, trying to parse each candidate.
    Returns the parsed dict, or None if repair fails.
    """
    if not s:
        return None
    # Record all clean boundaries (indices where we're not inside a string)
    in_string = False
    escape = False
    boundaries = []
    for i, ch in enumerate(s):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
                boundaries.append(i)  # string just closed
        else:
            if ch == '"':
                in_string = True
            elif ch in "{}[]":
                boundaries.append(i)
    # If we ended inside a string, the last boundary is the truncation point
    if in_string:
        boundaries = boundaries[:-1] if boundaries else []
    # Try each boundary from the end backwards
    for end in reversed(boundaries):
        candidate = s[: end + 1]
        # Balance brackets
        stack = []
        for ch in candidate:
            if ch in "[{":
                stack.append(ch)
            elif ch in "]}" and stack:
                stack.pop()
        closers = "".join("]" if o == "[" else "}" for o in reversed(stack))
        for extra in (closers, closers + "}", closers + "}]"):
            try:
                return json.loads(candidate + extra)
            except json.JSONDecodeError:
                continue
    return None


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from an LLM response that may have markdown fences or extra text.

    Tries in order:
    1. Direct JSON parse
    2. Strip markdown fences, then brace extraction
    3. Brace extraction on raw text
    """
    if not text or not text.strip():
        raise ValueError("Empty LLM response")

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip markdown fences and try again
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # Remove opening fence (handle leading whitespace)
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
        # Remove closing fence
        cleaned = re.sub(r'\n?\s*```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fall through to brace extraction on cleaned text
            text = cleaned
    elif "```" in cleaned:
        # Handle case where ``` is not at start (leading whitespace)
        idx = cleaned.index("```")
        cleaned = cleaned[idx:]
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
        cleaned = re.sub(r'\n?\s*```\s*$', '', cleaned)
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            text = cleaned

    # Brace extraction: find first { and last }
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        candidate = text[first : last + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Try progressively stripping trailing content
            for _ in range(5):
                last = text.rfind("}", 0, last)
                if last == -1 or last <= first:
                    break
                try:
                    return json.loads(text[first : last + 1])
                except json.JSONDecodeError:
                    continue

    # Truncated JSON fallback: if text starts with { but has no closing },
    # try appending } and parse
    if first != -1 and last == -1:
        candidate = text[first:] + "}"
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Try with multiple closing braces for nested objects
            for depth in range(2, 6):
                try:
                    return json.loads(text[first:] + "}" * depth)
                except json.JSONDecodeError:
                    continue

    # Truncated JSON with a premature closing brace: the response was cut off
    # mid-array/object. Try progressively appending closing braces AND brackets
    # to balance the structure, then parse.
    if first != -1:
        for extra in ("}", "}]", "}}", "}]}", "}}]", "}}}]", "}}}]}"):
            try:
                return json.loads(text[first:] + extra)
            except json.JSONDecodeError:
                continue

    # Mid-string truncation: the response was cut off INSIDE a string value
    # (e.g. "...description\": \"Mark starts to withdraw..."). Appending
    # brackets can't fix an unterminated string. Repair by truncating at the
    # last complete string boundary, then balancing brackets.
    if first != -1:
        repaired = _repair_truncated_json(text[first:])
        if repaired is not None:
            return repaired

    raise ValueError(f"Could not extract JSON from LLM response: {text[:200]}...")


# ---------------------------------------------------------------------------
# Ollama Provider
# ---------------------------------------------------------------------------

class OllamaProvider(LLMProvider):
    """Provider for Ollama (local LLM server).

    Calls http://localhost:11434/api/generate with the prompt.
    Handles JSON extraction from markdown code blocks.
    """

    def __init__(
        self,
        model: str = "deepseek-coder-v2:latest",
        url: str = "http://localhost:11434",
        timeout: int = 600,
    ):
        self.model = model
        self.url = url.rstrip("/")
        self.timeout = timeout

    def generate(self, prompt: str, config: LLMConfig | None = None) -> str:
        """Generate a response from Ollama."""
        import urllib.request

        cfg = config or LLMConfig()
        full_prompt = prompt

        payload = {
            "model": cfg.model or self.model,
            "prompt": full_prompt,
            "options": {
                "temperature": cfg.temperature,
                "num_predict": cfg.max_tokens,
            },
            "stream": False,
        }
        if cfg.num_ctx:
            payload["options"]["num_ctx"] = cfg.num_ctx
        payload["think"] = cfg.think

        url = f"{self.url}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                result = json.loads(raw)
                content = result.get("response", "")
                if not content or not content.strip():
                    raise RuntimeError("Ollama returned empty response")
                from movie_os.llm.runtime_logger import log_runtime_llm_call
                log_runtime_llm_call(
                    prompt=prompt,
                    response=content,
                    system_prompt="",
                    model=cfg.model or self.model,
                    provider="ollama_g2",
                    success=True,
                )
                return content
        except urllib.error.URLError as e:
            logger.warning(f"Ollama unavailable at {self.url}: {e}")
            from movie_os.llm.runtime_logger import log_runtime_llm_call
            log_runtime_llm_call(
                prompt=prompt,
                response="",
                system_prompt="",
                model=cfg.model or self.model,
                provider="ollama_g2",
                success=False,
                error=str(e),
            )
            raise RuntimeError(f"Ollama unavailable at {self.url}: {e}") from e
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Ollama response parse error: {e}")
            from movie_os.llm.runtime_logger import log_runtime_llm_call
            log_runtime_llm_call(
                prompt=prompt,
                response="",
                system_prompt="",
                model=cfg.model or self.model,
                provider="ollama_g2",
                success=False,
                error=str(e),
            )
            raise RuntimeError(f"Ollama response parse error: {e}") from e

    def is_available(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Mock Provider
# ---------------------------------------------------------------------------

class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing — returns deterministic responses.

    Register responses by keyword or use a default fallback.
    """

    def __init__(self, responses: dict[str, str] | None = None):
        self._responses = responses or {}
        self._default = '{"status": "mock", "content": {}}'
        self._call_log: list[str] = []

    def set_response(self, key: str, response: str) -> None:
        """Set a canned response for a given keyword."""
        self._responses[key] = response

    def set_default(self, response: str) -> None:
        """Set the default fallback response."""
        self._default = response

    def generate(self, prompt: str, config: LLMConfig | None = None) -> str:
        """Return a canned response based on the prompt content."""
        self._call_log.append(prompt[:100])
        for key, response in self._responses.items():
            if key.lower() in prompt.lower():
                return response
        return self._default

    def generate_json(self, prompt: str, config: LLMConfig | None = None) -> dict[str, Any]:
        """Return a canned JSON response."""
        response = self.generate(prompt, config)
        return _extract_json(response)

    @property
    def call_count(self) -> int:
        return len(self._call_log)

    @property
    def call_log(self) -> list[str]:
        return self._call_log
