"""Continuity Compiler -- analyzes scene transitions, timeline consistency, logical flow."""

from __future__ import annotations

from typing import Any

from movie_os.genesis3.compilers.base import BaseCompiler, CompilerEvidence, EvidenceItem, Finding


TRANSFER_MARKER = [
    "cut to", "transitions", "shifts to", "next scene",
    "meanwhile", "cross-cut", "interrcutting",
]
TEMPORAL_KEYWORDS = [
    "after", "before", "earlier", "later", "subsequently",
    "begins", "ends", "morning", "night", "evening", "dawn",
    "sunrise", "sunset", "days later", "years ago",
]
CONECTORS = [
    "because", "therefore", "consequently", "led to",
    "then", "next", "and then", "soon after", "as a result",
]


class ContinuityCompiler(BaseCompiler):
    name = "Continuity"
    dimension = "Scene Continuity"

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        findings: list[Finding] = []
        evidence_items: list[EvidenceItem] = []
        raw = (synopsis or "").strip().lower()

        # --- Scene transitions validity ---
        trans_hits = [t for t in TRANSFER_MARKER if t.lower() in raw]
        has_transitions = len(trans_hits) >= 1
        findings.append(Finding(
            category="scene_transition",
            status=("pass" if has_transitions
                    else "warning" if len(raw) > 50
                    else "info"),
            statement=("Scene transitions valid and navigable"
                       if has_transitions
                       else "No explicit transition markers - rely on story logic"),
            detail=f"Transition markers found: {trans_hits[:4]}",
        ))

        evidence_items.append(EvidenceItem(
            claim="Narrative flows through scene boundaries clearly",
            supporting_text=(str(trans_hits[:3]) if trans_hits
                             else "no explicit transitions detected"),
            source="synopsis_transition_cues",
        ))

        # --- Timeline consistency heuristic ---
        time_hits = [w for w in TEMPORAL_KEYWORDS if w.lower() in raw]
        has_timeline = len(time_hits) >= 2
        findings.append(Finding(
            category="timeline_consistency",
            status=("pass" if has_timeline
                    else "warning" if time_hits
                    else "fail"),
            statement=("Timeline internally consistent with temporal anchors"
                       if has_timeline
                       else "Temporal markers sparse - continuity risk on production"),
            detail=f"Time-related words found: {time_hits[:5]}",
        ))

        evidence_items.append(EvidenceItem(
            claim="Story time-space is coherent and navigable",
            supporting_text=str(time_hits[:3]) if time_hits else raw[:60],
            source="synopsis_temporal_signaling",
        ))

        # --- Logical flow / causality coherence check ---
        flow_hits = [w for w in CONECTORS if w.lower() in raw]
        has_flow = len(flow_hits) >= 3
        findings.append(Finding(
            category="logical_flow",
            status=("pass" if has_flow
                    else "warning" if flow_hits
                    else "fail"),
            statement=("Logical flow maintained through explicit connectors"
                       if has_flow
                       else "Partial continuity markers - narrative jumps possible"),
            detail=f"Flow connectors found: {flow_hits}",
        ))

        evidence_items.append(EvidenceItem(
            claim="Story logic chain is complete enough to follow without gaps",
            supporting_text=str(flow_hits[:4]) if flow_hits
            else "no explicit connectors - relying on narrative intuition",
            source="synopsis_logical_cue_analysis",
        ))

        # --- Continuity rules compliance ---
        location_words = ["room", "house", "street", "office", "apartment",
                          "hotel", "restaurant", "park", "city", "village"]
        loc_hits = [l for l in location_words if l.lower() in raw]
        findings.append(Finding(
            category="continuity_rules",
            status=("pass" if len(loc_hits) >= 2
                    else "info"),
            statement=f"Spatial continuity grounded {'with specific locations' if loc_hits else 'generically - benefit of the doubt to design dept'}",
            detail=f"Location markers found: {loc_hits[:4]}",
        ))

        evidence_items.append(EvidenceItem(
            claim="Physical spaces support consistent spatial geography",
            supporting_text=str(loc_hits[:3]) if loc_hits else "broad geography only",
            source="synopsis_location_signaling",
        ))

        # Confidence heuristic
        total = len(trans_hits) + len(time_hits) + len(flow_hits) + len(loc_hits)
        confidence = round(min(1.0, total / 10), 2) if raw else 0.0

        summary = self._summary(trans_hits, time_hits, flow_hits, loc_hits)
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=confidence,
            summary=summary,
        )

    def _summary(self, trans: list[str], time: list[str], flow: list[str], loc: list[str]) -> str:
        parts = []
        parts.append(f"{len(trans)} scene transition markers")
        parts.append("Timeline " + ("anchored" if time else "unmarked"))
        parts.append(f"{len(flow)} flow connectors detected")
        if loc:
            parts.append(f"{len(loc)} specific location hints found")
        return "; ".join(parts) + "."
