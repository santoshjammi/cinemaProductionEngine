Genesis Reference (GREF)
GREF-001 — Visual Style Guide Template

Document ID: GREF-001
Title: Visual Style Guide Template
Version: 1.0.0
Status: Reference
Authority: Derived from GO-109 Visual Expression Ontology

1. Purpose

This document provides a template for defining the visual style of a Genesis production. It is populated by the Production Orchestrator Agent at the start of a production and stored in the Production Knowledge Graph as a VisualStyle node. It is referenced by the Prompt Builder Agent, Image Generator Agent, and Visual Consistency Agent to ensure visual coherence across all generated frames.

The template is intentionally restrictive: every field constrains downstream generation so that the production maintains a single, governed visual identity.

2. Template

visual_style:
  name: "string (human-readable style name)"
  description: "string (one-paragraph description of the intended look)"
  production_id: "uuid (parent production)"
  version: "1.0.0"

color_palette:
  dominant: ["hex", "hex", "hex"]
  accent: ["hex", "hex"]
  emotional_temperature: "warm | cool | neutral | mixed"
  saturation: "high | medium | low | desaturated"
  contrast: "high | medium | low"
  black_point: "string (optional, e.g. 'crushed blacks')"
  white_point: "string (optional, e.g. 'rolled highlights')"

lighting:
  primary_source: "natural | artificial | mixed | practical"
  color_temperature: "warm | cool | neutral | mixed"
  contrast: "high | medium | low"
  shadows: "hard | soft | diffused | none"
  key_light_position: "front | side | back | top | bottom"
  fill_light: "present | absent | minimal"
  backlight: "present | absent | rim_only"
  time_of_day_default: "string (e.g. 'golden hour', 'blue hour', 'midday')"

camera:
  lens: "35mm | 50mm | 85mm | 135mm | anamorphic"
  depth_of_field: "shallow | medium | deep"
  aspect_ratio: "16:9 | 4:3 | 21:9 | 1:1"
  grain: "none | subtle | moderate | heavy"
  color_grade: "natural | teal_orange | bleach_bypass | desaturated | warm"
  shutter_angle: "string (optional, e.g. '180deg')"

composition:
  framing: "rule_of_thirds | center | dutch_angle | symmetry | negative_space"
  leading_lines: true | false
  negative_space: "minimal | balanced | generous"
  headroom: "tight | balanced | generous"
  symmetry_tolerance: "strict | moderate | loose"

mood_board:
  - description: "string (description of the reference image)"
    reference_path: "string (optional, path or URL)"
    emotional_tag: "string (optional, e.g. 'melancholic', 'intimate')"

style_qualifiers:
  - "string (e.g. 'cinematic', 'film grain', 'shallow depth of field')"
  - "string"

negative_qualifiers:
  - "string (e.g. 'cartoonish', 'oversaturated', 'plastic skin')"

3. Field Definitions

- name: Human-readable identifier for the style
- description: One-paragraph description of the intended look and feel
- production_id: UUID of the parent production
- version: Style version; bumped when the style is revised
- color_palette.dominant: Three primary hex colors that dominate the frame
- color_palette.accent: One or two accent hex colors used sparingly
- color_palette.emotional_temperature: Overall color temperature classification
- color_palette.saturation: Saturation level classification
- color_palette.contrast: Tonal contrast classification
- lighting.primary_source: Dominant light source type
- lighting.color_temperature: Color temperature classification
- lighting.contrast: Lighting contrast classification
- lighting.shadows: Shadow hardness classification
- lighting.key_light_position: Position of the key light relative to subject
- camera.lens: Default focal length for the production
- camera.depth_of_field: Default depth of field
- camera.aspect_ratio: Frame aspect ratio
- camera.grain: Film grain level
- camera.color_grade: Color grading style
- composition.framing: Default framing approach
- composition.leading_lines: Whether leading lines are emphasized
- composition.negative_space: Default negative space usage
- mood_board: Reference images with descriptions and emotional tags
- style_qualifiers: Free-form qualifiers appended to prompts
- negative_qualifiers: Free-form exclusions appended to negative prompts

4. Usage

This template is populated at the start of each production by the Production Orchestrator Agent and stored in the PKG as a VisualStyle node. All downstream agents reference it to ensure visual consistency:

- Prompt Builder Agent: injects style_qualifiers, color_palette, lighting, and camera fields into shot prompts
- Image Generator Agent: applies the style to every generated frame
- Visual Consistency Agent: validates generated frames against the style node
- Video Composer Agent: ensures consistent grain, color grade, and aspect ratio across the cut

5. Example Values

visual_style:
  name: "Morrison Intimate Realism"
  description: "Warm, naturalistic domestic realism with shallow depth of field and soft window light, evoking intimacy and quiet grief."
  production_id: "a1b2c3d4-..."
  version: "1.0.0"

color_palette:
  dominant: ["#D4A574", "#C4956A", "#8B7355"]
  accent: ["#2C3E50", "#1A252F"]
  emotional_temperature: "warm"
  saturation: "medium"
  contrast: "medium"

lighting:
  primary_source: "natural"
  color_temperature: "warm"
  contrast: "medium"
  shadows: "soft"
  key_light_position: "side"
  fill_light: "minimal"
  backlight: "absent"
  time_of_day_default: "golden hour"

camera:
  lens: "85mm"
  depth_of_field: "shallow"
  aspect_ratio: "16:9"
  grain: "subtle"
  color_grade: "warm"

composition:
  framing: "rule_of_thirds"
  leading_lines: true
  negative_space: "balanced"
  headroom: "balanced"
  symmetry_tolerance: "moderate"

mood_board:
  - description: "Warm kitchen scene with soft window light"
    emotional_tag: "intimate"
  - description: "Close-up of hands holding a coffee mug"
    emotional_tag: "tender"

style_qualifiers:
  - "cinematic"
  - "film grain"
  - "shallow depth of field"
  - "anamorphic lens"

negative_qualifiers:
  - "cartoonish"
  - "oversaturated"
  - "plastic skin"

6. Evolution Policy

This template may evolve through additive extensions governed by the Reference Governance Framework. New optional fields may be added without breaking existing VisualStyle nodes. Removal or renaming of existing fields requires a major version bump.