# Architecture Review — 017 (Validation Rules)

**Status:** Coherence Report
**Date:** 2026-07-21
**Subject:** `017 — Constitutional Validation Rules.md`

## Quality Check Results

| Check | Result | Notes |
|-------|--------|-------|
| No duplicated concepts | PASS | Rules are the executable projection of laws and invariants; they are not new laws. Each rule names its source law/invariant. |
| No duplicated authority | PASS | Rules are applied by the Governance Engine (014); they do not self-execute, do not mutate (VR-2, L-16). |
| No terminology conflicts | PASS | "Rule" (VR-N) is distinct from "Law" (L-N) and "Invariant" (I-SI-N). Clear hierarchy. |
| No invariant collisions | PASS | Rules project invariants; they do not redefine them. |
| No law collisions | PASS | Rules project laws; they do not redefine them. |
| No circular dependencies | PASS | Rules are applied to artifacts by the Governance Engine. Rules do not depend on the artifacts they validate. |
| No missing references | PASS | Cross-references to 004, 006, 014–016, 018 complete. |
| No constitutional violations | PASS | Rules are advisory (VR-2, L-16); deterministic (VR-3); transparent (VR-4). |

## ADR Candidates

**ADR-011: Rules Are the Executable Projection of Laws, Not Laws Themselves.**
- **Decision:** Validation rules (VR-N) are the machine-applicable projection of constitutional laws (L-N) and COM invariants (I-SI-N). If a rule and a law conflict, the law prevails.
- **Rationale:** If rules were laws, the rule set would become a second constitution, draggable and amendable independently of the real Constitution. Keeping rules as projections ensures the Constitution remains supreme and the rules are always synchronized with it.
- **Status:** Recommended for ratification.

## Conclusion

017 is constitutionally compliant, non-duplicative, and non-overlapping. One ADR candidate (ADR-011: rules are projections). **Proceed to 018.**