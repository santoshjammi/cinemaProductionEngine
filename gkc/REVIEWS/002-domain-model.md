# GKC-002 — Engineering Review

> Adversarial review of `DESIGN/002-domain-model.md`. The domain model is the vocabulary of the compiler; ambiguity here propagates everywhere.

## Review Stance

The reviewer is a type-system-pedantic domain modeler. They assume every term is overloaded until proven otherwise, and that every "lifecycle" is a state machine that can be violated.

## 1. Identity and Equality

For each of the 20 domain objects:

- [ ] Identity fields are explicitly named and minimal.
- [ ] Two instances with identical identity fields are equal — no hidden discriminators.
- [ ] Identity fields are **immutable** (you cannot change an object's identity in place).
- [ ] No object uses object identity (pointer/reference) as its identity.
- [ ] Content-addressed identities specify the hash function and the canonical serialization that feeds it.

## 2. Field Completeness

For each object:

- [ ] Every field named in `DESIGN/002` has a clear type description (or is explicitly deferred to `DESIGN/004`).
- [ ] Optional vs. required fields are marked.
- [ ] No field silently defaults to a magic value (e.g., `null` ≠ `unknown`).
- [ ] `provenance` fields exist wherever the object is derived from another (parser provenance, classifier provenance, inference provenance).

## 3. Lifecycle Legality

For each lifecycle state machine:

- [ ] States are an explicit finite enum.
- [ ] Transitions are a function, not a free mutation (i.e., you cannot go from `sealed` back to `building`).
- [ ] Terminal states are marked (`completed`, `failed`, `ended`, `aborted`, `gc-eligible`, etc.).
- [ ] Every state is reachable from an initial state through legal transitions.
- [ ] No object has a "limbo" state with no transitions out.

## 4. Ownership Boundaries

- [ ] Every object has exactly one **creator** (component or stage).
- [ ] No object is mutated by a component that does not own it.
- [ ] Cross-references to owning stages match the stage names in `DESIGN/005` and `ARCHITECTURE.md`.
- [ ] "Follows X lifecycle" relationships are explicit and not circular.

## 5. Invariant Enforceability

For every invariant in `DESIGN/002`:

- [ ] The invariant is expressible as a runtime or compile-time check.
- [ ] The invariant has a defined violation diagnostic (cross-reference to `DESIGN/005` validation).
- [ ] No invariant depends on global state (e.g., "current time").
- [ ] No invariant depends on a future stage's output (staging invariant from `DESIGN/001` § 7.2).

## 6. Relationship Integrity

- [ ] Every relationship is typed (source type, target type, edge type).
- [ ] No bidirectional relationship is modeled as two unidirectional ones without a sync invariant.
- [ ] Cycles in relationships are acknowledged (e.g., A references B, B references A) and either allowed or rejected explicitly.
- [ ] "Zero or more" vs. "one or more" is explicit for every relationship.

## 7. Specific Object Concerns

### 7.1 Artifact Kind (§ 3.2.1)

- [ ] The kind taxonomy is open (plugin-extensible) but the closure is total — every artifact has a kind.
- [ ] The `unknown` kind has a defined behavior downstream (parser, registry, validation).
- [ ] Cross-check with `DECISIONS/0002-artifact-kind-taxonomy.md` (if it exists) or file an ADR candidate.

### 7.2 Authority (§ 3.6)

- [ ] The stratification is total: every artifact's authority is one of the listed levels.
- [ ] `inferred` authority is always marked with provenance — no silent inference.
- [ ] The `unknown` level has a defined graph behavior.

### 7.3 Knowledge Graph (§ 3.9)

- [ ] Three graphs are separate, not one polymorphic graph. Cross-check `DESIGN/005` and `DESIGN/006`.
- [ ] Edge metadata is required (no anonymous edges).
- [ ] "Acyclic within a stratum" is formal — is the algorithm defined? Cross-check `DESIGN/005` and `DECISIONS/0003-authority-graph-stratification.md`.

### 7.4 Context Package (§ 3.11)

- [ ] "Dependency-closed" is formally defined: every artifact in a slice has all its hard dependencies included or transitively reachable.
- [ ] "Authority-aware" is formally defined: under budget pressure, lower-authority artifacts are dropped first.
- [ ] The slice enumeration is finite and named (no open-ended slice kinds).

### 7.5 Diagnostic (§ 3.20)

- [ ] Severity enum is closed (no plugin-defined severities).
- [ ] `constitutional-violation` is the highest severity; ordering is total.
- [ ] Every diagnostic carries an invariant reference or `unspecified-invariant` (which is itself a warning).

### 7.6 Plugin (§ 3.14)

- [ ] Capabilities are a closed enum, not free-form strings. Cross-check `DESIGN/008`.
- [ ] `integrity_hash` is verified before load — this is an invariant, not a recommendation.
- [ ] A plugin that fails to declare its capabilities is rejected at load time.

## 8. Cross-Document Consistency

- [ ] Every component name in the ownership matrix (§ 4) matches `ARCHITECTURE.md` and `DESIGN/003`.
- [ ] Every stage referenced in ownership matches `DESIGN/005` pipeline stages.
- [ ] The 20 domain objects map cleanly to the data model in `DESIGN/004` — no object in this doc is missing from that one, and vice versa.

## 9. Open Questions

- [ ] All five open questions in § 8 are reflected as ADR candidates in `DECISIONS/002-domain-model-adr-candidates.md`.
- [ ] None are blocking M0; if any are, escalate.

## 10. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms.
- [ ] Every term introduced here is used consistently in other DESIGN docs (spot-check `DESIGN/005` and `DESIGN/007`).
- [ ] Length is appropriate (target: under 2000 lines).

## 11. Exit Criteria

The document passes review iff every checkbox is checked or has an ADR candidate addressing the gap.

Reviewer sign-off: ____________________ Date: __________