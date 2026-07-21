Genesis Knowledge Reference (GKR)
GKR-003 — Vocabulary Registry

Document ID: GKR-003
Title: Vocabulary Registry
Version: 1.0.0
Status: Foundational Knowledge Reference
Authority: Derived from GO-001, GO-002, GO-003, GFS-000 through GFS-009

1. Purpose

This registry is the canonical vocabulary of Genesis. Every term used in
Genesis with a defined meaning is listed here with: the canonical name,
the ontology source, the definition, the usage rules, and the synonyms
(if any). Agents, validators, and workflows must use the canonical name.
Synonyms are mapped to the canonical name and never replace it.

If a term is used in Genesis but is not in this registry, it is a
vocabulary defect. Open a PR to add the term; do not use the unregistered
term in the meantime.

2. Reading Order

Terms are grouped by ontology source. Within each group, terms are
alphabetical. The registry is not a tutorial; it is a reference. For
conceptual background, read the ontology documents directly.

3. Core Concepts (GO-001)

Term: Thing
Ontology: GO-001 §5
Definition: The universal root concept; any identifiable constitutional
  object.
Usage: Every ontology concept ultimately derives from Thing. Never
  instantiate Thing directly; always use a subclass.
Synonyms: Entity (mapped, not canonical).

Term: Identity
Ontology: GO-001 §6
Definition: What something is; permanence across evolution.
Usage: Identity is immutable. A concept may be deprecated but its
  identity is never reused.
Synonyms: none.

Term: Knowledge Object
Ontology: GO-001 §7
Definition: A unit of knowledge in the PKG; a node with confidence and
  provenance.
Usage: Every node in the PKG is a Knowledge Object instance.
Synonyms: Fact (mapped, not canonical).

Term: Confidence
Ontology: GO-001 §7
Definition: The categorical classification of how a fact came to exist
  in the PKG.
Usage: Use values from T-001 (EXPLICIT, INFERRED, CONFIRMED, ASSUMED,
  UNKNOWN). Do not invent numeric confidences.
Synonyms: none.

Term: Traceability
Ontology: GO-001 §7
Definition: The ability to follow a decision back to its origin.
Usage: Every node and edge records provenance. Traceability is enforced
  by GFS-010 §3.
Synonyms: Lineage (mapped; lineage is the chain, traceability is the
  property).

Term: Discovery
Ontology: GO-001 §8
Definition: The process of transforming uncertainty into governed
  knowledge.
Usage: Discovery is a phase (state: discovering) and a capability. The
  Discovery Constitution (GFS-004) governs it.
Synonyms: none.

Term: Gap
Ontology: GO-001 §8
Definition: A missing piece of knowledge required for production
  readiness.
Usage: A Gap is a node in the PKG with confidence UNKNOWN. The discovery
  loop must resolve every critical-path Gap before certification.
Synonyms: Unknown (in this context; do not use "unknown" as a noun for
  Gap).

Term: Story
Ontology: GO-001 §9
Definition: The intentional creative expression; the narrative whole.
Usage: A Story contains Acts. Story is medium-independent.
Synonyms: Narrative (in some contexts; narrative is the broader
  expression, story is the structured whole).

Term: Theme
Ontology: GO-001 §9
Definition: The underlying idea a story expresses.
Usage: A Beat supports a Theme. A Story features one or more Themes.
Synonyms: none.

Term: Conflict
Ontology: GO-001 §9
Definition: The opposition that drives a story.
Usage: A Story features a Conflict. A Conflict is never identical to a
  Character.
Synonyms: none.

Term: Arc
Ontology: GO-001 §9
Definition: The trajectory of change across a Story or a Character.
Usage: An Arc is composed of Beats. A Character has an Arc; a Story has
  an Arc.
Synonyms: none.

Term: Character
Ontology: GO-001 §10
Definition: An intentional participant in a story; not limited to humans.
Usage: A Character has a CharacterDNA and an Arc. Characters may be
  people, animals, mythological beings, organizations, AI entities, or
  symbolic representations.
Synonyms: Persona (mapped, narrower).

Term: World
Ontology: GO-001 §11
Definition: The environment in which a story exists.
Usage: A World contains Environments. A World defines context, not
  presentation.
Synonyms: Setting (mapped, narrower).

Term: Environment
Ontology: GO-001 §11
Definition: A named location or context within a World.
Usage: A Scene occursIn an Environment.
Synonyms: Location (mapped, narrower; a Location is a specific place
  within an Environment).

Term: Relationship
Ontology: GO-001 §12
Definition: A semantic edge between two concepts.
Usage: Use relationship types from GO-002. Never invent relationships
  inline.
Synonyms: Edge (in graph terminology).

Term: Creative Intent
Ontology: GO-001 §13
Definition: Why a production exists; the creator's purpose.
Usage: Creative Intent precedes Story construction. The synopsis is the
  initial expression of Creative Intent.
Synonyms: Vision (mapped, narrower).

Term: Production
Ontology: GO-001 §14
Definition: The universal planning concept for a Genesis engagement.
Usage: A Production has a Brief, a Plan, and a PKG. A Production moves
  through the lifecycle states (T-003).
Synonyms: none.

Term: Specification
Ontology: GO-001 §14
Definition: A formal, validated description of a production concern.
Usage: Specifications are produced by architects and consumed by
  engineers and validators.
Synonyms: Spec (informal).

Term: Validation
Ontology: GO-001 §15
Definition: The act of checking a PKG or artifact against its
  specification.
Usage: Validation is performed by validator agents. Outcomes are from
  T-009.
Synonyms: none.

4. Knowledge Graph Terms (GFS-010)

Term: Production Knowledge Graph (PKG)
Ontology: GFS-010 §2
Definition: The single canonical representation of production
  intelligence; a directed labeled property graph.
Usage: Every agent reads from and writes to the PKG. The PKG is the
  source of truth.
Synonyms: Graph (informal).

Term: Node
Ontology: GFS-010 §3.1
Definition: A unit in the PKG; an instance of an ontology class.
Usage: Every node has id, type, label, properties, confidence,
  created_at, provenance.
Synonyms: Vertex (in graph theory).

Term: Edge
Ontology: GFS-010 §3.2
Definition: A directed semantic relationship between two nodes.
Usage: Every edge has id, type (from GO-002), source_id, target_id,
  properties, confidence, created_at, provenance.
Synonyms: Relationship (interchangeable in PKG context).

Term: Subgraph
Ontology: GFS-010 §3.3
Definition: A named, versioned collection of nodes and edges representing
  a production concern.
Usage: Every PKG must contain the five mandatory subgraphs (Narrative,
  Character, World, Audience, Production).
Synonyms: none.

Term: Production Knowledge Package (PKP)
Ontology: GFS-010 §7
Definition: The sealed, signed, distributable artifact containing the
  PKG and materialized views.
Usage: The PKP is what crosses the Genesis boundary to the Studio
  Engine. The PKG never leaves Genesis.
Synonyms: Package (informal).

5. Agent Terms (GFS-005)

Term: Constitutional Class
Ontology: GFS-005
Definition: The role family an agent belongs to.
Usage: Use values from T-002. Every agent declares exactly one
  constitutional class.
Synonyms: Role (informal).

Term: Dispatch
Ontology: GFS-005
Definition: The act of an orchestrator or architect invoking an agent.
Usage: Dispatch is recorded in the orchestrator's dispatch log.
Synonyms: none.

Term: Session
Ontology: GFS-005
Definition: A bounded execution context for a production.
Usage: Sessions are created and terminated by the orchestrator (GAS-026)
  and are the unit of checkpoint and resume.
Synonyms: none.

6. Validation Terms (GFS-006)

Term: Validator
Ontology: GFS-006
Definition: An agent that scores an output against a specification.
Usage: A validator emits a report with an outcome from T-009 and a
  severity from T-010.
Synonyms: Checker (informal).

Term: Defect
Ontology: GFS-006
Definition: A validator-flagged issue requiring repair.
Usage: Defects are routed to the Revision Agent (GAS-027).
Synonyms: Finding (informal).

Term: Repair
Ontology: GFS-006
Definition: The act of correcting a defect.
Usage: Repair is bounded by the Revision Agent's repair budget. When
  the budget is exhausted, the production may transition to failed.
Synonyms: none.

7. Governance Terms (GFS-007)

Term: Governance
Ontology: GFS-007
Definition: The authority that reviews and signs off production
  readiness.
Usage: Governance operates during the certifying state. Governance may
  veto a production.
Synonyms: none.

Term: Veto
Ontology: GFS-007
Definition: A governance decision to halt a production.
Usage: A veto transitions the production to failed. A veto is recorded
  in the PKG provenance log.
Synonyms: none.

8. Lifecycle Terms (GO-003)

Term: State
Ontology: GO-003
Definition: The current position of a production in the lifecycle.
Usage: Use values from T-003. The orchestrator owns state transitions.
Synonyms: none.

Term: Transition
Ontology: GO-003
Definition: A change from one state to another.
Usage: Transitions are recorded as edges of type go:transitionedTo with
  EXPLICIT confidence.
Synonyms: none.

9. Evolution Policy

This registry evolves additively. New terms are appended; existing
terms are never redefined. When a term's meaning needs to evolve, a new
term is introduced and the old term is deprecated. The Ontology
Evolution Framework (GMM-002) governs this process.

10. Maintenance

This registry is maintained by the maintainers. Any contributor may
propose a new term by opening a PR that:

- Adds the term in the correct group.
- Provides all required fields (Term, Ontology, Definition, Usage,
  Synonyms).
- Updates any documents that used the unregistered term to use the
  canonical name.
- Adds the term to the relevant domain ontology if it is not already
  present there.