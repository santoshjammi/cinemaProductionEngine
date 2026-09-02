# GKC-002 — Engineering Prompt

## Objective

Implement the **domain model layer**: the typed values for every object in `DESIGN/002-domain-model.md`, with their invariants enforced at construction time. No pipeline stages, no storage, no CLI — only the domain types and their constructors.

## Inputs

- `DESIGN/002-domain-model.md` (authoritative)
- `DECISIONS/0001-vision-adr-candidates.md` (for invariants)
- `DECISIONS/002-domain-model-adr-candidates.md` (for open questions; resolve blockers before starting)

## Scope

Implement, for each of the 20 domain objects in § 3:

1. **Type definition** — fields, types, identity function.
2. **Constructor** — validates invariants; refuses to construct invalid instances.
3. **Equality** — based on identity fields only (per the document).
4. **Lifecycle state machine** — states as an enum; transitions as a function that validates legality.
5. **Immutability** — for objects marked immutable (Registry Entry, Snapshot, Diagnostic, etc.): no setters; "mutations" return new instances.

Additionally:

6. **Ownership annotations** — each type carries metadata indicating which component creates/mutates/destroys it (for runtime assertion in debug builds).
7. **Diagnostic type** — full schema with severity enum, invariant reference, evidence, resolution, provenance.
8. **Content-addressed identity** — implement a deterministic hashing function for objects whose identity is content-addressed (Repository, Artifact, Registry Entry, Snapshot, Task Descriptor).

## Out of Scope

- Storage persistence (use in-memory).
- Pipeline integration.
- Any I/O.
- Concrete parsers, scanners, graph builders.

## Done Conditions

- All 20 domain objects from `DESIGN/002` § 3 are implemented.
- Every invariant in `DESIGN/002` is enforced by a constructor or transition function.
- Every content-addressed identity is deterministic: same inputs ⇒ same hash, verified by a property test.
- Every immutable object has no mutating setters.
- A test suite covers: construction (valid/invalid), equality, lifecycle transitions (legal/illegal), and identity determinism.
- The diagnostic type round-trips through serialization (to bytes and back) losslessly.

## Constraints

- Implementation language: per `DECISIONS/0010-implementation-language.md`.
- No external dependencies for hashing — use a stdlib hash (SHA-256 or equivalent).
- No reflection; all fields are explicit.
- No public API surface beyond internal constructors.

## Deliverables

- `domain/repository`, `domain/artifact`, `domain/document`, `domain/reference`, `domain/metadata`, `domain/authority`, `domain/dependency`, `domain/registry-entry`, `domain/knowledge-graph`, `domain/ontology-node`, `domain/context-package`, `domain/validation-report`, `domain/compilation-unit`, `domain/plugin`, `domain/workspace`, `domain/repository-snapshot`, `domain/build-session`, `domain/task-descriptor`, `domain/token-budget`, `domain/diagnostic`
- `domain/identity` — content-addressed hashing utilities
- `domain/lifecycle` — shared state-machine helpers
- `domain/tests/*` — one test file per domain object

## Verification

1. `gkc test domain` — all domain tests pass.
2. Property test: for any constructed object, reconstructing from its identity fields yields an equal object.
3. Property test: for any immutable object, attempting a mutation either returns a new instance or is rejected at compile time (depending on language).
4. Property test: for any content-addressed object, hashing twice yields the same hash.
5. Negative test: every documented invariant violation is rejected by the constructor.

Report pass/fail per step. Any failure blocks M1 entry.