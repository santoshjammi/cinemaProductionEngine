Genesis Foundational Standards (GFS)
PKP-08 — Psychology Specification

Document ID: PKP-08
Title: Psychology Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Psychology Specification defines the psychological depth of every
character. It captures attachment styles, defense mechanisms, trauma,
cognitive biases, emotional triggers, behavioral patterns, and transformation
posture.

Where the Character Specification (PKP-06) defines *who* a character is and the
Relationship Specification (PKP-07) defines *how they connect*, this
specification defines *why they behave as they do* at the level of psychological
mechanism. It is the layer that makes character behavior legible and
predictable to every downstream agent.

2. Scope

This specification defines, per character:
- Attachment style (secure, anxious, avoidant, disorganized)
- Defense mechanisms (the recurring psychological protections the character
  employs)
- Trauma (formative psychological wounds, declared with their origin and
  expression)
- Cognitive biases (the systematic distortions in the character's reasoning)
- Emotional triggers (stimuli that produce disproportionate responses)
- Behavioral patterns (recurring behaviors and their psychological drivers)
- Transformation posture (how the character changes across the runtime, in
  psychological terms)

Out of scope: biographical events (PKP-06), relationship dynamics (PKP-07),
scene-level behavior (PKP-09).

3. Contents

3.1 Attachment Style
The character's baseline attachment pattern, declared per relationship type
(intimate, professional, institutional) when they differ. Each declaration
includes the behavioral expression and the biographical source.

3.2 Defense Mechanisms
The recurring psychological protections the character employs. Each mechanism
is declared with its type (e.g., intellectualization, projection,
displacement, rationalization, suppression), its trigger, and its behavioral
signature.

3.3 Trauma
Formative psychological wounds. Each trauma is declared with its origin, its
expression (how it manifests in the present), its activation (what stirs it),
and its resolution posture (unresolved, integrated, denied, being worked).

3.4 Cognitive Biases
The systematic distortions in the character's reasoning. Each bias is declared
with its type, its expression, and its consequence for the character's
decisions.

3.5 Emotional Triggers
Stimuli that produce disproportionate responses. Each trigger is declared
with its stimulus, the response it produces, and the underlying
vulnerability.

3.6 Behavioral Patterns
Recurring behaviors and their psychological drivers. Each pattern is declared
with the behavior, the driver, the cue, and the payoff.

3.7 Transformation Posture
How the character changes across the runtime, in psychological terms. Declared
as a sequence of states with the psychological mechanism that drives each
transition.

4. Inputs

- Character Specification (PKP-06)
- Relationship Specification (PKP-07)
- Research Specification (PKP-03)
- Story Specification (PKP-04)

5. Outputs

- A validated Psychology record per character in the Production Knowledge Graph
- A materialized Psychology Specification document
- Psychological references propagated to PKP-09 (Narrative) and PKP-15
  (Production Blueprint)

6. Schema

```yaml
psychology:
  document_id: PKP-08
  version: 1.0.0
  entries:
    - character_id: <reference to PKP-06>
      attachment_style:
        - context: <intimate|professional|institutional>
          style: <secure|anxious|avoidant|disorganized>
          expression: <string>
          source: <string>
      defense_mechanisms:
        - type: <intellectualization|projection|displacement|rationalization|suppression|denial|sublimation|other>
          trigger: <string>
          behavioral_signature: <string>
      trauma:
        - id: <string>
          origin: <string>
          expression: <string>
          activation: <string>
          resolution_posture: <unresolved|integrated|denied|being_worked>
      cognitive_biases:
        - type: <string>
          expression: <string>
          consequence: <string>
      emotional_triggers:
        - stimulus: <string>
          response: <string>
          underlying_vulnerability: <string>
      behavioral_patterns:
        - behavior: <string>
          driver: <string>
          cue: <string>
          payoff: <string>
      transformation_posture:
        - phase: <string>
          psychological_state: <string>
          transition_mechanism: <string>
      research_citations: [<reference to PKP-03 items>]
      provenance:
        agent: <string>
        session: <string>
        confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

Per character:
- character_id
- attachment_style (at least one context)
- defense_mechanisms (at least one)
- trauma (the field is required; may be empty if no formative trauma exists,
  with justification)
- cognitive_biases (at least one)
- emotional_triggers (at least one)
- behavioral_patterns (at least one)
- transformation_posture (at least two phases)
- provenance.confidence

8. Optional Fields

- research_citations (required for realistic productions drawing on
  established psychology)
- Multiple attachment_style contexts (required if the character's attachment
  differs across contexts)

9. Validation Rules

- PSY-001: character_id must reference a character in PKP-06.
- PSY-002: attachment_style.style must be one of the four declared values.
- PSY-003: defense_mechanisms.type must be a recognized mechanism;
  non-standard mechanisms must be defined in notes.
- PSY-004: trauma.resolution_posture must be consistent with the character's
  emotional_arc in PKP-06. A character whose arc ends in tolerance may not
  have all trauma marked "integrated" without justification.
- PSY-005: cognitive_biases.consequence must be observable in at least one
  decision the character makes in PKP-09.
- PSY-006: emotional_triggers.stimulus must be a concrete, scannable element
  (a phrase, a sound, a gesture, a situation), not an abstract condition.
- PSY-007: behavioral_patterns.payoff must be psychological, not material —
  the pattern persists because it serves the character's psyche, not their
  interests.
- PSY-008: transformation_posture must be consistent with the character's
  emotional_arc in PKP-06.
- PSY-009: research_citations must reference items in PKP-03.
- PSY-010: No psychological declaration may violate a non-negotiable principle
  from PKP-00 (e.g., a principle forbidding the romanticization of trauma
  would constrain how trauma is presented).

10. Dependencies

- PKP-06 — Character Specification (hard)
- PKP-07 — Relationship Specification (hard)
- PKP-03 — Research Specification (soft)
- PKP-04 — Story Specification (soft)

11. Versioning

- MAJOR: Removal of a character's psychology, change to attachment_style, or
  change to transformation_posture final state.
- MINOR: Addition of mechanisms, traumas, biases, or patterns.
- PATCH: Wording refinements that do not alter psychological logic.

A MAJOR change to Psychology triggers revalidation of PKP-09 and PKP-15.

12. Examples

```yaml
psychology:
  document_id: PKP-08
  version: 1.0.0
  entries:
    - character_id: "CHR-001"
      attachment_style:
        - context: "professional"
          style: "avoidant"
          expression: "Maintains distance through formality; refuses collegial warmth."
          source: "Residency under a mentor who treated uncertainty as weakness."
        - context: "institutional"
          style: "anxious"
          expression: "Over-checks records, anticipates audit."
          source: "Contested paper five years prior."
      defense_mechanisms:
        - type: "intellectualization"
          trigger: "Emotional content in a clinical encounter."
          behavioral_signature: "Reframes affect as a diagnostic feature."
        - type: "suppression"
          trigger: "Personal questions from colleagues."
          behavioral_signature: "Acknowledges the question, then redirects to work."
      trauma:
        - id: "TRM-001"
          origin: "Public contestation of her paper five years ago."
          expression: "Excessive documentation; reluctance to publish."
          activation: "Requests for diagnostic opinion in writing."
          resolution_posture: "being_worked"
      cognitive_biases:
        - type: "Anchor bias on first observation."
          expression: "Treats the first symptom as the case's true center."
          consequence: "Pursues verification of the anomaly past the point of utility."
      emotional_triggers:
        - stimulus: "The phrase 'just close it out'."
          response: "Withdraws from the conversation for the rest of the shift."
          underlying_vulnerability: "Fear that closure is a form of dishonesty."
      behavioral_patterns:
        - behavior: "Re-reads patient notes after every consultation."
          driver: "Need to confirm she has not missed evidence."
          cue: "End of shift."
          payoff: "Temporary relief from dread of error."
      transformation_posture:
        - phase: "Opening"
          psychological_state: "Suppression of doubt under professional armor."
          transition_mechanism: "Anomaly cannot be suppressed by routine."
        - phase: "Middle"
          psychological_state: "Intellectualization fails; raw doubt surfaces."
          transition_mechanism: "Verification attempts exhaust without producing closure."
        - phase: "Closing"
          psychological_state: "Tentative tolerance of unresolved cognitive state."
          transition_mechanism: "Protagonist stops seeking closure; the armor relaxes."
      research_citations: ["RES-001"]
      provenance:
        agent: "PsychologyArchitectAgent"
        session: "sess-007"
        confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for clinical diagnosis (in-world, not of the character) may be added
  when the production requires it, with strict separation from real-world
  diagnostic claims.
- A field for group psychology (collective dynamics of an ensemble) may be
  added as Knowledge Graph hyperedges.
- A field for psychological assessment provenance (which expert reviewed the
  characterization) may be added when expert review becomes a first-class
  workflow.