# GKC-007 — Engineering Review

> Adversarial review of `DESIGN/007-context-compiler.md`. This is the flagship document; the review is correspondingly strict.

## Review Stance

The reviewer is an LLM-context engineer who has shipped context systems and watched them fail in production. They assume: rankings are biased toward the wrong things, closures are incomplete, budgets are mis-allocated, providers leak format, and the sufficiency test is a fig leaf until proven otherwise.

## 1. Problem Framing

- [ ] § 2 names the three failure modes (insufficiency, bloat, drift). Each is addressed in the design.
- [ ] Insufficiency is addressed by the closure invariant (§ 6.1).
- [ ] Bloat is addressed by semantic filtering (§ 5) and budget allocation (§ 8).
- [ ] Drift is addressed by authority expansion (§ 7) and conflict detection (§ 7.3).

## 2. Pipeline Completeness

- [ ] All 7 stages in § 3 are present with detailed contracts in §§ 4–10.
- [ ] Stages 1–4 are pure functions (no side effects; no I/O).
- [ ] The whole pipeline is deterministic for a fixed `(task, snapshot, budget, provider)`.
- [ ] Stage ordering is unambiguous.

## 3. Slice Selection (§ 4)

- [ ] All six slice kinds are documented.
- [ ] Candidate set construction is over-inclusive by design (§ 4.2).
- [ ] Slice identity is defined; duplicate slices merge.
- [ ] The candidate set is finite and bounded.

## 4. Semantic Filtering (§ 5)

- [ ] Relevance score is in `[0, 1]` for every slice kind.
- [ ] Authority weight is applied consistently (§ 5.2).
- [ ] Threshold is configurable.
- [ ] The scoring algorithm is deterministic.
- [ ] Does the scoring use the search index from `DESIGN/004` § 6.1? Cross-check.

## 5. Dependency Expansion (§ 6)

- [ ] The closure invariant (§ 6.1) is formally stated and testable.
- [ ] Closure computation uses the dependency closure index.
- [ ] Depth limits are configurable (per ADR-Candidate-0027).
- [ | Truncation is reported (`closure-truncated`), not silent.
- [ ] Truncation metadata records which artifacts' closures were truncated.
- [ ] Soft dependencies are not expanded by default; opt-in only.

## 6. Authority Expansion (§ 7)

- [ ] The authority-preference invariant (§ 7.1) is testable.
- [ ] Conflict detection uses the ontology compiler's conflict data.
- [ ] Conflicts are reported (`context-conflict`), not silent.
- [ ] Lower-authority artifacts are dropped unless explicitly referenced.

## 7. Budget Allocation (§ 8)

- [ ] The allocation invariant (§ 8.1) is testable.
- [ ] Tiered allocation (§ 8.2) is fully specified.
- [ ] Overflow policy is configurable; default is `drop-lowest-authority`.
- [ ] Token accounting uses a fast approximation (per § 8.4).
- [ ] Budget-too-small case is handled (§ 8.5).

## 8. Rendering and Providers (§ 9)

- [ ] All four built-in providers are documented.
- [ ] Provider selection from model profile is defined.
- [ ] Provider failure falls back to `markdown` with a marker.
- [ ] Plugin providers are supported (cross-check `DESIGN/008`).
- [ ] No provider leaks its format into the IR or cache key (except `provider_id` in the cache key, which is correct).

## 9. Package Assembly (§ 10)

- [ ] Slice ordering is total and deterministic.
- [ ] Package metadata is complete (§ 10.2).
- [ ] Dropped slices are recorded with reasons.
- [ ] Closure truncations are recorded.
- [ ] Conflicts are recorded.

## 10. Caching and Incremental (§ 11)

- [ ] Cache key is the identity tuple.
- [ ] Cache hit returns byte-identical package.
- [ ] Invalidation rules are complete.
- [ ] Incremental re-build is per-slice, not all-or-nothing.
- [ ] Warm-cache latency target (100 ms) is testable.

## 11. LLM Independence (§ 12)

- [ ] The LLM-independence invariant is stated and testable.
- [ ] The `local-llm` provider is specified for limited-context models.
- [ ] Semantic equivalence across providers is testable (§ 12.3).

## 12. Sufficiency Test (§ 13)

- [ ] The sufficiency invariant is stated.
- [ ] Test methodology is reproducible.
- [ ] The golden task set is referenced and maintained.
- [ ] The test covers the three reference agents (per ADR-Candidate-0010).
- [ ] Sufficiency is scoped to the package, not the agent (§ 13.4) — GKC's contract is clearly bounded.

## 13. Failure Modes (§ 14)

- [ ] All seven failures are typed errors or diagnostics.
- [ ] No failure is silent.
- [ ] Provider failure is isolated (does not crash the compiler).
- [ ] Closure truncation is info, not error (correct: the package is still useful).

## 14. Extension (§ 15)

- [ ] All five extension points are listed.
- [ ] None allow plugins to mutate the IR.
- [ ] Plugin providers go through the same dispatch path as built-ins.

## 15. Cross-Document Consistency

- [ ] Slice kinds match `DESIGN/002` § 3.11.1.
- [ ] Token Budget matches `DESIGN/002` § 3.19.
- [ ] Task Descriptor matches `DESIGN/002` § 3.18.
- [ ] Context Package identity matches `DESIGN/002` § 3.11.
- [ ] Cache layer matches `DESIGN/005` § 4.
- [ ] Component boundaries match `DESIGN/003` § C11.

## 16. Open Questions

- [ ] All five open questions are ADR candidates in `DECISIONS/007-context-compiler-adr-candidates.md`.
- [ ] None block M3.

## 17. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms.
- [ ] Reasonable length (target: under 2000 lines for a flagship doc).

## 18. Exit Criteria

The document passes iff every checkbox is checked or addressed by an ADR candidate. Given this is the flagship, reviewers should be especially strict about § 5 (filtering), § 6 (closure), § 7 (authority), and § 13 (sufficiency).

Reviewer sign-off: ____________________ Date: __________