"""Tests for Genesis2 — Creative Intelligence Engine."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from movie_os.genesis2.models import (
    ProductionKnowledgePackage,
    CreativeUnderstanding,
    StoryFoundation,
    CharacterPsychology,
    WorldDevelopment,
    NarrativeExpansion,
    ScenePlanning,
    DialoguePlanning,
    VisualLanguage,
    ProductionSpecifications,
    Validation,
    CreativeCritique,
    KnowledgeIntegration,
    PhaseResult,
    PhaseStatus,
    ConfidenceLevel,
    KnowledgeObject,
)
from movie_os.genesis2.llm_client import MockLLMClient, _extract_json
from movie_os.genesis2.engine import Genesis2Engine
from movie_os.genesis2.phases import PHASE_CLASSES


# ---------------------------------------------------------------------------
# Mock responses for all 12 phases
# ---------------------------------------------------------------------------

def _build_mock() -> MockLLMClient:
    mock = MockLLMClient()
    mock.set_response("Creative Understanding", json.dumps({
        "purpose": "Understand the story's meaning",
        "creative_intent": "Explore emotional withdrawal",
        "reasoning": "The synopsis centers on silence",
        "theme": "Withdrawal as communication",
        "genre": "Drama",
        "subgenre": "Relationship Drama",
        "audience": "Adults 30-55",
        "mood": "Melancholic",
        "core_question": "What happens when we stop talking?",
        "message": "Silence is a choice with consequences",
        "conflict": "Man vs self, man vs wife",
        "transformation": "Recognition of choice",
        "success_criteria": ["Emotional truth", "Narrative coherence"],
        "confidence": "inferred",
    }))
    mock.set_response("Story Foundation", json.dumps({
        "purpose": "Expand synopsis into story structure",
        "creative_intent": "Build narrative skeleton",
        "reasoning": "From synopsis themes",
        "premise": "A man withdraws after job loss",
        "acts": [{"name": "Act 1", "description": "Setup", "events": ["Job loss"]}],
        "major_events": ["Job loss", "Silent dinner", "Departure"],
        "emotional_journey": ["Comfort", "Tension", "Silence"],
        "story_beats": [{"name": "Inciting Incident", "description": "Job loss", "position": "beginning", "emotional_intent": "Shock"}],
        "narrative_rhythm": "Slow burn",
        "foreshadowing": ["Empty chair motif"],
        "symbolism": ["Closed doors"],
        "motifs": ["Silence", "Distance"],
        "confidence": "inferred",
    }))
    mock.set_response("Character Psychology", json.dumps({
        "purpose": "Generate character profiles",
        "creative_intent": "Create psychologically real characters",
        "reasoning": "From story foundation",
        "protagonist": {
            "name": "Daniel", "role": "protagonist",
            "identity": "Laid-off architect", "history": "Middle-class professional",
            "goals": ["Find work", "Save marriage"], "fear": "Rejection",
            "need": "Vulnerability", "want": "To be left alone",
            "weakness": "Pride", "strength": "Self-awareness",
            "internal_conflict": "Shame vs need for support",
            "external_conflict": "Unemployment",
            "speech_style": "Quiet, measured", "personality": "Introverted, avoidant",
            "transformation": "Learns to ask for help",
        },
        "confidence": "inferred",
    }))
    mock.set_response("World Development", json.dumps({
        "purpose": "Generate story world",
        "creative_intent": "Create believable environment",
        "reasoning": "From character needs",
        "history": "Urban middle-class setting",
        "culture": "Contemporary Western",
        "technology": "Smartphone era",
        "environment": "Two-bedroom apartment",
        "rules": ["No third-act confession"],
        "architecture": "Modern apartment building",
        "economy": "Post-recession",
        "politics": "N/A",
        "timeline": [{"event": "Job loss", "time": "Present"}],
        "social_structure": "Nuclear family",
        "confidence": "inferred",
    }))
    mock.set_response("Narrative Expansion", json.dumps({
        "purpose": "Expand into acts and scenes",
        "creative_intent": "Structure the narrative",
        "reasoning": "From story foundation",
        "acts": [{"name": "Act 1", "description": "The withdrawal", "sequences": ["Setup"]}],
        "sequences": [{"name": "Opening", "act": "Act 1", "scenes": [1]}],
        "scenes": [{"scene_number": 1, "act": "Act 1", "sequence": "Opening", "objective": "Establish silence", "conflict": "Unspoken tension", "outcome": "Distance grows", "emotional_objective": "Unease"}],
        "confidence": "inferred",
    }))
    mock.set_response("Scene Planning", json.dumps({
        "scenes": [{"scene_number": 1, "purpose": "Establish silence", "conflict": "Unspoken", "emotion": "Tension", "visual_goal": "Isolation", "audio_goal": "Silence", "character_goal": "Avoidance", "transition": "Hard cut", "duration": "60s", "dependencies": []}],
        "purpose": "Plan each scene",
        "creative_intent": "Scene-by-scene blueprint",
        "reasoning": "From narrative expansion",
        "confidence": "inferred",
    }))
    mock.set_response("Dialogue Planning", json.dumps({
        "dialogues": [{"scene_number": 1, "conversation_intent": "Avoid confrontation", "subtext": "I'm hurting", "emotional_state": "Withdrawn", "silence_opportunities": ["After question"], "dialogue_rhythm": "Sparse", "speech_patterns": "Short sentences", "voice_direction": "Quiet, flat"}],
        "purpose": "Plan dialogue",
        "creative_intent": "Subtext-driven dialogue",
        "reasoning": "From scene plans",
        "confidence": "inferred",
    }))
    mock.set_response("Visual Language", json.dumps({
        "purpose": "Define visual language",
        "creative_intent": "Visual storytelling",
        "reasoning": "From mood and theme",
        "color": "Muted earth tones, cold blues",
        "lighting": "Natural light, dusk preferred",
        "composition": "Negative space, isolated subjects",
        "textures": "Soft fabrics, worn wood",
        "atmosphere": "Quiet, watchful",
        "camera_intent": "Static frames, slow push-ins",
        "lens_suggestions": "50mm, 85mm",
        "movement_philosophy": "Stillness as statement",
        "environmental_storytelling": "Objects show passage of time",
        "confidence": "inferred",
    }))
    mock.set_response("Production Specifications", json.dumps({
        "purpose": "Generate production specs",
        "creative_intent": "Technical blueprint",
        "reasoning": "From all previous phases",
        "character_specs": [{"character": "Daniel", "wardrobe": "Casual", "props": ["Phone"]}],
        "location_specs": [{"location": "Apartment", "set_design": "Lived-in"}],
        "camera_specs": [{"body": "Sony FX6", "lens": "50mm"}],
        "lighting_specs": [{"fixtures": "LED panel", "gels": "CTO"}],
        "animation_specs": [],
        "audio_specs": [{"mics": "Boom", "recording": "24-bit"}],
        "music_specs": [{"instruments": "Cello", "tempo": "Slow"}],
        "editing_specs": [{"software": "DaVinci Resolve", "workflow": "Offline"}],
        "rendering_specs": [{"resolution": "4K", "format": "ProRes"}],
        "confidence": "inferred",
    }))
    mock.set_response("Validation", json.dumps({
        "issues": [],
        "passed": True,
        "score": 1.0,
        "purpose": "Validate all phases",
        "creative_intent": "Quality assurance",
        "reasoning": "Systematic check",
        "confidence": "confirmed",
    }))
    mock.set_response("Creative Critique", json.dumps({
        "findings": [{"question": "Is this emotionally believable?", "answer": "Yes", "severity": "minor", "recommendation": "Deepen Elena's perspective"}],
        "overall_assessment": "Strong foundation with room for emotional depth",
        "recommended_actions": ["Add more scenes from Elena's POV"],
        "purpose": "Creative quality review",
        "creative_intent": "Artistic integrity",
        "reasoning": "Critical analysis",
        "confidence": "confirmed",
    }))
    mock.set_response("Knowledge Integration", json.dumps({
        "package": {"version": "2.0.0", "phases": 12},
        "knowledge_graph": {"nodes": [], "edges": []},
        "asset_registry": [{"id": "char-001", "type": "character", "name": "Daniel"}],
        "dependencies": [{"from_phase": 1, "to_phase": 2, "relationship": "feeds_into"}],
        "cross_references": [{"source": "Phase 3", "target": "Phase 6", "relationship": "character_appears_in_scene"}],
        "version_history": [{"version": "2.0.0", "timestamp": "2026-07-20", "changes": ["Initial generation"]}],
        "purpose": "Merge all knowledge",
        "creative_intent": "Single source of truth",
        "reasoning": "Integration of all phases",
        "confidence": "confirmed",
    }))
    mock.set_default(json.dumps({
        "purpose": "default", "creative_intent": "default", "reasoning": "default",
        "confidence": "inferred",
    }))
    return mock


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestModels:
    def test_pkp_creation(self):
        pkg = ProductionKnowledgePackage(synopsis="Test")
        assert pkg.synopsis == "Test"
        assert pkg.version == "2.0.0"
        assert len(pkg.phase_results) == 0

    def test_creative_understanding_defaults(self):
        cu = CreativeUnderstanding()
        assert cu.theme == ""
        assert cu.confidence == ConfidenceLevel.UNKNOWN

    def test_character_defaults(self):
        from movie_os.genesis2.models import Character
        c = Character()
        assert c.role == ""
        assert c.goals == []

    def test_validation_issue_defaults(self):
        from movie_os.genesis2.models import ValidationIssue
        vi = ValidationIssue(category="test", severity="error", location="x", description="y")
        assert vi.suggestion == ""

    def test_phase_result_defaults(self):
        pr = PhaseResult(phase_number=1, phase_name="Test")
        assert pr.status == PhaseStatus.PENDING
        assert pr.draft_count == 0

    def test_knowledge_object_serialization(self):
        ko = KnowledgeObject(purpose="test", creative_intent="test", reasoning="test")
        data = ko.model_dump()
        assert data["purpose"] == "test"
        assert data["confidence"] == "unknown"


# ---------------------------------------------------------------------------
# Phase tests
# ---------------------------------------------------------------------------

class TestPhases:
    def test_all_phases_registered(self):
        assert len(PHASE_CLASSES) == 12
        names = [cls.__new__(cls).phase_name for cls in PHASE_CLASSES]
        expected = [
            "Creative Understanding", "Story Foundation", "Character Psychology",
            "World Development", "Narrative Expansion", "Scene Planning",
            "Dialogue Planning", "Visual Language", "Production Specifications",
            "Validation", "Creative Critique", "Knowledge Integration",
        ]
        assert names == expected

    def test_each_phase_has_correct_number(self):
        for i, cls in enumerate(PHASE_CLASSES, 1):
            assert cls.__new__(cls).phase_number == i

    def test_each_phase_has_draft_and_parse(self):
        for cls in PHASE_CLASSES:
            p = cls.__new__(cls)
            assert hasattr(p, "draft")
            assert hasattr(p, "parse_draft")
            assert hasattr(p, "build_draft_prompt")


# ---------------------------------------------------------------------------
# Engine tests
# ---------------------------------------------------------------------------

class TestEngine:
    def test_runs_all_12_phases(self):
        mock = _build_mock()
        engine = Genesis2Engine(llm=mock)
        pkg = engine.run(synopsis="A man withdraws from his wife after losing his job.")
        assert len(pkg.phase_results) == 12
        completed = sum(1 for r in pkg.phase_results if r.status == PhaseStatus.COMPLETED)
        assert completed == 12

    def test_pkg_has_all_fields(self):
        mock = _build_mock()
        engine = Genesis2Engine(llm=mock)
        pkg = engine.run(synopsis="Test")
        assert pkg.creative_understanding is not None
        assert pkg.story_foundation is not None
        assert pkg.character_psychology is not None
        assert pkg.world_development is not None
        assert pkg.narrative_expansion is not None
        assert pkg.scene_planning is not None
        assert pkg.dialogue_planning is not None
        assert pkg.visual_language is not None
        assert pkg.production_specifications is not None
        assert pkg.validation is not None
        assert pkg.creative_critique is not None
        assert pkg.knowledge_integration is not None

    def test_save_package(self):
        mock = _build_mock()
        engine = Genesis2Engine(llm=mock)
        pkg = engine.run(synopsis="Test")
        with tempfile.TemporaryDirectory() as tmpdir:
            written = engine.save_package(pkg, tmpdir)
            total = sum(len(v) for v in written.values())
            assert total == 14  # 1 package + 12 phases + 1 summary
            assert (Path(tmpdir) / "production_knowledge_package.json").exists()
            assert (Path(tmpdir) / "summary.json").exists()
            phases_dir = Path(tmpdir) / "phases"
            assert phases_dir.exists()
            assert len(list(phases_dir.glob("*.json"))) == 12

    def test_synopsis_preserved(self):
        mock = _build_mock()
        engine = Genesis2Engine(llm=mock)
        pkg = engine.run(synopsis="My test synopsis")
        assert pkg.synopsis == "My test synopsis"

    def test_constraints_preserved(self):
        mock = _build_mock()
        engine = Genesis2Engine(llm=mock)
        pkg = engine.run(synopsis="Test", constraints={"runtime": "15min"})
        assert pkg.constraints == {"runtime": "15min"}

    def test_version_is_2_0_0(self):
        mock = _build_mock()
        engine = Genesis2Engine(llm=mock)
        pkg = engine.run(synopsis="Test")
        assert pkg.version == "2.0.0"


# ---------------------------------------------------------------------------
# LLM Client tests
# ---------------------------------------------------------------------------

class TestLLMClient:
    def test_mock_set_and_get(self):
        mock = MockLLMClient()
        mock.set_response("test_key", '{"a": 1}')
        result = mock.generate("this contains test_key in the prompt")
        assert result == '{"a": 1}'

    def test_mock_default(self):
        mock = MockLLMClient()
        result = mock.generate("no match")
        assert "mock" in result

    def test_mock_set_default(self):
        mock = MockLLMClient()
        mock.set_default('{"custom": "default"}')
        result = mock.generate("no match")
        assert "custom" in result

    def test_extract_json_direct(self):
        result = _extract_json('{"a": 1}')
        assert result == {"a": 1}

    def test_extract_json_with_fences(self):
        result = _extract_json('```json\n{"a": 1}\n```')
        assert result == {"a": 1}

    def test_extract_json_braces(self):
        result = _extract_json('text {"a": 1} more text')
        assert result == {"a": 1}


# ---------------------------------------------------------------------------
# PhaseBase tests
# ---------------------------------------------------------------------------

class TestPhaseBase:
    def test_review_checks_required_fields(self):
        from movie_os.genesis2.phase_base import PhaseBase
        from movie_os.genesis2.models import KnowledgeObject

        class TestPhase(PhaseBase):
            phase_number = 99
            phase_name = "Test"
            def build_draft_prompt(self, pkg): return ""
            def parse_draft(self, response): return KnowledgeObject()
            def draft(self, pkg): return KnowledgeObject()

        p = TestPhase.__new__(TestPhase)
        p.llm = None
        ko = KnowledgeObject()
        issues = p.review(ko)
        assert "Missing purpose" in issues
        assert "Missing creative_intent" in issues
        assert "Missing reasoning" in issues

    def test_review_passes_with_all_fields(self):
        from movie_os.genesis2.phase_base import PhaseBase
        from movie_os.genesis2.models import KnowledgeObject

        class TestPhase(PhaseBase):
            phase_number = 99
            phase_name = "Test"
            def build_draft_prompt(self, pkg): return ""
            def parse_draft(self, response): return KnowledgeObject()
            def draft(self, pkg): return KnowledgeObject()

        p = TestPhase.__new__(TestPhase)
        p.llm = None
        ko = KnowledgeObject(purpose="x", creative_intent="x", reasoning="x")
        issues = p.review(ko)
        assert issues == []

    def test_validate_checks_empty(self):
        from movie_os.genesis2.phase_base import PhaseBase
        from movie_os.genesis2.models import KnowledgeObject

        class TestPhase(PhaseBase):
            phase_number = 99
            phase_name = "Test"
            def build_draft_prompt(self, pkg): return ""
            def parse_draft(self, response): return KnowledgeObject()
            def draft(self, pkg): return KnowledgeObject()

        p = TestPhase.__new__(TestPhase)
        p.llm = None
        issues = p.validate(None)
        assert len(issues) == 1
        assert issues[0].category == "missing_info"
