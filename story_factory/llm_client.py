"""Thin LMStudio HTTP client used by the Story Factory agents.

This is a minimal wrapper around the OpenAI-compatible /v1/chat/completions
endpoint that LMStudio exposes. It exists so each agent can call the LLM
with a tiny prompt and a tiny expected output — no 2000-token system prompts.

Usage:
    from story_factory.llm_client import chat

    text = chat(
        system="You are a DNA generator. Output only YAML.",
        user="Synopsis: A man stops reaching for his wife.",
        temperature=0.3,
        max_tokens=500,
    )
"""

import json
import urllib.request
import urllib.error
from typing import Any


class LLMError(RuntimeError):
    """Raised when the LLM call fails or returns unusable output."""


def chat(
    system: str,
    user: str,
    *,
    base_url: str = "http://localhost:1234",
    api_key: str = "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W",
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    timeout: int = 600,
) -> str:
    """Call LMStudio's chat completions endpoint and return the assistant text.

    The system + user prompts are intentionally tiny (per the Story Factory
    design — each agent has one responsibility). The LLM is expected to fill
    in the content, not invent the structure.

    Args:
        system: System prompt. Should describe the agent's single responsibility
            and the exact output format expected.
        user: User prompt. The synopsis or upstream artifact.
        base_url: LMStudio base URL.
        api_key: LMStudio API key (LMStudio doesn't actually validate this,
            but the client requires it).
        model: Model ID. If None, uses whatever LMStudio has loaded.
        temperature: Sampling temperature. Low for deterministic output.
        max_tokens: Maximum tokens in the response.
        timeout: Request timeout in seconds.

    Returns:
        The assistant's text response (stripped of leading/trailing whitespace).

    Raises:
        LLMError: If the HTTP call fails or returns a non-2xx status.
    """
    payload: dict[str, Any] = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if model is None:
        model = "qwen2.5:32b"
    payload["model"] = model

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise LLMError(f"LMStudio request failed: {e}") from e
    except urllib.error.HTTPError as e:
        raise LLMError(f"LMStudio returned {e.code}: {e.read().decode('utf-8', errors='replace')}") from e

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as e:
        raise LLMError(f"Unexpected LMStudio response shape: {data!r}") from e
