# GKC-006 — Engineering Review

> Adversarial review of `DESIGN/006-query-engine.md`.

## Review Stance

The reviewer is a search/info-retrieval engineer who assumes rankings are biased, provenance is incomplete, and performance targets are unmeasured until proven.

## 1. Query Catalog Completeness

- [ ] Every CLI subcommand in `DESIGN/009` maps to a query kind in § 2.
- [ ] No query kind is missing a contract in § 3.
- [ ] Plugin-extensible query kinds are explicitly noted.

## 2. Contract Completeness

For each Q1–Q12:

- [ ] Params are enumerated with types.
- [ ] Output structure is defined.
- [ ] Ranking policy is specified.
- [ ] Provenance is specified.
- [ ] Index dependencies are named.
- [ ] Performance target is stated.

## 3. Ranking Determinism

- [ ] Default ranking is specified for every query kind.
- [ ] Override policy is defined (§ 4.2).
- [ ] Tie-break is total (§ 4.3).
- [ ] Authority weighting is defined and applied consistently (§ 4.4).
- [ ] Invalid ranking-policy combinations are rejected.

## 4. Provenance Completeness

- [ ] Every result has a provenance set.
- [ ] The re-derivation property (§ 5.3) is testable.
- [ ] Provenance distinguishes declared vs. inferred edges.
- [ ] Provenance names the source artifact for each edge.

## 5. Performance Targets

- [ ] Each target is measurable.
- [ ] The reference hardware is defined (per ADR-Candidate-0008) or normalized.
- [ ] "Warm cache" is defined (per ADR-Candidate-0007).
- [ ] Targets cover all 12 query kinds.

## 6. Caching

- [ ] Cache key includes `query_hash` and `snapshot_id`.
- [ ] Cache invalidation rules are complete.
- [ ] Cache hit returns byte-identical result.
- [ ] Cache does not persist across GKC version changes.

## 7. Failure Modes

- [ ] All eight failure modes in § 8 are typed errors.
- [ ] No failure mode is silent.
- [ ] Index-unavailable fallback (`--allow-scan`) is opt-in, not default.
- [ ] Plugin query kind failure is isolated (does not crash the engine).

## 8. Extension

- [ ] Plugin query kinds go through the same dispatch path as built-ins.
- [ ] Required indexes are declared and enforced.
- [ ] Kind conflicts are rejected.
- [ ] Namespacing is required.

## 9. Output Formats

- [ ] All four formats (text, JSON, JSONL, DOT) are supported where applicable.
- [ ] Text output is stable for scripting.
- [ ] JSON output is self-describing.
- [ ] DOT output is Graphviz-valid.

## 10. Cross-Document Consistency

- [ ] Index names match `DESIGN/004` § 6.
- [ ] Snapshot lifecycle matches `DESIGN/002` and `DESIGN/004`.
- [ ] Component boundaries match `DESIGN/003` § C12.
- [ ] CLI subcommands match `DESIGN/009`.

## 11. Open Questions

- [ ] All five open questions are ADR candidates in `DECISIONS/006-query-engine-adr-candidates.md`.
- [ ] None block M2.

## 12. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms.
- [ ] Reasonable length (target: under 1500 lines).

## 13. Exit Criteria

The document passes iff every checkbox is checked or addressed by an ADR candidate.

Reviewer sign-off: ____________________ Date: __________