"""Ollama HTTP client with retry logic and error handling."""

import time
import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class OllamaClient:
    """HTTP client for interacting with Ollama API."""

    def __init__(self, endpoint: str = "http://localhost:11434", model: str = "llama3.2:latest"):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.9,
        timeout: int = 120,
        retry_attempts: int = 3,
        backoff_factor: int = 2,
    ) -> str:
        """Send a chat request to Ollama and return the assistant's response text.

        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": "..."} dicts.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.
            top_p: Nucleus sampling parameter.
            timeout: Seconds to wait for a response.
            retry_attempts: Number of times to retry on failure.
            backoff_factor: Exponential backoff multiplier between retries.

        Returns:
            The assistant's response text.

        Raises:
            OllamaError: If all retry attempts fail.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "top_p": top_p,
            },
        }

        last_error = None
        for attempt in range(1, retry_attempts + 1):
            try:
                logger.info(f"Ollama request (attempt {attempt}/{retry_attempts}) to {self.endpoint}/api/chat")
                response = self.session.post(
                    f"{self.endpoint}/api/chat",
                    json=payload,
                    timeout=timeout,
                )

                if response.status_code == 404:
                    # Older Ollama versions use /api/generate with prompt+system
                    logger.info("Chat endpoint not found, falling back to /api/generate")
                    return self._generate(payload, temperature, max_tokens, top_p, timeout, retry_attempts, backoff_factor)

                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "")

                if not content:
                    logger.warning("Ollama returned empty content")
                    last_error = "Empty response from Ollama"
                    continue

                logger.info(f"Ollama response received ({len(content)} chars)")
                return content

            except requests.exceptions.Timeout as e:
                logger.warning(f"Request timeout (attempt {attempt}/{retry_attempts}): {e}")
                last_error = e
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error (attempt {attempt}/{retry_attempts}): {e}")
                last_error = e
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error (attempt {attempt}/{retry_attempts}): {e}")
                raise
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response (attempt {attempt}/{retry_attempts}): {e}")
                last_error = e

            if attempt < retry_attempts:
                wait_time = backoff_factor ** (attempt - 1)
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

        raise OllamaError(f"All {retry_attempts} attempts failed. Last error: {last_error}")

    def _generate(
        self,
        payload: dict,
        temperature: float,
        max_tokens: int,
        top_p: float,
        timeout: int,
        retry_attempts: int,
        backoff_factor: int,
    ) -> str:
        """Fallback to /api/generate endpoint for older Ollama versions."""
        system = ""
        user_content = ""
        for msg in payload["messages"]:
            if msg["role"] == "system":
                system = msg["content"]
            elif msg["role"] == "user":
                user_content = msg["content"]

        generate_payload = {
            "model": self.model,
            "prompt": user_content,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": top_p,
            },
        }

        last_error = None
        for attempt in range(1, retry_attempts + 1):
            try:
                response = self.session.post(
                    f"{self.endpoint}/api/generate",
                    json=generate_payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                logger.warning(f"Generate fallback failed (attempt {attempt}/{retry_attempts}): {e}")
                last_error = e
                if attempt < retry_attempts:
                    time.sleep(backoff_factor ** (attempt - 1))

        raise OllamaError(f"All generate attempts failed. Last error: {last_error}")

    def list_models(self) -> list[dict]:
        """List available models on the Ollama instance."""
        try:
            response = self.session.get(f"{self.endpoint}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def check_health(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = self.session.get(f"{self.endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class OllamaError(Exception):
    """Raised when Ollama operations fail."""
    pass
