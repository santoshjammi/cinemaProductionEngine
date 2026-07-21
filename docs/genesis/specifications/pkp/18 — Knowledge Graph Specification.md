Genesis Foundational Standards (GFS)
PKP-18 — Knowledge Graph Specification

Document ID: PKP-18
Title: Knowledge Graph Specification
Version: 1.0.0
Status: Pre-Production Specification
Authority: Derived from GFS-000 Constitutional Charter

1. Purpose

The Knowledge Graph Specification defines the canonical map of the production.
It captures entities, relationships, dependencies, lineage, versioning,
confidence, evidence, and traceability across every specification in the
Production Knowledge Package.

Per the Constitutional Charter (GFS-000, Fifth Principle), knowledge is
canonical and files are not. This specification is the authoritative source
from which all other PKP specifications can be regenerated. It is the map of
the Production Knowledge Graph as it pertains to this production, distinct
from the GFS-010 specification that defines the graph's structure in general.

2. Scope

This specification defines:
- The entities the production contains (one per concept declared across the
  PKP)
- The relationships between those entities
- The dependencies between specifications
- The lineage of every decision (origin, evidence, alternatives, confidence)
- The versioning of every entity and relationship
- The confidence classification of every entity and relationship
- The evidence trail that supports every confirmed claim
- The traceability from any downstream artifact back to its source

Out of scope: the general structure of the Production Knowledge Graph (that
is GFS-010). This specification is the production-specific map.

3. Contents

3.1 Entities
Every concept declared across the PKP — visions, strategies, projects,
research items, stories, worlds, characters, relationships, psychologies,
narratives, scenes, shots, designs, audio intents, editing languages,
animation intents, blueprints, distributions, quality criteria. Each entity
is declared with its id, type, source specification, and confidence.

3.2 Relationships
The semantic relationships between entities — depends_on, cites, references,
derives_from, contradicts, refines, supersedes. Each relationship is declared
with its source entity, target entity, type, and confidence.

3.3 Dependencies
The dependency graph across specifications. Declared as a list of edges, each
with a source specification, target specification, dependency type (hard,
soft), and the reason.

3.4 Lineage
The lineage of every decision. Each decision is declared with its origin
(specification, agent, session), its supporting evidence (references to
research items or upstream decisions), the alternatives considered, and the
confidence at the time of decision.

3.5 Versioning
The version history of every entity and relationship. Each version is
declared with its number, its change type (MAJOR, MINOR, PATCH), its reason,
and its timestamp.

3.6 Confidence
The confidence classification of every entity and relationship, per the
Constitutional Charter (GFS-000, Sixth Principle): EXPLICIT, INFERRED,
CONFIRMED, ASSUMED, UNKNOWN. Each classification is declared with its basis.

3.7 Evidence
The evidence trail that supports every confirmed claim. Each evidence entry
is declared with its referenced research item, its strength, and its scope
(real-world, in-world, both).

3.8 Traceability
The traceability from any downstream artifact (shot, asset, design choice)
back to its source specification and decision. Each traceability entry is
declared with the artifact, the source specification, the source entity, and
the path.

4. Inputs

- Every prior PKP specification (PKP-00 through PKP-17)
- Production Knowledge Graph Specification (GFS-010)
- Constitutional Charter (GFS-000)

5. Outputs

- A validated Knowledge Graph record in the Production Knowledge Graph
- A materialized Knowledge Graph Specification document
- The canonical map from which any PKP specification can be regenerated

6. Schema

```yaml
knowledge_graph:
  document_id: PKP-18
  version: 1.0.0
  entities:
    - id: <string>
      type: <vision|strategy|project|research_item|story|world|character|relationship|psychology|narrative|scene|shot|design|audio_intent|editing_language|animation_intent|blueprint|distribution|quality_criterion|other>
      source_specification: <reference to PKP-NN>
      label: <string>
      confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
      confidence_basis: <string>
  relationships:
    - id: <string>
      source_entity: <reference>
      target_entity: <reference>
      type: <depends_on|cites|references|derives_from|contradicts|refines|supersedes|other>
      confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
      confidence_basis: <string>
  dependencies:
    - source_specification: <reference to PKP-NN>
      target_specification: <reference to PKP-NN>
      dependency_type: <hard|soft>
      reason: <string>
  lineage:
    - decision_id: <string>
      origin:
        specification: <reference>
        agent: <string>
        session: <string>
      supporting_evidence: [<reference to research items or decisions>]
      alternatives_considered: [<string>]
      confidence_at_decision: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
  versioning:
    - entity_id: <reference>
      version: <string>
      change_type: <MAJOR|MINOR|PATCH>
      reason: <string>
      timestamp: <ISO 8601>
  evidence:
    - entity_id: <reference>
      research_item: <reference to PKP-03>
      evidence_strength: <ESTABLISHED|SUPPORTED|CONTESTED|UNVERIFIED>
      scope: <REAL_WORLD|IN_WORLD|BOTH>
  traceability:
    - artifact: <string>
      source_specification: <reference to PKP-NN>
      source_entity: <reference>
      path: [<reference>]
  provenance:
    source_specifications: [<reference to PKP-00 through PKP-17>]
    agent: <string>
    session: <string>
    confidence: <EXPLICIT|INFERRED|CONFIRMED|ASSUMED|UNKNOWN>
```

7. Required Fields

- entities (at least one per source specification; the field is the union of
  all entities declared across the PKP)
- relationships (at least the dependency edges declared across the PKP)
- dependencies (the full dependency graph across PKP-00 through PKP-17)
- lineage (at least one entry per MAJOR decision across the PKP)
- versioning (at least one entry per entity, recording the initial version)
- evidence (at least one entry per entity with confidence CONFIRMED that
  cites a research item)
- traceability (at least one entry per artifact in PKP-15)
- provenance.confidence

8. Optional Fields

- relationships of type "contradicts" or "supersedes" (recommended when
  applicable; required when a decision reverses a prior decision)
- lineage.alternatives_considered (recommended; required for MAJOR decisions)

9. Validation Rules

- KG-001: Every entity.source_specification must reference a specification in
  the PKP.
- KG-002: Every relationship.source_entity and target_entity must reference
  entities present in `entities`.
- KG-003: dependencies must form a directed acyclic graph; no circular
  dependencies.
- KG-004: dependencies must be consistent with the Dependencies section of
  each source specification.
- KG-005: lineage must include an entry for every MAJOR version change
  recorded in versioning.
- KG-006: Every entity with confidence CONFIRMED must have at least one
  evidence entry.
- KG-007: traceability must cover every shot, asset, character reference, and
  environment in PKP-15.
- KG-008: No entity may have confidence UNKNOWN in a critical path. Critical
  paths are: Vision → Creative Strategy → Project → Story → Narrative →
  Production Blueprint.
- KG-009: The knowledge graph must be complete — every entity and
  relationship declared across PKP-00 through PKP-17 must be present.
- KG-010: No entity or relationship may violate a non-negotiable principle
  from PKP-00.
- KG-011: The graph must be regenerable — given the knowledge graph, every
  PKP specification must be reproducible without recourse to external
  conversation history.

10. Dependencies

- Every prior PKP specification (PKP-00 through PKP-17) — hard dependencies.
  The Knowledge Graph Specification cannot be authored until all upstream
  specifications are present and certified.
- GFS-010 — Production Knowledge Graph Specification (structural reference).

11. Versioning

- MAJOR: Removal of an entity, change to a dependency edge, or downgrade of
  a critical-path entity's confidence.
- MINOR: Addition of entities, relationships, or evidence.
- PATCH: Wording refinements that do not alter graph structure.

A MAJOR change to the Knowledge Graph triggers revalidation of PKP-17 and
invalidates the certification until the Governance Agent recertifies.

12. Examples

```yaml
knowledge_graph:
  document_id: PKP-18
  version: 1.0.0
  entities:
    - id: "ENT-001"
      type: "vision"
      source_specification: "PKP-00"
      label: "Vision: The Unverifiable Case"
      confidence: "CONFIRMED"
      confidence_basis: "Derived from creator synopsis and ratified by Governance Agent."
    - id: "ENT-002"
      type: "strategy"
      source_specification: "PKP-01"
      label: "Creative Strategy: Psychological drama, slow cinema."
      confidence: "CONFIRMED"
      confidence_basis: "Consistent with Vision; ratified."
    - id: "ENT-009"
      type: "scene"
      source_specification: "PKP-09"
      label: "Scene 3: The anomaly is recognized."
      confidence: "CONFIRMED"
      confidence_basis: "Validated against Story and Character specifications."
    - id: "ENT-015"
      type: "shot"
      source_specification: "PKP-15"
      label: "Shot SCN-003-01: Close on Holt, profile."
      confidence: "CONFIRMED"
      confidence_basis: "Derived from Directorial Language and Narrative."
  relationships:
    - id: "REL-KG-001"
      source_entity: "ENT-002"
      target_entity: "ENT-001"
      type: "derives_from"
      confidence: "CONFIRMED"
      confidence_basis: "Strategy explicitly derived from Vision."
    - id: "REL-KG-002"
      source_entity: "ENT-009"
      target_entity: "ENT-015"
      type: "derives_from"
      confidence: "CONFIRMED"
      confidence_basis: "Shot derived from scene."
  dependencies:
    - source_specification: "PKP-01"
      target_specification: "PKP-00"
      dependency_type: "hard"
      reason: "Creative Strategy cannot be authored without a certified Vision."
    - source_specification: "PKP-15"
      target_specification: "PKP-09"
      dependency_type: "hard"
      reason: "Blueprint shots derive from Narrative scenes."
  lineage:
    - decision_id: "DEC-001"
      origin:
        specification: "PKP-04"
        agent: "StoryArchitectAgent"
        session: "sess-003"
      supporting_evidence: ["RES-001"]
      alternatives_considered:
        - "Resolution posture: resolved. Rejected because it contradicts the Vision's non-negotiable principle that the verdict is never confirmed."
        - "Resolution posture: tragic. Rejected because it contradicts the audience transformation's to-state."
      confidence_at_decision: "CONFIRMED"
  versioning:
    - entity_id: "ENT-001"
      version: "1.0.0"
      change_type: "MAJOR"
      reason: "Initial certification."
      timestamp: "2026-07-19T12:00:00Z"
  evidence:
    - entity_id: "ENT-009"
      research_item: "RES-001"
      evidence_strength: "SUPPORTED"
      scope: "BOTH"
  traceability:
    - artifact: "Shot SCN-003-01"
      source_specification: "PKP-15"
      source_entity: "ENT-015"
      path: ["PKP-00", "PKP-01", "PKP-04", "PKP-09", "PKP-10", "PKP-15"]
  provenance:
    source_specifications: ["PKP-00", "PKP-01", "PKP-02", "PKP-03", "PKP-04", "PKP-05", "PKP-06", "PKP-07", "PKP-08", "PKP-09", "PKP-10", "PKP-11", "PKP-12", "PKP-13", "PKP-14", "PKP-15", "PKP-16", "PKP-17"]
    agent: "KnowledgeGraphArchitectAgent"
    session: "sess-017"
    confidence: "CONFIRMED"
```

13. Future Extensibility

- A field for cross-production graph linkage (shared entities across a
  series, alternate timelines, adaptations) may be added as Knowledge Graph
  hyperedges.
- A field for graph query declarations (named queries the Studio Engine may
  issue against the graph) may be added when the Studio Engine introduces a
  query layer.
- A field for graph integrity assertions (invariants the graph must satisfy
  at every version) may be promoted from validation rules in a future
  version.