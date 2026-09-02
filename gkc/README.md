# GKC — GENESIS Knowledge Compiler

> **Compiler for architectural knowledge. Context engine for AI agents. Semantic index for the repository.**
> The first executable component of the GENESIS platform.

---

## What GKC Is

GKC is a **knowledge compiler**. It takes a repository (or any structured body of architectural knowledge) and compiles it into a form that machines can reason over:

- a **registry** of artifacts and their metadata,
- an **authority graph** of constitutional relationships,
- a **dependency graph** of structural relationships,
- an **ontology** of domain concepts,
- and a **queryable context store** from which optimal prompts can be sliced for any AI agent, IDE, or runtime.

It is the engineering product that operationalizes the frozen GENESIS constitutional architecture (documents `000`–`018`). Where GENESIS specifies *what the architecture is*, GKC compiles *what the architecture means in a specific repository* and makes that meaning executable.

---

## Where GKC Fits

```
GENESIS (frozen architecture, 000–018)
    │
    │  operationalized by
    ▼
GKC  ───────────────────►  Reference Implementation
    │                            │
    │  compiles knowledge        │  becomes runtime substrate
    ▼                            ▼
Registry · Graphs · Ontology · Context  ──►  AIOS (AI Operating System)
                                            │
                                            │  schedules, plans, governs
                                            ▼
                                         Agents · Runtimes · IDEs
```

GKC is **not** a runtime, **not** an agent, **not** an LLM. It is the compiler that produces the knowledge substrate those systems consume.

---

## Design Package Map

This directory contains the **Product Design Package (PDP)** for GKC. It is the engineering analogue of LLVM's design docs — sufficient for an engineering team or AI coding agent to build the compiler without architectural ambiguity.

```
gkc/
├── README.md                  ← you are here
├── VISION.md                  ← product vision, non-goals, evolution
├── ROADMAP.md                 ← milestones M0–M5
├── ARCHITECTURE.md            ← system-level architecture (links DESIGN docs)
├── DESIGN/                    ← the 12 design documents (evolving)
│   ├── 001-vision.md
│   ├── 002-domain-model.md
│   ├── 003-component-architecture.md
│   ├── 004-data-model.md
│   ├── 005-pipeline.md
│   ├── 006-query-engine.md
│   ├── 007-context-compiler.md   ← flagship
│   ├── 008-plugin-framework.md
│   ├── 009-cli.md
│   ├── 010-storage.md
│   ├── 011-testing.md
│   └── 012-reference-implementation.md
├── DECISIONS/                 ← ADRs ratified during design
├── REVIEWS/                   ← engineering reviews of each DESIGN doc
├── PROMPTS/                   ← engineering prompts to drive implementation
└── IMPLEMENTATION/            ← reference-implementation tracking (filled during build)
```

### Document triplets

Every DESIGN doc is accompanied by a **Prompt**, a **Review**, and a set of **ADR Candidates**:

| Companion | Path | Purpose |
|---|---|---|
| Engineering Prompt | `PROMPTS/00N-*.md` | Drives an engineering agent to implement the document. |
| Engineering Review | `REVIEWS/00N-*.md` | Adversarial review checklist the doc must pass before implementation. |
| ADR Candidates | `DECISIONS/00N-*.md` | Architectural decisions surfaced by the doc, awaiting ratification. |

---

## How to Read This Package

| You are… | Read in this order |
|---|---|
| New to the project | `VISION.md` → `ARCHITECTURE.md` → `DESIGN/001` → `DESIGN/003` → `DESIGN/007` |
| Implementing a subsystem | The relevant `DESIGN/00N` → its `PROMPTS/00N` → its `REVIEWS/00N` |
| Reviewing a design | The `DESIGN/00N` → its `REVIEWS/00N` → its `DECISIONS/00N` |
| Planning a milestone | `ROADMAP.md` → `DESIGN/012` |
| Extending the compiler | `DESIGN/008` → `DESIGN/003` → `DESIGN/006` |

---

## Status

| Layer | State |
|---|---|
| GENESIS architecture (`000`–`018`) | **Frozen.** Do not redesign here. |
| GKC Product Design Package | **Drafting.** Documents evolve with engineering. |
| GKC Reference Implementation | **Not started.** See `ROADMAP.md` and `DESIGN/012`. |

---

## Constraints Carried Into Every Document

1. **No implementation code.** This package is software engineering design, not source.
2. **No language-specific design.** GKC must be implementable in any host language; the design favors interfaces, invariants, and data flow over idioms.
3. **No public API surface in the design docs.** API design happens at implementation time, against the contracts in `DESIGN/003` and `DESIGN/008`.
4. **The architecture is upstream.** Anywhere GKC behavior conflicts with GENESIS `000`–`018`, the GENESIS document wins and GKC files an ADR.
5. **Evolving, not constitutional.** Unlike GENESIS, these documents are expected to change as engineering proceeds. Change is recorded in `DECISIONS/`.

---

## CLI Preview

GKC ships as a single CLI, `gkc`, with stable subcommand surface:

```
gkc scan        gkc registry    gkc graph       gkc validate
gkc explain     gkc context     gkc search      gkc stats
gkc doctor      gkc cache
```

See `DESIGN/009` for the CLI architecture, UX philosophy, and automation contract.