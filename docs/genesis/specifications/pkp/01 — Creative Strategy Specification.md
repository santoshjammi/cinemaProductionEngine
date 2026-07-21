Genesis Foundational Standards (GFS)
PKP-01 — Creative Strategy Specification

Document ID: PKP-01
Title: Creative Strategy Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Creative Strategy Specification defines *how* the Vision will be achieved
creatively. It translates the vision-level "why" into a coherent creative
posture that governs genre, emotional mechanics, narrative positioning, and the
success metrics by which creative execution will be judged.

This specification is the editorial filter between the Vision and the
Narrative. Every narrative, directorial, and design choice must be traceable to
a strategy declared here.

2. Scope

This specification defines:
- Genre and sub-genre classification
- Production grammar (the visual and sonic vocabulary the production uses)
- Emotional strategy (the engineered emotional journey of the audience)
- Storytelling philosophy (the structural beliefs the production adheres to)
- Differentiation (what makes this production distinct within its genre)
- Narrative positioning (where the production sits in the cultural landscape)
- Creative constraints (the self-imposed rules that shape the work)
- Success metrics for creative execution

Out of scope: the story itself, character details, scene structure, technical
production parameters, distribution strategy.

3. Contents

3.1 Genre Classification
Primary genre, sub-genres, and any hybrid forms. Each classification must
include a justification that links back to the Vision.

3.2 Production Grammar
The recurring visual, sonic, and structural devices that constitute the
production's recognizable style. Includes lensing, framing tendencies, sonic
palette, and temporal structure.

3.3 Emotional Strategy
The engineered progression of audience emotional states across the runtime.
Defined as a sequence of emotional phases, each with a target state, a duration
envelope, and a transition rule.

3.4 Storytelling Philosophy
The structural beliefs the production holds about how stories should be told —
e.g., causal realism, subjective framing, chronological purity, ambiguity as
deliverable.

3.5 Differentiation
The specific attributes that distinguish this production from comparable works
in its genre. Must be falsifiable: an external reviewer must be able to confirm
or deny the differentiation.

3.6 Narrative Positioning
Where the production positions itself in the cultural landscape — its relation
to canon, to current discourse, and to its likely comparisons.

3.7 Creative Constraints
Self-imposed rules that constrain creative choice. These are not technical
limitations; they are artistic disciplines the production commits to.

3.8 Success Metrics
The observable criteria by which creative execution will be judged. These
metrics are creative, not commercial.

4. Inputs

- Vision Specification (PKP-00)
- Original synopsis and declared influences
- Constitutional Charter (GFS-000)

5. Outputs

- A validated Creative Strategy record in the Production Knowledge Graph
- A materialized Creative Strategy Specification document
- A set of creative constraints propagated to the Narrative, Directorial
  Language, Audio Intent, and Editing Language specifications

6. Schema

```yaml
creative_strategy:
  document_id: PKP-01
  version: 1.0.0
  genre:
    primary: <string>
    sub_genres: [<string>]
    hybrid: <string|null>
    justification: <string>
  production_grammar:
    visual: [<string>]
    sonic: [<string>]
    temporal: [<string>]
  emotional_strategy:
    phases:
      - name: <string>
        target_state: <string>
        duration_envelope: <string>
        transition_rule: <string>
  storytelling_philosophy: [<string>]
  differentiation:
    attributes: [<string>]
    falsifiable: true
  narrative_positioning:
    relation_to_canon: <string>
    relation_to_discourse: <string>
    likely_comparisons: [<string>]
  creative_constraints: [<string>]
  success_metrics:
    creative: [<string>]
    falsifiable: true
  provenance:
    source_vision: <reference to PKP-00>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- genre.primary
- genre.justification
- production_grammar (at least one entry in each of visual, sonic, temporal)
- emotional_strategy.phases (at least three phases)
- storytelling_philosophy (at least one entry)
- differentiation.attributes (at least one entry)
- creative_constraints (at least one entry)
- success_metrics.creative (at least one entry)
- provenance.source_vision
- provenance.confidence

8. Optional Fields

- genre.sub_genres
- genre.hybrid
- narrative_positioning (all sub-fields)
- long_term_value (inherited from Vision if expanded)

9. Validation Rules

- CS-001: genre.justification must reference the Vision statement by name or
  paraphrase.
- CS-002: emotional_strategy.phases must form a coherent sequence; no phase
  may be unreachable from the previous phase.
- CS-003: creative_constraints must be enforceable — each constraint must be
  checkable against downstream specifications.
- CS-004: differentiation.attributes must not be reducible to "high quality" or
  "well made"; they must identify a specific differentiator.
- CS-005: No creative constraint may contradict a non-negotiable principle
  declared in PKP-00.
- CS-006: success_metrics.creative must be observable without access to
  internal project records.

10. Dependencies

- PKP-00 — Vision Specification (hard dependency; cannot be authored without a
  certified Vision).

11. Versioning

- MAJOR: Change to genre.primary, emotional_strategy, or creative_constraints.
- MINOR: Additions to production_grammar, differentiation, or positioning.
- PATCH: Wording refinements that do not alter strategy.

A MAJOR change to Creative Strategy triggers revalidation of all narrative,
directorial, audio, and editing specifications.

12. Examples

```yaml
creative_strategy:
  genre:
    primary: "Psychological drama"
    sub_genres: ["Slow cinema", "Procedural inquiry"]
    hybrid: null
    justification: >-
      The Vision demands an examination of uncertainty; psychological drama
      permits the audience to inhabit that uncertainty without resolving it.
  production_grammar:
    visual:
      - "Static mid-shots held past the point of comfort."
      - "Negative space used to isolate the protagonist."
    sonic:
      - "Ambient room tone foregrounded over score."
      - "Dialogue mixed low; effort required to listen."
    temporal:
      - "Real-time duration in key scenes."
      - "Elliptical cuts between days, never within."
  emotional_strategy:
    phases:
      - name: "Immersion"
        target_state: "Attentive curiosity"
        duration_envelope: "0-15 minutes"
        transition_rule: "Establish professional baseline, then introduce anomaly."
      - name: "Doubt"
        target_state: "Cognitive uncertainty"
        duration_envelope: "15-70 minutes"
        transition_rule: "Anomaly resists resolution; certainty erodes."
      - name: "Tolerance"
        target_state: "Acceptance of unresolved state"
        duration_envelope: "70-95 minutes"
        transition_rule: "Protagonist stops seeking resolution; audience follows."
  storytelling_philosophy:
    - "Causality is suggested, never asserted."
    - "Subjectivity is the only available frame."
  differentiation:
    attributes:
      - "Protagonist's verdict is never revealed."
      - "No scene contains a flashback."
    falsifiable: true
  narrative_positioning:
    relation_to_canon: "Adjacent to the unreliable-witness tradition."
    relation_to_discourse: "Engages current debate on expert authority."
    likely_comparisons: ["The Seventh Seal", "A Woman's Tale"]
  creative_constraints:
    - "No scene longer than seven minutes."
    - "No more than four named characters."
    - "All time jumps marked by light change."
  success_metrics:
    creative:
      - "A test viewer cannot summarize the protagonist's verdict."
      - "Average shot length exceeds 9 seconds."
    falsifiable: true
```

13. Future Extensibility

- A field for cross-genre borrowing (e.g., drama borrowing thriller mechanics)
  may be added in a MINOR version.
- A field for audience segment-specific emotional strategies may be added
  when audience segmentation is introduced in PKP-00.
- A field for declared anti-patterns (what the production refuses to do
  creatively) may be promoted from creative_constraints in a future version.