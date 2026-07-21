Genesis Meta-Model (GMM)
GMM-001 — Genesis Meta-Model

Document ID: GMM-001
Title: Genesis Meta-Model
Version: 1.0.0
Status: Meta-Model
Authority: Derived from GFS-000, GFS-008, GFS-009, GO-001

1. Purpose

This document is the model of models. It describes how Genesis describes
itself: the meta-ontology that governs ontologies, the meta-specifications
that govern specifications, and the meta-workflows that govern workflows.
Every other document in Genesis is an instance of a concept defined here.

Genesis is a self-describing system. The Constitutional Meta-Model
(GFS-008) and the Constitutional Ontology Framework (GFS-009) are the
constitutional foundations; GMM-001 is their operational expression. Where
GFS-008 and GFS-009 say what must exist, GMM-001 says how those things are
structured, versioned, and validated.

2. The Three Meta-Layers

Genesis is built from three stacked meta-layers:

- M1 Meta-Ontology — defines what an ontology is and how it may evolve.
- M2 Meta-Specification — defines what a specification is and how it is
  validated.
- M3 Meta-Workflow — defines what a workflow is and how it is composed.

Each meta-layer is an instance of the layer above it and a specification
of the layer below it. The Charter (GFS-000) sits above all three; the
runtime (L6) sits below all three.

3. M1 Meta-Ontology

3.1 What an Ontology Is

An ontology is a versioned collection of classes, properties,
relationships, and invariants that define a coherent family of concepts.
Every ontology in Genesis:

- Has a stable identifier (GO-NNN).
- Has a parent ontology (GO-001 for top-level domain ontologies, another
  domain ontology for specialized ones).
- Declares its derivation explicitly.
- Declares its invariants.
- Declares its evolution policy (additive, deprecation rules).

3.2 Ontology Anatomy (Meta)

At the meta level, an ontology is described by:

- OntologyID: GO-NNN
- Title
- Domain (core, semantic, narrative, character, world, experience,
  execution, governance, learning, meta, organization, registry,
  strategy, creativity, foundation, constitutional, generated)
- ParentOntology: GO-NNN (or null for GO-001)
- Version: MAJOR.MINOR.PATCH
- Classes: list of ClassMeta
- Relationships: list of RelationshipMeta (from GO-002)
- Invariants: list of InvariantMeta
- EvolutionPolicy: reference to GMM-002
- Status: from T-007

3.3 ClassMeta

A class is described at the meta level by:

- StableIdentifier (immutable canonical name)
- HumanFriendlyName
- ParentClass (from this ontology or a parent)
- Properties: list of PropertyMeta
- Relationships: list of RelationshipMeta
- Lifecycle: from GO-001 §20

3.4 PropertyMeta

A property is described at the meta level by:

- Name
- Type (string, integer, float, boolean, enum, reference, URI, UUID,
  timestamp)
- Cardinality (required, optional, multi-valued)
- Constraints
- ConfidenceClassification (does this property carry EXPLICIT,
  INFERRED, CONFIRMED, ASSUMED, or UNKNOWN values)

3.5 InvariantMeta

An invariant is described at the meta level by:

- Name
- Formal statement (expressible as a graph constraint)
- Enforcement point (structural validation, semantic validation, or
  runtime validation)
- Severity (from T-010)

4. M2 Meta-Specification

4.1 What a Specification Is

A specification is a formal, validated description of a production
concern. Every specification in Genesis:

- Has a stable identifier (GSPEC-NNN or GFS-NNN for foundational).
- Declares its scope (what is in, what is explicitly out).
- Declares its invariants.
- Declares its validation requirements.
- Declares its compliance criteria.
- Declares the documents it derives from.

4.2 Specification Anatomy (Meta)

At the meta level, a specification is described by:

- SpecID
- Title
- Category (product, architecture, runtime, governance, implementation,
  integrations, deployment, enterprise, compiler, knowledge-graph,
  ontology)
- Scope
- Invariants
- ValidationRequirements
- ComplianceCriteria
- ParentDocuments
- Status: from T-008

4.3 Validation Contract

Every specification must declare how it is validated. The validation
contract consists of:

- A set of validators (agents or scripts) that must pass.
- A set of input artifacts the validators require.
- A set of output reports the validators produce.
- A pass/fail threshold.

A specification without a validation contract is invalid and will be
rejected by the linter.

5. M3 Meta-Workflow

5.1 What a Workflow Is

A workflow is an ordered, observable composition of agents and
sub-workflows that performs a unit of production work. Every workflow
in Genesis:

- Has a stable identifier (GWS-NNN).
- References the Full Production Workflow (GWS-001) as the baseline.
- Declares its phase in the lifecycle (T-003).
- Declares the agents it composes.
- Declares its inputs and outputs.
- Declares its error recovery strategy.

5.2 Workflow Anatomy (Meta)

At the meta level, a workflow is described by:

- WorkflowID
- Title
- Phase (from T-003)
- Agents: list of AgentRef
- SubWorkflows: list of WorkflowRef
- Inputs
- Outputs
- ErrorRecovery: reference to GAS-027 or to a governance escalation
- Observability: what events are emitted, what is recorded in the PKG
- Status: from T-008

5.3 Composition Rules

- A workflow may compose agents and sub-workflows.
- A sub-workflow may not compose its parent (no cycles).
- A workflow must declare which of its steps are parallelizable.
- A workflow must declare the conditions under which it transitions
  between steps.

6. The Self-Description Principle

Genesis is self-describing: every concept used inside Genesis is itself
defined inside Genesis. This creates a bootstrapping situation that is
resolved by treating GFS-000 (the Charter) as the unproven axiom. The
Charter is the only document in Genesis that is not an instance of a
meta-model concept. Everything else is.

Practical consequences:

- The Core Ontology (GO-001) is an instance of the M1 Meta-Ontology.
- The PKG Specification (GFS-010) is an instance of the M2
  Meta-Specification.
- The Full Production Workflow (GWS-001) is an instance of the M3
  Meta-Workflow.
- This document (GMM-001) is an instance of itself: it is a meta-model
  described by the meta-model. This recursion is bounded and accepted.

7. Validation of Meta-Models

Each meta-model is validated by a meta-validator that checks:

- Every instance conforms to its meta-model.
- Every meta-model is internally consistent.
- No meta-model contradicts the Charter (GFS-000).
- No meta-model redefines a concept from a lower layer.

Meta-validation is run by `tooling/check-meta-model.sh` (a sibling to
the doc linter) and is mandatory before any release.

8. Evolution of Meta-Models

Meta-models evolve under the same rules as the things they describe,
with one additional constraint: a change to a meta-model requires an
Architecture Decision Record (ADR) and governance approval. This is
because a meta-model change ripples to every instance; the blast
radius is the entire repository.

The Ontology Evolution Framework (GMM-002) governs the concrete
evolution procedure for ontologies. Equivalent frameworks for
specifications and workflows are defined inline in M2 and M3 above.

9. Relationship to the Constitutional Layer

GMM-001 is not constitutional. It is derived from GFS-008 (Constitutional
Meta-Model) and GFS-009 (Constitutional Ontology Framework), which are
constitutional. If GMM-001 conflicts with GFS-008 or GFS-009, those
documents prevail. GMM-001 is the operational expression; the
constitutional documents are the invariants.