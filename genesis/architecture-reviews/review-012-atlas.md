# Architecture Review — 012 (ATLAS)

**Status:** Coherence Report
**Date:** 2026-07-21
**Subject:** `012 — ATLAS Knowledge Architecture.md`
**Phase:** II — Final Specification

---

## Quality Check Results

| Check | Result | Notes |
|-------|--------|-------|
| **No duplicated concepts** | PASS | The ATLAS pillar is referenced to `001` §2.1 and architecturalized. Director Memory is referenced to `002` Part 6 and persisted, not redefined. Faculty enrichments are referenced to `005` Part 4.3 and persisted, not redefined. New concepts (Knowledge Object, knowledge compaction, cross-runtime knowledge, institutional memory as ATLAS-persisted) are architectural. |
| **No overlapping authority** | PASS | ATLAS persists; it does not decide, cognize, compile, render, or validate (Part 1.3). The single-persistence-authority rule (Part 1.2) is the architectural enforcement of `001` §2.1 invariant 4. |
| **No conflicting terminology** | PASS | "Knowledge Object," "PKG," "provenance," "frozen," "archived" used consistently. |
| **No broken invariants** | PASS | References L-4, L-5, L-8, L-9, L-18, L-19, L-20, L-21, L-25 by reference. No invariant redefined. |
| **No constitutional violations** | PASS | Part 11.3 verifies compliance with L-18, L-19, L-20, L-25. |
| **No circular dependencies** | PASS | All components write to ATLAS; ATLAS does not call any component (`001` §2.3). ATLAS is the mediator, not a participant. |
| **No runtime leakage into cognition** | PASS | ATLAS stores cognition artifacts (enrichments, CIR) but does not perform cognition. |
| **No cognition leakage into execution** | PASS | ATLAS stores execution artifacts (PKP, media) but does not execute. |

---

## Gap Analysis

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| The PKG partitioning between CIR and PKP subgraphs (flagged in review-009) is acknowledged here (Part 2.3: "the PKG is a graph store; ATLAS governs it; the structure is defined by the COM and the CIR") but the storage-level partitioning is not deeply specified. | Low | This is correct at the architectural level: the PKG's structure is defined by the COM (`004`) and the CIR (`007`); ATLAS governs storage, not structure. The storage-level partitioning (e.g., graph database vs. document store) is an implementation concern, not architectural. No action. |
| Knowledge compaction (Part 8.3) is acknowledged but the compaction policy is not deeply specified. | Low | Compaction is governed by the human (Part 11.3: the human may opt out) and is an operational concern. The architectural principle (compaction never discards knowledge, L-18) is sufficient. No action. |

---

## Constitutional Compliance Verification

| Law | How 012 complies |
|-----|------------------|
| L-4 (Shared Semantic Model) | ATLAS stores COM objects; the COM is the shared model. |
| L-5 (Objects Have Identity, Provenance, Lifecycle) | Part 2.2: every Knowledge Object carries identity, provenance, lifecycle. |
| L-8 (Decision Authority Is Defined) | ATLAS has no decision authority (Part 1.3). |
| L-9 (Every Decision Has Provenance) | ATLAS enforces provenance on every stored CIR node. |
| L-18 (Knowledge Outlives Media) | Part 1.1, Part 11.2: indefinite retention. |
| L-19 (History Is Immutable) | Part 1.2, Part 11.2: frozen artifacts are immutable. |
| L-20 (Learning Never Rewrites History) | Part 4.3: archived artifacts are read-only for learning. |
| L-21 (Learning Is Governed) | Part 4.1: pattern updates are persisted with governance approval. |
| L-25 (Human Supremacy) | Part 11.3: the human controls cross-production access and compaction opt-out. |

---

## ADR Candidates

**ADR-006: ATLAS Is the Single Persistence Authority.**
- **Decision:** ATLAS is the only system that writes to durable storage on behalf of the engine. All components issue store/retrieve requests to ATLAS; none write to storage directly.
- **Rationale:** Centralizing persistence ensures provenance integrity (every write goes through ATLAS's provenance enforcement), history immutability (ATLAS enforces immutability on frozen artifacts), and auditability (ORACLE audits a single store, not scattered component-private stores).
- **Irreversibility:** Allowing components to write to storage directly would break provenance integrity and history immutability, violating L-5, L-9, and L-19.
- **Status:** Recommended for ratification.

---

## Conclusion

012 is constitutionally compliant, non-duplicative, and non-overlapping. It architecturalizes the ATLAS pillar from `001` §2.1, defines ATLAS as the Knowledge Operating System and single persistence authority, and enforces L-18 (knowledge outlives media), L-19 (history is immutable), and L-20 (learning never rewrites history). ATLAS holds the platform's creative knowledge and institutional memory, enabling cross-production learning, cross-runtime knowledge sharing, and indefinite preservation.

**Phase II is complete.** All six architectural specifications (007–012) are delivered, reviewed, and constitutionally compliant. The ACI Platform's architecture — from the Constitution (006) through the creative front-end (000–005) through the runtime back-end (007–012) — is fully specified.

**Recommendation:** Ratify the ADRs (ADR-001 through ADR-006) and freeze Phase II.