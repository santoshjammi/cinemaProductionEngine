# Prompt 009 — Production Knowledge Package (PKP) Architecture

**Status:** Architectural Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `009 — Production Knowledge Package (PKP) Architecture.md`

---

## Role

You are the Chief Enterprise Architect of the ACI Platform. The Constitutional Foundation (000–006) is frozen. Phase II is in progress. 007 (CIR) and 008 (Compiler) are complete and reviewed.

## Objective

Generate the architectural specification for the **Production Knowledge Package (PKP)** — the compiled production artifact generated from the CIR by the compiler. The PKP is the executable specification PROMETHEUS renders; it is the "compiled binary" of the platform's compiler metaphor.

## Required Parts

1. **Architecture** — The PKP's structural architecture: artifacts, dependencies, root, partitions.
2. **Artifact Model** — Each PKP artifact's type, identity, ownership, `cir_origin`, lifecycle.
3. **Dependency Graph** — How PKP artifacts depend on each other; how dependencies mirror the CIR's `depends_on` graph.
4. **Identifiers** — The PKP's identity scheme, extending the COM's.
5. **Ownership** — Which compiler pass produces each artifact; which runtime consumes it.
6. **Regeneration** — How a PKP is regenerated from a CIR (full and incremental).
7. **Incremental Updates** — How a PKP is updated when a subset of the CIR changes.
8. **Packaging** — How the PKP is assembled, frozen, hashed, and distributed.
9. **Distribution** — How the PKP is handed to PROMETHEUS and to ORACLE.
10. **Validation** — Pre-freeze PKP validation; ORACLE's post-render validation against the PKP.
11. **Compilation Outputs** — The 19 PKP specification outputs (PKP-00..18).
12. **Runtime Contracts** — The PKP-PROMETHEUS contract; the PKP-ORACLE contract.
13. **Governance** — PKP evolution under the Constitution.
14. **Lifecycle** — The PKP's lifecycle from compilation to archival.

## Constitutional Constraints

- Derive authority from `006` (Constitution). The PKP is governed by L-13 (compiled, not generated), L-14 (execution never changes intent), L-18 (knowledge outlives media), L-19 (history is immutable).
- The PKP is produced by the compiler (`008`) from the CIR (`007`); every artifact carries `cir_origin`.
- The PKP is consumed by PROMETHEUS (`010`) and validated by ORACLE (`011`).
- Architecture only — no implementation, code, YAML, JSON, schemas, or APIs.

## Output

> **009 — Production Knowledge Package (PKP) Architecture**

---

## Design Intent Notes

The PKP is the "compiled binary" of the ACI Platform: the deterministic, executable specification that PROMETHEUS renders. The critical insight: the PKP carries *what to render*, not *why*. The "why" lives in the CIR (`007`); the PKP carries the compiled "what." This separation is what makes PROMETHEUS a pure executor — it reads the PKP and renders, without exercising creative judgment. The PKP's `cir_origin` on every artifact is the traceability link that enables ORACLE to verify that the rendered media matches the creative decisions, and to surgically re-enter the CIR when it doesn't.