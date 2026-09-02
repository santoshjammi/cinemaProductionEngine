Genesis Schema Specification (GSS)
GSS-501 — Genesis GraphQL Schema

Document ID: GSS-501
Title: Genesis GraphQL Schema
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010, GSS-001, GSS-301

1. Purpose

This document specifies the GraphQL schema for querying the Production
Knowledge Graph. It exposes the PKG's nodes, edges, subgraphs, and provenance
to clients — dashboards, review tools, downstream engines — without
exposing the underlying storage. Reads only; mutations are in GSS-502.

GraphQL is preferred for human-facing query surfaces because it lets clients
request exactly the fields they need and traverse the graph naturally.

2. Schema Topology

```
Query
  production(id)
  pkg(id)
  node(id)
  edge(id)
  search(type, filter, sort, paging)
  graphQuery(root, traversal)
```

3. Type Definitions

```graphql
scalar DateTime
scalar Confidence   # float in [0,1]
scalar Urn

enum KnowledgeClass {
  EXPLICIT
  INFERRED
  CONFIRMED
  ASSUMED
  UNKNOWN
}

enum ValidationStatus {
  PASS
  FAIL
  PENDING
}
```

4. Core Types

```graphql
type Production {
  id: Urn!
  title: String!
  version: String!
  status: ProductionStatus!
  pkg: PKG!
  createdAt: DateTime
  updatedAt: DateTime
}

type PKG {
  id: Urn!
  productionId: Urn!
  version: String!
  nodes(filter: NodeFilter, paging: Paging): NodeConnection!
  edges(filter: EdgeFilter, paging: Paging): EdgeConnection!
  subgraphs: [Subgraph!]!
  validation: ValidationResult
  createdAt: DateTime
}

type Node {
  id: Urn!
  conceptType: Urn!             # subclass of go:Thing
  rdfType: [Urn!]!
  canonicalName: String
  displayName: String
  confidence: Confidence!
  knowledgeClass: KnowledgeClass!
  attributes: JSON               # arbitrary typed attributes
  edges(direction: EdgeDirection = BOTH, predicate: Urn): [Edge!]!
  provenance: Provenance!
  revisions: [Revision!]!
}

type Edge {
  id: Urn!
  source: Node!
  target: Node!
  predicate: Urn!                # subclass of go:Relationship
  confidence: Confidence!
  knowledgeClass: KnowledgeClass!
  provenance: Provenance!
}

type Subgraph {
  name: String!
  nodeIds: [Urn!]!
  edgeIds: [Urn!]!
  nodes: [Node!]!
  edges: [Edge!]!
}

type Provenance {
  agent: Agent!
  session: Session!
  decisionId: Urn!
  evidence: [String!]!
  confidence: Confidence!
  timestamp: DateTime!
}

type Agent { id: Urn! name: String role: String }
type Session { id: Urn! startedAt: DateTime endedAt: DateTime }

type Revision {
  number: Int!
  timestamp: DateTime!
  agent: Agent!
  reason: String
  supersedes: Revision
}

type ValidationResult {
  status: ValidationStatus!
  errors: [ValidationError!]!
  validatedAt: DateTime!
}

type ValidationError {
  severity: Severity!
  shape: Urn!
  focusNode: Urn!
  message: String!
  path: String
}

enum Severity { VIOLATION WARNING INFO }
enum ProductionStatus { DRAFT IN_DISCOVERY READY SEALED ARCHIVED }
enum EdgeDirection { OUT IN BOTH }
```

5. Connections (Relay-style)

```graphql
type NodeConnection {
  edges: [NodeEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}
type NodeEdge { node: Node! cursor: String! }
type EdgeConnection {
  edges: [EdgeItem!]!
  pageInfo: PageInfo!
  totalCount: Int!
}
type EdgeItem { edge: Edge! cursor: String! }
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

6. Filters

```graphql
input NodeFilter {
  conceptType: Urn
  knowledgeClass: KnowledgeClass
  minConfidence: Confidence
  maxConfidence: Confidence
  attributeMatches: JSON
  ids: [Urn!]
}

input EdgeFilter {
  predicate: Urn
  sourceId: Urn
  targetId: Urn
  minConfidence: Confidence
  knowledgeClass: KnowledgeClass
}

input Paging {
  first: Int
  after: String
  last: Int
  before: String
}
```

7. Query Root

```graphql
type Query {
  production(id: Urn!): Production
  productions(filter: ProductionFilter, paging: Paging): ProductionConnection!

  pkg(id: Urn!): PKG
  pkgForProduction(productionId: Urn!): PKG

  node(id: Urn!): Node
  edge(id: Urn!): Edge

  search(
    type: SearchType!
    filter: NodeFilter
    sort: [SortClause!]
    paging: Paging
  ): NodeConnection!

  graphQuery(
    root: Urn!
    traversal: TraversalSpec
    maxDepth: Int = 5
  ): GraphSlice!
}

input TraversalSpec {
  predicates: [Urn!]
  direction: EdgeDirection = OUT
  filter: NodeFilter
}

type GraphSlice {
  root: Node!
  nodes: [Node!]!
  edges: [Edge!]!
  depth: Int!
}

input SortClause { field: String! direction: SortDirection! }
enum SortDirection { ASC DESC }
enum SearchType { NODE EDGE SUBGRAPH }

input ProductionFilter {
  status: ProductionStatus
  titleContains: String
}
```

8. Example Queries

Fetch a production and its protagonist:

```graphql
query {
  production(id: "urn:genesis:prod:abc") {
    title
    pkg {
      nodes(filter: { conceptType: "urn:genesis:ontology:Character",
                      attributeMatches: { role_in_story: "protagonist" } }) {
        edges { node { id canonicalName confidence } }
      }
    }
  }
}
```

Trace a character's relationships, depth 3:

```graphql
query {
  graphQuery(
    root: "urn:genesis:node:arjuna-uuid",
    traversal: { predicates: ["urn:genesis:ontology:hasRelationship",
                              "urn:genesis:ontology:seeks_guidance_from"],
                 direction: OUT },
    maxDepth: 3
  ) {
    depth
    nodes { id canonicalName }
    edges { id predicate }
  }
}
```

9. Validation

The schema MUST validate with `graphql validate`. Resolvers MUST enforce:

- All `Urn` scalars are valid Genesis URNs.
- Confidence is in [0, 1].
- `knowledgeClass` is one of the five constitutional classes.
- `graphQuery.maxDepth` MUST be ≤ 10 to prevent traversal DoS.

10. Authorization

Read access is granted to authenticated clients with `pkg:read` scope. The
schema does not expose write operations. Writes are performed by agents via
GSS-502 (Agent GraphQL Schema).

11. Performance

- `node.attributes` is stored as JSON; resolvers SHOULD project requested
  fields only.
- `graphQuery` MUST respect a server-side `maxDepth` cap.
- Lists MUST default to `first: 50`.

12. Relationship to Other Schemas

- Backed by GSS-301 (PKG RDF Serialization) for storage.
- Pairs with GSS-502 (Agent GraphQL Schema) for mutations.
- Type names mirror GSS-401 OWL classes.

13. Revision History

- 1.0.0 — Initial draft. Read-only schema.