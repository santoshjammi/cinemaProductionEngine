from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from movie_os.genesis2.engine import Genesis2Engine
from movie_os.genesis2.llm_client import MockLLMClient
from movie_os.genesis2.models import PhaseResult, PhaseStatus, ProductionKnowledgePackage
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


class CountingMockLLM(MockLLMClient):
    def __init__(self, responses: dict[str, str] | None = None):
        super().__init__(responses)
        self.phase_calls: list[str] = []

    def generate(self, prompt: str, config=None, tier: str = "planner", *args, **kwargs) -> str:  # type: ignore[override]
        for n in range(1, 13):
            if f"Phase {n:02d}" in prompt:
                self.phase_calls.append(f"{n:02d}")
                break
        return super().generate(prompt, config, tier)


@pytest.fixture()
def phase7_response_json():
    return phase7_response()


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


def test_canonical_resume_reuses_phases_1_to_7(tmp_path):
    checkpoint_dir = tmp_path / "productions" / "EP-1" / "runs" / "RUN-1" / "genesis" / "phases"
    llm = CountingMockLLM({
        "Phase 01": json.dumps({"purpose": "p1", "creative_intent": "p1", "reasoning": "p1", "confidence": "confirmed", "theme": "t", "genre": "Drama", "mood": "neutral", "core_question": "q", "audience": "adults", "success_criteria": ["truth"]}),
        "Phase 02": json.dumps({"purpose": "p2", "creative_intent": "p2", "reasoning": "p2", "confidence": "confirmed", "premise": "premise", "dramatic_question": "dq", "acts": [], "story_beats": []}),
        "Phase 03": json.dumps({"purpose": "p3", "creative_intent": "p3", "reasoning": "p3", "confidence": "confirmed", "protagonist": {"name": "MARK"}, "supporting_characters": [{"name": "SARAH"}]}),
        "Phase 04": json.dumps({"purpose": "p4", "creative_intent": "p4", "reasoning": "p4", "confidence": "confirmed", "history": "h", "culture": "c", "technology": "t", "environment": "e", "rules": [], "architecture": "a", "economy": "e", "politics": "p", "timeline": [], "social_structure": "s"}),
        "Phase 05": json.dumps({"purpose": "p5", "creative_intent": "p5", "reasoning": "p5", "confidence": "confirmed", "scenes": [{"scene_number": 1, "purpose": "keep going"}]}),
        "Phase 06": json.dumps({"purpose": "p6", "creative_intent": "p6", "reasoning": "p6", "confidence": "confirmed", "scenes": [
            {"scene_number": 1, "purpose": "open", "conflict": "c", "emotion": "e", "visual_goal": "v", "audio_goal": "a", "character_goal": "g", "transition": "t", "duration": "30", "dependencies": [], "narrative_beat": "hook"},
            {"scene_number": 2, "purpose": "plot", "conflict": "c", "emotion": "e", "visual_goal": "v", "audio_goal": "a", "character_goal": "g", "transition": "t", "duration": "30", "dependencies": [1], "narrative_beat": "plot"},
            {"scene_number": 3, "purpose": "close", "conflict": "c", "emotion": "e", "visual_goal": "v", "audio_goal": "a", "character_goal": "g", "transition": "t", "duration": "30", "dependencies": [2], "narrative_beat": "climax"},
        ]}),
        "Phase 07": phase7_response(),
    })
    engine = Genesis2Engine(llm=llm)
    constraints = {"episode_id": "EP-1", "run_id": "RUN-1", "policy_snapshot_id": "POL-1"}
    pkg = asyncio.run(engine.run_async("synopsis", constraints, checkpoint_dir=checkpoint_dir))
    engine.save_package(pkg, checkpoint_dir.parent)

    # clean resume from checkpoints only
    resume_llm = CountingMockLLM({"Phase 08": json.dumps({"purpose": "p8", "creative_intent": "p8", "reasoning": "p8", "confidence": "confirmed"})})
    resumed = Genesis2Engine(llm=resume_llm)
    resumed_pkg = asyncio.run(resumed.run_async("synopsis", constraints, checkpoint_dir=checkpoint_dir))

    assert len([p for p in resume_llm.phase_calls if p in {f"{i:02d}" for i in range(1, 8)}]) == 0
    assert all(any(f"{i:02d}" in c for c in resume_llm.phase_calls) is False for i in range(1, 8))
    assert resume_llm.phase_calls and resume_llm.phase_calls[0] == "08"
    assert len(resumed_pkg.phase_results) >= 8


def test_dependency_invalidation_reloads_phase7(tmp_path):
    checkpoint_dir = tmp_path / "productions" / "EP-1" / "runs" / "RUN-1" / "genesis" / "phases"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    engine = Genesis2Engine(llm=MockLLMClient())
    pkg = ProductionKnowledgePackage(episode_id="EP-1", run_id="RUN-1", policy_snapshot_id="POL-1")
    phase6 = PhaseResult(phase_number=6, phase_name="Scene Planning", status=PhaseStatus.COMPLETED, knowledge=None)
    phase7 = PhaseResult(phase_number=7, phase_name="Dialogue Planning", status=PhaseStatus.COMPLETED, knowledge=None)
    p6 = engine.write_phase_checkpoint(checkpoint_dir, pkg, phase6)
    pkg.phase_results.append(phase6)
    p7 = engine.write_phase_checkpoint(checkpoint_dir, pkg, phase7)
    data = json.loads(p6.read_text())
    data["result"]["phase_name"] = "Scene Planning Updated"
    p6.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        engine.read_phase_checkpoint(p6)
