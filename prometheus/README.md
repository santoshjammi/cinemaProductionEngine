# PROMETHEUS — Universal Execution Engine

> **The deterministic runtime that compiles declared intent into executable work.** PROMETHEUS reads a Production Knowledge Package (PKP), compiles it into a language-neutral Execution Intermediate Representation (EIR), orchestrates runtime adapters, and produces fully-provenanced outputs that ORACLE can validate and ATLAS can preserve.

---

## What PROMETHEUS Is

PROMETHEUS is the **execution engine** of the GENESIS platform. In the platform's compiler metaphor:

| Compiler stage | GENESIS analog |
|----------------|----------------|
| Source program | CIS (`003`) — intent |
| AST / IR | CIR (`007`) — decisions |
| Compiled binary | PKP (`009`) — executable specification |
| **Runtime execution** | **PROMETHEUS (this product)** |
| Program output | Media / Outputs |

PROMETHEUS is to the PKP what a program loader is to a compiled binary: it loads the specification and executes it, without exercising judgment about what the program should do. It **never invents** (`006` L-15) and **never alters intent** (`006` L-14).

PROMETHEUS is **not** a movie generator, not an AI agent, and not an orchestration script. It is a production-grade execution operating system whose contracts (EIR, events, adapter interfaces, provenance) are language-neutral and domain-independent.

---

## Where PROMETHEUS Fits

```
GENESIS  ─────────────►  Constitutional Architecture (000–018, frozen)
    │
    │  defines intent (what should exist)
    ▼
PKP (009)  ────────────►  Frozen executable specification
    │
    │  compiles intent into executable work
    ▼
PROMETHEUS (this product)
    │
    │  executes via adapters, emits events, produces provenance
    ▼
Outputs + Execution Report  ──►  ATLAS (preservation)
                              ──►  ORACLE (validation)
```

The four pillars have a single, unambiguous responsibility each:

| Pillar | Responsibility |
|---|---|
| **GENESIS** | Defines intent — *what should exist* |
| **PROMETHEUS** | Compiles intent into executable work — *how it should execute* |
| **ORACLE** | Verifies execution matched intent — *was it executed correctly?* |
| **ATLAS** | Preserves execution knowledge and provenance — *what happened and how can it be reused?* |

This separation follows the same concerns that made compiler architectures and operating systems successful, and keeps PROMETHEUS applicable beyond filmmaking: any domain that can express intent as a PKP can use the same execution engine.

---

## What This Package Contains

This directory is the **engineering product** that operationalizes the frozen constitutional architecture in `010 — PROMETHEUS Runtime Architecture.md`. It does **not** duplicate or replace `010`; it derives from it.

```
prometheus/
├── README.md            — this file (product overview)
├── VISION.md            — engineering vision: why PROMETHEUS exists as an execution engine
├── ARCHITECTURE.md      — system map; orients the reader; indexes DESIGN docs
├── ROADMAP.md           — milestones M0–M5 with done conditions
├── DESIGN/              — engineering-grade design docs (one per subsystem family)
├── DECISIONS/           — ADR candidates and ratified ADRs
├── PROMPTS/             — engineering prompts that drive implementation per DESIGN doc
├── REVIEWS/             — adversarial review checklists per DESIGN doc
└── IMPLEMENTATION/      — per-milestone tracking artifacts (filled during build)
```

The design package mirrors the structure used by `gkc/` (the GENESIS Knowledge Compiler product). The same conventions apply:

- **GENESIS (`000`–`018`) is frozen.** If a DESIGN doc conflicts with `010`, `010` wins; the DESIGN doc must either change or surface an ADR requesting a constitutional amendment.
- **This package evolves.** Engineering decisions live here; architectural decisions live in GENESIS.
- **Nothing here amends GENESIS.** Where a gap is found in `010`, it is closed by constitutional revision or ADR — never by silently overriding the architecture.

---

## Design Principles (Inherited from `010`)

PROMETHEUS executes; it does not create. Execution must always be:

- **Deterministic** — same PKP + same adapter versions ⇒ same outputs.
- **Reproducible** — every execution can be replayed byte-identically (modulo irreducibly non-deterministic providers, handled by the recorded-output fallback in `010` §9.3).
- **Observable** — no silent execution; every step emits structured events.
- **Auditable** — every decision is explainable; every artifact is traceable.
- **Resumable** — every execution can checkpoint and resume.
- **Versioned** — inputs, IR, adapters, and outputs all carry versions.
- **Traceable** — full provenance from PKP artifact → EIR node → adapter call → output → ATLAS entry.
- **Platform independent** — local-first, cloud-capable; no OS/hardware dependency in the core.
- **Plugin-oriented** — adapters, validators, schedulers, storage, and caches are replaceable.

---

## Non-Goals

PROMETHEUS does **not**:

- Write stories, invent scenes, generate prompts, or create dialogue.
- Perform creative reasoning or replace the Creative Mind (`005`).
- Replace GENESIS, ORACLE, or ATLAS.
- Make creative decisions when the PKP is silent — it reports a **rendering gap** (`010` §8.3).
- Depend on a specific implementation language, OS, cloud, or hardware.
- Become a prototype that turns into production by accident; the reference implementation proves the architecture, not the technology choice.

---

## Success Criteria

PROMETHEUS is successful when:

1. A valid PKP can be transformed into a complete, deterministic **Execution Intermediate Representation (EIR)**.
2. The EIR can be executed by **any compliant runtime adapter**.
3. Every execution is **reproducible** given the same PKP and adapter versions.
4. Every decision is **explainable** from the execution report and event stream.
5. Every artifact is **traceable** through the provenance chain.
6. Every execution is **resumable** from any checkpoint.
7. Every execution is **auditable** by ORACLE.
8. PROMETHEUS generalizes beyond cinema: any domain that can express intent as a PKP can use the same execution engine.

---

## See Also

- `010 — PROMETHEUS Runtime Architecture.md` (repo root) — canonical constitutional architecture.
- `009 — Production Knowledge Package (PKP) Architecture.md` — PROMETHEUS's input contract.
- `011 — ORACLE Validation Architecture.md` — validates PROMETHEUS's output.
- `012 — ATLAS Knowledge Architecture.md` — preserves PROMETHEUS's output and provenance.
- `gkc/README.md` — sibling engineering product; the pattern this package follows.