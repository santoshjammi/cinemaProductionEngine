Genesis Contracts
GC-003 — Ontology Contract

Document ID: GC-003
Title: Ontology Semantic Contract
Version: 1.0.0
Status: Binding Contract
Authority: Derived from GFS-003, GFS-009, GFS-010

1. Purpose

This contract governs every ontology file within the Genesis Engine. It
instantiates the Semantic Contract Template (GC-001) for the specific case
of an ontology artifact that proposes to describe some domain of production
knowledge.

An ontology is not a documentation file. It is the constitutional definition
of the concepts, relationships, and constraints that Genesis is permitted to
reason about within a domain. Any node, edge, or property that does not
conform to a contracted ontology is invalid and shall not enter the
Production Knowledge Graph.

2. Foundational Principle

Every ontology derives. No ontology contradicts.

The Core Ontology (GO-001) is the root of the ontology tree. Every other
ontology shall derive from it, directly or transitively, through an explicit
`derives_from` relationship. An ontology that cannot trace a derivation path
to GO-001 is non-canonical and may not be referenced by any agent.

3. Parties

3.1 Ontology Steward

- Party Class: ROLE
- Authority: DOMAIN (the namespace owned by this ontology)
- Accountability: correctness, internal consistency, and evolution of the
  ontology across versions

3.2 Knowledge Curator

- Party Class: ROLE
- Authority: CONSTITUTIONAL
- Accountability: registry admission, namespace assignment, conflict
  detection across ontologies

3.3 Validation Authority

- Party Class: ROLE
- Authority: CONSTITUTIONAL
- Accountability: certification that the ontology satisfies all
  constitutional and structural requirements before publication

3.4 Governance Agent

- Party Class: AGENT
- Authority: CONSTITUTIONAL
- Accountability: approval of version changes, deprecation, and supersession

4. Obligations

Every ontology file shall:

4.1 Declare Identity

- Document ID (GO-NNN)
- Title
- Version (MAJOR.MINOR.PATCH)
- Status (DRAFT | PROPOSED | ACTIVE | DEPRECATED | RETIRED)
- Namespace URI (globally unique, registered in the Ontology Registry
  GO-006)

4.2 Declare Derivation

- `derives_from`: explicit reference to a parent ontology ID
- `imports`: list of ontology IDs whose classes are reused
- The derivation chain shall be acyclic and shall terminate at GO-001.

4.3 Declare Classes

For each class:

- class_id (namespaced IRI)
- label (human-readable)
- subclass_of (parent class within this ontology or an imported one)
- properties (typed, with cardinality where applicable)
- constraints (SHACL or equivalent)
- confidence_basis (how a node of this class earns its confidence)

4.4 Declare Relationships

For each relationship:

- relationship_id (namespaced IRI, drawn from GO-002 where possible)
- domain class
- range class
- cardinality
- inverse relationship (if any)
- transitivity / symmetry flags

4.5 Declare Constraints

- Invariants that must hold for every instance of the ontology
- Prohibition rules (what may never coexist)
- Validation queries that the Validation Authority shall run

5. Guarantees

5.1 Derivation Integrity

The ontology shall trace an acyclic path to GO-001. The Knowledge Curator
guarantees to verify this on every version change.

5.2 Namespace Uniqueness

The ontology's namespace URI shall be globally unique within Genesis. No
two active ontologies shall share a namespace.

5.3 Internal Consistency

The ontology shall contain no class that is its own ancestor, no
relationship whose domain and range are undefined, and no constraint that
contradicts another constraint in the same file.

5.4 Cross-Ontology Consistency

The ontology shall not redefine a class already defined in another active
ontology. Reuse is permitted via `imports`; redefinition is a breach.

5.5 Version Stamp

Every published version shall carry an immutable version identifier and a
provenance entry naming the Steward and approving Governance Agent.

6. Prohibited Behaviors

An ontology shall not:

- Introduce a class that conflicts with a Core Ontology class
- Introduce a relationship not present in GO-002 unless also registered there
- Use a namespace already owned by another active ontology
- Reuse an IRI for a different concept across versions
- Lower a constraint that was previously stricter without a Governance
  amendment
- Enter the PKG without Validation Authority certification

7. Penalties

- MINOR (typographic or formatting defect): returned to Steward for
  correction within one review cycle
- MAJOR (broken derivation, namespace collision, internal contradiction):
  the ontology is reverted to its last ACTIVE version; the Steward is
  notified; agents referencing the ontology are warned
- CRITICAL (contradiction with a Core Ontology, unauthorized redefinition of
  a GO-001 class, publication without validation): the ontology is RETIRED,
  the Steward is suspended, and the Governance Agent opens a constitutional
  review

8. Duration

- Start: Validation Authority certifies a version as ACTIVE
- End: the version is superseded by a newer ACTIVE version, or RETIRED by
  Governance
- An ACTIVE ontology remains in force until explicitly replaced. There is
  no implicit expiration.

9. Termination

- Supersession: a newer ACTIVE version takes over; the prior version
  becomes DEPRECATED and is retained for provenance
- Deprecation: Governance declares the ontology obsolete; it remains
  queryable but no new nodes may be created against it
- Retirement: the ontology is removed from the active registry; existing
  PKG nodes referencing it remain valid and traceable

10. Versioning

- MAJOR: breaking change (class removed, constraint tightened, namespace
  moved)
- MINOR: additive change (new class, new relationship, relaxed constraint
  with Governance approval)
- PATCH: correction (typographic, documentation, IRI normalization)

A MAJOR change requires a new ontology review and re-validation. A MINOR
change requires Steward approval and Validation Authority sign-off. A PATCH
change requires Steward approval only.

11. Compliance

This contract is enforced by the Validation Authority and the Governance
Agent. Every ontology file in `ontology/` shall conform. The Ontology
Registry (GO-006) is the canonical index of compliant ontologies; an
ontology not in the registry does not exist for the purposes of Genesis.

12. Invariants

- Derivation is acyclic and rooted at GO-001.
- Namespaces are unique.
- Versions are immutable once ACTIVE.
- Contradictions are rejected before publication.
- Retirement preserves provenance.
- Governance owns every lifecycle transition.