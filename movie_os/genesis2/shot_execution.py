"""P0-06: Shot-level execution metadata for PROMETHEUS.

Adds the per-shot execution fields PROMETHEUS needs to determine who is
speaking, who is visible, and whether lip-sync is required:

    visible_characters      list[character_id]
    active_visible_speaker  character_id | None
    mouth_readability       CLEAR | PARTIAL | NOT_VISIBLE | NOT_APPLICABLE
    dialogue_line_ids       list[str]
    speech_mode             EXTERNAL | INTERNAL | VOICEOVER | NONE
    lipsync_intent          REQUIRED | NOT_REQUIRED | PROHIBITED | NOT_APPLICABLE

Deterministic rules (P0-06 §2).  This phase only expresses execution intent;
it does not optimize lip-sync quality.
"""
from __future__ import annotations

from typing import Any

# Canonical character ids (from the frozen PKP voice registry).
CHARACTER_IDS = {"MARK", "SARAH"}

# presentation_mode values that map to speech modes.
_EXTERNAL = {"EXTERNAL", "SPOKEN", "DIALOGUE"}
_INTERNAL = {"INTERNAL", "INNER", "INNER_VOICE", "INTERNAL_MONOLOGUE"}
_VOICEOVER = {"VOICEOVER", "VOICE_OVER", "NARRATION", "NARRATOR"}


def _norm(s: Any) -> str:
    return str(s or "").strip().upper()


def _resolve_speaker_id(raw: Any) -> str | None:
    """Map a raw speaker label to a canonical character id, or None."""
    s = _norm(raw)
    if not s:
        return None
    # Strip inner-voice suffix (e.g. "MARK_INNER" -> "MARK").
    for suffix in ("_INNER", "_INNER_VOICE", "_VOICEOVER", "_VOICE_OVER"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
    if s in CHARACTER_IDS:
        return s
    # Case-insensitive match.
    for cid in CHARACTER_IDS:
        if s == cid:
            return cid
    return None


def _speech_mode_from_presentation(presentation: Any, speaker: str | None) -> str:
    p = _norm(presentation)
    if p in _INTERNAL:
        return "INTERNAL"
    if p in _VOICEOVER:
        return "VOICEOVER"
    if p in _EXTERNAL:
        return "EXTERNAL"
    # Fall back on the speaker label.
    s = _norm(speaker)
    if s.endswith("_INNER") or "INNER" in s:
        return "INTERNAL"
    if "VOICEOVER" in s or "NARRAT" in s:
        return "VOICEOVER"
    return "EXTERNAL"


def _lipsync_intent(speech_mode: str, mouth_readability: str, active_visible_speaker: str | None) -> str:
    """P0-06 §2 deterministic rules."""
    if speech_mode == "NONE":
        return "NOT_APPLICABLE"
    if speech_mode == "INTERNAL":
        return "PROHIBITED"
    if speech_mode == "VOICEOVER":
        return "NOT_REQUIRED"
    # EXTERNAL
    if active_visible_speaker is None:
        # Listener reaction / no visible speaker -> no lip-sync.
        return "NOT_REQUIRED"
    if mouth_readability == "CLEAR":
        return "REQUIRED"
    if mouth_readability in ("PARTIAL", "NOT_VISIBLE"):
        return "NOT_REQUIRED"
    return "NOT_REQUIRED"


def enrich_shot_execution_metadata(
    shots: list[dict[str, Any]],
    dialogue_lines: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Deterministically add P0-06 execution metadata to every shot.

    `dialogue_lines` maps line_id -> {speaker, presentation_mode, ...}.
    Mutates and returns the same shot list (in place).
    """
    for shot in shots:
        # --- dialogue_line_ids: union of mapped + speaker_visibility lines ---
        mapped = shot.get("dialogue_mapping", {}).get("active_dialogue_line_ids", []) or []
        vis_lines = shot.get("speaker_visibility", {}).get("dialogue_line_ids", []) or []
        line_ids: list[str] = []
        for lid in list(mapped) + list(vis_lines):
            if lid and lid not in line_ids:
                line_ids.append(str(lid))

        # --- audible_speaker (already present; normalize) ---
        audible = shot.get("audio_context", {}).get("audible_speaker", "") or ""
        audible_id = _resolve_speaker_id(audible)

        # --- visible characters ---
        visible: list[str] = []
        vis = shot.get("speaker_visibility", {})
        if vis.get("visible"):
            sid = _resolve_speaker_id(vis.get("character_id") or shot.get("visual_subject", {}).get("primary"))
            if sid and sid not in visible:
                visible.append(sid)
        listener = shot.get("listener_visibility", {})
        if listener.get("visible"):
            lid2 = _resolve_speaker_id(listener.get("character_id"))
            if lid2 and lid2 not in visible:
                visible.append(lid2)
        # If nothing visible but a speaker is audible and the shot is a
        # speaker-coverage/two-shot, the speaker is visible.
        if not visible and audible_id and shot.get("purpose") in ("SPEAKER_COVERAGE", "TWO_SHOT"):
            visible.append(audible_id)

        # --- active_visible_speaker ---
        active_visible_speaker: str | None = None
        if audible_id and audible_id in visible:
            active_visible_speaker = audible_id
        elif len(visible) == 1:
            active_visible_speaker = visible[0]

        # --- speech_mode ---
        # Determine from the first mapped dialogue line's presentation_mode.
        speech_mode = "NONE"
        for lid in line_ids:
            line = dialogue_lines.get(lid, {})
            if line:
                presentation = line.get("presentation_mode") or line.get("delivery_mode")
                speaker = line.get("speaker") or audible
                speech_mode = _speech_mode_from_presentation(presentation, speaker)
                break
        if speech_mode == "NONE" and audible_id:
            # Audible but no mapped line -> external speech.
            speech_mode = "EXTERNAL"

        # --- mouth_readability ---
        mouth = _norm(vis.get("mouth_readability"))
        if mouth in ("CLEAR", "PARTIAL", "NOT_VISIBLE"):
            mouth_readability = mouth
        elif speech_mode == "NONE":
            mouth_readability = "NOT_APPLICABLE"
        elif active_visible_speaker is None:
            mouth_readability = "NOT_VISIBLE"
        else:
            mouth_readability = "CLEAR"

        # --- lipsync_intent ---
        lipsync = _lipsync_intent(speech_mode, mouth_readability, active_visible_speaker)

        # Write back.
        shot["execution_metadata"] = {
            "audible_speaker": audible_id,
            "visible_characters": visible,
            "active_visible_speaker": active_visible_speaker,
            "mouth_readability": mouth_readability,
            "dialogue_line_ids": line_ids,
            "speech_mode": speech_mode,
            "lipsync_intent": lipsync,
        }
    return shots


def validate_execution_metadata(shots: list[dict[str, Any]]) -> dict[str, Any]:
    """P0-06 acceptance checks."""
    total = len(shots)
    with_meta = sum(1 for s in shots if s.get("execution_metadata"))
    invalid_refs = 0
    ambiguous = 0
    internal_fake_lipsync = 0
    listener_wrong_lipsync = 0
    lipsync_required = 0
    lipsync_not_required = 0
    lipsync_prohibited = 0
    lipsync_na = 0

    for s in shots:
        em = s.get("execution_metadata", {})
        if not em:
            continue
        # Invalid character refs.
        for cid in em.get("visible_characters", []):
            if cid not in CHARACTER_IDS:
                invalid_refs += 1
        asp = em.get("active_visible_speaker")
        if asp is not None and asp not in CHARACTER_IDS:
            invalid_refs += 1
        # Ambiguous visible speakers: >1 visible and no active speaker.
        if len(em.get("visible_characters", [])) > 1 and asp is None and em.get("speech_mode") == "EXTERNAL":
            ambiguous += 1
        # Internal voice must not require lip-sync.
        if em.get("speech_mode") == "INTERNAL" and em.get("lipsync_intent") == "REQUIRED":
            internal_fake_lipsync += 1
        # Listener reaction (no active speaker) must not require lip-sync.
        if asp is None and em.get("lipsync_intent") == "REQUIRED":
            listener_wrong_lipsync += 1
        # Counts.
        li = em.get("lipsync_intent")
        if li == "REQUIRED":
            lipsync_required += 1
        elif li == "NOT_REQUIRED":
            lipsync_not_required += 1
        elif li == "PROHIBITED":
            lipsync_prohibited += 1
        elif li == "NOT_APPLICABLE":
            lipsync_na += 1

    passed = (
        with_meta == total
        and invalid_refs == 0
        and ambiguous == 0
        and internal_fake_lipsync == 0
        and listener_wrong_lipsync == 0
    )
    return {
        "passed": passed,
        "total_shots": total,
        "with_metadata": with_meta,
        "execution_metadata_coverage": round(100.0 * with_meta / total, 1) if total else 100.0,
        "invalid_character_refs": invalid_refs,
        "ambiguous_visible_speakers": ambiguous,
        "internal_voice_fake_lipsync": internal_fake_lipsync,
        "listener_reaction_wrong_lipsync": listener_wrong_lipsync,
        "lipsync_required_shots": lipsync_required,
        "lipsync_not_required_shots": lipsync_not_required,
        "lipsync_prohibited_shots": lipsync_prohibited,
        "lipsync_not_applicable_shots": lipsync_na,
    }
