Genesis Foundational Standards (GFS)
PKP-11 — Production Design Specification

Document ID: PKP-11
Title: Production Design Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Production Design Specification defines the physical production: the
architecture, props, wardrobe, costumes, set dressing, vehicles, technology,
and materials that constitute the visible world of the production.

This specification translates the World (PKP-05) and the Directorial Language
(PKP-10) into a coherent design program. It does not specify fabrication or
sourcing — those belong to the Production Blueprint (PKP-15) and downstream
Studio Engine specifications. It specifies the *design intent* from which
fabrication decisions are derived.

2. Scope

This specification defines:
- Architecture (the built environment as designed)
- Props (the objects the production uses, with their narrative function)
- Wardrobe (the clothing logic of each character)
- Costumes (specific costume changes across the runtime)
- Set dressing (the logic of how spaces are inhabited)
- Vehicles (the vehicles the production uses, with their narrative function)
- Technology (the in-world technology as designed, distinct from real-world
  technology)
- Materials (the material palette and its semantic use)

Out of scope: shot composition (PKP-10), scene structure (PKP-09), fabrication
schedules (PKP-15).

3. Contents

3.1 Architecture
The built environment as designed. Each architectural element is declared with
its style, its function, its sensory signature, and its narrative role.

3.2 Props
The objects the production uses. Each prop is declared with its name, its
owner (if any), its narrative function, and its recurrence pattern.

3.3 Wardrobe
The clothing logic of each character. Declared per character as a wardrobe
principle — what the character wears, why, and how it shifts across the
runtime.

3.4 Costumes
Specific costume changes across the runtime. Each costume is declared with
its scene of first appearance, its design logic, and its narrative function.

3.5 Set Dressing
The logic of how spaces are inhabited — what objects appear in which spaces,
and what their presence signifies.

3.6 Vehicles
The vehicles the production uses. Each vehicle is declared with its type, its
owner, its narrative function, and its sensory signature.

3.7 Technology
The in-world technology as designed. Distinct from real-world technology; this
field captures how the production presents technology, not what technology the
production uses to film.

3.8 Materials
The material palette and its semantic use. Each material is declared with its
surface quality, its connotation, and the spaces in which it appears.

4. Inputs

- World Specification (PKP-05)
- Directorial Language Specification (PKP-10)
- Character Specification (PKP-06)
- Narrative Specification (PKP-09)
- Research Specification (PKP-03)

5. Outputs

- A validated Production Design record in the Production Knowledge Graph
- A materialized Production Design Specification document
- Design references propagated to PKP-15 (Production Blueprint)

6. Schema

```yaml
production_design:
  document_id: PKP-11
  version: 1.0.0
  architecture:
    - id: <string>
      name: <string>
      style: <string>
      function: <string>
      sensory_signature: <string>
      narrative_role: <string>
  props:
    - id: <string>
      name: <string>
      owner: <reference to PKP-06|null>
      narrative_function: <string>
      recurrence_pattern: <string>
  wardrobe:
    - character_id: <reference to PKP-06>
      principle: <string>
      shift_logic: <string>
  costumes:
    - id: <string>
      character_id: <reference to PKP-06>
      first_appearance: <reference to PKP-09 scene>
      design_logic: <string>
      narrative_function: <string>
  set_dressing:
    - location_id: <reference to PKP-05>
      principle: <string>
      significant_objects: [<string>]
  vehicles:
    - id: <string>
      type: <string>
      owner: <reference to PKP-06|null>
      narrative_function: <string>
      sensory_signature: <string>
  technology:
    - id: <string>
      name: <string>
      presented_function: <string>
      design_logic: <string>
      narrative_function: <string>
  materials:
    - id: <string>
      name: <string>
      surface_quality: <string>
      connotation: <string>
      appears_in: [<reference to PKP-05 locations>]
  research_citations: [<reference to PKP-03 items>]
  provenance:
    source_world: <reference>
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- architecture (at least one entry)
- props (at least one entry)
- wardrobe (one entry per character with on-screen presence)
- materials (at least one entry)
- provenance.confidence

8. Optional Fields

- costumes (required if wardrobe shift_logic is declared)
- set_dressing (recommended)
- vehicles (required if any vehicle appears on screen)
- technology (required if in-world technology is narratively significant)
- research_citations

9. Validation Rules

- PD-001: Every architecture entry must be consistent with a location in
  PKP-05; if it introduces a new location, PKP-05 must be extended first.
- PD-002: props.owner must reference a character in PKP-06 or be null.
- PD-003: props.recurrence_pattern must be consistent with the scene list in
  PKP-09. A prop declared to recur must appear in at least two scenes.
- PD-004: wardrobe.shift_logic must be consistent with the character's
  emotional_arc in PKP-06.
- PD-005: costumes.first_appearance must reference a scene in PKP-09.
- PD-006: set_dressing.location_id must reference a location in PKP-05.
- PD-007: materials.appears_in must reference locations in PKP-05.
- PD-008: The material palette must be consistent with the color_language in
  PKP-10.
- PD-009: technology entries must be consistent with the technology.era
  declared in PKP-05.
- PD-010: research_citations must reference items in PKP-03.
- PD-011: No design element may violate a non-negotiable principle from
  PKP-00.

10. Dependencies

- PKP-05 — World Specification (hard)
- PKP-10 — Directorial Language Specification (hard)
- PKP-06 — Character Specification (hard)
- PKP-09 — Narrative Specification (soft)
- PKP-03 — Research Specification (soft)

11. Versioning

- MAJOR: Removal of an architecture entry, change to wardrobe principle, or
  change to material palette.
- MINOR: Addition of props, costumes, vehicles, or technology.
- PATCH: Wording refinements that do not alter design intent.

A MAJOR change to Production Design triggers revalidation of PKP-15.

12. Examples

```yaml
production_design:
  document_id: PKP-11
  version: 1.0.0
  architecture:
    - id: "ARCH-001"
      name: "Municipal Hospital, consultation wing."
      style: "Late institutional modernism, 1970s renovation."
      function: "Site of diagnostic encounters."
      sensory_signature: "Fluorescent light, linoleum, frosted glass."
      narrative_role: "Embodies the institutional frame Holt relies on."
  props:
    - id: "PROP-001"
      name: "Holt's diagnostic notebook."
      owner: "CHR-001"
      narrative_function: "Carries the visible record of her reasoning."
      recurrence_pattern: "Appears in every consultation scene; closed firmly at end of shift."
    - id: "PROP-002"
      name: "The paging speaker."
      owner: null
      narrative_function: "Embodiment of unanswerable institutional demand."
      recurrence_pattern: "Sounds at each decision point; never answered in frame."
  wardrobe:
    - character_id: "CHR-001"
      principle: "Clinical clothing worn slightly past neatness."
      shift_logic: "Clothing loosens and untucks subtly as certainty erodes."
  costumes:
    - id: "CST-001"
      character_id: "CHR-001"
      first_appearance: "SCN-001"
      design_logic: "Crisp clinical attire; lab coat buttoned."
      narrative_function: "Establishes professional armor."
    - id: "CST-002"
      character_id: "CHR-001"
      first_appearance: "SCN-007"
      design_logic: "Lab coat unbuttoned; sleeves pushed up."
      narrative_function: "Armor loosening; visible erosion of certainty."
  set_dressing:
    - location_id: "LOC-001"
      principle: "Sparse; objects are functional, not decorative."
      significant_objects: ["Diagnostic notebook", "Frosted glass partition", "Paging speaker."]
  vehicles:
    - id: "VEH-001"
      type: "Night-route tram"
      owner: null
      narrative_function: "Marks the boundary between hospital and outside world."
      sensory_signature: "Yellow interior light, low hum, bell at stops."
  technology:
    - id: "TECH-001"
      name: "Paging system"
      presented_function: "One-way audible summons."
      design_logic: "Analog; visible speaker grilles."
      narrative_function: "Embodiment of demand without response."
  materials:
    - id: "MAT-001"
      name: "Frosted glass"
      surface_quality: "Translucent, cool, slightly greasy."
      connotation: "Visibility without contact."
      appears_in: ["LOC-001"]
    - id: "MAT-002"
      name: "Linoleum"
      surface_quality: "Dull, scuffed, faintly reflective."
      connotation: "Institutional endurance."
      appears_in: ["LOC-001"]
  research_citations: ["RES-002"]
  provenance:
    source_world: "PKP-05 v1.0.0"
    agent: "ProductionDesignArchitectAgent"
    session: "sess-010"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for sustainability annotations (reuse, recycled materials) may be
  added when the Production Blueprint gains a sustainability dimension.
- A field for set-dressing temporal logic (how a space changes across the
  runtime) may be added in a MINOR version.
- A field for cross-production design lineage (shared design languages across
  a series) will be modeled as Knowledge Graph edges.