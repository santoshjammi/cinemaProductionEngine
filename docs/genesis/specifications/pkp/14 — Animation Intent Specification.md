Genesis Foundational Standards (GFS)
PKP-14 — Animation Intent Specification

Document ID: PKP-14
Title: Animation Intent Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Animation Intent Specification defines the motion language of the
production. It captures motion principles, gesture style, facial performance,
lip sync intent, physics, and effects philosophy.

This specification applies to any production that uses animation, motion
graphics, or any form of synthesized motion — including fully animated works,
hybrid live-action/animation, and productions with motion-graphic sequences.
For purely live-action works, this specification declares "motion is captured,
not synthesized" and is otherwise minimal.

This specification translates the Directorial Language (PKP-10) into a coherent
motion language. It does not specify rigs, skeletons, or simulation
parameters — those belong to the Production Blueprint (PKP-15) and downstream
Studio Engine specifications. It specifies the *intent* from which motion
production decisions are derived.

2. Scope

This specification defines:
- Motion principles (the production's beliefs about motion)
- Gesture style (the logic of body gesture)
- Facial performance (the logic of facial performance)
- Lip sync intent (the philosophy of lip synchronization)
- Physics (the physics model the production adheres to)
- Effects philosophy (the philosophy of visual effects)

Out of scope: shot composition (PKP-10), scene structure (PKP-09), rig
specifications, simulation parameters. Those belong to PKP-10, PKP-09, PKP-15,
and downstream Studio Engine specifications.

3. Contents

3.1 Motion Principles
The production's beliefs about motion — naturalistic, stylized, exaggerated,
withheld. Declared as a set of principles, each with its expression.

3.2 Gesture Style
The logic of body gesture. Declared as a set of principles for gesture
frequency, gesture amplitude, and the relation of gesture to speech.

3.3 Facial Performance
The logic of facial performance. Declared as a set of principles for the
micro-expressions the production permits, the expressions it refuses, and the
relation of facial performance to subtext.

3.4 Lip Sync Intent
The philosophy of lip synchronization. Declared as one of: precise, relaxed,
intentional desync, absent. If present, declares the tolerance and the
relation to vocal performance.

3.5 Physics
The physics model the production adheres to. Declared as one of: realist,
exaggerated, cartoon, abstract, withheld. Includes the rules governing
weight, momentum, and contact.

3.6 Effects Philosophy
The philosophy of visual effects. Declared as one of: absent, invisible,
expressive, presentational. Includes the principles governing when effects are
permitted and what they must accomplish.

4. Inputs

- Directorial Language Specification (PKP-10)
- Narrative Specification (PKP-09)
- Creative Strategy Specification (PKP-01)
- Vision Specification (PKP-00)

5. Outputs

- A validated Animation Intent record in the Production Knowledge Graph
- A materialized Animation Intent Specification document
- Motion principles propagated to PKP-15 (Production Blueprint)

6. Schema

```yaml
animation_intent:
  document_id: PKP-14
  version: 1.0.0
  applicability: <fully_animated|hybrid|motion_graphics|live_action|minimal>
  motion_principles:
    - principle: <string>
      expression: <string>
  gesture_style:
    - principle: <string>
      expression: <string>
  facial_performance:
    permitted_micro_expressions: [<string>]
    refused_expressions: [<string>]
    relation_to_subtext: <string>
  lip_sync_intent:
    mode: <precise|relaxed|intentional_desync|absent>
    tolerance: <string|null>
    relation_to_vocal_performance: <string|null>
  physics:
    model: <realist|exaggerated|cartoon|abstract|withheld>
    rules:
      - domain: <weight|momentum|contact|other>
        rule: <string>
  effects_philosophy:
    mode: <absent|invisible|expressive|presentational>
    principles: [<string>]
    when_permitted: <string|null>
    what_it_must_accomplish: <string|null>
  provenance:
    source_directorial: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- applicability
- motion_principles (at least one principle)
- physics.model
- effects_philosophy.mode
- provenance.confidence

8. Optional Fields

- gesture_style (required if applicability is not "live_action" or "minimal")
- facial_performance (required if applicability is "fully_animated" or
  "hybrid")
- lip_sync_intent (required if applicability is "fully_animated" or "hybrid"
  and the production includes spoken dialogue)
- physics.rules (recommended)
- effects_philosophy.principles, when_permitted, what_it_must_accomplish
  (required if mode is not "absent")

9. Validation Rules

- AN-001: applicability must be consistent with the format in PKP-02. A
  live-action feature may declare applicability "live_action" or "minimal";
  an animated feature must declare "fully_animated".
- AN-002: motion_principles must be consistent with the camera_philosophy in
  PKP-10. A camera that observes pairs with motion that observes; a camera
  that withholds pairs with motion that withholds.
- AN-003: gesture_style must be consistent with the performance_style in
  PKP-10.
- AN-004: facial_performance.relation_to_subtext must be consistent with the
  storytelling_philosophy in PKP-01.
- AN-005: lip_sync_intent.mode must be consistent with the voice_style in
  PKP-12.
- AN-006: physics.model must be consistent with the world rules in PKP-05.
- AN-007: effects_philosophy.mode must be consistent with the
  lighting_intent.philosophy in PKP-10.
- AN-008: No motion principle may violate a non-negotiable principle from
  PKP-00.
- AN-009: For applicability "live_action" or "minimal", motion_principles may
  declare "motion is captured, not synthesized" as a single principle.

10. Dependencies

- PKP-10 — Directorial Language Specification (hard)
- PKP-09 — Narrative Specification (soft)
- PKP-01 — Creative Strategy Specification (soft)
- PKP-00 — Vision Specification (soft)

11. Versioning

- MAJOR: Change to applicability, motion_principles, physics.model, or
  effects_philosophy.mode.
- MINOR: Additions to gesture_style, facial_performance, lip_sync_intent, or
  physics.rules.
- PATCH: Wording refinements that do not alter motion intent.

A MAJOR change to Animation Intent triggers revalidation of PKP-15.

12. Examples

```yaml
animation_intent:
  document_id: PKP-14
  version: 1.0.0
  applicability: "minimal"
  motion_principles:
    - principle: "Motion is captured, not synthesized."
      expression: "No animated or motion-graphic sequences; all motion is photographic."
  gesture_style: []
  facial_performance: []
  lip_sync_intent:
    mode: "absent"
    tolerance: null
    relation_to_vocal_performance: null
  physics:
    model: "realist"
    rules:
      - domain: "weight"
        rule: "Bodies obey real-world weight; no exaggerated falls."
      - domain: "contact"
        rule: "Contact is implied through sound and reaction, not visible impact."
  effects_philosophy:
    mode: "absent"
    principles: []
    when_permitted: null
    what_it_must_accomplish: null
  provenance:
    source_directorial: "PKP-10 v1.0.0"
    agent: "AnimationIntentArchitectAgent"
    session: "sess-013"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for virtual production intent (real-time engine-driven scenes) may
  be added when the Studio Engine supports virtual production.
- A field for motion capture philosophy (separate from motion principles) may
  be added in a MINOR version.
- A field for stylization references (specific animation traditions the
  production draws on) may be added when reference management becomes a
  first-class workflow.