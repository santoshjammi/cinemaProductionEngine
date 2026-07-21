Genesis Specification (GSPEC)
GSPEC-004 — Character DNA Format

Document ID: GSPEC-004
Title: Character DNA Format Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GO-104 Character Ontology

1. Purpose

This Specification defines the format for Character DNA — the complete specification of a character's identity, appearance, psychology, and arc.

2. Format

character_dna:
  key: "string (unique identifier)"
  name: "string"
  role: "protagonist | antagonist | supporting | tertiary"
  archetype: "string (optional)"

  physical:
    age: number
    gender: "male | female | non_binary"
    height: "string (optional)"
    build: "string (optional)"
    hair_color: "string"
    hair_style: "string"
    eye_color: "string"
    distinguishing_features: ["string"]
    visual_anchor: "string (key visual identifier for IPAdapter)"

  psychological:
    core_fear: "string"
    personality_traits: ["string"]
    emotional_patterns: ["string"]
    attachment_style: "secure | anxious | avoidant | disorganized"
    communication_style: "direct | indirect | avoidant | expressive"

  speech:
    vocabulary: "simple | moderate | rich | academic"
    rhythm: "slow | moderate | fast | varied"
    accent: "string (optional)"
    verbal_tics: ["string"]

  voice:
    pitch: "low | medium | high | varied"
    tone: "warm | cool | neutral | harsh | soft"
    pace: "slow | moderate | fast"
    emotional_range: ["string"]

  wardrobe:
    style: "string"
    colors: ["string"]
    signature_items: ["string"]

  expressions:
    facial: ["string"]
    gestural: ["string"]
    postural: ["string"]

  relationships:
    - character_id: "string"
      relationship_type: "spouse | parent | child | friend | colleague | rival"
      emotional_distance: number (1-10)
      dynamics: ["string"]

  history:
    formative_events: ["string"]
    secrets: ["string (optional)"]
    backstory: "string"

  arc:
    starting_state: "string"
    ending_state: "string"
    key_moments: ["string"]
    emotional_journey: ["string"]

3. Validation

- key must be unique within the production
- physical.age must be between 0 and 120
- psychological.core_fear must be non-empty
- arc.starting_state and arc.ending_state must be non-empty
- At least one relationship must be defined for non-tertiary characters
