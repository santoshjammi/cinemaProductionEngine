# GKC-008 — Engineering Review

> Adversarial review of `DESIGN/008-plugin-framework.md`.

## Review Stance

The reviewer is a security-minded platform engineer who assumes plugins will misbehave, that capability checks have holes, and that "load-time check only" is not enough.

## 1. Plugin Package Format (§ 2)

- [ ] Manifest schema is fully specified.
- [ ] Required vs. optional fields are marked.
- [ ] Integrity hash computation is reproducible (canonical serialization, sorted order).
- [ ] Integrity verification is always enforced (no skip).

## 2. Lifecycle (§ 3)

- [ ] All six states are explicit.
- [ ] Transitions are legal (no jumps from `unloaded` to `active`).
- [ ] Load failures are enumerated with diagnostics.
- [ ] Runtime failures are enumerated with recovery behavior.

## 3. Extension Point Contracts (§ 4)

For each of the 12 extension points:

- [ ] Contract is typed (inputs and outputs).
- [ ] Registration fields are specified.
- [ ] Determinism requirement is stated.
- [ ] Conflict behavior is defined.
- [ ] Override behavior is defined (where applicable).

## 4. Capabilities (§ 5)

- [ ] Capability enum is closed (no free-form strings).
- [ ] Policy model (allow/deny/require_explicit) is fully specified.
- [ ] Runtime enforcement level (A/B/C/D) is staged and matches ADR-Candidate-0020.
- [ ] Capability violation at runtime is detected and terminated.

## 5. Sandboxing (§ 6)

- [ ] Load-time sandboxing is always on (integrity + capability + version + conflict).
- [ ] Runtime sandboxing (level B) is specified for M4+.
- [ ] Future horizons (process / WASM) are noted without overdesigning.
- [ ] Bypass detection is acknowledged as best-effort at M4.

## 6. Plugin Registry (§ 7)

- [ ] Per-workspace isolation (per ADR-Candidate-0015).
- [ ] Registry contents are enumerated.
- [ ] Registry queries are listed.
- [ ] Registry persists across sessions.

## 7. Failure Isolation (§ 8)

- [ ] Per-artifact recovery is specified for all dispatching stages.
- [ ] Per-package recovery (context provider fallback) is specified.
- [ ] Per-invariant recovery (validator) is specified.
- [ ] Load-time failures are fatal for the plugin only; other plugins continue.

## 8. Built-in Plugins (§ 9)

- [ ] Built-ins go through the same dispatch path.
- [ ] Override mechanism is documented.
- [ ] No special-case code for built-ins in core.

## 9. Discovery (§ 10)

- [ ] Discovery path is explicit.
- [ ] Discovery order is deterministic.
- [ ] Priority field for order-sensitive extension points is defined.
- [ ] Conflicts are detected and rejected.

## 10. Development Workflow (§ 11)

- [ ] Authoring, distributing, installing, uninstalling are documented.
- [ ] `gkc plugin hash` is provided for integrity computation.
- [ ] No central registry in M0–M5 (deferred).

## 11. Observability (§ 12)

- [ ] Per-plugin metrics are emitted.
- [ ] `gkc doctor` and `gkc stats` surface them.

## 12. Cross-Document Consistency

- [ ] Extension points match `DESIGN/003` § 6.
- [ ] Failure policies match `DESIGN/005` § 5.
- [ ] Plugin domain object matches `DESIGN/002` § 3.14.
- [ ] CLI subcommands match `DESIGN/009`.

## 13. Open Questions

- [ ] All five open questions are ADR candidates in `DECISIONS/008-plugin-framework-adr-candidates.md`.
- [ ] None block M0 (level A sandboxing is sufficient).

## 14. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms.
- [ ] Reasonable length (target: under 1500 lines).

## 15. Exit Criteria

The document passes iff every checkbox is checked or addressed by an ADR candidate.

Reviewer sign-off: ____________________ Date: __________