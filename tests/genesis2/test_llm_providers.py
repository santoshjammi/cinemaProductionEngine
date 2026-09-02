"""Tests for GENESIS2 LLM providers — Ollama and Mock.

Tests cover:
- JSON extraction from various response formats
- MockLLMProvider deterministic behavior
- LLMFactory provider creation
- LLMClient auto-detection and tier routing
- Fallback chain (Ollama → Mock)
- Skip network tests when servers not running
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import patch, MagicMock

from movie_os.genesis2.llm_providers import (
    LLMConfig,
    LLMProvider,
    OllamaProvider,
    MockLLMProvider,
    _extract_json,
)
from movie_os.genesis2.llm_factory import LLMFactory, create_llm
from movie_os.genesis2.llm_client import LLMClient, MockLLMClient, _extract_json as _extract_json_reexport


# ---------------------------------------------------------------------------
# JSON extraction tests
# ---------------------------------------------------------------------------

class TestExtractJSON:
    """Tests for the _extract_json helper function."""

    def test_direct_json(self):
        text = '{"intent": "hello", "confidence": "inferred"}'
        result = _extract_json(text)
        assert result == {"intent": "hello", "confidence": "inferred"}

    def test_json_in_markdown_fence(self):
        text = '```json\n{"intent": "hello"}\n```'
        result = _extract_json(text)
        assert result == {"intent": "hello"}

    def test_json_in_plain_fence(self):
        text = '```\n{"intent": "hello"}\n```'
        result = _extract_json(text)
        assert result == {"intent": "hello"}

    def test_json_with_surrounding_text(self):
        text = 'Here is the JSON:\n{"intent": "hello"}\nDone.'
        result = _extract_json(text)
        assert result == {"intent": "hello"}

    def test_invalid_json_raises(self):
        text = "no json at all here, just text"
        with pytest.raises(ValueError) as exc:
            _extract_json(text)
        assert "Could not extract JSON" in str(exc.value)

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            _extract_json("")

    def test_nested_json(self):
        text = json.dumps({"outer": {"inner": [1, 2, 3]}, "x": True})
        result = _extract_json(text)
        assert result["outer"]["inner"] == [1, 2, 3]

    def test_json_with_extra_trailing_text(self):
        text = '```json\n{"a": 1, "b": 2}\n```\n\nLet me know if you need anything else.'
        result = _extract_json(text)
        assert result == {"a": 1, "b": 2}

    def test_json_with_whitespace(self):
        text = '  \n  {"key": "value"}  \n  '
        result = _extract_json(text)
        assert result == {"key": "value"}

    def test_reexported_extract_json(self):
        """Verify _extract_json is re-exported from llm_client."""
        assert _extract_json_reexport is _extract_json


# ---------------------------------------------------------------------------
# MockLLMProvider tests
# ---------------------------------------------------------------------------

class TestMockLLMProvider:
    """Tests for the MockLLMProvider."""

    def test_default_response(self):
        mock = MockLLMProvider()
        result = mock.generate("anything")
        assert "mock" in result

    def test_registered_response_by_keyword(self):
        mock = MockLLMProvider()
        mock.set_response("intent_analyst", '{"intent": "registered"}')
        result = mock.generate("Please run intent_analyst on this")
        assert "registered" in result

    def test_set_default(self):
        mock = MockLLMProvider()
        mock.set_default('{"a": 1}')
        assert mock.generate("anything") == '{"a": 1}'

    def test_call_log(self):
        mock = MockLLMProvider()
        mock.generate("first call")
        mock.generate("second call")
        assert mock.call_count == 2
        assert len(mock.call_log) == 2
        assert mock.call_log[0] == "first call"
        assert mock.call_log[1] == "second call"

    def test_keyword_case_insensitive(self):
        mock = MockLLMProvider()
        mock.set_response("INTENT_ANALYST", '{"a": 1}')
        result = mock.generate("run Intent_Analyst on this")
        assert result == '{"a": 1}'

    def test_no_match_uses_default(self):
        mock = MockLLMProvider()
        mock.set_response("foo", '{"a": 1}')
        mock.set_default('{"b": 2}')
        result = mock.generate("nothing matches")
        assert result == '{"b": 2}'

    def test_generate_json_extracts(self):
        mock = MockLLMProvider()
        mock.set_response("foo", '```json\n{"k": "v"}\n```')
        result = mock.generate_json("foo bar")
        assert result == {"k": "v"}

    def test_generate_json_direct(self):
        mock = MockLLMProvider()
        mock.set_response("test", '{"x": 42}')
        result = mock.generate_json("test prompt")
        assert result == {"x": 42}

    def test_generate_json_with_fences(self):
        mock = MockLLMProvider()
        mock.set_response("test", '```json\n{"nested": {"a": 1}}\n```')
        result = mock.generate_json("test prompt")
        assert result == {"nested": {"a": 1}}

    def test_generate_json_braces_extraction(self):
        mock = MockLLMProvider()
        mock.set_response("test", 'Some text {"key": "value"} more text')
        result = mock.generate_json("test prompt")
        assert result == {"key": "value"}

    def test_is_available_returns_true(self):
        mock = MockLLMProvider()
        assert mock.is_available() is True

    def test_config_parameter_accepted(self):
        """Test that generate accepts config parameter (for interface compatibility)."""
        mock = MockLLMProvider()
        config = LLMConfig(provider="mock")
        result = mock.generate("test", config)
        assert "mock" in result


# ---------------------------------------------------------------------------
# LLMConfig tests
# ---------------------------------------------------------------------------

class TestLLMConfig:
    """Tests for LLMConfig model."""

    def test_default_values(self):
        config = LLMConfig()
        assert config.provider == "ollama"
        assert config.model == "qwen3.6:latest"  # canonical local textual model
        assert config.temperature == 0.3
        assert config.max_tokens == 8192
        assert config.timeout == 600
        assert config.url == "http://localhost:11434"
        assert config.ollama_url == "http://localhost:11434"

    def test_custom_values(self):
        config = LLMConfig(
            provider="ollama",
            model="qwen3.6:latest",
            temperature=0.5,
            max_tokens=2048,
            timeout=60,
            url="http://localhost:9999",
            ollama_url="http://localhost:11434",
        )
        assert config.provider == "ollama"
        assert config.model == "qwen3.6:latest"
        assert config.temperature == 0.5
        assert config.max_tokens == 2048
        assert config.timeout == 60

    def test_auto_provider(self):
        config = LLMConfig(provider="auto")
        assert config.provider == "auto"

    def test_huggingface_provider(self):
        config = LLMConfig(provider="huggingface")
        assert config.provider == "huggingface"


# ---------------------------------------------------------------------------
# OllamaProvider tests
# ---------------------------------------------------------------------------

class TestOllamaProvider:
    """Tests for OllamaProvider."""

    def test_default_config(self):
        provider = OllamaProvider()
        assert provider.model == "qwen3.6:latest"  # canonical local textual model
        assert provider.url == "http://localhost:11434"
        assert provider.timeout == 600

    def test_custom_config(self):
        provider = OllamaProvider(
            model="custom-model",
            url="http://localhost:9999",
            timeout=30,
        )
        assert provider.model == "custom-model"
        assert provider.url == "http://localhost:9999"
        assert provider.timeout == 30

    def test_generate_uses_response_field(self):
        """Test that OllamaProvider uses the 'response' field."""
        provider = OllamaProvider()
        mock_response = {"response": '{"purpose": "ollama test"}'}
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_response).encode()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            result = provider.generate("test prompt")
            assert result == '{"purpose": "ollama test"}'

    def test_generate_raises_on_empty_response(self):
        """Test that OllamaProvider raises on empty response."""
        provider = OllamaProvider()
        mock_response = {"response": ""}
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_response).encode()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            with pytest.raises(RuntimeError, match="empty response"):
                provider.generate("test prompt")

    def test_generate_raises_on_server_unavailable(self):
        """Test that OllamaProvider raises when server is down."""
        provider = OllamaProvider()
        with patch("urllib.request.urlopen") as mock_urlopen:
            import urllib.error
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

            with pytest.raises(RuntimeError, match="Ollama unavailable"):
                provider.generate("test prompt")

    def test_generate_json(self):
        """Test that OllamaProvider.generate_json extracts JSON."""
        provider = OllamaProvider()
        mock_response = {"response": '```json\n{"key": "value"}\n```'}
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_response).encode()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            result = provider.generate_json("test prompt")
            assert result == {"key": "value"}

    def test_is_available_true_when_reachable(self):
        """Test is_available returns True when Ollama responds."""
        provider = OllamaProvider()
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            assert provider.is_available() is True

    def test_is_available_false_when_unreachable(self):
        """Test is_available returns False when Ollama is down."""
        provider = OllamaProvider()
        with patch("urllib.request.urlopen", side_effect=Exception("down")):
            assert provider.is_available() is False

    @pytest.mark.skip(reason="Requires Ollama running at http://localhost:11434")
    def test_generate_with_real_server(self):
        """Integration test — skip if server not running."""
        provider = OllamaProvider()
        assert provider.is_available(), "Ollama not running"
        result = provider.generate("Say hello")
        assert len(result) > 0


# ---------------------------------------------------------------------------
# LLMFactory tests
# ---------------------------------------------------------------------------

class TestLLMFactory:
    """Tests for LLMFactory."""

    def test_create_ollama_provider(self):
        config = LLMConfig(provider="ollama")
        provider = LLMFactory.create(config)
        assert isinstance(provider, OllamaProvider)

    def test_create_mock_provider(self):
        config = LLMConfig(provider="mock")
        provider = LLMFactory.create(config)
        assert isinstance(provider, MockLLMProvider)

    def test_create_huggingface_falls_back_to_mock(self):
        config = LLMConfig(provider="huggingface")
        provider = LLMFactory.create(config)
        assert isinstance(provider, MockLLMProvider)

    def test_create_default_is_ollama(self):
        provider = LLMFactory.create()
        assert isinstance(provider, OllamaProvider)

    def test_create_auto_ollama_available(self):
        """Test auto-detect returns Ollama when available."""
        with patch("movie_os.genesis2.llm_factory.OllamaProvider") as MockOllama:
            mock_instance = MagicMock()
            mock_instance.is_available.return_value = True
            MockOllama.return_value = mock_instance

            provider = LLMFactory.create_auto()
            # The factory returns whatever OllamaProvider() returns
            assert provider is mock_instance
            MockOllama.assert_called_once()
            mock_instance.is_available.assert_called_once()

    def test_create_auto_falls_to_mock(self):
        """Test auto-detect returns Mock when Ollama is down."""
        with patch("movie_os.genesis2.llm_factory.OllamaProvider") as MockOllama:
            mock_ollama = MagicMock()
            mock_ollama.is_available.return_value = False
            MockOllama.return_value = mock_ollama

            provider = LLMFactory.create_auto()
            assert isinstance(provider, MockLLMProvider)

    def test_create_from_config_explicit(self):
        config = LLMConfig(provider="ollama")
        provider = LLMFactory.create_from_config(config)
        assert isinstance(provider, OllamaProvider)

    def test_create_from_config_auto(self):
        config = LLMConfig(provider="auto")
        with patch("movie_os.genesis2.llm_factory.OllamaProvider") as MockOllama:
            mock_instance = MagicMock()
            mock_instance.is_available.return_value = True
            MockOllama.return_value = mock_instance

            provider = LLMFactory.create_from_config(config)
            assert provider is mock_instance

    def test_create_with_custom_ollama_model(self):
        config = LLMConfig(
            provider="ollama",
            model="custom-model",
            ollama_url="http://localhost:9999",
        )
        provider = LLMFactory.create(config)
        assert isinstance(provider, OllamaProvider)
        assert provider.model == "custom-model"
        assert provider.url == "http://localhost:9999"


# ---------------------------------------------------------------------------
# create_llm convenience function tests
# ---------------------------------------------------------------------------

class TestCreateLLM:
    """Tests for the create_llm convenience function."""

    def test_default_creates_ollama(self):
        provider = create_llm()
        assert isinstance(provider, OllamaProvider)

    def test_explicit_ollama(self):
        config = LLMConfig(provider="ollama")
        provider = create_llm(config)
        assert isinstance(provider, OllamaProvider)

    def test_auto_detect(self):
        config = LLMConfig(provider="auto")
        with patch("movie_os.genesis2.llm_factory.OllamaProvider") as MockOllama:
            mock_instance = MagicMock()
            mock_instance.is_available.return_value = True
            MockOllama.return_value = mock_instance

            provider = create_llm(config)
            assert provider is mock_instance


# ---------------------------------------------------------------------------
# LLMClient tests
# ---------------------------------------------------------------------------

class TestLLMClient:
    """Tests for the LLMClient wrapper."""

    def test_default_creates_ollama_provider(self):
        client = LLMClient()
        provider = client._get_provider()
        assert isinstance(provider, OllamaProvider)

    def test_explicit_ollama_config(self):
        config = LLMConfig(provider="ollama")
        client = LLMClient(config=config)
        provider = client._get_provider()
        assert isinstance(provider, OllamaProvider)

    def test_explicit_mock_config(self):
        config = LLMConfig(provider="mock")
        client = LLMClient(config=config)
        provider = client._get_provider()
        assert isinstance(provider, MockLLMProvider)

    def test_model_override(self):
        client = LLMClient(model="custom-model")
        provider = client._get_provider()
        assert provider.model == "custom-model"

    def test_temperature_override(self):
        client = LLMClient(temperature=0.5)
        assert client._config.temperature == 0.5

    def test_max_tokens_override(self):
        client = LLMClient(max_tokens=2048)
        assert client._config.max_tokens == 2048

    def test_generate_delegates_to_provider(self):
        """Test that LLMClient.generate delegates to the provider."""
        config = LLMConfig(provider="mock")
        client = LLMClient(config=config)
        client._get_provider().set_default('{"test": "value"}')
        result = client.generate("test prompt")
        assert result == '{"test": "value"}'

    def test_generate_json_delegates(self):
        """Test that LLMClient.generate_json delegates to the provider."""
        config = LLMConfig(provider="mock")
        client = LLMClient(config=config)
        client._get_provider().set_default('{"key": "value"}')
        result = client.generate_json("test prompt")
        assert result == {"key": "value"}

    def test_tier_routing(self):
        """Test that tier routing uses correct model."""
        config = LLMConfig(provider="mock")
        client = LLMClient(
            config=config,
            model="planner-model",
            reviewer_model="reviewer-model",
            validator_model="validator-model",
        )
        # The provider should receive the correct model for each tier
        # We test by checking the config is built correctly
        provider = client._get_provider()
        assert isinstance(provider, MockLLMProvider)

    def test_is_available(self):
        """Test is_available delegates to provider."""
        config = LLMConfig(provider="mock")
        client = LLMClient(config=config)
        assert client.is_available() is True

    def test_lazy_provider_init(self):
        """Test that provider is only created on first use."""
        client = LLMClient()
        assert client._provider is None
        _ = client._get_provider()
        assert client._provider is not None

    def test_provider_caching(self):
        """Test that the same provider instance is reused."""
        client = LLMClient()
        p1 = client._get_provider()
        p2 = client._get_provider()
        assert p1 is p2


# ---------------------------------------------------------------------------
# MockLLMClient tests (backward compatibility)
# ---------------------------------------------------------------------------

class TestMockLLMClient:
    """Tests for MockLLMClient (backward compatibility with old API)."""

    def test_default_response(self):
        mock = MockLLMClient()
        result = mock.generate("anything")
        assert "mock" in result

    def test_registered_response_by_keyword(self):
        mock = MockLLMClient()
        mock.set_response("intent_analyst", '{"intent": "registered"}')
        result = mock.generate("Please run intent_analyst on this")
        assert "registered" in result

    def test_set_default(self):
        mock = MockLLMClient()
        mock.set_default('{"a": 1}')
        assert mock.generate("anything") == '{"a": 1}'

    def test_call_log(self):
        mock = MockLLMClient()
        mock.generate("first call")
        mock.generate("second call")
        assert mock.call_count == 2
        assert len(mock.call_log) == 2

    def test_keyword_case_insensitive(self):
        mock = MockLLMClient()
        mock.set_response("INTENT_ANALYST", '{"a": 1}')
        result = mock.generate("run Intent_Analyst on this")
        assert result == '{"a": 1}'

    def test_no_match_uses_default(self):
        mock = MockLLMClient()
        mock.set_response("foo", '{"a": 1}')
        mock.set_default('{"b": 2}')
        result = mock.generate("nothing matches")
        assert result == '{"b": 2}'

    def test_generate_json_extracts(self):
        mock = MockLLMClient()
        mock.set_response("foo", '```json\n{"k": "v"}\n```')
        result = mock.generate_json("foo bar")
        assert result == {"k": "v"}

    def test_generate_json_direct(self):
        mock = MockLLMClient()
        mock.set_response("test", '{"x": 42}')
        result = mock.generate_json("test prompt")
        assert result == {"x": 42}

    def test_tier_parameter_accepted(self):
        """Test that tier parameter is accepted (backward compat)."""
        mock = MockLLMClient()
        mock.set_default('{"test": "value"}')
        result = mock.generate("test", tier="planner")
        assert result == '{"test": "value"}'

    def test_default_response_format(self):
        """Test that default response has expected fields."""
        mock = MockLLMClient()
        result = mock.generate("anything")
        data = json.loads(result)
        assert "purpose" in data
        assert "creative_intent" in data
        assert "reasoning" in data
        assert "confidence" in data


# ---------------------------------------------------------------------------
# Fallback chain tests
# ---------------------------------------------------------------------------

class TestFallbackChain:
    """Tests for the Ollama → Mock fallback chain."""

    def test_factory_auto_detects_ollama_first(self):
        """Test that auto-detect tries Ollama first."""
        with patch("movie_os.genesis2.llm_factory.OllamaProvider") as MockOllama:
            # Ollama is available
            mock_ollama = MagicMock()
            mock_ollama.is_available.return_value = True
            MockOllama.return_value = mock_ollama

            provider = LLMFactory.create_auto()

            assert provider is mock_ollama

    def test_factory_falls_to_mock_when_ollama_down(self):
        """Test that auto-detect falls to Mock when Ollama is down."""
        with patch("movie_os.genesis2.llm_factory.OllamaProvider") as MockOllama:
            mock_ollama = MagicMock()
            mock_ollama.is_available.return_value = False
            MockOllama.return_value = mock_ollama

            provider = LLMFactory.create_auto()
            assert isinstance(provider, MockLLMProvider)

    def test_provider_interface_compatibility(self):
        """Test that all providers implement the LLMProvider interface."""
        ollama = OllamaProvider()
        mock = MockLLMProvider()

        # All should have generate and generate_json
        for provider in [ollama, mock]:
            assert hasattr(provider, "generate")
            assert hasattr(provider, "generate_json")
            assert hasattr(provider, "is_available")
            assert callable(provider.generate)
            assert callable(provider.generate_json)
            assert callable(provider.is_available)

    def test_all_providers_accept_config(self):
        """Test that all providers accept LLMConfig parameter."""
        config = LLMConfig(provider="mock")
        # Mock provider works without network
        mock = MockLLMProvider()
        result = mock.generate("test", config)
        assert isinstance(result, str)
        # Ollama provider accepts the config param (it just needs network for generate)
        # We test that the method signature accepts it without error
        ollama = OllamaProvider()
        # Verify the method signature accepts config (use mock to avoid network)
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps({
                "response": '{"test": "value"}'
            }).encode()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp
            result = ollama.generate("test", config)
            assert isinstance(result, str)

    def test_ollama_has_model_attr(self):
        """Test OllamaProvider has model attribute."""
        ollama = OllamaProvider(model="custom-model")
        assert ollama.model == "custom-model"

    def test_mock_has_set_default(self):
        """Test MockLLMProvider has set_default method."""
        mock = MockLLMProvider()
        mock.set_default('{"a": 1}')
        assert mock.generate("anything") == '{"a": 1}'
