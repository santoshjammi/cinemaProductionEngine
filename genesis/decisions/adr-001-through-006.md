# Architecture Decision Records (ADRs)

**Status:** Institutional Memory — Design History
**Date:** 2026-07-21
**Governance:** These ADRs are governed by the ACI Constitution (`006` Part 8.7, Long-Term Preservation). ADRs are immutable once ratified; a superseded ADR is marked `superseded` with a reference to the superseding ADR, never edited.

---

## ADR Index

| ADR | Decision | Status | Source |
|-----|----------|--------|--------|
| ADR-001 | The CIR is the Intermediate Representation of Artificial Creativity. | Recommended for ratification | review-007 |
| ADR-002 | The Compiler Is a Pass-Based Pipeline with Isolated Passes. | Recommended for ratification | review-008 |
| ADR-003 | The PKP Is Read-Only for All Downstream Consumers. | Recommended for ratification | review-009 |
| ADR-004 | The Runtime Has Zero Creative Authority. | Recommended for ratification | review-010 |
| ADR-005 | ORACLE Is Advisory, Not Authoritative. | Recommended for ratification | review-011 |
| ADR-006 | ATLAS Is the Single Persistence Authority. | Recommended for ratification | review-012 |

---

## ADR-001: The CIR is the Intermediate Representation of Artificial Creativity

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-007-cir.md

### Decision

The Creative Intent Record (CIR) — not the CIS, not the PKP — is the Intermediate Representation (IR) that sits between creative cognition and compilation.

### Context

The ACI Platform has a three-artifact chain: CIS (intent) → CIR (reasoning) → PKP (executable). Each artifact answers a different question: the CIS answers "what does the human want?"; the PKP answers "what do I render?"; the CIR answers "why was each creative decision made, and what is the executable creative representation?"

### Rationale

The CIR carries both the decision and its rationale (the "what" and the "why"), enabling:
- **Explainability** (L-10): the "why?" query traverses the CIR's provenance.
- **Surgical revision** (`007` Part 10.5): a drift report names a CIR node; only that node and its dependents re-enter the pipeline.
- **Deterministic replay** (L-13): the CIR hash pins the creative state for replay.

The CIS carries intent without decisions; the PKP carries compiled decisions without rationale. Only the CIR carries both. Removing the CIR would collapse the chain into a two-artifact chain, losing either explainability (CIS→PKP) or intent-decision separation (CIS+CIR→PKP).

### Irreversibility

Removing the CIR would require re-introducing creative reasoning into either the CIS (making intent non-human-authored, violating L-2) or the PKP (making the compiled binary carry reasoning, breaking the compiler metaphor and L-13). The three-artifact chain is the foundation of surgical revision and constitutional explainability.

### Constitutional Grounding

L-6 (cognition precedes decision), L-8 (decision authority is defined), L-9 (every decision has provenance), L-10 (every decision is explainable), L-11 (decision precedes compilation), L-19 (history is immutable).

---

## ADR-002: The Compiler Is a Pass-Based Pipeline with Isolated Passes

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-008-compiler.md

### Decision

The GENESIS Compiler is a pipeline of isolated passes, each with a defined contract, communicating only through the PKP-in-progress. Passes do not read other passes' internal state, do not communicate directly, and do not modify the CIR.

### Context

The compiler transforms the CIR into the PKP through 19 passes (`001` §4.2). Each pass reads specific CIR nodes and produces specific PKP artifacts.

### Rationale

Pass isolation enables:
- **Incremental compilation** (`008` Part 7): only changed passes re-run; unchanged passes reuse cached outputs.
- **Parallelism** (`008` Part 4): independent passes run concurrently.
- **Determinism** (`008` Part 1.2): no hidden cross-pass state means the same inputs always produce the same outputs.

Without isolation, hidden cross-pass state would break all three properties, making the compiler non-deterministic and non-incremental.

### Irreversibility

Moving away from isolated passes (e.g., to a monolithic compiler) would require abandoning incremental compilation and surgical revision — the platform's core revision mechanism. The entire quality loop (ORACLE drift → CIR revision → incremental recompilation → re-render → re-validate) depends on pass isolation.

### Constitutional Grounding

L-11 (decision precedes compilation), L-12 (compilation never invents creativity), L-13 (production knowledge is compiled).

---

## ADR-003: The PKP Is Read-Only for All Downstream Consumers

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-009-pkp.md

### Decision

The PKP is read-only for PROMETHEUS, ORACLE, and the human. Amendments go through the CIR (re-compilation), never through the PKP directly.

### Context

The PKP is the compiled executable specification. PROMETHEUS renders it; ORACLE validates against it; the human inspects it. None of these consumers may modify it.

### Rationale

If any downstream consumer could amend the PKP, the PKP would no longer be the deterministic compiled output of the CIR, breaking:
- **L-13** (compiled, not generated): an amended PKP is generated, not compiled.
- **L-14** (execution never changes intent): if PROMETHEUS could amend the PKP, execution would change intent.
- **Deterministic replay**: an amended PKP cannot be reproduced from the CIR.

The CIR→PKP one-directional flow is what makes the platform's output auditable and surgically revisable.

### Irreversibility

Allowing PKP amendment would require re-introducing creative authority into the execution layer, violating the constitutional separation of powers (L-8, L-14, L-15).

### Constitutional Grounding

L-13 (production knowledge is compiled), L-14 (execution never changes intent), L-15 (execution never invents creativity), L-16 (validation never mutates).

---

## ADR-004: The Runtime Has Zero Creative Authority

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-010-prometheus.md

### Decision

PROMETHEUS is a pure executor; it has zero creative authority (L-15). If the PKP is silent on a detail, the runtime reports a rendering gap rather than inventing.

### Context

PROMETHEUS reads the PKP and renders media. The PKP is the executable specification; it carries "what to render." The runtime does not exercise creative judgment.

### Rationale

If the runtime could invent creative content:
- The media would not trace to the CIR (via `cir_origin` on PKP artifacts), breaking the traceability chain.
- ORACLE could not detect drift, because the runtime's inventions would be indistinguishable from the Board's decisions.
- The platform's deterministic replay chain would break at the final link (media would be non-deterministic).

The runtime's zero-creative-authority is what makes the entire four-pillar model coherent: the Board decides; the compiler compiles; the runtime renders; ORACLE validates. Each pillar has a distinct, non-overlapping authority.

### Irreversibility

Granting the runtime creative authority would collapse the separation of execution from cognition, violating L-15 and the constitutional separation of powers. The four-pillar model would degenerate into a generator.

### Constitutional Grounding

L-14 (execution never changes intent), L-15 (execution never invents creativity).

---

## ADR-005: ORACLE Is Advisory, Not Authoritative

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-011-oracle.md

### Decision

ORACLE writes validation reports; it never mutates artifacts (L-16) and never forces a decision. The human and the Board decide what to do with ORACLE's reports.

### Context

ORACLE is the independent validation authority. It validates media against the CIR (decisions) and the CIS (intent). It produces drift reports, quality scores, certification, and audits.

### Rationale

If ORACLE could mutate or force:
- It would become a second decision authority, violating L-8 (decision authority is defined — the Board's).
- It would violate L-25 (human supremacy): the human, not ORACLE, is the final authority.
- Validation would become self-assessment if ORACLE could "fix" what it found wrong.

Validation must be advisory to preserve the separation of validation from decision. ORACLE reports; the human and the Board decide.

### Irreversibility

Making ORACLE authoritative would collapse the separation of validation from decision, creating a second decision body and violating the constitutional separation of powers.

### Constitutional Grounding

L-16 (validation never mutates), L-17 (validation is against intent and decisions), L-25 (human supremacy).

---

## ADR-006: ATLAS Is the Single Persistence Authority

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-012-atlas.md

### Decision

ATLAS is the only system that writes to durable storage on behalf of the engine. All components issue store/retrieve requests to ATLAS; none write to storage directly.

### Context

ATLAS is the Knowledge Operating System. It persists the CIS, CIR, PKP, media, validation reports, Director Memory, faculty enrichments, and institutional memory. All other components (the Board, the compiler, PROMETHEUS, ORACLE, the Creative Mind) interact with storage through ATLAS.

### Rationale

Centralizing persistence ensures:
- **Provenance integrity**: every write goes through ATLAS's provenance enforcement (L-5, L-9). No component can write an artifact without provenance.
- **History immutability**: ATLAS enforces immutability on frozen artifacts (L-19). No component can overwrite a frozen artifact.
- **Auditability**: ORACLE audits a single store, not scattered component-private stores. The platform's full history is in one place.

If components could write to storage directly, provenance chains would be broken by components that do not record provenance correctly, history would be mutable by components that overwrite frozen artifacts, and audit would be impossible.

### Irreversibility

Allowing components to write to storage directly would break provenance integrity and history immutability, violating L-5, L-9, and L-19. The platform's auditability and reproducibility depend on ATLAS being the single persistence authority.

### Constitutional Grounding

L-5 (objects have identity, provenance, lifecycle), L-9 (every decision has provenance), L-18 (knowledge outlives media), L-19 (history is immutable).

---

## ADR Process

ADRs are created during architecture reviews and ratified by the human (`006` L-25 applies to architectural decisions as to intent). Once ratified, an ADR is immutable; it may be superseded by a new ADR that references it, but it is never edited. Superseded ADRs are marked `superseded` with a reference to the superseding ADR.

ADRs are persisted in ATLAS (`012` Part 10) as institutional memory, ensuring the platform's irreversible decisions and their rationale survive indefinitely.

---

**End of ADRs.**