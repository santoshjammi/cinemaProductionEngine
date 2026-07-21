Genesis Foundational Standards (GFS)
PKP-04 — Story Specification

Document ID: PKP-04
Title: Story Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Story Specification defines the narrative foundation of the production. It
captures the premise, theme, dramatic question, logline, central conflict,
symbolic structure, resolution posture, and recurring motifs.

This specification is the narrative seed from which the World (PKP-05),
Characters (PKP-06), and Narrative Structure (PKP-09) grow. It does not describe
the plot in detail — that is the role of the Narrative Specification. It
describes the story's *meaning* and *engine*.

2. Scope

This specification defines:
- The premise (the dramatic situation the production stages)
- The theme (the abstract subject the production examines)
- The dramatic question (the unanswered question that drives the story)
- The logline (a single-sentence expression of the story)
- The central conflict (the opposition that generates drama)
- The symbolic structure (the recurring symbolic logic of the work)
- The resolution posture (how the story ends, in tonal terms)
- The motifs (recurring elements that bind the work together)

Out of scope: scene structure, character psychology, world geography, shot
language. Those belong to PKP-09, PKP-08, PKP-05, and PKP-10 respectively.

3. Contents

3.1 Premise
The dramatic situation the production stages. Must be expressible in two to
four sentences and must contain a protagonist, a situation, and a source of
tension.

3.2 Theme
The abstract subject the production examines. Must be a noun phrase, not a
moral statement. The production examines the theme; it does not argue a
position on it.

3.3 Dramatic Question
The unanswered question that generates the story's forward motion. Must be
answerable in principle but not answered until the resolution, and possibly
not even then.

3.4 Logline
A single-sentence expression of the story containing protagonist, situation,
opposition, and stakes. Must be under 35 words.

3.5 Central Conflict
The opposition that generates drama. Declared at three levels: external
(protagonist vs. external force), internal (protagonist vs. self), and
philosophical (idea vs. idea).

3.6 Symbolic Structure
The recurring symbolic logic of the work. Identifies the primary symbols,
their referents, and the rules governing their use.

3.7 Resolution Posture
How the story ends, expressed in tonal and structural terms — not as a plot
summary. Declared as one of: resolved, unresolved, transformed, ambiguous,
tragic, cyclical.

3.8 Motifs
Recurring elements (objects, phrases, images, sounds) that bind the work
together. Each motif is declared with its first appearance, its recurrence
pattern, and its meaning.

4. Inputs

- Research Specification (PKP-03)
- Vision Specification (PKP-00)
- Creative Strategy Specification (PKP-01)

5. Outputs

- A validated Story record in the Production Knowledge Graph
- A materialized Story Specification document
- The dramatic question and theme propagated to the Narrative (PKP-09),
  Character (PKP-06), and Directorial Language (PKP-10) specifications as
  governing intent

6. Schema

```yaml
story:
  document_id: PKP-04
  version: 1.0.0
  premise: <string, 2-4 sentences>
  theme: <string, noun phrase>
  dramatic_question: <string, question form>
  logline: <string, <= 35 words>
  central_conflict:
    external: <string>
    internal: <string>
    philosophical: <string>
  symbolic_structure:
    primary_symbols:
      - symbol: <string>
        referent: <string>
        rules_of_use: [<string>]
  resolution_posture: <resolved|unresolved|transformed|ambiguous|tragic|cyclical>
  resolution_description: <string>
  motifs:
    - id: <string>
      element: <string>
      first_appearance: <string>
      recurrence_pattern: <string>
      meaning: <string>
  research_citations: [<reference to PKP-03 items>]
  provenance:
    source_research: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- premise
- theme
- dramatic_question
- logline
- central_conflict (all three levels)
- resolution_posture
- resolution_description
- motifs (at least one entry)
- provenance.confidence

8. Optional Fields

- symbolic_structure (recommended for any production with symbolic intent)
- research_citations

9. Validation Rules

- S-001: premise must contain a protagonist, a situation, and a source of
  tension. If any is missing, validation fails.
- S-002: theme must be a noun phrase, not a proposition. "The fragility of
  expert certainty" is valid; "Experts should be more humble" is not.
- S-003: dramatic_question must be in question form and must not be answerable
  by a single fact.
- S-004: logline must be a single sentence under 35 words.
- S-005: central_conflict must declare all three levels; a production with no
  internal conflict must declare it as "absent" with justification, not omit
  the field.
- S-006: resolution_posture must be consistent with the audience_transformation
  declared in PKP-00. A production with a tragic resolution may not promise a
  hopeful to-state, and vice versa.
- S-007: Each motif must recur at least twice across the runtime; the
  recurrence_pattern field must describe how.
- S-008: research_citations must reference items that exist in PKP-03.
- S-009: The story must not contradict any non-negotiable principle from
  PKP-00.

10. Dependencies

- PKP-03 — Research Specification (hard)
- PKP-00 — Vision Specification (soft; constrains resolution posture)
- PKP-01 — Creative Strategy Specification (soft; constrains storytelling
  philosophy)

11. Versioning

- MAJOR: Change to premise, dramatic_question, theme, or resolution_posture.
- MINOR: Addition of motifs, refinement of symbolic structure, addition of
  conflict levels.
- PATCH: Wording refinements that do not alter story meaning.

A MAJOR change to Story triggers revalidation of PKP-05, PKP-06, PKP-08, and
PKP-09.

12. Examples

```yaml
story:
  document_id: PKP-04
  version: 1.0.0
  premise: >-
    A respected diagnostician in a municipal hospital observes a symptom that
    cannot be reconciled with any available diagnosis. As she pursues
    verification, the case corrodes the certainty on which her professional
    identity rests.
  theme: "The fragility of expert certainty"
  dramatic_question: "Can a clinician survive the loss of the evidence on which her authority was built?"
  logline: >-
    A physician's authority unravels after a single unverifiable observation
    forces her to choose between professional certainty and intellectual
    honesty.
  central_conflict:
    external: "Protagonist vs. institutional pressure to resolve the case."
    internal: "Protagonist vs. her own need for diagnostic closure."
    philosophical: "Certainty vs. intellectual honesty."
  symbolic_structure:
    primary_symbols:
      - symbol: "The glass partition in the consultation room."
        referent: "The invisible barrier between expert and patient."
        rules_of_use:
          - "Appears in every consultation scene."
          - "Becomes more visually prominent as protagonist's certainty erodes."
  resolution_posture: "ambiguous"
  resolution_description: >-
    The protagonist closes the case without confirming or denying her
    hypothesis. The audience is left inside her uncertainty.
  motifs:
    - id: "MOT-001"
      element: "The unanswered page."
      first_appearance: "Opening sequence."
      recurrence_pattern: "Sounds at the moment of each decision point."
      meaning: "The demand for response that certainty cannot satisfy."
  research_citations: ["RES-001"]
  provenance:
    source_research: "PKP-03 v1.0.0"
    agent: "StoryArchitectAgent"
    session: "sess-003"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for alternative endings (declared as variations, not commitments)
  may be added in a MINOR version.
- A field for thematic counterpoint (the secondary theme the production sets
  against the primary) may be promoted from symbolic_structure.
- Cross-story lineage (for adaptations and sequels) will be modeled as
  Knowledge Graph edges.