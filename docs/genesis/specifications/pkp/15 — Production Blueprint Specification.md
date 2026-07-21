Genesis Foundational Standards (GFS)
PKP-15 — Production Blueprint Specification

Document ID: PKP-15
Title: Production Blueprint Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Production Blueprint Specification is the bridge between Genesis and the
Studio Engine. It aggregates the shot, asset, character, environment, camera,
lighting, rendering, and prompt requirements derived from every upstream
specification, and presents them in a form the Studio Engine can consume
without reinterpreting creative intent.

Per the Constitutional Charter (GFS-000, Section 15), Genesis ends at the
conclusion of pre-production. This specification is the last document Genesis
produces before handing off to the Studio Engine. It contains no
model-specific, renderer-specific, or provider-specific details. It contains
only creative intent expressed in implementation-neutral terms.

2. Scope

This specification defines:
- Shot requirements (per scene, derived from PKP-09 and PKP-10)
- Asset requirements (per scene, derived from PKP-11)
- Character requirements (per scene, derived from PKP-06 and PKP-08)
- Environment requirements (per scene, derived from PKP-05 and PKP-11)
- Camera intent (per shot, derived from PKP-10)
- Lighting intent (per scene, derived from PKP-10)
- Rendering intent (creative only; no renderer or model references)
- Prompt intent (the creative guidance downstream systems must honor)
- Production dependencies (the order in which assets must be prepared)

Out of scope: model selection, renderer selection, provider selection, GPU
allocation, render farm configuration, asset fabrication schedules. Those
belong to the Studio Engine.

3. Contents

3.1 Shot Requirements
Per scene, the shots the production requires. Each shot declares its scene,
its objective, its scale, its framing intent, its duration envelope, and its
relation to the scene's turning point.

3.2 Asset Requirements
Per scene, the assets the production requires. Each asset declares its type
(prop, set, costume, vehicle, technology), its source (from PKP-11), and its
narrative function.

3.3 Character Requirements
Per scene, the characters the production requires. Each character reference
declares the character's emotional state (from PKP-09), the wardrobe (from
PKP-11), and the performance register (from PKP-10).

3.4 Environment Requirements
Per scene, the environment the production requires. Each environment reference
declares the location (from PKP-05), the time of day, the weather, and the
sensory signature.

3.5 Camera Intent
Per shot, the camera intent. Declared as scale, angle tendency, movement
philosophy, and framing intent. No lens, no rig, no camera model.

3.6 Lighting Intent
Per scene, the lighting intent. Declared as the philosophy (from PKP-10), the
key direction, the contrast level, and the color temperature band. No fixture,
no wattage, no lighting console.

3.7 Rendering Intent
The creative rendering intent only. Declared as the look the production
requires — realism level, grain, sharpness, color saturation, motion blur
posture. No renderer, no model, no engine.

3.8 Prompt Intent
The creative guidance downstream systems must honor when generating any
asset. Declared as a set of principles derived from PKP-00 through PKP-14,
not as model-specific prompts.

3.9 Production Dependencies
The order in which assets must be prepared. Declared as a dependency graph
over assets, characters, and environments.

4. Inputs

- All prior PKP specifications (PKP-00 through PKP-14)
- Constitutional Charter (GFS-000)

5. Outputs

- A validated Production Blueprint record in the Production Knowledge Graph
- A materialized Production Blueprint Specification document
- A handoff package to the Studio Engine, containing the blueprint and
  references to every upstream specification

6. Schema

```yaml
production_blueprint:
  document_id: PKP-15
  version: 1.0.0
  shots:
    - id: <string>
      scene_id: <reference to PKP-09>
      objective: <string>
      scale: <wide|medium|close|extreme|other>
      framing_intent: <string>
      duration_envelope: <string>
      relation_to_turning_point: <string|null>
  assets:
    - id: <string>
      scene_id: <reference to PKP-09>
      type: <prop|set|costume|vehicle|technology>
      source: <reference to PKP-11>
      narrative_function: <string>
  characters:
    - scene_id: <reference to PKP-09>
      character_id: <reference to PKP-06>
      emotional_state: <string>
      wardrobe: <reference to PKP-11>
      performance_register: <string>
  environments:
    - scene_id: <reference to PKP-09>
      location_id: <reference to PKP-05>
      time_of_day: <string>
      weather: <string>
      sensory_signature: <string>
  camera_intent:
    - shot_id: <reference>
      scale: <string>
      angle_tendency: <string>
      movement_philosophy: <string>
      framing_intent: <string>
  lighting_intent:
    - scene_id: <reference to PKP-09>
      philosophy: <reference to PKP-10>
      key_direction: <string>
      contrast_level: <string>
      color_temperature_band: <string>
  rendering_intent:
    realism_level: <photoreal|realist|stylized|abstract>
    grain: <string>
    sharpness: <string>
    color_saturation: <string>
    motion_blur_posture: <string>
  prompt_intent:
    principles: [<string>]
    source_specifications: [<reference>]
  production_dependencies:
    - asset_id: <string>
      depends_on: [<asset_id>]
      reason: <string>
  provenance:
    source_specifications: [<reference to PKP-00 through PKP-14>]
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- shots (at least one per scene in PKP-09)
- assets (at least one per scene that requires an asset)
- characters (one entry per character per scene they appear in)
- environments (one entry per scene)
- camera_intent (one entry per shot)
- lighting_intent (one entry per scene)
- rendering_intent (all sub-fields)
- prompt_intent.principles (at least one)
- production_dependencies (the field is required; may be empty if no
  dependencies exist, with justification)
- provenance.confidence

8. Optional Fields

- shot.relation_to_turning_point (absent for shots not at a turning point)
- production_dependencies (recommended; required when assets have preparation
  order constraints)

9. Validation Rules

- PB-001: Every shot.scene_id must reference a scene in PKP-09.
- PB-002: Every asset.source must reference an asset in PKP-11.
- PB-003: Every character reference must be consistent with the scene's
  participants in PKP-09.
- PB-004: Every environment reference must be consistent with the scene's
  location in PKP-09.
- PB-005: camera_intent.scale must be consistent with the composition rules in
  PKP-10.
- PB-006: lighting_intent.philosophy must reference the lighting_intent in
  PKP-10.
- PB-007: rendering_intent.realism_level must be consistent with the
  camera_philosophy in PKP-10 and the physics.model in PKP-14.
- PB-008: prompt_intent.principles must not contain model-specific, 
  renderer-specific, or provider-specific references. Any such reference is
  invalid.
- PB-009: production_dependencies must form a directed acyclic graph; no
  circular dependencies.
- PB-010: The blueprint must contain no field that references a specific AI
  model, renderer, hardware platform, or commercial provider.
- PB-011: No requirement may violate a non-negotiable principle from PKP-00.
- PB-012: The blueprint must be complete — every scene in PKP-09 must have
  at least one shot, one environment, and the required character references.

10. Dependencies

- PKP-00 through PKP-14 (all hard dependencies; the blueprint cannot be
  authored without all upstream specifications certified)

11. Versioning

- MAJOR: Removal of a shot, change to rendering_intent, or change to
  prompt_intent.principles.
- MINOR: Addition of shots, assets, or dependencies.
- PATCH: Wording refinements that do not alter blueprint intent.

A MAJOR change to the Production Blueprint invalidates the handoff package
and requires recertification before delivery to the Studio Engine.

12. Examples

```yaml
production_blueprint:
  document_id: PKP-15
  version: 1.0.0
  shots:
    - id: "SHOT-001-01"
      scene_id: "SCN-001"
      objective: "Establish Holt's professional baseline."
      scale: "medium"
      framing_intent: "Holt centered, glass partition behind her."
      duration_envelope: "45-60 seconds"
      relation_to_turning_point: null
    - id: "SHOT-003-01"
      scene_id: "SCN-003"
      objective: "Mark the moment the anomaly is recognized."
      scale: "close"
      framing_intent: "Holt's face in profile; symptom visible on chart."
      duration_envelope: "30-40 seconds"
      relation_to_turning_point: "The turning point itself."
  assets:
    - id: "ASSET-001-01"
      scene_id: "SCN-001"
      type: "prop"
      source: "PROP-001"
      narrative_function: "Holt's diagnostic notebook, closed firmly."
    - id: "ASSET-003-01"
      scene_id: "SCN-003"
      type: "prop"
      source: "PROP-001"
      narrative_function: "Notebook open, page turned and re-turned."
  characters:
    - scene_id: "SCN-001"
      character_id: "CHR-001"
      emotional_state: "Practiced calm."
      wardrobe: "CST-001"
      performance_register: "internalized"
    - scene_id: "SCN-003"
      character_id: "CHR-001"
      emotional_state: "Curiosity shading into unease."
      wardrobe: "CST-001"
      performance_register: "internalized"
  environments:
    - scene_id: "SCN-001"
      location_id: "LOC-001"
      time_of_day: "Morning shift, 08:30."
      weather: "Overcast; amber light absent."
      sensory_signature: "Fluorescent hum, distant pages, low voices."
    - scene_id: "SCN-003"
      location_id: "LOC-001"
      time_of_day: "Late shift, 22:15."
      weather: "Rain audible against the window."
      sensory_signature: "Ventilation hum, rain, single distant page."
  camera_intent:
    - shot_id: "SHOT-001-01"
      scale: "medium"
      angle_tendency: "Eye-level, slight."
      movement_philosophy: "Static; no movement."
      framing_intent: "Symmetry of the institutional space."
    - shot_id: "SHOT-003-01"
      scale: "close"
      angle_tendency: "Slight low; protagonist's gaze downward to chart."
      movement_philosophy: "Static; no movement."
      framing_intent: "Reduce headroom; press the protagonist into the frame."
  lighting_intent:
    - scene_id: "SCN-001"
      philosophy: "withholding"
      key_direction: "Overhead fluorescent, slightly off-axis."
      contrast_level: "Low-to-moderate."
      color_temperature_band: "Cool, 5000-5600K."
    - scene_id: "SCN-003"
      philosophy: "withholding"
      key_direction: "Overhead fluorescent, one tube failing."
      contrast_level: "Moderate; shadow on protagonist's face."
      color_temperature_band: "Cool, 5000-5600K, with warm rain-window accent."
  rendering_intent:
    realism_level: "realist"
    grain: "Fine, present, never clean."
    sharpness: "Moderate; clinical detail without hyperrealism."
    color_saturation: "Desaturated; skin tones held neutral."
    motion_blur_posture: "Minimal; shutter angle implies 180° at 24fps."
  prompt_intent:
    principles:
      - "The audience must not be told how to feel."
      - "Every shot must earn its duration."
      - "Ambiguity is a deliverable, not a defect."
      - "No on-screen violence is shown; only its aftermath."
    source_specifications: ["PKP-00", "PKP-01", "PKP-04", "PKP-10", "PKP-12"]
  production_dependencies:
    - asset_id: "ASSET-003-01"
      depends_on: ["ASSET-001-01"]
      reason: "Notebook must be established as closed before its re-opening carries weight."
  provenance:
    source_specifications: ["PKP-00", "PKP-01", "PKP-02", "PKP-03", "PKP-04", "PKP-05", "PKP-06", "PKP-07", "PKP-08", "PKP-09", "PKP-10", "PKP-11", "PKP-12", "PKP-13", "PKP-14"]
    agent: "BlueprintArchitectAgent"
    session: "sess-014"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for sustainability annotations (carbon budget per scene) may be
  added when the Studio Engine introduces a sustainability layer.
- A field for virtual production intent (real-time engine-driven scenes) may
  be added in a MINOR version, expressed in implementation-neutral terms.
- A field for cross-production asset reuse (shared assets across a series)
  will be modeled as Knowledge Graph edges.