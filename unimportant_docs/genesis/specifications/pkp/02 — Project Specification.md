Genesis Foundational Standards (GFS)
PKP-02 — Project Specification

Document ID: PKP-02
Title: Project Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Project Specification defines the production's identity at the manifest
level. It is the canonical record of what the production is as a deliverable —
its title, format, runtime, language, platform, audience, rating, and scope.

This specification is the bridge between creative intent (Vision, Creative
Strategy) and the knowledge specifications that follow. Every downstream
specification must conform to the parameters declared here.

2. Scope

This specification defines:
- The production's title and working title
- Runtime and format
- Language and localization parameters
- Episode or installment identity (for serialized works)
- Target platform and delivery format
- Target audience and age rating
- Deliverables and their acceptance criteria
- Project-level constraints and scope boundaries

Out of scope: creative strategy, story content, character details, technical
production parameters (those live in the Production Blueprint, PKP-15).

3. Contents

3.1 Title and Working Title
The canonical title and any working title used during pre-production. The
canonical title is the one used in all downstream specifications and in the
Knowledge Graph.

3.2 Runtime
The target runtime of the finished production, expressed as a range with a
negotiation envelope. For serialized works, per-episode runtime and total
season runtime.

3.3 Language
Primary language of dialogue, and any secondary languages present in-world.
Declared localization languages are recorded here as intentions, not as
commitments — those live in the Distribution Specification (PKP-16).

3.4 Format
The production format — feature film, short film, limited series, serialized
season, anthology episode, single-shot work, or other.

3.5 Episode Identity
For serialized works: episode number, season number, episode title, and
position within the season arc.

3.6 Platform
The intended primary distribution platform. Declared at the manifest level;
detailed distribution strategy lives in PKP-16.

3.7 Target Audience
The intended audience, expressed as a demographic envelope and a psychographic
profile. The audience transformation declared in PKP-00 must be achievable for
this audience.

3.8 Age Rating
The target age rating and the rating authority under which it is being
declared. Includes content advisories that the production commits to.

3.9 Deliverables
The list of pre-production deliverables that this PKP must produce — the
specifications themselves, plus any required materialized views.

3.10 Constraints
Project-level constraints: budget envelope (declared as a band, not a number),
schedule envelope, legal constraints, and any explicit creative constraints
inherited from PKP-00 and PKP-01.

3.11 Scope
What is in scope and what is explicitly out of scope for this production. Acts
as the boundary for every downstream specification.

4. Inputs

- Vision Specification (PKP-00)
- Creative Strategy Specification (PKP-01)
- Original synopsis and any creator-supplied constraints
- Constitutional Charter (GFS-000)

5. Outputs

- A validated Project record in the Production Knowledge Graph
- A materialized Project Specification document
- Project-level parameters propagated to every downstream specification as
  inherited constraints

6. Schema

```yaml
project:
  document_id: PKP-02
  version: 1.0.0
  title:
    canonical: <string>
    working: <string>
  runtime:
    target_minutes: <integer>
    envelope_minutes: [<integer>, <integer>]
    per_episode: <integer|null>
    season_total: <integer|null>
  language:
    primary: <ISO 639-1 code>
    secondary_in_world: [<ISO 639-1 code>]
    localization_intent: [<ISO 639-1 code>]
  format: <feature|short|limited_series|serialized|anthology|single_shot|other>
  episode_identity:
    season: <integer|null>
    episode: <integer|null>
    episode_title: <string|null>
    arc_position: <string|null>
  platform:
    primary: <string>
    secondary: [<string>]
  target_audience:
    demographic: <string>
    psychographic: <string>
  age_rating:
    target: <string>
    authority: <string>
    content_advisories: [<string>]
  deliverables:
    - name: <string>
      type: <specification|view|manifest|certificate>
      acceptance: <string>
  constraints:
    budget_band: <string|null>
    schedule_envelope: <string|null>
    legal: [<string>]
    inherited_from_vision: [<reference to PKP-00 principles>]
    inherited_from_strategy: [<reference to PKP-01 constraints>]
  scope:
    in_scope: [<string>]
    out_of_scope: [<string>]
  provenance:
    source_vision: <reference>
    source_strategy: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- title.canonical
- runtime.target_minutes
- language.primary
- format
- platform.primary
- target_audience.demographic
- target_audience.psychographic
- age_rating.target
- age_rating.authority
- deliverables (at least one entry)
- scope.in_scope (at least one entry)
- scope.out_of_scope (at least one entry)
- provenance.confidence

8. Optional Fields

- title.working
- runtime.envelope_minutes
- runtime.per_episode and season_total (required for serialized works)
- language.secondary_in_world
- language.localization_intent
- episode_identity (required for serialized works)
- platform.secondary
- constraints.budget_band
- constraints.schedule_envelope
- constraints.legal

9. Validation Rules

- P-001: For serialized format, episode_identity must be fully specified.
- P-002: runtime.target_minutes must fall within runtime.envelope_minutes if
  both are declared.
- P-003: target_audience must be compatible with the audience_transformation
  declared in PKP-00 — the transformation must be achievable for the declared
  audience.
- P-004: age_rating.target must be consistent with content_advisories.
- P-005: deliverables must include at minimum all PKP specifications required
  by the production's format.
- P-006: scope.out_of_scope must not contradict scope.in_scope.
- P-007: No inherited constraint from PKP-00 or PKP-01 may be silently dropped
  in this specification.

10. Dependencies

- PKP-00 — Vision Specification (hard)
- PKP-01 — Creative Strategy Specification (hard)

11. Versioning

- MAJOR: Change to title.canonical, format, runtime.target_minutes, or
  target_audience.
- MINOR: Additions to deliverables, platforms, or scope entries.
- PATCH: Corrections to metadata that do not alter production identity.

A MAJOR change to the Project Specification triggers revalidation of every
downstream specification.

12. Examples

```yaml
project:
  title:
    canonical: "The Unverifiable Case"
    working: "Project Tessera"
  runtime:
    target_minutes: 95
    envelope_minutes: [88, 102]
  language:
    primary: "en"
    secondary_in_world: ["fr"]
    localization_intent: ["fr", "de", "ja"]
  format: "feature"
  platform:
    primary: "theatrical"
    secondary: ["streaming"]
  target_audience:
    demographic: "Adults 30-55, urban, tertiary-educated"
    psychographic: "Viewers who value ambiguity over resolution."
  age_rating:
    target: "R"
    authority: "MPA"
    content_advisories: ["language", "thematic elements"]
  deliverables:
    - name: "Vision Specification"
      type: "specification"
      acceptance: "Certified by Governance Agent."
    - name: "Production Blueprint"
      type: "specification"
      acceptance: "Approved by Studio Engine intake."
  constraints:
    budget_band: "USD 2-4M"
    schedule_envelope: "Pre-production 12 weeks."
    legal: ["Adaptation rights cleared for source essay."]
    inherited_from_vision: ["No on-screen violence shown."]
    inherited_from_strategy: ["No scene longer than seven minutes."]
  scope:
    in_scope:
      - "Single feature film, pre-production knowledge only."
      - "One protagonist, four named characters total."
    out_of_scope:
      - "Sequel planning."
      - "Marketing materials."
      - "Post-production pipeline design."
  provenance:
    source_vision: "PKP-00 v1.0.0"
    source_strategy: "PKP-01 v1.0.0"
    agent: "ProjectArchitectAgent"
    session: "sess-001"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for franchise identity (for works belonging to a shared universe) may
  be added in a MINOR version.
- A field for declared sustainability constraints (carbon budget, location
  limits) may be added when the Production Blueprint (PKP-15) gains a
  sustainability dimension.
- Cross-project linkage fields will be modeled as edges in the Knowledge Graph
  rather than fields in this specification.