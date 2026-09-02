# GKC-003 — Engineering Prompt

## Objective

Implement the **component interfaces and boundaries** for every component in `DESIGN/003-component-architecture.md`. This is the contract layer: typed interfaces, in/out records, failure-mode stubs, and boundary tests. No business logic.

## Inputs

- `DESIGN/003-component-architecture.md` (authoritative)
- `DESIGN/002-domain-model.md` (for types)
- `DECISIONS/003-component-architecture-adr-candidates.md`

## Scope

For each of the 15 components (C1–C15):

1. **Interface module** declaring:
   - The `Request` and `Result` types from the doc.
   - The component's primary entry function.
   - Extension point slots (named, typed hooks the plugin framework will fill).
2. **Boundary stub** that:
   - Accepts the request.
   - Returns a typed empty / no-op result.
   - Emits a `component-not-implemented` info diagnostic.
3. **Failure-mode tests** that verify:
   - Plugin failure is caught at the component boundary.
   - The affected artifact is marked; other artifacts proceed.
   - Storage failure does not corrupt the snapshot.
   - Invalid input is rejected with a typed error, not a panic.
4. **Static dependency assertions** that verify the import graph matches § 4.1 of the doc (no component imports a forbidden dependency).

## Out of Scope

- Real classification, parsing, resolution, graph building, validation, indexing, context compilation, query answering.
- Storage backend implementation (use in-memory stub).
- Plugin loading mechanism (use hard-coded stubs).
- CLI command parsing (covered in `DESIGN/009`).

## Done Conditions

- All 15 components have interface modules with the documented Request/Result types.
- All 15 components have boundary stubs that pass a "smoke compile" of `gold/empty`.
- Failure-mode tests pass for: plugin failure, storage failure, invalid input.
- Static dependency assertions pass: no component imports a forbidden dependency.
- Every extension point slot is named and typed; plugins can be registered against them (in stub form).

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- No public API beyond the interfaces; internals are not exposed.
- Stubs must be deterministic (same input ⇒ same output, including same diagnostics).
- All failure paths emit typed errors, not exceptions/panics, at the component boundary.

## Deliverables

- `components/scanner`, `components/parser`, `components/normalizer`, `components/resolver`, `components/registry`, `components/authority-builder`, `components/dependency-builder`, `components/ontology-compiler`, `components/validator`, `components/indexer`, `components/context-compiler`, `components/query-engine`, `components/storage`, `components/plugin-framework`, `components/cli`
- `components/extension-points` — shared extension point registry
- `components/tests/boundaries` — boundary failure-mode tests
- `components/tests/dependencies` — static dependency assertion tests

## Verification

1. `gkc test components` — all interface and boundary tests pass.
2. `gkc compile gold/empty` — succeeds using only stubs; produces an empty snapshot.
3. `gkc test dependencies` — static dependency assertions pass.
4. `gkc test failure-modes` — all four failure-mode categories pass.

Report pass/fail per step. Any failure blocks M1.