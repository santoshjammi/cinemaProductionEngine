"""LLM Configuration — loads YAML config with auto-detect.

Config file location (first found wins):
1. `--llm-config` CLI flag
2. `./genesis_llm.yaml`
3. `~/.config/movie_os/genesis_llm.yaml`
4. Built-in defaults
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import urllib.request
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("movie_os.genesis.llm_config")

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "movie_os" / "genesis_llm.yaml"

DEFAULT_CONFIG: dict[str, Any] = {
    "backend": "auto",
    "default_model": "qwen2.5:32b",
    "ollama": {
        "url": "http://localhost:11434",
        "python_api": True,
    },
    "lmstudio": {
        "url": "http://127.0.0.1:1234",
    },
    "hf": {
        "enabled": True,
        "models": {
            "discovery": "Qwen/Qwen2.5-1.5B-Instruct",
            "pkp": "Qwen/Qwen2.5-7B-Instruct",
            "reviewer": "Qwen/Qwen2.5-14B-Instruct",
            "chief": "Qwen/Qwen2.5-14B-Instruct",
        },
        "device": "auto",
        "load_in_8bit": False,
    },
    "timeout": 120.0,
    "temperature": 0.7,
    "max_tokens": 4096,
}


def _try_import_yaml() -> Any:
    """Try to import PyYAML, return None if unavailable."""
    try:
        import yaml
        return yaml
    except ImportError:
        return None


def _load_yaml(path: Path) -> dict[str, Any] | None:
    """Load a YAML file, return None if not found or parse error."""
    if not path.exists():
        return None
    yaml = _try_import_yaml()
    if yaml is None:
        logger.warning(f"PyYAML not installed, skipping {path}")
        return None
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Failed to load {path}: {e}")
        return None


def _merge_config(base: dict, override: dict) -> dict:
    """Deep-merge override into base dict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_config(result[key], value)
        else:
            result[key] = value
    return result


def _check_ollama_running(url: str) -> bool:
    """Check if Ollama server is reachable."""
    try:
        req = urllib.request.Request(f"{url}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def _check_lmstudio_running(url: str) -> bool:
    """Check if LMStudio server is reachable."""
    try:
        req = urllib.request.Request(f"{url}/v1/models", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def _detect_backend(config: dict[str, Any]) -> str:
    """Auto-detect which backend is available.

    Priority: ollama > lmstudio > hf
    """
    ollama_url = config.get("ollama", {}).get("url", "http://localhost:11434")
    lmstudio_url = config.get("lmstudio", {}).get("url", "http://127.0.0.1:1234")

    if _check_ollama_running(ollama_url):
        logger.info("Auto-detect: Ollama running at %s", ollama_url)
        return "ollama"
    if _check_lmstudio_running(lmstudio_url):
        logger.info("Auto-detect: LMStudio running at %s", lmstudio_url)
        return "lmstudio"
    if config.get("hf", {}).get("enabled", True):
        logger.info("Auto-detect: No server found, using HuggingFace")
        return "hf"
    logger.warning("Auto-detect: No backend available")
    return "none"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load LLM config from file, merging with defaults.

    Args:
        path: Optional explicit config path.

    Returns:
        Merged config dict.
    """
    config = dict(DEFAULT_CONFIG)

    # Try explicit path
    if path:
        override = _load_yaml(Path(path))
        if override:
            config = _merge_config(config, override)
            logger.info("Loaded config from %s", path)
            return config

    # Try default paths
    for candidate in [
        Path("genesis_llm.yaml"),
        Path("genesis_llm.yml"),
        DEFAULT_CONFIG_PATH,
    ]:
        override = _load_yaml(candidate)
        if override:
            config = _merge_config(config, override)
            logger.info("Loaded config from %s", candidate)
            break

    # Auto-detect backend if set to "auto"
    if config.get("backend") == "auto":
        config["backend"] = _detect_backend(config)

    return config


def get_model_for_tier(config: dict[str, Any], tier: str) -> str:
    """Get the model name for a given agent tier.

    Args:
        config: The loaded LLM config dict.
        tier: One of "discovery", "pkp", "reviewer", "chief".

    Returns:
        Model name string.
    """
    backend = config.get("backend", "auto")

    if backend == "ollama":
        return config.get("default_model", "qwen2.5:32b")

    if backend == "lmstudio":
        return config.get("default_model", "qwen3-coder")

    if backend == "hf":
        hf_models = config.get("hf", {}).get("models", {})
        return hf_models.get(tier, hf_models.get("pkp", "Qwen/Qwen2.5-7B-Instruct"))

    return config.get("default_model", "qwen2.5:32b")
