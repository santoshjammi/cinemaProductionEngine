Genesis Template (GTMP)
GTMP-004 — Architecture Document Template

Document ID: GTMP-004
Title: Architecture Document Template
Version: 1.0.0
Status: Template
Authority: Derived from GFS-000

1. Purpose

Blank template for Genesis architecture documents. Use this for any document
that describes system structure, boundaries, deployment, or component layout.
Place finished documents in `architecture/` with the GARCH-NNN scheme.

2. Template

```
Genesis Architecture (GARCH)
GARCH-NNN — <Title>

Document ID: GARCH-NNN
Title: <Title>
Version: 1.0.0
Status: Draft | Reviewed | Approved
Authority: Derived from GFS-000

1. Purpose
<One paragraph describing the architectural concern addressed.>

2. Scope
<What this architecture covers and explicitly excludes.>

3. Components
For each component:
- Name: <ComponentName>
- Responsibility: <one sentence>
- Inputs: <list>
- Outputs: <list>
- Dependencies: <other components or external systems>
- Boundary: <what it does NOT do>

4. Boundaries
- Genesis-internal boundaries
- Genesis ↔ Studio Engine boundary
- Genesis ↔ external integrations (Neo4j, LLMs)

5. Data Flow
<Describe how knowledge flows between components. Include a textual diagram.>

6. Storage
- Canonical store: Production Knowledge Graph (PKG)
- Derived stores: file system, caches, indexes
- Persistence guarantees

7. Deployment
- Single-process / multi-process / distributed
- Required runtime services
- Configuration model

8. Non-Functional Requirements
- Performance targets
- Reliability targets
- Security posture
- Observability posture

9. Constraints
- Constitutional constraints (GFS-000)
- Boundary constraints (no media generation inside Genesis)
- Provider independence

10. Open Questions
- <question>
- <question>

11. Dependencies
- <GARCH-NNN, GSPEC-NNN, GO-NNN>
```

3. Usage Notes

- Architecture documents describe structure, not behavior. Behavior goes in workflows.
- Every component must declare its boundary (what it does NOT do).
- All data flow must terminate in or originate from the PKG.