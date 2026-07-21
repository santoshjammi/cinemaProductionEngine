Genesis Schema Specification (GSS)
GSS-502 — Agent GraphQL Schema

Document ID: GSS-502
Title: Agent GraphQL Schema
Version: 1.0.0
Status: Schema Specification
Authority: Derived from GFS-010, GSS-001, GSS-302

1. Purpose

This document specifies the GraphQL schema for agent operations on the PKG.
Where GSS-501 is read-only and client-facing, GSS-502 is the agent-facing
mutation surface: creating nodes, asserting edges, recording decisions,
opening and closing discovery sessions, and requesting validation.

Only authenticated Genesis agents may call mutations on this schema. Human
clients use GSS-501 plus REST endpoints (GSS-601).

2. Schema Topology

```
Mutation
  startSession
  endSession
  assertNode
  updateNode
  retractNode
  assertEdge
  retractEdge
  recordDecision
  requestValidation
  sealPKG
```

3. Shared Types

Imports the read types from GSS-501: `Node`, `Edge`, `PKG`, `Provenance`,
`Agent`, `Session`, `KnowledgeClass`, `ValidationStatus`, `Urn`,
`Confidence`, `DateTime`.

```graphql
enum MutationStatus { OK REJECTED PARTIAL }
type MutationResult {
  status: MutationStatus!
  message: String
  affected: [Urn!]!
  warnings: [String!]!
}
```

4. Session Mutations

```graphql
type Mutation {
  startSession(agentId: Urn!, role: String!, parentSessionId: Urn): Session!

  endSession(sessionId: Urn!, summary: String): MutationResult!
}
```

A session MUST be open before any other mutation may be called. Every later
mutation takes a `sessionId` argument that MUST match an open session owned by
the calling agent.

5. Node Mutations

```graphql
type Mutation {
  assertNode(
    sessionId: Urn!
    pkgId: Urn!
    conceptType: Urn!              # subclass of go:Thing
    canonicalName: String
    displayName: String
    attributes: JSON
    confidence: Confidence!
    knowledgeClass: KnowledgeClass!
    evidence: [EvidenceInput!]!
  ): Node!

  updateNode(
    sessionId: Urn!
    nodeId: Urn!
    attributes: JSON                # partial update
    confidence: Confidence
    knowledgeClass: KnowledgeClass
    rationale: String!
  ): Node!

  retractNode(
    sessionId: Urn!
    nodeId: Urn!
    rationale: String!
  ): MutationResult!
}
```

6. Edge Mutations

```graphql
type Mutation {
  assertEdge(
    sessionId: Urn!
    pkgId: Urn!
    sourceId: Urn!
    targetId: Urn!
    predicate: Urn!                 # subclass of go:Relationship
    confidence: Confidence!
    knowledgeClass: KnowledgeClass!
    evidence: [EvidenceInput!]!
  ): Edge!

  retractEdge(
    sessionId: Urn!
    edgeId: Urn!
    rationale: String!
  ): MutationResult!
}
```

7. Decision Recording

```graphql
input EvidenceInput {
  sourceUri: String!
  sourceType: EvidenceType!
  excerpt: String
  weight: Float
}

enum EvidenceType {
  BRIEF_LINE
  ONTOLOGY_CLAUSE
  PKG_NODE
  PKG_EDGE
  EXTERNAL_REFERENCE
  AGENT_OUTPUT
  USER_INPUT
}

input OptionInput {
  id: Urn!
  label: String!
  rationale: String
}

type Mutation {
  recordDecision(
    sessionId: Urn!
    question: String!
    affectedDomain: Urn!
    consideredOptions: [OptionInput!]!
    chosenOption: Urn!
    confidence: Confidence!
    rationale: String!
    dependsOnDecisions: [Urn!]
    evidence: [EvidenceInput!]!
  ): DecisionRecord!
}
```

8. Validation and Sealing

```graphql
type Mutation {
  requestValidation(
    sessionId: Urn!
    pkgId: Urn!
    shapes: [Urn!]                  # defaults to GSS-201 + GSS-205
  ): ValidationResult!

  sealPKG(
    sessionId: Urn!
    pkgId: Urn!
    readinessReport: Urn!           # link to readiness artifact
  ): MutationResult!
}
```

`sealPKG` MUST refuse if any validation result is not `PASS`.

9. Subscriptions

```graphql
type Subscription {
  nodeChanged(pkgId: Urn!, conceptType: Urn): NodeEvent!
  edgeChanged(pkgId: Urn!, predicate: Urn): EdgeEvent!
  validationCompleted(pkgId: Urn!): ValidationResult!
}

type NodeEvent {
  kind: EventKind!
  node: Node!
  at: DateTime!
  by: Agent!
}
type EdgeEvent {
  kind: EventKind!
  edge: Edge!
  at: DateTime!
  by: Agent!
}
enum EventKind { CREATED UPDATED RETRACTED }
```

10. Authorization

- Mutations require `agent:write` scope and a valid `agentId`.
- `startSession` verifies the agent is registered in the Agent Registry.
- Each mutation verifies `sessionId` belongs to the calling agent and is
  open.
- `sealPKG` requires the Governance role (GAS-027).

11. Validation at the Boundary

Resolvers MUST enforce:

- `conceptType` is a subclass of `go:Thing` in the loaded OWL ontology.
- `predicate` is a subclass of `go:Relationship`.
- `confidence ∈ [0,1]`.
- `evidence` is non-empty for `INFERRED` and `ASSUMED` assertions.
- `recordDecision.chosenOption ∈ consideredOptions`.

12. Provenance Generation

Every mutation automatically attaches a `Provenance` record referencing the
`sessionId`, `agentId`, and (where applicable) the `decisionId`. Agents do not
author provenance manually; the schema layer enforces traceability per GFS-000
§8.

13. Example Mutation

```graphql
mutation {
  startSession(agentId: "urn:genesis:agent:character-architect",
               role: "architect") { id }
}

mutation {
  assertNode(
    sessionId: "urn:genesis:session:s1",
    pkgId: "urn:genesis:pkg:abc",
    conceptType: "urn:genesis:ontology:Character",
    canonicalName: "Arjuna",
    attributes: { archetype: "reluctant_hero", role_in_story: "protagonist" },
    confidence: 0.92,
    knowledgeClass: CONFIRMED,
    evidence: [
      { sourceUri: "brief#L14", sourceType: BRIEF_LINE,
        excerpt: "reluctant warrior", weight: 0.8 }
    ]
  ) { id confidence }
}
```

14. Relationship to Other Schemas

- Read types inherited from GSS-501.
- Provenance modeled per GSS-302 (Provenance RDF Vocabulary).
- Backed by GSS-301 (PKG RDF Serialization) storage.
- Agent registry defined by GAS-001.

15. Revision History

- 1.0.0 — Initial draft. Mutation surface for agents.