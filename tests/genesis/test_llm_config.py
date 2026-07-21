"""Unit tests for movie_os.genesis.llm_config."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from movie_os.genesis.llm_config import (
    DEFAULT_CONFIG,
    load_config,
    get_model_for_tier,
    _detect_backend,
    _check_ollama_running,
    _check_lmstudio_running,
    _merge_config,
)


class TestMergeConfig:
    def test_simple_override(self):
        base = {"a": 1, "b": 2}
        override = {"b": 3}
        result = _merge_config(base, override)
        assert result == {"a": 1, "b": 3}

    def test_nested_merge(self):
        base = {"ollama": {"url": "a", "port": 11434}}
        override = {"ollama": {"url": "b"}}
        result = _merge_config(base, override)
        assert result["ollama"]["url"] == "b"
        assert result["ollama"]["port"] == 11434

    def test_new_keys_added(self):
        base = {"a": 1}
        override = {"b": 2}
        result = _merge_config(base, override)
        assert result == {"a": 1, "b": 2}


class TestLoadConfig:
    def test_defaults_when_no_file(self, tmp_path):
        config = load_config()
        assert config["backend"] in ("auto", "ollama", "lmstudio", "hf", "none")
        assert config["default_model"] == "qwen2.5:32b"
        assert config["timeout"] == 120.0

    def test_loads_from_explicit_path(self, tmp_path):
        cfg_path = tmp_path / "test_llm.yaml"
        cfg_path.write_text("backend: ollama\ndefault_model: test-model\n")
        config = load_config(str(cfg_path))
        assert config["backend"] == "ollama"
        assert config["default_model"] == "test-model"

    def test_explicit_path_overrides_defaults(self, tmp_path):
        cfg_path = tmp_path / "test_llm.yaml"
        cfg_path.write_text("timeout: 30.0\n")
        config = load_config(str(cfg_path))
        assert config["timeout"] == 30.0

    def test_missing_explicit_path_uses_defaults(self):
        config = load_config("/nonexistent/path.yaml")
        assert config["default_model"] == "qwen2.5:32b"


class TestDetectBackend:
    def test_returns_string(self):
        config = dict(DEFAULT_CONFIG)
        backend = _detect_backend(config)
        assert backend in ("ollama", "lmstudio", "hf", "none")

    def test_hf_fallback_when_no_server(self):
        config = dict(DEFAULT_CONFIG)
        config["hf"]["enabled"] = True
        backend = _detect_backend(config)
        # If no server running, should fall back to hf
        if backend not in ("ollama", "lmstudio"):
            assert backend == "hf"

    def test_none_when_hf_disabled(self):
        config = dict(DEFAULT_CONFIG)
        config["hf"]["enabled"] = False
        backend = _detect_backend(config)
        if backend not in ("ollama", "lmstudio"):
            assert backend == "none"


class TestCheckRunning:
    def test_ollama_unreachable(self):
        assert _check_ollama_running("http://127.0.0.1:1") is False

    def test_lmstudio_unreachable(self):
        assert _check_lmstudio_running("http://127.0.0.1:1") is False


class TestGetModelForTier:
    def test_ollama_backend_uses_default(self):
        config = {"backend": "ollama", "default_model": "qwen2.5:32b"}
        assert get_model_for_tier(config, "discovery") == "qwen2.5:32b"
        assert get_model_for_tier(config, "pkp") == "qwen2.5:32b"

    def test_lmstudio_backend_uses_default(self):
        config = {"backend": "lmstudio", "default_model": "qwen3-coder"}
        assert get_model_for_tier(config, "pkp") == "qwen3-coder"

    def test_hf_backend_uses_tiered_models(self):
        config = {
            "backend": "hf",
            "hf": {
                "models": {
                    "discovery": "small-model",
                    "pkp": "medium-model",
                    "reviewer": "large-model",
                    "chief": "large-model",
                }
            },
        }
        assert get_model_for_tier(config, "discovery") == "small-model"
        assert get_model_for_tier(config, "pkp") == "medium-model"
        assert get_model_for_tier(config, "reviewer") == "large-model"
        assert get_model_for_tier(config, "chief") == "large-model"

    def test_hf_falls_back_to_pkp(self):
        config = {
            "backend": "hf",
            "hf": {"models": {"pkp": "default-model"}},
        }
        assert get_model_for_tier(config, "unknown_tier") == "default-model"
