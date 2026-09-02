"""Emotion Compiler — analyzes emotional journey, payoff moments, catharsis."""

from __future__ import annotations

from typing import Any

from movie_os.genesis3.compilers.base import BaseCompiler, CompilerEvidence, EvidenceItem, Finding


EMOTION_MARKER = [
    "joy", "sadness", "fear", "anger", "love", "hope", "despair",
    "triumph", "grief", "nostalgia", "longing", "relief", "sorrow",
    "elation", "melancholy", "wonder", "awe", "tenderness",
]
PAYOFF_MARKER = [
    "realizes", "understands", "accepts", "forgives", "embraces",
    "reconciles", "understanding dawns", "moment of clarity",
    "breakthrough", "epiphany", "awakening", "turnaround",
]
CATHARSIS_MARKER = [
    "tears", "cry", "weep", "release", "let go", "surrender",
    "breakdown", "breakthrough", "emotional", "powerful", "moving",
    "touching", "heartfelt", "poignant",
]


class EmotionCompiler(BaseCompiler):
    name = "Emotion"
    dimension = "Emotional Resonance"

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        findings: list[Finding] = []
        evidence_items: list[EvidenceItem] = []
        raw = (synopsis or "").strip().lower()

        # --- Emotional range detection ---
        emotion_hits = [e for e in EMOTION_MARKER if e in raw]
        has_range = len(emotion_hits) >= 2
        findings.append(Finding(
            category="emotional_range",
            status="pass" if has_range else ("warning" if emotion_hits else "fail"),
            statement=("Emotional range diverse and compelling" if has_range else ("partial emotional palette" if emotion_hits else "Emotional markers sparse")),
            detail=f"Emotion words found: {emotion_hits}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Story can evoke multiple emotional states",
            supporting_text=str(emotion_hits[:6]),
            source="synopsis_emotional_vocabulary",
        ))

        # --- Payoff moment analysis ---
        payoff_hits = [p for p in PAYOFF_MARKER if p in raw]
        has_payoff = len(payoff_hits) >= 1
        findings.append(Finding(
            category="emotional_payoff",
            status="pass" if has_payoff else "warning",
            statement=("Emotional payoff earned" if has_payoff else "Payoff moment needs setup"),
            detail=f"Climactic realization markers: {payoff_hits}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Story builds toward an emotional resolution point",
            supporting_text=str(payoff_hits[:2]) if payoff_hits else raw[:80],
            source="synopsis_payoff_building_blocks",
        ))

        # --- Catharsis potential ---
        catharsis_hits = [c for c in CATHARSIS_MARKER if c in raw]
        has_catharsis = len(catharsis_hits) >= 2
        findings.append(Finding(
            category="catharsis",
            status="pass" if has_catharsis else ("warning" if catharsis_hits else "info"),
            statement=("Climax satisfies premise with emotional release" if has_catharsis else ""),
            detail=f"Cathartic indicators: {catharsis_hits[:4]}",
            references=[],
        ))

        # Add a finding for empty but info-level
        if not catharsis_hits:
            findings[-1] = Finding(
                category="catharsis",
                status="info",
                statement="Climax payoff implied but needs explicit emotional release markers",
                detail="No direct catharsis language detected — story relies on subtextual resolution",
                references=[],
            )

        evidence_items.append(EvidenceItem(
            claim=f"Cathartic potential {'strong' if has_catharsis else 'available through performance and direction'}",
            supporting_text=str(catharsis_hits[:3]),
            source="synopsis_emotional_release_points",
        ))

        # --- Ending emotional intent ---
        ending_words = ["ending", "finally", "in the end", "ultimately", "concludes", "ends with"]
        ending_hits = [w for w in ending_words if w in raw]
        findings.append(Finding(
            category="ending_emotion",
            status="pass" if ending_hits and has_payoff else "warning",
            statement="Ending produces intended emotion" if (ending_hits and has_payoff) else "Ending emotional impact unclear without payoff markers",
            detail=f"Ending signals found: {ending_hits}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Story concludes at an emotionally determined point",
            supporting_text=str(ending_hits[:2]),
            source="synopsis_resolution_cues",
        ))

        # Confidence heuristic
        total = (1 if has_range else 0) + (1 if has_payoff else 0) + (1 if has_catharsis else 0) + len(payoff_hits) * 2
        confidence = round(min(1.0, total / 6), 2) if raw else 0.0

        summary = self._summary(emotion_hits, payoff_hits, catharsis_hits)
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=confidence,
            summary=summary,
        )

    def _summary(self, emotions: list[str], payoffs: list[str], catharsis: list[str]) -> str:
        parts = []
        parts.append(f"{len(emotions)} emotional states identified")
        parts.append("Payoff " + ("present" if payoffs else "needs setup"))
        if catharsis:
            parts.append(f"{len(catharsis)} release-point markers found")
        else:
            parts.append("Catharsis implicit — benefit of the doubt to performer")
        return "; ".join(parts) + "."
