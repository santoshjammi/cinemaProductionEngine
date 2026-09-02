Genesis Standard (GSTD)
GSTD-003 — Documentation Standards

Document ID: GSTD-003
Title: Documentation Standards
Version: 1.0.0
Status: Standard
Authority: Derived from GFS-000, GFS-010, GSTD-001

1. Purpose

This Standard defines the structure, formatting, and lifecycle of every
document in the Genesis Engine repository. Documentation is treated as a
first-class artifact: it is versioned, reviewed, and compiled where
applicable. The Standard exists to make Genesis self-explaining — every
engineer, agent, and auditor can navigate the system without external lore.

2. Document Classes

| Class        | Prefix  | Location                  |
|--------------|---------|---------------------------|
| Constitution | GFS     | `constitutions/`          |
| Ontology     | GO      | `ontology/`               |
| Agent spec   | GAS     | `agents/`                 |
| Specification| GSPEC   | `specifications/`         |
| Workflow     | GWS     | `workflows/`              |
| Schema       | GSS     | `schemas/`                |
| Reference    | GREF    | `references/`             |
| Template     | GTMP    | `templates/`              |
| Standard     | GSTD    | `standards/`              |
| Decision     | GDEC    | `decisions/`              |

3. Required Header Block

Every document MUST begin with:

{Class full name} ({PREFIX})
{PREFIX}-{NNN} — {Title}

Document ID: {PREFIX}-{NNN}
Title: {Title}
Version: {semver}
Status: Draft | Reviewed | Stable | Deprecated | Superseded
Authority: Derived from {parent document ids}

Lines are blank-separated. The header is mandatory; documents missing it are
rejected by the linter and the Ontology Compiler.

4. Body Structure

The body uses numbered top-level sections (`1. Purpose`, `2. Scope`, ...).
Subsections use `### Title` under the relevant numbered section. Lines wrap
at 100 characters where practical. Prose is terse and declarative.

5. Required Sections by Class

| Class        | Required sections                                              |
|--------------|---------------------------------------------------------------|
| Constitution | Purpose, Scope, Principles, Authority, Amendments             |
| Ontology     | Per GSPEC-041 §4                                              |
| Agent spec   | Identity, Purpose, Responsibilities, Inputs, Outputs, Quality Criteria, Dependencies |
| Specification| Purpose, Scope, Format/Protocol, Validation, Cross-References |
| Workflow     | Purpose, Trigger, Steps, Inputs, Outputs, Exit Criteria, Rollback |
| Schema       | Purpose, Schema, Validation Rules, Usage                      |
| Reference    | Purpose, Source citation, Summary, Applicability              |
| Template     | Purpose, Fields, Usage example                                |
| Standard     | Purpose, Scope, Rules, Cross-References                       |
| Decision     | Context, Decision, Rationale, Alternatives, Consequences      |

6. Cross-References

In-document references use the Document ID in parentheses: `(GSS-001)`,
`(GSPEC-041 §4)`. External references link to the file path or URL. Every
document MUST end with a `Cross-References` section listing its parents,
dependencies, and related documents.

7. Code Blocks

- Fenced code blocks declare a language: ` ```json `, ` ```yaml `,
  ` ```python `, ` ```cypher `.
- Inline code uses single backticks.
- Schema documents embed the schema as a fenced block and follow it with
  prose validation rules.

8. Tables

GitHub-flavored markdown tables. Columns are aligned with spaces. Numeric
columns are right-aligned. Tables are used for enumerations, matrices, and
summaries — not for narrative.

9. Versioning and Lifecycle

- Every document carries a semantic version in its header.
- A patch bump fixes typos or clarifies prose.
- A minor bump adds content without invalidating prior references.
- A major bump changes meaning, structure, or required sections.
- `Status` transitions: Draft → Reviewed → Stable → Deprecated/Superseded.
- A Deprecated document references its successor. A Superseded document is
  retained read-only.

10. Change Log

Repository-level changes are recorded in `CHANGELOG.md` under
`Keep a Changelog` format. Document-level changes are summarized in the
document's `Amendments` or `Revision History` section when the class requires
it (Constitutions, Decisions).

11. Review

- Drafts are authored in a feature branch.
- Reviewers are assigned by the Governance Board for Stable-bound documents.
- Review checklist: header correct, sections present, cross-references valid,
  no broken file paths, no unresolved TODOs, version bumped, CHANGELOG
  updated.
- Merge requires at least one approving review.

12. Linting

A documentation linter (`genesis docs lint`) enforces:
- Header block presence and correctness.
- Required sections per class.
- Document ID uniqueness within prefix.
- Cross-reference targets exist.
- Line wrap at 100 chars (warning).
- No trailing whitespace, no tabs in prose.

13. Cross-References

- Naming Conventions: GSTD-001
- Coding Standards: GSTD-002
- Ontology Specification Standard: GSPEC-041
- Ontology Compiler (lint integration): GSPEC-031