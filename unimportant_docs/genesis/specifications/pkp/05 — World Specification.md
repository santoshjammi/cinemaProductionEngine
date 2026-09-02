Genesis Foundational Standards (GFS)
PKP-05 — World Specification

Document ID: PKP-05
Title: World Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The World Specification defines the complete universe in which the story takes
place. It establishes the geography, timeline, locations, society, rules,
technology, environment, and culture that govern every event in the production.

The world is the container of the story. Every character action, every scene,
and every line of dialogue must be consistent with the world declared here. If
a downstream specification requires a world element not present in this
specification, the world must be extended before that specification may be
certified.

2. Scope

This specification defines:
- The world's geography (regions, districts, routes, key sites)
- The world's timeline (eras, current period, key historical events)
- The locations the production uses (each a named, described place)
- The society (institutions, hierarchies, norms, tensions)
- The rules (physical, social, metaphysical — what is and is not possible)
- The technology (era, key devices, constraints)
- The environment (climate, light, sound, season)
- The culture (customs, rituals, language registers, taboos)

Out of scope: specific scenes, character psychology, shot language. Those
belong to PKP-09, PKP-08, and PKP-10 respectively.

3. Contents

3.1 Geography
The spatial organization of the world. Declared at three scales: macro
(regions, nations, districts), meso (neighborhoods, routes, boundaries), and
micro (specific sites, buildings, rooms).

3.2 Timeline
The temporal organization of the world. Declared as: eras (long-scale periods),
current period (when the story takes place), and key historical events (events
that shape the present of the story).

3.3 Locations
Each named location the production uses. A location is a place where at least
one scene occurs. Each location declares its function, its sensory signature,
and its narrative role.

3.4 Society
The institutional and social structure of the world. Includes institutions,
hierarchies, social norms, and active social tensions.

3.5 Rules
The laws of the world — physical, social, and metaphysical. A rule declares
what is possible, what is forbidden, and what is contested.

3.6 Technology
The technological era and the specific technologies that matter to the story.
Each technology declares its function, its limits, and its social role.

3.7 Environment
The sensory and climatic baseline of the world — light, weather, season,
ambient sound, air quality. The environment is what the audience sees and
hears when no character is present.

3.8 Culture
The customs, rituals, language registers, and taboos of the world. Culture is
what makes the world feel inhabited rather than staged.

4. Inputs

- Story Specification (PKP-04)
- Research Specification (PKP-03)
- Vision Specification (PKP-00)
- Creative Strategy Specification (PKP-01)

5. Outputs

- A validated World record in the Production Knowledge Graph
- A materialized World Specification document
- A library of locations and rules cited by the Narrative (PKP-09), Production
  Design (PKP-11), and Production Blueprint (PKP-15) specifications

6. Schema

```yaml
world:
  document_id: PKP-05
  version: 1.0.0
  geography:
    macro: [<string>]
    meso: [<string>]
    micro: [<string>]
  timeline:
    eras:
      - name: <string>
        span: <string>
        character: <string>
    current_period: <string>
    key_historical_events:
      - name: <string>
        when: <string>
        significance: <string>
  locations:
    - id: <string>
      name: <string>
      type: <interior|exterior|mixed|virtual>
      function: <string>
      sensory_signature:
        visual: <string>
        sonic: <string>
        olfactory: <string|null>
      narrative_role: <string>
      rules_in_force: [<reference to rules>]
  society:
    institutions: [<string>]
    hierarchies: [<string>]
    norms: [<string>]
    tensions: [<string>]
  rules:
    - id: <string>
      domain: <physical|social|metaphysical>
      statement: <string>
      status: <possible|forbidden|contested>
      justification: <string>
  technology:
    era: <string>
    items:
      - name: <string>
        function: <string>
        limits: <string>
        social_role: <string>
  environment:
    climate: <string>
    season: <string>
    light: <string>
    ambient_sound: <string>
    air_quality: <string|null>
  culture:
    customs: [<string>]
    rituals: [<string>]
    language_registers: [<string>]
    taboos: [<string>]
  research_citations: [<reference to PKP-03 items>]
  provenance:
    source_story: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- geography (at least one entry at one scale)
- timeline.current_period
- locations (at least one entry)
- society (at least one institution and one norm)
- rules (at least one entry)
- environment (climate, season, light, ambient_sound)
- culture (at least one custom or ritual)
- provenance.confidence

8. Optional Fields

- timeline.eras and key_historical_events (required for works with historical
  depth)
- technology.items (required if technology is narratively significant)
- society.tensions
- environment.olfactory and air_quality
- culture.taboos

9. Validation Rules

- W-001: Every location referenced by PKP-09 (Narrative) must exist in
  `locations` with matching id.
- W-002: Every rule referenced by a location must exist in `rules`.
- W-003: No rule may contradict a non-negotiable principle from PKP-00.
- W-004: technology.era must be consistent with timeline.current_period.
- W-005: society.norms must not contradict society.tensions without an
  explicit tension declaration explaining the contradiction.
- W-006: research_citations must reference items that exist in PKP-03.
- W-007: A location's sensory_signature must be consistent with the
  environment baseline; deviations must be justified in the location's
  narrative_role.
- W-008: For realistic productions, rules with status "contested" must cite
  the research basis for the contest.

10. Dependencies

- PKP-04 — Story Specification (hard)
- PKP-03 — Research Specification (hard)
- PKP-00 — Vision Specification (soft)
- PKP-01 — Creative Strategy Specification (soft)

11. Versioning

- MAJOR: Removal of a location, change to a rule's status, or change to
  timeline.current_period.
- MINOR: Addition of locations, rules, social elements, or technologies.
- PATCH: Refinements to descriptions that do not alter world logic.

A MAJOR change to World triggers revalidation of PKP-06, PKP-09, PKP-11, and
PKP-15.

12. Examples

```yaml
world:
  document_id: PKP-05
  version: 1.0.0
  geography:
    macro: ["Single unnamed European-style city."]
    meso: ["Hospital district", "Old town", "Tram-served residential ring."]
    micro: ["Municipal Hospital, fourth-floor consultation wing."]
  timeline:
    eras:
      - name: "Post-reform period"
        span: "Approximately the last decade."
        character: "Institutional modernization under fiscal pressure."
    current_period: "Late autumn of an unspecified recent year."
    key_historical_events:
      - name: "Hospital reform"
        when: "Eight years prior."
        significance: "Established the diagnostic protocol the protagonist serves."
  locations:
    - id: "LOC-001"
      name: "Consultation Room 4B"
      type: "interior"
      function: "Site of diagnostic encounters."
      sensory_signature:
        visual: "Gray-green walls, frosted glass partition, fluorescent light."
        sonic: "Hum of ventilation, distant pages, low voices."
        olfactory: "Disinfectant and stale paper."
      narrative_role: "Where certainty is performed and erodes."
      rules_in_force: ["RUL-001", "RUL-002"]
  society:
    institutions: ["Municipal Hospital", "Diagnostic Board"]
    hierarchies: ["Attending > Resident > Intern"]
    norms: ["Closure within the consultation is expected."]
    tensions: ["Fiscal pressure vs. diagnostic rigor."]
  rules:
    - id: "RUL-001"
      domain: "social"
      statement: "A case may not be closed without a recorded diagnosis."
      status: "contested"
      justification: "Protagonist's case tests the rule's limits."
    - id: "RUL-002"
      domain: "physical"
      statement: "Sound does not carry through the glass partition."
      status: "possible"
      justification: "Establishes the isolation of the consultation."
  technology:
    era: "Contemporary, near-present."
    items:
      - name: "Paging system"
        function: "Audible summons to staff."
        limits: "One-way; cannot be answered."
        social_role: "Embodiment of unanswerable institutional demand."
  environment:
    climate: "Temperate, damp."
    season: "Late autumn."
    light: "Low-angle, overcast, fluorescent interiors."
    ambient_sound: "Distant traffic, ventilation hum, intermittent pages."
  culture:
    customs: ["Staff address each other by surname."]
    rituals: ["Morning handover, formal and timed."]
    language_registers: ["Clinical register in public spaces; informal in private."]
    taboos: ["Discussing uncertainty in front of patients."]
  research_citations: ["RES-002"]
  provenance:
    source_story: "PKP-04 v1.0.0"
    agent: "WorldArchitectAgent"
    session: "sess-004"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for cross-world lineage (shared universes, alternate timelines) may
  be added as Knowledge Graph edges.
- A field for environmental change across the runtime (seasonal shift, light
  progression) may be added in a MINOR version.
- A field for declared worldbuilding anti-patterns (what the world refuses to
  contain) may be promoted from rules in a future version.