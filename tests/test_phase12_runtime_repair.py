"""Tests for the P0 Phase12 runtime repair: bounded structured output.

Covers:
- Phase12 uses structured output
- Phase12 has explicit output budget (not global 4096)
- malformed/incomplete Phase12 output fails
- valid dict output parses
- valid structured output passes
- Phase12 payload survives persistence
"""
from __future__ import annotations

import asyncio

import pytest

from movie_os.genesis2.llm_client import LLMClient
from movie_os.genesis2.phases.phase12_knowledge_integration import KnowledgeIntegrationPhase


class _RecordingLLM(LLMClient):
    def __init__(self, response: dict):
        super().__init__()
        self._response = response
        self.max_tokens_seen: list[int | None] = []
        self.response_formats_seen: list = []

    def generate_json(self, prompt, tier="planner", phase_name=None, task_key=None, *, response_format=None):
        self.max_tokens_seen.append(getattr(self._config, "max_tokens", None))
        self.response_formats_seen.append(response_format)
        return dict(self._response)


def _ctx():
    ctx = {"synopsis": "Mark withdraws from Sarah.", "constraints": {}}
    for i in range(1, 12):
        ctx[f"phase_{i:02d}"] = {"purpose": "x"}
    return ctx


def _valid_response():
    return {
        "purpose": "integrate", "creative_intent": "unify", "reasoning": "fixture", "confidence": "confirmed",
        "package": {"integrated": True, "summary": "all phases"},
        "knowledge_graph": {"nodes": [{"id": "n1", "type": "theme", "label": "fear"}], "edges": []},
        "asset_registry": [], "dependencies": [], "cross_references": [], "version_history": [],
    }


def test_phase12_uses_structured_output():
    llm = _RecordingLLM(_valid_response())
    phase = KnowledgeIntegrationPhase(llm)
    knowledge = phase.draft(_ctx())
    assert knowledge.package["integrated"] is True
    assert llm.response_formats_seen and llm.response_formats_seen[0] is not None


def test_phase12_has_explicit_output_budget():
    llm = _RecordingLLM(_valid_response())
    phase = KnowledgeIntegrationPhase(llm)
    phase.draft(_ctx())
    assert llm.max_tokens_seen == [512]
    assert llm._config.max_tokens == 8192  # global ceiling untouched


def test_phase12_does_not_inherit_global_4096():
    llm = _RecordingLLM(_valid_response())
    phase = KnowledgeIntegrationPhase(llm)
    phase.draft(_ctx())
    assert llm.max_tokens_seen[0] != 4096
    assert llm.max_tokens_seen[0] == 512


def test_malformed_phase12_output_fails():
    class _ProseLLM(LLMClient):
        def generate_json(self, prompt, tier="planner", phase_name=None, task_key=None, *, response_format=None):
            from movie_os.genesis2.llm_providers import _extract_json
            return _extract_json("This is not JSON at all, just prose.")

    phase = KnowledgeIntegrationPhase(_ProseLLM())
    with pytest.raises(Exception):
        phase.draft(_ctx())


def test_valid_dict_output_parses():
    llm = _RecordingLLM(_valid_response())
    phase = KnowledgeIntegrationPhase(llm)
    knowledge = phase.draft(_ctx())
    assert knowledge.package["integrated"] is True
    assert len(knowledge.knowledge_graph["nodes"]) == 1


def test_valid_structured_output_passes():
    llm = _RecordingLLM(_valid_response())
    phase = KnowledgeIntegrationPhase(llm)
    result = asyncio.run(phase.run(_ctx()))
    assert result.status.value == "completed"
    assert result.knowledge.package["integrated"] is True


def test_phase12_payload_survives_persistence():
    llm = _RecordingLLM(_valid_response())
    phase = KnowledgeIntegrationPhase(llm)
    knowledge = phase.draft(_ctx())
    dumped = knowledge.model_dump()
    assert dumped["package"]["integrated"] is True
    assert len(dumped["knowledge_graph"]["nodes"]) == 1
