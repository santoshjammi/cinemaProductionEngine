Genesis Guide (GDE)
GDE-002 — Contributor Guide

Document ID: GDE-002
Title: Genesis Contributor Guide
Version: 1.0.0
Status: Guide
Authority: Derived from GFS-000, GFS-007

1. Purpose

This guide tells a contributor how to propose a change to the Genesis Engine
documentation repository. It covers forking, branch naming, commit hygiene,
the pull request process, the review criteria, and the constitutional
compliance checks every change must pass.

Genesis is a constitutionally governed repository. A contribution is not
measured only by whether it is well written; it is measured by whether it
respects the Charter (GFS-000), the derived constitutions (GFS-001 through
GFS-009), and the canonical hierarchy. A technically correct change that
violates a constitutional invariant will be rejected.

2. Who May Contribute

Genesis accepts contributions from any contributor who agrees to work within
the constitutional hierarchy. There are no special access requirements for
proposing a change. Reviewers and maintainers are governed by GFS-007
(Governance Constitution).

3. Fork and Branch

1. Fork the repository.
2. Create a feature branch from `main`. The branch name must encode intent:

   - `add/<NNN>-<slug>`      — adding a new document.
   - `update/<NNN>-<slug>`    — updating an existing document.
   - `fix/<NNN>-<slug>`       — fixing a defect in an existing document.
   - `refactor/<area>-<slug>` — restructuring without semantic change.
   - `meta/<slug>`            — repository meta-changes (tooling, linting).

   Examples:
   - `add/GAS-028-casting-director`
   - `fix/GO-104-character-dna-facet`
   - `update/GFS-010-pkg-serialization`

3. Do not branch from another feature branch. Always branch from `main`
   unless explicitly coordinating with a maintainer.

4. Commit Hygiene

- One logical change per commit.
- The commit subject references the document ID: `GAS-028: add Casting
  Director Agent specification`.
- The commit body explains why the change is needed, not what it does;
  the diff already shows what.
- No secrets, no credentials, no local paths.
- No generated artifacts committed alongside source unless the document
  explicitly requires them (e.g., a packaged skill zip).

5. Pull Request Process

1. Open the PR against `main`.
2. The PR description must include:
   - The document IDs affected.
   - The parent documents in the constitutional hierarchy.
   - The motivation (what uncertainty does this reduce?).
   - The validation commands run and their results.
3. The PR must pass the automated constitutional checks (see §7) before a
   human reviewer is assigned.
4. A reviewer is assigned by the maintainers based on the affected area.
5. The reviewer may request changes. Address them in the same branch; do
   not open a new PR.
6. Once the reviewer approves, a maintainer merges. Maintainers use
   squash-and-merge to keep `main` history linear.

6. Review Criteria

Reviewers evaluate every contribution against six axes. A PR must pass all
six.

6.1 Constitutional Compliance

- Does the change respect GFS-000 and the derived constitutions?
- Does it preserve the invariants declared in the Charter?
- If it introduces a new invariant, has it been through the constitutional
  amendment process (GFS-009)?

6.2 Ontological Coherence

- If the change touches ontology, does it derive from GO-001?
- Does it redefine any existing concept? (It must not.)
- Is the new concept registered in the Ontology Registry?

6.3 Architectural Fit

- Does the change belong in the directory it is placed in?
- Does it respect the layer boundaries in GD-001?
- Does it introduce a cross-layer dependency? (It must not.)

6.4 Internal Consistency

- Are all cross-references valid?
- Are the inputs, outputs, and dependencies declared and consistent with
  the rest of the repository?
- Does the change contradict any existing document without an ADR?

6.5 Completeness

- Does the document have the mandatory header block?
- Does it have between 150 and 600 lines of real content?
- Does it have the required sections for its document type?

6.6 Style and Naming

- Does the filename use the em-dash convention?
- Is the document ID unique within its directory?
- Is the Status value from the canonical set?

7. Constitutional Compliance Checks

Before opening a PR, run the following from the repository root:

- `bash tooling/lint-docs.sh`
- `bash tooling/validate-cross-refs.sh`
- `bash tooling/check-ontology-derivation.sh`
- `bash tooling/check-agent-registry.sh`

Each script exits non-zero on failure. Fix every reported issue before
opening the PR. A PR that fails any of these checks will not be assigned a
reviewer.

If a check needs to be updated because a constitutional invariant has
changed, open a separate `meta/` PR for the linter change first. Do not
bundle a linter change with a content change.

8. Special Contribution Types

8.1 New Constitution or Amendment

A new constitution (GFS-NNN) or an amendment to an existing one is the
highest-impact change type. It requires:

- A dedicated PR with only the constitutional change.
- An Architecture Decision Record (ADR) explaining the motivation.
- Approval from at least two maintainers.
- An update to the Constitutional Ontology Framework (GFS-009) if the
  change alters the derivation rules.

8.2 New Ontology

A new ontology (GO-NNN) requires:

- Derivation from GO-001 or a parent domain ontology.
- Registration in the Ontology Registry.
- An entry in the Ontology Evolution Framework (GMM-002) describing the
  versioning and backward compatibility policy for the new ontology.

8.3 New Agent

A new agent (GAS-NNN) requires:

- A declared constitutional class.
- Declared inputs, outputs, and dependencies.
- An entry in the Agent Registry.
- An update to the Agent Dependency Graph (GD-002) if dependencies are
  non-obvious.

9. Deprecation

Contributors may propose deprecation of a document. Deprecation is not
deletion. The document's Status is changed to `Deprecated`, a
`Deprecation Notice` section is added explaining the rationale and
replacement, and the registry entry is updated. A deprecated document
remains in the repository for audit and reference.

10. Communication

- Use the issue tracker for proposals and questions before opening a PR
  when the change is non-trivial.
- Keep PR discussions about the change, not about the contributor.
- Reviewers are expected to give actionable feedback. "Looks good" is
  not a review.
- Maintainers are expected to enforce the constitutional hierarchy
  impartially.

11. Licensing and Attribution

By contributing, you agree that your contribution is licensed under the
same terms as the repository. You attest that you have the right to make
the contribution. Generated or AI-assisted contributions must be reviewed
and attested by a human before merging.