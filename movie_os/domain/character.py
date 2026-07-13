"""Character DNA — the 9 facets that make a character persistent.

A Character is not just a name and an anchor string. It's a structured
DNA that persists across stories. When a story references a character
by ID, the renderer pulls the full DNA and uses it to:

  - generate consistent images (reference image + IPAdapter)
  - generate consistent voice (voice profile → TTS voice selection)
  - generate consistent behavior (psychological tendencies)
  - generate consistent speech (speaking style)
  - track relationships (who they are to other characters)
  - track history (what happened to them in previous stories)
  - track arc (how they developed over the story)
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    OTHER = "other"
    UNSPECIFIED = "unspecified"


# ---------------------------------------------------------------------------
# Facets of the Character DNA
# ---------------------------------------------------------------------------

class PhysicalAppearance(BaseModel):
    """What they look like."""
    age: int
    gender: Gender = Gender.UNSPECIFIED
    ethnicity: str = ""
    height_cm: Optional[int] = None
    build: str = ""                                  # "slim", "athletic", "stocky"
    hair: str = ""                                   # "auburn, slightly tangled"
    eyes: str = ""
    distinguishing_features: list[str] = Field(default_factory=list)
    # The visual anchor — short, comma-separated tokens used in image prompts
    visual_anchor: str = ""                          # "man mid-30s, dark hair, stubble, grey shirt"


class PsychologicalProfile(BaseModel):
    """Who they are on the inside."""
    personality_traits: list[str] = Field(default_factory=list)
    emotional_tendencies: list[str] = Field(default_factory=list)  # "tends toward withdrawal under stress"
    psychological_wounds: list[str] = Field(default_factory=list)
    defense_mechanisms: list[str] = Field(default_factory=list)
    core_fear: str = ""
    core_desire: str = ""


class SpeechProfile(BaseModel):
    """How they talk."""
    speaking_style: str = ""                         # "quiet, trailing off, short sentences"
    vocabulary_level: str = "conversational"         # simple, conversational, academic
    verbal_tics: list[str] = Field(default_factory=list)
    silence_tendencies: str = ""                    # "tends to go quiet when hurt"


class VoiceProfile(BaseModel):
    """What they sound like — drives TTS voice selection."""
    pitch: str = "medium"                            # low, medium, high
    pace: str = "medium"                             # slow, medium, fast
    tone: str = "warm"                               # warm, cold, neutral
    accent: str = ""
    # The TTS voice name (e.g., "en-US-GuyNeural")
    tts_voice: str = "en-US-GuyNeural"
    tts_provider: str = "edge"                       # "edge", "voicebox", "kokoro", etc.


class Wardrobe(BaseModel):
    """What they wear — persists across scenes for visual consistency."""
    default_outfit: str = ""                         # "grey t-shirt, half-tucked"
    signature_items: list[str] = Field(default_factory=list)
    style_notes: str = ""


class ExpressionRange(BaseModel):
    """The facial expressions they can show — for image generation variety."""
    expressions: list[str] = Field(default_factory=list)
    # Example: ["restraint: hand frozen mid-reach", "shame: head bowed", "numbness: blank stare"]


class Relationship(BaseModel):
    """Connection to another character."""
    other_character_id: UUID
    relationship_type: str = ""                      # "wife", "therapist", "estranged father"
    emotional_dynamic: str = ""                      # "protective but distant", "seeking approval"
    history: str = ""


class CharacterHistory(BaseModel):
    """Past events that shape them — for continuity across stories."""
    backstory: str = ""
    significant_events: list[str] = Field(default_factory=list)
    last_story_id: Optional[UUID] = None            # for cross-story continuity


class DevelopmentArc(BaseModel):
    """How they change over a story — for the renderer to know the arc."""
    starting_state: str = ""
    ending_state: str = ""
    key_moments: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Reference images
# ---------------------------------------------------------------------------

class CharacterReference(BaseModel):
    """A reference image for visual consistency (used by IPAdapter / img2img)."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    path: str                                        # path to the image file
    angle: str = "front"                             # front, three-quarter, side, back
    expression: str = "neutral"
    seed: Optional[int] = None
    created_at: date = Field(default_factory=date.today)


# ---------------------------------------------------------------------------
# Character DNA — the full thing
# ---------------------------------------------------------------------------

class CharacterDNA(BaseModel):
    """The complete character — 9 facets.

    This is the persistent definition. Stories reference characters by
    their `key` (a short string) and the renderer looks up the full
    DNA from the character registry.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    key: str                                          # short key, e.g., "husband", "wife"
    name: str
    role: str = ""                                    # "protagonist", "partner", "therapist"
    tags: list[str] = Field(default_factory=list)    # for searching

    # The 9 facets
    physical: PhysicalAppearance = Field(default_factory=lambda: PhysicalAppearance(age=0))
    psychological: PsychologicalProfile = Field(default_factory=PsychologicalProfile)
    speech: SpeechProfile = Field(default_factory=SpeechProfile)
    voice: VoiceProfile = Field(default_factory=VoiceProfile)
    wardrobe: Wardrobe = Field(default_factory=Wardrobe)
    expressions: ExpressionRange = Field(default_factory=ExpressionRange)
    relationships: list[Relationship] = Field(default_factory=list)
    history: CharacterHistory = Field(default_factory=CharacterHistory)
    arc: DevelopmentArc = Field(default_factory=DevelopmentArc)

    # Reference images
    reference_images: list[CharacterReference] = Field(default_factory=list)

    # Provenance
    created_at: date = Field(default_factory=date.today)
    notes: str = ""
