"""Ollama LLM Client — talks to Ollama via Python API or subprocess fallback.

Uses the `ollama` Python package when available (python_api=True).
Falls back to `ollama run` subprocess when the package is not installed.
"""

from __future__ import annotations

import json
import logging
import subprocess
import urllib.error
import urllib.request
from typing import Any, Optional

from .llm_client import LLMClient

logger = logging.getLogger("movie_os.genesis.llm_ollama")


class OllamaClient(LLMClient):
    """LLM client that talks to Ollama.

    Uses the `ollama` Python package when available, falls back to
    the Ollama HTTP API (OpenAI-compatible endpoint) or subprocess.
    """

    def __init__(
        self,
        url: str = "http://localhost:11434",
        model: str = "qwen2.5:32b",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 120.0,
        use_python_api: bool = True,
        use_http_api: bool = True,
    ):
        self.url = url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.use_python_api = use_python_api
        self.use_http_api = use_http_api
        self._ollama_module = None

    def _get_ollama_module(self):
        """Lazy-import the ollama Python package."""
        if self._ollama_module is None:
            try:
                import ollama
                self._ollama_module = ollama
                logger.info("Using ollama Python package")
            except ImportError:
                self._ollama_module = False  # sentinel
                logger.info("ollama package not available, using HTTP API")
        return self._ollama_module if self.use_python_api else False

    def generate(self, prompt: str, system: str = "") -> str:
        """Generate a response from Ollama.

        Uses HTTP API first when use_python_api=False,
        otherwise tries Python package then subprocess.
        """
        result = None
        used_backend = "unknown"
        error_msg = ""
        
        # Try HTTP API first if python_api is disabled
        if not self.use_python_api:
            try:
                result = self._generate_http_api(prompt, system)
                used_backend = "http"
            except Exception as e:
                logger.warning(f"Ollama HTTP API failed: {e}, trying subprocess")
                error_msg += f"http: {e}; "
            
            if not result:
                try:
                    result = self._generate_subprocess(prompt, system)
                    used_backend = "subprocess"
                except Exception as e:
                    logger.warning(f"Ollama subprocess failed: {e}")
                    error_msg += f"subprocess: {e}; "
        else:
            # Try Python API first (most reliable)
            mod = self._get_ollama_module()
            if mod:
                try:
                    result = self._generate_python_api(prompt, system)
                    used_backend = "python"
                except Exception as e:
                    logger.warning(f"Ollama Python API failed: {e}, trying subprocess")
                    error_msg += f"python: {e}; "

            if not result:
                # Try subprocess
                try:
                    result = self._generate_subprocess(prompt, system)
                    used_backend = "subprocess"
                except Exception as e:
                    logger.warning(f"Ollama subprocess failed: {e}")
                    error_msg += f"subprocess: {e}; "

        from movie_os.llm.runtime_logger import log_runtime_llm_call
        if result and result.strip():
            log_runtime_llm_call(
                prompt=prompt,
                response=result,
                system_prompt=system,
                model=self.model,
                provider=f"ollama_{used_backend}",
                success=True,
            )
            return result

        log_runtime_llm_call(
            prompt=prompt,
            response="",
            system_prompt=system,
            model=self.model,
            provider="ollama_all",
            success=False,
            error=f"All backends failed: {error_msg}",
        )
        raise RuntimeError("All Ollama backends failed to produce a response")

    def _generate_python_api(self, prompt: str, system: str = "") -> str:
        """Generate using the ollama Python package."""
        mod = self._get_ollama_module()
        if not mod:
            raise RuntimeError("ollama Python package not available")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = mod.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        )
        return response["message"]["content"]

    def _generate_http_api(self, prompt: str, system: str = "") -> str:
        """Generate using Ollama's generate API (more reliable than chat)."""
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{full_prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
            "stream": False,
        }

        url = f"{self.url}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            raw = resp.read()
            result = json.loads(raw)
            content = result.get("response", "")
            if not content or not content.strip():
                raise RuntimeError("Ollama returned empty response")
            return content

    def _generate_subprocess(self, prompt: str, system: str = "") -> str:
        """Generate using `ollama run` subprocess."""
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{full_prompt}"

        result = subprocess.run(
            ["ollama", "run", self.model],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"ollama run failed (exit {result.returncode}): {result.stderr[:200]}"
            )
        # Strip ANSI escape sequences that ollama run sometimes emits
        import re
        clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', result.stdout)
        # Strip all remaining control characters except newlines and tabs
        clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', clean)
        # Replace newlines with spaces to fix ANSI line-break artifacts
        # e.g. "the\neffects" -> "the effects" (valid JSON)
        clean = clean.replace('\n', ' ').replace('\r', ' ')
        # Collapse multiple spaces
        clean = re.sub(r' +', ' ', clean)
        return clean.strip()

    def is_available(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            req = urllib.request.Request(f"{self.url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False
