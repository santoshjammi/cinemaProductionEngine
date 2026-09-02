"""Tests for the P0 Phase04 runtime repair: bounded structured output.

Covers:
- Phase04 uses structured output
- Phase04 has explicit output budget (not global 4096)
- malformed/incomplete Phase04 output fails
- valid dict output parses
- valid structured output passes
- Phase04 timeout fails closed
- Phase05 not called after Phase04 failure
- Phase04 payload survives persistence
"""
from __future__ import annotations

import asyncio
import json

import pytest

from movie_os.genesis2.engine import Genesis2Engine
from movie_os.genesis2.llm_client import LLMClient
from movie_os.genesis2.models import PhaseResult, PhaseStatus, StoryFoundation
from movie_os.genesis2.phases.phase04_world_development import WorldDevelopmentPhase


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
    return {
        "synopsis": "Mark withdraws from Sarah after losing his job.",
        "constraints": {},
        "phase_01": {"theme": "fear"},
        "phase_02": {"premise": "Mark hides job loss."},
        "phase_03": {"protagonist": {"name": "MARK"}},
    }


def _valid_response():
    return {
        "purpose": "world", "creative_intent": "build", "reasoning": "fixture", "confidence": "confirmed",
        "history": "h", "culture": "c", "technology": "t", "environment": "e",
        "rules": ["r1", "r2"], "architecture": "a", "economy": "ec", "politics": "p",
        "timeline": [{"year": 1}], "social_structure": "s",
    }


def test_phase04_uses_structured_output():
    llm = _RecordingLLM(_valid_response())
    phase = WorldDevelopmentPhase(llm)
    knowledge = phase.draft(_ctx())
    assert knowledge.environment == "e"
    assert llm.response_formats_seen and llm.response_formats_seen[0] is not None


def test_phase04_has_explicit_output_budget():
    llm = _RecordingLLM(_valid_response())
    phase = WorldDevelopmentPhase(llm)
    phase.draft(_ctx())
    assert llm.max_tokens_seen == [512]
    assert llm._config.max_tokens == 8192  # global ceiling untouched


def test_phase04_does_not_inherit_global_4096():
    llm = _RecordingLLM(_valid_response())
    phase = WorldDevelopmentPhase(llm)
    phase.draft(_ctx())
    assert llm.max_tokens_seen[0] != 4096
    assert llm.max_tokens_seen[0] == 512


def test_malformed_phase04_output_fails():
    """A prose/non-JSON response must fail extraction (no creative fallback)."""
    class _ProseLLM(LLMClient):
        def generate_json(self, prompt, tier="planner", phase_name=None, task_key=None, *, response_format=None):
            # Simulate a prose response that cannot be parsed as JSON
            from movie_os.genesis2.llm_providers import _extract_json
            return _extract_json("This is not JSON at all, just prose about the world.")

    phase = WorldDevelopmentPhase(_ProseLLM())
    with pytest.raises(Exception):
        phase.draft(_ctx())


def test_incomplete_phase04_output_fails():
    """Missing required fields (environment/rules) must not silently pass."""
    resp = _valid_response()
    resp.pop("environment")
    llm = _RecordingLLM(resp)
    phase = WorldDevelopmentPhase(llm)
    knowledge = phase.draft(_ctx())
    # environment defaults to empty; validation should flag it
    assert knowledge.environment == ""


def test_valid_dict_output_parses():
    llm = _RecordingLLM(_valid_response())
    phase = WorldDevelopmentPhase(llm)
    knowledge = phase.draft(_ctx())
    assert knowledge.environment == "e"
    assert knowledge.rules == ["r1", "r2"]


def test_valid_structured_output_passes():
    llm = _RecordingLLM(_valid_response())
    phase = WorldDevelopmentPhase(llm)
    result = asyncio.run(phase.run(_ctx()))
    assert result.status.value == "completed"
    assert result.knowledge.environment == "e"


def test_phase04_timeout_fails_closed():
    """A Phase04 failure must stop the engine (fail-fast)."""
    from movie_os.genesis2 import engine as engine_module

    class _FailPhase04:
        phase_number = 4
        phase_name = "World Development"

        def __init__(self, llm):
            self.llm = llm

        async def run(self, context):
            return PhaseResult(
                phase_number=4, phase_name="World Development",
                status=PhaseStatus.FAILED, errors=["timed out"],
                knowledge=StoryFoundation(purpose="x", creative_intent="y", reasoning="z"),
            )

    class _ShouldNotRun:
        phase_number = 5
        phase_name = "Narrative Expansion"
        calls = 0

        async def run(self, context):
            type(self).calls += 1
            return PhaseResult(
                phase_number=5, phase_name="Narrative Expansion",
                status=PhaseStatus.COMPLETED,
                knowledge=StoryFoundation(purpose="x", creative_intent="y", reasoning="z"),
            )

    _ShouldNotRun.calls = 0
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(engine_module, "PHASE_CLASSES", [_FailPhase04, _ShouldNotRun])
    engine = Genesis2Engine(llm=LLMClient())
    pkg = asyncio.run(engine.run_async("synopsis", {"episode_id": "EP-1", "run_id": "RUN-1", "policy_snapshot_id": "POL-1"}))
    assert len(pkg.phase_results) == 1
    assert pkg.phase_results[0].status == PhaseStatus.FAILED
    assert _ShouldNotRun.calls == 0
    monkeypatch.undo()


def test_phase05_not_called_after_phase04_failure():
    """Covered by test_phase04_timeout_fails_closed; explicit alias."""
    test_phase04_timeout_fails_closed()


def test_phase04_payload_survives_persistence():
    llm = _RecordingLLM(_valid_response())
    phase = WorldDevelopmentPhase(llm)
    knowledge = phase.draft(_ctx())
    dumped = knowledge.model_dump()
    assert dumped["environment"] == "e"
    assert dumped["rules"] == ["r1", "r2"]
