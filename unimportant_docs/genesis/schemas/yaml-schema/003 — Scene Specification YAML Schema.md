Genesis Schema Specification (GSS)
GSS-103 — Scene Specification YAML Schema

Document ID: GSS-103
Title: Scene Specification YAML Schema
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010, GSS-001, GO-106

1. Purpose

This Schema defines the YAML serialization format for Scene Specifications.
A Scene Specification is a medium-independent blueprint of one dramatic unit:
its dramatic goal, participants, location, conflict, beats, and resulting
knowledge deltas. It does not contain camera, blocking, or rendering detail —
those belong to the Studio Engine.

2. When to Use

- When a narrative agent proposes a scene to insert into the PKG
- When materializing a scene from the PKG for review
- When validating scene-level consistency against character DNA and world rules

3. Top-Level Structure

```yaml
scene:
  id: "urn:genesis:scene:<uuid>"         # required, stable
  version: "1.0.0"                        # semver, required
  status: draft | reviewed | approved
  production_id: "urn:genesis:prod:<uuid>"
  sequence_id: "urn:genesis:sequence:<uuid>"  # parent sequence
  ordinal: 7                              # position within sequence
  title: "The Council of Doubt"
  slug: "council_of_doubt"
  scene_type: confrontation | revelation | decision | transition | setup | payoff | montage
  duration_seconds: 180                   # estimated runtime target
```

4. Dramatic Goal Block

```yaml
dramatic_goal:
  want: "Arjuna asks Krishna whether to fight."
  need: "Arjuna must confront the cost of refusal."
  stakes: "If unresolved, the war ends before it begins."
  question: "Is inaction ever morally superior to action?"
  change: "Arjuna moves from paralysis to receptivity."
```

5. Participants Block

```yaml
participants:
  - character_id: "urn:genesis:character:<arjuna-uuid>"
    role_in_scene: focal | present | referenced | offscreen
    pov: true
    state_on_entry: "collapsed in grief"
    state_on_exit: "still, listening"
  - character_id: "urn:genesis:character:<krishna-uuid>"
    role_in_scene: present
    state_on_entry: "calm, attentive"
    state_on_exit: "teaching"
```

6. Setting Block

Setting references the World Ontology (GO-105) and is intentionally
presentation-neutral.

```yaml
setting:
  location_id: "urn:genesis:location:<uuid>"
  location_name: "Kurukshetra battlefield, between the armies"
  time_of_day: "dawn"
  time_in_story: "minutes before battle"
  weather: "still, grey"
  atmosphere: "suspended, sacred, dread"
  world_rules_applied:
    - "urn:genesis:rule:<dharma-rule-uuid>"
```

7. Conflict Block

```yaml
conflict:
  type: internal | interpersonal | societal | cosmic
  axis: "duty vs. self-preservation"
  parties:
    - "urn:genesis:character:<arjuna-uuid>"
    - "urn:genesis:character:<krishna-uuid>"   # as interlocutor, not opponent
  manifestation: "verbal: argument collapses into surrender"
```

8. Beats Block

A beat is the smallest narrative unit inside a scene. Each beat carries its
own micro-change.

```yaml
beats:
  - ordinal: 1
    type: action | dialogue | reaction | silence | revelation | decision
    summary: "Arjuna drops his bow."
    characters: ["<arjuna-uuid>"]
    knowledge_delta:
      added:
        - node_id: "urn:genesis:state:<uuid>"
          type: EmotionalState
          attrs: { emotion: "despair", intensity: 0.9 }
      updated: []
      removed: []
  - ordinal: 2
    type: dialogue
    summary: "Arjuna declares he will not fight."
    characters: ["<arjuna-uuid>"]
    knowledge_delta: { added: [], updated: [], removed: [] }
```

9. Knowledge Delta Block

Every scene MUST produce a non-empty `knowledge_delta` at the scene level,
aggregated from beats. This enforces the constitutional invariant that every
specification must emerge from validated knowledge (GFS-000 §6).

```yaml
knowledge_delta:
  added: [...]
  updated: [...]
  removed: [...]
  relationships:
    - from: "urn:genesis:character:<arjuna-uuid>"
      to: "urn:genesis:character:<krishna-uuid>"
      predicate: "urn:genesis:rel:seeks_guidance_from"
      confidence: 0.92
```

10. Validation Rules

- `scene.id` MUST be a valid URN
- `participants` MUST contain at least one entry with `role_in_scene: focal`
- `beats` MUST be non-empty
- Every beat MUST have a `summary` and `type`
- Aggregated `knowledge_delta` MUST be non-empty
- Every `participants[*].character_id` MUST resolve to a Character DNA (GSS-102)
- `setting.location_id` MUST resolve to a World node (GO-105)

11. Provenance Block

```yaml
provenance:
  source: inferred | confirmed | explicit
  confidence: 0.0 - 1.0
  origin:
    agent: "urn:genesis:agent:narrative-architect"
    session: "urn:genesis:session:<uuid>"
    decision_id: "urn:genesis:decision:<uuid>"
  evidence:
    - "GO-106 §4: Event requires cause and consequence."
    - "Character DNA Arjuna: wound = betrayal by trusted teacher."
```

12. Tooling

```bash
genesis validate scene --schema gss-103 --input scene.yaml
genesis materialize scene --pkg <pkg-id> --id <scene-urn>
genesis validate scene --pkg <pkg-id> --id <scene-urn> --check consistency
```

13. Relationship to Other Schemas

- Inherits vocabulary from GO-106 (Event, Action & Causality Ontology)
- Consumes GSS-102 (Character DNA) for participants
- Consumes GO-105 (World & Environment Ontology) for setting
- Serialized into GSS-001 (PKG JSON Schema) nodes and edges

14. Revision History

- 1.0.0 — Initial draft. Derived from GO-106 v1.0.0.