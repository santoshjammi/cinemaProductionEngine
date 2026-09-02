from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from movie_os.genesis2.engine import Genesis2Engine
from movie_os.genesis2.llm_client import MockLLMClient
from movie_os.genesis2.phases.phase07_dialogue_planning import DialoguePlanningPhase


class _Scene6Stub:
    @staticmethod
    def context():
        return {
            "synopsis": "Mark is afraid of disappointing Sarah after unstable work news, so he withdraws instead of speaking.",
            "constraints": {"runtime": "3-5 minutes"},
            "phase_03": {"protagonist": {"name": "MARK"}, "supporting_characters": [{"name": "SARAH"}]},
            "phase_05": {"narrative_rhythm": "tight"},
            "phase_06": {
                "scenes": [
                    {"scene_number": 1, "narrative_beat": "hook", "purpose": "open", "conflict": "silence", "emotion": "panic"},
                    {"scene_number": 2, "narrative_beat": "plot", "purpose": "escalate", "conflict": "avoidance", "emotion": "guilt"},
                    {"scene_number": 3, "narrative_beat": "climax", "purpose": "resolve", "conflict": "truth", "emotion": "vulnerable"},
                ]
            },
        }


def phase7_response() -> str:
    return json.dumps({
        "purpose": "dialogue plan",
        "creative_intent": "real conversation",
        "reasoning": "fixture",
        "confidence": "confirmed",
        "dialogues": [
            {
                "scene_number": 3,
                "conversation_intent": "break silence",
                "subtext": "Sarah needs truth; Mark is ashamed",
                "emotional_state": "desperate",
                "silence_opportunities": ["pause"],
                "dialogue_rhythm": "tight",
                "speech_patterns": "short",
                "voice_direction": "strained",
                "lines": [
                    {"speaker": "SARAH", "text": "Mark, please say something.", "delivery_intent": "pleading for honesty while staying calm", "emotion": "urgent"},
                    {"speaker": "MARK", "text": "I am trying.", "delivery_intent": "struggling to speak through shame", "emotion": "strained"},
                    {"speaker": "SARAH", "text": "Trying is not the same as telling me.", "delivery_intent": "presses for a direct answer without shouting", "emotion": "hurt"},
                    {"speaker": "MARK", "text": "I lost the job.", "delivery_intent": "forces the admission out with a breath", "emotion": "broken"},
                    {"speaker": "SARAH", "text": "Why did you hide that from me?", "delivery_intent": "asks the question carefully but with real pain", "emotion": "hurt"},
                    {"speaker": "MARK", "text": "Because I was scared you would look at me differently.", "delivery_intent": "confesses fear while avoiding eye contact", "emotion": "ashamed"},
                    {"speaker": "SARAH", "text": "Look at me now.", "delivery_intent": "asks him to return to the relationship", "emotion": "steady"},
                    {"speaker": "MARK", "text": "I am here.", "delivery_intent": "quietly commits to staying present", "emotion": "relieved"},
                ],
                "inner_voice": [
                    {"speaker": "MARK_INNER", "text": "If I say it, it becomes real.", "emotion": "whisper"}
                ],
            }
        ],
    })


def test_phase7_line_ids_are_deterministic_and_delivery_intent_required():
    phase = DialoguePlanningPhase(MockLLMClient({"Phase 07": phase7_response()}))
    ctx = _Scene6Stub.context()
    result = asyncio.run(phase.run(ctx))
    assert result.status.value == "completed"
    dialogue = result.knowledge.model_dump()["dialogues"][0]
    ids = [line["line_id"] for line in dialogue["lines"]]
    assert ids == [f"3:D{i:03d}" for i in range(1, 9)]
    assert len(set(ids)) == len(ids)
    assert [line["text"] for line in dialogue["lines"]][0] == "Mark, please say something."
    assert all(line["delivery_intent"] for line in dialogue["lines"])
    assert dialogue["scene_number"] == 3


def test_phase7_rejects_orphan_scene_reference():
    bad = json.loads(phase7_response())
    bad["dialogues"][0]["scene_number"] = 99
    phase = DialoguePlanningPhase(MockLLMClient({"Phase 07": json.dumps(bad)}))
    ctx = _Scene6Stub.context()
    result = asyncio.run(phase.run(ctx))
    assert result.status.value == "failed"
    assert any("scene_number" in issue.description or "scene" in issue.description.lower() for issue in result.validation_issues)


def test_phase7_persistence_and_resume_checkpoint(tmp_path):
    phase = DialoguePlanningPhase(MockLLMClient({"Phase 07": phase7_response()}))
    ctx = _Scene6Stub.context()
    result = asyncio.run(phase.run(ctx))
    assert result.status.value == "completed"

    assert result.knowledge is not None
    saved = phase.persist_checkpoint(result.knowledge, tmp_path / "run" / "genesis" / "phases")
    assert saved.exists()
    loaded = json.loads(saved.read_text())
    assert loaded["result"]["dialogues"][0]["lines"][0]["text"] == "Mark, please say something."
    assert loaded["result"]["dialogues"][0]["lines"][0]["line_id"] == "3:D001"
