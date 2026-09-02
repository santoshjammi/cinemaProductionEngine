# Architecture Review — 011 (ORACLE)

**Status:** Coherence Report
**Date:** 2026-07-21
**Subject:** `011 — ORACLE Validation Architecture.md`

---

## Quality Check Results

| Check | Result | Notes |
|-------|--------|-------|
| **No duplicated concepts** | PASS | The ORACLE pillar is referenced to `001` §2.1 and architecturalized. The Creative Metrics are referenced to `002` Part 11 and measured, not redefined. The COM invariants are referenced to `004` Part 5 and enforced, not redefined. New concepts (five-layer validation model, drift report, certification report, violation report, audit report) are architectural. |
| **No overlapping authority** | PASS | ORACLE validates; it does not decide (`002`), does not compile (`008`), does not render (`010`), does not persist (`012`). Part 1.2 (never mutates) and Part 6 contracts are explicit. |
| **No conflicting terminology** | PASS | "drift," "certification," "validation report," "cir_origin" used consistently. |
| **No broken invariants** | PASS | References 10 COM invariants (I-SI-1, 3, 5, 7, 8, 9, 14, 15, 19, 21) and 17 constitutional laws by reference. No invariant is redefined. |
| **No constitutional violations** | PASS | Part 13.3 verifies compliance with L-16, L-17, L-9, L-10, L-12, L-14, L-15, L-22. |
| **No circular dependencies** | PASS | ORACLE reads artifacts from ATLAS and writes reports to ATLAS. The violation loop (Part 12.3) is mediated by ATLAS; no direct calls. |
| **No runtime leakage into cognition** | PASS | ORACLE validates artifacts; it does not perform cognition. |
| **No cognition leakage into execution** | PASS | ORACLE validates against the CIR (decisions) and the CIS (intent), not against its own creative judgment (L-17, Part 1.3). |

---

## Gap Analysis

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| The "subjective-proxy checks" (Part 5.2: emotion detection, theme classification models) are acknowledged as model-based estimates with confidence levels, but the governance of these models is not deeply specified. | Low | The models are providers behind the capability registry (`010` Part 5.1); their governance follows the same provider-governance rules. No action at the architectural level. |
| ORACLE's role as the enforcer of the Constitution (Part 7: certification) is a significant authority. The spec correctly makes it advisory (the human can override), but the relationship between ORACLE's certification and the Constitutional Review Board (`006` Part 7.5) could be clearer. | Low | ORACLE certifies productions; the Constitutional Review Board reviews amendments and interpretations. They are distinct bodies with distinct scopes. The spec is correct; no action. |

---

## Constitutional Compliance Verification

| Law | How 011 complies |
|-----|------------------|
| L-1 (Intent Precedes Cognition) | Part 3: ORACLE checks CIR Root references a pinned CIS. |
| L-2 (Intent Is Human-Authored) | Part 3: ORACLE audits for engine-authored intent. |
| L-4, L-5 (Shared Semantic Model, Object Identity) | Part 4: semantic validation. |
| L-6 (Cognition Precedes Decision) | Part 3: ORACLE audits CIR provenance for enrichment references. |
| L-8 (Decision Authority Is Defined) | Part 3: ORACLE audits for home director. |
| L-9, L-10 (Provenance, Explainability) | Part 3, Part 4.2. |
| L-11 (Decision Precedes Compilation) | Part 3: `cir_origin` audit. |
| L-12 (Compilation Never Invents) | Part 5.3: compile-time drift detection. |
| L-13 (Production Knowledge Is Compiled) | Part 3: hash verification. |
| L-14, L-15 (Execution Never Changes/Invents) | Part 5.4: render-time drift detection. |
| L-16 (Validation Never Mutates) | Part 1.2: writes only reports. |
| L-17 (Validation Against Intent and Decisions) | Part 1.3, Part 5. |
| L-18 (Knowledge Outlives Media) | Part 7: archive audit. |
| L-19 (History Is Immutable) | Part 3: version integrity audit. |
| L-22 (Constitutional Amendments Require Process) | Part 7: certification enforces constitutional compliance. |
| L-25 (Human Supremacy) | Part 7.2, Part 11.2: human can override certification and blocking findings. |

---

## ADR Candidates

**ADR-005: ORACLE Is Advisory, Not Authoritative.**
- **Decision:** ORACLE writes validation reports; it never mutates artifacts (L-16) and never forces a decision. The human and the Board decide what to do with ORACLE's reports.
- **Rationale:** If ORACLE could mutate or force, it would become a second decision authority, violating L-8 (decision authority is defined — the Board's) and L-25 (human supremacy). Validation must be advisory to preserve the separation of powers.
- **Irreversibility:** Making ORACLE authoritative would collapse the separation of validation from decision, violating the constitutional separation of powers.
- **Status:** Recommended for ratification.

---

## Conclusion

011 is constitutionally compliant, non-duplicative, and non-overlapping. It architecturalizes the ORACLE pillar from `001` §2.1, defines ORACLE as the independent validation authority with five layers (constitution, semantic, creative, runtime, compliance), and enforces L-16 (never mutates) and L-17 (validates against intent and decisions). ORACLE's drift detection enables surgical revision; its certification enforces constitutional compliance; its audits inform governance.

**Recommendation:** Proceed to 012 — ATLAS Knowledge Architecture (the final Phase II specification).