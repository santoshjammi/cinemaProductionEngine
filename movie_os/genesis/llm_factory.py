"""LLM Factory — creates the right LLM client based on config and agent tier.

The factory supports:
- Auto-detect: tries Ollama → LMStudio → HuggingFace
- Explicit backend selection via config or CLI flags
- Tiered model routing for HuggingFace (different models per agent type)
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from .llm_client import LLMClient, MockLLMClient
from .llm_config import load_config, get_model_for_tier

logger = logging.getLogger("movie_os.genesis.llm_factory")


# Agent tiers map to model sizes
TIER_DISCOVERY = "discovery"   # 1-3B models
TIER_PKP = "pkp"               # 7B models
TIER_REVIEWER = "reviewer"     # 14B+ models
TIER_CHIEF = "chief"           # 14B+ models


def create_client(
    config_path: str | None = None,
    backend: str | None = None,
    model: str | None = None,
    llm_url: str | None = None,
    mock: bool = False,
) -> LLMClient:
    """Create an LLM client based on config and CLI overrides.

    Args:
        config_path: Path to YAML config file.
        backend: Override backend (ollama, lmstudio, hf, mock).
        model: Override model name.
        llm_url: Override server URL.
        mock: If True, return MockLLMClient.

    Returns:
        An LLMClient instance.
    """
    if mock:
        from .mock_data import build_rich_mock_llm
        return build_rich_mock_llm()

    config = load_config(config_path)

    # CLI overrides
    if backend:
        config["backend"] = backend
    if model:
        config["default_model"] = model
    if llm_url:
        # Set URL for the active backend
        active = config.get("backend", "auto")
        if active == "ollama":
            config.setdefault("ollama", {})["url"] = llm_url
        elif active == "lmstudio":
            config.setdefault("lmstudio", {})["url"] = llm_url

    active_backend = config.get("backend", "auto")
    if active_backend == "auto":
        from .llm_config import _detect_backend
        active_backend = _detect_backend(config)

    logger.info("Creating LLM client: backend=%s", active_backend)

    if active_backend == "ollama":
        return _create_ollama_client(config)
    elif active_backend == "lmstudio":
        return _create_lmstudio_client(config)
    elif active_backend == "hf":
        return _create_hf_client(config)
    else:
        logger.warning("No backend available, falling back to mock")
        from .mock_data import build_rich_mock_llm
        return build_rich_mock_llm()


def create_tiered_clients(
    config_path: str | None = None,
    backend: str | None = None,
    model: str | None = None,
    llm_url: str | None = None,
    mock: bool = False,
) -> dict[str, LLMClient]:
    """Create LLM clients for each agent tier.

    Returns a dict mapping tier names to LLMClient instances.
    For Ollama/LMStudio, all tiers share the same client.
    For HuggingFace, each tier gets its own model.

    Returns:
        Dict with keys: "discovery", "pkp", "reviewer", "chief"
    """
    if mock:
        from .mock_data import build_rich_mock_llm
        mock_client = build_rich_mock_llm()
        return {
            TIER_DISCOVERY: mock_client,
            TIER_PKP: mock_client,
            TIER_REVIEWER: mock_client,
            TIER_CHIEF: mock_client,
        }

    config = load_config(config_path)

    if backend:
        config["backend"] = backend
    if model:
        config["default_model"] = model
    if llm_url:
        active = config.get("backend", "auto")
        if active == "ollama":
            config.setdefault("ollama", {})["url"] = llm_url
        elif active == "lmstudio":
            config.setdefault("lmstudio", {})["url"] = llm_url

    active_backend = config.get("backend", "auto")
    if active_backend == "auto":
        from .llm_config import _detect_backend
        active_backend = _detect_backend(config)

    logger.info("Creating tiered clients: backend=%s", active_backend)

    if active_backend == "ollama":
        client = _create_ollama_client(config)
        return {t: client for t in (TIER_DISCOVERY, TIER_PKP, TIER_REVIEWER, TIER_CHIEF)}

    elif active_backend == "lmstudio":
        client = _create_lmstudio_client(config)
        return {t: client for t in (TIER_DISCOVERY, TIER_PKP, TIER_REVIEWER, TIER_CHIEF)}

    elif active_backend == "hf":
        return _create_tiered_hf_clients(config)

    else:
        logger.warning("No backend available, falling back to mock")
        from .mock_data import build_rich_mock_llm
        mock_client = build_rich_mock_llm()
        return {t: mock_client for t in (TIER_DISCOVERY, TIER_PKP, TIER_REVIEWER, TIER_CHIEF)}


def _create_ollama_client(config: dict[str, Any]) -> LLMClient:
    """Create an Ollama client from config."""
    from .llm_ollama import OllamaClient

    ollama_cfg = config.get("ollama", {})
    return OllamaClient(
        url=ollama_cfg.get("url", "http://localhost:11434"),
        model=config.get("default_model", "qwen2.5:32b"),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4096),
        timeout=config.get("timeout", 120.0),
        use_python_api=ollama_cfg.get("python_api", True),
    )


def _create_lmstudio_client(config: dict[str, Any]) -> LLMClient:
    """Create an LMStudio client from config."""
    from .llm_client import LLMClient

    lm_cfg = config.get("lmstudio", {})
    return LLMClient(
        url=lm_cfg.get("url", "http://127.0.0.1:1234"),
        model=config.get("default_model", "qwen3-coder"),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4096),
        timeout=config.get("timeout", 120.0),
    )


def _create_hf_client(config: dict[str, Any]) -> LLMClient:
    """Create a single HuggingFace client (uses pkp model by default)."""
    from .llm_hf import HFClient

    hf_cfg = config.get("hf", {})
    return HFClient(
        models=hf_cfg.get("models", {}),
        device=hf_cfg.get("device", "auto"),
        load_in_8bit=hf_cfg.get("load_in_8bit", False),
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 4096),
        timeout=config.get("timeout", 120.0),
    )


def _create_tiered_hf_clients(config: dict[str, Any]) -> dict[str, LLMClient]:
    """Create separate HuggingFace clients for each tier."""
    from .llm_hf import HFClient

    hf_cfg = config.get("hf", {})
    models = hf_cfg.get("models", {})
    device = hf_cfg.get("device", "auto")
    load_in_8bit = hf_cfg.get("load_in_8bit", False)
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 4096)
    timeout = config.get("timeout", 120.0)

    clients = {}
    for tier in (TIER_DISCOVERY, TIER_PKP, TIER_REVIEWER, TIER_CHIEF):
        tier_models = {tier: models.get(tier, models.get("pkp", "Qwen/Qwen2.5-7B-Instruct"))}
        clients[tier] = HFClient(
            models=tier_models,
            device=device,
            load_in_8bit=load_in_8bit,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
    return clients
