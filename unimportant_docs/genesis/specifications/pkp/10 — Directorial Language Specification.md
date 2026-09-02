Genesis Foundational Standards (GFS)
PKP-10 — Directorial Language Specification

Document ID: PKP-10
Title: Directorial Language Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Directorial Language Specification defines the directing intent of the
production. It captures camera philosophy, composition, color language,
blocking, performance style, lighting intent, and visual metaphors.

This specification translates narrative structure into a coherent visual
language. It does not specify shots — that is the role of the Production
Blueprint (PKP-15). It specifies the *principles* from which shots are
derived. The Production Blueprint must conform to the language declared here.

2. Scope

This specification defines:
- Camera philosophy (the production's beliefs about what the camera does)
- Composition (the recurring framing logic)
- Color language (the palette and its semantic use)
- Blocking (the logic of body placement in space)
- Performance style (the intended register of acting)
- Lighting intent (the lighting philosophy, not the lighting setup)
- Visual metaphors (the recurring visual figures that carry meaning)

Out of scope: shot lists, lens choices, lighting setups, specific blocking
diagrams. Those belong to the Production Blueprint (PKP-15) and downstream
Studio Engine specifications.

3. Contents

3.1 Camera Philosophy
The production's beliefs about what the camera does — observes, interrogates,
accompanies, withdraws, withholds. Declared as a set of principles, each with
its expression.

3.2 Composition
The recurring framing logic — shot scale tendencies, headroom logic, negative
space use, symmetry and asymmetry, framing of the protagonist vs. the world.

3.3 Color Language
The palette and its semantic use. Declared as a primary palette, a secondary
palette, and the rules governing color transitions across the runtime.

3.4 Blocking
The logic of body placement in space — proximity rules, orientation rules, the
use of objects as barriers, the relation of bodies to architecture.

3.5 Performance Style
The intended register of acting — externalized, internalized, behavioral,
stylized. Declared with its source (Stanislavskian, Meisner, behavioral,
other) and its expression.

3.6 Lighting Intent
The lighting philosophy — naturalistic, designed, expressive, withholding.
Declared with its principles and its refusal (what the lighting will not do).

3.7 Visual Metaphors
The recurring visual figures that carry meaning. Each metaphor is declared
with its visual form, its referent, and its rules of use.

4. Inputs

- Narrative Specification (PKP-09)
- Creative Strategy Specification (PKP-01)
- Vision Specification (PKP-00)
- World Specification (PKP-05)

5. Outputs

- A validated Directorial Language record in the Production Knowledge Graph
- A materialized Directorial Language Specification document
- Directorial principles propagated to PKP-14 (Animation Intent) and PKP-15
  (Production Blueprint)

6. Schema

```yaml
directorial_language:
  document_id: PKP-10
  version: 1.0.0
  camera_philosophy:
    - principle: <string>
      expression: <string>
  composition:
    shot_scale_tendencies: <string>
    headroom_logic: <string>
    negative_space_use: <string>
    symmetry: <string>
    protagonist_vs_world: <string>
  color_language:
    primary_palette: [<string>]
    secondary_palette: [<string>]
    semantic_rules:
      - rule: <string>
        expression: <string>
    transitions: <string>
  blocking:
    proximity_rules: <string>
    orientation_rules: <string>
    objects_as_barriers: <string>
    bodies_and_architecture: <string>
  performance_style:
    register: <externalized|internalized|behavioral|stylized>
    source: <string>
    expression: <string>
  lighting_intent:
    philosophy: <naturalistic|designed|expressive|withholding>
    principles: [<string>]
    refusal: [<string>]
  visual_metaphors:
    - id: <string>
      visual_form: <string>
      referent: <string>
      rules_of_use: [<string>]
  provenance:
    source_narrative: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- camera_philosophy (at least one principle)
- composition (all sub-fields)
- color_language (primary_palette and semantic_rules)
- blocking (all sub-fields)
- performance_style (register and expression)
- lighting_intent (philosophy and principles)
- provenance.confidence

8. Optional Fields

- color_language.secondary_palette
- color_language.transitions
- lighting_intent.refusal (recommended)
- visual_metaphors (recommended for any production with symbolic intent)

9. Validation Rules

- DL-001: camera_philosophy must be consistent with the storytelling_philosophy
  in PKP-01. A storytelling philosophy of "subjectivity is the only available
  frame" implies a camera philosophy that does not claim omniscience.
- DL-002: composition.protagonist_vs_world must be consistent with the
  audience_transformation in PKP-00.
- DL-003: color_language.semantic_rules must be enforceable — each rule must
  be checkable against the scene list in PKP-09.
- DL-004: blocking.objects_as_barriers must be consistent with the
  symbolic_structure in PKP-04 when symbols involve physical objects.
- DL-005: performance_style.register must be consistent with the dialogue_style
  of the protagonist in PKP-06.
- DL-006: lighting_intent.refusal must not contradict a creative_constraint
  from PKP-01.
- DL-007: visual_metaphors must not duplicate the symbolic_structure in
  PKP-04; they extend it into the visual register.
- DL-008: No directorial principle may violate a non-negotiable principle from
  PKP-00.

10. Dependencies

- PKP-09 — Narrative Specification (hard)
- PKP-01 — Creative Strategy Specification (hard)
- PKP-00 — Vision Specification (soft)
- PKP-05 — World Specification (soft)

11. Versioning

- MAJOR: Change to camera_philosophy, performance_style.register, or
  lighting_intent.philosophy.
- MINOR: Additions to composition, color_language, blocking, or visual
  metaphors.
- PATCH: Wording refinements that do not alter directorial intent.

A MAJOR change to Directorial Language triggers revalidation of PKP-14 and
PKP-15.

12. Examples

```yaml
directorial_language:
  document_id: PKP-10
  version: 1.0.0
  camera_philosophy:
    - principle: "The camera observes; it does not narrate."
      expression: "No camera movement that explains what the protagonist is feeling."
    - principle: "The camera withholds."
      expression: "Reactions are framed out; we see what is looked at, not the looking."
  composition:
    shot_scale_tendencies: "Mid-shots dominate; close-ups reserved for moments of decision."
    headroom_logic: "Extra headroom in scenes of certainty; reduced headroom as doubt grows."
    negative_space_use: "Negative space expands as the protagonist's certainty contracts."
    symmetry: "Symmetry in institutional spaces; asymmetry in private ones."
    protagonist_vs_world: "Protagonist isolated in frame even when surrounded."
  color_language:
    primary_palette: ["Clinical gray-green", "Fluorescent white", "Skin tones only."]
    secondary_palette: ["Late-autumn amber", "Tram-light yellow."]
    semantic_rules:
      - rule: "Amber appears only outside the hospital."
        expression: "Marks spaces of respite; never appears inside."
      - rule: "Skin tones desaturate as certainty erodes."
        expression: "Subtle; cumulative across the runtime."
    transitions: "Palette shifts happen at act boundaries, never within."
  blocking:
    proximity_rules: "Protagonist maintains arm's-length distance from all colleagues."
    orientation_rules: "Protagonist faces the patient or the chart, rarely the colleague."
    objects_as_barriers: "The glass partition is the recurring barrier; never crossed by hand."
    bodies_and_architecture: "Bodies framed against institutional geometry; never against nature."
  performance_style:
    register: "internalized"
    source: "Behavioral; minimal external gesture."
    expression: "Performance carried in breath, gaze, and pause."
  lighting_intent:
    philosophy: "withholding"
    principles:
      - "Light sources visible in frame where possible."
      - "No fill light on protagonist's face during moments of doubt."
      - "Shadows permitted to obscure reaction."
    refusal:
      - "No motivated key light that flatters the protagonist."
      - "No backlight to separate protagonist from background."
  visual_metaphors:
    - id: "VM-001"
      visual_form: "The glass partition, increasingly prominent in frame."
      referent: "The barrier between expert certainty and the patient's reality."
      rules_of_use:
        - "Appears in every consultation scene."
        - "Prominence in frame increases across the runtime."
  provenance:
    source_narrative: "PKP-09 v1.0.0"
    agent: "DirectorialLanguageArchitectAgent"
    session: "sess-009"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for virtual camera philosophy (for animated or hybrid productions)
  may be added in a MINOR version.
- A field for color grading intent (separate from color language) may be added
  when the Studio Engine introduces a grading layer.
- A field for directorial anti-patterns (what the direction refuses to do) may
  be promoted from lighting_intent.refusal in a future version.