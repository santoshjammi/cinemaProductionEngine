# Architecture Decision Records (ADRs) — Phase III

**Status:** Institutional Memory — Design History
**Date:** 2026-07-21
**Governance:** These ADRs are governed by the ACI Constitution (`006` Part 8.7). ADRs are immutable once ratified.

---

## ADR Index (Phase III)

| ADR | Decision | Status | Source |
|-----|----------|--------|--------|
| ADR-007 | The Repository Structure Mirrors the Constitutional Tier Hierarchy. | Recommended for ratification | review-013 |
| ADR-008 | The Governance Engine Is Advisory, Not Authoritative. | Recommended for ratification | review-014 |
| ADR-009 | The Registry Is Derived, Not Authored. | Recommended for ratification | review-015 |
| ADR-010 | Metadata Is Mandatory for Every Architectural Artifact. | Recommended for ratification | review-016 |
| ADR-011 | Rules Are the Executable Projection of Laws, Not Laws Themselves. | Recommended for ratification | review-017 |
| ADR-012 | The Developer Platform Has No Constitutional Authority. | Recommended for ratification | review-018 |

---

## ADR-007: The Repository Structure Mirrors the Constitutional Tier Hierarchy

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-013-repository.md

### Decision

The repository's directory taxonomy mirrors the constitutional tiers (Tier 0 Constitution at root, Tier 1 runtime constitutions in docs/genesis/constitutions/, Tier 2 specifications at root, Tier 3 standards in docs/genesis/, Tier 4 implementation in code directories).

### Rationale

If the repository structure did not mirror the tiers, a contributor could not locate an artifact by its constitutional authority, and the Governance Engine could not validate the repository automatically. The tier-reflected structure is what makes the repository self-validating and AI-native.

### Constitutional Grounding

L-4 (shared semantic model), L-19 (history is immutable), L-22 (amendments require process).

---

## ADR-008: The Governance Engine Is Advisory, Not Authoritative

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-014-governance.md

### Decision

The Governance Engine reports compliance and violations; it never mutates artifacts, never blocks operations autonomously, and never amends the Constitution. The Constitutional Review Board and the human decide remediation.

### Rationale

If the engine could mutate or block, it would become a second legislative or executive authority, violating the separation of powers.

### Constitutional Grounding

L-16 (validation never mutates), L-22 (amendments require process), L-25 (human supremacy).

---

## ADR-009: The Registry Is Derived, Not Authored

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-015-registry.md

### Decision

The Architecture Registry is built by scanning the repository's documents and metadata, not by hand-editing.

### Rationale

A hand-edited Registry would drift from the repository; a derived Registry is always consistent (rebuildable). This is the architectural analog of the PKG being derived from the CIR.

### Constitutional Grounding

L-4 (shared semantic model), L-5 (identity, provenance, lifecycle).

---

## ADR-010: Metadata Is Mandatory for Every Architectural Artifact

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-016-metadata.md

### Decision

Every document in the repository must carry a metadata header (016 Part 4.1). A document without metadata is non-compliant.

### Rationale

Without mandatory metadata, the Registry cannot index the document, the Governance Engine cannot validate it, and AI agents cannot discover it. Mandatory metadata is what makes the repository machine-readable.

### Constitutional Grounding

L-4 (shared semantic model), L-5 (identity, provenance, lifecycle), L-22 (amendments require process).

---

## ADR-011: Rules Are the Executable Projection of Laws, Not Laws Themselves

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-017-validation-rules.md

### Decision

Validation rules (VR-N) are the machine-applicable projection of constitutional laws (L-N) and COM invariants (I-SI-N). If a rule and a law conflict, the law prevails.

### Rationale

If rules were laws, the rule set would become a second constitution, independently amendable. Keeping rules as projections ensures the Constitution remains supreme.

### Constitutional Grounding

L-16 (validation never mutates), L-22 (amendments require process).

---

## ADR-012: The Developer Platform Has No Constitutional Authority

**Date:** 2026-07-21
**Status:** Recommended for ratification
**Source:** review-018-developer-platform.md

### Decision

The Developer Platform is a tool layer; it has no creative, decision, governance, or validation authority. It consumes the Registry and the Governance Engine; it does not replace them.

### Rationale

If the platform had authority, it would become a parallel governance system, violating the constitutional separation of powers.

### Constitutional Grounding

L-22 (amendments require process), L-25 (human supremacy).

---

**End of Phase III ADRs.**