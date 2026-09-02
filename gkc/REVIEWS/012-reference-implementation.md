# GKC-012 — Engineering Review

> Adversarial review of `DESIGN/012-reference-implementation.md`.

## Review Stance

The reviewer is a senior engineering lead who has shipped compilers and watched reference implementations drift from their designs. They assume: packages will have wrong dependencies, milestones will slip silently, risks will materialize unmitigated, and migration will be an afterthought.

## 1. Language Selection (§ 2)

- [ ] Selection criteria are explicit and ordered.
- [ ] Candidate languages are listed with honest assessments.
- [ ] The ADR (`DECISIONS/0010-implementation-language.md`) is referenced and is a blocker for M0.
- [ ] No language is silently privileged.

## 2. Package Structure (§ 3)

- [ ] Packages match components in `DESIGN/003`.
- [ ] Dependency rules (§ 3.1) match `DESIGN/003` § 4.1.
- [ ] Public surface is restricted to `cli/` (per `DESIGN/009`).
- [ ] No circular package dependencies.

## 3. Repository Structure (§ 4)

- [ ] Layout is complete.
- [ ] Self-compilation is specified (good dogfooding signal).
- [ ] Branching strategy is defined.
- [ ] Tagging convention is defined.

## 4. Per-Milestone Deliverables (§ 5)

For each milestone (M0–M5):

- [ ] Deliverables are listed with package locations.
- [ ] Each deliverable maps to a DESIGN doc.
- [ ] Status column is present (for tracking).
- [ ] Done-conditions are cross-referenced with `ROADMAP.md`.

## 5. Implementation Tracking (§ 6)

- [ ] `IMPLEMENTATION/` directory is defined.
- [ ] Per-milestone status template is provided.
- [ | Invariant codification tracker is referenced.
- [ ] Golden tasks tracker is referenced.

## 6. Risks (§ 7)

- [ ] Engineering risks are listed with likelihood, impact, mitigation.
- [ ] Organizational risks are listed.
- [ ] External risks are listed.
- [ ] The highest-impact risks have concrete mitigations (not "we'll figure it out").
- [ ] The "incremental != full rebuild" risk is explicitly addressed (it's the most dangerous).

## 7. Migration (§ 8)

- [ ] Workspace migration (minor and major) is defined.
- [ ] Plugin migration is defined.
- [ ] User migration (from GENESIS-only to GKC) is defined.
- [ ] Major-version migration tool is planned.

## 8. Future Evolution (§ 9)

- [ ] Post-M5 horizons match `DESIGN/001` § 10.
- [ ] Each horizon is additive (no restructuring).
- [ ] Triggers for each horizon are stated (not just "when we feel like it").
- [ ] Versioning policy is explicit (0.x, 1.0, 1.x, 2.0).

## 9. Release Process (§ 10)

- [ ] Milestone, patch, minor, and major releases are defined.
- [ ] Release notes are required.
- [ | Golden snapshot re-recording is part of the process.
- [ ] Tags follow a convention.

## 10. Cross-Document Consistency

- [ ] Milestones match `ROADMAP.md`.
- [ ] Done-conditions match `ROADMAP.md`.
- [ ] Package structure matches `DESIGN/003` components.
- [ ] CI configurations match `DESIGN/011` § 12.

## 11. Open Questions

- [ ] All five open questions are ADR candidates in `DECISIONS/012-reference-implementation-adr-candidates.md`.
- [ ] ADR-0010 (implementation language) is marked as a blocker for M0.

## 12. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms (until the language ADR is ratified).
- [ ] Reasonable length (target: under 1500 lines).

## 13. Exit Criteria

The document passes iff every checkbox is checked or addressed by an ADR candidate.

Reviewer sign-off: ____________________ Date: __________