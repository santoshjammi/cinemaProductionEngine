"""Tests for the P0 Phase05 canonical scene normalization.

The model may emit narrative scenes nested inside acts[].sequences[].scenes
while the flat authoritative scenes[] list stays empty.  Phase05 must
deterministically project nested scenes into the flat list before validation.
"""
from __future__ import annotations

import asyncio
import json

import pytest

from movie_os.genesis2.llm_client import MockLLMClient
from movie_os.genesis2.models import NarrativeExpansion, Scene
from movie_os.genesis2.phases.phase05_narrative_expansion import NarrativeExpansionPhase


def _nested_only_payload() -> dict:
    return {
        "purpose": "expand", "creative_intent": "arc", "reasoning": "fixture", "confidence": "confirmed",
        "acts": [
            {"name": "Act I", "description": "setup", "sequences": [
                {"name": "Seq A", "act": "Act I", "scenes": [
                    {"scene_number": 1, "act": "Act I", "sequence": "Seq A", "objective": "hook objective", "conflict": "c1", "outcome": "o1", "emotional_objective": "e1", "narrative_beat": "hook"},
                    {"scene_number": 2, "act": "Act I", "sequence": "Seq A", "objective": "plot objective", "conflict": "c2", "outcome": "o2", "emotional_objective": "e2", "narrative_beat": "plot"},
                ]},
            ]},
            {"name": "Act II", "description": "climax", "sequences": [
                {"name": "Seq B", "act": "Act II", "scenes": [
                    {"scene_number": 3, "act": "Act II", "sequence": "Seq B", "objective": "climax objective", "conflict": "c3", "outcome": "o3", "emotional_objective": "e3", "narrative_beat": "climax"},
                ]},
            ]},
        ],
    }


def _ctx():
    return {
        "synopsis": "Mark withdraws from Sarah after losing his job.",
        "constraints": {},
        "phase_01": {"theme": "fear"},
        "phase_02": {"premise": "Mark hides job loss."},
        "phase_03": {"protagonist": {"name": "MARK"}},
        "phase_04": {"environment": "home"},
    }


def test_nested_only_scenes_are_canonicalized_to_flat():
    phase = NarrativeExpansionPhase(MockLLMClient())
    knowledge = phase.parse_draft(json.dumps(_nested_only_payload()))
    assert len(knowledge.scenes) == 3
    assert [s.scene_number for s in knowledge.scenes] == [1, 2, 3]


def test_nested_scene_order_is_stable():
    phase = NarrativeExpansionPhase(MockLLMClient())
    knowledge = phase.parse_draft(json.dumps(_nested_only_payload()))
    # Act order, then sequence order, then scene order
    assert [s.scene_number for s in knowledge.scenes] == [1, 2, 3]


def test_all_scene_fields_survive_flattening():
    phase = NarrativeExpansionPhase(MockLLMClient())
    knowledge = phase.parse_draft(json.dumps(_nested_only_payload()))
    s1 = knowledge.scenes[0]
    assert s1.objective == "hook objective"
    assert s1.conflict == "c1"
    assert s1.outcome == "o1"
    assert s1.emotional_objective == "e1"
    assert s1.narrative_beat == "hook"


def test_realizes_requirements_survives_flattening():
    """realizes_requirements is bridge-derived, not a Scene model field; the
    flattening must preserve all Scene schema fields (objective/conflict/etc)."""
    payload = _nested_only_payload()
    phase = NarrativeExpansionPhase(MockLLMClient())
    knowledge = phase.parse_draft(json.dumps(payload))
    s1 = knowledge.scenes[0]
    assert s1.objective == "hook objective"
    assert s1.conflict == "c1"
    assert s1.outcome == "o1"
    assert s1.narrative_beat == "hook"


def test_normalization_is_idempotent():
    phase = NarrativeExpansionPhase(MockLLMClient())
    k1 = phase.parse_draft(json.dumps(_nested_only_payload()))
    k2 = phase.canonicalize_narrative_scenes(k1)
    assert [s.scene_number for s in k1.scenes] == [s.scene_number for s in k2.scenes]
    assert [s.objective for s in k1.scenes] == [s.objective for s in k2.scenes]


def test_duplicate_scene_ids_renumbered():
    """Duplicate nested scene_ids (per-act restart) are renumbered deterministically."""
    payload = _nested_only_payload()
    # Two nested scenes with the same scene_number (per-act restart)
    payload["acts"][0]["sequences"][0]["scenes"].append(
        {"scene_number": 1, "act": "Act I", "sequence": "Seq A", "objective": "SECOND SCENE 1", "conflict": "x", "outcome": "y", "emotional_objective": "z", "narrative_beat": "plot"}
    )
    phase = NarrativeExpansionPhase(MockLLMClient())
    knowledge = phase.parse_draft(json.dumps(payload))
    nums = [s.scene_number for s in knowledge.scenes]
    assert len(nums) == len(set(nums)), f"scene ids not unique: {nums}"


def test_conflicting_flat_and_nested_scene_flat_wins():
    """On a flat/nested conflict, the authoritative FLAT scene wins (CANONICAL_SCENE_LAW)."""
    payload = _nested_only_payload()
    payload["scenes"] = [{"scene_number": 1, "act": "Act I", "sequence": "Seq A", "objective": "FLAT WINS", "conflict": "x", "outcome": "y", "emotional_objective": "z", "narrative_beat": "hook"}]
    phase = NarrativeExpansionPhase(MockLLMClient())
    knowledge = phase.parse_draft(json.dumps(payload))
    s1 = next(s for s in knowledge.scenes if s.scene_number == 1)
    assert s1.objective == "FLAT WINS"


def test_empty_flat_and_nested_fails():
    empty_payload = json.dumps({"purpose": "x", "creative_intent": "y", "reasoning": "z", "confidence": "confirmed", "acts": [], "scenes": []})
    phase = NarrativeExpansionPhase(MockLLMClient({"Phase 05": empty_payload}))
    knowledge = phase.parse_draft(empty_payload)
    assert len(knowledge.scenes) == 0
    result = asyncio.run(phase.run(_ctx()))
    assert result.status.value == "failed"


def test_normalized_flat_scenes_pass_existing_validator():
    phase = NarrativeExpansionPhase(MockLLMClient())
    knowledge = phase.parse_draft(json.dumps(_nested_only_payload()))
    issues = phase._validate_specific(knowledge)
    assert not any(i.severity == "error" for i in issues)


def test_canonical_flat_scenes_survive_serialization_reload():
    phase = NarrativeExpansionPhase(MockLLMClient())
    knowledge = phase.parse_draft(json.dumps(_nested_only_payload()))
    dumped = knowledge.model_dump()
    assert len(dumped["scenes"]) == 3
    reloaded = NarrativeExpansion.model_validate(dumped)
    assert len(reloaded.scenes) == 3
    assert [s.scene_number for s in reloaded.scenes] == [1, 2, 3]


def test_metadata_only_response_triggers_bounded_repair():
    """If the model returns only metadata (no acts/scenes), Phase05 re-prompts
    ONCE with a focused repair and must not fail."""
    from movie_os.genesis2.llm_providers import LLMConfig

    class _RepairMock(MockLLMClient):
        def __init__(self):
            super().__init__()
            self._config = LLMConfig(provider="ollama", model="qwen3:4b", max_tokens=1536)
            self._provider = object()
            self.calls = 0

        def _get_provider(self):
            return self._provider

        def generate_json(self, prompt, tier="planner", phase_name=None, task_key=None, *, response_format=None):
            self.calls += 1
            if self.calls == 1:
                return {"purpose": "x", "creative_intent": "y", "reasoning": "z", "confidence": "confirmed"}
            return {
                "purpose": "x", "creative_intent": "y", "reasoning": "z", "confidence": "confirmed",
                "acts": [{"name": "Act I", "description": "d", "sequences": [{"name": "Seq A", "act": "Act I", "scenes": [
                    {"scene_number": 1, "act": "Act I", "sequence": "Seq A", "objective": "hook obj", "conflict": "c", "outcome": "o", "emotional_objective": "e", "narrative_beat": "hook"},
                    {"scene_number": 2, "act": "Act I", "sequence": "Seq A", "objective": "climax obj", "conflict": "c", "outcome": "o", "emotional_objective": "e", "narrative_beat": "climax"},
                ]}]}],
            }

    mock = _RepairMock()
    phase = NarrativeExpansionPhase(mock)
    result = asyncio.run(phase.run(_ctx()))
    assert result.status.value == "completed"
    assert mock.calls == 2
    assert len(result.knowledge.scenes) == 2
    assert [s.narrative_beat for s in result.knowledge.scenes] == ["hook", "climax"]
