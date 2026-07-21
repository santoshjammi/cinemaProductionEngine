Genesis Schema Specification (GSS)
GSS-102 — Character DNA YAML Schema

Document ID: GSS-102
Title: Character DNA YAML Schema
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010, GSS-001, GO-104

1. Purpose

This Schema defines the YAML serialization format for Character DNA — the
atomic, transferable definition of a character used across the Production
Knowledge Graph. Character DNA captures the immutable psychological and
narrative core of a character; performance, voice, and appearance are derived
downstream and are out of scope here.

2. When to Use

- When a discovery agent materializes a character node into a portable file
- When a creator pre-seeds a character for a production brief
- When characters are exchanged between productions as archetypes

3. Top-Level Structure

```yaml
character:
  id: "urn:genesis:character:<uuid>"     # required, stable
  version: "1.0.0"                        # semver, required
  status: draft | reviewed | approved
  canonical_name: "Arjuna"                # required, immutable
  display_name: "Arjuna"
  aliases:
    - "Partha"
    - "The Reluctant Warrior"
  archetype: "reluctant_hero"              # controlled vocabulary
  role_in_story: protagonist | antagonist | mentor | ally | foil | side | ensemble
```

4. Identity Block

```yaml
identity:
  species: human | animal | mythological | organization | ai | symbolic
  age_band: child | youth | adult | middle | elder | ageless
  gender: any controlled value or "unspecified"
  cultural_origin: "Vedic North India"
  occupation: "warrior prince"
  social_class: "kshatriya"
```

5. Psychology Block

Per GO-103 (Human Psychology & Behavior Ontology) and GO-104 (Character
Ontology), psychology is the engine of behavior.

```yaml
psychology:
  core_motivation: "To live up to dharma without losing himself."
  conscious_goal: "Win the war justly."
  unconscious_need: "Permission to refuse."
  fear: "Becoming what he hates."
  belief: "Duty overrides feeling."
  values:
    - dharma
    - loyalty
    - mercy
  shadow: "The part of him that wants to walk away."
  mbti_hint: "INFJ"  # advisory only, not canonical
  big_five:
    openness: 0.78
    conscientiousness: 0.82
    extraversion: 0.45
    agreeableness: 0.60
    neuroticism: 0.55
```

6. Narrative Block

```yaml
narrative:
  arc: "reluctance → acceptance → transformation"
  wound: "Betrayal by a teacher he trusted."
  ghost: "Brother died in his arms."
  want: "To be excused from killing kin."
  need: "To accept responsibility for the unavoidable."
  lie_believed: "I can remain untouched by my choices."
  truth_to_learn: "Action is unavoidable; detached action is freedom."
  transformation: "despair → clarity → committed action"
```

7. Relationships Block

```yaml
relationships:
  - to: "urn:genesis:character:<krishna-uuid>"
    type: mentor | ally | foil | antagonist | family | rival
    dynamic: "spiritual guide"
    tension: "high"
  - to: "urn:genesis:character:<duryodhana-uuid>"
    type: antagonist
    dynamic: "fraternal enemy"
    tension: "extreme"
```

8. Behavior Block

```yaml
behavior:
  speech_pattern: "formal, deliberate, questioning"
  gesture: "stillness before action"
  default_strategy: "deliberation then decisive act"
  stress_response: "paralysis followed by revelation-seeking"
  conflict_style: avoid | accommodate | compete | compromise | collaborate
```

9. Provenance Block

```yaml
provenance:
  source: explicit | inferred | confirmed | assumed | unknown
  confidence: 0.0 - 1.0
  origin:
    agent: "urn:genesis:agent:character-architect"
    session: "urn:genesis:session:<uuid>"
    decision_id: "urn:genesis:decision:<uuid>"
  evidence:
    - "Brief line 14: 'reluctant warrior'"
    - "GO-104 §6: Character wound archetype"
```

10. Validation Rules

- `character.id` MUST be a valid URN
- `psychology.core_motivation` MUST be non-empty
- `narrative.want` and `narrative.need` MUST be distinct strings
- `relationships[*].to` MUST resolve to a known character URN
- `provenance.confidence` MUST be in [0, 1]
- `archetype` and `role_in_story` MUST come from controlled vocabularies

11. Tooling

```bash
genesis validate character --schema gss-102 --input arjuna.yaml
genesis materialize character --pkg <pkg-id> --id <character-urn>
```

12. Relationship to Other Schemas

- Inherits vocabulary from GO-104 and GO-103
- Links to GSS-001 (PKG JSON Schema) via `character.id`
- Consumed by GSS-103 (Scene Specification YAML Schema) through relationships

13. Revision History

- 1.0.0 — Initial draft. Derived from GO-104 v1.0.0.