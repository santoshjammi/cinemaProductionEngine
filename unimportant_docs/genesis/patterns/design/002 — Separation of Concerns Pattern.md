Genesis Pattern (GP)
GP-DESIGN-002 — Separation of Concerns Pattern

Document ID: GP-DESIGN-002
Title: Separation of Concerns Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-005, GFS-009

1. Purpose

The Separation of Concerns Pattern defines how Genesis decomposes a system into components, each owning a single concern. Concerns are the dimensions along which Genesis changes — ontology, reasoning, workflow, agent, governance, format — and each must be owned by exactly one component. Overlapping concerns produce silent coupling; orphaned concerns produce unowned behavior.

In Genesis, separation is not stylistic — it is constitutional. The Charter separates Genesis from media generation absolutely. This pattern generalizes that separation to every internal boundary so that the same principle — one concern, one owner — governs the whole engine.

2. When to Apply

Apply this pattern when:

- Designing a new agent — name its single concern before its responsibilities.
- Reviewing an agent that has accumulated unrelated responsibilities (knowledge production + governance + format).
- Splitting a monolithic ontology into a layered stack (core / domain / vertical).
- Splitting a workflow stage that mixes creative reasoning with validation.
- Establishing the boundary between Genesis and a downstream engine.

Do not apply this pattern for trivial utilities — separation has a coordination cost that small utilities cannot justify.

3. Concern Catalog

Genesis recognizes seven canonical concerns:

- Ontology — what vocabulary exists and how it relates. Owner: ontologies under ontology/.
- Knowledge — what the PKG contains and how it is produced. Owner: reasoning + agents that produce Knowledge Objects.
- Reasoning — how conclusions are drawn. Owner: Reasoning Engine and Reasoning Catalog.
- Workflow — how agents are ordered and orchestrated. Owner: Production Orchestrator and workflow manifests.
- Validation — whether knowledge satisfies constraints. Owner: validators and SHACL shapes.
- Governance — whether decisions are approved. Owner: governance agents and the approval chain.
- Format — how knowledge is materialized into files. Owner: publishers and templates.

Each concern has exactly one owner. A component that touches two concerns is split; a concern with no owner is assigned.

4. Separation Rules

- One concern per component — an agent that produces knowledge and validates it is two components.
- Concerns communicate through contracts — never through shared mutable state.
- Concerns do not import each other's internals — they import each other's declared surfaces.
- Validation never mutates — validators emit Validation Reports; they do not fix knowledge.
- Governance never reasons — governance agents approve or deny; they do not infer.
- Format never owns knowledge — publishers materialize; they do not canonicalize.
- Reasoning never orchestrates — the Reasoning Engine draws conclusions; it does not sequence agents.

5. Workflow

5.1 Name the Concern

When designing a component, state its single concern in one phrase using the Concern Catalog. Example: "The Structural Validation Agent's concern is Validation."

5.2 Enumerate Responsibilities

List the component's responsibilities. Each must map to the named concern. A responsibility that maps to a different concern is a defect; either move it to the correct component or split the component.

5.3 Declare Inputs and Outputs

Declare the component's input contract and output contract. Inputs must come from the surfaces of other concerns; outputs must be consumed by surfaces of other concerns. Cross-concern internals are off-limits.

5.4 Verify No Overlap

A reviewer checks that no two components own the same concern. Overlaps are resolved by either merging (if the concern is genuinely one) or splitting (if it is two).

5.5 Register the Component

The component is registered in the appropriate registry (Agent Registry, Ontology Registry, Capability Registry) with its concern named. Undeclared concerns are architectural defects.

6. Use Inside Genesis

- Story Architect Agent — concern: Knowledge (Narrative Subgraph). Does not validate, does not govern, does not format.
- Structural Validation Agent — concern: Validation. Produces Validation Reports; does not fix defects.
- Governance Agent — concern: Governance. Approves or denies; does not produce knowledge.
- Revision Agent — concern: Workflow (revision routing). Does not reason about the defect; routes it.
- Publisher — concern: Format. Materializes the PKG into a Production Knowledge Package; does not modify knowledge.
- Reasoning Engine — concern: Reasoning. Draws conclusions; does not orchestrate.

7. Worked Example

A proposed "Screenplay Validator Agent" that (a) validates screenplay structure and (b) rewrites failing scenes to satisfy SHACL.

Concern check: validation is Validation; rewriting is Knowledge. Two concerns in one component — defect.

Split:

- Screenplay Validator Agent — concern: Validation. Emits a Validation Report naming failing scenes.
- Screenplay Revision Agent — concern: Knowledge. Receives the Validation Report and rewrites scenes.

The two communicate through the Validation Report contract. Neither owns the other's concern.

8. Anti-Patterns

- The "do-everything" agent that produces, validates, and governs in one spec.
- Validators that mutate the PKG to fix what they found.
- Governance agents that perform inference to justify approvals — reasoning belongs to the Reasoning Engine.
- Publishers that canonicalize knowledge — they only materialize.
- Reasoning engines that decide the next workflow stage — orchestration belongs to the Production Orchestrator.
- Two agents that both own Validation with overlapping scopes — overlaps produce inconsistent verdicts.

9. Exit Criteria

Separation of concerns is complete when:

- Every component names exactly one concern from the Concern Catalog.
- No two components own the same concern.
- Every cross-concern interaction goes through a declared surface.
- The component is registered with its concern named.
- A reviewer has signed off on the concern map.