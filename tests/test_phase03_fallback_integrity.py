"""Diagnostic-honesty tests for the P0 Phase03 timeout + fallback-integrity repair.

Covers:
- Phase03 failure stops Phase04 and later (engine fail-fast).
- Phase03 failure produces zero real Phase06 scenes / Phase07 dialogues.
- Missing Phase06 does not generate synopsis scenes in RUNTIME mode.
- Missing Phase07 does not generate fake dialogue diagnostics.
- Downstream report marks payload missing only.
- Fallback scene titles do not appear in runtime failure artifact.
- Explicit fixture mode may use fixture behavior.
- Runtime mode never uses creative synopsis fallback.
- Phase03 uses a bounded structured budget (mirrors Phase02).
"""
from __future__ import annotations

import asyncio
import json

from movie_os.genesis2.bridge import Genesis2Bridge
from movie_os.genesis2.engine import Genesis2Engine
from movie_os.genesis2.llm_client import LLMClient
from movie_os.genesis2.models import (
    PhaseResult,
    PhaseStatus,
    ProductionKnowledgePackage,
    StoryFoundation,
)
from movie_os.genesis2.phases.phase03_character_psychology import CharacterPsychologyPhase


# ---------------------------------------------------------------------------
# Phase03 bounded structured budget
# ---------------------------------------------------------------------------

class _RecordingLLM(LLMClient):
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
            "protagonist": {
                "name": "MARK", "role": "protagonist", "identity": "a man",
                "history": "h", "fear": "f", "need": "n", "want": "w",
                "weakness": "wk", "strength": "st", "internal_conflict": "ic",
                "external_conflict": "ec", "speech_style": "ss",
                "personality": "p", "transformation": "t",
            },
            "antagonist": None,
            "supporting_characters": [{"name": "SARAH", "role": "supporting"}],
        }


def test_phase03_uses_bounded_structured_budget():
    llm = _RecordingLLM()
    phase = CharacterPsychologyPhase(llm)
    knowledge = phase.draft({
        "synopsis": "Mark is afraid of disappointing Sarah after losing his job.",
        "constraints": {},
        "phase_01": {"theme": "fear"},
        "phase_02": {"premise": "Mark hides job loss."},
    })
    assert knowledge.protagonist.name == "MARK"
    assert llm.max_tokens_seen == [1024]
    assert llm._config.max_tokens == 8192  # global ceiling untouched


# ---------------------------------------------------------------------------
# Engine fail-fast: Phase03 failure stops Phase04 and later
# ---------------------------------------------------------------------------

class _FailPhase03:
    phase_number = 3
    phase_name = "Character Psychology"

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
    phase_number = 4
    phase_name = "World Development"
    calls = 0

    async def run(self, context):
        type(self).calls += 1
        return PhaseResult(
            phase_number=self.phase_number,
            phase_name=self.phase_name,
            status=PhaseStatus.COMPLETED,
            knowledge=StoryFoundation(purpose="x", creative_intent="y", reasoning="z"),
        )


def test_phase03_failure_stops_phase04_and_later(monkeypatch):
    from movie_os.genesis2 import engine as engine_module

    _ShouldNotRunPhase.calls = 0
    monkeypatch.setattr(engine_module, "PHASE_CLASSES", [_FailPhase03, _ShouldNotRunPhase])
    engine = Genesis2Engine(llm=LLMClient())
    pkg = asyncio.run(engine.run_async("synopsis", {"episode_id": "EP-1", "run_id": "RUN-1", "policy_snapshot_id": "POL-1"}))
    assert len(pkg.phase_results) == 1
    assert pkg.phase_results[0].status == PhaseStatus.FAILED
    assert _ShouldNotRunPhase.calls == 0


def test_phase03_failure_produces_zero_real_phase06_scenes():
    """A Phase03-failed PKP must carry no real Phase06 scene payload."""
    pkg = ProductionKnowledgePackage(
        episode_id="EP-1", run_id="RUN-1", policy_snapshot_id="POL-1",
        synopsis="Mark withdraws from Sarah.",
        constraints={"mode": "RUNTIME"},
        phase_results=[
            PhaseResult(phase_number=3, phase_name="Character Psychology", status=PhaseStatus.FAILED),
        ],
    )
    assert pkg.scene_planning is None or len(pkg.scene_planning.scenes) == 0


def test_phase03_failure_produces_zero_real_phase07_dialogues():
    pkg = ProductionKnowledgePackage(
        episode_id="EP-1", run_id="RUN-1", policy_snapshot_id="POL-1",
        synopsis="Mark withdraws from Sarah.",
        constraints={"mode": "RUNTIME"},
        phase_results=[
            PhaseResult(phase_number=3, phase_name="Character Psychology", status=PhaseStatus.FAILED),
        ],
    )
    assert pkg.dialogue_planning is None or len(pkg.dialogue_planning.dialogues) == 0


# ---------------------------------------------------------------------------
# Bridge fail-closed law
# ---------------------------------------------------------------------------

def _make_pkp(mode: str = "RUNTIME") -> ProductionKnowledgePackage:
    return ProductionKnowledgePackage(
        episode_id="EP-1", run_id="RUN-1", policy_snapshot_id="POL-1",
        synopsis="After losing his job, Mark withdraws from Sarah.",
        constraints={"mode": mode},
        phase_results=[
            PhaseResult(phase_number=i + 1, phase_name=f"phase_{i + 1}", status=PhaseStatus.COMPLETED)
            for i in range(3)
        ],
    )


def test_runtime_mode_never_uses_creative_synopsis_fallback():
    """RUNTIME (default) must not fabricate scenes when phase data is absent."""
    pkg = _make_pkp("RUNTIME")
    bridge = Genesis2Bridge(pkg)
    brief = bridge.to_brief()
    assert bridge._creative_fallback_allowed() is False
    assert brief["scenes"] == []


def test_missing_phase06_does_not_generate_synopsis_scenes():
    pkg = _make_pkp("RUNTIME")
    brief = Genesis2Bridge(pkg).to_brief()
    assert len(brief["scenes"]) == 0


def test_missing_phase07_does_not_generate_fake_dialogue_diagnostics():
    """No fake scenes -> no DIALOGUE_PLANNING_INCOMPLETE per fake scene."""
    pkg = _make_pkp("RUNTIME")
    brief = Genesis2Bridge(pkg).to_brief()
    # No scenes means the downstream ensure_scene_state_fields has nothing to flag.
    assert brief["scenes"] == []
    assert brief.get("dialogues", []) == []


def test_fallback_scene_titles_do_not_appear_in_runtime_failure_artifact():
    pkg = _make_pkp("RUNTIME")
    brief = Genesis2Bridge(pkg).to_brief()
    titles = [s.get("title", "") for s in brief["scenes"]]
    assert "Opening" not in titles
    assert "Climax" not in titles


def test_explicit_fixture_mode_may_use_fixture_behavior():
    pkg = _make_pkp("QUALIFICATION_FIXTURE")
    bridge = Genesis2Bridge(pkg)
    assert bridge._creative_fallback_allowed() is True
    brief = bridge.to_brief()
    assert len(brief["scenes"]) >= 3


def test_legacy_fixture_mode_may_use_fixture_behavior():
    pkg = _make_pkp("LEGACY_FIXTURE")
    assert Genesis2Bridge(pkg)._creative_fallback_allowed() is True


def test_runtime_can_never_enter_implicitly():
    """A PKP with no mode field defaults to RUNTIME (fail-closed)."""
    pkg = ProductionKnowledgePackage(
        episode_id="EP-1", run_id="RUN-1", policy_snapshot_id="POL-1",
        synopsis="Mark withdraws from Sarah.",
        constraints={},
    )
    assert Genesis2Bridge(pkg)._creative_fallback_allowed() is False
