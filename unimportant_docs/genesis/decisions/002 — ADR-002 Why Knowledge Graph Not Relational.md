Genesis Architecture Decision Record (ADR)

ADR-002 — Why Knowledge Graph Not Relational

Document ID: ADR-002
Title: The Production Knowledge Graph is a Property Graph, Not a Relational Schema
Version: 1.0.0
Status: Accepted
Authority: Derived from GFS-000 Constitutional Charter §5, §10, §12

Date: 2025-01-03
Decision Maker: Chief Architect
Reviewer: Governance Agent
Supersedes: none
Superseded By: none
Related Documents: GFS-000, GO-001, GO-002, GARCH-001, GARCH-002, ADR-001

1. Context

The Constitutional Charter declares that "knowledge is canonical" (GFS-000 §5) and that "the Production Knowledge Graph is the canonical representation of production intelligence" (§5). The Charter further requires that "every decision must be traceable" (§12) and that "inference must be distinguished from fact" (§10). Together these requirements describe a data structure that must:

- Represent entities of many types (characters, worlds, themes, shots, locations, conflicts, evidence, approvals)
- Represent relationships between those entities that are themselves semantically meaningful and themselves carry metadata (confidence, provenance, version)
- Support queries that traverse relationships of arbitrary depth (e.g., "find every decision that depends, directly or transitively, on this assumption")
- Support provenance tracing from any assertion back through every supporting assertion to source material
- Support contradiction detection across large connected subgraphs
- Support schema evolution without destructive migration, because productions evolve as they are authored
- Support confidence propagation from supporting nodes to derived nodes
- Survive the addition of new relationship types without rewriting existing data

Productions are inherently relational in the semantic sense. A character supports a narrative. A narrative expresses a theme. A theme evokes an emotion. An emotion creates an audience experience. A shot depends on a character, a location, a mood, a piece of evidence, and a prior decision. The meaning of a production is the sum of these connections, not the sum of its entities in isolation.

The question was therefore: what data structure should the Production Knowledge Graph be implemented on?

Two candidates were considered seriously:

- A relational schema (tables with foreign keys, possibly with JSON columns for flexible attributes)
- A property graph (labeled nodes and typed edges, each carrying properties)

Document stores and object stores were considered informally and rejected early because they cannot express relationships as first-class entities, which the Charter requires.

2. Decision

The Production Knowledge Graph is implemented as a property graph. Nodes are typed by ontology concept; edges are typed by semantic predicates from GO-002. Both nodes and edges carry properties, including confidence, provenance anchor, version, and lifecycle state. The graph is the only canonical store. Relational databases may be used for derived indexes, caches, and operational stores, but never as the source of truth.

The decision is elaborated by the following binding rules:

- The PKG is stored in a graph database whose query surface supports labeled property graphs (per GARCH-002 §3).
- Every node carries an `ontology_type` reference to a concept declared in GO-001 or a derived ontology.
- Every edge carries a `predicate` drawn from the Semantic Relationship Catalog (GO-002).
- Every node and every edge carries `confidence`, `version`, `state`, and a `provenance_anchor`.
- Relationships are first-class entities. They are not implied by shared foreign keys; they are explicit, queryable, and versioned.
- Schema evolution is additive. New node types and new predicates may be added; existing ones may not be redefined.
- Relational stores may exist alongside the PKG only as derived projections (e.g., a confidence summary table, a validation findings log). They must be rebuildable from the PKG.

3. Status

Accepted on 2025-01-03 by the Chief Architect, reviewed and approved by the Governance Agent.

No supersession is anticipated. A move to a non-graph canonical store would require revisiting GFS-000 §5 and GO-001 §22 and would constitute a constitutional-level change.

4. Consequences

4.1 Positive Consequences

- The schema matches the domain. Productions are graphs. Forcing them into tables produces join-heavy, brittle schemas that must be redesigned every time the production evolves.
- Semantic queries are first-class. "Find every decision that transitively depends on this assumption" is a three-line graph query. In a relational schema it is a recursive CTE or an application-level traversal, both of which perform poorly and read badly.
- Provenance tracing is natural. Provenance is a path through the graph. A graph database returns paths natively; a relational database returns rows that must be reassembled into paths by the application.
- Relationships carry metadata. In a property graph, an edge can have its own confidence, version, and provenance. In a relational schema, a relationship is a row in a join table that must carry those columns, which is workable but awkward and explodes in number as relationship types proliferate.
- Schema evolution is additive. New predicates can be introduced without migrating existing data. New node types can be introduced without touching existing tables. This is critical because productions are authored incrementally.
- Inheritance is natural. The Core Ontology's `is_a` hierarchy maps directly to subtyping in the graph. A Protagonist is a Character is a Creative Thing is a Thing. Relational schemas model inheritance through joins or single-table inheritance, both of which have well-known problems.
- Subgraph extraction is cheap. An agent that wants its working set pulls a bounded subgraph with one query. In a relational schema the same operation requires many joins.
- Contradiction detection is tractable. The `contradicts` predicate and its symmetric propagation rule are expressible as a graph pattern. Relational contradiction detection typically requires bespoke queries per contradiction type.

4.2 Negative Consequences

- Graph databases are less mature than relational databases. Tooling, operational experience, and hosted offerings are improving but are not as universal as PostgreSQL or MySQL.
- Graph query languages vary. Cypher, Gremlin, SPARQL, and GQL differ in syntax and capability. Lock-in risk exists at the query layer. The Reference Architecture mitigates this by mandating a graph-agnostic query surface in GARCH-002 §3.4.
- Reporting and analytics favor relational data. Business reports, dashboards, and aggregate metrics are easier to build on tables. The mitigation is the derived relational store: projections of the PKG into tables for analytics, rebuilt on demand.
- Operational tooling for graph databases is thinner. Backup, restore, replication, and observability are less standardized than for relational systems. Operators must invest in graph-specific expertise.
- Graphs can grow without bound if discipline is not enforced. Without schema constraints, a graph can accumulate ad hoc predicates and node types until it becomes unreadable. The Ontology Layer and the Validation Engine enforce this discipline.
- Transactions across very large graphs can be slower than relational transactions on comparable data volumes. The mitigation is subgraph-scoped transactions: agents transact only on the subgraphs they touch.

4.3 Neutral Consequences

- The team's vocabulary shifts toward graph terminology: predicates, traversal, closure, neighborhood. Future ADRs and specifications must use this vocabulary consistently.
- The PKG becomes the central engineering surface. Whatever graph database is chosen becomes the most carefully operated subsystem in Genesis.
- Relational stores become second-class citizens in the architecture. They exist for projections and operational convenience, never for truth.

5. Alternatives

5.1 Alternative 1: Relational Schema with Join Tables for Relationships

Description: The PKG would be stored as a set of relational tables. Each ontology concept maps to a table. Each relationship type maps to a join table carrying the predicate, endpoints, and metadata columns.

Advantages:
- Mature tooling. Every team knows relational databases.
- Universal hosting. Every cloud offers managed PostgreSQL or MySQL.
- Strong analytics. Reporting and dashboards are trivial.
- Mature transaction semantics. ACID is well understood and well supported.

Disadvantages:
- Relationship metadata becomes join-table metadata. Every new predicate requires a new join table or a polymorphic join table, both of which are awkward.
- Traversal is expensive. Multi-hop queries require recursive CTEs or application-level loops, both of which perform poorly and are hard to read.
- Provenance is awkward. A provenance path is a chain of evidence edges; in a relational store this is a chain of join rows that must be reassembled.
- Schema evolution is painful. Adding a new relationship type means migrating the schema, which is a production-risky operation.
- Inheritance is painful. Single-table inheritance produces wide sparse tables; class-table inheritance produces many joins.
- The schema does not match the domain. Productions are graphs. Forcing them into tables produces a constant translation tax.

Rejection Rationale: The relational model fights the domain at every turn. The cost of the translation tax—engineering time, query complexity, schema migration risk—exceeds the cost of adopting a graph database. The relational model remains valuable for derived analytics projections, which is why the Reference Architecture permits derived relational stores alongside the canonical graph.

5.2 Alternative 2: Document Store with Embedded Relationships

Description: The PKG would be stored as documents (e.g., MongoDB, CouchDB) with relationships embedded as arrays of references inside each document.

Advantages:
- Schema flexibility. Documents can evolve without migration.
- Simple single-entity queries. Fetching a character and its immediate neighbors is a single read.
- Familiar to web-era engineers.

Disadvantages:
- Relationships are not first-class. They are embedded as reference arrays, which means they cannot carry their own metadata (confidence, provenance, version) without becoming nested objects, at which point the document store is reinventing a graph database badly.
- Traversal is application-level. Multi-hop queries require N reads, one per hop.
- Provenance tracing is impossible to do efficiently. Every hop is a separate query.
- Contradiction detection requires scanning many documents.
- Bidirectional consistency is hard. If A references B, B must also reference A, or the relationship is invisible from B's side.

Rejection Rationale: A document store cannot treat relationships as first-class entities, which the Charter requires. It would force the application to reinvent graph semantics on top of documents, which is worse than using a graph database directly.

5.3 Alternative 3: Hybrid — Relational for Entities, Graph for Relationships

Description: Entities (nodes) would be stored in a relational database; relationships (edges) would be stored in a graph database. The two stores would be kept consistent by the application.

Advantages:
- Best of both worlds for analytics. Entities are in tables for reporting; relationships are in a graph for traversal.
- Allows incremental adoption. Teams can start relational and add the graph later.

Disadvantages:
- Two stores must be kept consistent. Distributed transaction semantics or eventual consistency must be introduced.
- Operational complexity doubles. Two databases to back up, monitor, and upgrade.
- Provenance is split across stores. A node's metadata is in the relational store; the edges that support it are in the graph store. Queries must join across stores in the application.
- The complexity is not justified. The graph database already handles entity storage well; there is no need for a second store.

Rejection Rationale: The hybrid model doubles operational complexity for marginal analytics convenience. The derived relational store pattern (rebuild tables from the graph for analytics) delivers the same benefit without distributed consistency problems.

6. Compliance

6.1 Validation Rules

The Validation Engine (S3 per GARCH-002) enforces the following invariants:

- Every node in the PKG must carry an `ontology_type` that resolves to a published concept in GO-001 or a derived ontology.
- Every edge in the PKG must carry a `predicate` that resolves to a published predicate in GO-002.
- Every node and every edge must carry a `confidence` value drawn from the five-level enumeration (EXPLICIT, INFERRED, CONFIRMED, ASSUMED, UNKNOWN).
- Every node and every edge must carry a `provenance_anchor` that resolves to an entry in the Provenance Ledger.
- No relationship may exist that is not expressed as an explicit edge. Foreign-key-style implied relationships are forbidden.
- No relational store within Genesis may be marked canonical. All relational stores must be rebuildable from the PKG.

6.2 Governance Gates

- The Architecture Review gate (per the Governance Constitution) must approve any proposal to introduce a new persistent store inside Genesis. Adding a derived relational store for analytics requires governance approval and a documented rebuild procedure.
- The Ontology Review gate must approve any new predicate added to GO-002 before it may be used in the PKG.

6.3 Audit Checks

- Query for any node whose `ontology_type` does not resolve to a published concept. Such nodes indicate schema drift.
- Query for any edge whose `predicate` does not resolve to a published predicate. Such edges indicate relationship drift.
- Query for any node or edge lacking a `provenance_anchor`. Such entities indicate a write that bypassed the Provenance Ledger.
- Query for any persistent store inside Genesis that is not the PKG and is not documented as a derived projection. Such stores indicate unauthorized canonicality.

6.4 Amendment Process

This ADR may be amended by supersession. A superseding ADR proposing a non-graph canonical store must demonstrate that the invariants above can still be satisfied and must address every negative consequence enumerated in this ADR's rejection of the relational alternative.

7. References

- GFS-000 Constitutional Charter, §§5, 10, 12
- GO-001 Genesis Core Ontology, §§5, 12, 16, 22
- GO-002 Semantic Relationship Catalog (referenced)
- GARCH-001 Enterprise Architecture, §§2, 4
- GARCH-002 Reference Architecture, §3
- ADR-001 Why Genesis is Pre-Production Only

8. Notes

The graph choice is the second architectural cornerstone of Genesis, after the pre-production boundary. Together, ADR-001 and ADR-002 define the shape of the system: Genesis is a knowledge system, and its knowledge is a graph. Every other decision flows from these two.

9. Sign-off

| Role | Name | Date | Signature |
|------|------|------|----------|
| Decision Maker | Chief Architect | 2025-01-03 | (signed) |
| Reviewer | Governance Agent | 2025-01-04 | (signed) |
| Governance Agent | Governance Agent | 2025-01-04 | (signed) |