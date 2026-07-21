Genesis Knowledge Reference (GKR)
GKR-001 — Production Knowledge Graph Definition

Document ID: GKR-001
Title: Production Knowledge Graph Definition
Version: 1.0.0
Status: Foundational Knowledge Reference
Authority: Derived from GFS-010, GO-001, GO-002

1. Purpose

This document is the canonical conceptual definition of the Production
Knowledge Graph (PKG). It complements GFS-010, which is the formal
specification. GFS-010 defines the serialization, node and edge schemas,
and validation rules. GKR-001 defines what the PKG is, why it exists, how
it differs from a database, and how to think about it when designing
agents and workflows.

If GFS-010 and GKR-001 appear to conflict, GFS-010 is authoritative for
machine-checkable contracts; GKR-001 is authoritative for conceptual
clarity.

2. What the PKG Is

The PKG is the single canonical representation of production intelligence
inside Genesis. Every creative decision, every inferred fact, every
constraint, every relationship, and every confidence assessment lives in
the PKG. Every document Genesis produces — a screenplay, a storyboard, a
production plan, a validation certificate — is a materialized view of
the PKG, never a parallel source of truth.

The PKG is a directed labeled property graph (per GFS-010 §3). It is
composed of:

- Nodes, each an instance of an ontology class.
- Edges, each an instance of a semantic relationship from GO-002.
- Properties on both nodes and edges.
- Confidence on both nodes and edges.
- Provenance on both nodes and edges.

3. Why the PKG Exists

The PKG exists to make knowledge explicit, traceable, and validated
before any production activity begins. The Charter (GFS-000 §5) states:
"Knowledge precedes production." The PKG is how Genesis holds that
knowledge.

Without the PKG, Genesis would be a pile of documents. Documents are
opaque: they hide assumptions, they duplicate facts, they drift, and
they cannot be queried structurally. The PKG makes every fact addressable,
every assumption visible, and every contradiction detectable.

4. How the PKG Differs From a Database

A database stores data. The PKG stores knowledge. The distinction is not
rhetorical; it has structural consequences.

| Aspect | Database | PKG |
|--------|----------|-----|
| Unit | Row in a table | Node in a graph |
| Relationship | Foreign key | First-class edge with type and properties |
| Schema | Table definitions | Ontology (GO-001 + domain ontologies) |
| Semantics | Implicit in code | Explicit in GO-002 relationship types |
| Confidence | Not first-class | First-class on every node and edge |
| Provenance | Audit log, external | First-class on every node and edge |
| Query | Tabular joins | Graph traversal + semantic queries |
| Contradiction | Possible, undetected | Detectable via invariants |
| Evolution | Migration scripts | Additive versioning per GMM-002 |

The PKG may be stored in a graph database, but the graph database is an
implementation detail. The PKG is the graph itself, serialized as JSON-LD
per GFS-010 §4 for distribution.

5. PKG Structure

The PKG is divided into mandatory subgraphs (per GFS-010 §3.3):

- Narrative Subgraph — story, acts, sequences, scenes, beats.
- Character Subgraph — characters, DNA, relationships, arcs.
- World Subgraph — environments, locations, objects, cultures.
- Audience Subgraph — audience, experience, emotion targets.
- Production Subgraph — brief, plan, milestones, dependencies.

A subgraph is a named, versioned collection. Subgraphs reference each
other through cross-subgraph edges (e.g., a Scene features a Character,
a Scene occursIn an Environment). Cross-subgraph edges are the
integration surface and the most valuable edges in the graph.

6. Node Anatomy

Every node has, at minimum:

- id: UUID, immutable, assigned by Genesis.
- type: an ontology class from GO-001 or a domain ontology.
- label: human-readable name.
- properties: type-constrained key-value map.
- confidence: one of {EXPLICIT, INFERRED, CONFIRMED, ASSUMED, UNKNOWN}.
- created_at: ISO 8601 timestamp.
- provenance: the agent and session that created the node.

7. Edge Anatomy

Every edge has, at minimum:

- id: UUID.
- type: a relationship type from GO-002.
- source_id, target_id: existing node UUIDs.
- properties: type-constrained key-value map.
- confidence: one of {EXPLICIT, INFERRED, CONFIRMED, ASSUMED, UNKNOWN}.
- created_at.
- provenance.

8. Confidence Semantics

Confidence is not a numeric score. It is a categorical classification of
how a fact came to exist in the PKG.

- EXPLICIT — stated in the source material (the brief or creator input).
- INFERRED — derived by an agent from other PKG evidence.
- CONFIRMED — validated by a validator agent or by the creator.
- ASSUMED — adopted without evidence; flagged for review.
- UNKNOWN — a gap detected; the discovery loop must resolve this.

A PKG may not be certified while any node on a critical path carries
UNKNOWN. This is a constitutional invariant (GFS-000 §10, GFS-010 §5.3).

9. Provenance Semantics

Provenance is first-class. Every node and every edge records the agent
and session that created it. This enables:

- Traceability: every decision can be traced to its origin (GFS-000 §12).
- Audit: governance can review who decided what and when.
- Revision: the Revision Agent (GAS-027) can target the exact node that
  a validator flagged.
- Reproducibility: a session can be replayed from the provenance log.

10. Query Patterns

The PKG supports four families of queries:

10.1 Structural Queries

"Give me every Scene in Act II." This is a graph traversal: start at the
Story node, follow `go:contains` to Acts, filter to Act II, follow
`go:contains` to Sequences, then to Scenes.

10.2 Semantic Queries

"Which Characters appear in Scenes that evoke grief?" This combines
traversal with relationship semantics: traverse Scenes, filter by
`go:evokes` targeting an EmotionTarget of grief, then follow
`go:features` to Characters.

10.3 Confidence Queries

"Which Beats have UNKNOWN confidence?" This is a filter on the
confidence property. It drives the discovery loop.

10.4 Provenance Queries

"Which nodes were created by the Story Architect in session sess-001?"
This is a filter on the provenance property. It drives audit and
revision.

11. Versioning

The PKG is versioned as a whole (GFS-010 §6). Each certified version is
immutable. Version numbering is MAJOR.MINOR.PATCH:

- MAJOR: incompatible structural changes.
- MINOR: additive changes (new nodes, edges, subgraphs).
- PATCH: confidence upgrades, corrections, refinements.

During a session, the PKG is mutable. When the orchestrator certifies
readiness, the PKG is frozen into a Production Knowledge Package (PKP),
an immutable, signed, distributable artifact (GFS-010 §7).

12. Relationship to the PKP

The PKG is the live graph. The PKP is the sealed package. The PKP
contains:

- The PKG JSON-LD document.
- A manifest describing contents.
- Materialized views (screenplay, storyboard, plan, etc.).
- A validation certificate signed by governance.
- A provenance log of all decisions.

The PKP is what crosses the Genesis boundary to the Studio Engine. The
PKG never leaves Genesis.

13. Compliance

Every Genesis agent must read from and write to the PKG (GFS-010 §9).
No agent may maintain its own independent knowledge store. Temporary
working memory is permitted during a reasoning session and must be
committed to the PKG before the session concludes. Violating this rule
breaks the single-source-of-truth invariant and is a constitutional
defect.