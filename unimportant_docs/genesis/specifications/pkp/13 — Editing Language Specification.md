Genesis Foundational Standards (GFS)
PKP-13 — Editing Language Specification

Document ID: PKP-13
Title: Editing Language Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Editing Language Specification defines the editorial language of the
production. It captures rhythm, montage, transition rules, flashback policy,
time compression, titles, and credits.

This specification translates narrative structure into a coherent editorial
language. It does not specify cuts or edits — those belong to the Production
Blueprint (PKP-15) and downstream Studio Engine specifications. It specifies
the *principles* from which editorial decisions are derived.

2. Scope

This specification defines:
- Rhythm (the editorial tempo of the production)
- Montage (the philosophy of montage use)
- Transition rules (the permitted and refused transitions)
- Flashback policy (whether and how flashbacks are used)
- Time compression (how time is compressed across the runtime)
- Titles (the title sequence philosophy)
- Credits (the credits philosophy)

Out of scope: scene structure (PKP-09), shot lists, specific edit points.
Those belong to PKP-09, PKP-15, and downstream Studio Engine specifications.

3. Contents

3.1 Rhythm
The editorial tempo of the production. Declared as a set of principles for
shot duration, cut frequency, and the relation of rhythm to narrative phase.

3.2 Montage
The philosophy of montage use. Declared as one of: absent, summary, abstract,
associative, dialectical. If present, declares when montage is permitted and
what it must accomplish.

3.3 Transition Rules
The permitted and refused transitions. Declared as a list of permitted
transitions (cut, dissolve, fade, hard stop, match cut) and a list of refused
transitions with justifications.

3.4 Flashback Policy
Whether and how flashbacks are used. Declared as one of: absent, rare,
structural, pervasive. If present, declares the trigger logic and the
visual convention that distinguishes flashback from present.

3.5 Time Compression
How time is compressed across the runtime. Declared as a set of principles
for what compression is permitted (ellipses, match cuts, dissolve sequences)
and what is refused.

3.6 Titles
The title sequence philosophy. Declared as: absent, opening, closing, integrated.
If present, declares the duration envelope and the relation to the story.

3.7 Credits
The credits philosophy. Declared as: opening, closing, integrated, omitted.
If present, declares the duration envelope and the relation to the story.

4. Inputs

- Narrative Specification (PKP-09)
- Creative Strategy Specification (PKP-01)
- Vision Specification (PKP-00)
- Directorial Language Specification (PKP-10)
- Audio Intent Specification (PKP-12)

5. Outputs

- A validated Editing Language record in the Production Knowledge Graph
- A materialized Editing Language Specification document
- Editorial principles propagated to PKP-15 (Production Blueprint)

6. Schema

```yaml
editing_language:
  document_id: PKP-13
  version: 1.0.0
  rhythm:
    - principle: <string>
      expression: <string>
  montage:
    mode: <absent|summary|abstract|associative|dialectical>
    when_permitted: <string|null>
    what_it_must_accomplish: <string|null>
  transition_rules:
    permitted: [<cut|dissolve|fade|hard_stop|match_cut|other>]
    refused:
      - transition: <string>
        justification: <string>
  flashback_policy:
    mode: <absent|rare|structural|pervasive>
    trigger_logic: <string|null>
    visual_convention: <string|null>
  time_compression:
    permitted: [<string>]
    refused: [<string>]
  titles:
    mode: <absent|opening|closing|integrated>
    duration_envelope: <string|null>
    relation_to_story: <string|null>
  credits:
    mode: <opening|closing|integrated|omitted>
    duration_envelope: <string>
    relation_to_story: <string>
  provenance:
    source_narrative: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- rhythm (at least one principle)
- montage.mode (required; if mode is "absent", other montage fields are null)
- transition_rules.permitted (at least one)
- flashback_policy.mode (required; if mode is "absent", other flashback fields
  are null)
- time_compression.permitted (at least one)
- titles.mode
- credits.mode, duration_envelope, relation_to_story
- provenance.confidence

8. Optional Fields

- montage.when_permitted and what_it_must_accomplish (required if mode is not
  "absent")
- transition_rules.refused (recommended)
- flashback_policy.trigger_logic and visual_convention (required if mode is
  not "absent")
- time_compression.refused (recommended)
- titles.duration_envelope and relation_to_story (required if mode is not
  "absent")

9. Validation Rules

- EL-001: rhythm must be consistent with the pacing in PKP-09.
- EL-002: montage.mode must be consistent with the storytelling_philosophy in
  PKP-01. A philosophy of "causality is suggested, never asserted" forbids
  dialectical montage that asserts causality.
- EL-003: transition_rules.permitted must be consistent with the
  camera_philosophy in PKP-10. A camera that observes forbids match cuts that
  assert equivalence.
- EL-004: flashback_policy.mode must be consistent with the creative_constraints
  in PKP-01. A constraint forbidding flashbacks requires mode "absent".
- EL-005: time_compression.permitted must be consistent with the temporal
  structure in PKP-09.
- EL-006: titles.mode and credits.mode must be consistent with the
  runtime.target_minutes in PKP-02.
- EL-007: No editorial principle may violate a non-negotiable principle from
  PKP-00.
- EL-008: No transition may be both permitted and refused.

10. Dependencies

- PKP-09 — Narrative Specification (hard)
- PKP-01 — Creative Strategy Specification (hard)
- PKP-00 — Vision Specification (soft)
- PKP-10 — Directorial Language Specification (soft)
- PKP-12 — Audio Intent Specification (soft)

11. Versioning

- MAJOR: Change to rhythm principles, montage.mode, flashback_policy.mode, or
  titles.mode.
- MINOR: Additions to transition_rules, time_compression, or credits.
- PATCH: Wording refinements that do not alter editorial intent.

A MAJOR change to Editing Language triggers revalidation of PKP-15.

12. Examples

```yaml
editing_language:
  document_id: PKP-13
  version: 1.0.0
  rhythm:
    - principle: "Average shot length exceeds 9 seconds."
      expression: "Holds are held past the point of comfort."
    - principle: "Cut frequency decreases across the runtime."
      expression: "Final act contains the fewest cuts in the production."
  montage:
    mode: "absent"
    when_permitted: null
    what_it_must_accomplish: null
  transition_rules:
    permitted: ["cut", "fade", "hard_stop"]
    refused:
      - transition: "dissolve"
        justification: "Dissolves imply subjective passage; production forbids subjective time."
      - transition: "match_cut"
        justification: "Match cuts assert equivalence; production forbids asserted equivalence."
  flashback_policy:
    mode: "absent"
    trigger_logic: null
    visual_convention: null
  time_compression:
    permitted:
      - "Ellipses between days, marked by light change."
      - "Hard stops at end of shift."
    refused:
      - "Compression within a single consultation."
      - "Summary montage."
  titles:
    mode: "opening"
    duration_envelope: "60-90 seconds."
    relation_to_story: "Titles play over the opening shift; no separate title card."
  credits:
    mode: "closing"
    duration_envelope: "120-150 seconds."
    relation_to_story: "Credits play over the closing shot and the only non-diegetic music."
  provenance:
    source_narrative: "PKP-09 v1.0.0"
    agent: "EditingLanguageArchitectAgent"
    session: "sess-012"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for non-linear editorial structures (branching, interactive) may be
  added in a MINOR version when interactive productions are supported.
- A field for title typography intent (separate from title sequence) may be
  added when the Studio Engine introduces a typography layer.
- A field for cross-production editorial lineage (shared editorial languages
  across a series) will be modeled as Knowledge Graph edges.