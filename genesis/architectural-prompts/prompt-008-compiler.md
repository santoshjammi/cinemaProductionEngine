# Prompt 008 — GENESIS Compiler Architecture

**Status:** Architectural Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `008 — GENESIS Compiler Architecture.md`

---

## Role

You are the Chief Enterprise Architect of the ACI Platform. The Constitutional Foundation (000–006) is frozen. Phase II is in progress. 007 (CIR) is complete and reviewed.

## Objective

Generate the architectural specification for the **GENESIS Compiler** — the deterministic compiler that transforms the CIR (`007`) into executable production artifacts (the PKP, `009`). The compiler is the architectural realization of `00` §3.2 (compilation over generation) and `006` L-11/L-12/L-13.

## Required Parts

1. **Compiler Philosophy** — Why the platform compiles rather than generates; why the compiler is deterministic; why it never invents creativity.
2. **Compiler Pipeline** — The canonical pipeline of passes (`001` §4.2, architecturalized).
3. **Pass Architecture** — Each pass's contract: input, output, dependencies, validation, ownership.
4. **Scheduling** — How passes are ordered and parallelized; dependency-driven scheduling.
5. **Dependency Resolution** — How `depends_on` edges in the CIR determine compilation order.
6. **Optimization** — Within-profile optimization for creative metrics (`002` Part 11).
7. **Incremental Compilation** — Only changed CIR nodes and their dependents are recompiled.
8. **Partial Compilation** — Subset compilation for surgical revision.
9. **Caching** — Compilation caches for replay determinism.
10. **Compiler Diagnostics** — Error reporting, warning reporting, drift detection at compile time.
11. **Recovery** — How the compiler recovers from a failed pass.
12. **Compiler Plugins** — Extension points for runtime-specific passes.
13. **Compiler Extension Points** — Governed extension under the Constitution.
14. **Governance** — Compiler evolution under the Constitution.
15. **Migration** — Integration with the existing architecture.

## Constitutional Constraints

- Derive authority from `006` (Constitution). The compiler is governed by L-11 (decision precedes compilation), L-12 (compilation never invents creativity), L-13 (production knowledge is compiled, not generated).
- The compiler reads the CIR (`007`); it does not read the CIS, does not consume faculty enrichments, does not render media.
- The compiler produces the PKP (`009`); every PKP artifact carries `cir_origin`.
- Architecture only — no implementation, code, YAML, JSON, schemas, or APIs.

## Output

> **008 — GENESIS Compiler Architecture**

---

## Design Intent Notes

The compiler is the platform's "compilation over generation" principle made architectural. The critical insight: the compiler is a deterministic transformer of creative decisions (CIR) into executable specifications (PKP). It never invents; it only executes. This is what makes the platform's output reproducible, auditable, and surgically revisable. The compiler's relationship to the CIR is the same as a traditional compiler's relationship to an AST: it traverses the typed graph and emits executable code, without exercising creative judgment.