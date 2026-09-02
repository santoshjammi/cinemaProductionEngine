"""Dialogue Compiler — analyzes dialogue authenticity, subtext, character voice."""

from __future__ import annotations

from typing import Any

from movie_os.genesis3.compilers.base import BaseCompiler, CompilerEvidence, EvidenceItem, Finding


DIALOGUE_MARKER = [
    "says", "whispers", "shouts", "argues", "confronts",
    "confides", "admits", "denies", "proclaims", "muttering",
    "speaks", "conversation", "dialogue", "words",
]
SUBTEXT_MARKER = [
    "silence", "pauses", "glance", "hesitates", "unspoken",
    "between the lines", "reads between", "implied", "hinted",
    "suggestion", "loaded", "tension in words",
]
VOICE_MARKER = [
    "voice", "tone", "accent", "slang", "formal", "colloquial",
    "distinctive", "recognizable", "idiomatic", "cadence",
    "rhythm of speech", "speech pattern", "way of speaking",
]


class DialogueCompiler(BaseCompiler):
    name = "Dialogue"
    dimension = "Dialogue Quality"

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        findings: list[Finding] = []
        evidence_items: list[EvidenceItem] = []
        raw = (synopsis or "").strip().lower()

        # --- Character voice distinctness ---
        voice_hits = [v for v in VOICE_MARKER if v in raw]
        has_voice = len(voice_hits) >= 1
        findings.append(Finding(
            category="character_voice",
            status="pass" if has_voice else "warning",
            statement=("Character voice distinguishable from description" if has_voice else "Voice direction not yet defined — critical for distinct character"),
            detail=f"Voice/style markers: {voice_hits[:4]}",
            references=voice_hits,
        ))

        evidence_items.append(EvidenceItem(
            claim="Each character can carry a distinguishable speech pattern",
            supporting_text=str(voice_hits[:3]) if voice_hits else raw[:60],
            source="synopsis_voice_design_cues",
        ))

        # --- Subtext presence ---
        subtext_hits = [s for s in SUBTEXT_MARKER if s in raw]
        has_subtext = len(subtext_hits) >= 2
        findings.append(Finding(
            category="subtext",
            status="pass" if has_subtext else ("warning" if subtext_hits else "fail"),
            statement="Subtext rich and layered" if has_subtext else ("some implicit layers detected" if subtext_hits else "Text is surface-level only — dialogue needs more beneath-the-surface"),
            detail=f"Subtext markers: {subtext_hits[:5]}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Dialogue carries dual meaning (what's said vs what's meant)",
            supporting_text=str(subtext_hits[:3]) if subtext_hits else "no subtext markers found",
            source="synopsis_subtext_analysis",
        ))

        # --- Dialogue advances plot ---
        dialogue_verbs = [d for d in DIALOGUE_MARKER if d in raw]
        action_words = ["decides", "acts", "changes", "moves", "leaves", "returns", "arrives"]
        action_hits = [a for a in action_words if a in raw and len(a) > 4]
        has_plot_advancement = len(dialogue_verbs) >= 2 or (len(action_hits) >= 2)
        findings.append(Finding(
            category="dialogue_advances_plot",
            status="pass" if has_plot_advancement else "warning",
            statement=("Dialogue drives story forward" if has_plot_advancement else "Character actions present but dialogue's narrative function unclear"),
            detail=f"Talk/interaction markers: {dialogue_verbs[:4]}; action verbs: {action_hits}",
            references=dialogue_verbs,
        ))

        evidence_items.append(EvidenceItem(
            claim="Conversation is purposeful and moves the story",
            supporting_text=str(dialogue_verbs[:3]) if dialogue_verbs else str(action_hits[:2]),
            source="synopsis_dialogue_function_analysis",
        ))

        # --- Authenticity check ---
        # --- Authenticity check ---
        emotion_words = ["cry", "laugh", "scream", "whisper", "mutter", "stammer"]
        auth_hits = [e for e in emotion_words if e in raw]
        auth_status = "pass" if len(auth_hits) >= 1 else ("warning" if dialogue_verbs else "fail")
        auth_statement = ("Dialogue authenticity has behavioral grounding"
                          if auth_hits
                          else "Physical vocal cues sparse — rely on writing to suggest sound")
        findings.append(Finding(
            category="dialogue_authenticity",
            status=auth_status,
            statement=auth_statement,
            detail=f"Behavioral speech markers: {auth_hits[:4]}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Dialogue can be performed with behavioral truth",
            supporting_text=str(auth_hits[:2]) if auth_hits else "no vocal performance cues found",
            source="synopsis_authenticity_signals",
        ))

        # Confidence heuristic
        total = (1 if has_voice else 0) + (1 if has_subtext else 0) + (1 if has_plot_advancement else 0) + len(auth_hits) + len(dialogue_verbs)
        confidence = round(min(1.0, total / 7), 2) if raw else 0.0

        summary = self._summary(voice_hits, subtext_hits, dialogue_verbs, auth_hits)
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=confidence if raw else 0.0,
            summary=summary,
        )

    def _summary(self, voice: list[str], subtext: list[str], dialogue: list[str], auth: list[str]) -> str:
        parts = []
        parts.append(f"{len(voice)} voice direction cues")
        parts.append("Subtext " + ("layered" if subtext else "minimal in text"))
        parts.append(f"{len(dialogue)} dialogue action verbs")
        if auth:
            parts.append(f"{len(auth):d} vocal performance markers found")
        return "; ".join(parts) + "."
