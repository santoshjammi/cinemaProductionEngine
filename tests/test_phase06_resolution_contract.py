"""Targeted tests for the terminal-resolution contract (GIRI-EP0006-REQ008).

Covers:
  - positive: resolution required and explicitly realized -> PASS
  - negative: arc ends on revelation/climax only -> FAIL
  - negative_sparse: resolution scene with only title+beat -> FAIL
  - regression: episodes without mandatory resolution -> unchanged
"""
from __future__ import annotations

import asyncio
import json

from movie_os.genesis2.llm_client import MockLLMClient
from movie_os.genesis2.phases.phase05_narrative_expansion import NarrativeExpansionPhase
from movie_os.genesis2.phases.phase06_scene_planning import ScenePlanningPhase


class _FakeCfg:
    def __init__(self, max_tokens: int = 4096):
        self.max_tokens = max_tokens

    def model_dump(self):
        return {"max_tokens": self.max_tokens, "provider": "ollama", "model": "qwen3:4b", "temperature": 0.7, "timeout": 120}


class _BudgetProbeLLM(MockLLMClient):
    def __init__(self, response: dict | str):
        super().__init__({"Phase 05": json.dumps(response) if isinstance(response, dict) else response})
        self._config = _FakeCfg()
        self._payload = response if isinstance(response, dict) else json.loads(response)

    def _get_provider(self):
        return self

    def generate_json(self, prompt, tier="planner", phase_name=None, task_key=None, response_format=None):  # type: ignore[override]
        return json.loads(json.dumps(self._payload))


def _resolution_manifest() -> list[dict]:
    """A manifest that mandates a RESOLUTION requirement (REQ-008)."""
    return [
        {"id": "REQ-001", "category": "INCIDENT", "statement": "An incident disrupts the ordinary world.", "obligation": "MUST"},
        {"id": "REQ-008", "category": "RESOLUTION", "statement": "Mark and Sarah move toward reconnection.", "obligation": "MUST", "semantic_role": "RESOLUTION"},
    ]


def _no_resolution_manifest() -> list[dict]:
    """A manifest with NO mandatory resolution requirement (regression)."""
    return [
        {"id": "REQ-001", "category": "INCIDENT", "statement": "An incident disrupts the ordinary world.", "obligation": "MUST"},
    ]


def _pkg(manifest: list[dict]) -> dict:
    return {
        "synopsis": "Mark hides something from Sarah, then they reconnect.",
        "constraints": {"canonical_requirements": manifest},
        "phase_01": {"purpose": "p1"},
        "phase_02": {"purpose": "p2"},
        "phase_03": {"purpose": "p3"},
        "phase_04": {"purpose": "p4"},
    }


# ---------------------------------------------------------------------------
# Phase 05 — narrative expansion
# ---------------------------------------------------------------------------

def _p05_arc(beats: list[str]) -> dict:
    scenes = [
        {"scene_number": i + 1, "act": "A", "sequence": "S", "objective": "o", "conflict": "c",
         "outcome": "out", "emotional_objective": "e", "narrative_beat": b}
        for i, b in enumerate(beats)
    ]
    return {
        "purpose": "expand", "creative_intent": "ci", "reasoning": "r", "confidence": "confirmed",
        "acts": [{"name": "A", "description": "d", "sequences": []}],
        "sequences": [{"name": "S", "act": "A", "scenes": []}],
        "scenes": scenes,
    }


def test_phase05_prompt_requires_resolution_when_manifest_mandates():
    """The Phase05 prompt must include the Terminal Resolution Contract when a
    RESOLUTION requirement is mandated."""
    phase = NarrativeExpansionPhase(MockLLMClient({}))
    prompt = phase.build_draft_prompt(_pkg(_resolution_manifest()))
    assert "Terminal Resolution Contract" in prompt
    assert "REQ-008" in prompt
    assert "resolution" in prompt.lower()


def test_phase05_prompt_omits_resolution_when_not_mandated():
    """Regression: no resolution contract when the manifest has none."""
    phase = NarrativeExpansionPhase(MockLLMClient({}))
    prompt = phase.build_draft_prompt(_pkg(_no_resolution_manifest()))
    assert "Terminal Resolution Contract" not in prompt


def test_phase05_arc_ending_on_climax_only_still_parses():
    """Phase05 parse is permissive (the freeze gate enforces coverage). An arc
    ending on climax only must still parse without crashing."""
    llm = _BudgetProbeLLM(_p05_arc(["hook", "plot", "climax"]))
    phase = NarrativeExpansionPhase(llm)
    knowledge = phase.parse_draft(_p05_arc(["hook", "plot", "climax"]))
    assert len(knowledge.scenes) == 3
    assert knowledge.scenes[-1].narrative_beat == "climax"


# ---------------------------------------------------------------------------
# Phase 06 — scene planning (fail closed)
# ---------------------------------------------------------------------------

def _p06_scenes(scenes: list[dict]) -> dict:
    return {
        "purpose": "plan", "creative_intent": "ci", "reasoning": "r", "confidence": "confirmed",
        "scenes": scenes,
    }


def _p06_scene(sn: int, beat: str, purpose: str = "p", conflict: str = "c", outcome: str = "o") -> dict:
    return {
        "scene_number": sn, "title": f"Scene {sn}", "purpose": purpose, "conflict": conflict,
        "emotion": "e", "visual_goal": "v", "audio_goal": "a", "character_goal": "g",
        "transition": "t", "duration": "30", "dependencies": [], "narrative_beat": beat,
    }


def test_phase06_resolution_required_and_realized_passes():
    """Positive: resolution required and a resolution scene with full semantic
    fields is present -> validation passes."""
    llm = _BudgetProbeLLM(_p06_scenes([
        _p06_scene(1, "hook"),
        _p06_scene(2, "plot"),
        _p06_scene(3, "climax"),
        _p06_scene(4, "resolution", purpose="They reconcile", conflict="tension eases", outcome="reconnect"),
    ]))
    phase = ScenePlanningPhase(llm)
    pkg = _pkg(_resolution_manifest())
    result = asyncio.run(phase.run(pkg))
    assert result.status.value == "completed"
    assert not [i for i in result.validation_issues if i.severity == "error"]


def test_phase06_arc_ends_on_climax_only_fails():
    """Negative: resolution required but arc ends on climax only -> FAIL."""
    llm = _BudgetProbeLLM(_p06_scenes([
        _p06_scene(1, "hook"),
        _p06_scene(2, "plot"),
        _p06_scene(3, "climax"),
    ]))
    phase = ScenePlanningPhase(llm)
    pkg = _pkg(_resolution_manifest())
    result = asyncio.run(phase.run(pkg))
    assert result.status.value == "failed"
    assert any("RESOLUTION" in (i.description or "") for i in result.validation_issues)


def test_phase06_resolution_scene_title_and_beat_only_fails():
    """Negative sparse: resolution scene with only title+beat (empty semantic
    fields) -> FAIL."""
    llm = _BudgetProbeLLM(_p06_scenes([
        _p06_scene(1, "hook"),
        _p06_scene(2, "plot"),
        _p06_scene(3, "climax"),
        _p06_scene(4, "resolution", purpose="", conflict="", outcome=""),
    ]))
    phase = ScenePlanningPhase(llm)
    pkg = _pkg(_resolution_manifest())
    result = asyncio.run(phase.run(pkg))
    assert result.status.value == "failed"
    assert any("non-empty purpose" in (i.description or "") for i in result.validation_issues)

def test_phase06_no_resolution_required_unchanged():
    """Regression: manifest without mandatory resolution -> arc ending on
    climax is fine (unchanged behavior)."""
    llm = _BudgetProbeLLM(_p06_scenes([
        _p06_scene(1, "hook"),
        _p06_scene(2, "plot"),
        _p06_scene(3, "climax"),
    ]))
    phase = ScenePlanningPhase(llm)
    pkg = _pkg(_no_resolution_manifest())
    result = asyncio.run(phase.run(pkg))
    assert result.status.value == "completed"
    assert not [i for i in result.validation_issues if i.severity == "error"]
