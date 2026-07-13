"""Default characters and environments for the emotional_withdrawal territory.

These are the canonical characters and environments used in the
psychological cinema series. They're seeded into the registry on
first use so that stories can reference them by key.

Characters:
  - ethan_morrison: 32-year-old husband, the protagonist
  - claire_morrison: 30-year-old wife, the partner

Environments:
  - bedroom_morrison: their shared bedroom
  - kitchen_morrison: their kitchen
  - car_morrison: the parked car (where the first fracture happens)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from movie_os.domain.character import (
    CharacterDNA, PhysicalAppearance, PsychologicalProfile, SpeechProfile,
    VoiceProfile, Wardrobe, ExpressionRange, Relationship, CharacterHistory,
    DevelopmentArc, Gender,
)
from movie_os.domain.environment import (
    EnvironmentDNA, LightingProfile, ColorPalette, SoundAmbience,
    CameraPosition, EnvironmentVariant, TimeOfDay, ArchitecturalStyle,
)
from movie_os.data_layer.character_registry import CharacterRegistry
from movie_os.data_layer.environment_registry import EnvironmentRegistry


logger = logging.getLogger("movie_os.data_layer.seeds")


def make_ethan_morrison() -> CharacterDNA:
    """Ethan Morrison — the protagonist, 32-year-old husband."""
    return CharacterDNA(
        key="ethan_morrison",
        name="Ethan Morrison",
        role="protagonist",
        tags=["emotional_withdrawal", "married_husband", "fear_based_withdrawal"],
        physical=PhysicalAppearance(
            age=32,
            gender=Gender.MALE,
            ethnicity="",
            hair="dark hair, slightly messy, receding at temples",
            build="average, slight stoop when tired",
            distinguishing_features=["slight stubble", "faint lines around eyes"],
            visual_anchor="man mid-30s, dark hair slightly messy, stubble, grey t-shirt half-tucked, lived-in face",
        ),
        psychological=PsychologicalProfile(
            personality_traits=["quiet", "observant", "emotionally restrained", "protective"],
            emotional_tendencies=["withdraws under stress", "goes silent when hurt", "overthinks social cues"],
            psychological_wounds=["anticipated rejection from wife", "childhood pressure to be 'the strong one'"],
            defense_mechanisms=["rationalization", "avoidance", "displacement into work"],
            core_fear="being unwanted / unlovable as he is",
            core_desire="to feel safe reaching for his wife again",
        ),
        speech=SpeechProfile(
            speaking_style="short sentences, trailing off, avoids eye contact when vulnerable",
            verbal_tics=["...", "I just thought...", "it's nothing"],
            silence_tendencies="goes quiet when hurt, retreats to internal monologue",
        ),
        voice=VoiceProfile(
            pitch="low-medium",
            pace="slow, measured",
            tone="warm but guarded",
            accent="general American",
            tts_voice="en-US-GuyNeural",
            tts_provider="edge",
        ),
        wardrobe=Wardrobe(
            default_outfit="grey t-shirt half-tucked, dark jeans, barefoot at home",
            signature_items=["grey t-shirt", "worn leather belt"],
            style_notes="comfort over style, slight dishevelment",
        ),
        expressions=ExpressionRange(
            expressions=[
                "restraint: hand frozen mid-reach, eyes watchful",
                "shame: head bowed, hunched shoulders",
                "numbness: blank stare, slack jaw",
                "grief: motionless, eyes unfocused",
                "tired: heavy eyes, posture not straight",
                "awkward: one sleeve half-rolled, off-center",
                "distracted: looking away mid-thought",
                "delayed: emotional response 5 seconds too long",
            ],
        ),
        history=CharacterHistory(
            backstory="Married 8 years. Was affectionate and playful in courtship. Work stress has increased over the past 2 years. Has experienced several moments of rejection from Claire that he's internalized as evidence of his unworthiness.",
        ),
        arc=DevelopmentArc(
            starting_state="confident, affectionate, playful",
            ending_state="quietly recognizing that his fear of rejection has created the very distance he was trying to avoid",
            key_moments=[
                "the first 'not tonight' he didn't speak about",
                "the long showers to avoid the bedroom",
                "the almost-touching moment in the kitchen",
                "Claire's quiet question that finally lands",
            ],
        ),
    )


def make_claire_morrison() -> CharacterDNA:
    """Claire Morrison — the partner, 30-year-old wife."""
    return CharacterDNA(
        key="claire_morrison",
        name="Claire Morrison",
        role="partner",
        tags=["emotional_withdrawal", "married_wife"],
        physical=PhysicalAppearance(
            age=30,
            gender=Gender.FEMALE,
            ethnicity="",
            hair="auburn, slightly tangled, usually down",
            build="slim, soft shoulders",
            distinguishing_features=["auburn hair", "thoughtful eyes", "small scar on left wrist (old, faded)"],
            visual_anchor="woman early 30s, auburn hair slightly tangled, white shirt, cardigan half-off, thoughtful eyes",
        ),
        psychological=PsychologicalProfile(
            personality_traits=["warm", "expressive", "intuitive", "exhausted"],
            emotional_tendencies=["interprets Ethan's withdrawal as rejection", "moves toward when hurt", "bottles then explodes"],
            psychological_wounds=["father was emotionally unavailable", "fears being a burden"],
            defense_mechanisms=["confrontation after long silence", "busyness as avoidance", "false cheerfulness"],
            core_fear="being too much, or not enough",
            core_desire="to feel chosen again",
        ),
        speech=SpeechProfile(
            speaking_style="soft, short sentences when hurt; long flowing when safe",
            verbal_tics=["I'm fine", "It's okay", "you don't have to..."],
            silence_tendencies="goes silent when truly hurt, then asks one devastating question",
        ),
        voice=VoiceProfile(
            pitch="medium-high",
            pace="measured, slows when emotional",
            tone="warm, slightly tired",
            accent="general American",
            tts_voice="en-US-JennyNeural",
            tts_provider="edge",
        ),
        wardrobe=Wardrobe(
            default_outfit="white shirt, cardigan half-off her shoulder, jeans, bare feet",
            signature_items=["white linen shirt", "oversized grey cardigan"],
            style_notes="casual elegance, slightly disheveled by the end of the day",
        ),
        expressions=ExpressionRange(
            expressions=[
                "warmth: leaning on his shoulder, eyes closed",
                "distance: facing away, gap between bodies",
                "exhaustion: tired, delayed response, slumped",
                "tired: heavy eyes, holding herself differently",
                "awkward: fidgeting with sleeve hem",
                "distracted: looking away, fiddling with mug",
                "delayed: emotional response 5 seconds too long",
                "grief: tears falling silently, staring at nothing",
            ],
        ),
        history=CharacterHistory(
            backstory="Married 8 years. Was expressive and warm in courtship. Has been initiating less as Ethan's withdrawal grew. Recently started a new job that takes more of her energy. Misses the man she married but doesn't know how to reach him.",
        ),
        arc=DevelopmentArc(
            starting_state="warm, expressive, hopeful",
            ending_state="quietly grieving, but also recognizing her own role in the distance",
            key_moments=[
                "the first morning she stopped trying to touch him",
                "the email she almost sent",
                "the almost-question that she finally asks",
            ],
        ),
    )


def make_bedroom_morrison() -> EnvironmentDNA:
    """The Morrisons' bedroom — the central environment."""
    return EnvironmentDNA(
        key="bedroom_morrison",
        name="James & Sarah's Bedroom",
        location_type="interior",
        architectural_style=ArchitecturalStyle.MODERN,
        lighting=LightingProfile(
            primary_source="bedside lamp + phone glow",
            color_temperature="warm amber + cool phone glow",
            practical_lights=["bedside lamp", "phone screen"],
            shadow_character="soft, intimate",
        ),
        palette=ColorPalette(
            dominant="cool blue undertones",
            accent="warm amber practical lights",
            shadows="deep but not crushed",
            highlights="soft, rolled off",
        ),
        ambience=SoundAmbience(
            room_tone="low hum of fan",
            primary_sounds=["fan hum", "breathing", "sheets rustling"],
            secondary_sounds=["distant traffic", "wind against window"],
            reverb_character="dry, bedroom close-mic",
        ),
        camera_positions=[
            CameraPosition(name="bedside_low", description="low angle from bed level", shot_size="medium"),
            CameraPosition(name="pillow", description="from pillow POV, looking at ceiling", shot_size="wide"),
            CameraPosition(name="doorway", description="from bedroom door, into the room", shot_size="wide"),
        ],
        variants=[
            EnvironmentVariant(time_of_day=TimeOfDay.NIGHT, weather="clear"),
            EnvironmentVariant(time_of_day=TimeOfDay.LATE_NIGHT, weather="clear"),
        ],
        description="A modest modern bedroom. The bed is slightly unmade — neither of them has had the energy to fix it. Mail on the nightstand, a phone face-down, a glass of water. Two pillows. The distance between them is visible.",
        notable_features=["unmade bed", "mail on nightstand", "phone face-down", "glass of water", "two pillows with space between"],
    )


def seed_default_characters(registry: CharacterRegistry) -> dict[str, CharacterDNA]:
    """Seed the registry with the default emotional_withdrawal characters.

    Returns a dict of {key: character} for the seeded characters.
    Only seeds characters that don't already exist.
    """
    defaults = {
        "ethan_morrison": make_ethan_morrison(),
        "claire_morrison": make_claire_morrison(),
    }
    seeded = {}
    for key, char in defaults.items():
        if not registry.has(key):
            registry.save(char)
            seeded[key] = char
            logger.info(f"Seeded character: {key}")
    return seeded


def seed_default_environments(registry: EnvironmentRegistry) -> dict[str, EnvironmentDNA]:
    """Seed the registry with the default emotional_withdrawal environments."""
    defaults = {
        "bedroom_morrison": make_bedroom_morrison(),
    }
    seeded = {}
    for key, env in defaults.items():
        if not registry.has(key):
            registry.save(env)
            seeded[key] = env
            logger.info(f"Seeded environment: {key}")
    return seeded
