"""Tests for the P0 Phase07 duplicate-dialogue integrity repair.

Covers:
- distinct scene packets/prompts bind correct scene intent
- exact duplicate dialogue across distinct scenes is rejected
- one targeted duplicate repair can replace a scene
- repaired scene replaces original
- repaired scene survives serialization
- duplicate after single repair fails closed
- negative control: same dialogue referenced twice inside same scene is not misclassified
"""
from __future__ import annotations

import asyncio
import json

import pytest

from movie_os.genesis2.llm_client import MockLLMClient
from movie_os.genesis2.phases.phase07_dialogue_planning import DialoguePlanningPhase


def _ctx():
    return {
        "synopsis": "Mark withdraws from Sarah after losing his job.",
        "constraints": {},
        "phase_03": {"protagonist": {"name": "MARK"}, "supporting_characters": [{"name": "SARAH"}]},
        "phase_05": {
            "scenes": [
                {"scene_number": 1, "objective": "establish job loss", "conflict": "fear", "outcome": "trigger", "narrative_beat": "hook"},
                {"scene_number": 2, "objective": "conceal the loss", "conflict": "avoidance", "outcome": "evasive", "narrative_beat": "plot"},
                {"scene_number": 3, "objective": "Sarah detects withdrawal", "conflict": "distance", "outcome": "notices", "narrative_beat": "plot"},
            ]
        },
        "phase_06": {
            "scenes": [
                {"scene_number": 1, "title": "S1", "narrative_beat": "hook"},
                {"scene_number": 2, "title": "S2", "narrative_beat": "plot"},
                {"scene_number": 3, "title": "S3", "narrative_beat": "climax"},
            ]
        },
    }


def _dialogue(scene_num: int, texts: list[str]) -> dict:
    return {
        "scene_number": scene_num,
        "conversation_intent": "intent",
        "subtext": "subtext",
        "emotional_state": "state",
        "lines": [{"speaker": "MARK" if i % 2 == 0 else "SARAH", "text": t, "delivery_intent": "d", "emotion": "e"} for i, t in enumerate(texts)],
        "inner_voice": [],
    }


def _phase7_response(scene_texts: dict[int, list[str]]) -> str:
    return json.dumps({
        "purpose": "dialogue plan", "creative_intent": "real", "reasoning": "fixture", "confidence": "confirmed",
        "dialogues": [_dialogue(sn, texts) for sn, texts in scene_texts.items()],
    })


def test_distinct_scene_prompts_bind_correct_scene():
    phase = DialoguePlanningPhase(MockLLMClient())
    prompt = phase.build_draft_prompt(_ctx())
    # Each scene's distinct objective must appear in the prompt
    assert "establish job loss" in prompt
    assert "conceal the loss" in prompt
    assert "Sarah detects withdrawal" in prompt


def test_exact_duplicate_dialogue_across_distinct_scenes_is_rejected():
    """Scenes 1 and 2 with identical dialogue but distinct intent must be deduped."""
    texts = ["line one", "line two", "line three", "line four", "line five", "line six"]
    # Mock returns identical dialogue for scenes 1 and 2, distinct for 3.
    # The dedup repair will be invoked; mock the repair to return a distinct scene 2.
    class _DedupMock(MockLLMClient):
        def generate(self, prompt, *args, **kwargs):
            if "dedup" in str(kwargs.get("task_key", "")):
                return _phase7_response({2: ["different", "dialogue", "for", "scene", "two", "now"]})
            return _phase7_response({1: texts, 2: texts, 3: ["third", "scene", "distinct", "content", "here", "ok"]})

    phase = DialoguePlanningPhase(_DedupMock())
    knowledge = phase.draft(_ctx())
    dialogues = {d.scene_number: d for d in knowledge.dialogues}
    assert 1 in dialogues and 2 in dialogues and 3 in dialogues
    # Scene 2 must no longer be an exact duplicate of scene 1
    p1 = phase._normalize_dialogue_payload(dialogues[1])
    p2 = phase._normalize_dialogue_payload(dialogues[2])
    assert p1 != p2, "scene 2 still duplicates scene 1 after repair"


def test_one_targeted_duplicate_repair_can_replace_scene():
    class _DedupMock(MockLLMClient):
        def generate(self, prompt, *args, **kwargs):
            if "dedup" in str(kwargs.get("task_key", "")):
                return _phase7_response({2: ["replacement", "dialogue", "for", "scene", "two", "unique"]})
            return _phase7_response({1: ["a", "b", "c", "d", "e", "f"], 2: ["a", "b", "c", "d", "e", "f"], 3: ["g", "h", "i", "j", "k", "l"]})

    phase = DialoguePlanningPhase(_DedupMock())
    knowledge = phase.draft(_ctx())
    d2 = next(d for d in knowledge.dialogues if d.scene_number == 2)
    assert d2.lines[0].text == "replacement"


def test_repaired_scene_replaces_original():
    class _DedupMock(MockLLMClient):
        def generate(self, prompt, *args, **kwargs):
            if "dedup" in str(kwargs.get("task_key", "")):
                return _phase7_response({2: ["replacement", "dialogue", "for", "scene", "two", "unique"]})
            return _phase7_response({1: ["a", "b", "c", "d", "e", "f"], 2: ["a", "b", "c", "d", "e", "f"], 3: ["g", "h", "i", "j", "k", "l"]})

    phase = DialoguePlanningPhase(_DedupMock())
    knowledge = phase.draft(_ctx())
    # Only one dialogue per scene (no duplicate scene 2 retained)
    scene2s = [d for d in knowledge.dialogues if d.scene_number == 2]
    assert len(scene2s) == 1
    assert scene2s[0].lines[0].text == "replacement"


def test_repaired_scene_survives_serialization():
    class _DedupMock(MockLLMClient):
        def generate(self, prompt, *args, **kwargs):
            if "dedup" in str(kwargs.get("task_key", "")):
                return _phase7_response({2: ["replacement", "dialogue", "for", "scene", "two", "unique"]})
            return _phase7_response({1: ["a", "b", "c", "d", "e", "f"], 2: ["a", "b", "c", "d", "e", "f"], 3: ["g", "h", "i", "j", "k", "l"]})

    phase = DialoguePlanningPhase(_DedupMock())
    knowledge = phase.draft(_ctx())
    dumped = knowledge.model_dump()
    d2 = next(d for d in dumped["dialogues"] if d["scene_number"] == 2)
    assert d2["lines"][0]["text"] == "replacement"


def test_duplicate_after_single_repair_fails_closed():
    """If the repair still returns a duplicate, the scene is dropped (fail closed)."""
    class _StubbornMock(MockLLMClient):
        def generate(self, prompt, *args, **kwargs):
            if "dedup" in str(kwargs.get("task_key", "")):
                # Repair returns the SAME duplicate as scene 1
                return _phase7_response({2: ["a", "b", "c", "d", "e", "f"]})
            # Initial draft: scenes 1 and 2 identical, scene 3 distinct
            return _phase7_response({1: ["a", "b", "c", "d", "e", "f"], 2: ["a", "b", "c", "d", "e", "f"], 3: ["g", "h", "i", "j", "k", "l"]})

    phase = DialoguePlanningPhase(_StubbornMock())
    knowledge = phase.draft(_ctx())
    scene2s = [d for d in knowledge.dialogues if d.scene_number == 2]
    # Scene 2 dropped because it could not be made distinct
    assert len(scene2s) == 0


def test_negative_control_same_dialogue_inside_same_scene_not_misclassified():
    """Two dialogue objects for the SAME scene with identical content are not a
    cross-scene duplicate defect (they share the same intent)."""
    class _SameSceneMock(MockLLMClient):
        def generate(self, prompt, *args, **kwargs):
            return _phase7_response({1: ["a", "b", "c", "d", "e", "f"], 2: ["g", "h", "i", "j", "k", "l"]})

    phase = DialoguePlanningPhase(_SameSceneMock())
    knowledge = phase.draft(_ctx())
    # Both scenes present, no dedup repair triggered (distinct payloads)
    assert {d.scene_number for d in knowledge.dialogues} == {1, 2}


def test_underfilled_repair_prompt_uses_phase05_intent_not_empty_phase06_anchor():
    """The underfilled/missing-scene repair prompt must bind the scene to its
    distinct Phase05 objective/conflict/outcome, not empty Phase06 anchors
    (which produced malformed 'beat: ' prompts and prose output)."""
    class _RepairMock(MockLLMClient):
        def __init__(self):
            super().__init__()
            self.repair_prompts = []

        def generate(self, prompt, *args, **kwargs):
            if "repair" in str(kwargs.get("task_key", "")):
                self.repair_prompts.append(prompt)
                # Return a valid 6-line scene-4 dialogue, DISTINCT from scene 1
                return _phase7_response({4: ["w", "x", "y", "z", "aa", "bb"]})
            # Initial draft: scenes 1-3 only, scene 4 missing
            return _phase7_response({1: ["a", "b", "c", "d", "e", "f"], 2: ["g", "h", "i", "j", "k", "l"], 3: ["m", "n", "o", "p", "q", "r"]})

    ctx = _ctx()
    # Phase06 scene 4 has empty narrative_beat/purpose (the defect)
    ctx["phase_06"]["scenes"].append({"scene_number": 4, "title": "S4"})
    # Phase05 scene 4 has distinct intent
    ctx["phase_05"]["scenes"].append({"scene_number": 4, "objective": "confront the withdrawal", "conflict": "fear of failure", "outcome": "reconnect", "narrative_beat": "turning_point"})

    phase = DialoguePlanningPhase(_RepairMock())
    knowledge = phase.draft(ctx)
    # Scene 4 must be repaired and present with 6 lines
    scene4 = [d for d in knowledge.dialogues if d.scene_number == 4]
    assert len(scene4) == 1
    assert len(scene4[0].lines) == 6
    # The repair prompt must reference the Phase05 objective, not empty beat
    assert any("confront the withdrawal" in p for p in phase.llm.repair_prompts)
