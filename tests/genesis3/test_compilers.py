"""Tests for GENESIS 3 — Quality Assurance Compilers."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from movie_os.genesis3.compilers.base import (
    BaseCompiler,
    CompilerEvidence,
    EvidenceItem,
    Finding,
)
from movie_os.genesis3.compilers.discovery_compiler import DiscoveryCompiler
from movie_os.genesis3.compilers.narrative_compiler import NarrativeCompiler
from movie_os.genesis3.compilers.character_compiler import CharacterCompiler
from movie_os.genesis3.compilers.emotion_compiler import EmotionCompiler
from movie_os.genesis3.compilers.psychology_compiler import PsychologyCompiler
from movie_os.genesis3.compilers.visual_compiler import VisualCompiler
from movie_os.genesis3.compilers.dialogue_compiler import DialogueCompiler
from movie_os.genesis3.compilers.continuity_compiler import ContinuityCompiler
from movie_os.genesis3.compilers.__init__ import (
    COMPILERS,
    list_compilers,
    get_compiler,
    run_all,
    MockCompiler,
)


# ---------------------------------------------------------------------------
# Sample synopses used across tests
# ---------------------------------------------------------------------------

STRONG_SYNOPSIS = (
    "A young woman discovers her grandmother's diary revealing "
    "a decades-old family betrayal. She must choose between protecting "
    "her family name and seeking the truth, even if it means losing "
    "everyone she loves. The story explores themes of loyalty, love, "
    "and redemption through a journey of self-discovery."
)

STRONG_SYNOPSIS_2 = (
    "When a retired soldier discovers a secret that could save her "
    "estranged daughter, she confronts the fear that kept them apart "
    "for years. Through emotional battles with herself and others, "
    "they find courage to forgive and begin anew."
)

NORMAL_SYNOPSIS = (
    "A man falls in love with a stranger during a journey across Europe."
)

EMPTY_SYNOPSIS = ""
WHITESPACE_SYNOPSIS = "   \n\t  "
LONG_SYNOPSIS = STRONG_SYNOPSIS + " " + STRONG_SYNOPSIS_2 + " " * 500 + STRONG_SYNOPSIS


# ---------------------------------------------------------------------------
# Testing each concrete Compiler subclass exists and has correct class attrs
# ---------------------------------------------------------------------------

CONCRETE_COMPILERS: list[type[BaseCompiler]] = [
    DiscoveryCompiler,
    NarrativeCompiler,
    CharacterCompiler,
    EmotionCompiler,
    PsychologyCompiler,
    VisualCompiler,
    DialogueCompiler,
    ContinuityCompiler,
]


class TestCompilerSubclasses:
    """Each concrete compiler is a proper subclass of BaseCompiler."""

    def test_all_have_name(self):
        for cls in CONCRETE_COMPILERS:
            assert isinstance(cls.name, str)
            assert len(cls.name) > 0

    def test_all_have_dimension(self):
        for cls in CONCRETE_COMPILERS:
            assert isinstance(cls.dimension, str)
            assert len(cls.dimension) > 0

    def test_all_subclass_BaseCompiler(self):
        for cls in CONCRETE_COMPILERS:
            assert issubclass(cls, BaseCompiler)

    def test_all_have_compile_method(self):
        for cls in CONCRETE_COMPILERS:
            assert hasattr(cls, "compile")
            assert callable(getattr(cls, "compile"))


# ---------------------------------------------------------------------------
# Base model tests (Finding / EvidenceItem / CompilerEvidence)
# ---------------------------------------------------------------------------

class TestBaseModels:
    def test_finding_valid(self):
        f = Finding(
            category="test",
            status="pass",
            statement="works",
            detail="it does",
        )
        assert f.category == "test"
        assert f.status == "pass"

    def test_finding_all_statuses(self):
        for s in ("pass", "fail", "warning", "info"):
            Finding(category="x", status=s, statement="y", detail="z")

    def test_finding_invalid_status_raises(self):
        with pytest.raises(ValidationError):
            Finding(category="x", status="INVALID", statement="y", detail="z")

    def test_evidence_item_defaults(self):
        e = EvidenceItem(claim="c", supporting_text="s", source="src")
        assert e.claim == "c"

    def test_evidence_items_can_be_empty(self):
        evidence = CompilerEvidence(
            compiler_name="test",
            dimension="Test",
        )
        assert len(evidence.findings) == 0
        assert len(evidence.evidence_items) == 0
        assert evidence.confidence == 0.0

    def test_compiler_evidence_with_findings(self):
        findings = [Finding(
            category="f1", status="pass", statement="s1", detail="d1",
        )]
        items = [EvidenceItem(claim="c1", supporting_text="s1", source="src")]
        evidence = CompilerEvidence(
            compiler_name="test",
            dimension="Test",
            findings=findings,
            evidence_items=items,
            confidence=0.85,
            summary="OK",
        )
        assert len(evidence.findings) == 1
        assert len(evidence.evidence_items) == 1
        assert evidence.confidence == 0.85


# ---------------------------------------------------------------------------
# Compiler registry tests (COMPILERS dict, list_compilers, get_compiler, run_all)
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_exactly_eight_compilers(self):
        assert len(COMPILERS) == 8

    def test_all_compilers_in_list(self):
        names = {name for name, _ in list_compilers()}
        assert names == set(COMPILERS.keys())

    def test_list_compilers_sorted(self):
        names = [n for n, _ in list_compilers()]
        assert names == sorted(names)

    def test_get_compiler_case_insensitive(self):
        for name, _ in COMPILERS.items():
            get_compiler(name.upper())
            get_compiler(name.capitalize())

    def test_get_compiler_raises_missing(self):
        with pytest.raises(KeyError, match="nonexistent"):
            get_compiler("nonexistent")

    def test_run_all_returns_8_results(self):
        results = run_all(STRONG_SYNOPSIS)
        assert len(results) >= 8  # 8 real compilers + optional mock


# ---------------------------------------------------------------------------
# Individual compiler tests — discovery
# ---------------------------------------------------------------------------

class TestDiscoveryCompiler:
    def setup_method(self):
        self.compiler = DiscoveryCompiler()

    def test_produces_evidence_structure(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert isinstance(evidence, CompilerEvidence)
        assert evidence.compiler_name == "Discovery"
        assert evidence.dimension == "Story Discovery"

    def test_at_least_3_findings(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert len(evidence.findings) >= 3

    def test_confidence_in_range(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert 0.0 <= evidence.confidence <= 1.0

    def test_empty_synopsis_returns_evidence(self):
        evidence = self.compiler.compile("")
        assert len(evidence.findings) >= 1
        assert evidence.confidence == 0.0

    def test_strong_synopsis_passes_premise(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        premise_statuses = [f.status for f in evidence.findings if f.category == "premise"]
        if premise_statuses:
            assert premise_statuses[0] == "pass"

    def test_summary_not_empty(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert len(evidence.summary) > 10


# ---------------------------------------------------------------------------
# Individual compiler tests — narrative
# ---------------------------------------------------------------------------

class TestNarrativeCompiler:
    def setup_method(self):
        self.compiler = NarrativeCompiler()

    def test_produces_evidence_structure(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert isinstance(evidence, CompilerEvidence)
        assert evidence.compiler_name == "Narrative"

    def test_at_least_3_findings(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert len(evidence.findings) >= 3

    def test_confidence_in_range(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert 0.0 <= evidence.confidence <= 1.0


# ---------------------------------------------------------------------------
# Individual compiler tests — character
# ---------------------------------------------------------------------------

class TestCharacterCompiler:
    def setup_method(self):
        self.compiler = CharacterCompiler()

    def test_produces_evidence_structure(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert isinstance(evidence, CompilerEvidence)
        assert evidence.compiler_name == "Character"

    def test_at_least_3_findings(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert len(evidence.findings) >= 3


# ---------------------------------------------------------------------------
# Individual compiler tests — emotion
# ---------------------------------------------------------------------------

class TestEmotionCompiler:
    def setup_method(self):
        self.compiler = EmotionCompiler()

    def test_produces_evidence_structure(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert isinstance(evidence, CompilerEvidence)
        assert evidence.compiler_name == "Emotion"

    def test_at_least_3_findings(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert len(evidence.findings) >= 3


# ---------------------------------------------------------------------------
# Individual compiler tests — psychology
# ---------------------------------------------------------------------------

class TestPsychologyCompiler:
    def setup_method(self):
        self.compiler = PsychologyCompiler()

    def test_produces_evidence_structure(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert isinstance(evidence, CompilerEvidence)
        assert evidence.compiler_name == "Psychology"

    def test_at_least_3_findings(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert len(evidence.findings) >= 3


# ---------------------------------------------------------------------------
# Individual compiler tests — visual
# ---------------------------------------------------------------------------

class TestVisualCompiler:
    def setup_method(self):
        self.compiler = VisualCompiler()

    def test_produces_evidence_structure(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert isinstance(evidence, CompilerEvidence)
        assert evidence.compiler_name == "Visual"

    def test_at_least_3_findings(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert len(evidence.findings) >= 3


# ---------------------------------------------------------------------------
# Individual compiler tests — dialogue
# ---------------------------------------------------------------------------

class TestDialogueCompiler:
    def setup_method(self):
        self.compiler = DialogueCompiler()

    def test_produces_evidence_structure(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert isinstance(evidence, CompilerEvidence)
        assert evidence.compiler_name == "Dialogue"

    def test_at_least_3_findings(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert len(evidence.findings) >= 3


# ---------------------------------------------------------------------------
# Individual compiler tests — continuity
# ---------------------------------------------------------------------------

class TestContinuityCompiler:
    def setup_method(self):
        self.compiler = ContinuityCompiler()

    def test_produces_evidence_structure(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert isinstance(evidence, CompilerEvidence)
        assert evidence.compiler_name == "Continuity"

    def test_at_least_3_findings(self):
        evidence = self.compiler.compile(STRONG_SYNOPSIS)
        assert len(evidence.findings) >= 3


# ---------------------------------------------------------------------------
# MockCompiler tests
# ---------------------------------------------------------------------------

class TestMockCompiler:
    def test_produces_valid_evidence(self):
        mc = MockCompiler()
        evidence = mc.compile(STRONG_SYNOPSIS)
        assert isinstance(evidence, CompilerEvidence)
        assert evidence.compiler_name == "Mock"

    def test_at_least_3_findings(self):
        mc = MockCompiler()
        evidence = mc.compile(STRONG_SYNOPSIS)
        assert len(evidence.findings) >= 3

    def test_empty_synopsis(self):
        mc = MockCompiler()
        evidence = mc.compile("")
        assert isinstance(evidence, CompilerEvidence)
        # Should have at least one finding about the empty input
        assert len(evidence.findings) >= 1


# ---------------------------------------------------------------------------
# Edge-case tests for run_all and individual compilers
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_run_all_empty_synopsis(self):
        results = run_all("")
        assert len(results) >= 8  # 8 real compilers + optional mock
        # every compiler should return some evidence (possibly error-level)
        for name, evid in results.items():
            assert isinstance(evid.findings, list)

    def test_run_all_whitespace_only(self):
        results = run_all(WHITESPACE_SYNOPSIS)
        assert len(results) >= 8  # 8 real compilers + optional mock

    def test_run_all_long_synopsis(self):
        results = run_all(LONG_SYNOPSIS)
        assert len(results) >= 8  # 8 real compilers + optional mock
        # No AssertionError / IndexError should occur

    def test_run_all_with_constraints(self):
        constraints = {"genre": "drama", "runtime": 120}
        results = run_all(STRONG_SYNOPSIS, constraints)
        assert len(results) >= 8  # 8 real compilers + optional mock

    def test_individual_compilers_empty(self):
        for cls in CONCRETE_COMPILERS:
            ev = cls().compile("")
            assert hasattr(ev, "findings")

    def test_findings_have_valid_statuses(self):
        evidence = run_all(STRONG_SYNOPSIS)
        for name, evid in evidence.items():
            for f in evid.findings:
                assert f.status in {"pass", "fail", "warning", "info"}

    def test_evidence_items_have_sources(self):
        evidence = run_all(STRONG_SYNOPSIS)
        for name, evid in evidence.items():
            for ei in evid.evidence_items:
                assert len(ei.source) > 0


# ---------------------------------------------------------------------------
# Constraints passthrough (ensure constraints aren't lost or crash)
# ---------------------------------------------------------------------------

class TestConstraintsPassthrough:
    def test_empty_constraints(self):
        results = run_all(STRONG_SYNOPSIS, {})
        assert len(results) >= 8  # 8 real compilers + optional mock

    def test_complex_constraints(self):
        constraints = {
            "genre": "drama",
            "tone": "melancholic",
            "runtime": 120,
            "audience": "adults",
            "budget": "micro",
        }
        results = run_all(STRONG_SYNOPSIS, constraints)
        assert len(results) >= 8  # 8 real compilers + optional mock


# ---------------------------------------------------------------------------
# Evidence quality checks (non-LFM — do not fabricate data)
# ---------------------------------------------------------------------------

class TestEvidenceQuality:
    def test_strong_synopsis_yields_more_findings(self):
        """Strong synopses should generally produce more findings than trivial ones."""
        strong_findings = {n: len(e.findings) for n, e in run_all(STRONG_SYNOPSIS).items()}
        weak_findings = {n: len(e.findings) for n, e in run_all(NORMAL_SYNOPSIS).items()}
        # Not every compiler must score higher; the average should be.
        assert (sum(strong_findings.values()) / len(strong_findings)) >= \
               (sum(weak_findings.values()) / len(weak_findings))

    def test_all_findings_have_statement(self):
        for name, evid in run_all(STRONG_SYNOPSIS).items():
            for f in evid.findings:
                assert len(f.statement) > 0

    def test_confidence_is_float(self):
        for name, evid in run_all(STRONG_SYNOPSIS).items():
            assert isinstance(evid.confidence, (int, float))

    def test_summary_is_string(self):
        for name, evid in run_all(STRONG_SYNOPSIS).items():
            assert isinstance(evid.summary, str)
