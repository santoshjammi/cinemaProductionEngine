# ADR-0001 — GKC Name and Scope

**Status:** Ratified
**Date:** 2026-07-21
**Supersedes:** RIC (Repository Intelligence Compiler) — working name during initial drafting

---

## Context

The product was originally drafted as **RIC — Repository Intelligence Compiler**. As the design progressed, it became clear that the scope already exceeds "repository intelligence":

- It compiles *architectural knowledge*, of which repository intelligence is the first domain.
- It will (per `VISION.md` § Future Evolution) also compile ontologies, schemas, contracts, policies, prompts, and runtime traces.
- The substrate it produces is consumed by AI agents, IDEs, validators, and future runtimes — not just repository tools.

A name that constrains the product to "repository intelligence" would force a rename when the scope grows.

## Decision

The product is named **GKC — GENESIS Knowledge Compiler**.

- **G**ENESIS: the parent architecture; GKC is the first executable component of GENESIS.
- **K**nowledge: what GKC compiles. "Knowledge" subsumes repository intelligence, ontologies, contracts, schemas, prompts, and runtime traces.
- **C**ompiler: the operational model (per `DESIGN/001` § 2). GKC is a compiler in the strict sense: deterministic, staged, cacheable, incremental, language-agnostic.

The CLI is `gkc` (e.g., `gkc scan`, `gkc context`, `gkc explain`).

The file headers, domain language, and brand use GKC consistently.

## Alternatives Considered

- **RIC — Repository Intelligence Compiler.** Accurate to today's scope but constrains future expansion. Rejected.
- **GIE — GENESIS Intelligence Engine.** "Engine" is vaguer than "compiler" and loses the LLVM-style framing that distinguishes GKC from a runtime or agent. Rejected.
- **GC — GENESIS Compiler.** Too generic; collides with "garbage collector" in compiler contexts. Rejected.
- **KC — Knowledge Compiler.** Loses the GENESIS parent brand. Rejected.

## Consequences

- All design documents use GKC as the product name.
- The CLI is `gkc`.
- The directory structure uses `gkc/` at the repository root.
- Future horizons (ontologies, contracts, prompts, traces) extend GKC without requiring a rename.
- The compiler framing (per `DESIGN/001`) is the commitment; the name reinforces it.