"""Tests for P0-06 shot-level execution metadata (PROMETHEUS handoff)."""
from __future__ import annotations

import json

from movie_os.genesis2.shot_execution import (
    enrich_shot_execution_metadata,
    validate_execution_metadata,
)


def _shot(purpose="SPEAKER_COVERAGE", audible="MARK", visible=True, mouth="CLEAR", lines=None, primary="MARK"):
    return {
        "shot_id": "SC01-SH01",
        "scene_id": 1,
        "purpose": purpose,
        "visual_subject": {"primary": primary, "secondary": []},
        "dialogue_mapping": {"active_dialogue_line_ids": lines or []},
        "audio_context": {"audible_speaker": audible},
        "speaker_visibility": {"visible": visible, "mouth_readability": mouth, "dialogue_line_ids": lines or []},
        "listener_visibility": {"character_id": "", "visible": False},
    }


def _line(speaker="MARK", presentation="EXTERNAL"):
    return {"speaker": speaker, "presentation_mode": presentation}


def test_external_visible_speaker_requires_lipsync():
    shots = [_shot(lines=["1:D001"])]
    enriched = enrich_shot_execution_metadata(shots, {"1:D001": _line()})
    em = enriched[0]["execution_metadata"]
    assert em["speech_mode"] == "EXTERNAL"
    assert em["active_visible_speaker"] == "MARK"
    assert em["lipsync_intent"] == "REQUIRED"


def test_internal_voice_prohibits_lipsync():
    shots = [_shot(audible="MARK_INNER", lines=["1:D001"])]
    enriched = enrich_shot_execution_metadata(shots, {"1:D001": _line(presentation="INTERNAL")})
    em = enriched[0]["execution_metadata"]
    assert em["speech_mode"] == "INTERNAL"
    assert em["lipsync_intent"] == "PROHIBITED"


def test_listener_reaction_no_lipsync():
    shots = [_shot(purpose="LISTENER_REACTION", audible="MARK", visible=False, mouth="NOT_VISIBLE", lines=["1:D001"])]
    enriched = enrich_shot_execution_metadata(shots, {"1:D001": _line()})
    em = enriched[0]["execution_metadata"]
    assert em["active_visible_speaker"] is None
    assert em["lipsync_intent"] == "NOT_REQUIRED"


def test_silent_shot_not_applicable():
    shots = [_shot(purpose="ESTABLISHING", audible="", visible=False, mouth="NONE", lines=[])]
    enriched = enrich_shot_execution_metadata(shots, {})
    em = enriched[0]["execution_metadata"]
    assert em["speech_mode"] == "NONE"
    assert em["lipsync_intent"] == "NOT_APPLICABLE"


def test_voiceover_not_required():
    shots = [_shot(audible="MARK", lines=["1:D001"])]
    enriched = enrich_shot_execution_metadata(shots, {"1:D001": _line(presentation="VOICEOVER")})
    em = enriched[0]["execution_metadata"]
    assert em["speech_mode"] == "VOICEOVER"
    assert em["lipsync_intent"] == "NOT_REQUIRED"


def test_acceptance_all_metadata_present():
    shots = [
        _shot(purpose="ESTABLISHING", audible="", visible=False, mouth="NONE", lines=[]),
        _shot(lines=["1:D001"]),
        _shot(purpose="LISTENER_REACTION", audible="MARK", visible=False, mouth="NOT_VISIBLE", lines=["1:D002"]),
    ]
    dlg = {"1:D001": _line(), "1:D002": _line()}
    enriched = enrich_shot_execution_metadata(shots, dlg)
    report = validate_execution_metadata(enriched)
    assert report["passed"] is True
    assert report["execution_metadata_coverage"] == 100.0
    assert report["invalid_character_refs"] == 0
    assert report["ambiguous_visible_speakers"] == 0
    assert report["internal_voice_fake_lipsync"] == 0
    assert report["listener_reaction_wrong_lipsync"] == 0


def test_unknown_speaker_resolves_to_none():
    """An unknown speaker label resolves to None (dropped), never an invalid ref."""
    shots = [_shot(primary="ZORP", audible="", lines=["1:D001"])]
    enriched = enrich_shot_execution_metadata(shots, {"1:D001": _line()})
    em = enriched[0]["execution_metadata"]
    # ZORP is not a canonical character -> not in visible_characters, no invalid ref.
    assert em["visible_characters"] == []
    report = validate_execution_metadata(enriched)
    assert report["invalid_character_refs"] == 0
