# Architecture Review — 009 (PKP)

**Status:** Coherence Report
**Date:** 2026-07-21
**Subject:** `009 — Production Knowledge Package (PKP) Architecture.md`

---

## Quality Check Results

| Check | Result | Notes |
|-------|--------|-------|
| **No duplicated concepts** | PASS | The PKP is referenced to `001` §5 and architecturalized, not redefined. The 19 PKP specifications (PKP-00..18) are referenced as existing artifacts, not redefined. New concepts (PKP Root, PKP hash, artifact state machine, incremental update provenance) are architectural. |
| **No overlapping authority** | PASS | The PKP is produced by the compiler (`008`), rendered by PROMETHEUS (`010`), validated by ORACLE (`011`), persisted by ATLAS (`012`). The PKP itself has no authority; it is an artifact. Part 12 contracts are explicit boundaries. |
| **No conflicting terminology** | PASS | "CIR," "cir_origin," "PKP artifact," "frozen," "hash" used consistently. |
| **No broken invariants** | PASS | References I-SI-15 (acyclic), I-SI-21 (cir_origin), I-SI-22 (voice), I-SI-23 (duration), I-SI-40 (runtime sum) by reference. Pre-freeze validation (Part 10.1) enforces them. |
| **No constitutional violations** | PASS | Part 13.3 verifies L-13, L-14, L-18, L-19. The PKP is read-only for PROMETHEUS (L-14) and ORACLE (L-16). |
| **No circular dependencies** | PASS | CIR → Compiler → PKP → PROMETHEUS → Media → ORACLE → (drift report) → CIR revision. The revision loop re-enters the CIR, not the PKP directly. |
| **No runtime leakage into cognition** | PASS | The PKP is the compiled output; it carries no cognition (no enrichments, no alternatives, no rationale — those are in the CIR). Part 12.1: PROMETHEUS reads the PKP, not the CIR. |
| **No cognition leakage into execution** | PASS | The PKP carries "what to render," not "why." Part 1.1 is explicit. |

---

## Gap Analysis

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| The provider non-determinism replay mechanism (flagged in review-008) is partially addressed (Part 6.3: cross-provider regeneration) but the "replay from recorded output" fallback is not fully specified. | Medium | This belongs in PROMETHEUS (`010`)'s replay contract. 009 correctly identifies that the PKP records provider versions for replay; 010 should specify what happens when a provider is irreducibly non-deterministic. Track for 010. |
| The PKP's relationship to the PKG (GFS-003) is stated (the PKP is a PKG subgraph) but the partitioning between the CIR subgraph and the PKP subgraph within the PKG is not deeply specified. | Low | Both the CIR (`007` Part 2.1) and the PKP (Part 1.2) are typed subgraphs of the PKG, distinguished by node state (reasoning vs. executable). This is sufficient at the architectural level; the storage-level partitioning is an ATLAS (`012`) concern. Track for 012. |

---

## Constitutional Compliance Verification

| Law | How 009 complies |
|-----|------------------|
| L-5 (Objects Have Identity, Provenance, Lifecycle) | Part 2 (artifact contract), Part 4 (identifiers). |
| L-11 (Decision Precedes Compilation) | Part 10.1: every artifact's `cir_origin` references a frozen CIR node. |
| L-12 (Compilation Never Invents Creativity) | Part 10.1: pre-freeze validation checks `cir_origin` completeness. |
| L-13 (Production Knowledge Is Compiled) | Part 1.1, Part 6. |
| L-14 (Execution Never Changes Intent) | Part 12.1: PKP is read-only for PROMETHEUS. |
| L-15 (Execution Never Invents Creativity) | Part 12.1: PROMETHEUS makes zero creative decisions. |
| L-16 (Validation Never Mutates Artifacts) | Part 12.2: PKP is read-only for ORACLE. |
| L-17 (Validation Is Against Intent and Decisions) | Part 10.2: ORACLE validates against PKP (which traces to CIR and CIS). |
| L-18 (Knowledge Outlives Media) | Part 6.3: PKP regeneration from archived CIR. |
| L-19 (History Is Immutable) | Part 8.4: frozen PKPs are immutable. |

---

## ADR Candidates

**ADR-003: The PKP Is Read-Only for All Downstream Consumers.**
- **Decision:** The PKP is read-only for PROMETHEUS, ORACLE, and the human. Amendments go through the CIR (re-compilation), never through the PKP directly.
- **Rationale:** If any downstream consumer could amend the PKP, the PKP would no longer be the deterministic compiled output of the CIR, breaking L-13 (compiled, not generated) and L-14 (execution never changes intent). The CIR→PKP one-directional flow is what makes the platform's output auditable and surgically revisable.
- **Irreversibility:** Allowing PKP amendment would require re-introducing creative authority into the execution layer, violating the constitutional separation of powers.
- **Status:** Recommended for ratification.

---

## Conclusion

009 is constitutionally compliant, non-duplicative, and non-overlapping. It architecturalizes the PKP from `001` §5, binds it to the CIR (`007`) via `cir_origin`, and defines the PKP's architecture (artifact model, dependency graph, packaging, distribution, validation, lifecycle) within constitutional bounds. Two gaps (provider replay mechanism, PKG partitioning) are tracked for 010/012.

**Recommendation:** Proceed to 010 — PROMETHEUS Runtime Architecture.