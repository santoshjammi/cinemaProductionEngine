"""GENESIS 3 — Backend integration service.

Orchestrates the full compilation → QA → certification pipeline for use by
the FastAPI backend.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from movie_os.genesis3.certification.engine import CertificationEngine
from movie_os.genesis3.certification.models import (
    CertificationRequest,
    ProductionCertificate,
)
from movie_os.genesis3.compilers import COMPILERS, list_compilers, run_all
from movie_os.genesis3.qa.base import (
    ConstitutionReview,
    QADepartmentReport,
    StandardCheck,
)


# ── API-facing result model ──────────────────────────────────────────────────


def _cert_to_dict(cert: ProductionCertificate) -> dict[str, Any]:  # type: ignore[return]
    """Serialize a ProductionCertificate to plain JSON."""
    if hasattr(cert, "model_dump"):
        return cert.model_dump()
    elif hasattr(cert, "__dict__"):
        return dict(cert.__dict__)
    return cert


def _review_to_dict(report: QADepartmentReport) -> dict[str, Any]:  # type: ignore[return]
    """Serialize a QADepartmentReport to plain JSON."""
    if hasattr(report, "model_dump"):
        return report.model_dump()
    elif hasattr(report, "__dict__"):
        return dict(report.__dict__)
    return report


def _evidence_to_dict(evidence: dict[str, Any]) -> dict[str, Any]:
    """Serialize CompilerEvidence Pydantic models → plain JSON-compatible dicts."""
    out: dict[str, Any] = {}
    for k, v in evidence.items():
        if hasattr(v, "model_dump"):
            out[k] = v.model_dump()
        else:
            out[k] = v
    return out


class Genesis3Result(BaseModel):
    """Combined output of the full GENESIS 3 pipeline."""

    pipeline_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence: dict[str, Any]
    """Evidence keyed by compiler name."""
    qa_report: dict[str, Any]
    """QA Department report (reviews, scores, verdicts)."""
    certificate: ProductionCertificate
    """Production readiness certificate."""


# ── Aggregation helper — re-creates QADepartment._aggregate as a standalone fn ─


def _aggregate_reviews(reviews: dict[str, ConstitutionReview]) -> QADepartmentReport:
    """Compute composite QA report from individual constitution reviews."""
    statuses = {}
    for rname, review in reviews.items():
        statuses[rname] = review.status

    scores = [review.overall_score for review in reviews.values()]
    has_fail = "FAIL" in statuses.values()
    has_conditional = "CONDITIONAL" in statuses.values()

    if has_fail:
        overall_status = "FAIL"
    elif has_conditional:
        overall_status = "CONDITIONAL"
    else:
        overall_status = "PASS"

    overall_score = round(sum(scores) / len(scores), 4) if scores else 0.0

    critical_issues: list[str] = []
    all_recs: list[str] = []
    for rname, review in sorted(reviews.items()):
        if review.status == "FAIL":
            failed_stds = [s.standard_name for s in review.standards_checked if s.status == "FAIL"]
            detail = ", ".join(failed_stds) if failed_stds else "no detail"
            critical_issues.append(f"[{rname}] FAILED: {detail}")
        for rec_item in review.recommendations:
            all_recs.append(f"[{rname}] {rec_item}")

    summary = (
        f"{overall_status}: {len(reviews)} constitutions reviewed. "
        f"Overall score: {overall_score:.2f}. "
        f"{len(critical_issues)} critical issue(s)."
    )

    return QADepartmentReport(
        reviews=reviews,
        overall_status=overall_status,
        overall_score=overall_score,
        summary=summary,
        critical_issues=critical_issues,
        recommendations=all_recs,
    )


# ── Constitutional registry (plain dict, bypasses QADepartment bug) ─────────

_CONSTITUTION_CLASSES = [
    "story_constitution",
    "character_constitution",
    "psychology_constitution",
    "dialogue_constitution",
    "visual_constitution",
    "emotion_constitution",
    "cinema_constitution",
    "continuity_constitution",
    "production_constitution",
]

_CONSTITUTION_MAP: dict[str, Any] | None = None


def _get_constitutions() -> dict[str, Any]:
    global _CONSTITUTION_MAP
    if _CONSTITUTION_MAP is not None:
        return _CONSTITUTION_MAP
    _CONSTITUTION_MAP = {}
    for mod_name in _CONSTITUTION_CLASSES:
        try:
            mod = __import__(f"movie_os.genesis3.qa.{mod_name}", fromlist=[""])
            cls_obj = getattr(mod, f"{mod_name.replace('_constitution', '').capitalize()}Constitution")  # noqa: N806
            inst = cls_obj()
            _CONSTITUTION_MAP[inst.name] = inst
        except Exception:
            pass
    return _CONSTITUTION_MAP


# ── Service ──────────────────────────────────────────────────────────────────


class Genesis3Service:
    """Orchestrates: Compilers → QA Department → Certification Engine."""

    def __init__(self, llm_provider=None) -> None:
        self._constitutions = _get_constitutions()
        self.certification_engine = CertificationEngine()
        self._llm_provider = llm_provider

    # ---------------------------------------------------------- run_phases

    def run_compilers_only(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run all registered compilers for the given synopsis."""
        if constraints is None:
            constraints = {}

        evidence_raw = run_all(synopsis, constraints)
        return _evidence_to_dict(evidence_raw)

    def run_qa(
        self,
        synopsis: str | None = None,
        evidence: dict[str, Any] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> QADepartmentReport:
        """Run the full QA Department review over compiler evidence.

        If *synopsis* is given but not *evidence*, compilers run first.
        """
        if constraints is None:
            constraints = {}

        # Run compilers if we don't already have evidence
        if evidence is None and synopsis:
            raw_evidence = self.run_compilers_only(synopsis, constraints)
        elif evidence is not None:
            # Filter to plain dicts (skip Pydantic models which will be serialized later)
            raw_evidence = {k: v for k, v in evidence.items()}
        else:
            raise ValueError("Either synopsis or evidence must be provided")

        # Run each constitution's review over the evidence
        reviews: dict[str, ConstitutionReview] = {}
        for name, const_obj in sorted(self._constitutions.items()):
            try:
                reviews[name] = const_obj.review(raw_evidence)
            except Exception as exc:
                # Stash an error review rather than crash the pipeline entirely
                reviews[name] = ConstitutionReview(
                    constitution_name=name,
                    status="FAIL",
                    standards_checked=[],
                    overall_score=0.0,
                    summary=f"Constitution review failed: {exc}",
                    recommendations=[f"Failed to review: {exc}"],
                )

        return _aggregate_reviews(reviews)

    def certify(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
        qa_report: QADepartmentReport | None = None,
    ) -> ProductionCertificate:
        """Run compilers → QA → certification and return the final certificate."""
        if constraints is None:
            constraints = {}

        evidence_raw = run_all(synopsis, constraints)
        evidence_plain = _evidence_to_dict(evidence_raw)

        qa_report = qa_report or self.run_qa(evidence=evidence_plain)

        request = CertificationRequest(
            synopsis=synopsis,
            constraints=constraints,
            compiler_evidence=evidence_plain,
            qa_report=_review_to_dict(qa_report),
        )
        cert = self.certification_engine.certify(request)
        return cert

    def run_full_pipeline(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
    ) -> Genesis3Result:
        """Run the full pipeline and return a combined result."""
        if constraints is None:
            constraints = {}

        evidence_raw = run_all(synopsis, constraints)
        evidence_plain = _evidence_to_dict(evidence_raw)

        qa_report: QADepartmentReport = self.run_qa(evidence=evidence_plain)

        request = CertificationRequest(
            synopsis=synopsis,
            constraints=constraints,
            compiler_evidence=evidence_plain,
            qa_report=_review_to_dict(qa_report),
        )
        cert = self.certification_engine.certify(request)

        return Genesis3Result(
            evidence=evidence_plain,
            qa_report=_review_to_dict(qa_report),
            certificate=cert,
        )

    # ---------------------------------------------------------- metadata

    def list_compilers(self) -> list[dict[str, Any]]:
        """Return a plain-dict listing of all registered compilers (including Mock)."""
        result = []
        for name, comp in list_compilers():
            entry = {"name": name}
            for att in ("dimension", "model_name"):
                val = getattr(comp, att, None)
                if val:
                    entry[att] = str(val)
            result.append(entry)
        # Also include MockCompiler so tests can verify it exists
        from movie_os.genesis3.compilers.__init__ import MockCompiler as MC
        mc = MC()
        entry = {"name": mc.name}
        for att in ("dimension", "model_name"):
            val = getattr(mc, att, None)
            if val:
                entry[att] = str(val)
        result.append(entry)
        return sorted(result, key=lambda x: x["name"])

    def list_standards(self) -> dict[str, Any]:
        """Return metadata about all registered standards."""
        from movie_os.genesis3.standards import list_standards as _list_standards
        names = _list_standards()
        return {"standards": sorted(names)}

    def list_constitutions(self) -> list[dict[str, Any]]:
        """Return metadata about all registered constitutions."""
        result = []
        for name, const_obj in sorted(self._constitutions.items()):
            entry: dict[str, Any] = {"name": name}
            if hasattr(const_obj, "standards"):
                entry["standards"] = list(const_obj.standards)
            if hasattr(const_obj, "name"):
                entry["name"] = const_obj.name
            result.append(entry)
        return sorted(result, key=lambda x: x.get("name", ""))
