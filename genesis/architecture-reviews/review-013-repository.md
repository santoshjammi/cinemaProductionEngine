# Architecture Review — 013 (Repository & Metadata)

**Status:** Coherence Report
**Date:** 2026-07-21
**Subject:** `013 — Repository & Metadata Architecture.md`

---

## Quality Check Results

| Check | Result | Notes |
|-------|--------|-------|
| **No duplicated concepts** | PASS | The repository structure formalizes the existing layout (000–012 at root, genesis/ for institutional memory, docs/genesis/ for cinema-runtime). No concept is duplicated; the tier hierarchy mirrors `006` Part 1.5. |
| **No duplicated authority** | PASS | Folder ownership (Part 4.3) assigns each directory to a distinct owner (Constitutional Review Board for root, GFS-007 for cinema constitutions, engineering teams for implementation). No overlap. |
| **No terminology conflicts** | PASS | "Tier 0/1/2/3/4" used consistently with `006` Part 1.5. "Institutional memory" used consistently with `genesis/README.md`. |
| **No invariant collisions** | PASS | References L-4, L-19, L-22, L-25 by reference. No new invariants introduced. |
| **No law collisions** | PASS | No new laws; L-22 (amendments require process) governs structural changes, L-19 (history is immutable) governs git history. |
| **No circular dependencies** | PASS | The repository contains artifacts; it does not depend on them at runtime. The Governance Engine (014) reads the repository; the repository does not read the Governance Engine. |
| **No missing references** | PASS | Cross-references to 000–012, 014–018, genesis/ subdirectories, docs/genesis/ subdirectories are complete. |
| **No constitutional violations** | PASS | The repository structure reflects the constitutional tier hierarchy; metadata is mandatory (RP-3); history is immutable (RP-5, L-19). |

---

## Gap Analysis

| Gap | Severity | Recommendation |
|-----|----------|----------------|
| The metadata model is referenced (Part 4.5) but defined in 016, not here. This is correct (separation of concerns) but means 013 and 016 are tightly coupled. | Low | This is intentional: 013 governs the repository structure; 016 governs the metadata content. The coupling is architectural, not a defect. No action. |
| The naming convention for GFS files (Part 4.4) references `001` TD-006's normalization recommendation but does not enforce it. | Low | Enforcement is a Governance Engine (014) responsibility, not a repository architecture responsibility. 013 correctly states the convention; 014 enforces it. No action. |

---

## Constitutional Compliance Verification

| Law | How 013 complies |
|-----|------------------|
| L-4 (Shared Semantic Model) | The repository's taxonomy mirrors the COM's object taxonomy and the constitutional tiers. |
| L-19 (History Is Immutable) | RP-5: git history is immutable; amendments create new commits. |
| L-22 (Constitutional Amendments Require Process) | Part 7.1: structural changes require governance approval. |
| L-25 (Human Supremacy) | Ratification of root specifications requires human approval (Part 8.1). |

---

## ADR Candidates

**ADR-007: The Repository Structure Mirrors the Constitutional Tier Hierarchy.**
- **Decision:** The repository's directory taxonomy mirrors the constitutional tiers (Tier 0 Constitution at root, Tier 1 runtime constitutions in docs/genesis/constitutions/, Tier 2 specifications at root, Tier 3 standards in docs/genesis/, Tier 4 implementation in code directories).
- **Rationale:** If the repository structure did not mirror the tiers, a contributor could not locate an artifact by its constitutional authority, and the Governance Engine could not validate the repository against the Constitution automatically. The tier-reflected structure is what makes the repository self-validating and AI-native.
- **Irreversibility:** Decoupling the repository structure from the constitutional tiers would break the Governance Engine's automated validation and the Architecture Registry's authority graph construction.
- **Status:** Recommended for ratification.

---

## Potential Ontology Additions

- A `RepositoryDirectory` concept in the COM, with `contains` relationships to documents. This would enable the Architecture Registry (015) to model the repository as a graph. Track for 015.

## Potential Schema Additions

- A repository metadata schema (defined in 016, not here) that formalizes the metadata header fields. Track for 016.

## Potential Implementation Implications

- A metadata backfill tool (Phase REP-1) that adds metadata headers to existing documents.
- A naming normalization tool (Phase REP-4) that renames GFS files per `001` TD-006.
- A repository graph generator (018) that visualizes the directory taxonomy and document hierarchy.

---

## Conclusion

013 is constitutionally compliant, non-duplicative, and non-overlapping. It formalizes the existing repository structure, establishes the tier-reflected taxonomy, makes metadata mandatory, and governs structural changes under the Constitution. One ADR candidate (ADR-007: repository structure mirrors constitutional tiers) is identified.

**Recommendation:** Proceed to 014 — Governance & Constitutional Compliance Engine.