"""Psychology Compiler — analyzes character psychology, behavioral consistency, internal logic."""

from __future__ import annotations

from typing import Any

from movie_os.genesis3.compilers.base import BaseCompiler, CompilerEvidence, EvidenceItem, Finding


PSYCHOLOGY_MARKER = [
    "believes", "thinks", "feels", "pretends", "hides", "reveals",
    "denies", "conceals", "suppresses", "wishes", "imagines",
    "fears", "dreads", "expects", "anticipates", "doubts",
]
BEHAVIOR_MARKER = [
    "actions speak louder", "does not", "refuses", "resists",
    "pushes away", "pulls closer", "avoids", "seeks out",
    "insist", "argues", "denies", "clings to", "lets go",
]
CONFLICT_MARKER = [
    "inner battle", "torn between", "divided", "at odds with",
    "struggle within", "conflicted", "paradox", "contradiction",
    "pulls him", "pulls her", "pushes him", "pushes her",
]
RESOLUTION_MARKER = [
    "accepts", "embraces", "confronts", "faces", "overcomes",
    "resolves", "settles", "comes to terms", "finds peace",
]


class PsychologyCompiler(BaseCompiler):
    name = "Psychology"
    dimension = "Psychological Consistency"

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        findings: list[Finding] = []
        evidence_items: list[EvidenceItem] = []
        raw = (synopsis or "").strip().lower()

        # --- Psychological depth ---
        psych_hits = [p for p in PSYCHOLOGY_MARKER if p in raw]
        has_psychology = len(psych_hits) >= 2
        findings.append(Finding(
            category="psychological_consistency",
            status="pass" if has_psychology else ("warning" if psych_hits else "fail"),
            statement="Psychological consistency maintained" if has_psychology else "Character interiority needs more explicit markers",
            detail=f"Psychology indicators: {psych_hits[:6]}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Character motivations are internally grounded",
            supporting_text=str(psych_hits[:3]),
            source="synopsis_interiority_analysis",
        ))

        # --- Behavioral logic ---
        behavior_hits = [b for b in BEHAVIOR_MARKER if b in raw]
        has_behavioral_logic = len(behavior_hits) >= 2
        findings.append(Finding(
            category="behavioral_logic",
            status="pass" if has_behavioral_logic else "warning",
            statement="Behavioral logic sound" if has_behavioral_logic else "Character behavior needs stronger motivation",
            detail=f"Action markers: {behavior_hits}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Actions stem from believable internal drivers",
            supporting_text=str(behavior_hits[:3]),
            source="synopsis_action_behavior_cues",
        ))

        # --- Internal conflict presence ---
        conflict_hits = [c for c in CONFLICT_MARKER if c in raw]
        has_conflict = len(conflict_hits) >= 1
        findings.append(Finding(
            category="internal_conflict",
            status="pass" if has_conflict else "info",
            statement=("Internal conflict clearly articulated" if has_conflict else "Internal tension implied but not explicit"),
            detail=f"Conflict language: {conflict_hits[:4]}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Psychological stake exists to drive authentic decisions",
            supporting_text=str(conflict_hits[:2]) if conflict_hits else raw[:60],
            source="synopsis_conflict_analysis",
        ))

        # --- Conflict resolution plausibility ---
        resolution_hits = [r for r in RESOLUTION_MARKER if r in raw]
        has_resolution = len(resolution_hits) >= 1
        findings.append(Finding(
            category="conflict_resolution",
            status="pass" if has_resolution else "info",
            statement=("Internal conflict resolved through character-driven choice" if has_resolution else "Resolution path not yet defined — leave room for organic development"),
            detail=f"Resolution markers: {resolution_hits[:4]}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Story has a psychologically satisfying resolution arc",
            supporting_text=str(resolution_hits[:3]) if resolution_hits else raw[:80],
            source="synopsis_resolution_psychology",
        ))

        # Confidence heuristic
        total = (1 if has_psychology else 0) + (1 if has_behavioral_logic else 0) + len(psych_hits) + (1 if has_conflict else 0) + (1 if has_resolution else 0)
        confidence = round(min(1.0, total / 7), 2) if raw else 0.0

        summary = self._summary(psych_hits, behavior_hits, conflict_hits, resolution_hits)
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=confidence,
            summary=summary,
        )

    def _summary(self, psych: list[str], behavior: list[str], conflicts: list[str], resolutions: list[str]) -> str:
        parts = []
        parts.append(f"Psychological depth {'strong' if len(psych) >= 3 else 'present'}")
        parts.append(f"{len(behavior)} behavioral drives identified")
        if conflicts:
            parts.append(f"Internal tension through {len(conflicts):d} markers")
        if resolutions:
            parts.append("Resolution pathway defined")
        else:
            parts.append("Resolution arc not yet mapped")
        return "; ".join(parts) + "."
