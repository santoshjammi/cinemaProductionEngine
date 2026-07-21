Genesis Architecture Specification (GAS)
GARCH-003 — Semantic Layer Architecture

Document ID: GARCH-003
Title: Semantic Layer Architecture
Version: 1.0.0
Status: Architecture Specification
Authority: Derived from GARCH-001, GO-001, GO-002, GFS-000

1. Purpose

This document defines the Semantic Layer Architecture of the Genesis Engine. The Semantic Layer is the set of mechanisms that turn the Production Knowledge Graph from a raw graph store into a queryable, filterable, traceable, and projectable knowledge system.

Where GARCH-002 specifies the physical subsystems, this document specifies how those subsystems cooperate to expose the PKG as a layered semantic surface consumed by agents, workflows, and the materialization service.

2. Semantic Stack

The Semantic Layer is organized as a stack of projections. Each layer is derived from the layer beneath it and never writes back downward.

Layer A — Ontology
Layer B — Instances
Layer C — Relationships
Layer D — Subgraphs
Layer E — Materialized Views

Every upper layer is a function of the layers beneath. None of them store canonical truth; only the PKG at Layer B (Instances) is canonical. Everything above is a derived projection.

3. Layer A — Ontology

3.1 Contents
The Core Ontology (GO-001), the Semantic Relationship Catalog (GO-002), and all derived Domain Ontologies (GO-101+). The Ontology Layer defines the vocabulary: which concept types exist, which relationship predicates are valid, and what each one means.

3.2 Role in the Semantic Stack
The Ontology Layer is the schema. It constrains the Instances Layer. A node may not exist in the PKG unless its `ontology_type` is declared in the Ontology Layer. An edge may not exist unless its `predicate` is declared in GO-002.

3.3 Immutability Constraint
Ontology concepts evolve only through the constitutional amendment process defined in GFS-000 and the Governance Constitution. Once a concept is Published, its canonical identifier and semantic meaning are immutable. Extensions may add concepts; they may not redefine existing ones.

4. Layer B — Instances

4.1 Contents
The PKG itself: concrete nodes that instantiate ontology concepts and edges that instantiate semantic relationships. Each node carries a confidence classification, a state, a version, and a provenance anchor.

4.2 Canonicality
Instances are the only canonical layer. Every other layer is derived. If a derived layer disagrees with the Instances Layer, the Instances Layer prevails.

4.3 Confidence Tagging
Every instance carries one of five confidence classifications per GFS-000 §10:
- EXPLICIT — directly stated by the creator in source material
- INFERRED — derived by an agent from existing knowledge
- CONFIRMED — inferred and subsequently validated against evidence
- ASSUMED — adopted without evidence for the purpose of forward progress
- UNKNOWN — acknowledged gap; candidate for discovery

Confidence is a first-class attribute. It travels with the instance through every upper layer and into every materialized view.

5. Layer C — Relationships

5.1 Contents
Edges between instances, each typed by a predicate from GO-002. Relationships are themselves instances: they carry confidence, provenance, and version just like nodes.

5.2 Semantic Predicates
Predicates are not arbitrary strings. They are drawn from the Semantic Relationship Catalog (GO-002), which declares for each predicate:
- Canonical name
- Domain and range (which concept types it may connect)
- Cardinality (one-to-one, one-to-many, many-to-many)
- Directionality (directed, bidirectional)
- Transitivity (transitive, intransitive)
- Symmetry (symmetric, asymmetric)
- Lifecycle implications (does the relationship imply dependency, blocking, or inheritance?)

5.3 Reasoning Over Relationships
Because predicates carry semantic metadata, the Semantic Layer can perform graph reasoning:
- Transitive closure over `depends_on` to compute dependency chains
- Symmetric propagation over `contradicts` to detect inconsistency clusters
- Inheritance traversal over `is_a` to project specialized concepts to their general forms
- Path queries over arbitrary predicate sequences for exploration

6. Layer D — Subgraphs

6.1 Definition
A Subgraph is a bounded, named, queryable projection of the PKG. It contains a set of nodes and edges satisfying a declared predicate. Subgraphs are the unit of work for agents and workflows: an agent does not query the entire PKG; it operates on a subgraph scoped to its domain.

6.2 Subgraph Declarations
A subgraph is declared by a query expression over the PKG. Examples:
- `CharacterSubgraph` — all nodes of type Character and their one-hop relationships
- `NarrativeSubgraph` — all nodes reachable from a declared Story within three hops
- `ProductionSubgraph` — all nodes whose `state` is Approved or Validated
- `ProvenanceSubgraph` — all evidence nodes supporting a given target

6.3 Confidence Filtering
Subgraphs may be filtered by confidence. A common pattern is to materialize two projections of the same subgraph:
- `CharacterSubgraph.confirmed` — only CONFIRMED and EXPLICIT nodes
- `CharacterSubgraph.full` — all confidence levels, including ASSUMED and UNKNOWN

Agents that require high-trust inputs operate on `.confirmed` projections. Discovery agents that explore gaps operate on `.full` projections to find ASSUMED and UNKNOWN nodes.

6.4 Caching and Invalidation
Subgraphs are cacheable. They are invalidated when any node or edge they contain is modified. The Validation Engine publishes invalidation events on the message bus; subscribers discard stale caches and rebuild on demand.

7. Layer E — Materialized Views

7.1 Definition
A Materialized View is a structured projection of the PKG into a non-graph format suitable for a specific consumer. Examples include:
- A character brief (Markdown)
- A shot list (JSON)
- A production schedule (YAML)
- A provenance report (HTML)
- A deliverable manifest (JSON-LD)

7.2 Properties
- Views are derived. They are never edited directly. Edits are made to the PKG and the view is rebuilt.
- Views are versioned. A view carries the PKG revision it was built from.
- Views are signed. A view exported outside Genesis carries a signature derived from the PKP.
- Views are invalidatable. A view older than the current PKG revision is stale and must be marked as such.

7.3 The Materialization Service
The Materialization Service is the only subsystem permitted to produce Materialized Views. It reads subgraphs from Layer D, applies a view template, and writes the view to the export surface. Agents and workflows request views by name; they never assemble views themselves.

8. Querying the PKG

The Semantic Layer exposes a unified query surface over the PKG. All queries flow through the same path regardless of caller.

8.1 Query Primitives
- `get(id)` — fetch a single node by identifier
- `traverse(start_id, predicate, depth)` — follow a predicate up to N hops
- `subgraph(query)` — return a named subgraph matching the query expression
- `filter(subgraph, confidence_levels)` — return the subgraph restricted to declared confidence levels
- `provenance(target_id)` — return the full provenance chain for a node or edge
- `lineage(target_id)` — return all ancestor decisions that influenced the target
- `dependents(target_id)` — return all nodes that depend on the target
- `contradictions(subgraph)` — return all `contradicts` edges within the subgraph
- `gaps(subgraph)` — return all UNKNOWN or ASSUMED nodes within the subgraph

8.2 Confidence-Aware Queries
Every query may declare a minimum confidence threshold. The Semantic Layer silently excludes nodes below the threshold unless the query explicitly requests `include_unknown=true`. This makes confidence a first-class filter at the query surface, not an afterthought.

9. Provenance Tracing

9.1 The Provenance Anchor
Every node and edge in the PKG carries a `provenance_anchor` pointing to an entry in the Provenance Ledger (S2 per GARCH-002). The anchor records:
- The agent that created or last modified the entity
- The operation performed
- The evidence referenced
- The timestamp
- The agent signature

9.2 Forward Tracing
From any node, a consumer may ask: "What depends on this?" The `dependents` query returns the forward closure over `depends_on` edges. This is used by impact analysis when a node is revised.

9.3 Backward Tracing
From any node, a consumer may ask: "Why does this exist?" The `lineage` query returns the backward closure over `supports` and `evidence` edges, terminating at source material (the synopsis, the brief, or explicit creator input).

9.4 Contradiction Tracing
From any node flagged in a contradiction, the `contradictions` query returns all related `contradicts` edges and the subgraph that contains the conflict. This is used by the Validation Engine and the Governance Engine to drive resolution.

10. Confidence Propagation

Confidence does not travel alone. When a derived node is built from supporting nodes, its confidence is a function of its supporters' confidence.

10.1 Propagation Rules
- A node derived only from EXPLICIT supporters inherits EXPLICIT
- A node derived from a mix of EXPLICIT and CONFIRMED inherits CONFIRMED
- A node derived from any INFERRED supporter inherits at most INFERRED
- A node derived from any ASSUMED supporter inherits at most ASSUMED
- A node with no supporters inherits UNKNOWN

10.2 Recomputation
When a supporting node's confidence changes, all derived nodes must be re-evaluated. The Validation Engine triggers recomputation; the Semantic Layer applies propagation rules and updates derived confidence tags. The recomputation itself is recorded in the Provenance Ledger.

11. Subgraph Versioning

Subgraphs are versioned alongside the PKG. A subgraph snapshot carries:
- The PKG revision it was built from
- The query expression that produced it
- The confidence filter applied
- The timestamp

A subgraph may be replayed against any prior PKG revision, allowing historical analysis: "What did the CharacterSubgraph look like at revision 47?"

12. Materialized View Lifecycle

A Materialized View moves through the following states:

| State | Meaning |
|-------|---------|
| Requested | A consumer has requested the view |
| Building | The Materialization Service is assembling it |
| Ready | The view is built and matches the current PKG revision |
| Stale | The PKG has advanced beyond the view's source revision |
| Invalid | The view's source revision has been retired |
| Signed | The view has been signed for export as part of a PKP |

Stale views are flagged but still readable; consumers are warned. Invalid views are refused; consumers must rebuild.

13. Integration with the Materialization Service

The Materialization Service consumes Subgraphs (Layer D) and emits Materialized Views (Layer E). It is the only path by which knowledge leaves the graph form. Downstream engines and human-readable documents are always produced through this service.

14. Invariants

- The PKG is the only canonical layer.
- All upper layers are derived and rebuildable.
- Confidence is first-class at every layer.
- Provenance is mandatory at every layer.
- Subgraph caches may be discarded without loss.
- Materialized views may be invalidated without loss.
- No upper layer may write back to a lower layer.

15. Approval

This specification is approved as the canonical Semantic Layer Architecture of the Genesis Engine. All future query surfaces, subgraph declarations, materialized view templates, and provenance tooling must conform to it.