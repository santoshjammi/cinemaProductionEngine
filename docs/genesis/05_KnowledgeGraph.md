Genesis Master Specification
05 — Knowledge Graph

Document ID: GMS-005
Title: Genesis Master Specification — Knowledge Graph
Version: 1.0.0
Status: Master Specification
Authority: Derived from GARCH-001, GARCH-002, GARCH-003, GFS-003

1. Purpose

This document describes the Production Knowledge Graph (PKG): its structure, its query patterns, its materialization, and its storage. The PKG is the central, canonical data structure of Genesis.

2. What the PKG Is

The PKG is a directed, typed, provenance-annotated graph. Nodes are instances of ontology concepts. Edges are instances of relationships from GO-002. Every node and every edge carries confidence and provenance.

The PKG is the single source of truth. Documents, prompts, manifests, and reports are projections of the PKG, not canonical data.

3. What the PKG Contains

- Instances of every Core and Domain ontology concept (Thing, Character, World, Narrative, Scene, Shot, etc.).
- Semantic relationships between instances (depends_on, supports, evokes, contradicts, derives_from, part_of, instance_of, references, implies, refines).
- Confidence classifications (EXPLICIT, INFERRED, CONFIRMED, ASSUMED, UNKNOWN) per GFS-000.
- Provenance records linking each assertion to its source, agent, evidence, and timestamp.
- Version history and revision metadata.
- Validation status and governance approval state.

4. What the PKG Does Not Contain

- Media assets (images, audio, video).
- Rendered documents (those are materialized views).
- Provider-specific prompts (those are generated on demand).
- Implementation artifacts (code, configs, binaries).

5. Canonicality Rules

- Any data not present in the PKG is considered nonexistent within Genesis.
- Any data present in the PKG but not validated is considered advisory.
- Any data present and validated is considered authoritative.
- Any data present, validated, and approved is considered production-ready.

6. Structure

6.1 Nodes
Every node has: id (URI), type (GO concept), properties (object), provenance, confidence, revision, supersededBy.

6.2 Edges
Every edge has: id, type (GO-002 relationship), source, target, properties, provenance, confidence, revision.

6.3 Subgraphs
A subgraph is a query result containing a set of nodes and the edges between them. Subgraphs are the primary unit agents read.

6.4 Materialized Views
A materialized view is a derived projection: a screenplay, a shot list, a character bible, a prompt manifest. Views are immutable for a given PKG revision and may be regenerated on demand.

7. Query Patterns

The Semantic Layer (GARCH-003) exposes the PKG through a stack of projections:

- Layer A — Ontology: schema and constraints.
- Layer B — Instances: the actual nodes and edges.
- Layer C — Relationships: typed edges between instances.
- Layer D — Subgraphs: query results scoped by concept, relationship, or property.
- Layer E — Materialized Views: derived documents and manifests.

Agents query through Layers D and E. They never read raw storage.

Supported query shapes:
- By concept type (all `Character` nodes).
- By relationship (all `evokes` edges from a given node).
- By property (all nodes with `confidence = INFERRED`).
- By subgraph (all nodes reachable from a given root within N hops).
- By provenance (all assertions by a given agent).

8. Materialization

Materialization is the process of producing a derived view from the PKG. It is performed by the Materialization Service (S-MAT) on demand. Materialized views are caches, not sources. A view may be invalidated and rebuilt at any time without loss of knowledge.

Materialization inputs: a view template (GTMP-NNN) and a PKG revision. Output: a rendered document or manifest.

9. Storage

The PKG is persisted to a graph database. The reference architecture (GARCH-002) does not mandate a specific vendor. The storage engine must support:

- Typed nodes and edges.
- Property indexing.
- Provenance and confidence as first-class metadata.
- Immutable revisions.
- Append-only provenance ledger.
- Snapshotting for PKP assembly.

Three deployment shapes are supported:
- Local: embedded graph database on a single workstation.
- Cloud: distributed graph database on managed infrastructure.
- Hybrid: synchronized local and cloud instances with provenance preserved across sync.

10. Versioning

Every mutation creates a new revision. Revisions are immutable. The current revision is a pointer; rollback moves the pointer without overwriting history. Superseded nodes are retained for audit.

11. Write Discipline

- Only agents operating within constitutional authority may write.
- Every write carries provenance (agent, source, evidence, timestamp).
- Every write carries a confidence classification.
- Writes that violate ontology constraints are rejected by the Knowledge Layer.
- Writes that omit provenance are rejected by the Knowledge Layer.

12. Read Discipline

- Any agent or workflow may read the PKG through the Semantic Layer.
- Downstream consumers (Studio Engine) read only through the PKP or materialized views.
- No external system may read the live PKG directly.

13. Approval

This document is the consolidated knowledge graph reference. For any conflict, GARCH-002 and GARCH-003 prevail.