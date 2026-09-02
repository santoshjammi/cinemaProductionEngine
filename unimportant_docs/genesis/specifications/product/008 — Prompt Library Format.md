Genesis Specification (GSPEC)
GSPEC-008 — Prompt Library Format

Document ID: GSPEC-008
Title: Prompt Library Format Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GO-109 Visual Expression Ontology

1. Purpose

This Specification defines the format for the Prompt Library — a reusable collection of prompt fragments, lighting setups, composition patterns, and style qualifiers that the Prompt Builder Agent uses to construct shot prompts.

2. Format

prompt_library:
  version: "1.0.0"

  style_qualifiers:
    cinematic:
      - "cinematic"
      - "film grain"
      - "shallow depth of field"
      - "anamorphic lens"
    photorealistic:
      - "photorealistic"
      - "8k"
      - "highly detailed"
      - "sharp focus"
    atmospheric:
      - "atmospheric"
      - "moody"
      - "soft lighting"
      - "diffused light"

  lighting_setups:
    natural_daylight:
      description: "Soft natural light from a window"
      qualifiers: ["soft natural lighting", "window light", "diffused daylight"]
    warm_interior:
      description: "Warm artificial light in an interior space"
      qualifiers: ["warm artificial lighting", "lamp light", "warm glow"]
    cold_night:
      description: "Cold blue light at night"
      qualifiers: ["cold blue light", "moonlight", "cool color temperature"]
    dramatic_shadow:
      description: "High contrast with strong shadows"
      qualifiers: ["high contrast", "strong shadows", "chiaroscuro lighting"]
    practical_lights:
      description: "Light from practical sources (TV, computer, candle)"
      qualifiers: ["practical lighting", "TV glow", "computer screen light"]

  composition_patterns:
    rule_of_thirds:
      description: "Subject placed on the rule of thirds grid"
      qualifiers: ["rule of thirds composition"]
    center_frame:
      description: "Subject centered in frame"
      qualifiers: ["centered composition", "symmetrical framing"]
    negative_space:
      description: "Generous negative space around subject"
      qualifiers: ["negative space", "minimalist composition"]
    dutch_angle:
      description: "Tilted camera for unease"
      qualifiers: ["dutch angle", "canted frame"]

  color_palettes:
    warm_amber:
      dominant: ["#D4A574", "#C4956A", "#B8855A"]
      accent: ["#8B4513", "#A0522D"]
    cool_blue:
      dominant: ["#4A6FA5", "#5B7FA5", "#6B8FA5"]
      accent: ["#2C3E50", "#1A252F"]
    desaturated_muted:
      dominant: ["#8B8B83", "#9B9B93", "#7B7B73"]
      accent: ["#5B5B53", "#4B4B43"]

  character_anchors:
    ethan:
      - "man in his early 30s"
      - "short dark brown hair"
      - "light stubble beard"
      - "gentle eyes"
      - "grey t-shirt"
      - "wedding band"
    claire:
      - "woman in her early 30s"
      - "shoulder-length brown hair"
      - "warm smile"
      - "soft sweaters"
      - "wedding band"

  environment_anchors:
    bedroom_morrison:
      - "master bedroom"
      - "queen bed with white linens"
      - "warm lamp on nightstand"
      - "dark wood dresser"
      - "curtained window"
    kitchen_morrison:
      - "modest kitchen"
      - "warm morning light from window"
      - "wooden table with two chairs"
      - "coffee maker on counter"
      - "open shelving with ceramic mugs"

3. Usage

The Prompt Library is loaded by the Prompt Builder Agent at the start of each production. The agent selects appropriate qualifiers based on the scene's emotional state, energy level, and visual requirements.
