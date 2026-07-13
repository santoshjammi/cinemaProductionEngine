"""Environment DNA — the 8 facets that make a location persistent.

Like Character DNA, an Environment is not just "bedroom" — it's a
structured definition that persists across stories. When a story says
"the bedroom", the renderer pulls the full Environment DNA and uses it
to:

  - generate consistent images (lighting, color palette, architecture)
  - generate consistent ambient audio (sound profile)
  - track multiple camera positions (which angles are available)
  - track time-of-day variants (day / night / golden hour)
  - track weather variants (rain / clear / overcast)
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class TimeOfDay(str, Enum):
    DAWN = "dawn"
    MORNING = "morning"
    MIDDAY = "midday"
    GOLDEN_HOUR = "golden_hour"
    DUSK = "dusk"
    NIGHT = "night"
    LATE_NIGHT = "late_night"


class Weather(str, Enum):
    CLEAR = "clear"
    OVERCAST = "overcast"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    STORM = "storm"


class ArchitecturalStyle(str, Enum):
    MODERN = "modern"
    CONTEMPORARY = "contemporary"
    TRADITIONAL = "traditional"
    INDUSTRIAL = "industrial"
    MINIMALIST = "minimalist"
    RUSTIC = "rustic"
    VICTORIAN = "victorian"
    MID_CENTURY = "mid_century"
    ASIAN = "asian"                                  # generic Asian
    UNSPECIFIED = "unspecified"


# ---------------------------------------------------------------------------
# Facets
# ---------------------------------------------------------------------------

class LightingProfile(BaseModel):
    """The lighting setup of this environment."""
    primary_source: str = "natural"                  # "natural window", "practical lamp", "overhead"
    color_temperature: str = "neutral"               # "warm amber", "cool blue", "neutral"
    practical_lights: list[str] = Field(default_factory=list)
    shadow_character: str = "soft"
    typical_key_to_fill_ratio: str = "2:1"           # lighting ratio
    notes: str = ""


class ColorPalette(BaseModel):
    """The dominant colors."""
    dominant: str = ""                               # "cool blue undertones"
    accent: str = ""                                 # "warm amber practical lights"
    shadows: str = "deep"                            # "deep but not crushed"
    highlights: str = "soft"                         # "soft, rolled off"
    avoid: list[str] = Field(default_factory=list)   # colors to avoid


class SoundAmbience(BaseModel):
    """The acoustic signature of this environment."""
    room_tone: str = ""                              # "low hum of refrigerator"
    primary_sounds: list[str] = Field(default_factory=list)
    secondary_sounds: list[str] = Field(default_factory=list)
    reverb_character: str = "dry"                    # "dry", "live", "echoey"
    notes: str = ""


class CameraPosition(BaseModel):
    """A specific camera angle in this environment — reusable across scenes."""
    name: str                                        # "bedside", "kitchen counter", "window"
    description: str = ""                            # "low angle from bed level, looking toward door"
    shot_size: str = "medium"                        # typical shot size from this position
    lens_mm: int = 50
    typical_subjects: list[str] = Field(default_factory=list)  # what's usually in frame


class EnvironmentVariant(BaseModel):
    """A variant of this environment (different time/weather)."""
    time_of_day: TimeOfDay
    weather: Weather
    lighting_overrides: dict[str, str] = Field(default_factory=dict)
    ambient_overrides: dict[str, str] = Field(default_factory=dict)
    notes: str = ""


class EnvironmentReference(BaseModel):
    """A reference image for visual consistency."""
    id: UUID = Field(default_factory=uuid4)
    path: str
    time_of_day: TimeOfDay = TimeOfDay.MIDDAY
    weather: Weather = Weather.CLEAR
    camera_position: str = "default"
    seed: Optional[int] = None
    created_at: date = Field(default_factory=date.today)


# ---------------------------------------------------------------------------
# Environment DNA
# ---------------------------------------------------------------------------

class EnvironmentDNA(BaseModel):
    """The complete environment — 8 facets."""
    model_config = ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    key: str                                          # short key, e.g., "bedroom", "kitchen"
    name: str                                        # "James & Sarah's Bedroom"
    location_type: str = ""                          # "interior", "exterior", "mixed"
    architectural_style: ArchitecturalStyle = ArchitecturalStyle.UNSPECIFIED

    # The 8 facets
    lighting: LightingProfile = Field(default_factory=LightingProfile)
    palette: ColorPalette = Field(default_factory=ColorPalette)
    ambience: SoundAmbience = Field(default_factory=SoundAmbience)
    camera_positions: list[CameraPosition] = Field(default_factory=list)
    variants: list[EnvironmentVariant] = Field(default_factory=list)
    reference_images: list[EnvironmentReference] = Field(default_factory=list)

    # Descriptive
    description: str = ""                            # "modest apartment, lived-in, dimly lit"
    notable_features: list[str] = Field(default_factory=list)  # "unmade bed, mail on counter, plants"

    # Provenance
    created_at: date = Field(default_factory=date.today)
    notes: str = ""
