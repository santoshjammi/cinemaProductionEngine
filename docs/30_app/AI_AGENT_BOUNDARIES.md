# AI Agent Boundaries

**Version:** 1.0

## Purpose

Multiple AI systems are allowed.

Multiple creative authorities are not.

Each agent receives only the context necessary for its job.

---

## Hermes

Role:
- orchestrator;
- planning;
- task decomposition;
- content coverage reasoning;
- policy-aware coordination.

Hermes may:
- propose Episode Contracts;
- identify ontology gaps;
- assemble work for GENESIS/PROMETHEUS/ORACLE;
- report blockers.

Hermes may not:
- silently amend constitutions;
- treat legacy docs as current authority;
- call a render “approved” without ORACLE;
- invent canon because information is missing.

---

## GENESIS agents/models

May:
- reason creatively;
- write/revise screenplay before freeze;
- produce exact dialogue;
- create scene/shot/performance intent;
- compile PKP.

Must receive:
- Effective Policy Snapshot;
- Episode Contract;
- relevant canon/continuity;
- selected ontology nodes;
- applicable standards.

Do not give GENESIS the entire `unimportant_docs`.

---

## PROMETHEUS agents/models

May:
- execute media tasks;
- choose technical fallback only within PKP-authorized ranges;
- retry generation;
- report infeasibility.

May not:
- rewrite dialogue;
- reinterpret the ending;
- choose a different character;
- change psychological meaning;
- invent narration to avoid lip sync.

If execution is impossible, return a structured blocker.

---

## ORACLE agents/models

May:
- validate;
- compare;
- score;
- identify timestamped defects;
- request rework.

May not:
- silently repair the creative work;
- approve based only on technical validity;
- change thresholds per run without versioned standard changes.

---

## Coding agents

May implement the application and production runtime.

They must not redesign product law while coding.

If implementation reveals a missing decision:

```yaml
status: DESIGN_DECISION_REQUIRED
do_not_invent: true
```

---

## Context minimization

Each agent should receive references by ID/version rather than all documents.

This is required to reduce:

- prompt conflict;
- model drift;
- token waste;
- accidental legacy revival.
