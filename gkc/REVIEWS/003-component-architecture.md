# GKC-003 — Engineering Review

> Adversarial review of `DESIGN/003-component-architecture.md`.

## Review Stance

The reviewer is a systems architect who assumes components will leak into each other unless boundaries are explicit and tested. The reviewer looks for: missing components, overlapping responsibilities, hidden coupling, and interfaces that cannot be implemented as specified.

## 1. Component Inventory Completeness

- [ ] Every component in `ARCHITECTURE.md` appears in § 2 of this doc.
- [ ] No component in § 2 is missing from `ARCHITECTURE.md`.
- [ ] Every domain object in `DESIGN/002` has at least one component that creates it.
- [ ] Every domain object has at least one component that destroys it (or marks it for GC).

## 2. Responsibility Clarity

For each component (C1–C15):

- [ ] Responsibilities are imperative sentences ("does X"), not vague nouns.
- [ ] Boundaries section lists at least three "does NOT" items.
- [ ] No two components share a primary responsibility.
- [ ] No responsibility is orphaned (every "X does Y" has an owner).

## 3. Interface Completeness

For each component:

- [ ] Request type is named and has its fields enumerated (or referenced).
- [ ] Result type is named and has its fields enumerated.
- [ ] Failure modes are listed and each maps to a typed diagnostic.
- [ ] The interface is implementable without referencing another component's internals.

## 4. Boundary Integrity

- [ ] The "Boundaries" section of each component forbids at least one tempting but wrong behavior.
- [ ] The § 5 summary table's "Does NOT" column is non-empty for every component.
- [ ] No component claims to mutate a domain object it does not own per `DESIGN/002` § 4.
- [ ] The static dependency graph (§ 4.1) is acyclic.

## 5. Failure Isolation

- [ ] Plugin failure isolation is specified per-component (not just globally).
- [ ] Storage failure is specified to not corrupt snapshots.
- [ ] Validator failure is specified to mark the invariant `not-checked`.
- [ ] Every component has at least one documented failure mode.

## 6. Extension Point Coherence

- [ ] Every extension point in § 6 names its host component and its DESIGN doc.
- [ ] No extension point allows plugins to mutate the IR directly (extensions produce outputs that stages consume).
- [ ] The plugin framework itself is not extensible (per § C14).
- [ ] Built-in plugins are not privileged (per § C14).

## 7. Interaction Map Validity

- [ ] The static dependency graph (§ 4.1) matches the boundaries in § 3.
- [ ] The runtime flow (§ 4.2) matches the pipeline in `DESIGN/005`.
- [ ] The failure isolation boundaries (§ 4.3) reference real components and real failure modes.
- [ ] No component appears in the runtime flow before its static dependencies are loaded.

## 8. Non-Goal Enforcement

- [ ] § 7 lists five non-goals; each is checkable against the component specs.
- [ ] No component specifies a network call (except plugins with declared capability).
- [ ] No component specifies a subprocess spawn (except plugins with declared capability).
- [ ] No component persists state outside Storage.

## 9. Cross-Document Consistency

- [ ] Component names match `ARCHITECTURE.md` and `DESIGN/005`.
- [ ] Extension points match `DESIGN/008`.
- [ ] CLI subcommands implied by components (e.g., `gkc scan` → C1) match `DESIGN/009`.
- [ ] Storage interface matches `DESIGN/010`.

## 10. Open Questions

- [ ] All five open questions in § 8 are ADR candidates in `DECISIONS/003-component-architecture-adr-candidates.md`.
- [ ] None block M0; if any do, escalate.

## 11. Document Quality

- [ ] No implementation code.
- [ ] No language-specific idioms.
- [ ] No public API surface.
- [ ] Reasonable length (target: under 1500 lines).

## 12. Exit Criteria

The document passes iff every checkbox is checked or has an ADR candidate addressing it.

Reviewer sign-off: ____________________ Date: __________