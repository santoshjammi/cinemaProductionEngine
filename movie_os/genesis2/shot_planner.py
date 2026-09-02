"""P0-05: Cinematic shot planning.

Replaces the mechanical one-line-per-shot compiler behavior with a cinematic
shot-planning system.  GENESIS determines shots from dramatic purpose,
speaker/listener dynamics, emotional state, blocking, visual storytelling,
performance intent, and continuity — never from dialogue-line arithmetic.

Core principle:
    A cut is a cinematic decision, not a line separator.
    Dialogue determines what is heard; drama determines what is seen.

No fixed shot count.  Shot count emerges from cinematic need:
    - multiple lines -> one two-shot / coverage shot
    - one line -> multiple shots (e.g. speaker then listener reaction)
    - silence / physical action / insert / establishing -> shots with no dialogue

This module is DETERMINISTIC for the structural plan (scene coverage, purpose,
mapping, IDs, continuity, timing) and exposes a semantic layer for the shot /
scene / episode evaluation + focused repair.
"""
from __future__ import annotations

import re
import logging
from typing import Any, Optional

logger = logging.getLogger("movie_os.genesis2.shots")

# Shot purpose taxonomy (P0-05 §7).
SHOT_PURPOSES = {
    "ESTABLISHING", "SPEAKER_COVERAGE", "LISTENER_REACTION", "TWO_SHOT",
    "OVER_THE_SHOULDER", "INSERT", "CUTAWAY", "SILENT_BEHAVIOR", "TRANSITION",
    "REVEAL", "EMOTIONAL_HOLD",
}

FRAMING = {"WIDE", "MEDIUM", "CLOSE_UP", "EXTREME_CLOSE_UP", "TWO_SHOT", "OVER_THE_SHOULDER", "INSERT"}
CAMERA_ANGLE = {"EYE_LEVEL", "HIGH", "LOW", "DUTCH"}
CAMERA_MOVEMENT = {"STATIC", "SLOW_PUSH_IN", "SLOW_TRACK", "HANDHELD", "PAN", "TILT", "CRANE"}
TRANSITION = {"CUT", "DISSOLVE", "WIPE", "FADE"}


# ---------------------------------------------------------------------------
# Canonical shot model
# ---------------------------------------------------------------------------

def empty_shot(scene_id: int, shot_index: int) -> dict[str, Any]:
    return {
        "shot_id": f"SC{scene_id:02d}-SH{shot_index:02d}",
        "scene_id": scene_id,
        "sequence_index": shot_index,
        "purpose": "",
        "narrative_function": "",
        "visual_subject": {"primary": "", "secondary": []},
        "framing": {"type": ""},
        "camera": {"angle": "EYE_LEVEL", "movement": "STATIC", "lens_intent": ""},
        "composition": {"relationship": ""},
        "visual_action": "",
        "emotional_intent": "",
        "performance_context": {},
        "dialogue_mapping": {"active_dialogue_line_ids": [], "starts_during_line": None, "ends_during_line": None},
        "audio_context": {"audible_speaker": ""},
        "speaker_visibility": {"visible": False, "mouth_readability": "NONE", "dialogue_line_ids": []},
        "listener_visibility": {"character_id": "", "visible": False},
        "continuity": {"previous_shot_id": None, "next_shot_id": None},
        "transition_intent": "CUT",
        "timing": {"estimated_duration_seconds": 0, "dialogue_span": 0, "pre_dialogue_hold": 0, "post_dialogue_hold": 0},
    }


# ---------------------------------------------------------------------------
# Deterministic coverage helpers
# ---------------------------------------------------------------------------

def _chars(scene: dict) -> list[str]:
    return [str(c) for c in (scene.get("characters_present") or ["Mark", "Sarah"]) if c]


def _other_char(scene: dict, speaker: str) -> str:
    chars = _chars(scene)
    low = (speaker or "").lower().replace("_inner", "")
    for c in chars:
        if c.lower() != low:
            return c
    return chars[0] if chars else ""


def _scene_has_spatial_need(scene: dict) -> bool:
    txt = " ".join([
        str(scene.get("scene_description") or ""),
        str(scene.get("title") or ""),
    ]).lower()
    spatial = ["house", "home", "kitchen", "dining", "bedroom", "door", "room",
               "apartment", "office", "couch", "table", "window", "lounge",
               "morning", "kitchen table", "front door", "living room"]
    return any(w in txt for w in spatial) or _scene_is_opening(scene)


def _scene_is_opening(scene: dict) -> bool:
    """Scene 1 or any scene whose description marks a strong spatial/time shift."""
    txt = (str(scene.get("scene_description") or "") + " " + str(scene.get("act") or "")).lower()
    return any(w in txt for w in ("establishes", "establish", "first", "introduces", "location",
                                  "arrives", "enters", "moves to", "the next", "new day"))


def _scene_is_first_or_turning(scene_id: int, scene: dict) -> bool:
    """An establishing shot helps the first scene, or a scene with a strong
    spatial/time shift (location change, Act boundary)."""
    txt = (str(scene.get("scene_description") or "") + " " + str(scene.get("act") or "")).lower()
    if scene_id == 1:
        return True
    if any(w in txt for w in ("new location", "moves to", "next day", "door", "arrives", "enters")):
        return True
    return False


def _scene_emotional_state(scene: dict) -> str:
    return str(scene.get("emotional_state") or scene.get("narrative_beat") or "").strip()


def _performance_fields(line: dict) -> dict:
    return {
        "emotional_state_primary": line.get("emotional_state_primary") or line.get("emotion", ""),
        "delivery_intent": line.get("delivery_intent", ""),
        "subtext": line.get("subtext", ""),
        "character_voice_id": line.get("character_voice_id", ""),
        "presentation_mode": line.get("presentation_mode", "EXTERNAL"),
        "physical_gaze": line.get("physical_gaze", ""),
        "physical_action": line.get("physical_action", ""),
        "objective": line.get("objective", ""),
    }


def _physical_signals(line: dict) -> list[str]:
    out = []
    for k in ("physical_gaze", "physical_posture", "physical_action"):
        v = str(line.get(k, "") or "").strip()
        if v:
            out.append(v)
    return out


def _line_id(line: dict, scene_id: int, idx: int) -> str:
    return str(line.get("line_id") or f"{scene_id}:D{idx+1:03d}")


def _camera_movement_for(line: dict) -> str:
    delivery = str(line.get("delivery_intent", "")).lower()
    if any(w in delivery for w in ("hesitat", "quiet", "slow", "careful", "restrain")):
        return "STATIC"
    if any(w in delivery for w in ("intense", "confront", "demand", "force", "push")):
        return "SLOW_PUSH_IN"
    return "STATIC"


def _composition_relationship(scene: dict) -> str:
    comp = str(scene.get("composition") or "").lower()
    if any(w in comp for w in ("negative space", "separation", "distance", "opposite")):
        return "separation / negative space"
    return "intimacy / shared frame"


def _is_major_beat(idx: int, n_lines: int, scene: dict) -> bool:
    total = max(n_lines, 1)
    txt = (str(scene.get("scene_description") or "") + " " + str(scene.get("title") or "")).lower()
    if idx == 0 or idx == total - 1:
        return True
    if any(w in txt for w in ("confront", "breaking", "reveal", "turning", "climax")):
        return True
    if idx == total // 2:
        return True
    return False


def _warrants_reaction(line: dict, prev_line: Optional[dict]) -> bool:
    """A reaction shot is warranted when the line is a question, an emotional
    pivot, carries subtext, or follows a major beat — regardless of whether
    `listener_reaction_intent` is populated."""
    # Explicit intent is the strongest signal.
    if str(line.get("listener_reaction_intent", "") or "").strip():
        return True
    text = str(line.get("text", "") or "").strip().lower()
    subtext = str(line.get("subtext", "") or "").strip().lower()
    delivery = str(line.get("delivery_intent", "") or "").strip().lower()
    # A question invites the listener's reaction.
    if text.endswith("?") or text.startswith("why") or text.startswith("how") or text.startswith("what"):
        return True
    # Subtext-heavy lines (concealment, fear, shame) warrant capturing the listener.
    if any(w in subtext for w in ("hidden", "hiding", "scared", "shame", "fear", "don't", "avoid", "protect")):
        return True
    if any(w in delivery for w in ("confront", "demand", "quiet but direct", "revelation", "admit")):
        return True
    return False


def _is_groupable(idx: int, n_lines: int, scene: dict) -> bool:
    """Minor lines can be grouped into a two-shot unless it's a confrontation
    scene where cutting carries the tension."""
    txt = (str(scene.get("scene_description") or "")).lower()
    if any(w in txt for w in ("confront", "climax", "reveal", "turning point", "breaking point")):
        return False
    return True


# ---------------------------------------------------------------------------
# Shot builders
# ---------------------------------------------------------------------------

def _speaker_shot(scene: dict, line: dict, scene_id: int, idx: int) -> dict:
    speaker = str(line.get("speaker", ""))
    listener = str(line.get("listener_character_id", "") or _other_char(scene, speaker))
    perf = _performance_fields(line)
    shot = empty_shot(scene_id, 0)
    lid = _line_id(line, scene_id, idx)
    shot["purpose"] = "SPEAKER_COVERAGE"
    shot["narrative_function"] = f"Capture {speaker} delivering a key line."
    shot["visual_subject"] = {"primary": speaker, "secondary": [listener] if listener else []}
    shot["framing"] = {"type": "CLOSE_UP"}
    shot["camera"] = {"angle": "EYE_LEVEL", "movement": _camera_movement_for(line), "lens_intent": ""}
    shot["composition"] = {"relationship": _composition_relationship(scene)}
    shot["visual_action"] = str(line.get("physical_action", "") or "speaking")
    shot["emotional_intent"] = perf["emotional_state_primary"] or _scene_emotional_state(scene)
    shot["performance_context"] = {"speaker": speaker, **perf}
    shot["dialogue_mapping"]["active_dialogue_line_ids"] = [lid]
    shot["audio_context"]["audible_speaker"] = speaker
    shot["speaker_visibility"] = {"visible": True, "mouth_readability": "CLEAR", "dialogue_line_ids": [lid]}
    shot["listener_visibility"] = {"character_id": listener, "visible": False}
    shot["timing"] = {"estimated_duration_seconds": 3.0, "dialogue_span": 1, "pre_dialogue_hold": 0.5, "post_dialogue_hold": 0.5}
    return shot


def _two_shot(scene: dict, group_lines: list[dict], scene_id: int, base_idx: int) -> dict:
    shot = empty_shot(scene_id, 0)
    lds = [str(ln.get("line_id") or "") for ln in group_lines if ln.get("line_id")]
    shot["purpose"] = "TWO_SHOT"
    shot["narrative_function"] = "Sustained two-shot carrying a natural multi-line exchange without cutting."
    shot["visual_subject"] = {"primary": "", "secondary": list(_chars(scene))}
    shot["framing"] = {"type": "TWO_SHOT"}
    shot["camera"] = {"angle": "EYE_LEVEL", "movement": "STATIC", "lens_intent": ""}
    shot["composition"] = {"relationship": _composition_relationship(scene)}
    shot["visual_action"] = "natural dialogue exchange"
    shot["emotional_intent"] = _scene_emotional_state(scene)
    shot["dialogue_mapping"]["active_dialogue_line_ids"] = lds
    shot["speaker_visibility"] = {"visible": True, "mouth_readability": "CLEAR", "dialogue_line_ids": lds}
    shot["audio_context"] = {"audible_speaker": "alternating"}
    shot["timing"] = {"estimated_duration_seconds": max(3.0, 1.5 * len(group_lines)), "dialogue_span": len(group_lines), "pre_dialogue_hold": 0, "post_dialogue_hold": 1}
    return shot


def _reaction_shot(scene: dict, line: dict, scene_id: int, idx: int, offscreen_speaker: str = "") -> dict:
    speaker = str(line.get("speaker", ""))
    listener = str(line.get("listener_character_id", "") or _other_char(scene, speaker))
    react_intent = str(line.get("listener_reaction_intent", "") or "").strip()
    perf = _performance_fields(line)
    shot = empty_shot(scene_id, 0)
    shot["purpose"] = "LISTENER_REACTION"
    shot["narrative_function"] = f"Capture {listener}'s reaction to {speaker}'s line."
    shot["visual_subject"] = {"primary": listener, "secondary": []}
    shot["framing"] = {"type": "CLOSE_UP"}
    shot["camera"] = {"angle": "EYE_LEVEL", "movement": "STATIC", "lens_intent": ""}
    shot["composition"] = {"relationship": "isolated / alone"}
    shot["visual_action"] = "reaction / processing"
    shot["emotional_intent"] = react_intent or f"{listener} registers the shift"
    shot["performance_context"] = {"reacting_character": listener, "reaction_intent": react_intent}
    if offscreen_speaker:
        shot["audio_context"]["audible_speaker"] = offscreen_speaker
        shot["dialogue_mapping"]["active_dialogue_line_ids"] = [str(line.get("line_id") or "")]
    shot["speaker_visibility"] = {"visible": False, "mouth_readability": "NOT_VISIBLE", "dialogue_line_ids": []}
    shot["listener_visibility"] = {"character_id": listener, "visible": True}
    shot["timing"] = {"estimated_duration_seconds": 3.0, "dialogue_span": 0, "pre_dialogue_hold": 0.5, "post_dialogue_hold": 1}
    return shot


def _establishing_shot(scene: dict, scene_id: int) -> dict:
    shot = empty_shot(scene_id, 0)
    shot["purpose"] = "ESTABLISHING"
    shot["narrative_function"] = f"Establish location/time/physical relationship for {scene.get('title')}."
    shot["visual_subject"] = {"primary": "", "secondary": list(_chars(scene))}
    shot["framing"] = {"type": "WIDE"}
    shot["camera"] = {"angle": "EYE_LEVEL", "movement": "STATIC", "lens_intent": "spatial context"}
    shot["composition"] = {"relationship": "establishes distance and environment"}
    shot["visual_action"] = "show the space containing the scene's emotional field"
    shot["emotional_intent"] = _scene_emotional_state(scene)
    shot["timing"] = {"estimated_duration_seconds": 3.0, "dialogue_span": 0, "pre_dialogue_hold": 2, "post_dialogue_hold": 0}
    return shot


def _insert_shot(scene: dict, scene_id: int, subject: str, fn: str) -> dict:
    shot = empty_shot(scene_id, 0)
    shot["purpose"] = "INSERT"
    shot["narrative_function"] = fn
    shot["visual_subject"] = {"primary": subject, "secondary": []}
    shot["framing"] = {"type": "INSERT"}
    shot["camera"] = {"angle": "EYE_LEVEL", "movement": "STATIC", "lens_intent": ""}
    shot["composition"] = {"relationship": "object / context"}
    shot["visual_action"] = f"show {subject}"
    shot["emotional_intent"] = "the emotional reality is in the detail"
    shot["timing"] = {"estimated_duration_seconds": 2.0, "dialogue_span": 0, "pre_dialogue_hold": 0, "post_dialogue_hold": 0}
    return shot


def _exit_hold(scene: dict, scene_id: int) -> dict:
    chars = _chars(scene)
    shot = empty_shot(scene_id, 0)
    shot["purpose"] = "EMOTIONAL_HOLD"
    shot["narrative_function"] = f"Leave the audience on the scene's {_scene_emotional_state(scene)} state."
    shot["visual_subject"] = {"primary": chars[-1] if chars else "", "secondary": []}
    shot["framing"] = {"type": "CLOSE_UP"}
    shot["camera"] = {"angle": "EYE_LEVEL", "movement": "STATIC", "lens_intent": ""}
    shot["composition"] = {"relationship": "residual / after effect"}
    shot["visual_action"] = "linger on the reaction / physical distance"
    shot["emotional_intent"] = scene.get("emotional_state") or "after-effect of the scene"
    shot["timing"] = {"estimated_duration_seconds": 4.0, "dialogue_span": 0, "pre_dialogue_hold": 0, "post_dialogue_hold": 3}
    return shot


def _motivated_inserts(scene: dict, scene_id: int) -> list[dict]:
    txt = (str(scene.get("scene_description") or "") + " " + str(scene.get("title") or "")).lower()
    out = []
    if any(w in txt for w in ("email", "termination", "letter", "notice")):
        out.append(_insert_shot(scene, scene_id, "termination email / letter", "reveal the inciting document"))
    elif any(w in txt for w in ("phone", "unread message", "message")):
        out.append(_insert_shot(scene, scene_id, "unread message / phone", "show the unattended connection"))
    elif any(w in txt for w in ("coffee", "cup", "untouched")):
        out.append(_insert_shot(scene, scene_id, "untouched coffee", "objectifies the disconnection"))
    elif any(w in txt for w in ("photo", "wedding", "photograph")):
        out.append(_insert_shot(scene, scene_id, "wedding photograph", "the relationship that is slipping away"))
    return out


# ---------------------------------------------------------------------------
# Scene planner
# ---------------------------------------------------------------------------

def plan_scene_shots(scene: dict, dialogue_plan: Optional[dict], scene_id: int) -> list[dict[str, Any]]:
    lines = (dialogue_plan or {}).get("lines", []) or []
    inner = (dialogue_plan or {}).get("inner_voice", []) or []
    shots: list[dict[str, Any]] = []

    # Establishing (only when spatial clarity benefits, and on scene 1 / shifts).
    if _scene_has_spatial_need(scene) and _scene_is_first_or_turning(scene_id, scene):
        shots.append(_establishing_shot(scene, scene_id))

    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]
        speaker = str(line.get("speaker", ""))
        listener = str(line.get("listener_character_id", "") or _other_char(scene, speaker))
        react_intent = str(line.get("listener_reaction_intent", "") or "").strip()

        # Reaction to the PREVIOUS line (listener reaction is first-class, §14).
        if i > 0 and _warrants_reaction(lines[i-1], None):
            shots.append(_reaction_shot(scene, lines[i-1], scene_id, i-1, offscreen_speaker=speaker))

        if _is_major_beat(i, n, scene):
            # Key line gets its own speaker shot.
            shots.append(_speaker_shot(scene, line, scene_id, i))
            # If it warrants a reaction, add one (one line -> two shots).
            if _warrants_reaction(line, None):
                shots.append(_reaction_shot(scene, line, scene_id, i, offscreen_speaker=speaker))
            i += 1
        elif _is_groupable(i, n, scene):
            # Group consecutive minor lines into one two-shot (multi-line shot).
            group = []
            while i < n and len(group) < 3 and _is_groupable(i, n, scene):
                group.append(lines[i])
                i += 1
            shots.append(_two_shot(scene, group, scene_id, i - len(group)))
        else:
            # Minor line as a quick single coverage shot.
            shots.append(_speaker_shot(scene, line, scene_id, i))
            i += 1

    # Motivated inserts (§13).
    for ins in _motivated_inserts(scene, scene_id):
        shots.append(ins)

    # Scene exit / emotional hold (§17).
    shots.append(_exit_hold(scene, scene_id))

    # Continuity links.
    for k, sh in enumerate(shots):
        sh["continuity"]["previous_shot_id"] = shots[k-1]["shot_id"] if k > 0 else None
        sh["continuity"]["next_shot_id"] = shots[k+1]["shot_id"] if k < len(shots)-1 else None
    return shots


def plan_episode_shots(scenes: list[dict], dialogue_plans: dict[int, dict]) -> list[dict[str, Any]]:
    all_shots: list[dict[str, Any]] = []
    for scene in scenes:
        sid = int(scene.get("scene_number") or scene.get("number") or 0)
        dlg = dialogue_plans.get(sid)
        all_shots.extend(plan_scene_shots(scene, dlg, sid))
    # Global re-index to unique shot ids.
    counter = 0
    for sh in all_shots:
        counter += 1
        sh["shot_id"] = f"SC{sh['scene_id']:02d}-SH{counter:02d}"
        sh["sequence_index"] = counter
    return all_shots
