"""GENESIS 3 — Certification Engine.

The CertificationEngine is the final gate in GENESIS. After QA review completes
against all constitutions, the engine issues a ProductionReadiness Certificate.
When ``production_ready`` is True PROMETHEUS begins rendering.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Union

from movie_os.genesis3.certification.models import CertificationRequest, ProductionCertificate


# ── Constants ────────────────────────────────────────────────────────────────

_DIMENSION_MAP: List[tuple[str, str]] = [
    ("story", "story_integrity"),
    ("character", "character_development"),
    ("psychology", "psychology"),
    ("dialogue", "narrative_logic"),
    ("emotion", "emotional_resonance"),
    ("visual", "visual_readiness"),
    ("continuity", "continuity"),
]

_DIMENSIONS: List[tuple[str, str]] = [
    ("story_integrity", "Story Integrity"),
    ("psychology", "Psychology"),
    ("character_development", "Character Development"),
    ("narrative_logic", "Narrative Logic"),
    ("emotional_resonance", "Emotional Resonance"),
    ("visual_readiness", "Visual Readiness"),
    ("continuity", "Continuity"),
]


# ── Helpers ──────────────────────────────────────────────────────────────────


def _val(obj: Any, key: str, default: Any) -> Any:
    """Return obj[key] or getattr(obj, key); fall back to *default*."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _str_val(obj: Any, key: str, default: str) -> str:
    """Str-safe pull; empty → default."""
    v = _val(obj, key, None)
    if v is None or v == "":
        return default
    return str(v)


class CertificationEngine:
    """Final gate — issues Production Readiness Certificates."""

    # ------------------------------------------------------------------ certify

    def certify(self, request: CertificationRequest) -> ProductionCertificate:
        qa = request.qa_report

        reviews: Union[dict, Any] = _val(qa, "reviews", {})
        qa_summary: str = _str_val(qa, "summary", "")
        qa_status: str = _str_val(qa, "overall_status", "")

        # Normalise each review entry to a plain dict with status / scores.
        normed: Dict[str, Any] = {}
        if isinstance(reviews, dict):
            for rk, rv in reviews.items():
                if isinstance(rv, dict):
                    normed[rk] = rv
                else:
                    normed[rk] = {
                        "status": _str_val(rv, "status", "FAIL"),
                        "overall_score": _val(rv, "overall_score", 0.0),
                        "standards_checked": getattr(rv, "standards_checked", []),
                    }

        verdicts: Dict[str, Literal["PASS", "FAIL", "CONDITIONAL"]] = {}
        scores: List[float] = []

        for const_name, dim_key in _DIMENSION_MAP:
            rev = normed.get(const_name)
            if rev is None or not isinstance(rev, dict):
                verdicts[dim_key] = "FAIL"
                scores.append(0.0)
                continue

            status = _str_val(rev, "status", "FAIL")
            if status not in ("PASS", "FAIL", "CONDITIONAL"):
                status = "FAIL"
            verdicts[dim_key] = status

            raw_sc = _val(rev, "overall_score", 0.0)
            try:
                scores.append(float(raw_sc))
            except (TypeError, ValueError):
                scores.append(0.0)

        production_ready: bool = qa_status == "PASS"

        # Use QA-report's authoritative overall_score when available.
        raw_qa_score = _val(qa, "overall_score", None)
        if raw_qa_score is not None:
            try:
                overall_score = max(0.0, min(1.0, float(raw_qa_score)))
            except (TypeError, ValueError):
                overall_score = round(sum(scores) / len(scores), 4) if scores else 0.0
        else:
            overall_score = round(sum(scores) / len(scores), 4) if scores else 0.0

        critical_issues: List[str] = list(_val(qa, "critical_issues", []) or [])
        recommendations: List[str] = list(_val(qa, "recommendations", []) or [])

        # Add per-dimension failures that the QA report didn't surface.
        for const_name, dim_key in _DIMENSION_MAP:
            rev = normed.get(const_name)
            if rev is not None and isinstance(rev, dict) and _str_val(rev, "status", "") == "FAIL":
                has_key = any(f"[{const_name}]" in ci for ci in critical_issues)
                if not has_key:
                    stds_failed = [
                        s["standard_name"]
                        for s in (rev.get("standards_checked") or [])
                        if isinstance(s, dict) and _val(s, "standard_name", "")
                    ]
                    detail = ", ".join(stds_failed) if stds_failed else "multiple failures"
                    critical_issues.append(f"[{const_name}] FAILED: {detail}")

        synopsis_short = (request.synopsis or "")[:50]
        project_name = _str_val(request.constraints, "project", "") or synopsis_short

        cert_kwargs: Dict[str, Any] = {
            "project_name": str(project_name),
            "synopsis_summary": (request.synopsis or "")[:200],
            "production_ready": production_ready,
            "overall_score": overall_score,
            "critical_issues": critical_issues,
            "recommendations": recommendations,
            "qa_report_summary": qa_summary,
        }
        for dim_key in [mk for _, mk in _DIMENSION_MAP]:
            cert_kwargs[dim_key] = verdicts.get(dim_key, "FAIL")

        cert = ProductionCertificate(**cert_kwargs)
        # Always generate the body — ignore empty-string early return.
        cert.certificate_body = self._build_body(cert)
        return cert

    # ------------------------------------------------------------------ formatting

    def _status_mark(self, s: str) -> str:
        if s == "PASS":
            return chr(9745)  # ✓
        if s == "CONDITIONAL":
            return chr(8637)  # ?
        return chr(10006)  # ✗

    def _build_body(self, cert: ProductionCertificate) -> str:
        """Build the ornamental text certificate."""
        TL = chr(0x2554)  # ╔
        TR = chr(0x2557)  # ╗
        BL = chr(0x255A)  # ╚
        BR = chr(0x255D)  #╝
        HR = chr(0x2550)  # ═
        VL = chr(0x2551)  # │

        W = 66  # inner content width
        sep = TL + HR * (W - len(TL) - len(TR)) + TR
        row = lambda t: VL + t.center(W) + VL  # noqa: E731 — short convenience
        hr = lambda: row("")  # a purely horizontal rule

        lines: List[str] = []

        def add(t: str) -> None:
            lines.append(row(t))

        # Top border / title
        lines.append(sep)
        add("PRODUCTION READINESS CERTIFICATE")
        lines.append(sep)

        # Metadata
        fmt_val = lambda v: str(v) if v is not None else ""
        add(f"{'Project:':<30s}  {fmt_val(cert.project_name)}")
        add(f"{'Certificate ID:':<30s}  {fmt_val(cert.certification_id)}")
        add(f"{'Issued:':<30s}  {fmt_val(cert.issued_at.strftime('%Y-%m-%dT%H:%M:%SZ') + ' UTC')}")

        lines.append(sep)

        # Verdict table
        add(f"{'Dimension':<30s}  {'Verdict':>18s}")
        lines.append(hr())

        for key, label in _DIMENSIONS:
            v = getattr(cert, key, "?")
            mark = self._status_mark(v)
            verdict_cell = f"{v}  {mark}"
            add(f"{'  ' + label:<30s}  {verdict_cell:>18s}")

        lines.append(hr())

        # Verdict
        ready_icon = "YES ✓" if cert.production_ready else "NO ✗"
        add(f"{'Production Ready:':<30s}  {ready_icon:>18s}")
        score_str = f"{cert.overall_score:.2f}"
        add(f"{'Overall Score:':<30s}  {score_str:>18s}")

        lines.append(hr())

        # Critical issues
        if cert.critical_issues:
            header = f"Critical Issues ({len(cert.critical_issues)} found):"
            add(header)
            for issue in cert.critical_issues[:10]:
                add(f"  • {issue}")
        else:
            add("Critical Issues:    None")

        # Recommendations
        if cert.recommendations:
            lines.append(hr())
            header = f"Recommendations ({len(cert.recommendations)} given):"
            add(header)
            for rec in cert.recommendations[:10]:
                add(f"    → {rec}")

        # Bottom border
        lines.append(sep)
        lines.append(BL + HR * (W - len(BL) - len(BR)) + BR)
        lines.append("")

        cert.certificate_body = "\n".join(lines)
        return cert.certificate_body
