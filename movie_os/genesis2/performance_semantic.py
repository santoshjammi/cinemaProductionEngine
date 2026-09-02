"""P0-04: Semantic performance evaluation.

Deterministic orchestration over semantic signals.  The semantic evaluator
(LLM via DeepSeek V4 Flash / Ollama Cloud per policy) produces structured
verdicts; the code enforces warnings/blockers.  For regression we use captured
fixtures so tests are deterministic and not live-model dependent.

Checks:
  - line-level: acting direction coherent, subtext actionable, emotion plausible
  - scene-level: progression believable, emotional transitions causal
  - cross-scene: SCENE-N end state vs SCENE-N+1 enter state continuity
  - professional register: mature working-professional realism
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("movie_os.genesis2.performance.semantic")

# Series/niche rule: working professionals.  These patterns are WARNING/FAIL.
PROFESSIONAL_ADULT_ANTIPATTERNS = [
    "cartoonish", "cartoon", "teenage affect", "soap-opera", "soap opera",
    "exaggerated drama", "motivational-speaker", "announcer", "assistant-polite",
    "virtual assistant", "exposition voice", "constant shouting", "constant crying",
    "overly theatrical", "melodramatic", "over-articulated",
]
PROFESSIONAL_ADULT_PREFERRED = [
    "restraint", "hesitation", "clipped", "controlled frustration",
    "quiet defensiveness", "natural pauses", "avoidance", "professional cadence",
    "emotion below the words", "restrained",
]

# Emotional continuity: an unexplained leap between incompatible states is a
# discontinuity.  Pairs that may transition given story events.
_INCOMPATIBLE_STATES = {
    ("guarded", "ecstatic"), ("ecstatic", "devastated"), ("devastated", "casual"),
    ("guarded", "cheerful"), ("shame", "exuberant"), ("withdrawn", "exuberant"),
    ("withdrawn", "cheerful"), ("defensive", "ecstatic"), ("shut_down", "cheerful"),
    ("guarded", "exuberant"), ("shame", "cheerful"), ("fear", "exuberant"),
    ("sad", "exuberant"), ("guarded", "ecstatic"),
}


def classify_emotion(text: str) -> str:
    """Normalize a raw emotion label to a coarse state token for continuity."""
    low = str(text or "").strip().lower()
    if any(w in low for w in ("guard", "withdr", "shut", "closed", "retreat")):
        return "guarded"
    if any(w in low for w in ("cheer", "happy", "joy", "exuber", "ecstatic", "bright")):
        return "exuberant"
    if any(w in low for w in ("devast", "despair", "grief", "destroyed")):
        return "devastated"
    if any(w in low for w in ("casual", "flat", "indifferent", "neutral", "detached")):
        return "casual"
    if any(w in low for w in ("shame", "asham", "humiliat")):
        return "shame"
    if any(w in low for w in ("defens", "pressur", "corner", "under attack")):
        return "defensive"
    if any(w in low for w in ("fear", "scared", "terrif", "anxious", "nervous")):
        return "fear"
    if any(w in low for w in ("anger", "angry", "irritat", "frustrat", "cold")):
        return "angry"
    if any(w in low for w in ("sad", "hurt", "pain", "grief", "sorrow")):
        return "sad"
    if any(w in low for w in ("vulnerab", "soft", "warm", "tender", "hopeful")):
        return "vulnerable"
    return "other"


def line_professional_register(evaluation: str) -> dict[str, Any]:
    """Evaluate whether a performance direction suits mature working professionals."""
    low = (evaluation or "").lower()
    flagged = [p for p in PROFESSIONAL_ADULT_ANTIPATTERNS if p in low]
    preferred = [p for p in PROFESSIONAL_ADULT_PREFERRED if p in low]
    verdict = "PASS"
    if flagged:
        verdict = "WARNING" if len(flagged) <= 2 else "FAIL"
    return {
        "antipatterns_found": flagged,
        "preferred_signals": preferred,
        "verdict": verdict,
        "passed": verdict in ("PASS", "WARNING"),
    }


def scene_emotional_continuity(seq: list[str]) -> dict[str, Any]:
    """Track emotional state through a scene; reject unexplained leaps."""
    violations = []
    prev_cat = None
    for i, raw in enumerate(seq):
        cat = classify_emotion(raw)
        if prev_cat and cat and prev_cat != cat:
            if (prev_cat, cat) in _INCOMPATIBLE_STATES or (cat, prev_cat) in _INCOMPATIBLE_STATES:
                violations.append({"index": i, "from": prev_cat, "to": cat})
        prev_cat = cat or prev_cat
    return {"violations": violations, "passed": len(violations) == 0}


def cross_scene_continuity(end_state: str, next_start: str) -> dict[str, Any]:
    """SCENE N end vs SCENE N+1 start must not contradict without justification."""
    e = classify_emotion(end_state)
    s = classify_emotion(next_start)
    contradiction = bool(e and s and ((e, s) in _INCOMPATIBLE_STATES or (s, e) in _INCOMPATIBLE_STATES))
    return {
        "end_state": end_state, "next_start": next_start,
        "contradiction": contradiction,
        "passed": not contradiction,
    }


def subtext_matches_character_motive(subtext: str, character_motive: str) -> dict[str, Any]:
    """Subtext should align with the character's established motivation."""
    if not subtext or not character_motive:
        return {"verdict": "PASS", "note": "insufficient data", "passed": True}
    low_sub = (subtext or "").lower()
    low_mot = (character_motive or "").lower()
    # Naive overlap heuristic — the semantic evaluator refines this.  Used only
    # for fixtures/deterministic regression.
    shares = any(w in low_sub and w in low_mot for w in low_mot.split() if len(w) > 3)
    return {"verdict": "PASS" if shares else "WARNING", "passed": shares, "note": "subtext-motif check"}
