Genesis Foundational Standards (GFS)
PKP-12 — Audio Intent Specification

Document ID: PKP-12
Title: Audio Intent Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Audio Intent Specification defines the sonic identity of the production.
It captures voice style, narration philosophy, dialogue style, music intent,
silence, sound design, and emotional audio.

This specification translates narrative structure into a coherent sonic
language. It does not specify recordings, mixes, or scores — those belong to
the Production Blueprint (PKP-15) and downstream Studio Engine specifications.
It specifies the *intent* from which sonic production decisions are derived.

2. Scope

This specification defines:
- Voice style (the production's approach to the spoken voice)
- Narration philosophy (whether and how narration is used)
- Dialogue style (the production's approach to dialogue)
- Music intent (the philosophy of music use, not the score itself)
- Silence (the production's use of silence as a sonic element)
- Sound design (the philosophy of designed sound)
- Emotional audio (the engineered sonic progression of audience emotion)

Out of scope: scene structure (PKP-09), score composition, mix specifications,
voice casting. Those belong to PKP-15 and downstream Studio Engine
specifications.

3. Contents

3.1 Voice Style
The production's approach to the spoken voice — register, breath, proximity,
the relation of voice to body. Declared as a set of principles.

3.2 Narration Philosophy
Whether and how narration is used. Declared as one of: absent, external,
internal, ambiguous. If present, declares the narrator, the tense, and the
relation to the story's temporal present.

3.3 Dialogue Style
The production's approach to dialogue — density, overlap, ellipsis, the
relation of speech to action. Declared as a set of principles.

3.4 Music Intent
The philosophy of music use — when music is permitted, when it is refused,
what music may and may not do. Declared as a set of permissions and refusals.

3.5 Silence
The production's use of silence as a sonic element. Declared as a set of
principles for when silence is used and what it signifies.

3.6 Sound Design
The philosophy of designed sound — realism, abstraction, hyperrealism,
withholding. Declared with its principles and its refusal.

3.7 Emotional Audio
The engineered sonic progression of audience emotion across the runtime.
Declared as a sequence of phases, each with a sonic character and a transition
rule.

4. Inputs

- Narrative Specification (PKP-09)
- Creative Strategy Specification (PKP-01)
- Vision Specification (PKP-00)
- Directorial Language Specification (PKP-10)

5. Outputs

- A validated Audio Intent record in the Production Knowledge Graph
- A materialized Audio Intent Specification document
- Audio principles propagated to PKP-15 (Production Blueprint)

6. Schema

```yaml
audio_intent:
  document_id: PKP-12
  version: 1.0.0
  voice_style:
    - principle: <string>
      expression: <string>
  narration_philosophy:
    mode: <absent|external|internal|ambiguous>
    narrator: <reference to PKP-06|null>
    tense: <present|past|other|null>
    relation_to_present: <string|null>
  dialogue_style:
    - principle: <string>
      expression: <string>
  music_intent:
    permissions: [<string>]
    refusals: [<string>]
    when_permitted: <string>
  silence:
    - principle: <string>
      expression: <string>
  sound_design:
    philosophy: <realism|abstraction|hyperrealism|withholding>
    principles: [<string>]
    refusal: [<string>]
  emotional_audio:
    - phase: <string>
      sonic_character: <string>
      transition_rule: <string>
  provenance:
    source_narrative: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- voice_style (at least one principle)
- narration_philosophy.mode (required; if mode is "absent", other narration
  fields are null)
- dialogue_style (at least one principle)
- music_intent (permissions, refusals, and when_permitted)
- silence (at least one principle)
- sound_design (philosophy and principles)
- emotional_audio (at least two phases)
- provenance.confidence

8. Optional Fields

- narration_philosophy.narrator, tense, relation_to_present (required if mode
  is not "absent")
- sound_design.refusal (recommended)

9. Validation Rules

- AI-001: voice_style must be consistent with the dialogue_style of the
  protagonist in PKP-06.
- AI-002: narration_philosophy.mode must be consistent with the
  storytelling_philosophy in PKP-01. A philosophy of "subjectivity is the only
  available frame" permits internal narration but forbids external omniscient
  narration.
- AI-003: If narration_philosophy.narrator is declared, it must reference a
  character in PKP-06.
- AI-004: music_intent.refusals must not contradict a creative_constraint from
  PKP-01 (e.g., a constraint that "music never tells the audience how to feel"
  implies a refusal of emotional scoring).
- AI-005: silence principles must be consistent with the pacing in PKP-09.
- AI-006: sound_design.philosophy must be consistent with the
  camera_philosophy in PKP-10. A camera that observes pairs with sound that
  observes; a camera that withholds pairs with sound that withholds.
- AI-007: emotional_audio must be consistent with the emotional_strategy in
  PKP-01 and the emotional_rhythm in PKP-09.
- AI-008: No audio principle may violate a non-negotiable principle from
  PKP-00.

10. Dependencies

- PKP-09 — Narrative Specification (hard)
- PKP-01 — Creative Strategy Specification (hard)
- PKP-00 — Vision Specification (soft)
- PKP-10 — Directorial Language Specification (soft)

11. Versioning

- MAJOR: Change to narration_philosophy.mode, music_intent.permissions, or
  sound_design.philosophy.
- MINOR: Additions to voice_style, dialogue_style, silence, or
  emotional_audio.
- PATCH: Wording refinements that do not alter audio intent.

A MAJOR change to Audio Intent triggers revalidation of PKP-15.

12. Examples

```yaml
audio_intent:
  document_id: PKP-12
  version: 1.0.0
  voice_style:
    - principle: "Voices are mixed low; the audience must lean in."
      expression: "Dialogue peaks below reference; ambient sound foregrounded."
    - principle: "Breath is audible."
      expression: "No noise reduction that removes breath; breath is part of speech."
  narration_philosophy:
    mode: "absent"
    narrator: null
    tense: null
    relation_to_present: null
  dialogue_style:
    - principle: "Dialogue is sparse; silence is the default."
      expression: "Long stretches of any scene contain no speech."
    - principle: "Overlap is forbidden."
      expression: "Characters do not interrupt; they wait, or they leave."
  music_intent:
    permissions:
      - "Music permitted only at act boundaries."
      - "Music permitted only diegetically (e.g., a radio in a scene)."
    refusals:
      - "No music under dialogue."
      - "No music under moments of decision."
      - "No emotional scoring."
    when_permitted: "Act transitions and the closing shot only."
  silence:
    - principle: "Silence is the default sonic state."
      expression: "Ambient room tone counts as silence."
    - principle: "Silence expands as certainty erodes."
      expression: "Scene silences lengthen across the runtime."
  sound_design:
    philosophy: "withholding"
    principles:
      - "Sound sources visible in frame where possible."
      - "Off-screen sound is rare and must be justified."
      - "Foley is restrained; only what the protagonist would notice."
    refusal:
      - "No designed stings at moments of revelation."
      - "No sound that the protagonist does not hear."
  emotional_audio:
    - phase: "Establishment"
      sonic_character: "Low ambient hum, sparse dialogue, no music."
      transition_rule: "Anomaly introduces a single unfamiliar sound."
    - phase: "Erosion"
      sonic_character: "Silences lengthen; ambient detail sharpens."
      transition_rule: "Music remains absent; silence becomes structural."
    - phase: "Settling"
      sonic_character: "Silence accepted as the sonic baseline."
      transition_rule: "Closing shot permits the only non-diegetic music."
  provenance:
    source_narrative: "PKP-09 v1.0.0"
    agent: "AudioIntentArchitectAgent"
    session: "sess-011"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for spatial audio intent (3D sound positioning) may be added when
  the Distribution Specification (PKP-16) supports spatial formats.
- A field for cross-production audio lineage (shared sonic identities across
  a series) will be modeled as Knowledge Graph edges.
- A field for declared audio anti-patterns (what the audio refuses to do) may
  be promoted from music_intent.refusals and sound_design.refusal in a future
  version.