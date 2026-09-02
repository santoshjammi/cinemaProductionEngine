from __future__ import annotations

import asyncio
import json

from movie_os.genesis2.llm_client import MockLLMClient
from movie_os.genesis2.models import KnowledgeObject
from movie_os.genesis2.phases.phase05_narrative_expansion import NarrativeExpansionPhase


class _FakeCfg:
    def __init__(self, max_tokens: int = 4096):
        self.max_tokens = max_tokens

    def model_dump(self):
        return {"max_tokens": self.max_tokens, "provider": "ollama", "model": "qwen3:4b", "temperature": 0.7, "timeout": 120}


class _BudgetProbeLLM(MockLLMClient):
    def __init__(self, response: dict | str):
        super().__init__({"Phase 05": json.dumps(response) if isinstance(response, dict) else response})
        self._config = _FakeCfg()
        self.seen_max_tokens: list[int] = []
        self._payload = response if isinstance(response, dict) else json.loads(response)

    def _get_provider(self):
        return self

    def generate_json(self, prompt, tier="planner", phase_name=None, task_key=None, response_format=None):  # type: ignore[override]
        self.seen_max_tokens.append(self._config.max_tokens)
        return json.loads(json.dumps(self._payload))


def _phase05_payload():
    return {
        "purpose": "expand story",
        "creative_intent": "coherent scene plan",
        "reasoning": "fixture",
        "confidence": "confirmed",
        "acts": [{"name": "Act 1", "description": "setup", "sequences": []}],
        "sequences": [{"name": "Seq 1", "act": "Act 1", "scenes": []}],
        "scenes": [
            {"scene_number": 1, "act": "Act 1", "sequence": "Seq 1", "objective": "open", "conflict": "silence", "outcome": "question", "emotional_objective": "worry", "narrative_beat": "hook"},
            {"scene_number": 2, "act": "Act 1", "sequence": "Seq 1", "objective": "deepen", "conflict": "avoidance", "outcome": "pressure", "emotional_objective": "guilt", "narrative_beat": "plot"},
            {"scene_number": 3, "act": "Act 2", "sequence": "Seq 2", "objective": "turn", "conflict": "truth", "outcome": "reveal", "emotional_objective": "fear", "narrative_beat": "turning_point"},
            {"scene_number": 4, "act": "Act 2", "sequence": "Seq 2", "objective": "push", "conflict": "distance", "outcome": "friction", "emotional_objective": "hurt", "narrative_beat": "plot"},
            {"scene_number": 5, "act": "Act 3", "sequence": "Seq 3", "objective": "resolve", "conflict": "reconciliation", "outcome": "reconnect", "emotional_objective": "relief", "narrative_beat": "climax"},
        ],
    }


def test_phase05_structured_output_roundtrip_accepts_dict():
    phase = NarrativeExpansionPhase(MockLLMClient({"Phase 05": json.dumps(_phase05_payload())}))
    knowledge = phase.parse_draft(_phase05_payload())
    assert len(knowledge.scenes) == 5
    assert knowledge.scenes[0].scene_number == 1


def test_phase05_missing_required_unit_fails():
    llm = _BudgetProbeLLM({
        "purpose": "expand story",
        "creative_intent": "coherent scene plan",
        "reasoning": "fixture",
        "confidence": "confirmed",
        "acts": [],
        "sequences": [],
        "scenes": [],
    })
    phase = NarrativeExpansionPhase(llm)
    pkg = {
        "synopsis": "Mark hides job loss from Sarah, then must confront it.",
        "constraints": {"canonical_requirements": []},
        "phase_01": {"purpose": "p1"},
        "phase_02": {"purpose": "p2"},
        "phase_03": {"purpose": "p3"},
        "phase_04": {"purpose": "p4"},
    }
    result = asyncio.run(phase.run(pkg))
    assert result.status.value == "failed"
    assert any("No scenes expanded" in issue.description or "scene" in issue.description.lower() for issue in result.validation_issues)


def test_phase05_has_explicit_output_budget_and_roundtrip():
    llm = _BudgetProbeLLM(_phase05_payload())
    phase = NarrativeExpansionPhase(llm)
    pkg = {
        "synopsis": "Mark hides job loss from Sarah, then must confront it.",
        "constraints": {"canonical_requirements": []},
        "phase_01": {"purpose": "p1"},
        "phase_02": {"purpose": "p2"},
        "phase_03": {"purpose": "p3"},
        "phase_04": {"purpose": "p4"},
    }
    result = asyncio.run(phase.run(pkg))
    assert result.status.value == "completed"
    assert llm.seen_max_tokens == [2560]
    assert llm._config.max_tokens == 4096
    assert result.knowledge is not None
    assert len(result.knowledge.scenes) == 5
    assert all(scene.narrative_beat for scene in result.knowledge.scenes)
