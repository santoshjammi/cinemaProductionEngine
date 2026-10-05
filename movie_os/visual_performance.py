"""Visual Performance Realization — map GENESIS-authored performance to FLUX prompt language.

PROMETHEUS-STATIC-PERFORMANCE-STANDARD-001.

GENESIS already authors performance intent (emotion, delivery_intent, subtext,
shot purpose). This module deterministically translates that into specific,
restrained visual language for FLUX image prompts — facial expression, gaze,
body language, and emotional subtext — WITHOUT reinterpreting the psychology.

Design principles (from the standard):
  - Preserve character identity FIRST (ethnicity, age, hair, wardrobe).
  - Then add facial expression, gaze, posture, emotional subtext, composition.
  - Default intensity is SUBTLE (adult psychological realism, restrained).
  - Avoid generic tokens ("emotional", "sad", "dramatic") — use specific visual language.
  - Listener reactions derive from what was heard, never copy the speaker.
  - Two-shots allow different emotions per character with relational body language.

This is deterministic (no LLM) so it is fast, cheap, and reproducible.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("movie_os.visual_performance")

# --------------------------------------------------------------------------- #
# Emotion → visual language (facial cues, gaze, body language)                #
# --------------------------------------------------------------------------- #

# Each emotion maps to specific, EVIDENT visual language (user directive
# 2026-09-08: convey emotion through the still image, not subtle). The values
# are concrete and avoid generic "sad"/"emotional" tokens.
_EMOTION_VISUALS: dict[str, dict[str, str]] = {
    "anxious": {
        "facial": "brow deeply furrowed, lips pressed tight, visible tension around the eyes, jaw clenched",
        "gaze": "avoidant, eyes darting down and away, unable to hold contact",
        "body": "shoulders hunched inward, weight shifting restlessly, hands clasped white-knuckled",
    },
    "guarded": {
        "facial": "mouth set in a hard line, jaw tight, eyes narrowed and watchful",
        "gaze": "guarded, brief hard contact then dropping away",
        "body": "arms folded defensively, torso turned away, chin tucked",
    },
    "defensive": {
        "facial": "jaw clenched hard, brow lowered, mouth a firm tight line",
        "gaze": "direct and hard, chin raised, challenging",
        "body": "shoulders squared, leaning back, arms crossed, rigid",
    },
    "vulnerable": {
        "facial": "guard visibly dropped, brow lifted, mouth slightly parted, eyes soft and open",
        "gaze": "tentative, searching the other's eyes, hopeful",
        "body": "shoulders dropped, hands open and exposed, leaning in",
    },
    "hurt": {
        "facial": "eyes glassy and brimming, brow drawn, mouth pressed to hold back",
        "gaze": "downcast, wounded, avoiding the other",
        "body": "arms wrapped around self, head bowed, shrinking",
    },
    "hurt_with_empathy": {
        "facial": "eyes soft and glistening with concern, brow gently lifted, mouth soft",
        "gaze": "warm, steady, full of care on the other",
        "body": "leaning in, hand reaching toward but not touching",
    },
    "concerned": {
        "facial": "brow knit deeply, eyes wide and searching, mouth set with worry",
        "gaze": "steady, intense, fixed on the other",
        "body": "leaning forward, open, alert",
    },
    "restrained_frustration": {
        "facial": "jaw tight, brow low, lips pressed into a thin line, nostrils flared slightly",
        "gaze": "direct, controlled, holding back",
        "body": "still but tense, hands clasped, shoulders rigid",
    },
    "softening_attention": {
        "facial": "brow relaxed, eyes warm and tender, mouth soft",
        "gaze": "gentle, focused, full of care",
        "body": "open posture, leaning in, receptive",
    },
    "calm": {
        "facial": "relaxed brow, soft steady eyes, gentle mouth",
        "gaze": "warm, present, grounded",
        "body": "relaxed, open, centered",
    },
    "patient": {
        "facial": "soft brow, attentive warm eyes, gentle encouraging mouth",
        "gaze": "steady, encouraging, present",
        "body": "still, open, leaning slightly in",
    },
    "tense": {
        "facial": "brow tight, jaw clenched, eyes watchful and narrowed",
        "gaze": "focused, hard, unblinking",
        "body": "rigid posture, shoulders up, hands still and clenched",
    },
    "sad": {
        "facial": "brow drawn, eyes downcast and heavy, mouth soft and downturned",
        "gaze": "downward, unfocused, lost",
        "body": "slumped shoulders, head lowered, deflated",
    },
    "grief": {
        "facial": "eyes unfocused and red-rimmed, brow heavy, mouth slack and trembling",
        "gaze": "distant, hollow, unfocused",
        "body": "motionless, shoulders collapsed, broken posture",
    },
    "relieved": {
        "facial": "brow lifted, eyes soft and bright, mouth relaxing into a faint exhale",
        "gaze": "warm, meeting the other, grateful",
        "body": "shoulders dropping, posture loosening, exhaling",
    },
    "hopeful": {
        "facial": "brow lifted, eyes bright and searching, mouth soft with a hint of a smile",
        "gaze": "warm, hopeful, seeking the other",
        "body": "open, leaning forward, reaching",
    },
    "neutral": {
        "facial": "relaxed, composed, unforced",
        "gaze": "natural, present",
        "body": "relaxed, natural posture",
    },
}

# Emotion aliases → canonical key (normalize GENESIS's varied labels).
_EMOTION_ALIASES: dict[str, str] = {
    "anxious": "anxious",
    "anxiety": "anxious",
    "nervous": "anxious",
    "guarded": "guarded",
    "defensive": "defensive",
    "vulnerable": "vulnerable",
    "hurt": "hurt",
    "hurt with empathy": "hurt_with_empathy",
    "concerned": "concerned",
    "worry": "concerned",
    "worried": "concerned",
    "frustrated": "restrained_frustration",
    "frustration": "restrained_frustration",
    "calm": "calm",
    "patient": "patient",
    "tense": "tense",
    "tension": "tense",
    "sad": "sad",
    "sadness": "sad",
    "grief": "grief",
    "grieving": "grief",
    "relieved": "relieved",
    "relief": "relieved",
    "hopeful": "hopeful",
    "hope": "hopeful",
    "neutral": "neutral",
    "": "neutral",
}

# Intensity → how strongly the visual language is stated in the prompt.
# User directive (2026-09-08): emotions must be EVIDENT, not subtle — the
# whole point is to convey emotion through the still image. So the default
# floor is MODERATE (clearly readable), and strong emotions go STRONG.
_INTENSITY_ADVERB: dict[str, str] = {
    "SUBTLE": "subtle, restrained",
    "MODERATE": "clearly readable, evident",
    "STRONG": "pronounced, unmistakable",
}


def _canonical_emotion(emotion: str) -> str:
    """Normalize an emotion label to a canonical key."""
    if not emotion:
        return "neutral"
    key = emotion.strip().lower()
    return _EMOTION_ALIASES.get(key, key)


def _intensity_of(emotion: str, shot_purpose: str) -> str:
    """Intensity per emotion + shot purpose.

    User directive (2026-09-08): emotions must be EVIDENT, not subtle. So the
    floor is MODERATE for everything, and strong emotions / reaction shots go
    STRONG so the beat reads clearly in a still image.
    """
    e = _canonical_emotion(emotion)
    if e in ("grief", "hurt", "vulnerable", "relieved", "hopeful", "defensive", "tense"):
        return "STRONG"
    if shot_purpose in ("LISTENER_REACTION", "EMOTIONAL_HOLD", "TWO_SHOT"):
        return "STRONG"
    return "MODERATE"


# --------------------------------------------------------------------------- #
# Shot-purpose focus                                                          #
# --------------------------------------------------------------------------- #

def _shot_focus(shot_purpose: str, speaker: str, listener: str) -> str:
    """Return the visual focus directive for a shot purpose."""
    p = (shot_purpose or "").upper()
    if p == "SPEAKER_COVERAGE":
        return f"focus on {speaker or 'the speaker'}, mid-close framing"
    if p == "LISTENER_REACTION":
        return f"focus on {listener or 'the listener'}, reaction close-up"
    if p == "TWO_SHOT":
        return "two-shot, both characters in frame, relational"
    if p == "ESTABLISHING":
        return "wide establishing, both characters small in frame"
    if p == "INSERT":
        return "extreme close-up insert, shallow depth of field"
    if p == "EMOTIONAL_HOLD":
        return f"emotional hold on {speaker or 'the character'}, lingering"
    return "medium framing"


# --------------------------------------------------------------------------- #
# Listener reaction derivation                                                #
# --------------------------------------------------------------------------- #

def _listener_reaction(preceding_line: dict[str, Any] | None) -> dict[str, str]:
    """Derive a listener's reaction from the preceding dialogue line.

    The reaction is specific to what was heard — never a copy of the speaker's
    expression.
    """
    if not preceding_line:
        return _EMOTION_VISUALS["neutral"]
    speaker_emotion = _canonical_emotion(str(preceding_line.get("emotion", "")))
    text = str(preceding_line.get("text", "")).lower()

    # Painful admission / vulnerability → hurt with empathy
    if speaker_emotion in ("vulnerable", "hurt", "grief") or any(
        w in text for w in ["afraid", "scared", "can't", "cannot", "too late", "worse", "hurt",
                            "not sure", "don't know", "talk about", "say anything", "nothing to say"]
    ):
        return _EMOTION_VISUALS["hurt_with_empathy"]
    # Defensiveness → restrained frustration
    if speaker_emotion in ("defensive", "guarded") or any(
        w in text for w in ["don't want", "won't", "nothing", "leave", "stop"]
    ):
        return _EMOTION_VISUALS["restrained_frustration"]
    # Vulnerability / softening → softening attention
    if speaker_emotion in ("calm", "patient", "hopeful") or any(
        w in text for w in ["try", "here", "okay", "we can", "be with"]
    ):
        return _EMOTION_VISUALS["softening_attention"]
    # Default: attentive concern
    return _EMOTION_VISUALS["concerned"]


# --------------------------------------------------------------------------- #
# Two-shot per-character emotions                                            #
# --------------------------------------------------------------------------- #

def _two_shot_emotions(active_lines: list[dict[str, Any]]) -> dict[str, str]:
    """For a two-shot, assign each character a distinct emotion from the active lines.

    Returns {character_key: emotion_key}. Defaults to a relational distance
    (Mark withdrawn, Sarah searching) when no line data is available.
    """
    result: dict[str, str] = {}
    for line in active_lines:
        speaker = str(line.get("speaker", "")).upper().replace("_INNER", "")
        emotion = _canonical_emotion(str(line.get("emotion", "")))
        if speaker and speaker not in result:
            result[speaker] = emotion
    # Fill missing with relational defaults
    if "MARK" not in result:
        result["MARK"] = "guarded"
    if "SARAH" not in result:
        result["SARAH"] = "concerned"
    return result


# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #

def build_visual_performance(
    shot: dict[str, Any],
    dialogue_lines: list[dict[str, Any]],
    character_anchors: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build the visual-performance block for a shot.

    Args:
        shot: A frozen-PKP shot dict (has purpose, performance_context,
            dialogue_mapping, emotional_intent, composition).
        dialogue_lines: The brief's dialogue lines for the shot's scene
            (used to resolve the active line + preceding line for reactions).
        character_anchors: {character_key: visual_anchor} for identity
            preservation (optional; falls back to a generic anchor).

    Returns a dict with the visual-performance contract fields:
        primary_emotion, intensity, facial_cues, gaze, body_language,
        emotional_subtext, shot_focus, character_identity.
    """
    purpose = str(shot.get("purpose", "")).upper()
    pc = shot.get("performance_context", {}) or {}
    dm = shot.get("dialogue_mapping", {}) or {}
    active_ids = dm.get("active_dialogue_line_ids", []) or []

    # Resolve the active line(s) for this shot.
    active_lines = [l for l in dialogue_lines if l.get("line_id") in active_ids]
    if not active_lines and dialogue_lines:
        # Fallback: use the first line of the scene.
        active_lines = [dialogue_lines[0]]

    # Speaker / listener from performance_context or the active line.
    speaker = pc.get("speaker") or (active_lines[0].get("speaker") if active_lines else "")
    speaker_key = str(speaker).upper().replace("_INNER", "")
    listener = pc.get("reacting_character") or (
        "SARAH" if speaker_key == "MARK" else "MARK"
    )

    # Primary emotion: from performance_context, else shot emotional_intent,
    # else the active line's emotion.
    raw_emotion = (
        pc.get("emotional_state_primary")
        or shot.get("emotional_intent")
        or (active_lines[0].get("emotion") if active_lines else "")
    )
    primary_emotion = _canonical_emotion(str(raw_emotion))
    intensity = _intensity_of(primary_emotion, purpose)

    # Build the visual block per shot purpose.
    if purpose == "LISTENER_REACTION":
        # Preceding line = the line the listener just heard (the active line).
        visuals = _listener_reaction(active_lines[0] if active_lines else None)
        primary_emotion = "concerned"  # reaction is contextual, not the speaker's
        subtext = f"reacting to: {active_lines[0].get('text','') if active_lines else ''}"
    elif purpose == "TWO_SHOT":
        emotions = _two_shot_emotions(active_lines)
        visuals = {
            "facial": _EMOTION_VISUALS.get(emotions.get("MARK", "guarded"), _EMOTION_VISUALS["guarded"])["facial"]
            + "; "
            + _EMOTION_VISUALS.get(emotions.get("SARAH", "concerned"), _EMOTION_VISUALS["concerned"])["facial"],
            "gaze": "Mark and Sarah looking at each other, relational",
            "body": "relational body language, distance or connection between them",
        }
        subtext = f"Mark: {emotions.get('MARK','guarded')}, Sarah: {emotions.get('SARAH','concerned')}"
    else:
        # Speaker coverage / establishing / insert / emotional hold.
        visuals = _EMOTION_VISUALS.get(primary_emotion, _EMOTION_VISUALS["neutral"])
        subtext = str(pc.get("subtext") or shot.get("emotional_intent") or "")

    # Character identity anchor (preserve first).
    anchors = character_anchors or {}
    # The on-screen character differs by shot purpose: listener reactions focus
    # on the reacting_character, speaker shots on the speaker.
    identity_owner = listener if purpose == "LISTENER_REACTION" else speaker_key
    identity = anchors.get(identity_owner.lower()) or anchors.get("mark") or (
        "a man in his late 30s with short dark hair" if identity_owner == "MARK"
        else "a woman in her early 30s with long dark hair"
    )

    return {
        "primary_emotion": primary_emotion,
        "intensity": intensity,
        "facial_cues": visuals["facial"],
        "gaze": visuals["gaze"],
        "body_language": visuals["body"],
        "emotional_subtext": subtext,
        "shot_focus": _shot_focus(purpose, speaker_key, listener),
        "character_identity": identity,
        "speaker": speaker_key,
        "listener": listener,
        "shot_purpose": purpose,
    }


def render_visual_prompt(visual: dict[str, Any]) -> str:
    """Render a visual-performance block into FLUX prompt language.

    Preserves identity first, then adds facial/gaze/body/subtext/composition.
    Uses specific visual language (no generic "emotional"/"sad"/"dramatic").
    """
    intensity = _INTENSITY_ADVERB.get(visual.get("intensity", "SUBTLE"), "subtle, restrained")
    parts = [
        visual.get("character_identity", ""),
        visual.get("shot_focus", ""),
        f"facial expression: {visual.get('facial_cues', '')}",
        f"gaze: {visual.get('gaze', '')}",
        f"body language: {visual.get('body_language', '')}",
        f"emotional subtext: {visual.get('emotional_subtext', '')}",
        f"intensity: {intensity}",
        "adult psychological realism, restrained natural performance",
    ]
    return ", ".join(p for p in parts if p)
