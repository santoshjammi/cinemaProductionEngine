Genesis Registry (GREG)
GREG-003 — Capability Registry

Document ID: GREG-003
Title: Capability Registry
Version: 1.0.0
Status: Registry
Authority: Derived from GFS-000, GFS-005, GFS-009

1. Purpose

The Capability Registry is the authoritative catalog of every capability Genesis exposes — to agents, to workflows, to downstream engines, and to human creators. A capability that is not registered here does not exist constitutionally. Agents may not invoke unregistered capabilities; workflows may not depend on them; downstream engines may not consume them.

The registry complements the Ontology Registry (GREG-001) and the Agent Registry (GREG-002): ontologies define vocabulary, agents execute reasoning, and capabilities define the callable surface Genesis offers. Together they form the operational contract of the engine.

2. Registry Schema

Each entry contains:

- Capability ID — GCAP-NNN, permanent.
- Title — human-readable name.
- Category — Knowledge / Reasoning / Validation / Workflow / Governance / Format / Integration.
- Surface — API endpoint, event type, PKG query, or prompt invocation that exposes the capability.
- Owner — the agent role accountable for the capability.
- Input Contract — typed inputs the capability requires.
- Output Contract — typed outputs the capability produces.
- Dependencies — ontologies, agents, and other capabilities this capability depends on.
- Status — Proposed / Reviewed / Validated / Approved / Published / Deprecated / Archived.
- SLA — the maximum time the capability has to return a result before escalation (see GP-GOV-002).

3. Knowledge Capabilities

| ID | Title | Owner | Status |
|----|-------|------|--------|
| GCAP-001 | PKG Read | Reasoning Engine | Published |
| GCAP-002 | PKG Write (Staging) | Production Orchestrator | Published |
| GCAP-003 | PKG Merge (Atomic) | Production Orchestrator | Published |
| GCAP-004 | PKG Snapshot | Production Orchestrator | Published |
| GCAP-005 | PKG Query (SHACL) | Reasoning Engine | Published |
| GCAP-006 | Decision Record Commit | Reasoning Engine | Published |
| GCAP-007 | Gap Detected Emit | Discovery Agent | Published |
| GCAP-008 | Knowledge Object Classify | Reasoning Engine | Published |

4. Reasoning Capabilities

| ID | Title | Owner | Status |
|----|-------|------|--------|
| GCAP-010 | Deductive Inference | Reasoning Engine | Published |
| GCAP-011 | Inductive Rule Propose | Reasoning Engine | Published |
| GCAP-012 | Inductive Rule Promote | Governance Agent | Published |
| GCAP-013 | Abductive Hypothesis Score | Reasoning Engine | Published |
| GCAP-014 | Reasoning Catalog Query | Reasoning Engine | Published |
| GCAP-015 | Confidence Compute | Reasoning Engine | Published |

5. Validation Capabilities

| ID | Title | Owner | Status |
|----|-------|------|--------|
| GCAP-020 | Structural Validation (SHACL) | Structural Validator | Published |
| GCAP-021 | Semantic Validation (Rules) | Semantic Validator | Published |
| GCAP-022 | Completeness Validation | Completeness Validator | Published |
| GCAP-023 | Psychology Review | Psychology Reviewer | Published |
| GCAP-024 | Narrative Coherence Check | Story Coherence Validator | Published |
| GCAP-025 | World Rule Check | World Rule Validator | Published |

6. Workflow Capabilities

| ID | Title | Owner | Status |
|----|-------|------|--------|
| GCAP-030 | Stage Dispatch | Production Orchestrator | Published |
| GCAP-031 | Parallel Fan-Out | Production Orchestrator | Published |
| GCAP-032 | Conditional Route | Routing Agent | Published |
| GCAP-033 | Barrier Sync | Production Orchestrator | Published |
| GCAP-034 | Merge with Conflict Detection | Production Orchestrator | Published |
| GCAP-035 | Revision Dispatch | Revision Agent | Published |
| GCAP-036 | Checkpoint Commit | Production Orchestrator | Published |

7. Governance Capabilities

| ID | Title | Owner | Status |
|----|-------|------|--------|
| GCAP-040 | Approval Chain Submit | Governance Agent | Published |
| GCAP-041 | Approval Verdict Record | Governance Agent | Published |
| GCAP-042 | Escalation Emit | Any Agent | Published |
| GCAP-043 | Escalation Route | Production Orchestrator | Published |
| GCAP-044 | Production Readiness Certify | Governance Agent | Published |
| GCAP-045 | Waiver Grant | Governance Agent | Published |

8. Format and Integration Capabilities

| ID | Title | Owner | Status |
|----|-------|------|--------|
| GCAP-050 | Prompt Materialize | Prompt Builder | Published |
| GCAP-051 | Screenplay Document Materialize | Screenplay Writer | Published |
| GCAP-052 | Production Plan Materialize | Production Planner | Published |
| GCAP-053 | Production Knowledge Package Assemble | Publisher | Published |
| GCAP-054 | PKG Export (to Studio Engine) | Publisher | Published |
| GCAP-055 | Learning Corpus Ingest | Learning Agent | Published |

9. Event Bus Capabilities

| ID | Title | Owner | Status |
|----|-------|------|--------|
| GCAP-060 | Event Publish | Event Bus | Published |
| GCAP-061 | Event Subscribe | Event Bus | Published |
| GCAP-062 | Event Trace Propagate | Event Bus | Published |
| GCAP-063 | Event Audit Query | Governance Agent | Published |

10. Registry Update Rules

- A capability may be added only through a Capability Registration approval chain (Brief Parser → Core Reviewer → Governance Agent).
- A capability's Surface may change only through a capability version bump.
- A capability's Input and Output Contracts may extend additively (backward compatible) without a new ID; breaking contract changes require a new ID and deprecation of the old.
- A capability ID is permanent. Reuse of an archived ID is forbidden.
- A capability in Deprecated status may not be invoked by new agents or workflows; existing consumers must migrate.
- Every Published capability must have an SLA declared.

11. Anti-Patterns

- Invoking a capability ID not in this registry.
- Calling a capability's internal function instead of its declared Surface.
- Reusing an archived capability ID.
- Changing a contract without a version bump.
- Allowing an unregistered capability to subscribe to the Event Bus.
- Exposing a capability without an SLA.

12. Exit Criteria

The registry is complete when:

- Every capability exposed by Genesis has a registry entry.
- Every Published capability has a declared Surface and SLA.
- Every Deprecated capability has a replacement and a migration note.
- The registry is cross-referenced with the Agent Registry (each capability's Owner is a registered agent) and the Ontology Registry (each capability's Input and Output Contracts reference registered ontologies).