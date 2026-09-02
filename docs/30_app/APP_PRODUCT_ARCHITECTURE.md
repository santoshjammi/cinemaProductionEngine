# videoGen Application Product Architecture

**Version:** 1.0  
**Purpose:** Define what the app should manage, independent of specific AI providers.

## 1. Product idea

The application is not primarily a prompt launcher.

It is a **cinematic production operating system** that:

- manages constitutions and canon;
- plans content from an ontology;
- maintains continuity;
- creates Episode Contracts;
- resolves effective policy;
- drives GENESIS;
- freezes PKPs;
- orchestrates PROMETHEUS;
- validates with ORACLE;
- persists in ATLAS;
- creates distribution derivatives;
- learns from coverage/performance.

---

## 2. Core product objects

1. Niche
2. Domain
3. Problem Family
4. Sub-Series
5. Mechanism Variant
6. Story Universe
7. Character
8. Continuity State
9. Episode / Multi-Part Arc
10. Episode Contract
11. Policy Snapshot
12. GENESIS Project
13. PKP
14. Production Run
15. Asset
16. ORACLE Validation
17. Master Release
18. Distribution Package
19. Coverage Entry
20. Learning Record

---

## 3. Primary Psychology workflow

```text
Choose Psychology
    ↓
Choose Relationship & Emotional Psychology
    ↓
Choose Problem Family
    ↓
Choose Sub-Series
    ↓
Define Mechanism Variant
    ↓
Choose Mark & Sarah
    ↓
Load Continuity
    ↓
Create Episode Contract
    ↓
Resolve Effective Policy
    ↓
GENESIS
    ↓
Creative Review / ORACLE Preflight
    ↓
Freeze PKP
    ↓
PROMETHEUS
    ↓
ORACLE Media Review
    ↓
Approve Master
    ↓
Create Platform Derivatives
    ↓
Publish
    ↓
Record Coverage + Learning
```

---

## 4. UX principle

The UI should expose **decisions and state**, not raw architecture jargon unless the user asks for it.

Example episode dashboard:

- What are we making?
- Why this topic?
- Which psychological mechanism?
- What happened previously in Mark & Sarah?
- Is story approved?
- Are character/voice references locked?
- Is PKP frozen?
- What is rendering?
- What failed?
- Is the master approved?
- What derivatives are ready?

---

## 5. No prompt soup

The app should never concatenate every file in `docs/` into one enormous LLM prompt.

Instead it should use policy resolution to create a compact, versioned Effective Policy Snapshot.

---

## 6. Replaceable AI providers

Provider configuration belongs below creative authority.

The app should allow:

- local models;
- cloud models when explicitly chosen;
- alternate image generators;
- alternate lip-sync models;
- alternate TTS;

without changing story/canon schemas.

---

## 7. Human approval points

Initial recommended human approvals:

- Episode Contract;
- screenplay/dialogue;
- character/voice reference binding;
- PKP freeze;
- final master.

Automation can increase later after ORACLE proves reliable.

---

## 8. MVP discipline

The first app milestone is not “support all video niches.”

It is:

> **Produce one consistent Mark & Sarah Psychology vertical slice through the full authority → GENESIS → PKP → PROMETHEUS → ORACLE chain.**

Then generalize.

---

## 9. Future niche expansion

When Kids Stories is added:

- create Kids Sub-Constitution;
- create its ontology;
- create its series/universe canon;
- reuse the same app entities and lifecycle.

The app should not need a second production engine.
