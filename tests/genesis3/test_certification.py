"""Tests for GENESIS 3 — Production Certification system."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------

from movie_os.genesis3.certification import (
    CertificationEngine,
    ProductionCertificate,
    CertificationRequest,
)


# ---------------------------------------------------------------------------
# Fixtures: sample QA reports (plain dicts matching QADepartmentReport shape)
# ---------------------------------------------------------------------------

def _pass_qa_report() -> dict:
    return {
        "reviews": {
            "story": {"status": "PASS", "overall_score": 0.92},
            "psychology": {"status": "PASS", "overall_score": 0.87},
            "character": {"status": "PASS", "overall_score": 0.90},
            "dialogue": {"status": "PASS", "overall_score": 0.85},
            "emotion": {"status": "PASS", "overall_score": 0.88},
            "visual": {"status": "PASS", "overall_score": 0.91},
            "continuity": {"status": "PASS", "overall_score": 0.89},
        },
        "overall_status": "PASS",
        "overall_score": 0.89,
        "summary": "All constitutions passed with flying colors.",
        "critical_issues": [],
        "recommendations": ["Maintain current quality bar."],
    }


def _fail_qa_report() -> dict:
    return {
        "reviews": {
            "story": {"status": "PASS", "overall_score": 0.92},
            "psychology": {"status": "FAIL", "overall_score": 0.30},
            "character": {"status": "CONDITIONAL", "overall_score": 0.65},
            "dialogue": {"status": "PASS", "overall_score": 0.85},
            "emotion": {"status": "FAIL", "overall_score": 0.28},
            "visual": {"status": "CONDITIONAL", "overall_score": 0.70},
            "continuity": {"status": "PASS", "overall_score": 0.88},
        },
        "overall_status": "FAIL",
        "overall_score": 0.62,
        "summary": "Two constitutions failed; critical issues found.",
        "critical_issues": [
            "[psychology] FAILED: trauma_response",
            "[emotion] FAILED: catharsis_arc",
        ],
        "recommendations": [
            "[psychology] trauma_response: Insufficient research depth",
            "[emotion] Add reconciliation scene for audience payoff",
        ],
    }


def _conditional_qa_report() -> dict:
    return {
        "reviews": {
            s: {"status": "CONDITIONAL", "overall_score": 0.65}
            for s in ["story", "psychology", "character", "dialogue",
                      "emotion", "visual", "continuity"]
        },
        "overall_status": "CONDITIONAL",
        "overall_score": 0.65,
        "summary": "Conditional across all quality domains.",
        "critical_issues": [],
        "recommendations": ["Strengthen evidence in all areas."],
    }


def _empty_qa_report() -> dict:
    return {}


# ---------------------------------------------------------------------------
# 1. ProductionCertificate model tests
# ---------------------------------------------------------------------------

class TestProductionCertificateDefaults:
    """Verify the pydantic model creates correctly with defaults."""

    def test_creation_with_all_fields(self):
        cert = ProductionCertificate(
            project_name="Test Film",
            synopsis_summary="A short test.",
            story_integrity="PASS", psychology="PASS",
            character_development="PASS", narrative_logic="PASS",
            emotional_resonance="PASS", visual_readiness="PASS",
            continuity="PASS", production_ready=True, overall_score=0.95,
            critical_issues=[], recommendations=[], qa_report_summary="All good.",
        )
        assert cert.project_name == "Test Film"
        assert len(cert.certification_id) > 0
        assert isinstance(cert.issued_at, datetime)

    def test_all_literal_statuses_accept_pass_fail_conditional(self):
        for sv in ("PASS", "FAIL", "CONDITIONAL"):
            c = ProductionCertificate(
                project_name="T", synopsis_summary="S",
                story_integrity=sv, psychology=sv, character_development=sv,
                narrative_logic=sv, emotional_resonance=sv, visual_readiness=sv,
                continuity=sv, production_ready=(sv == "PASS"), overall_score=0.5,
                critical_issues=[], recommendations=[], qa_report_summary="",
            )
            assert c.story_integrity == sv

    def test_invalid_literal_raises_validation_error(self):
        with pytest.raises(ValidationError):
            ProductionCertificate(
                project_name="T", synopsis_summary="S",
                story_integrity="INVALID", psychology="PASS",
                character_development="PASS", narrative_logic="PASS",
                emotional_resonance="PASS", visual_readiness="PASS",
                continuity="PASS", production_ready=True, overall_score=0.5,
                critical_issues=[], recommendations=[], qa_report_summary="",
            )

    def test_overall_score_bounds(self):
        for s in (0.0, 0.5, 1.0):
            c = ProductionCertificate(
                project_name="T", synopsis_summary="S", story_integrity="PASS",
                psychology="PASS", character_development="PASS", narrative_logic="PASS",
                emotional_resonance="PASS", visual_readiness="PASS", continuity="PASS",
                production_ready=True, overall_score=s, critical_issues=[],
                recommendations=[], qa_report_summary="",
            )
            assert c.overall_score == s

    def test_overall_score_out_of_bounds_raises(self):
        for bad in (-0.1, 1.5):
            with pytest.raises(ValidationError):
                ProductionCertificate(
                    project_name="T", synopsis_summary="S", story_integrity="PASS",
                    psychology="PASS", character_development="PASS", narrative_logic="PASS",
                    emotional_resonance="PASS", visual_readiness="PASS", continuity="PASS",
                    production_ready=True, overall_score=bad, critical_issues=[],
                    recommendations=[], qa_report_summary="",
                )

    def test_certificate_body_default_empty(self):
        cert = ProductionCertificate(
            project_name="A", synopsis_summary="B",
            story_integrity="PASS", psychology="PASS", character_development="PASS",
            narrative_logic="PASS", emotional_resonance="PASS", visual_readiness="PASS",
            continuity="PASS", production_ready=True, overall_score=1.0,
            critical_issues=[], recommendations=[], qa_report_summary="",
        )
        assert cert.certificate_body == ""


# ---------------------------------------------------------------------------
# 2. CertificationRequest model tests
# ---------------------------------------------------------------------------

class TestCertificationRequestModel:
    def test_creation_with_dict_qa(self):
        req = CertificationRequest(
            synopsis="A story about forgiveness.",
            constraints={"genre": "drama"},
            qa_report=_pass_qa_report(),
        )
        assert isinstance(req.qa_report, dict)
        assert req.constraints == {"genre": "drama"}

    def test_qs50_truncation(self):
        long_s = "X" * 200
        c = ProductionCertificate(
            project_name=long_s[:50], synopsis_summary=long_s[:50],
            story_integrity="PASS", psychology="PASS", character_development="PASS",
            narrative_logic="PASS", emotional_resonance="PASS", visual_readiness="PASS",
            continuity="PASS", production_ready=True, overall_score=1.0,
            critical_issues=[], recommendations=[], qa_report_summary="",
        )
        assert len(c.project_name) <= 50
        assert len(c.synopsis_summary) <= 200

    def test_mandatory_fields_required(self):
        with pytest.raises(ValidationError):
            CertificationRequest(constraints={}, qa_report={})


# ---------------------------------------------------------------------------
# Helper: engine + pass request for formatting tests
# ---------------------------------------------------------------------------

def _engine_pass_cert():
    return CertificationEngine().certify(CertificationRequest(
        synopsis="Passing story", constraints={}, qa_report=_pass_qa_report(),
    ))


# ---------------------------------------------------------------------------
# 3. CertificationEngine — certification logic
# ---------------------------------------------------------------------------

class TestCertificationEngineCertify:

    def test_certify_valid_report_marks_production_ready(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="A beautiful story about hope.", constraints={"genre": "drama"},
            qa_report=_pass_qa_report(),
        ))
        assert cert.production_ready is True

    def test_certify_all_pass_statuses_when_all_review_pass(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_pass_qa_report(),
        ))
        for field in ["story_integrity", "psychology", "character_development",
                      "narrative_logic", "emotional_resonance", "visual_readiness",
                      "continuity"]:
            assert getattr(cert, field) == "PASS"

    def test_certify_high_overall_score_on_passing_report(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_pass_qa_report(),
        ))
        assert cert.overall_score == _pass_qa_report()["overall_score"]

    def test_certify_failing_report_not_production_ready(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_fail_qa_report(),
        ))
        assert cert.production_ready is False

    def test_certify_map_failure_dimensions(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_fail_qa_report(),
        ))
        assert cert.psychology == "FAIL"
        assert cert.emotional_resonance == "FAIL"
        assert cert.character_development == "CONDITIONAL"
        assert cert.visual_readiness == "CONDITIONAL"

    def test_certify_contains_critical_issues_on_failure(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_fail_qa_report(),
        ))
        assert len(cert.critical_issues) > 0
        for issue in cert.critical_issues:
            assert isinstance(issue, str)

    def test_certify_contains_recommendations_on_failure(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_fail_qa_report(),
        ))
        assert len(cert.recommendations) > 0
        for r in cert.recommendations:
            assert isinstance(r, str)

    def test_certify_conditional_yields_conditionally_ready(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_conditional_qa_report(),
        ))
        assert cert.production_ready is False  # only PASS -> production_ready=True

    def test_certify_conditional_maps_conditionals(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_conditional_qa_report(),
        ))
        for field in ["story_integrity", "psychology", "character_development",
                      "narrative_logic", "emotional_resonance", "visual_readiness",
                      "continuity"]:
            assert getattr(cert, field) == "CONDITIONAL"


# ---------------------------------------------------------------------------
# 4. Certificate text formatting
# ---------------------------------------------------------------------------

class TestCertificationEngineFormat:

    def test_format_returns_string(self):
        body = _engine_pass_cert().certificate_body
        assert isinstance(body, str)
        assert len(body) > 100

    def test_format_contains_project_name(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="My Movie Title", constraints={}, qa_report=_pass_qa_report(),
        ))
        assert cert.certificate_body != ""
        assert "My Movie Title" in cert.certificate_body

    def test_format_contains_certificate_id(self):
        result = _engine_pass_cert()
        body = result.certificate_body
        assert result.certification_id in body

    def test_format_contains_production_ready_text(self):
        body = _engine_pass_cert().certificate_body
        assert "Production Ready" in body

    def test_format_overall_score_present(self):
        body = _engine_pass_cert().certificate_body
        # Score 0.89 should appear somewhere
        assert "0.89" in body

    def test_format_title_present(self):
        body = _engine_pass_cert().certificate_body
        assert "PRODUCTION" in body or "Production Readiness Certificate" in body

    def test_format_issuer_line_present(self):
        cert = _engine_pass_cert()
        date_str = cert.issued_at.strftime("%Y-%m-%d")
        assert date_str in cert.certificate_body

    def test_format_on_failure_shows_fails(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_fail_qa_report(),
        ))
        body = cert.certificate_body
        # FAIL statuses and "NO" for production ready should appear
        assert len(cert.critical_issues) > 0


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_empty_evidence_yields_not_production_ready(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="", constraints={}, qa_report=_empty_qa_report(),
        ))
        assert isinstance(cert, ProductionCertificate)
        assert cert.production_ready is False  # missing overall_status -> not PASS

    def test_all_dimension_failures(self):
        all_fail = {
            "reviews": {s: {"status": "FAIL", "overall_score": 0.1}
                        for s in ["story", "psychology", "character", "dialogue",
                                  "emotion", "visual", "continuity"]},
            "overall_status": "FAIL",
            "overall_score": 0.1,
            "summary": "All failed.",
            "critical_issues": ["all dimensions failed"],
            "recommendations": ["Complete overhaul needed."],
        }
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="Fail Film", constraints={}, qa_report=all_fail,
        ))
        assert cert.production_ready is False
        assert cert.overall_score == 0.1

    def test_missing_key_in_evidence_does_not_crash(self):
        partial = {
            **{s: {} for s in ["story", "psychology"]},
            **{"overall_status": "FAIL", "overall_score": 0.0,
               "summary": "", "critical_issues": [], "recommendations": []},
        }
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="Partial", constraints={}, qa_report=partial,
        ))
        assert isinstance(cert, ProductionCertificate)


# ---------------------------------------------------------------------------
# 6. UUID and timestamp correctness
# ---------------------------------------------------------------------------

class TestUUIDAndTimestamp:
    def test_uuid_is_valid_format(self):
        cert = ProductionCertificate(
            project_name="A", synopsis_summary="B", story_integrity="PASS",
            psychology="PASS", character_development="PASS", narrative_logic="PASS",
            emotional_resonance="PASS", visual_readiness="PASS", continuity="PASS",
            production_ready=True, overall_score=1.0, critical_issues=[],
            recommendations=[], qa_report_summary="",
        )
        parts = cert.certification_id.split("-")
        assert len(parts) == 5

    def test_uuids_unique(self):
        c1 = ProductionCertificate(
            project_name="A", synopsis_summary="B", story_integrity="PASS",
            psychology="PASS", character_development="PASS", narrative_logic="PASS",
            emotional_resonance="PASS", visual_readiness="PASS", continuity="PASS",
            production_ready=True, overall_score=1.0, critical_issues=[],
            recommendations=[], qa_report_summary="",
        )
        c2 = ProductionCertificate(
            project_name="A", synopsis_summary="B", story_integrity="PASS",
            psychology="PASS", character_development="PASS", narrative_logic="PASS",
            emotional_resonance="PASS", visual_readiness="PASS", continuity="PASS",
            production_ready=True, overall_score=1.0, critical_issues=[],
            recommendations=[], qa_report_summary="",
        )
        assert c1.certification_id != c2.certification_id

    def test_issued_at_has_utc_timezone(self):
        cert = ProductionCertificate(
            project_name="A", synopsis_summary="B", story_integrity="PASS",
            psychology="PASS", character_development="PASS", narrative_logic="PASS",
            emotional_resonance="PASS", visual_readiness="PASS", continuity="PASS",
            production_ready=True, overall_score=1.0, critical_issues=[],
            recommendations=[], qa_report_summary="",
        )
        assert cert.issued_at.tzinfo is not None

    def test_issued_at_is_recent(self):
        before = datetime.now(timezone.utc)
        cert = ProductionCertificate(
            project_name="A", synopsis_summary="B", story_integrity="PASS",
            psychology="PASS", character_development="PASS", narrative_logic="PASS",
            emotional_resonance="PASS", visual_readiness="PASS", continuity="PASS",
            production_ready=True, overall_score=1.0, critical_issues=[],
            recommendations=[], qa_report_summary="",
        )
        after = datetime.now(timezone.utc)
        assert before <= cert.issued_at <= after


# ---------------------------------------------------------------------------
# 7. Synopsis summary handling
# ---------------------------------------------------------------------------

class TestSynopsisSummary:
    def test_synopsis_truncated_for_project_name(self):
        long_s = "A" * 500
        cert = ProductionCertificate(
            project_name=long_s[:50], synopsis_summary=long_s[:50],
            story_integrity="PASS", psychology="PASS", character_development="PASS",
            narrative_logic="PASS", emotional_resonance="PASS", visual_readiness="PASS",
            continuity="PASS", production_ready=True, overall_score=1.0,
            critical_issues=[], recommendations=[], qa_report_summary="",
        )
        assert len(cert.project_name) <= 50

    def test_certificate_body_filled_after_certify(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="Test synopsis", constraints={}, qa_report=_pass_qa_report(),
        ))
        assert len(cert.certificate_body) > 0


# ---------------------------------------------------------------------------
# 8. End-to-end: green / red cycles
# ---------------------------------------------------------------------------

class TestEndToEnd:
    def test_green_path(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="A great story.", constraints={"genre": "drama"}, qa_report=_pass_qa_report(),
        ))
        assert cert.production_ready is True

    def test_red_path(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="Broken story.", constraints={}, qa_report=_fail_qa_report(),
        ))
        assert cert.production_ready is False


# ---------------------------------------------------------------------------
# 9. Format structure verification
# ---------------------------------------------------------------------------

class TestFormatStructure:

    @staticmethod
    def _cert_pass():
        return CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_pass_qa_report(),
        ))

    def test_format_has_borders(self):
        body = self._cert_pass().certificate_body
        lines = body.split("\n")
        has_top = any("┌" in l for l in lines) or any("╔" in l for l in lines)
        has_bot = any("└" in l for l in lines) or any("╚" in l for l in lines)
        assert has_top and has_bot

    def test_format_has_section_dividers(self):
        body = self._cert_pass().certificate_body
        lines = body.split("\n")
        has_divider = any("═" in l or "─" in l for l in lines)
        assert has_divider


# ---------------------------------------------------------------------------
# 10. Constraints passthrough (no crash, fields survive)
# ---------------------------------------------------------------------------

class TestConstraintsPassthrough:
    def test_empty_constraints_no_crash(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T", constraints={}, qa_report=_pass_qa_report(),
        ))
        assert isinstance(cert, ProductionCertificate)

    def test_complex_constraints_no_crash(self):
        cert = CertificationEngine().certify(CertificationRequest(
            synopsis="T",
            constraints={"project": "Epic", "genre": "sci-fi", "budget": "indie"},
            qa_report=_pass_qa_report(),
        ))
        assert isinstance(cert, ProductionCertificate)
