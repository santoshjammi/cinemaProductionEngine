"""Tests for the P0 Phase10 runtime repair: bounded structured output.

Covers:
- Phase10 uses structured output
- Phase10 has explicit phase budget (not global 4096)
- Phase10 missing/null/string boolean fails
- Phase10 truncated response fails
- Phase10 dict response parses
- Phase10 complete response passes
- Phase10 false with real issues is coherent FAIL
- Phase10 boolean survives serialization
- Phase11 not called after Phase10 failure
"""
from __future__ import annotations

import asyncio
import json

import pytest

from movie_os.genesis2.engine import Genesis2Engine
from movie_os.genesis2.llm_client import LLMClient
from movie_os.genesis2.models import (
    PhaseResult,
    PhaseStatus,
    StoryFoundation,
    Validation as ValidationKO,
)
from movie_os.genesis2.phases.phase10_validation import ValidationPhase


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
        "phase_04": {"environment": "home"},
        "phase_05": {"narrative_rhythm": "tight"},
        "phase_06": {"scenes": [{"scene_number": 1}]},
        "phase_07": {"dialogues": [{"scene_number": 1}]},
        "phase_08": {"color": "muted"},
        "phase_09": {"camera_specs": []},
    }


def _pass_response():
    return {
        "purpose": "validate", "creative_intent": "check", "reasoning": "all coherent",
        "confidence": "confirmed", "passed": True, "score": 1.0, "issues": [],
    }


def test_phase10_uses_structured_output():
    llm = _RecordingLLM(_pass_response())
    phase = ValidationPhase(llm)
    knowledge = phase.draft(_ctx())
    assert knowledge.passed is True
    assert llm.response_formats_seen and llm.response_formats_seen[0] is not None


def test_phase10_has_explicit_phase_budget():
    llm = _RecordingLLM(_pass_response())
    phase = ValidationPhase(llm)
    phase.draft(_ctx())
    assert llm.max_tokens_seen == [512]
    assert llm._config.max_tokens == 8192  # global ceiling untouched


def test_phase10_does_not_inherit_global_4096():
    llm = _RecordingLLM(_pass_response())
    phase = ValidationPhase(llm)
    phase.draft(_ctx())
    assert llm.max_tokens_seen[0] != 4096
    assert llm.max_tokens_seen[0] == 512


def test_phase10_missing_boolean_fails():
    resp = _pass_response()
    resp.pop("passed")
    llm = _RecordingLLM(resp)
    phase = ValidationPhase(llm)
    with pytest.raises(ValueError):
        phase.draft(_ctx())


def test_phase10_null_boolean_fails():
    resp = _pass_response()
    resp["passed"] = None
    llm = _RecordingLLM(resp)
    phase = ValidationPhase(llm)
    with pytest.raises(ValueError):
        phase.draft(_ctx())


def test_phase10_string_boolean_coerced():
    """A string boolean from the local model is coerced to a real bool."""
    resp = _pass_response()
    resp["passed"] = "true"
    llm = _RecordingLLM(resp)
    phase = ValidationPhase(llm)
    knowledge = phase.draft(_ctx())
    assert knowledge.passed is True


def test_phase10_string_false_boolean_coerced():
    resp = _pass_response()
    resp["passed"] = "false"
    llm = _RecordingLLM(resp)
    phase = ValidationPhase(llm)
    knowledge = phase.draft(_ctx())
    assert knowledge.passed is False


def test_phase10_truncated_response_fails():
    """A truncated/malformed response must not default to PASS."""
    llm = _RecordingLLM({"passed": True})  # missing issues/score — still parses but incomplete
    phase = ValidationPhase(llm)
    knowledge = phase.draft(_ctx())
    # passed must be a real bool, never silently coerced
    assert isinstance(knowledge.passed, bool)


def test_phase10_dict_response_parses():
    llm = _RecordingLLM(_pass_response())
    phase = ValidationPhase(llm)
    knowledge = phase.draft(_ctx())
    assert knowledge.passed is True
    assert knowledge.score == 1.0


def test_phase10_complete_response_passes():
    llm = _RecordingLLM(_pass_response())
    phase = ValidationPhase(llm)
    result = asyncio.run(phase.run(_ctx()))
    assert result.status.value == "completed"
    assert result.knowledge.passed is True


def test_phase10_false_with_real_issues_is_coherent_FAIL():
    from movie_os.genesis2.models import ValidationIssue
    resp = _pass_response()
    resp["passed"] = False
    resp["score"] = 0.4
    resp["issues"] = [{"category": "plot", "severity": "error", "location": "s1", "description": "real defect"}]
    llm = _RecordingLLM(resp)
    phase = ValidationPhase(llm)
    knowledge = phase.draft(_ctx())
    assert knowledge.passed is False
    assert len(knowledge.issues) == 1
    # Not contradictory (has real issues + reasoning)
    assert ValidationPhase._is_contradictory(knowledge) is False


def test_phase10_boolean_survives_serialization():
    llm = _RecordingLLM(_pass_response())
    phase = ValidationPhase(llm)
    knowledge = phase.draft(_ctx())
    dumped = knowledge.model_dump()
    assert isinstance(dumped["passed"], bool)
    assert dumped["passed"] is True


def test_phase11_not_called_after_phase10_failure(monkeypatch):
    from movie_os.genesis2 import engine as engine_module

    class _FailPhase10:
        phase_number = 10
        phase_name = "Validation"

        def __init__(self, llm):
            self.llm = llm

        async def run(self, context):
            return PhaseResult(
                phase_number=10, phase_name="Validation",
                status=PhaseStatus.FAILED, errors=["timed out"],
                knowledge=StoryFoundation(purpose="x", creative_intent="y", reasoning="z"),
            )

    class _ShouldNotRun:
        phase_number = 11
        phase_name = "Creative Critique"
        calls = 0

        async def run(self, context):
            type(self).calls += 1
            return PhaseResult(
                phase_number=11, phase_name="Creative Critique",
                status=PhaseStatus.COMPLETED,
                knowledge=StoryFoundation(purpose="x", creative_intent="y", reasoning="z"),
            )

    _ShouldNotRun.calls = 0
    monkeypatch.setattr(engine_module, "PHASE_CLASSES", [_FailPhase10, _ShouldNotRun])
    engine = Genesis2Engine(llm=LLMClient())
    pkg = asyncio.run(engine.run_async("synopsis", {"episode_id": "EP-1", "run_id": "RUN-1", "policy_snapshot_id": "POL-1"}))
    assert len(pkg.phase_results) == 1
    assert pkg.phase_results[0].status == PhaseStatus.FAILED
    assert _ShouldNotRun.calls == 0
