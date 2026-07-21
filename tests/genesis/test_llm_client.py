"""Unit tests for movie_os.genesis.llm_client."""

from __future__ import annotations

import json
import urllib.error

import pytest

from movie_os.genesis.llm_client import LLMClient, MockLLMClient


class TestLLMClientExtractJson:
    """Tests for the static JSON extraction helper."""

    def test_direct_json(self):
        text = '{"intent": "hello", "confidence": "inferred"}'
        result = LLMClient._extract_json(text)
        assert result == {"intent": "hello", "confidence": "inferred"}

    def test_json_in_markdown_fence(self):
        text = '```json\n{"intent": "hello"}\n```'
        result = LLMClient._extract_json(text)
        assert result == {"intent": "hello"}

    def test_json_in_plain_fence(self):
        text = '```\n{"intent": "hello"}\n```'
        result = LLMClient._extract_json(text)
        assert result == {"intent": "hello"}

    def test_json_with_surrounding_text(self):
        text = 'Here is the JSON:\n{"intent": "hello"}\nDone.'
        result = LLMClient._extract_json(text)
        assert result == {"intent": "hello"}

    def test_invalid_json_raises(self):
        text = "no json at all here, just text"
        with pytest.raises(ValueError) as exc:
            LLMClient._extract_json(text)
        assert "Could not extract JSON" in str(exc.value)

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            LLMClient._extract_json("")

    def test_nested_json(self):
        text = json.dumps({"outer": {"inner": [1, 2, 3]}, "x": True})
        result = LLMClient._extract_json(text)
        assert result["outer"]["inner"] == [1, 2, 3]


class TestMockLLMClient:
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
        assert mock.call_log[0] == "first call"
        assert mock.call_log[1] == "second call"

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


class TestLLMClient:
    def test_url_trailing_slash_stripped(self):
        client = LLMClient(url="http://example.com/")
        assert client.url == "http://example.com"

    def test_defaults(self):
        client = LLMClient()
        assert client.model == "qwen3-coder"
        assert client.temperature == 0.7
        assert client.max_tokens == 4096
        assert client.timeout == 120.0

    def test_custom_config(self):
        client = LLMClient(
            url="http://localhost:1234",
            model="custom-model",
            temperature=0.2,
            max_tokens=2048,
            timeout=30.0,
        )
        assert client.url == "http://localhost:1234"
        assert client.model == "custom-model"
        assert client.temperature == 0.2
        assert client.max_tokens == 2048
        assert client.timeout == 30.0

    def test_generate_json_delegates(self, monkeypatch):
        client = LLMClient()
        # Stub the actual generate to avoid network
        monkeypatch.setattr(
            client, "generate", lambda prompt, system="": '{"k": "v"}'
        )
        result = client.generate_json("anything")
        assert result == {"k": "v"}
