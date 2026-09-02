from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, cast

import pytest

from movie_os.genesis2.freeze_gate import reconcile_requirements
from movie_os.genesis2.phases.phase09_production_specs import ProductionSpecificationsPhase
from movie_os.genesis2.requirement_manifest import compile_episode_requirements


class _Phase09StubLLM:
    def __init__(self):
        self.calls: list[dict] = []
        self._config = SimpleNamespace(max_tokens=8192, model_dump=lambda: {"max_tokens": 8192})

    def _get_provider(self):
        return object()

    def generate_json(self, prompt, tier, phase_name, task_key, response_format=None):
        self.calls.append({
            "prompt": prompt,
            "tier": tier,
            "phase_name": phase_name,
            "task_key": task_key,
            "response_format": response_format,
        })
        return {
            "purpose": "Generate production specs",
            "creative_intent": "Technical blueprint",
            "reasoning": "Bounded structured output",
            "confidence": "confirmed",
            "character_specs": [{"character": "MARK", "wardrobe": "Casual", "props": ["Phone"]}],
            "location_specs": [{"location": "Apartment", "set_design": "Lived-in"}],
            "camera_specs": [{"body": "Sony FX6", "lens": "50mm"}],
            "lighting_specs": [{"fixtures": "LED panel", "gels": "CTO"}],
            "animation_specs": [],
            "audio_specs": [{"mics": "Boom", "recording": "24-bit"}],
            "music_specs": [{"instruments": "Cello", "tempo": "Slow"}],
            "editing_specs": [{"software": "DaVinci Resolve", "workflow": "Offline"}],
            "rendering_specs": [{"resolution": "4K", "format": "ProRes"}],
        }

    def generate(self, prompt, phase_name=None, task_key=None):
        raise AssertionError("structured path should be used")


def test_phase09_real_runtime_uses_structured_output_and_bounded_budget():
    llm = cast(Any, _Phase09StubLLM())
    phase = ProductionSpecificationsPhase(llm)
    pkg = {"synopsis": "After losing his job, Mark withdraws from Sarah.", "phase_08": {}}
    knowledge = cast(Any, phase.draft(pkg))
    assert knowledge.character_specs
    assert llm.calls
    call = llm.calls[0]
    assert call["phase_name"] == "Production Specifications"
    assert call["task_key"] == "Production Specifications"
    assert "character_specs" in json.dumps(call["response_format"])
    assert llm._config.max_tokens == 8192  # draft should not mutate the shared config object


def test_req005_keyword_only_does_not_pass():
    canon = [r.to_dict() for r in compile_episode_requirements(episode_id="EP-0001", synopsis="After losing his job, a husband withdraws from his wife.", contract={"working_title": "x"}).requirements]
    scenes = [
        {"scene_number": 1, "narrative_beat": "hook", "title": "A", "realizes_requirements": ["REQ-001", "REQ-002"]},
        {"scene_number": 2, "narrative_beat": "plot", "title": "B", "scene_description": "Mark withdraws further and the relational distance worsens.", "realizes_requirements": ["REQ-003", "REQ-004"]},
        {"scene_number": 3, "narrative_beat": "climax", "title": "C", "realizes_requirements": ["REQ-006", "REQ-007", "REQ-008"]},
    ]
    pkg = {"phase_results": [], "validation": {"passed": True, "score": 1.0}, "scene_planning": {"scenes": scenes}, "narrative_expansion": {"scenes": scenes}, "dialogue_planning": {"dialogues": []}, "creative_critique": {"findings": []}, "story": {"ending": "reconnect"}}
    brief = {"scenes": scenes, "canonical_requirements": canon, "narrative_contract": {"resolution_requirement": "REQUIRED", "narrative_structure": "LINEAR"}}
    rec = reconcile_requirements(pkg, canon, brief)
    assert rec["requirements"]["REQ-005"]["realized"] is False
    assert rec["passed"] is False


def test_valid_req005_evidence_survives_serialization_and_reconciliation():
    canon = [r.to_dict() for r in compile_episode_requirements(episode_id="EP-0001", synopsis="After losing his job, a husband withdraws from his wife.", contract={"working_title": "x"}).requirements]
    scenes = [
        {"scene_number": 1, "narrative_beat": "hook", "title": "A", "realizes_requirements": ["REQ-001", "REQ-002"]},
        {"scene_number": 2, "narrative_beat": "plot", "title": "B", "realizes_requirements": ["REQ-003", "REQ-004", "REQ-005"], "scene_description": "Mark pulls away again, worsening the distance."},
        {"scene_number": 3, "narrative_beat": "climax", "title": "C", "realizes_requirements": ["REQ-006", "REQ-007", "REQ-008"]},
    ]
    pkg = json.loads(json.dumps({"phase_results": [], "validation": {"passed": True, "score": 1.0}, "scene_planning": {"scenes": scenes}, "narrative_expansion": {"scenes": scenes}, "dialogue_planning": {"dialogues": []}, "creative_critique": {"findings": []}, "story": {"ending": "reconnect"}}))
    brief = {"scenes": scenes, "canonical_requirements": canon, "narrative_contract": {"resolution_requirement": "REQUIRED", "narrative_structure": "LINEAR"}}
    rec = reconcile_requirements(pkg, canon, brief)
    assert rec["requirements"]["REQ-005"]["realized"] is True
    assert rec["passed"] is True
