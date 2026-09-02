Genesis Pattern (GP)
GP-ARCH-001 — Layered Architecture Pattern

Document ID: GP-ARCH-001
Title: Layered Architecture Pattern
Version: 1.0.0
Status: Pattern
Authority: Derived from GFS-000, GFS-003, GFS-005

1. Purpose

The Layered Architecture Pattern defines how Genesis is decomposed into horizontal strata, each with a single responsibility and a strictly downward dependency. Layers prevent the most common Genesis failure mode: agents, ontologies, and workflows silently coupling across concerns so that a change in one ripple unpredictably into another.

In Genesis, layering is constitutional. The Charter declares knowledge precedes production and inference must be distinguished from fact. Layering operationalizes those principles by separating the knowledge foundation from the reasoning engine from the workflow engine from the agent layer. A higher layer may depend on a lower one; a lower layer never depends on a higher one.

2. When to Apply

Apply this pattern when:

- Designing a new subsystem inside Genesis (knowledge, reasoning, workflow, agents, governance).
- Adding a capability that crosses ontologies, agents, and pipelines.
- Refactoring a subsystem that has accumulated cross-layer coupling.
- Establishing the boundary between Genesis and a downstream engine (Studio Engine, Learning Engine).

Do not apply this pattern for single-file utilities — layering is architectural, not file-system cosmetics.

3. Layer Catalog

Genesis is organized into five canonical layers, from bottom to top:

- L0 — Constitutional Foundation. The Charter, constitution documents, and immutable invariants. Depends on nothing. Everything depends on L0.
- L1 — Ontological Foundation. GO-001 Core Ontology, GO-002 Relationship Catalog, and every registered domain ontology. Depends on L0 only.
- L2 — Knowledge & Reasoning. The Production Knowledge Graph, the Reasoning Catalog, the Reasoning Engine, the Discovery Engine. Depends on L1 for vocabulary and L0 for authority.
- L3 — Workflow & Agents. Workflows, agent specifications, agent runtime contracts, prompts. Depends on L2 for knowledge and L1 for vocabulary.
- L4 — Governance & Production. Governance agents, approval chains, escalation, production readiness certification, the Production Knowledge Package. Depends on L3 for orchestration and L2 for knowledge.

A sixth, external layer L-1 — Downstream Engines — sits outside Genesis. Genesis exports to L-1 only through the Production Knowledge Package; it never imports from L-1.

4. Dependency Rules

- Downward only — a layer may depend only on the same layer or a lower one.
- No skip-layer cycles — L3 may depend on L1 but may not bypass L2's contracts to mutate PKG internals directly.
- No upward imports — L1 may not import an agent or workflow concept. Violations are architectural defects.
- Same-layer contracts — components in the same layer communicate through declared contracts, not through shared mutable state.
- Cross-layer versioning — when an L1 ontology changes, L2/L3/L4 consumers are updated per the Ontology Versioning Pattern (GP-ONT-002).

5. Layer Boundaries

Each layer exposes a typed surface:

- L0 exposes constitutional invariants and amendment rules.
- L1 exposes registered ontologies, SHACL shapes, and the Relationship Catalog.
- L2 exposes PKG read/write APIs, the Reasoning Catalog, and the Discovery API.
- L3 exposes agent specs, workflow manifests, and prompt contracts.
- L4 exposes the Production Knowledge Package, approval records, and the Production Readiness Certificate.

A higher layer consumes only the exposed surface. Internal structure of a lower layer is off-limits.

6. Workflow

6.1 Identify the Layer

When adding a component, place it in the highest layer it requires. A component that needs only ontology vocabulary belongs to L1; a component that needs reasoning belongs to L2; a component that orchestrates agents belongs to L3.

6.2 Declare Dependencies

The component's spec lists its layer and its dependencies on lower layers. Dependencies must be on exposed surfaces only. Undeclared dependencies are architectural defects.

6.3 Verify No Upward Coupling

A reviewer (automated or human) checks that no dependency points upward. Cyclic dependencies are rejected at registration.

6.4 Version the Surface

Any change to an exposed surface follows the versioning pattern of that layer (GP-ONT-002 for L1, the Reasoning Catalog policy for L2, the Workflow Versioning policy for L3, the Governance Constitution for L4).

7. Use Inside Genesis

- The Story Architect Agent (L3) reads PKG (L2), uses GO-101 Narrative Ontology (L1), and conforms to the Charter (L0). It does not modify the ontology or the constitution.
- The Reasoning Engine (L2) reads ontologies (L1) and writes to the PKG (L2). It does not invoke agents.
- The Governance Agent (L4) reads the PKG (L2), the workflow manifest (L3), and certifies readiness. It does not modify ontologies.
- Downstream engines (L-1) consume the Production Knowledge Package (L4) and never write back.

8. Worked Example

Adding a new Music Composer Agent:

1. Layer: L3 (orchestrates knowledge and reasoning into a music plan).
2. Dependencies: GO-105 World Ontology (L1), PKG read API (L2), Workflow Manifest for Stage 5 (L3).
3. No upward coupling: the agent does not modify ontologies or the Charter.
4. Surface: exposes a Music Plan output contract consumed by downstream Studio Engine (L-1) via the Production Knowledge Package (L4).

9. Anti-Patterns

- An agent that writes directly to an ontology file. Ontologies are L1; agents are L3.
- A workflow that embeds constitutional rules instead of referencing L0.
- A reasoning engine that invokes an agent — reasoning is L2, agents are L3.
- A Production Knowledge Package that imports Studio Engine types — L4 may not import from L-1.
- Skipping the dependency declaration — undeclared coupling is the most common layering defect.

10. Exit Criteria

Layering is complete when:

- Every component declares its layer and its lower-layer dependencies.
- No upward dependency exists.
- Every cross-layer interaction goes through an exposed surface.
- The layer catalog is reflected in the directory structure and the registry.
- A reviewer has signed off on the dependency graph.