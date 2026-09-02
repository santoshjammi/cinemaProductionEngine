"""Narrative Compiler — analyzes plot structure, cause-effect chain, subplot integration, pacing."""

from __future__ import annotations

from typing import Any

from movie_os.genesis3.compilers.base import BaseCompiler, CompilerEvidence, EvidenceItem, Finding


# Keywords for narrative analysis
ACT_MARKER = ["act", "first half", "second half", "third act", "beginning", "middle", "end"]
CAUSE_EFFECT = [
    "because", "therefore", "as a result", "consequence", "led to",
    "caused", "triggered", "prompted", "resulted in", "forced",
]
SUBPLOT_MARKER = [
    "parallel", "subsequently", "meanwhile", "similarly", "alternately",
    "secondary storyline", "side story", "subplot", "intertwined",
]
PACING_KEYWORDS = [
    "rapidly", "slowly", "gradually", "suddenly", "quickly",
    "momentum", "building", "tension", "pacing", "rhythm",
]
STRUCTURE_MARKER = [
    "three-act", "three act", "hero's journey", "hero's, hero’s, monomyth",
    "in media res", "flashback", "parallel", "circle back", "full circle",
    "climax", "resolution", "turning point", "inciting incident",
]


class NarrativeCompiler(BaseCompiler):
    name = "Narrative"
    dimension = "Narrative Engineering"

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        findings: list[Finding] = []
        evidence_items: list[EvidenceItem] = []
        raw = (synopsis or "").strip().lower()

        # --- Act structure detection ---
        act_mentions = [a for a in ACT_MARKER if a in raw]
        has_structure = any(s.lower() in raw for s in STRUCTURE_MARKER)
        findings.append(Finding(
            category="act_structure",
            status="pass" if len(act_mentions) >= 2 or has_structure else "warning",
            statement=("Three-act structure detected" if (len(act_mentions) >= 2 or has_structure) else "Act structure unclear"),
            detail=f"Act-related terms found: {act_mentions}",
            references=[a for a in act_mentions] if act_mentions else [],
        ))

        evidence_items.append(EvidenceItem(
            claim="Narrative framework exists within the synopsis",
            supporting_text=", ".join(act_mentions) or "implicit structure inferred from context",
            source="synopsis_language_patterns",
        ))

        # --- Cause-effect chain validity ---
        cause_markers = [c for c in CAUSE_EFFECT if c in raw]
        has_chain = len(cause_markers) >= 2
        findings.append(Finding(
            category="cause_effect",
            status="pass" if has_chain else "warning",
            statement="Cause-effect chain " + ("valid" if has_chain else "requires strengthening"),
            detail=f"Found {len(cause_markers)} causal connectors: {cause_markers}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Events are causally linked or can be inferred",
            supporting_text=str(cause_markers[:3]),
            source="synopsis_causal_language",
        ))

        # --- Subplot integration ---
        subplot_mentions = [s for s in SUBPLOT_MARKER if s in raw]
        has_subplots = len(subplot_mentions) >= 1
        findings.append(Finding(
            category="subplot_integration",
            status="pass" if has_subplots else "info",
            statement="Subplots " + ("present and integrated" if has_subplots else "not explicitly present — may strengthen with"),
            detail=f"Subplot indicators: {subplot_mentions or 'none detected'}",
            references=subplot_mentions,
        ))

        evidence_items.append(EvidenceItem(
            claim="Story has narrative depth to support multi-thread plotting" if has_subplots else "Single-thread narrative — consider adding parallel arc",
            supporting_text=str(subplot_mentions[:2]) if subplot_mentions else raw[:60],
            source="synopsis_layering_signals",
        ))

        # --- Pacing analysis ---
        pacing_hits = [p for p in PACING_KEYWORDS if p in raw]
        pacing_status = "pass" if len(pacing_hits) >= 2 else ("warning" if pacing_hits else "fail")
        findings.append(Finding(
            category="pacing",
            status=pacing_status,
            statement=f"Pacing markers {'clear' if len(pacing_hits) >= 3 else 'partial' if pacing_hits else 'absent'}",
            detail=f"Pacing indicators found: {pacing_hits}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Rhythmic intent is expressible from text cues",
            supporting_text=str(pacing_hits[:3]),
            source="synopsis_rhythm_cues",
        ))

        # Confidence heuristic
        total_strength = (1 if has_structure else 0) + (1 if has_chain else 0) + len(cause_markers) + (1 if has_subplots else 0) + len(pacing_hits)
        confidence = round(min(1.0, total_strength / 8), 2) if raw else 0.0

        summary = self._summary(has_structure, has_chain, subplot_mentions, pacing_hits)
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=confidence,
            summary=summary,
        )

    def _summary(self, has_structure: bool, has_chain: bool, subplots: list[str], pacing: list[str]) -> str:
        parts = []
        parts.append("Structure " + ("present" if has_structure else "needs definition"))
        parts.append("Causality " + ("strong" if has_chain else "sparse"))
        if subplots:
            parts.append(f"{len(subplots)} subplot signals detected")
        else:
            parts.append("No explicit subplot markers — consider adding secondary thread")
        if pacing:
            parts.append(f"Pacing signaled by {len(pacing)} cues")
        return "; ".join(parts) + "."
