# GKC-005 — Engineering Review

> Adversarial review of `DESIGN/005-pipeline.md`.

## Review Stance

The reviewer is a compiler engineer who has shipped incremental pipelines and been burned by them. They assume incremental compilation is wrong until proven correct, that parallelism breaks determinism unless proven otherwise, and that failure policies have holes.

## 1. Pipeline DAG

- [ ] All 11 stages are listed with their dependencies.
- [ ] The DAG is acyclic (verify by topological sort).
- [ ] Stages 6, 7, 8 are correctly independent (all depend only on 5).
- [ ] Stage 9 correctly depends on 5, 6, 7, 8 (not just 5).
- [ ] Stage 10 correctly depends on 5, 6, 7, 8.
- [ ] Stage 11 is correctly lazy (depends on 10 but runs on demand).

## 2. Stage Contracts

For each stage (§§ 2.4–2.12):

- [ ] Input and output types are named.
- [ ] Determinism rules specify what is normalized and how.
- [ ] Failure policy is per-artifact or per-stage explicitly.
- [ ] Side effects are explicitly listed (filesystem read, write, none).

## 3. Incremental Compilation Correctness

- [ ] The invariant "incremental == full rebuild" is stated and testable.
- [ ] § 3.3 lists each stage's incremental trigger explicitly.
- [ ] § 3.4 defines affected-subgraph computation unambiguously.
- [ ] § 3.5 explains how graph re-build is correct (sorted emission).
- [ ] Edge cases: what if a removed artifact was a graph hub? Is the affected subgraph still correct?

## 4. Caching

- [ ] Three cache layers are distinguished (stage, snapshot, context).
- [ ] Cache keys are content-addressed (no time, no machine-specific data).
- [ ] Cache hit semantics: byte-identical output.
- [ ] Cache miss semantics: full execution, write on success only.
- [ ] Eviction policy is defined (LRU + reference counting + explicit prune).
- [ ] Cache integrity check on load (hash mismatch → miss).

## 5. Failure Policies

- [ ] Stage failure is per-artifact (not per-compile).
- [ ] Plugin failure is per-artifact with `plugin-failed` marker.
- [ ] Hard invariant failure (constitutional violation) does not block by default; CLI exit code reflects it.
- [ ] Storage failure is fatal to the session; prior snapshot unaffected.
- [ ] Every failure path emits a diagnostic.

## 6. Parallelism and Determinism

- [ ] § 6 lists which stages are parallel.
- [ ] § 6.6 specifies the sort key for merging parallel outputs.
- [ ] The sort key is total (no ties).
- [ ] Determinism under parallelism is testable (the M1 verification step covers this).

## 7. Partial Compilation

- [ ] Downward-closed subsets are enforced.
- [ ] Partial snapshots are not sealable.
- [ ] The `unbuilt` marker mechanism is defined.
- [ ] Use cases in § 7.2 map to real CLI subcommands (cross-check `DESIGN/009`).

## 8. Diagnostics

- [ ] Severity ordering is total (per `DESIGN/002` § 3.12).
- [ ] Ranking is deterministic (the total order is stable).
- [ ] Diagnostic ids are content-addressed (per ADR-Candidate-0016).
- [ ] Diagnostics are immutable once emitted.
- [ ] The validation report is the canonical ranked set.

## 9. Build Session Lifecycle

- [ ] § 9 lists the lifecycle steps.
- [ ] Single-threaded commit is enforced.
- [ ] Multiple sessions can compile in parallel into different snapshot branches.
- [ ] Workspace lock behavior is defined.

## 10. Observability

- [ ] Metrics are emitted per stage.
- [ ] Metrics do not affect determinism (excluded from snapshots).
- [ ] `gkc doctor` and `gkc stats` aggregate metrics.

## 11. Cross-Document Consistency

- [ ] Stage numbers match `ARCHITECTURE.md` and `DESIGN/003`.
- [ ] Cache keys match the determinism invariant in `DESIGN/001` § 7.4.
- [ ] Diagnostic types match `DESIGN/002` § 3.20.
- [ ] Snapshot structure matches `DESIGN/004` § 5.

## 12. Open Questions

- [ ] All five open questions in § 11 are ADR candidates in `DECISIONS/005-pipeline-adr-candidates.md`.
- [ ] None block M0; if any do, escalate.

## 13. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms.
- [ ] Reasonable length (target: under 1500 lines).

## 14. Exit Criteria

The document passes iff every checkbox is checked or addressed by an ADR candidate.

Reviewer sign-off: ____________________ Date: __________