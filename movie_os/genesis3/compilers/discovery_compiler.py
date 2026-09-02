"""Discovery Compiler -- finds the core premise, theme, central question, and dramatic potential."""

from __future__ import annotations

import re
from typing import Any

from movie_os.genesis3.compilers.base import BaseCompiler, CompilerEvidence, EvidenceItem, Finding

PREMISE_HINTS = [
    "about a", "follows a", "centers on", "story of", "premise is",
    "the story", "protagonist", "hero embarks", "journey", "quest",
]
THEME_HINTS = [
    "theme", "message", "lesson", "taught", "learned", "means",
    "symbolizes", "represents", "about love", "about life",
    "exploring", "examines", "explores", "question",
]
DRAMATIC_HINTS = [
    "conflict", "struggle", "battle", "fight", "war", "rally",
    "save", "discover", "uncover", "reveal", "secret", "mystery",
    "race against", "dilemma", "choice", "sacrifice",
]

PUNCTUATION_PATTERNS = re.compile(r"[.,;!?]")


class DiscoveryCompiler(BaseCompiler):
    name = "Discovery"
    dimension = "Story Discovery"

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        findings: list[Finding] = []
        evidence_items: list[EvidenceItem] = []
        stripped = (synopsis or "").strip()

        # --- Premise identification ---
        has_premise = any(ph.lower() in stripped for ph in PREMISE_HINTS)
        premise_span = ""
        if has_premise:
            sentences = PUNCTUATION_PATTERNS.split(stripped)
            candidates = [s.strip() for s in sentences if len(s.strip()) > 10]
            if candidates:
                premise_span = max(candidates, key=len)

        findings.append(Finding(
            category="premise",
            status="pass" if has_premise else "warning",
            statement=("Premise identified" if has_premise else "Premise not clearly stated"),
            detail=f"Found {len([ph for ph in PREMISE_HINTS if ph.lower() in stripped])} premise indicator(s)",
            references=[premise_span] if premise_span else [],
        ))

        evidence_items.append(EvidenceItem(
            claim="Premise located within story text" if has_premise else "Premise weak or absent",
            supporting_text=premise_span if premise_span else stripped[:80],
            source="synopsis" if premise_span else "synopsis_full",
        ))

        # --- Theme extraction ---
        theme_words = [th for th in THEME_HINTS if th.lower() in stripped]
        has_theme = len(theme_words) > 0
        extracted_theme = theme_words[0].upper() if has_theme else "UNSPECIFIED"

        findings.append(Finding(
            category="theme",
            status="pass" if has_theme else "warning",
            statement=("Theme extracted" if has_theme else "Theme not explicitly stated"),
            detail=f"Discovered theme keywords: {', '.join(theme_words) or 'none detected'}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Central theme identified as '" + extracted_theme + "'",
            supporting_text=stripped[:120],
            source="synopsis_keywords",
        ))

        # --- Central question formulation ---
        query_terms = ["can they", "will it", "what if", "how can",
                       "dare to", "is able", "must they", "should he", "should she"]
        has_question = ("?" in stripped or
                        any(q in stripped.lower() for q in query_terms))
        question_span = ""
        if has_question:
            qs = [q.strip() for q in PUNCTUATION_PATTERNS.split(stripped)
                  if any(w in q.lower() for w in ["can", "will", "what",
                                                    "how", "dare",
                                                    "must", "should"])]
            question_span = max(qs, key=len) if qs else ""

        findings.append(Finding(
            category="central_question",
            status=("pass" if has_question and question_span
                    else "warning" if has_question else "info"),
            statement=("Central dramatic question formulated with interrogative"
                       if has_question and question_span
                       else "Central dramatic question implicit but not explicit"),
            detail="Interrogative query present: " + str(bool(question_span)),
            references=[question_span] if question_span else [],
        ))

        evidence_items.append(EvidenceItem(
            claim="Dramatic tension exists to support a central question",
            supporting_text=(question_span or
                             PUNCTUATION_PATTERNS.split(stripped)[0] or
                             "no direct query found"),
            source="synopsis_dramatic_elements",
        ))

        # --- Dramatic potential ---
        dramatic_scores = sum(1 for d in DRAMATIC_HINTS if d.lower() in stripped)
        if dramatic_scores >= 5:
            dram_label = "strong"
            dram_status = "pass"
        elif dramatic_scores >= 3:
            dram_label = "moderate"
            dram_status = "warning"
        else:
            dram_label = "low"
            dram_status = "fail"

        det = [d for d in DRAMATIC_HINTS if d.lower() in stripped]
        findings.append(Finding(
            category="dramatic_potential",
            status=dram_status,
            statement=f"Dramatic potential {dram_label}",
            detail=f"Found {dramatic_scores} dramatic indicators: {det}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Story carries dramatic weight through conflict markers",
            supporting_text=str(det[:3]),
            source="synopsis_dramatic_markers",
        ))

        # confidence heuristic based on evidence density
        total_signals = (1 if has_premise else 0) + (1 if has_theme else 0) + \
                         (1 if has_question else 0) + dramatic_scores
        evidence_density = min(1.0, total_signals / 6) if stripped else 0.0
        conf = round(evidence_density * 0.9, 2)

        summary = self._build_summary(has_premise, has_theme, question_span, dramatic_scores)
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=conf,
            summary=summary,
        )

    def _build_summary(self, has_premise: bool, has_theme: bool,
                       question_span: str, dramatic_scores: int) -> str:
        parts = []
        if has_premise:
            parts.append("Premise clearly identified")
        else:
            parts.append("Premise requires clarification")
        if has_theme:
            parts.append("Theme present and extractable")
        else:
            parts.append("Theme needs more explicit grounding")
        if dramatic_scores >= 3:
            parts.append(f"{dramactic_scores} dramatic indicators found")
        else:
            parts.append("Drama markers sparse -- consider strengthening conflict")
        return "; ".join(parts) + "."
