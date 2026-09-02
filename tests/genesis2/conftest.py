"""Pytest fixtures for genesis2 tests."""
from __future__ import annotations

import pytest
from movie_os.genesis2.llm_client import MockLLMClient


@pytest.fixture
def good_mock() -> MockLLMClient:
    """A MockLLMClient that returns valid JSON responses."""
    return MockLLMClient()
