Genesis Foundational Standards (GFS)
PKP-09 — Narrative Specification

Document ID: PKP-09
Title: Narrative Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Narrative Specification defines the story structure of the production. It
captures acts, sequences, scenes, pacing, foreshadowing, callbacks, emotional
rhythm, and scene objectives.

This specification is the structural backbone of the production. Every scene
in the production must be declared here, and every scene must be traceable to
the Story (PKP-04), Characters (PKP-06), Relationships (PKP-07), and Psychology
(PKP-08) specifications. A scene not present in this specification may not be
shot, blocked, or designed.

2. Scope

This specification defines:
- The act structure of the production
- The sequences within each act
- The scenes within each sequence
- The pacing of the production
- The foreshadowing the production plants
- The callbacks the production harvests
- The emotional rhythm of the runtime
- The objective of each scene

Out of scope: shot language (PKP-10), set design (PKP-11), audio intent
(PKP-12), editing language (PKP-13).

3. Contents

3.1 Act Structure
The top-level structural divisions of the production. Each act declares its
narrative function, its opening condition, and its closing condition.

3.2 Sequences
Within each act, the sequences that compose it. A sequence is a chain of
scenes that share a single dramatic question. Each sequence declares its
dramatic question, its opening scene, and its closing scene.

3.3 Scenes
Within each sequence, the scenes that compose it. Each scene declares its
location, its participants, its objective, its conflict, its turning point
(if any), and its outcome.

3.4 Pacing
The tempo profile of the production across the runtime. Declared as a
sequence of pacing phases, each with a target shot-density envelope and a
target scene-duration envelope.

3.5 Foreshadowing
The elements the production plants for later harvest. Each foreshadow is
declared with its plant scene, its harvest scene, and its payload (what is
being foreshadowed).

3.6 Callbacks
The elements the production harvests from earlier plants. Each callback is
declared with its source scene, its callback scene, and its transformation
(how the meaning has shifted).

3.7 Emotional Rhythm
The engineered progression of audience emotional states across the runtime,
at scene-level resolution. This is the scene-level refinement of the
emotional_strategy declared in PKP-01.

3.8 Scene Objectives
The dramatic objective of each scene — what the scene must accomplish for the
story. A scene with no objective must be cut.

4. Inputs

- Story Specification (PKP-04)
- Character Specification (PKP-06)
- Relationship Specification (PKP-07)
- Psychology Specification (PKP-08)
- World Specification (PKP-05)
- Creative Strategy Specification (PKP-01)

5. Outputs

- A validated Narrative record in the Production Knowledge Graph
- A materialized Narrative Specification document
- The scene list propagated to PKP-10 (Directorial Language), PKP-12 (Audio
  Intent), PKP-13 (Editing Language), and PKP-15 (Production Blueprint)

6. Schema

```yaml
narrative:
  document_id: PKP-09
  version: 1.0.0
  acts:
    - id: <string>
      function: <string>
      opening_condition: <string>
      closing_condition: <string>
      sequences: [<reference to sequence ids>]
  sequences:
    - id: <string>
      act_id: <reference>
      dramatic_question: <string>
      opening_scene: <reference>
      closing_scene: <reference>
      scenes: [<reference to scene ids>]
  scenes:
    - id: <string>
      sequence_id: <reference>
      number: <integer>
      location: <reference to PKP-05>
      participants: [<reference to PKP-06>]
      objective: <string>
      conflict: <string>
      turning_point: <string|null>
      outcome: <string>
      duration_envelope: <string>
      emotional_state: <string>
  pacing:
    - phase: <string>
      act_range: <string>
      shot_density_envelope: <string>
      scene_duration_envelope: <string>
  foreshadowing:
    - id: <string>
      plant_scene: <reference>
      harvest_scene: <reference>
      payload: <string>
  callbacks:
    - id: <string>
      source_scene: <reference>
      callback_scene: <reference>
      transformation: <string>
  emotional_rhythm:
    - scene_id: <reference>
      audience_state: <string>
      transition_rule: <string>
  provenance:
    source_story: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- acts (at least one)
- sequences (at least one per act)
- scenes (at least one per sequence)
- For each scene: id, sequence_id, number, location, participants, objective,
  conflict, outcome, duration_envelope, emotional_state
- pacing (at least one phase)
- emotional_rhythm (one entry per scene)
- provenance.confidence

8. Optional Fields

- foreshadowing (recommended for any production with structural complexity)
- callbacks (recommended; required if foreshadowing is declared)
- scene.turning_point (absent for scenes without a turning point)

9. Validation Rules

- N-001: Every scene.location must reference a location in PKP-05.
- N-002: Every scene.participant must reference a character in PKP-06.
- N-003: Scene numbers must be unique and monotonic across the production.
- N-004: Each scene must have a non-empty objective; a scene with no objective
  is invalid.
- N-005: emotional_rhythm must have one entry per scene; the sequence of
  audience_states must be consistent with the emotional_strategy in PKP-01.
- N-006: foreshadowing.harvest_scene must occur after plant_scene in scene
  number order.
- N-007: callbacks.source_scene must occur before callback_scene in scene
  number order.
- N-008: A scene's emotional_state must be consistent with the emotional_arc
  of each participant as declared in PKP-06 and PKP-08.
- N-009: No scene may violate a creative_constraint from PKP-01 (e.g., a
  constraint forbidding scenes over seven minutes caps duration_envelope).
- N-010: No scene may violate a non-negotiable principle from PKP-00.
- N-011: Each act's closing_condition must be met by the outcome of its final
  scene.

10. Dependencies

- PKP-04 — Story Specification (hard)
- PKP-06 — Character Specification (hard)
- PKP-07 — Relationship Specification (hard)
- PKP-08 — Psychology Specification (hard)
- PKP-05 — World Specification (hard)
- PKP-01 — Creative Strategy Specification (soft)

11. Versioning

- MAJOR: Removal of an act, sequence, or scene; change to scene order; change
  to a scene's objective.
- MINOR: Addition of scenes, sequences, or acts; addition of foreshadowing or
  callbacks.
- PATCH: Wording refinements that do not alter structure.

A MAJOR change to Narrative triggers revalidation of PKP-10, PKP-12, PKP-13,
and PKP-15.

12. Examples

```yaml
narrative:
  document_id: PKP-09
  version: 1.0.0
  acts:
    - id: "ACT-01"
      function: "Establish protagonist's professional certainty."
      opening_condition: "Routine shift begins."
      closing_condition: "Anomaly introduced; certainty first strained."
      sequences: ["SEQ-01", "SEQ-02"]
    - id: "ACT-02"
      function: "Pursuit of closure; certainty erodes."
      opening_condition: "Anomaly resists verification."
      closing_condition: "Closure fails to arrive."
      sequences: ["SEQ-03"]
    - id: "ACT-03"
      function: "Protagonist stops seeking closure."
      opening_condition: "Closure attempt abandoned."
      closing_condition: "Protagonist leaves case open without rupture."
      sequences: ["SEQ-04"]
  sequences:
    - id: "SEQ-01"
      act_id: "ACT-01"
      dramatic_question: "Will the shift pass without incident?"
      opening_scene: "SCN-001"
      closing_scene: "SCN-002"
      scenes: ["SCN-001", "SCN-002"]
    - id: "SEQ-02"
      act_id: "ACT-01"
      dramatic_question: "What is the anomaly?"
      opening_scene: "SCN-003"
      closing_scene: "SCN-003"
      scenes: ["SCN-003"]
  scenes:
    - id: "SCN-001"
      sequence_id: "SEQ-01"
      number: 1
      location: "LOC-001"
      participants: ["CHR-001", "CHR-002"]
      objective: "Establish Holt's professional baseline and her relationship with Lindgren."
      conflict: "Institutional demand for closure vs. Holt's standard of rigor."
      turning_point: null
      outcome: "Baseline established; routine preserved."
      duration_envelope: "4-6 minutes"
      emotional_state: "Practiced calm."
    - id: "SCN-003"
      sequence_id: "SEQ-02"
      number: 3
      location: "LOC-001"
      participants: ["CHR-001"]
      objective: "Introduce the anomaly that will drive the production."
      conflict: "Holt's diagnostic framework vs. a symptom that does not fit."
      turning_point: "Holt recognizes the symptom does not fit any available diagnosis."
      outcome: "Anomaly acknowledged; first hairline crack in certainty."
      duration_envelope: "5-7 minutes"
      emotional_state: "Curiosity shading into unease."
  pacing:
    - phase: "Establishment"
      act_range: "ACT-01"
      shot_density_envelope: "Low; long takes."
      scene_duration_envelope: "4-7 minutes per scene."
    - phase: "Erosion"
      act_range: "ACT-02"
      shot_density_envelope: "Moderate; takes shorten as certainty erodes."
      scene_duration_envelope: "3-6 minutes per scene."
    - phase: "Settling"
      act_range: "ACT-03"
      shot_density_envelope: "Low; takes lengthen again."
      scene_duration_envelope: "5-8 minutes per scene."
  foreshadowing:
    - id: "FORESHADOW-001"
      plant_scene: "SCN-001"
      harvest_scene: "SCN-009"
      payload: "The institutional demand for closure will return as the thing Holt must refuse."
  callbacks:
    - id: "CALLBACK-001"
      source_scene: "SCN-001"
      callback_scene: "SCN-009"
      transformation: "The phrase 'just close it out' returns, but Holt now refuses it."
  emotional_rhythm:
    - scene_id: "SCN-001"
      audience_state: "Attentive calm."
      transition_rule: "Routine invites the audience into the protagonist's rhythm."
    - scene_id: "SCN-003"
      audience_state: "First unease."
      transition_rule: "Anomaly breaks the routine; audience inherits the crack."
  provenance:
    source_story: "PKP-04 v1.0.0"
    agent: "NarrativeArchitectAgent"
    session: "sess-008"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for alternative structures (non-linear, branching) may be added in
  a MINOR version when interactive productions are supported.
- A field for scene-level beats (sub-scene structural units) may be added when
  the Studio Engine requires beat-level resolution.
- A field for cross-narrative lineage (sequels, adaptations) will be modeled
  as Knowledge Graph edges.