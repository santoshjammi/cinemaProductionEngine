"""Medium-Specific Prompt Generation (SAI-90 / TASK-010).

Produces separate image, video, and audio generation prompts from the frozen
screenplay, each with the correct medium constraints:

  - image  → FLUX: single-shot composition, character anchors, still cinematography
  - video  → motion: the movement/framing directive (push-in, pan, zoom, hold)
  - audio  → TTS / ambience / foley / music: delivery, spatial, silence, score intent

The base cinematic language is shared; only the medium-appropriate constraint
is added. This keeps every stage deterministic and medium-correct.
"""

from __future__ import annotations

from typing import Any, Optional

# Medium constraint prefixes that must prefix each prompt class.
_MEDIUM_PREFIX = {
    "image": "IMAGEGEN_FLUX",
    "video": "VIDEO_MOTION",
    "tts": "TTS_VOICE",
    "ambience": "SFX_AMBIENCE",
    "foley": "SFX_FOLEY",
    "music": "MUSIC_SCORE",
}


def _extract_directive(shot: dict[str, Any]) -> str:
    """Pull the camera/movement directive from a shot spec, else ''."""
    for k in ("camera", "movement", "composition", "framing"):
        v = shot.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def build_image_prompt(scene: dict[str, Any]) -> str:
    """FLUX image prompt: anchors + behaviour + cinematic style (still)."""
    anchors = scene.get("character_lore") or scene.get("character_anchors") or ""
    behaviour = scene.get("visual_action") or scene.get("behaviour") or ""
    style = scene.get("cinematic_style") or scene.get("visual_grammar") or ""
    parts = [
        f"{_MEDIUM_PREFIX['image']}: still single-frame cinematic image",
        f"BEHAVIOUR: {behaviour}",
        f"CHARS: {anchors}" if anchors else None,
        f"STYLE: {style}",
    ]
    return ". ".join(p for p in parts if p)


def build_video_prompt(shot: dict[str, Any]) -> str:
    """Motion/video prompt: the camera movement directive only."""
    directive = _extract_directive(shot) or "static hold"
    subject = shot.get("visual_subject") or shot.get("visual_action") or ""
    return (
        f"{_MEDIUM_PREFIX['video']}: {directive}; subject: {subject}; "
        f"deterministic push-in/pull-back/pan/zoom/hold via ffmpeg Ken Burns"
    )


def build_tts_prompt(line: dict[str, Any]) -> str:
    """TTS prompt: spoken text + delivery intent + emotion."""
    text = line.get("text") or ""
    delivery = line.get("delivery_intent") or line.get("delivery") or ""
    emotion = line.get("emotion") or "neutral"
    return f"{_MEDIUM_PREFIX['tts']}: \"{text}\" | delivery: {delivery} | emotion: {emotion}"


def build_ambience_prompt(scene: dict[str, Any]) -> str:
    """Ambience prompt: the ambient/silence directive for the scene."""
    audio = scene.get("audio_goal") or scene.get("ambience") or ""
    return f"{_MEDIUM_PREFIX['ambience']}: {audio} — real or CC0 ambient bed, honour silence map"


def build_foley_prompt(scene: dict[str, Any]) -> str:
    foley = scene.get("foley") or scene.get("audio_refs") or ""
    return f"{_MEDIUM_PREFIX['foley']}: {foley} — diegetic, low in mix"


def build_music_prompt(scene: dict[str, Any]) -> str:
    music = scene.get("music_intent") or scene.get("score") or ""
    return f"{_MEDIUM_PREFIX['music']}: {music} — CC0/local only, under dialogue (see music_policy.yaml)"


def build_medium_prompts(scene: dict[str, Any], shot: dict[str, Any] | None = None, lines: list[dict[str, Any]] | None = None) -> dict[str, list[str]]:
    """Build the full medium-specific prompt set for a scene/line bundle.

    Returns a dict keyed by medium (image/video/tts/ambience/foley/music) of
    prompt strings. Empty list = no prompt needed for that medium in this unit.
    """
    result: dict[str, list[str]] = {"image": [], "video": [], "tts": [], "ambience": [], "foley": [], "music": []}
    result["image"].append(build_image_prompt(scene))
    if shot:
        result["video"].append(build_video_prompt(shot))
    result["ambience"].append(build_ambience_prompt(scene))
    foley = build_foley_prompt(scene)
    if foley != f"{_MEDIUM_PREFIX['foley']}: ":
        result["foley"].append(foley)
    music = build_music_prompt(scene)
    if music != f"{_MEDIUM_PREFIX['music']}: ":
        result["music"].append(music)
    if lines:
        result["tts"] = [build_tts_prompt(l) for l in lines if l.get("text")]
    return result
