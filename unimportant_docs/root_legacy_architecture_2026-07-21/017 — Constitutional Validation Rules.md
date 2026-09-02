# 017 — Constitutional Validation Rules

**Status:** Platform Engineering Specification — Phase III
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution, Part 3 Laws and Part 9 Compliance); `004` (COM, Part 5 Invariants); `013` (Repository); `014` (Governance Engine); `015` (Registry); `016` (Metadata).
**Precedence:** Below the Constitution. This specification defines the **executable validation rules** the Governance Engine (014) applies.
**Scope:** Law validation, invariant validation, authority validation, ownership validation, dependency validation, repository validation, reference validation, review validation, ADR validation, ontology validation, schema validation, compliance scoring, violation severity, certification rules, lifecycle, evolution.

---

## Table of Contents

1. [Philosophy](#1-philosophy)
2. [Objectives](#2-objectives)
3. [Principles](#3-principles)
4. [Architecture](#4-architecture)
5. [Components](#5-components)
6. [Responsibilities](#6-responsibilities)
7. [Governance](#7-governance)
8. [Lifecycle](#8-lifecycle)
9. [Integration](#9-integration)
10. [Migration](#10-migration)
11. [Future Evolution](#11-future-evolution)

---

# 1. Philosophy

## 1.1 The Laws Made Executable

The Constitution (`006` Part 3) defines 25 constitutional laws (L-1..L-25). The COM (`004` Part 5) defines 40 semantic invariants (I-SI-1..I-SI-40). These are constitutional text — authoritative, but not directly executable by a machine. The Constitutional Validation Rules are the **executable form** of these laws and invariants: precise, machine-applicable rules that the Governance Engine (014) applies to artifacts.

A rule is not a law; a rule is the executable projection of a law. The law is supreme; the rule is its enforcement mechanism. If a rule and a law conflict, the law prevails, and the rule is amended.

## 1.2 Constitutional Derivation

| Law | How it governs the rules |
|-----|-------------------------|
| L-16 (Validation Never Mutates) | The rules report violations; they do not fix. |
| L-22 (Amendments Require Process) | The rules enforce that amendments follow the process. |

---

# 2. Objectives

| # | Objective |
|---|-----------|
| O-1 | Every constitutional law (L-1..L-25) has a corresponding executable rule. |
| O-2 | Every COM invariant (I-SI-1..I-SI-40) has a corresponding executable rule. |
| O-3 | Every rule produces a finding (blocking, warning, advisory) with evidence. |
| O-4 | Rules are applied by the Governance Engine (014) without human judgment. |
| O-5 | Rules are governable: new rules require architectural amendment; rules do not self-modify. |

---

# 3. Principles

| # | Principle |
|---|-----------|
| VR-1 | **Rules derive from laws.** Every rule names the law or invariant it enforces. |
| VR-2 | **Rules are advisory.** Rules report; they do not mutate (L-16). |
| VR-3 | **Rules are deterministic.** The same artifact + the same rule → the same finding. |
| VR-4 | **Rules are transparent.** Every finding names the rule, the law, the evidence, and the severity. |

---

# 4. Architecture

## 4.1 The Rule Specification Contract

Every rule is specified by:

| Field | Definition |
|-------|-----------|
| **Rule identifier** | `VR-<ordinal>` (e.g., VR-1). |
| **Law reference** | The constitutional law (L-N) or invariant (I-SI-N) this rule enforces. |
| **Rule statement** | The rule, in one declarative sentence. |
| **Scope** | What the rule applies to (which artifacts, which layers). |
| **Check** | What the Governance Engine checks. |
| **Evidence** | What evidence the finding provides. |
| **Severity** | `blocking / warning / advisory`. |

## 4.2 Law Validation Rules

Each constitutional law (L-1..L-25) has a corresponding executable rule. The full catalog is extensive; the pattern is:

| Rule | Law | Statement | Severity |
|------|-----|-----------|----------|
| VR-1 | L-1 | The CIR Root references a pinned, approved CIS. | Blocking. |
| VR-2 | L-2 | No CIR node's provenance shows engine-authored intent in CIS domains. | Blocking. |
| VR-3 | L-3 | The CIR's `cis_version` is pinned and matches an approved CIS version. | Blocking. |
| VR-4 | L-4 | All artifacts in the repository use the COM's identity and relationship model; no competing semantic model is present. | Blocking. |
| VR-5 | L-5 | Every artifact has identity, provenance, and lifecycle. | Blocking. |
| VR-6 | L-6 | Every CIR node references faculty enrichments in its provenance. | Blocking. |
| VR-7 | L-7 | No CIR node names a faculty as its decision authority. | Blocking. |
| VR-8 | L-8 | Every CIR node names a home director. | Blocking. |
| VR-9 | L-9 | Every CIR node is provenance-complete. | Blocking. |
| VR-10 | L-10 | The `explain` query returns a valid answer for every CIR node. | Blocking. |
| VR-11 | L-11 | Every PKP artifact carries `cir_origin` referencing a frozen CIR node. | Blocking. |
| VR-12 | L-12 | No PKP artifact has content not traceable to a CIR node. | Blocking. |
| VR-13 | L-13 | The PKP hash matches the compiler's recorded hash. | Blocking. |
| VR-14 | L-14 | No media has content not traceable to a PKP artifact. | Blocking. |
| VR-15 | L-15 | (Same as VR-14; render-time invention is drift.) | Blocking. |
| VR-16 | L-16 | No validator (ORACLE or Governance Engine) has written to any artifact other than a validation/compliance report. | Blocking. |
| VR-17 | L-17 | Every validation report references CIR nodes or CIS domains. | Blocking. |
| VR-18 | L-18 | All knowledge artifacts (CIS, CIR, PKP, reports) are persisted in ATLAS. | Blocking. |
| VR-19 | L-19 | No frozen artifact has been mutated; all revisions create new versions. | Blocking. |
| VR-20 | L-20 | No learning operation has retroactively re-reasoned an archived production. | Blocking. |
| VR-21 | L-21 | All cognitive-pattern updates have governance approval. | Blocking. |
| VR-22 | L-22 | All constitutional amendments follow the amendment process. | Blocking. |
| VR-23 | L-23 | Every runtime constitution derives from the ACI Constitution. | Blocking. |
| VR-24 | L-24 | No evolution violates a constitutional law. | Blocking. |
| VR-25 | L-25 | No component has overridden human intent authority without a recorded human override. | Blocking. |

## 4.3 Invariant Validation Rules

Each COM invariant (I-SI-1..I-SI-40) has a corresponding executable rule. The pattern:

| Rule | Invariant | Statement | Severity |
|------|-----------|-----------|----------|
| VR-26 | I-SI-1 | Every Scene has a Purpose. | Blocking. |
| VR-27 | I-SI-2 | Every Beat belongs to exactly one Scene. | Blocking. |
| ... | ... | ... | ... |
| VR-65 | I-SI-40 | The sum of Runtime Segment durations equals the Timeline total runtime. | Blocking. |

(40 rules, one per invariant. The full catalog is the executable projection of `004` Part 5.)

## 4.4 Authority Validation

| Rule | Statement | Severity |
|------|-----------|----------|
| VR-66 | Every artifact's `deriving_authority` references an existing, ratified artifact. | Blocking. |
| VR-67 | Every artifact's `constitutional_tier` is lower than or equal to its deriving authority's tier. | Blocking. |
| VR-68 | The authority graph is acyclic. | Blocking. |

## 4.5 Ownership Validation

| Rule | Statement | Severity |
|------|-----------|----------|
| VR-69 | Every directory has a defined owner (013 Part 4.3). | Warning. |
| VR-70 | No artifact is owned by a body that does not have authority over the artifact's tier. | Blocking. |

## 4.6 Dependency Validation

| Rule | Statement | Severity |
|------|-----------|----------|
| VR-71 | Every dependency reference points to an existing artifact. | Blocking. |
| VR-72 | The dependency graph has no cycles. | Blocking. |

## 4.7 Repository Validation

| Rule | Statement | Severity |
|------|-----------|----------|
| VR-73 | Every artifact is in its canonical directory (013 Part 4.2). | Blocking. |
| VR-74 | Every artifact's name follows the naming convention (013 Part 4.4). | Warning. |
| VR-75 | Every artifact has a metadata header (016). | Blocking. |
| VR-76 | The metadata header is valid (016 Part 4.6). | Blocking. |

## 4.8 Reference Validation

| Rule | Statement | Severity |
|------|-----------|----------|
| VR-77 | Every cross-reference in a document points to an existing artifact. | Blocking. |
| VR-78 | No cross-reference is ambiguous (points to multiple artifacts). | Warning. |

## 4.9 Review Validation

| Rule | Statement | Severity |
|------|-----------|----------|
| VR-79 | Every ratified artifact has a corresponding architecture review. | Warning. |
| VR-80 | Every architecture review's findings have been addressed (blocking findings remediated). | Blocking. |

## 4.10 ADR Validation

| Rule | Statement | Severity |
|------|-----------|----------|
| VR-81 | Every ADR has a status (recommended / ratified / superseded). | Warning. |
| VR-82 | No ratified ADR has been edited (immutability, L-19). | Blocking. |

## 4.11 Ontology Validation

| Rule | Statement | Severity |
|------|-----------|----------|
| VR-83 | Every ontology term used in a specification references a GO identity. | Warning. |
| VR-84 | No specification defines an ontology term that duplicates a GO term. | Blocking. |

## 4.12 Schema Validation

| Rule | Statement | Severity |
|------|-----------|----------|
| VR-85 | Every schema referenced in a specification exists in the schema registry. | Warning. |
| VR-86 | No schema contradicts the COM's object types. | Blocking. |

## 4.13 Compliance Scoring

The Governance Engine (014) produces a **compliance score** for each validation:

| Score | Definition |
|-------|-----------|
| **Compliant** | Zero blocking findings. |
| **Compliant with warnings** | Zero blocking findings; one or more warnings. |
| **Non-compliant** | One or more blocking findings. |

## 4.14 Violation Severity

(As defined in 014 Part 4.2: blocking, warning, advisory.)

## 4.15 Certification Rules

(As defined in 014 Part 4.4: an artifact is certified when it is compliant; a release is certified when all its artifacts are certified.)

---

# 5. Components

| Component | What it is |
|-----------|-----------|
| **Rule Registry** | The registry of all validation rules (VR-1..VR-86+). |
| **Rule Engine** | The engine that applies rules to artifacts (part of the Governance Engine, 014). |
| **Finding Generator** | Produces findings from rule applications. |

---

# 6. Responsibilities

| Body | Responsibility |
|------|---------------|
| **Rule authors** | Define rules that faithfully project laws and invariants. |
| **Governance Engine (014)** | Applies the rules. |
| **Constitutional Review Board** | Reviews new rules and rule amendments. |

---

# 7. Governance

| Change type | Authority |
|--------------|-----------|
| **New rule** | Architectural amendment to this specification. |
| **Rule amendment** | Architectural amendment (the rule's corresponding law must still be faithfully projected). |
| **Rule deprecation** | Architectural amendment (the law must be deprecated first, per `006` Part 8.2). |

## 7.1 Rule and Law Synchronization

If a law is amended (`006` Part 8.1), the corresponding rule is amended to match. If a law is deprecated, the corresponding rule is deprecated. The Rule Registry tracks the law-rule mapping; the Governance Engine detects when a rule does not match its law (synchronization drift).

---

# 8. Lifecycle

```
rule proposed → rule reviewed → rule ratified → rule published → (rule amended) → (rule deprecated) → (rule obsolete)
```

Rules follow the same lifecycle as specifications (013 Part 8.1). A rule is immutable once ratified; amendments create new rule versions.

---

# 9. Integration

| Spec | Integration |
|------|-------------|
| `006` (Constitution) | The rules are the executable projection of the laws. |
| `004` (COM) | The rules are the executable projection of the invariants. |
| `014` (Governance Engine) | Applies the rules. |
| `015` (Registry) | Provides the artifact graph the rules operate on. |
| `016` (Metadata) | Rules validate metadata. |
| `018` (Developer Platform) | Provides tooling for rule authoring and validation. |

---

# 10. Migration

## 10.1 Migration Phases

### Phase VR-1 — Rule Definition
- Define the executable rules (VR-1..VR-86) from the constitutional laws and COM invariants.
- Register the rules in the Rule Registry.

### Phase VR-2 — Rule Engine Integration
- Integrate the rules with the Governance Engine (014).

### Phase VR-3 — Law-Rule Synchronization Verification
- Verify that every law has a corresponding rule; verify synchronization.

## 10.2 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| Constitutional laws (L-1..L-25) | **Preserved.** Rules project them; they do not modify them. | None. |
| COM invariants (I-SI-1..I-SI-40) | **Preserved.** Rules project them. | None. |

## 10.3 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Rule-law desynchronization.** A law is amended but the rule is not updated. | Medium | The Rule Registry tracks the mapping; the Governance Engine detects desynchronization. |
| **Rule completeness.** Not all laws may have rules initially. | Medium | Phase VR-3 verifies completeness; gaps are tracked. |

---

# 11. Future Evolution

## 11.1 New Rules
New rules are added as new laws or invariants are ratified, or as new validation concerns emerge (e.g., security, performance).

## 11.2 AI-Assisted Rule Generation
AI agents may draft rules from laws, with human review and ratification.

## 11.3 Self-Validating Rules
The rules may evolve to validate themselves (meta-rules that check rule-law synchronization).

---

## Architectural Rules (Restated)

This specification produced no implementation code. It defines the executable validation rules — the machine-applicable projection of the constitutional laws (L-1..L-25) and the COM invariants (I-SI-1..I-SI-40) — that the Governance Engine (014) applies to artifacts. Rules are advisory (VR-2, L-16), deterministic (VR-3), and transparent (VR-4).

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | Part 3 (Laws) — the rules project these. |
| `004` (COM) | Part 5 (Invariants) — the rules project these. |
| `014` (Governance Engine) | Applies the rules. |
| `015` (Registry) | Provides the artifact graph. |
| `016` (Metadata) | Rules validate metadata. |
| `018` (Developer Platform) | Provides rule tooling. |

---

**End of Specification.**