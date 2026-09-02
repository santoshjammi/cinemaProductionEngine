Genesis Foundational Standards (GFS)
PKP-06 — Character Specification

Document ID: PKP-06
Title: Character Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Character Specification defines every character in the production. It
captures identity, biography, psychology, motivation, fear, goal, appearance,
voice, dialogue style, emotional arc, and relationships at a per-character
level.

Characters are the load-bearing element of narrative. Every event in the
production must be traceable to a character decision, and every character
decision must be traceable to the fields declared here. A character not present
in this specification may not appear in any downstream specification.

2. Scope

This specification defines, per character:
- Identity (name, role, function, archetype)
- Biography (history that matters to the story)
- Psychology (cognitive and emotional baseline)
- Motivation (what drives the character)
- Fear (what the character cannot face)
- Goal (what the character pursues)
- Appearance (physical presence as designed)
- Voice (vocal and verbal identity)
- Dialogue style (how the character speaks)
- Emotional arc (the trajectory across the runtime)
- Relationships (declared as references to PKP-07)

Out of scope: relationship dynamics in detail (PKP-07), psychological depth
(PKP-08), scene-level behavior (PKP-09).

3. Contents

3.1 Identity
The character's name, narrative role (protagonist, antagonist, foil, witness,
chorus, supporting), dramatic function (what the character does for the
story), and archetype (if any).

3.2 Biography
The history that matters to the story. Not a full life — only the events that
shape the character's presence in the production. Each event is declared with
its weight and its relevance.

3.3 Psychology
The cognitive and emotional baseline of the character. Declared as a set of
traits, each with a source (biographical or dispositional). Detailed
psychology lives in PKP-08; this field captures the working baseline.

3.4 Motivation
What drives the character. Declared at three levels: conscious (what the
character believes they want), unconscious (what they actually seek), and
declared (what they say they want).

3.5 Fear
What the character cannot face. The fear is the inverse of the goal and the
engine of internal conflict.

3.6 Goal
What the character pursues. Declared as external (the surface objective),
internal (the underlying need), and superobjective (the recurring desire across
the production).

3.7 Appearance
The character's physical presence as designed — build, posture, dress logic,
grooming, distinguishing features. Not a casting brief; a design brief.

3.8 Voice
The character's vocal and verbal identity — register, pace, accent, vocabulary
range, characteristic rhythms.

3.9 Dialogue Style
How the character speaks in dramatic situations — directness, ellipsis,
formality, use of silence, characteristic phrases.

3.10 Emotional Arc
The trajectory of the character's internal state across the runtime. Declared
as a sequence of states with transition rules.

3.11 Relationships
References to the Relationship Specification (PKP-07). Each relationship is
declared by id only here; the dynamics live in PKP-07.

4. Inputs

- Story Specification (PKP-04)
- World Specification (PKP-05)
- Research Specification (PKP-03)
- Vision Specification (PKP-00)

5. Outputs

- A validated Character record per character in the Production Knowledge Graph
- A materialized Character Specification document
- Character references propagated to PKP-07 (Relationships), PKP-08
  (Psychology), PKP-09 (Narrative), and PKP-15 (Production Blueprint)

6. Schema

```yaml
characters:
  document_id: PKP-06
  version: 1.0.0
  entries:
    - id: <string>
      identity:
        name: <string>
        role: <protagonist|antagonist|foil|witness|chorus|supporting>
        dramatic_function: <string>
        archetype: <string|null>
      biography:
        - event: <string>
          when: <string>
          weight: <formative|supporting|incidental>
          relevance: <string>
      psychology:
        traits:
          - trait: <string>
            source: <biographical|dispositional>
            expression: <string>
      motivation:
        conscious: <string>
        unconscious: <string>
        declared: <string>
      fear: <string>
      goal:
        external: <string>
        internal: <string>
        superobjective: <string>
      appearance:
        build: <string>
        posture: <string>
        dress_logic: <string>
        grooming: <string>
        distinguishing_features: [<string>]
      voice:
        register: <string>
        pace: <string>
        accent: <string|null>
        vocabulary_range: <string>
        characteristic_rhythms: <string>
      dialogue_style:
        directness: <string>
        ellipsis: <string>
        formality: <string>
        use_of_silence: <string>
        characteristic_phrases: [<string>]
      emotional_arc:
        - phase: <string>
          state: <string>
          transition_rule: <string>
      relationships: [<reference to PKP-07 ids>]
      research_citations: [<reference to PKP-03 items>]
      provenance:
        agent: <string>
        session: <string>
        confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

Per character:
- identity.name, role, dramatic_function
- biography (at least one formative event)
- motivation.conscious and unconscious
- fear
- goal.external and internal
- appearance (build, posture, dress_logic)
- voice (register, pace, vocabulary_range)
- dialogue_style (directness, formality)
- emotional_arc (at least two phases)
- provenance.confidence

8. Optional Fields

- identity.archetype
- biography events with weight "supporting" or "incidental"
- motivation.declared
- goal.superobjective
- appearance.grooming, distinguishing_features
- voice.accent, characteristic_rhythms
- dialogue_style.ellipsis, use_of_silence, characteristic_phrases
- research_citations

9. Validation Rules

- C-001: Every character referenced by PKP-09 (Narrative) must exist here with
  matching id.
- C-002: A production must declare at least one protagonist.
- C-003: No character may be both protagonist and antagonist.
- C-004: motivation.conscious and motivation.unconscious must be distinct; if
  they are identical, the character has no internal conflict and the field
  must be marked.
- C-005: fear must be the inverse of goal.internal — the character fears what
  would deny them their internal need.
- C-006: emotional_arc must form a coherent trajectory; the final state must
  be consistent with the resolution_posture declared in PKP-04.
- C-007: dialogue_style must be consistent with voice; a character with a
  sparse vocabulary may not have verbose characteristic_phrases.
- C-008: relationships must reference entries in PKP-07; no orphan references.
- C-009: No character may violate a non-negotiable principle from PKP-00.
- C-010: For realistic productions, psychology.traits must cite research
  where applicable.

10. Dependencies

- PKP-04 — Story Specification (hard)
- PKP-05 — World Specification (hard)
- PKP-03 — Research Specification (soft)
- PKP-00 — Vision Specification (soft)

11. Versioning

- MAJOR: Removal of a character, change to role, or change to emotional_arc
  final state.
- MINOR: Addition of characters, addition of biography events, refinement of
  traits.
- PATCH: Wording refinements that do not alter character identity.

A MAJOR change to Characters triggers revalidation of PKP-07, PKP-08, PKP-09,
and PKP-15.

12. Examples

```yaml
characters:
  document_id: PKP-06
  version: 1.0.0
  entries:
    - id: "CHR-001"
      identity:
        name: "Dr. Maren Holt"
        role: "protagonist"
        dramatic_function: "Carries the production's examination of uncertainty."
        archetype: "The diagnostician"
      biography:
        - event: "Completed residency under a mentor known for closure."
          when: "Twelve years prior."
          weight: "formative"
          relevance: "Establishes her baseline commitment to diagnostic certainty."
        - event: "Published a paper that was later contested."
          when: "Five years prior."
          weight: "supporting"
          relevance: "Left a residue of professional caution."
      psychology:
        traits:
          - trait: "High need for cognitive closure."
            source: "biographical"
            expression: "Refuses to leave a case open at end of shift."
          - trait: "Suppressed self-doubt."
            source: "dispositional"
            expression: "Reframes uncertainty as laziness in others."
      motivation:
        conscious: "To resolve the case and restore normalcy."
        unconscious: "To test whether her identity survives unresolved certainty."
        declared: "To close the case correctly."
      fear: "That her authority depends on evidence she does not possess."
      goal:
        external: "Resolve the anomalous case."
        internal: "Discover whether her identity can survive uncertainty."
        superobjective: "To remain a person whose judgment can be trusted."
      appearance:
        build: "Tall, narrow-shouldered."
        posture: "Controlled, weight forward when listening."
        dress_logic: "Clinical clothing worn slightly past neatness."
        grooming: "Restrained, deliberate."
        distinguishing_features: ["A single ink stain on the left cuff."]
      voice:
        register: "Mezzo, low placement."
        pace: "Deliberate; accelerates under pressure."
        accent: null
        vocabulary_range: "Clinical precision, plain in private."
        characteristic_rhythms: "Sentence, pause, qualification."
      dialogue_style:
        directness: "High in clinical settings; low in personal ones."
        ellipsis: "Frequent in moments of doubt."
        formality: "Default formal; breaks formality rarely."
        use_of_silence: "Uses silence as a diagnostic instrument."
        characteristic_phrases: ["Let me restate.", "That doesn't fit."]
      emotional_arc:
        - phase: "Opening"
          state: "Practiced certainty."
          transition_rule: "Anomaly introduces first hairline crack."
        - phase: "Middle"
          state: "Active pursuit of closure under mounting doubt."
          transition_rule: "Closure fails to arrive; doubt becomes structural."
        - phase: "Closing"
          state: "Tolerance for unresolved certainty."
          transition_rule: "Protagonist stops seeking resolution."
      relationships: ["REL-001", "REL-002"]
      research_citations: ["RES-001"]
      provenance:
        agent: "CharacterArchitectAgent"
        session: "sess-005"
        confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for character doubles (paired characters who mirror each other) may
  be added as Knowledge Graph edges.
- A field for casting direction (separate from design) may be added when the
  Studio Engine adds a casting layer.
- A field for character voice sampling references (for downstream voice
  synthesis) will be defined in coordination with the Studio Engine, not here.