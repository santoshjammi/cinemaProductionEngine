Genesis Specification (GSPEC)
GSPEC-006 — Scene Specification Format

Document ID: GSPEC-006
Title: Scene Specification Format
Version: 1.0.0
Status: Specification
Authority: Derived from GO-101 Narrative Ontology, GO-111 Temporal Experience Ontology

1. Purpose

This Specification defines the format for a single scene specification within a production. Each scene is a complete dramatic unit with narrative, visual, and audio specifications.

2. Format

scene:
  number: integer
  title: "string"
  act: "act_1 | act_2 | act_3"
  phase: "hook | warmth | normalcy | crack | collapse | almost | retreat | duality | climax"
  beat: "string (dramatic beat identifier)"

  narrative:
    scene_description: "string (what the audience sees)"
    scene_description_alt: "string (alternate angle for hard cut, optional)"
    emotional_state: "string"
    energy: integer (1-10)
    voiceover: "string (narration text)"
    dialogues:
      - character: "string"
        line: "string"
        timing: "string (optional)"
        emotion: "string (optional)"

  visual:
    shot_language:
      shot_size: "wide | medium | close-up | extreme_close-up"
      lighting_key: "string"
      lens_mm: integer
      depth_of_field: "shallow | medium | deep"
    ken_burns_effect: "ken-burns | zoom-in | zoom-out | pan-left | pan-right | static"
    characters_present: ["string (character keys)"]
    environment_id: "string (environment key)"

  audio:
    music_cue:
      zone: "act_1 | act_2 | act_3 | sting | none"
      volume: number (0.0-1.0)
      tempo: integer (optional, BPM)
      key: "string (optional, musical key)"
    silence_engine:
      silence_before: number (seconds, optional)
      silence_after: number (seconds, optional)
      silence_instead: boolean
    sfx_layers: ["string (effect types)"]

  timing:
    target_duration_seconds: number
    duration_hint: "string (optional)"

  flags:
    irreversible_moment: boolean
    pre_moment: boolean
    post_moment: boolean
    shows_duality: boolean
    vocal_fracture: boolean

3. Validation

- number must be unique within the production
- energy must be between 1 and 10
- target_duration_seconds must be between 1 and 300
- If irreversible_moment is true, scene_description_alt must be non-empty
- At least one of scene_description or scene_description_alt must be non-empty
