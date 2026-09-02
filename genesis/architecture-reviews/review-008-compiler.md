# Architecture Review — 008 (Compiler)

**Status:** Coherence Report
**Date:** 2026-07-21
**Subject:** `008 — GENESIS Compiler Architecture.md`

---

## Quality Check Results

| Check | Result | Notes |
|-------|--------|-------|
| **No duplicated concepts** | PASS | The 19-pass pipeline is referenced to `001` §4.2 and architecturalized, not redefined. The pass contract (Part 3.1) extends `001`'s pass definitions with the CIR-compiler binding. New concepts (compilation cache, dependency resolver, recovery loop, plugin registry) are architectural, not duplicates. |
| **No overlapping authority** | PASS | The compiler compiles; it does not decide (`002`), does not cognize (`005`), does not render (`010`), does not validate (`011`), does not persist (`012`). MI-2 and MI-4 are explicit. |
| **No conflicting terminology** | PASS | "CIR," "PKP," "COM," "cir_origin," "Directorial Board" used consistently. |
| **No broken invariants** | PASS | References L-2, L-11, L-12, L-13, L-14, L-19, L-25, I-SI-15 by reference. The compiler's "never invent" rule (Part 1.3) enforces L-12. The freeze-before-compile rule (Part 2.2) enforces L-11. |
| **No constitutional violations** | PASS | Part 14.3 verifies compliance with L-11, L-12, L-13, L-19. |
| **No circular dependencies** | PASS | CIR → Compiler → PKP is a one-directional chain. The recovery loop (Part 11.4) re-enters the Board (not the compiler) on failure; the compiler does not call the Board. |
| **No runtime leakage into cognition** | PASS | The compiler reads the CIR (decisions), not the Mind's enrichments (cognition). Part 12.3 of `007` and MI-2 of `008` are explicit. |
| **No cognition leakage into execution** | PASS | The compiler produces the PKP; PROMETHEUS renders it. The compiler does not render. |

---

## Gap Analysis

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| The compiler's relationship to non-deterministic providers is acknowledged (Risk: Provider non-determinism) but the "replay from recorded output" mechanism is not fully specified. | Medium | This is a runtime concern that belongs in the PKP (`009`) specification's provenance model and in PROMETHEUS (`010`)'s replay contract. 008 correctly identifies the risk; 009/010 should address the mechanism. Track for 009/010. |
| The canonical pipeline is cinema-specific (19 passes map to cinema's 18 directors). The compiler's runtime-independence is stated (Part 14.2) but the cinema-specificity of the pipeline is not deeply reconciled. | Low | The reconciliation is correct: the compiler's *architecture* (pass contract, scheduling, caching, recovery) is runtime-independent; the *canonical pipeline* is cinema-specific. Future runtimes define their own pipelines using the architecture. This is sufficient at the architectural level. No action. |

---

## Constitutional Compliance Verification

| Law | How 008 complies |
|-----|------------------|
| L-2 (Intent Is Human-Authored) | The compiler does not read the CIS (MI-2); it reads the CIR, which is the Board's decisions from the CIS. |
| L-11 (Decision Precedes Compilation) | Part 2.2: the CIR Loader verifies the CIR is frozen. |
| L-12 (Compilation Never Invents Creativity) | Part 1.3, Part 2.3, Part 6.2, Part 10.1 (drift detection). |
| L-13 (Production Knowledge Is Compiled) | Part 1.2 (determinism). |
| L-14 (Execution Never Changes Intent) | The compiler produces the PKP; it does not execute it. |
| L-19 (History Is Immutable) | Part 14.3: frozen PKPs are immutable. |
| L-25 (Human Supremacy) | Part 11.4: the human intervenes on repeated recovery-loop failure. |

---

## ADR Candidates

**ADR-002: The Compiler Is a Pass-Based Pipeline with Isolated Passes.**
- **Decision:** The compiler is a pipeline of isolated passes, each with a defined contract, communicating only through the PKP-in-progress.
- **Rationale:** Pass isolation enables incremental compilation, parallelism, and determinism. Without isolation, hidden cross-pass state would break all three.
- **Irreversibility:** Moving away from isolated passes (e.g., to a monolithic compiler) would require abandoning incremental compilation and surgical revision — the platform's core revision mechanism.
- **Status:** Recommended for ratification.

---

## Conclusion

008 is constitutionally compliant, non-duplicative, and non-overlapping. It architecturalizes the 19-pass pipeline from `001` §4.2, binds it to the CIR (`007`), and defines the compiler's architecture (scheduling, caching, incremental/partial compilation, diagnostics, recovery, plugins) within constitutional bounds. One gap (provider non-determinism replay mechanism) is tracked for 009/010.

**Recommendation:** Proceed to 009 — Production Knowledge Package (PKP) Architecture.