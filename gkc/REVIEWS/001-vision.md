# GKC-001 — Engineering Review

> Adversarial review checklist for `DESIGN/001-vision.md`. The document must pass every item before M0 implementation begins.

## Review Stance

The reviewer is a skeptical compiler engineer who assumes the vision is over-claimed until proven otherwise. The reviewer's job is to find places where the vision makes commitments the rest of the design cannot cash.

## 1. Coherence with GENESIS

- [ ] Does the document claim GKC enforces GENESIS invariants? If yes, cite at least three invariants from `000`–`018` that GKC will codify, and confirm they are machine-checkable.
- [ ] Does the document define what "conflict with GENESIS" means operationally? If not, file an ADR candidate.
- [ ] Does the document respect the frozen status of GENESIS? It must not propose amendments.

## 2. Invariant Testability

For each invariant in § 7, the reviewer checks:

- [ ] **7.1 Determinism** — Is there a defined normalization step for non-deterministic inputs (timestamps, walk order, parallel scheduling)? If not, the invariant is untestable.
- [ ] **7.2 Staging** — Is the DAG structure of the pipeline specified somewhere testable? Cross-check with `DESIGN/005`.
- [ ] **7.3 Incrementality** — Is "affected subgraph" defined? Cross-check with `DESIGN/005`.
- [ ] **7.4 Cacheability** — Is the cache key function total and pure? Cross-check with the implementation in M0.
- [ ] **7.5 Diagnostic** — Is the diagnostic schema specified? Cross-check with `DESIGN/005`.
- [ ] **7.6 Plugin isolation** — Is "plugin failure" defined (exception? timeout? bad output?)? Cross-check with `DESIGN/008`.
- [ ] **7.7 GENESIS primacy** — Is the conflict-detection mechanism defined, even as a stub? Cross-check with M4 plans.
- [ ] **7.8 Local-first** — Does the document define what counts as "network access" (DNS? loopback? local IPC?)? If not, file an ADR candidate.

## 3. Success Criteria Measurability

For each criterion in § 6, the reviewer checks:

- [ ] S1 Determinism — measurable? what's the tolerance (byte-identical? hash-identical?)?
- [ ] S2 Incrementality — is "k bounded by affected subgraph" formal enough to test? Cross-check `DESIGN/005`.
- [ ] S3 Diagnostic completeness — is "ranked" defined (total order? partial order?)? Cross-check `DESIGN/005`.
- [ ] S4 Context sufficiency — is the "reference agent" defined? Cross-check `DESIGN/007` and `DESIGN/011`.
- [ ] S5 Query latency — is "warm cache" defined? Cross-check `DESIGN/010`.
- [ ] S6 Plugin isolation — is the test scenario defined? Cross-check `DESIGN/008` and `DESIGN/011`.
- [ ] S7 AIOS boot — is the AIOS contract defined? Cross-check with AIOS specs.
- [ ] S8 Compile throughput — is the hardware reference defined? If not, file an ADR candidate.

## 4. Definition Risks

- [ ] § 3 "Understanding" — Are the four closures independently testable? If any closure depends on another, the definition is not operational.
- [ ] § 3.2 Authority — "Acyclic within a stratum, stratified across strata" — is this formally defined? Cross-check `DESIGN/005` and `DECISIONS/0003-authority-graph-stratification.md`.
- [ ] § 3.4 Ontology — "Every reference to a domain concept resolves to an ontology node" — what about forward references? Unresolved references at the closure boundary?

## 5. Philosophy Risks

- [ ] § 8.3 "Authority wins" — what happens when two artifacts have equal authority and one must be dropped? File an ADR candidate if not resolved.
- [ ] § 8.4 "Diagnostics over silence" — does this conflict with the cacheability invariant (7.4)? A cache hit does not re-emit diagnostics; is that "silence"?
- [ ] § 8.6 "Local LLM parity" — is this a hard constraint or a target? If hard, the context compiler must produce multiple formats from one substrate; cross-check `DESIGN/007`.

## 6. Non-Goal Boundary

- [ ] § 9 lists six engineering non-goals. For each, confirm no other DESIGN doc relies on GKC performing that non-goal.
- [ ] Cross-check `DESIGN/007` — does the context compiler accidentally start "generating"? If so, it violates non-goal "GKC does not generate".
- [ ] Cross-check `DESIGN/008` — do plugins accidentally start "scheduling"? If so, they violate non-goal "GKC does not schedule".

## 7. Evolution Coherence

- [ ] § 10 — For each horizon, confirm the claim "additive, not restructure" holds against the current pipeline design. Cross-check `DESIGN/005`.
- [ ] Are there any horizons that *would* require restructuring? If yes, surface as an ADR candidate.

## 8. Open Questions

- [ ] Are all five open questions in § 11 reflected as ADR candidates in `DECISIONS/0001-vision-adr-candidates.md`?
- [ ] Are any of them blocking M0? If yes, escalate.

## 9. Document Quality

- [ ] Every section has a clear purpose; no section is filler.
- [ ] Cross-references to other DESIGN docs are correct.
- [ ] No implementation code, no API surface, no language-specific idioms.
- [ ] Length is reasonable for a vision document (target: under 1500 lines).

## 10. Exit Criteria

The document passes review iff every checkbox above is either checked or has a filed ADR candidate addressing the gap. Open ADR candidates do not block the review; unaddressed gaps do.

Reviewer sign-off: ____________________ Date: __________