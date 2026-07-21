Genesis Foundational Standards (GFS)
PKP-07 — Relationship Specification

Document ID: PKP-07
Title: Relationship Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Relationship Specification defines the interpersonal dynamics between every
pair of characters in the production. It captures emotional connection, trust,
power, conflict, history, hidden motivation, dependency, and evolution.

A production is not a collection of characters; it is a network of
relationships. This specification makes that network explicit, versioned, and
validatable. Every scene in the production must be consistent with the
relationships declared here.

2. Scope

This specification defines, per relationship (character pair):
- The emotional connection between the two characters
- The trust level and its direction
- The power balance and its source
- The active conflict between them
- The shared history that shapes the present
- The hidden motivations each character holds toward the other
- The dependency (asymmetric or symmetric) between them
- The evolution of the relationship across the runtime

Out of scope: individual character psychology (PKP-06, PKP-08), scene-level
behavior (PKP-09).

3. Contents

3.1 Emotional Connection
The affective bond between the two characters — affection, resentment,
indifference, fascination, obligation. Declared per direction (A toward B, B
toward A) when asymmetric.

3.2 Trust
The trust level between the characters, declared per direction on a four-tier
scale: HIGH, CONDITIONAL, LOW, BROKEN. Includes the basis for the trust level.

3.3 Power
The power balance between the characters, declared per direction on a four-tier
scale: DOMINANT, EQUAL, SUBORDINATE, CONTESTED. Includes the source of power
(institutional, personal, informational, moral).

3.4 Conflict
The active tension between the characters. Each conflict is declared with its
surface (what they argue about) and its underlying (what the argument is
really about).

3.5 History
The shared events that shape the present relationship. Each event is declared
with its weight and its present effect.

3.6 Hidden Motivation
What each character wants from the other that they have not declared. May be
empty for transparent relationships.

3.7 Dependency
The structural reliance between the characters — professional, emotional,
informational, moral. Declared per direction and as symmetric or asymmetric.

3.8 Evolution
The trajectory of the relationship across the runtime. Declared as a sequence
of states with transition rules.

4. Inputs

- Character Specification (PKP-06)
- Story Specification (PKP-04)
- World Specification (PKP-05)

5. Outputs

- A validated Relationship record per character pair in the Production
  Knowledge Graph
- A materialized Relationship Specification document
- Relationship references propagated to PKP-08 (Psychology), PKP-09
  (Narrative), and PKP-15 (Production Blueprint)

6. Schema

```yaml
relationships:
  document_id: PKP-07
  version: 1.0.0
  entries:
    - id: <string>
      parties:
        a: <reference to PKP-06 character id>
        b: <reference to PKP-06 character id>
      type: <professional|familial|romantic|adversarial|mentorship|stranger|other>
      emotional_connection:
        a_to_b: <string>
        b_to_a: <string>
      trust:
        a_to_b: <HIGH|CONDITIONAL|LOW|BROKEN>
        b_to_a: <HIGH|CONDITIONAL|LOW|BROKEN>
        basis: <string>
      power:
        a_to_b: <DOMINANT|EQUAL|SUBORDINATE|CONTESTED>
        b_to_a: <DOMINANT|EQUAL|SUBORDINATE|CONTESTED>
        source: <institutional|personal|informational|moral|other>
      conflict:
        surface: <string>
        underlying: <string>
      history:
        - event: <string>
          when: <string>
          weight: <formative|supporting|incidental>
          present_effect: <string>
      hidden_motivation:
        a_toward_b: <string|null>
        b_toward_a: <string|null>
      dependency:
        a_on_b: <professional|emotional|informational|moral|none>
        b_on_a: <professional|emotional|informational|moral|none>
        symmetry: <symmetric|asymmetric>
      evolution:
        - phase: <string>
          state: <string>
          transition_rule: <string>
      provenance:
        agent: <string>
        session: <string>
        confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

Per relationship:
- id
- parties.a and parties.b
- type
- emotional_connection (both directions)
- trust (both directions, with basis)
- power (both directions, with source)
- conflict (surface and underlying)
- evolution (at least two phases)
- provenance.confidence

8. Optional Fields

- history (recommended; required if the relationship has formative prior events)
- hidden_motivation (may be null for transparent relationships)
- dependency (recommended)

9. Validation Rules

- REL-001: parties.a and parties.b must reference characters that exist in
  PKP-06.
- REL-002: A relationship must not be declared between a character and
  themselves.
- REL-003: No duplicate relationships between the same pair — each pair has
  exactly one entry.
- REL-004: trust and power must be declared in both directions; symmetry is
  permitted but not assumed.
- REL-005: conflict.underlying must not be identical to conflict.surface; if
  they are identical, the conflict has no subtext and the field must be marked.
- REL-006: evolution must form a coherent trajectory consistent with the
  emotional arcs of both characters in PKP-06.
- REL-007: dependency.symmetry must match the directional declarations; if
  a_on_b and b_on_a are both "none", symmetry must be "symmetric".
- REL-008: No relationship may violate a non-negotiable principle from PKP-00.
- REL-009: For each relationship referenced by a scene in PKP-09, the
  relationship's evolution phase at that point in the runtime must be
  consistent with the scene's emotional state.

10. Dependencies

- PKP-06 — Character Specification (hard)
- PKP-04 — Story Specification (soft)
- PKP-05 — World Specification (soft)

11. Versioning

- MAJOR: Removal of a relationship, change to type, or change to evolution
  final state.
- MINOR: Addition of relationships, addition of history events, refinement of
  trust or power levels.
- PATCH: Wording refinements that do not alter relationship dynamics.

A MAJOR change to Relationships triggers revalidation of PKP-08, PKP-09, and
PKP-15.

12. Examples

```yaml
relationships:
  document_id: PKP-07
  version: 1.0.0
  entries:
    - id: "REL-001"
      parties:
        a: "CHR-001"
        b: "CHR-002"
      type: "professional"
      emotional_connection:
        a_to_b: "Respect tempered by weariness."
        b_to_a: "Affectionate deference shading into concern."
      trust:
        a_to_b: "CONDITIONAL"
        b_to_a: "HIGH"
        basis: "Years of shared shifts; Holt's recent withdrawal has eroded her trust in him."
      power:
        a_to_b: "DOMINANT"
        b_to_a: "SUBORDINATE"
        source: "institutional"
      conflict:
        surface: "Whether to escalate the anomalous case."
        underlying: "Whether certainty is a duty or a luxury."
      history:
        - event: "Worked same floor for six years."
          when: "Ongoing."
          weight: "formative"
          present_effect: "Familiarity that permits abbreviation in speech."
        - event: "Lindgren covered for Holt during her contested paper."
          when: "Five years prior."
          weight: "formative"
          present_effect: "Asymmetric loyalty; Lindgren expects reciprocity."
      hidden_motivation:
        a_toward_b: "To be allowed to fail without being rescued."
        b_toward_a: "To preserve the version of Holt he has always relied on."
      dependency:
        a_on_b: "professional"
        b_on_a: "emotional"
        symmetry: "asymmetric"
      evolution:
        - phase: "Opening"
          state: "Working familiarity."
          transition_rule: "Holt's withdrawal introduces first strain."
        - phase: "Middle"
          state: "Lindgren attempts rescue; Holt refuses."
          transition_rule: "Refusal reveals the asymmetry of the dependency."
        - phase: "Closing"
          state: "Functional distance without rupture."
          transition_rule: "Both accept the new shape of the relationship."
      provenance:
        agent: "RelationshipArchitectAgent"
        session: "sess-006"
        confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for triadic relationships (A through B toward C) may be added as
  Knowledge Graph hyperedges.
- A field for relationship external witnesses (characters whose presence
  alters a relationship) may be added in a MINOR version.
- A field for declared relationship anti-patterns (what the relationship
  refuses to become) may be promoted from evolution in a future version.