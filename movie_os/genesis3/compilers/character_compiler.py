"""Character Compiler — analyzes character arcs, motivations, relationships, growth."""

from __future__ import annotations

from typing import Any

from movie_os.genesis3.compilers.base import BaseCompiler, CompilerEvidence, EvidenceItem, Finding


CHARACTER_MARKER = [
    "protagonist", "hero", "villain", "antagonist", "love interest",
    "mentor", "sidekick", "friend", "rival", "enemy",
]
MOTIVATION_MARKER = [
    "wants", "needs", "desires", "goal", "purpose", "motivation",
    "seeking", "searching", "pursuing", "determined", "resolved",
]
RELATIONSHIP_MARKER = [
    "relationship", "bond", "connects with", "clashes with", "trusts",
    "opposes", "partners with", "allies", "confides in", "betrayal",
]
GROWTH_MARKER = [
    "changes", "grows", "learns", "discovers", "realizes", "evolves",
    "transforms", "matures", "breaks free", "finds courage",
    "overcomes", "conquers", "becomes", "redeems",
]


class CharacterCompiler(BaseCompiler):
    name = "Character"
    dimension = "Character Development"

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        findings: list[Finding] = []
        evidence_items: list[EvidenceItem] = []
        raw = (synopsis or "").strip().lower()

        # --- Character arc completeness ---
        chars = [c for c in CHARACTER_MARKER if c in raw]
        growth_hits = [g for g in GROWTH_MARKER if g in raw]
        has_arc = len(growth_hits) >= 1
        findings.append(Finding(
            category="character_arc",
            status="pass" if has_arc and chars else ("warning" if growth_hits or chars else "fail"),
            statement=("Character arc complete" if has_arc else ("characters present but growth unmarked" if growth_hits else "No character transformation signaled")),
            detail=f"Character types: {chars[:3]}; growth verbs: {growth_hits[:3]}",
            references=[c for c in chars[:2]] if chars else [],
        ))

        evidence_items.append(EvidenceItem(
            claim="Character arc exists and is trackable",
            supporting_text=", ".join(growth_hits) or "no explicit growth verbs found",
            source="synopsis_character_journey",
        ))

        # --- Motivation consistency ---
        mot_hits = [m for m in MOTIVATION_MARKER if m in raw]
        has_motivation = len(mot_hits) >= 2
        findings.append(Finding(
            category="motivation",
            status="pass" if has_motivation else "warning",
            statement=("Motivation consistent and clear" if has_motivation else "Motivation weak or implicit"),
            detail=f"Motivation markers found: {mot_hits}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Character driving force is identifiable",
            supporting_text=str(mot_hits[:3]),
            source="synopsis_motivation_cues",
        ))

        # --- Relationship dynamics clarity ---
        rel_hits = [r for r in RELATIONSHIP_MARKER if r in raw]
        has_relationships = len(rel_hits) >= 1
        findings.append(Finding(
            category="relationship_dynamics",
            status="pass" if has_relationships else "info",
            statement="Relationship dynamics " + ("clear and defined" if has_relationships else "not explicit — could be stronger"),
            detail=f"Relationship indicators: {rel_hits or 'none detected'}",
            references=rel_hits,
        ))

        evidence_items.append(EvidenceItem(
            claim="Inter-character tension exists to support ensemble",
            supporting_text=str(rel_hits[:3]) if rel_hits else raw[:60],
            source="synopsis_relationship_signals",
        ))

        # --- Character voice / internal conflict ---
        internal_conflict_markers = [
            "but", "yet", "however", "struggles", "torn between",
            "pulls apart", "conflicted", "hesitates",
        ]
        internal_hits = [m for m in internal_conflict_markers if m in raw]
        findings.append(Finding(
            category="internal_conflict",
            status="pass" if len(internal_hits) >= 2 else ("warning" if internal_hits else "info"),
            statement="Internal conflict " + ("richly textured" if len(internal_hits) >= 3 else ("present" if internal_hits else "undeveloped")),
            detail=f"Conflict language: {internal_hits[:4]}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Character interiority supports authentic psychology",
            supporting_text=str(internal_hits[:2]),
            source="synopsis_internal_conflict_markers",
        ))

        # Confidence heuristic
        total_signals = (1 if has_arc else 0) + (1 if has_motivation else 0) + (1 if has_relationships else 0) + len(internal_hits)
        confidence = round(min(1.0, total_signals / 5), 2) if raw else 0.0

        summary = self._summary(has_arc, has_motivation, rel_hits, internal_hits)
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=confidence,
            summary=summary,
        )

    def _summary(self, has_arc: bool, has_motivation: bool, rels: list[str], conflicts: list[str]) -> str:
        arc_label = "complete arc" if has_arc else "present"
        parts = []
        parts.append(f"Character {arc_label}")
        parts.append("Motivation " + ("strong" if has_motivation else "weak"))
        if rels:
            parts.append(f"{len(rels)} relational dynamics identified")
        if conflicts:
            parts.append(f"Internal tension via {len(conflicts)} markers")
        return "; ".join(parts) + "."
