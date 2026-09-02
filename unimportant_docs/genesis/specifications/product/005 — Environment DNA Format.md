Genesis Specification (GSPEC)
GSPEC-005 — Environment DNA Format

Document ID: GSPEC-005
Title: Environment DNA Format Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GO-105 World & Environment Ontology

1. Purpose

This Specification defines the format for Environment DNA — the complete specification of a location's visual, auditory, and atmospheric identity.

2. Format

environment_dna:
  key: "string (unique identifier)"
  name: "string"
  location_type: "interior | exterior | urban | natural | liminal | vehicle"
  architectural_style: "string (optional)"

  lighting:
    primary_source: "natural | artificial | mixed | practical | none"
    color_temperature: "warm | cool | neutral | mixed"
    intensity: "bright | moderate | dim | dark"
    contrast: "high | medium | low"
    shadows: "hard | soft | diffused | none"
    key_light_position: "front | side | back | top | bottom | multiple"

  palette:
    dominant: ["hex", "hex", "hex"]
    accent: ["hex", "hex"]
    emotional_temperature: "warm | cool | neutral | mixed"
    saturation: "high | medium | low | desaturated"

  ambience:
    room_tone: "string"
    ambient_sounds: ["string"]
    silence_quality: "dead | live | warm | cold | neutral"
    echo: "none | slight | moderate | heavy"

  camera_positions:
    - name: "string"
      angle: "eye_level | low_angle | high_angle | dutch | overhead"
      distance: "close | medium | far | extreme"
      description: "string"

  variants:
    - name: "string"
      time_of_day: "dawn | morning | afternoon | evening | night | late_night"
      weather: "clear | cloudy | rainy | stormy | snowy | foggy"
      lighting_override: { ... }
      palette_override: { ... }

  visual_anchor: "string (key visual identifier for IPAdapter)"

3. Validation

- key must be unique within the production
- location_type must be one of the defined types
- At least one camera position must be defined
- visual_anchor must be non-empty for primary locations
