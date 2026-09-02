Genesis Integration (GINT)
GINT-001 — Neo4j Integration

Document ID: GINT-001
Title: Neo4j Integration
Version: 1.0.0
Status: Active
Authority: Derived from GFS-000

1. Purpose

Defines how Genesis integrates with Neo4j for storage and traversal of the
Production Knowledge Graph (PKG). Neo4j is the canonical runtime store for the
PKG; files and documents are materialized views of the graph.

2. Scope

- Covers graph schema, load paths, query patterns, and lifecycle.
- Does not cover LLM integration (GINT-002) or Movie OS handoff (GINT-003).
- Neo4j is the reference implementation; other graph stores may be substituted
  if they implement the same contract.

3. Graph Schema

### Node labels

- `Ontology` — a GO-NNN ontology record.
- `Class` — a class defined in an ontology.
- `Property` — a property on a class.
- `Relationship` — a relationship defined in an ontology.
- `Rule` — a rule defined in an ontology.
- `Production` — a production (root of a PKG).
- `Character`, `Scene`, `World`, `Narrative`, `Decision` — PKG entity nodes.
- `Assertion` — an individual classified assertion.

### Relationship types

- `DEFINED_IN` — Class → Ontology
- `HAS_PROPERTY` — Class → Property
- `HAS_RELATIONSHIP` — Class → Relationship
- `PARENT_OF` — Class → Class (inheritance)
- `GOVERNS` — Ontology → Class | Relationship | Rule
- `PART_OF` — entity → Production
- `EVIDENCE_FOR` — Assertion → Decision
- `DERIVED_FROM` — Assertion → source (agent, workflow, human)
- `CONTRADICTS` — Assertion → Assertion (used by consistency checks)

### Properties on every node

- `genesis_id` — stable Genesis identifier
- `classification` — one of {Explicit, Inferred, Confirmed, Assumed, Unknown}
- `confidence` — float in [0, 1]
- `origin` — agent ID, workflow ID, or human
- `evidence` — array of references
- `revision` — array of revision records
- `created_at`, `updated_at` — ISO 8601

4. Load Paths

### Metamodel load

- Source: compiled ontology graph payloads (GEN-GRAPH, GCMP-001).
- Target: `Ontology`, `Class`, `Property`, `Relationship`, `Rule` nodes.
- Trigger: `genesis compile --ontology` or `genesis generate --kind graph --from ontology`.
- Idempotent: re-running updates existing nodes by `genesis_id`.

### PKG load

- Source: a compiled PKG.
- Target: `Production` and entity nodes plus `Assertion` nodes.
- Trigger: `genesis compile --pkg` or `genesis generate --kind graph --from pkg`.
- Idempotent on `genesis_id`; assertions are appended with revision history.

5. Query Patterns

### Consistency check

```cypher
MATCH (a:Assertion)-[:CONTRADICTS]->(b:Assertion)
WHERE a.classification IN ['Confirmed','Explicit']
  AND b.classification IN ['Confirmed','Explicit']
RETURN a, b
```
Zero rows required for certification (GVAL-001 M004).

### Confidence audit

```cypher
MATCH (d:Decision)
WHERE d.required = true AND d.confidence < d.threshold
RETURN d
```
Zero rows required for certification (GVAL-003 G13).

### Traceability lookup

```cypher
MATCH (a:Assertion)-[:DERIVED_FROM]->(src)-[:EVIDENCE_FOR]->(d:Decision)
RETURN a, src, d
```

6. Lifecycle

- A PKG is loaded into a dedicated database (or graph project) per production.
- The database is created by `genesis init` and named by the production ID.
- Certification writes a `Certificate` node linked to the `Production` node.
- Handoff to Movie OS Studio Engine (GINT-003) reads the graph; the Studio
  Engine never writes back to the Genesis graph.

7. Configuration

```yaml
graph:
  provider: neo4j
  uri: bolt://localhost:7687
  user: ${NEO4J_USER}
  password: ${NEO4J_PASSWORD}
  database: genesis-${production_id}
```

- Credentials come from environment variables, never from config files.
- The database name is derived from the production ID to enforce isolation.

8. Failure Modes

- Connection refused: CLI exits 3 (dependency missing) per GTOOL-001.
- Auth failure: reported; no fallback to insecure mode.
- Schema drift: if the metamodel does not match the loaded ontology set,
  `genesis compile` aborts with a validation report.

9. Dependencies

- Compiler: GCMP-001 (produces graph payloads)
- Generators: GGEN-001 (GEN-GRAPH)
- Validator: GVAL-001 (uses queries for consistency and traceability)
- CLI: GTOOL-001 (`--config` graph section)