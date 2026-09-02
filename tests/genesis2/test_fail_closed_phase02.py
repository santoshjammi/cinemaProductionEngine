from __future__ import annotations

import asyncio
import json

from movie_os.genesis2.engine import Genesis2Engine
from movie_os.genesis2.llm_client import LLMClient
from movie_os.genesis2.models import PhaseResult, PhaseStatus, StoryFoundation
from movie_os.genesis2.phases.phase02_story_foundation import StoryFoundationPhase


class RecordingLLM(LLMClient):
    def __init__(self):
        super().__init__()
        self.max_tokens_seen: list[int | None] = []

    def generate_json(self, prompt, tier="planner", phase_name=None, task_key=None, *, response_format=None):
        self.max_tokens_seen.append(getattr(self._config, "max_tokens", None))
        return {
            "purpose": "mock purpose",
            "creative_intent": "mock intent",
            "reasoning": "mock reasoning",
            "confidence": "confirmed",
            "premise": "Mark hides job loss from Sarah.",
            "dramatic_question": "Will Mark tell Sarah the truth?",
            "acts": [],
            "major_events": [],
            "emotional_journey": [],
            "story_beats": [],
            "narrative_rhythm": "tight",
            "foreshadowing": [],
            "symbolism": [],
            "motifs": [],
        }


class _FailPhase:
    phase_number = 2
    phase_name = "Story Foundation"

    def __init__(self, llm):
        self.llm = llm

    async def run(self, context):
        return PhaseResult(
            phase_number=self.phase_number,
            phase_name=self.phase_name,
            status=PhaseStatus.FAILED,
            knowledge=StoryFoundation(purpose="x", creative_intent="y", reasoning="z"),
        )


class _ShouldNotRunPhase:
    phase_number = 3
    phase_name = "Character Psychology"
    calls = 0

    async def run(self, context):
        type(self).calls += 1
        return PhaseResult(
            phase_number=self.phase_number,
            phase_name=self.phase_name,
            status=PhaseStatus.COMPLETED,
            knowledge=StoryFoundation(purpose="x", creative_intent="y", reasoning="z"),
        )


def test_phase02_uses_explicit_budget():
    llm = RecordingLLM()
    phase = StoryFoundationPhase(llm)
    knowledge = phase.draft({"synopsis": "Mark is afraid of disappointing Sarah after losing his job.", "constraints": {}})
    assert knowledge.premise
    assert llm.max_tokens_seen == [1024]
    assert llm._config.max_tokens == 8192


def test_engine_stops_after_required_phase_failure(monkeypatch):
    from movie_os.genesis2 import engine as engine_module

    _ShouldNotRunPhase.calls = 0
    monkeypatch.setattr(engine_module, "PHASE_CLASSES", [_FailPhase, _ShouldNotRunPhase])
    engine = Genesis2Engine(llm=LLMClient())
    pkg = asyncio.run(engine.run_async("synopsis", {"episode_id": "EP-1", "run_id": "RUN-1", "policy_snapshot_id": "POL-1"}))
    assert len(pkg.phase_results) == 1
    assert pkg.phase_results[0].status == PhaseStatus.FAILED
    assert _ShouldNotRunPhase.calls == 0
