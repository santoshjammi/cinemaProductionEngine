"""Tests for the LMStudio client (no actual LLM calls — we test the wrapper)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest

from story_factory.llm_client import chat, LLMError


class TestLLMClient:
    def test_connection_error_raises_llmerror(self):
        """When LMStudio is unreachable, we should get a clean LLMError."""
        with pytest.raises(LLMError) as exc_info:
            chat(
                system="test",
                user="test",
                base_url="http://localhost:1",  # nothing listens here
                timeout=2,
            )
        assert "LMStudio" in str(exc_info.value)

    def test_invalid_url_raises_llmerror(self):
        with pytest.raises(LLMError):
            chat(
                system="test",
                user="test",
                base_url="http://this-domain-does-not-exist-abc123.invalid",
                timeout=2,
            )
