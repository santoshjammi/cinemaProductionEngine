# GKC-011 — Engineering Review

> Adversarial review of `DESIGN/011-testing.md`.

## Review Stance

The reviewer is a test engineer who has shipped testing strategies and watched coverage numbers lie. They assume: unit tests don't cover integration, golden snapshots drift from reality, performance targets are unmeasured, and the sufficiency test is a smoke test until proven otherwise.

## 1. Test Layer Coverage

- [ ] All 8 layers in § 2 are specified with scope, count target, and runtime target.
- [ ] Every invariant in `DESIGN/001` § 7 has a test in § 9.
- [ ] Every success criterion in `DESIGN/001` § 6 has a test in § 8 or § 10.
- [ ] Every contract in `DESIGN/003` has an integration test (§ 4).

## 2. Unit Tests (§ 3)

- [ ] Scope is enumerated.
- [ ] Property tests are listed (determinism, round-trip, identity, inverse).
- [ ] Negative tests are required (invariant violations, invalid input).

## 3. Integration Tests (§ 4)

- [ ] Stage-to-stage, component-to-component, plugin, storage, CLI routing are covered.
- [ ] Boundary tests (failure isolation) are explicit.

## 4. Repository Tests (§ 5)

- [ ] Test repos are enumerated with sizes and purposes.
- [ ] Assertions are explicit (snapshot sealed, registry count, graph cycles, validation).

## 5. Golden Repositories (§ 6)

- [ ] 10 golden repos are listed.
- [ ] Recording mechanism is defined.
- [ ] Update process requires ADR justification.
- [ ] Byte-stable comparison is the test.

## 6. Regression Tests (§ 7)

- [ ] Every bug fix gets a regression test.
- [ ] Tests are organized by bug id.
- [ ] CI never skips regression tests.

## 7. Performance Tests (§ 8)

- [ ] All 4 targets from `DESIGN/001` § 6 are covered.
- [ ] Benchmark methodology is defined (reference machine, warm cache, runs, p95).
- [ ] Regression detection threshold is defined (10%).
- [ ] Trends are tracked.

## 8. Compiler Correctness (§ 9)

- [ ] All 7 invariants from `DESIGN/001` § 7 have tests.
- [ ] Determinism tests cover parallelism and cross-machine variants.
- [ ] Incrementality tests cover single-artifact and no-op changes.
- [ ] Staging tests cover DAG acyclicity and no-forward-reads.
- [ ] Plugin isolation tests cover failure and capability violation.
- [ ] GENESIS primacy tests verify non-silent override.
- [ ] Local-first tests cover network-disabled scenarios.

## 9. Context Correctness (§ 10)

- [ ] Sufficiency is tested with all three reference agents (per ADR-Candidate-0010).
- [ ] LLM independence tests cover all 4 built-in providers.
- [ ] Closure property test is on 100 random pairs.
- [ ] Budget compliance property test is on 100 random pairs.
- [ ] Authority preference is tested with a synthetic IR.

## 10. Test Harness (§ 11)

- [ ] All 9 `gkc test` subcommands are defined.
- [ ] Output formats (text/JSON) are supported.
- [ ] Parallelism rules are explicit.
- [ ] Exit codes are defined.

## 11. CI Integration (§ 12)

- [ ] Per-commit, per-PR, nightly, release configurations are defined.
- [ ] Runtime targets are realistic.
- [ ] Performance tests target relevant PRs.

## 12. Fixtures Management (§ 13)

- [ ] Golden repos are self-contained.
- [ ] Golden tasks are versioned.
- [ ] Reference agents are stubbed for per-commit CI; LLMs for nightly.

## 13. Coverage (§ 14)

- [ ] Line coverage targets are defined.
- [ ] Invariant coverage is mapped.
- [ ] Mutation testing is planned (quarterly).

## 14. Cross-Document Consistency

- [ ] Performance targets match `DESIGN/001` § 6.
- [ | Invariants match `DESIGN/001` § 7.
- [ ] Sufficiency methodology matches `DESIGN/007` § 13.
- [ ] Reference agents match ADR-Candidate-0010.

## 15. Open Questions

- [ ] All five open questions are ADR candidates in `DECISIONS/011-testing-adr-candidates.md`.
- [ ] None block M0.

## 16. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms.
- [ ] Reasonable length (target: under 1500 lines).

## 17. Exit Criteria

The document passes iff every checkbox is checked or addressed by an ADR candidate.

Reviewer sign-off: ____________________ Date: __________