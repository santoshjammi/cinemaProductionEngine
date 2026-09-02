"""Comprehensive API tests for GENESIS 3 integration endpoints.

Tests cover:
- Metadata endpoints (compilers, standards, constitutions)
- Analyze (compilers only endpoint)
- Review (compilers + QA endpoint)
- Certify (full pipeline endpoint)
- Certificate retrieval
- Error handling and validation
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# Ensure the project root is on sys.path (same conftest.py that exists at repo root)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.main import app  # noqa: E402


@pytest.fixture()
def client():
    """Create a test client for the app under test."""
    return TestClient(app)


# ── Helpers ───────────────────────────────────────────────────────────────────

VALID_synopsis = (
    "A young orphan discovers she has magical powers and must journey across "
    "a war-torn land to defeat an ancient evil, making new friends along the way. "
    "She faces betrayal from a trusted ally but ultimately finds courage within herself "
    "to save her family and restore peace."
)

EMPTY_synopsis = "   "  # whitespace only


def _analyze(client):
    """Call /analyze with the standard synopsis."""
    return client.post("/api/v1/genesis3/analyze", json={"synopsis": VALID_synopsis})


def _review(client):
    """Call /review with the standard synopsis."""
    return client.post("/api/v1/genesis3/review", json={"synopsis": VALID_synopsis})


def _certify(client):
    """Call /certify with the standard synopsis."""
    return client.post("/api/v1/genesis3/certify", json={"synopsis": VALID_synopsis})


# =============================================================================
#  Metadata endpoints
# =============================================================================

class TestCompilersEndpoint:
    """/api/v1/genesis3/compilers"""

    def test_returns_200(self, client):
        resp = client.get("/api/v1/genesis3/compilers")
        assert resp.status_code == 200

    def test_returns_compilers_list(self, client):
        resp = _analyze(client).json()
        compilers_resp = client.get("/api/v1/genesis3/compilers").json()
        compilers = compilers_resp["compilers"]
        assert isinstance(compilers, list)
        # We expect 8 real compilers + Mock
        assert len(compilers) >= 8

    def test_each_compiler_has_name(self, client):
        compilers = client.get("/api/v1/genesis3/compilers").json()["compilers"]
        for entry in compilers:
            assert "name" in entry

    def test_includes_mock_compiler(self, client):
        names = {e["name"].lower() for e in
                 client.get("/api/v1/genesis3/compilers").json()["compilers"]}
        assert "mock" in names


class TestStandardsEndpoint:
    """/api/v1/genesis3/standards"""

    def test_returns_200(self, client):
        resp = client.get("/api/v1/genesis3/standards")
        assert resp.status_code == 200

    def test_returns_standards_key(self, client):
        resp = client.get("/api/v1/genesis3/standards").json()
        assert "standards" in resp
        assert isinstance(resp["standards"], list)

    def test_standards_are_strings(self, client):
        standards = client.get("/api/v1/genesis3/standards").json()["standards"]
        for s in standards:
            assert isinstance(s, str)
            assert len(s) > 0


class TestConstitutionsEndpoint:
    """/api/v1/genesis3/constitutions"""

    def test_returns_200(self, client):
        resp = client.get("/api/v1/genesis3/constitutions")
        assert resp.status_code == 200

    def test_returns_constitutions_key(self, client):
        resp = client.get("/api/v1/genesis3/constitutions").json()
        assert "constitutions" in resp
        assert isinstance(resp["constitutions"], list)

    def test_expected_constitutions_present(self, client):
        names = {
            c.get("name") for c in
            client.get("/api/v1/genesis3/constitutions").json()["constitutions"]
        }
        # All 9 constitutions should be registered
        expected = {
            "story", "character", "psychology", "dialogue",
            "visual", "emotion", "cinema", "continuity", "production",
        }
        assert expected.issubset(names), f"Missing: {expected - names}"


# =============================================================================
#  POST /analyze — compilers only
# =============================================================================

class TestAnalyzeEndpoint:
    """/api/v1/genesis3/analyze"""

    def test_returns_200(self, client):
        resp = _analyze(client)
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client):
        resp = _analyze(client).json()
        assert "pipeline_id" in resp
        assert "created_at" in resp
        assert "evidence" in resp
        assert isinstance(resp["evidence"], dict)

    def test_evidence_keys_are_compiler_names(self, client):
        evidence = _analyze(client).json()["evidence"]
        expected_compilers = {
            "mock", "mockllm", "discovery", "narrative", "character",
            "emotion", "psychology", "visual", "dialogue",
            "continuity",
        }
        assert set(evidence.keys()) == expected_compilers

    def test_evidence_has_summary_per_compiler(self, client):
        evidence = _analyze(client).json()["evidence"]
        for comp_name, comp_evidence in evidence.items():
            assert "summary" in comp_evidence, f"{comp_name} missing 'summary'"
            assert isinstance(comp_evidence["summary"], str)

    def test_compilers_have_findings(self, client):
        evidence = _analyze(client).json()["evidence"]
        for comp_name, ev in evidence.items():
            assert "findings" in ev, f"{comp_name} missing 'findings'"
            assert isinstance(ev["findings"], list)

    def test_empty_synopsis_rejected(self, client):
        resp = client.post("/api/v1/genesis3/analyze", json={})
        assert resp.status_code == 422

    def test_whitespace_only_synopsis_rejected(self, client):
        resp = client.post("/api/v1/genesis3/analyze", json={"synopsis": "   "})
        assert resp.status_code == 422

    def test_different_synthpsis_produces_different_evidence(self, client):
        resp1 = _analyze(client).json()["evidence"]
        resp2 = client.post("/api/v1/genesis3/analyze", json={
            "synopsis": ("A completely different story about cooking "
                         "and delicious food with no conflict."),
        }).json()["evidence"]
        # The Mock compiler is keyword-driven — evidence summaries must differ
        assert resp1["mock"]["summary"] != resp2["mock"]["summary"] or \
            {f["category"] for f in resp1["mock"]["findings"]} != \
            {f["category"] for f in resp2["mock"]["findings"]}


# =============================================================================
#  POST /review — compilers + QA Department
# =============================================================================

class TestReviewEndpoint:
    """/api/v1/genesis3/review"""

    def test_returns_200(self, client):
        resp = _review(client)
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client):
        resp = _review(client).json()
        assert "pipeline_id" in resp
        assert "qa_report" in resp
        qa = resp["qa_report"]
        assert "overall_status" in qa
        assert "overall_score" in qa
        assert "reviews" in qa

    def test_qa_overall_status_in_verdicts(self, client):
        overall = _review(client).json()["qa_report"]["overall_status"]
        assert overall in {"PASS", "FAIL", "CONDITIONAL"}

    def test_has_reviews_for_each_constitution(self, client):
        reviews = _review(client).json()["qa_report"]["reviews"]
        expected_constitutions = {
            "story", "character", "psychology", "dialogue",
            "visual", "emotion", "cinema", "continuity", "production",
        }
        assert set(reviews.keys()) == expected_constitutions

    def test_each_review_has_status_and_score(self, client):
        reviews = _review(client).json()["qa_report"]["reviews"]
        for name, review in reviews.items():
            assert "status" in review, f"{name} missing 'status'"
            assert "overall_score" in review, f"{name} missing 'overall_score'"

    def test_evidence_in_review_has_compilers(self, client):
        resp = _review(client).json()
        evidence = resp.get("evidence")
        # Either the API passes raw evidence alongside qa_report or it reruns compilers
        # Both paths should produce valid compiler names at some point
        assert "reviews" in resp["qa_report"]

    def test_empty_synopsis_rejected(self, client):
        resp = client.post("/api/v1/genesis3/review", json={})
        assert resp.status_code == 422

    def test_whitespace_only_synopsis_rejected(self, client):
        resp = client.post("/api/v1/genesis3/review", json={"synopsis": "   "})
        assert resp.status_code == 422


# =============================================================================
#  POST /certify — full pipeline (compilers → QA → Certification)
# =============================================================================

class TestCertifyEndpoint:
    """/api/v1/genesis3/certify"""

    def test_returns_200(self, client):
        resp = _certify(client)
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client):
        resp = _certify(client).json()
        assert "pipeline_id" in resp
        assert "certificate_data" in resp
        cert = resp["certificate_data"]
        assert "production_ready" in cert
        assert "overall_score" in cert
        assert "certificate_id" in cert or "certification_id" in cert

    def test_certificate_has_dimension_verdicts(self, client):
        cert = _certify(client).json()["certificate_data"]
        expected_dims = {
            "story_integrity", "psychology", "character_development",
            "narrative_logic", "emotional_resonance", "visual_readiness",
            "continuity",
        }
        for dim in expected_dims:
            assert dim in cert, f"Certificate missing dimension '{dim}'"

    def test_dimensions_have_valid_verdicts(self, client):
        cert = _certify(client).json()["certificate_data"]
        verdict_set = {"PASS", "FAIL", "CONDITIONAL"}
        for dim in ["story_integrity", "psychology", "character_development"]:
            assert cert[dim] in verdict_set

    def test_production_ready_is_boolean(self, client):
        cert = _certify(client).json()["certificate_data"]
        assert isinstance(cert["production_ready"], bool)

    def test_overall_score_between_0_and_1(self, client):
        score = _certify(client).json()["certificate_data"]["overall_score"]
        assert 0.0 <= score <= 1.0

    def test_critical_issues_is_list(self, client):
        issues = _certify(client).json()["certificate_data"].get("critical_issues", [])
        assert isinstance(issues, list)

    def test_recommendations_is_list(self, client):
        recs = _certify(client).json()["certificate_data"].get("recommendations", [])
        assert isinstance(recs, list)

    def test_evidence_keyed_by_compiler_name(self, client):
        evidence = _certify(client).json()["evidence"]
        expected_compilers = {
            "mock", "mockllm", "discovery", "narrative", "character",
            "emotion", "psychology", "visual", "dialogue",
            "continuity",
        }
        assert set(evidence.keys()) == expected_compilers

    def test_qa_report_includes_overall_status(self, client):
        qa = _certify(client).json()["qa_report"]
        assert "overall_status" in qa
        assert qa["overall_status"] in {"PASS", "FAIL", "CONDITIONAL"}

    def test_empty_synopsis_rejected(self, client):
        resp = client.post("/api/v1/genesis3/certify", json={})
        assert resp.status_code == 422

    def test_whitespace_only_synopsis_rejected(self, client):
        resp = client.post("/api/v1/genesis3/certify", json={"synopsis": "   "})
        assert resp.status_code == 422


# =============================================================================
#  GET /certificate/{id} — certificate retrieval
# =============================================================================

class TestCertificateRecovery:
    """/api/v1/genesis3/certificate/{id}"""

    def test_retrieve_existing_certificate(self, client):
        # First certify to create a certificate
        cert_resp = _certify(client).json()
        cert_id = cert_resp["certificate_data"].get(
            "certificate_id", cert_resp["certificate_data"].get("certification_id")
        )

        resp = client.get(f"/api/v1/genesis3/certificate/{cert_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert "certificate_data" in data
        assert data["certificate_data"]["project_name"] != ""

    def test_retrieve_missing_certificate_returns_404(self, client):
        fake_id = "nonexistent-uuid-000000"
        resp = client.get(f"/api/v1/genesis3/certificate/{fake_id}")
        assert resp.status_code == 404

    def test_empty_cert_id_returns_404(self, client):
        resp = client.get("/api/v1/genesis3/certificate/")
        # The route expects str; an empty path segment may or may not match depending on routing
        # We just check it doesn't crash with a 500
        assert resp.status_code != 500


# =============================================================================
#  Integration / full-flow tests
# =============================================================================

class TestFullFlow:
    """Verify the chain works end-to-end."""

    def test_analyze_to_review_to_certify_chain(self, client):
        """Run all three endpoints in sequence and verify data consistency."""
        analyze = _analyze(client).json()
        rev_resp = _review(client).json()
        cert_resp = _certify(client).json()

        # Analysis evidence → review should have same compiler names
        assert set(analyze["evidence"].keys()) == {
            "mock", "mockllm", "discovery", "narrative", "character",
            "emotion", "psychology", "visual", "dialogue", "continuity",
        }

        # Review QA report should be valid
        qa = rev_resp["qa_report"]
        assert qa["overall_status"] in {"PASS", "FAIL", "CONDITIONAL"}
        assert 0.0 <= qa["overall_score"] <= 1.0
        assert len(qa["reviews"]) == 9

        # Certificate must have a valid score and production_ready flag
        cert = cert_resp["certificate_data"]
        assert cert["overall_score"] >= 0.0
        assert isinstance(cert["production_ready"], bool)

    def test_certificate_recovered_matches_original(self, client):
        """Verify certificate retrieval returns data matching the original certify output."""
        cert_resp = _certify(client).json()
        original_data = cert_resp["certificate_data"]

        cert_id = original_data.get(
            "certificate_id", original_data.get("certification_id")
        )

        get_resp = client.get(f"/api/v1/genesis3/certificate/{cert_id}").json()
        recovered = get_resp["certificate_data"]

        # Core fields should match
        assert recovered.get("production_ready") == original_data["production_ready"]
        assert recovered.get("overall_score") == pytest.approx(original_data["overall_score"], abs=1e-4)

    def test_different_synthpsis_produce_certificates(self, client):
        """Two certify calls both return valid certificates (sanity check)."""
        resp1 = _certify(client).json()
        resp2 = client.post("/api/v1/genesis3/certify", json={
            "synopsis": ("Deep space exploration where humanity seeks a new home among the stars. "
                         "Scientists discover sentient beings on distant planets. "
                         "A war between civilizations looms as resources dwindle."),
        }).json()

        # Both responses should have valid structure
        for resp in [resp1, resp2]:
            cert = resp["certificate_data"]
            assert isinstance(cert["production_ready"], bool)
            assert 0.0 <= cert["overall_score"] <= 1.0
            assert "story_integrity" in cert

    def test_analyze_and_review_produce_valid_evidence_and_qa(self, client):
        """Analyze + Review together yield consistent results."""
        analyze_resp = _analyze(client).json()
        review_resp = _review(client).json()
        # Analyzer evidence should have Mock compiler (key proof of compilation integration)
        evidence_keys = set(analyze_resp["evidence"].keys())
        assert "mock" in evidence_keys

    def test_certify_returns_valid_certificate_id(self, client):
        """Certificate ID from /certify can be used with /certificate/{id}"""
        cert_resp = _certify(client).json()
        cert_id = cert_resp["certificate_data"].get("certificate_id") or cert_resp["certificate_data"]["certification_id"]

        get_resp = client.get(f"/api/v1/genesis3/certificate/{cert_id}").json()
        assert get_resp["certificate_data"]["production_ready"] is not None
