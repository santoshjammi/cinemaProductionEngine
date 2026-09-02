Genesis Master Specification
01 — Architecture

Document ID: GMS-001
Title: Genesis Master Specification — Architecture
Version: 1.0.0
Status: Master Specification
Authority: Derived from GMS-000 and GARCH-001..003

1. Purpose

This document is the consolidated architecture overview of the Genesis Engine. It combines the 4-layer consumer view with the 7-layer Genesis internal architecture and the deployment models. It is the entry point for any engineer or agent who needs to understand how Genesis is built.

For full detail, refer to the GARCH-001..009 family in `architecture/`.

2. The 4-Layer Consumer View

From the perspective of anyone consuming Genesis output, the system exposes four layers:

2.1 Knowledge
The Production Knowledge Graph and the ontologies that type it. This is where truth lives. Consumers do not read this layer directly; they read its projections.

2.2 Specifications
Materialized views of the PKG: screenplays, shot lists, character bibles, world bibles, score plans, prompt manifests. These are derived, immutable for a given PKG revision, and may be regenerated on demand.

2.3 Production
The certified Production Knowledge Package. A frozen, signed, immutable projection of the PKG at the moment of certification. This is the boundary artifact.

2.4 Delivery
The handoff to the Studio Engine. The PKP plus the manifest of materializable views the Studio Engine may request.

Each layer is a strict function of the layer beneath it. None of them store canonical truth; only the PKG at the Knowledge layer is canonical.

3. The 7-Layer Genesis Architecture

Internally, Genesis is organized as seven layers. Each layer depends only on the layer directly beneath it and exposes a stable interface to the layer above. Cross-layer calls are forbidden.

3.1 Layer 0 — Core Ontology
Contents: GO-001 Core Ontology, GO-002 Semantic Relationship Catalog, GO-003 State and Lifecycle, GO-004 Confidence and Provenance.
Responsibility: Define the universal vocabulary, relationship types, lifecycle, and assertion metadata.

3.2 Layer 1 — PKG (Production Knowledge Graph)
Contents: PKG Store, Provenance Ledger, Confidence Registry, Validation Engine.
Responsibility: Store, version, query, and trace every knowledge artifact.

3.3 Layer 2 — Decision Engine
Contents: Workflow Engine, Governance Engine, conflict resolution, completion gates.
Responsibility: Decide what work happens next, enforce gates, resolve conflicts.

3.4 Layer 3 — Domain Agents
Contents: GAS-001..027 and the learning/publishing agents.
Responsibility: Perform discovery, reasoning, validation, and governance work on the PKG.

3.5 Layer 4 — Validation Engine
Contents: Validators (GAS-017..023), Reviewers (GAS-009), validation rule registry.
Responsibility: Continuously evaluate PKG contents against constitutional and ontology constraints.

3.6 Layer 5 — Materialization Engine
Contents: Materialization Service, generators (Markdown, JSON Schema, YAML, RDF, GraphQL, TypeScript, Python).
Responsibility: Produce derived projections of the PKG on demand.

3.7 Layer 6 — Pre-Production Gate
Contents: Governance Engine approval, PKP assembly, signature, handoff.
Responsibility: Certify production readiness and emit the PKP to the Studio Engine.

4. Layer Dependencies

- Layer 0 depends on nothing inside Genesis.
- Layer 1 depends on Layer 0.
- Layer 2 depends on Layers 0 and 1.
- Layer 3 depends on Layers 0, 1, and 2.
- Layer 4 depends on Layers 0, 1, and 2.
- Layer 5 depends on Layers 0 and 1.
- Layer 6 depends on Layers 1, 2, 4, and 5.

No layer may skip a level. No layer may write downward to a layer it does not own.

5. Subsystem Map

| Subsystem | Layer | Specification |
|-----------|------|----------------|
| Constitutional Engine | 0 | GFS-000..009 |
| Ontology Registry | 0 | GO-001 |
| PKG Store | 1 | GARCH-002 |
| Provenance Ledger | 1 | GARCH-002 |
| Confidence Registry | 1 | GARCH-002 |
| Validation Engine | 1 | GARCH-002 |
| Workflow Engine | 2 | GWS-001 |
| Governance Engine | 2 | GFS-007 |
| Agent Runtime | 3 | GARCH-002, GARCH-005 |
| Materialization Service | 5 | GARCH-003 |
| CLI | 6 | GARCH-002 |
| REST/GraphQL API | 6 | GARCH-002 |
| LLM Integration Layer | 6 | GARCH-002 |
| Message Bus | 6 | GARCH-002 |

6. Deployment Models

Genesis supports three deployment models. The architecture is identical across all three; only the execution layer adapts.

6.1 Local Model
Runs entirely on a single workstation. PKG persisted to an embedded graph database. Agents executed in-process. LLM providers accessed via local runtime or external API. Suitable for individual creators and small productions.

6.2 Cloud Model
Runs on managed infrastructure. PKG persisted to a distributed graph database. Agents executed as discrete services. Message bus carries inter-agent communication. Suitable for teams, large productions, and concurrent sessions.

6.3 Hybrid Model
Local execution for discovery and interactive authoring. Cloud execution for heavy reasoning, validation, and governance. PKG synchronized between local and cloud instances. Provenance preserved across synchronization. Suitable for creators who move between studios and remote work.

7. Architectural Invariants

The following are invariants and may not change without constitutional amendment:

- The PKG is the single source of truth.
- The Studio Engine may not write back into the live PKG.
- Every write to the PKG carries provenance.
- Every assertion carries a confidence classification.
- Genesis produces no media.
- The constitutional layer outranks every other layer.
- The PKP is read-only once certified.

8. Cross-Cutting Concerns

- Provenance — every write records its origin.
- Versioning — every mutation creates a new immutable revision.
- Validation — continuous evaluation, findings not silent corrections.
- Governance — approval gates are binding.
- Audit — every action is recorded in an append-only log.

9. Boundary With the Studio Engine

Genesis begins at the intake of creative intent. Genesis ends at the issuance of a certified PKP. The Studio Engine consumes the PKP; it may not reach back into the live PKG. Revisions require the Studio Engine to return the PKP to Genesis for re-certification.

See `architecture/007 — Studio Handoff Specification.md` for the full boundary contract.

10. Approval

This document is the consolidated architecture reference. For any conflict, the relevant GARCH-NNN document prevails.