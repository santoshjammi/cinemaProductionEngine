Genesis Ontology (GO)
GO-002 — Genesis Semantic Relationship Catalog

Document ID: GO-002

Title: Genesis Semantic Relationship Catalog

Version: 1.0.0

Status: Core Ontology

Authority: Derived from GFS-000 through GFS-009 and GO-001

1. Purpose

The Genesis Semantic Relationship Catalog establishes the canonical library of semantic predicates that connect concepts within the Genesis Engine.

Where GO-001 defines the nouns of the Genesis semantic language, this catalog defines the grammar — the governed relationships that may exist between concepts, their cardinality, directionality, transitivity, symmetry, lifecycle implications, and validation rules.

Every edge in the Production Knowledge Graph, every inference produced by the Reasoning Engine, and every dependency tracked by the Discovery Engine shall use a relationship type defined or derived from this catalog.

2. Foundational Principle

**Relationships carry semantic meaning.**

A relationship is not a label.

A relationship is a governed predicate with defined semantics, constraints, and consequences.

If a relationship's meaning cannot be stated precisely, it shall not be used in the Production Knowledge Graph.

3. Architectural Position

```text
GO-001 Core Ontology (nouns)
        │
        ↓
GO-002 Semantic Relationship Catalog (verbs / predicates)
        │
        ↓
Production Knowledge Graph (instances + edges)
        │
        ↓
Reasoning Engine, Discovery Engine, Validation Engine
```

This catalog is the canonical grammar of Genesis.

4. Relationship Specification Model

Every relationship in this catalog shall define:

* Canonical Name
* Stable Identifier
* Directionality (unidirectional, bidirectional)
* Symmetry (symmetric, asymmetric, antisymmetric)
* Transitivity (transitive, intransitive)
* Cardinality (one-to-one, one-to-many, many-to-many)
* Domain (valid source concept types)
* Range (valid target concept types)
* Inverse (canonical inverse relationship, if any)
* Lifecycle Implication (whether the relationship affects lifecycle state)
* Validation Rule
* Examples

5. Canonical Relationship Types

The catalog defines the following governed relationship families:

* Temporal: precedes, follows
* Causal: causes, implies, contradicts
* Dependency: depends_on, references, requires
* Governance: validates, governs
* Structural: contains, part_of, has_a, is_a
* Evolution: evolves_into, transforms_into, derives_from
* Influence: influences, supports, opposes, motivates
* Discovery: validates, contradicts, references

6. Temporal Relationships

### 6.1 precedes

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing with lifecycle or temporal position
* Range: any Thing with lifecycle or temporal position
* Inverse: follows
* Meaning: A occurs before B in time or lifecycle
* Validation: no cycles; A and B must share a comparable temporal axis
* Example: Scene_001 precedes Scene_002

### 6.2 follows

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing with lifecycle or temporal position
* Range: any Thing with lifecycle or temporal position
* Inverse: precedes
* Meaning: A occurs after B in time or lifecycle
* Validation: no cycles; follows is the inverse of precedes
* Example: Scene_002 follows Scene_001

7. Causal Relationships

### 7.1 causes

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: Event, Action, Decision
* Range: Event, State, Consequence
* Inverse: caused_by (derived)
* Meaning: A produces B as a consequence
* Validation: requires evidence; inferred causality must be marked as such
* Example: WoundingEvent causes FearOfAbandonment

### 7.2 implies

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: implied_by (derived)
* Meaning: A being true makes B necessarily true
* Validation: logical entailment must be demonstrable
* Example: Betrayal implies BrokenTrust

### 7.3 contradicts

* Directionality: bidirectional
* Symmetry: symmetric
* Transitivity: intransitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: self
* Meaning: A and B cannot both be true within the same context
* Validation: contradiction must trigger a resolution workflow
* Example: CharacterFear contradicts CharacterAction (if action requires courage)

8. Dependency Relationships

### 8.1 depends_on

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: required_by (derived)
* Meaning: A cannot exist, complete, or validate without B
* Validation: dependency cycles must be broken before approval
* Example: Scene_017 depends_on CharacterArc_Protagonist

### 8.2 references

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: intransitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: referenced_by (derived)
* Meaning: A mentions or points to B without structural dependency
* Validation: target must exist; weak link does not trigger validation
* Example: Dialogue_014 references Symbol_Water

### 8.3 requires

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: required_by
* Meaning: A mandates the presence of B for production readiness
* Validation: missing requirements block approval
* Example: Scene_003 requires Prop_Gun

9. Governance Relationships

### 9.1 validates

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: intransitive
* Cardinality: many-to-many
* Domain: Validator, Rule, Evidence
* Range: any Thing
* Inverse: validated_by (derived)
* Meaning: A confirms the integrity, completeness, or correctness of B
* Validation: validator must be authoritative for the target's domain
* Example: ConsistencyCheck validates CharacterSubgraph

### 9.2 governs

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: one-to-many
* Domain: Standard, Constitution, Policy, Rule
* Range: any Thing
* Inverse: governed_by (derived)
* Meaning: A defines the rules B must conform to
* Validation: governed things must be checked against their governor
* Example: GFS-000 governs all Genesis artifacts

10. Structural Relationships

### 10.1 is_a

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: subclass_of (derived)
* Meaning: A is a specialization of B
* Validation: A must inherit B's properties
* Example: Protagonist is_a Character

### 10.2 has_a

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: intransitive
* Cardinality: one-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: part_of
* Meaning: A possesses B as a component
* Validation: deletion of A cascades consideration to B
* Example: Character has_a PsychologicalProfile

### 10.3 part_of

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-one
* Domain: any Thing
* Range: any Thing
* Inverse: has_a
* Meaning: A is a component of B
* Validation: A's lifecycle is bounded by B's lifecycle
* Example: Beat part_of Scene

### 10.4 contains

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: one-to-many
* Domain: Container Thing
* Range: Contained Thing
* Inverse: contained_in
* Meaning: A holds B as a member
* Validation: containment hierarchy must be acyclic
* Example: Sequence contains Scenes

11. Evolution Relationships

### 11.1 evolves_into

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: intransitive
* Cardinality: one-to-one
* Domain: any Thing
* Range: any Thing
* Inverse: evolved_from
* Meaning: A transforms over time into B
* Validation: identity continuity must be preserved
* Example: DraftCharacter evolves_into FinalCharacter

### 11.2 transforms_into

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: intransitive
* Cardinality: one-to-one
* Domain: any Thing
* Range: any Thing
* Inverse: transformed_from
* Meaning: A becomes B through a governed transformation event
* Validation: requires a transformation trigger
* Example: Protagonist_State_A transforms_into Protagonist_State_B

### 11.3 derives_from

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: source_of (derived)
* Meaning: A is produced from B as a source
* Validation: lineage must be traceable
* Example: DerivedLightingProfile derives_from MasterLightingProfile

12. Influence Relationships

### 12.1 influences

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: influenced_by (derived)
* Meaning: A affects B without strictly determining it
* Validation: influence claims require evidence or reasoning
* Example: WoundingEvent influences Worldview

### 12.2 supports

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: supported_by (derived)
* Meaning: A reinforces or strengthens B
* Validation: supporting evidence must be citable
* Example: Theme_Sacrifice supports CharacterArc_Protagonist

### 12.3 opposes

* Directionality: bidirectional
* Symmetry: symmetric
* Transitivity: intransitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: any Thing
* Inverse: self
* Meaning: A and B stand in tension without strict contradiction
* Validation: opposition must be narratively productive, not arbitrary
* Example: Character_A opposes Character_B

### 12.4 motivates

* Directionality: unidirectional
* Symmetry: asymmetric
* Transitivity: transitive
* Cardinality: many-to-many
* Domain: any Thing
* Range: Action, Decision, Goal
* Inverse: motivated_by (derived)
* Meaning: A provides the reason for B
* Validation: motivation must be traceable to a character's psychology or to creator intent
* Example: Fear motivates Withdrawal

13. Discovery Relationships

### 13.1 references (discovery variant)

See §8.2. The same predicate is reused for discovery references.

### 13.2 validates (discovery variant)

See §9.1. Used by validators to confirm discovered knowledge.

### 13.3 contradicts (discovery variant)

See §7.3. Used by the Discovery Engine to surface knowledge gaps.

14. Relationship Lifecycle

Every relationship in the PKG shall carry:

* Source
* Target
* Predicate
* Confidence
* Evidence
* Origin (explicit, inferred, assumed)
* CreatedAt
* ValidatedAt
* LifecycleState

Relationships that are inferred shall never be treated as facts.

15. Relationship with the Core Ontology

Every relationship in this catalog shall connect instances of concepts defined in GO-001 or its derived ontologies.

The catalog does not introduce new nouns — only predicates.

16. Relationship with the Production Knowledge Graph

The PKG stores relationship instances as governed edges.

Each edge shall reference a predicate from this catalog or a governed derivation.

Edges not present in the catalog shall be rejected at validation time.

17. Inheritance of Relationships

Specialized ontologies may specialize relationships but shall not redefine their core semantics.

Example:

```text
GO-002 contains
        ↓
GO-101 narrative_contains (specialization)
        ↓
GO-201 scene_contains (further specialization)
```

Specialization narrows domain and range; it shall not broaden them.

18. Validation Rules

Relationships shall be validated for:

* Predicate presence in the catalog
* Domain and range conformance
* Cardinality conformance
* Cycle detection (for acyclic predicates)
* Symmetry conformance
* Transitivity conformance
* Evidence presence (for inferred relationships)
* Lifecycle state alignment
* Inverse presence (where canonical)

19. Constitutional Invariants

The following principles are immutable:

* Relationships carry semantic meaning.
* The catalog is the canonical source of predicates.
* Domain ontologies extend but do not redefine predicates.
* Inferred relationships shall not be treated as facts.
* Every relationship instance shall carry confidence and evidence.
* Relationship evolution remains governed.

20. Evolution Policy

This catalog may evolve through additive extensions governed by the Constitutional Ontology Framework and the Governance Constitution.

New predicates may be added; existing predicates shall preserve their semantic meaning to maintain compatibility across productions and generations of the platform.

21. Approval

This Catalog is approved as the canonical library of semantic predicates of the Genesis Engine.

All Production Knowledge Graphs, Reasoning Engines, Discovery Engines, Validation Engines, and domain ontologies shall use only predicates defined herein or governed derivations thereof.