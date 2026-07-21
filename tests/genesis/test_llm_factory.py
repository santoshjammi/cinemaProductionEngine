"""Unit tests for movie_os.genesis.llm_factory."""

from __future__ import annotations

import pytest

from movie_os.genesis.llm_factory import (
    create_client,
    create_tiered_clients,
    TIER_DISCOVERY,
    TIER_PKP,
    TIER_REVIEWER,
    TIER_CHIEF,
)
from movie_os.genesis.llm_client import MockLLMClient


class TestCreateClient:
    def test_mock_returns_rich_mock(self):
        client = create_client(mock=True)
        assert isinstance(client, MockLLMClient)
        # Rich mock has registered responses
        assert len(client._responses) > 0

    def test_auto_backend_returns_something(self):
        client = create_client()
        # Should return some client (mock fallback if no server)
        assert client is not None
        assert hasattr(client, "generate")

    def test_ollama_backend_creates_ollama_client(self, monkeypatch):
        monkeypatch.setattr(
            "movie_os.genesis.llm_config._detect_backend",
            lambda config: "ollama",
        )
        client = create_client(backend="ollama")
        from movie_os.genesis.llm_ollama import OllamaClient
        assert isinstance(client, OllamaClient)

    def test_lmstudio_backend_creates_lmstudio_client(self, monkeypatch):
        monkeypatch.setattr(
            "movie_os.genesis.llm_config._detect_backend",
            lambda config: "lmstudio",
        )
        client = create_client(backend="lmstudio")
        from movie_os.genesis.llm_client import LLMClient
        assert isinstance(client, LLMClient)

    def test_hf_backend_creates_hf_client(self, monkeypatch):
        monkeypatch.setattr(
            "movie_os.genesis.llm_config._detect_backend",
            lambda config: "hf",
        )
        client = create_client(backend="hf")
        from movie_os.genesis.llm_hf import HFClient
        assert isinstance(client, HFClient)

    def test_model_override(self, monkeypatch):
        monkeypatch.setattr(
            "movie_os.genesis.llm_config._detect_backend",
            lambda config: "ollama",
        )
        client = create_client(backend="ollama", model="custom-model")
        assert client.model == "custom-model"

    def test_url_override(self, monkeypatch):
        monkeypatch.setattr(
            "movie_os.genesis.llm_config._detect_backend",
            lambda config: "ollama",
        )
        client = create_client(backend="ollama", llm_url="http://localhost:9999")
        assert "9999" in client.url


class TestCreateTieredClients:
    def test_mock_returns_same_client_for_all_tiers(self):
        clients = create_tiered_clients(mock=True)
        assert len(clients) == 4
        assert TIER_DISCOVERY in clients
        assert TIER_PKP in clients
        assert TIER_REVIEWER in clients
        assert TIER_CHIEF in clients
        # All point to the same mock instance
        assert clients[TIER_DISCOVERY] is clients[TIER_PKP]

    def test_ollama_returns_same_client_for_all_tiers(self, monkeypatch):
        monkeypatch.setattr(
            "movie_os.genesis.llm_config._detect_backend",
            lambda config: "ollama",
        )
        clients = create_tiered_clients(backend="ollama")
        assert clients[TIER_DISCOVERY] is clients[TIER_PKP]

    def test_hf_returns_separate_clients(self, monkeypatch):
        monkeypatch.setattr(
            "movie_os.genesis.llm_config._detect_backend",
            lambda config: "hf",
        )
        clients = create_tiered_clients(backend="hf")
        from movie_os.genesis.llm_hf import HFClient
        assert isinstance(clients[TIER_DISCOVERY], HFClient)
        assert isinstance(clients[TIER_PKP], HFClient)
        # Each tier has its own client instance
        assert clients[TIER_DISCOVERY] is not clients[TIER_PKP]
