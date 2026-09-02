Genesis Registry (GREG)
GREG-002 — Agent Registry

Document ID: GREG-002
Title: Agent Registry
Version: 1.0.0
Status: Registry
Authority: Derived from GFS-000, GFS-005, GFS-009

1. Purpose

The Agent Registry is the authoritative catalog of every registered agent in Genesis. An agent that is not registered here does not exist constitutionally. Workflows may not invoke unregistered agents; the Event Bus may not deliver to unregistered subscribers; the Production Orchestrator may not route to unregistered branches.

The registry is the single source of truth for agent IDs, roles, concerns, prompts, dependencies, and statuses. It is updated only through the Agent Registration approval chain (see GP-GOV-001).

2. Registry Schema

Each entry contains:

- Agent ID — GAS-NNN, permanent.
- Title — human-readable name.
- Role — Orchestrator / Architect / Engineer / Validator / Reviewer / Researcher / Governor / Publisher / Learner.
- Concern — the single concern from the Concern Catalog (see GP-DESIGN-002).
- Layer — L0–L4 (see GP-ARCH-001).
- Prompt Path — path to the canonical system prompt under prompts/.
- Dependencies — ontologies, registries, and other agents this agent consumes.
- Status — Proposed / Reviewed / Validated / Approved / Published / Deprecated / Archived.
- Owner — the role accountable for the agent's spec.
- Registration Date — when the agent was first registered.

3. Orchestrators

| ID | Title | Role | Concern | Status |
|----|-------|------|---------|--------|
| GAS-001 | Production Orchestrator Agent | Orchestrator | Workflow | Published |
| GAS-002 | Revision Agent | Orchestrator | Workflow | Published |
| GAS-003 | Routing Agent | Orchestrator | Workflow | Published |

4. Architects

| ID | Title | Role | Concern | Status |
|----|-------|------|---------|--------|
| GAS-004 | Story Architect Agent | Architect | Knowledge (Narrative) | Published |
| GAS-005 | Character Manager Agent | Architect | Knowledge (Character) | Published |
| GAS-006 | Environment Manager Agent | Architect | Knowledge (World) | Published |
| GAS-007 | Scene Planner Agent | Architect | Knowledge (Staging) | Published |
| GAS-008 | Shot Planner Agent | Architect | Knowledge (Shot) | Published |
| GAS-009 | Music Composer Agent | Architect | Knowledge (Music) | Published |
| GAS-010 | Prompt Builder Agent | Architect | Format (Prompts) | Published |

5. Engineers

| ID | Title | Role | Concern | Status |
|----|-------|------|---------|--------|
| GAS-011 | Screenplay Writer Agent | Engineer | Knowledge (Screenplay) | Published |
| GAS-012 | Dialogue Writer Agent | Engineer | Knowledge (Dialogue) | Published |
| GAS-013 | Asset Spec Agent (Image) | Engineer | Knowledge (Asset Spec) | Published |
| GAS-014 | Asset Spec Agent (Voice) | Engineer | Knowledge (Asset Spec) | Published |
| GAS-015 | Asset Spec Agent (SFX) | Engineer | Knowledge (Asset Spec) | Published |
| GAS-016 | Asset Spec Agent (Animation) | Engineer | Knowledge (Asset Spec) | Published |
| GAS-017 | Production Planner Agent | Engineer | Knowledge (Plan) | Published |

6. Validators

| ID | Title | Role | Concern | Status |
|----|-------|------|---------|--------|
| GAS-018 | Structural Validation Agent | Validator | Validation | Published |
| GAS-019 | Semantic Validation Agent | Validator | Validation | Published |
| GAS-020 | Completeness Validation Agent | Validator | Validation | Published |

7. Reviewers

| ID | Title | Role | Concern | Status |
|----|-------|------|---------|--------|
| GAS-021 | Psychology Reviewer Agent | Reviewer | Validation (Character) | Published |
| GAS-022 | Story Coherence Validator | Reviewer | Validation (Narrative) | Published |
| GAS-023 | World Rule Validator | Reviewer | Validation (World) | Published |

8. Researchers

| ID | Title | Role | Concern | Status |
|----|-------|------|---------|--------|
| GAS-024 | Research Agent | Researcher | Knowledge (Research) | Published |
| GAS-025 | Archival Research Agent | Researcher | Knowledge (Archival) | Published |

9. Governance

| ID | Title | Role | Concern | Status |
|----|-------|------|---------|--------|
| GAS-026 | Governance Agent | Governor | Governance | Published |
| GAS-027 | Devotional Coherence Validator | Governor | Governance (Devotional) | Published |

10. Publishers and Learners

No separate IDs are allocated in this version. The Publisher and Learning Agent functions are owned by GAS-010 (Prompt Builder) derivatives and the Learning Engine (outside Genesis scope) respectively. Future versions may allocate GAS-028+ as required.

11. Registry Update Rules

- An agent may be added only through the Agent Registration approval chain (Brief Parser → Core Reviewer → Governance Agent).
- An agent's Prompt Path may change only through a prompt version bump.
- An agent's Concern may not change — concern changes require a new agent ID.
- An agent ID is permanent. Reuse of an archived ID is forbidden.
- An agent in Deprecated status may not be invoked by new workflows; existing workflows must migrate.
- An agent in Archived status is removed from the active registry and held in the archive.

12. Anti-Patterns

- Invoking an agent ID not in this registry.
- Letting two agents own the same concern with overlapping scope.
- Reusing an archived agent ID.
- Bumping a prompt without updating the Prompt Path.
- Allowing an unregistered agent to subscribe to the Event Bus.

13. Exit Criteria

The registry is complete when:

- Every agent spec under agents/ has a registry entry.
- Every Published agent has a Prompt Path.
- Every Deprecated agent has a replacement and a migration note.
- The registry is auditable end-to-end.