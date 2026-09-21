"""Backend-Neutral Voice Profiles (SAI-98 / TASK-018).

Defines voice *intent* independently of any TTS provider name, then maps each
profile to the concrete voice each adapter supports (edge-tts, VoxCPM, etc.).

GENESIS/PKP carries canonical voice IDs (e.g. MSVR-MARK, MSVR-SARAH) and
line-level delivery_intent. This module decouples that intent from the engine
so swapping a TTS backend changes only the `providers` map per profile — never
the story, the PKP, or the caller.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class VoiceProfile:
    """A backend-neutral voice identity."""

    profile_id: str                      # e.g. "msvr-mark" (canonical voice ID, low)
    role: str                            # protagonist / supporting_lead / narrator
    gender: str                          # male / female / neutral
    age_band: str                        # adult_30s / etc. — intent only
    energy: str                          # calm / restrained / warm / strained (delivery intent)
    emotion_default: str = "neutral"
    # Provider-specific voice names. Empty = profile not yet mapped for that backend.
    providers: dict[str, str] = field(default_factory=dict)

    def resolve(self, backend: str, fallback: str | None = None) -> str:
        """Return the concrete voice `backend` should use, or the fallback / ''."""
        return self.providers.get(backend) or fallback or ""


# Canonical profiles. profile_id matches the PKP voice registry IDs (MSVR-*)
# normalized to lowercase, so `msvr-mark` <- "MSVR-MARK".
VOICE_PROFILES: dict[str, VoiceProfile] = {
    "msvr-mark": VoiceProfile(
        profile_id="msvr-mark",
        role="protagonist",
        gender="male",
        age_band="adult_30s",
        energy="restrained",
        emotion_default="neutral",
        providers={
            "edge_tts": "en-US-BrianNeural",
            "xtts": "mark",
            "voxcpm": "mark",
        },
    ),
    "msvr-sarah": VoiceProfile(
        profile_id="msvr-sarah",
        role="supporting_lead",
        gender="female",
        age_band="adult_30s",
        energy="warm",
        emotion_default="neutral",
        providers={
            "edge_tts": "en-US-AriaNeural",
            "xtts": "sarah",
            "voxcpm": "sarah",
        },
    ),
    "narrator": VoiceProfile(
        profile_id="narrator",
        role="narrator",
        gender="neutral",
        age_band="adult",
        energy="calm",
        emotion_default="neutral",
        providers={
            "edge_tts": "en-US-GuyNeural",
            "xtts": "narrator",
        },
    ),
}

# Backend aliases accepted by resolve()/lookup.
_BACKEND_ALIASES = {
    "edge": "edge_tts",
    "edge-tts": "edge_tts",
    "edge_tts": "edge_tts",
    "xtts": "xtts",
    "coqui": "xtts",
    "voxcpm": "voxcpm",
}


def normalize_profile_id(value: str) -> str:
    """Normalize a PKP voice id (e.g. 'MSVR-MARK', 'Mark', 'MARK_INNER') to a key."""
    return (value or "").strip().lower().split("_")[0].strip()


def get_profile(profile_id: str) -> VoiceProfile | None:
    """Look up a profile by its normalized id.

    Accepts the PKP canonical form (MSVR-MARK), the bare character name
    (MARK, Mark), or the inner-voice suffix (MARK_INNER) — all resolve to the
    canonical profile.
    """
    if not profile_id:
        return None
    key = normalize_profile_id(profile_id)
    if key in VOICE_PROFILES:
        return VOICE_PROFILES[key]
    # Try the bare character name mapped to its MSVR- profile.
    for prof in VOICE_PROFILES.values():
        if key in prof.profile_id or key == prof.role:
            return prof
    return None


def resolve_voice(profile_id: str, backend: str, fallback: str = "") -> str:
    """Resolve a PKP voice id + backend to a concrete provider voice name."""
    prof = get_profile(profile_id)
    if prof is None:
        return fallback
    backend = _BACKEND_ALIASES.get((backend or "").lower(), (backend or "").lower())
    return prof.resolve(backend, fallback)


def available_backends() -> list[str]:
    """All provider names referenced across the profile set."""
    seen: set[str] = set()
    for p in VOICE_PROFILES.values():
        seen.update(p.providers.keys())
    return sorted(seen)
