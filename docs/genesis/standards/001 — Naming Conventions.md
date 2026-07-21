Genesis Standard (GSTD)
GSTD-001 — Naming Conventions

Document ID: GSTD-001
Title: Naming Conventions
Version: 1.0.0
Status: Standard
Authority: Derived from GFS-000, GFS-010

1. Purpose

This Standard defines the naming conventions for every artifact in the Genesis
Engine repository — documents, directories, identifiers, code symbols,
ontology elements, and runtime entities. Consistent naming is a prerequisite
for the Ontology Compiler, the registry, and human navigation.

2. Document File Naming

Pattern: `NNN — Title.md`

- `NNN` is a zero-padded number unique within the parent directory.
- A space precedes and follows the em-dash (`—`, U+2014).
- Title uses Title Case.
- File extension is lowercase `.md`.

Examples:
- `001 — ConstitutionCharter.md`
- `014 — Production Plan Format.md`
- `101 — Character DNA YAML Schema.md`

A regular hyphen (`-`) is acceptable when em-dash entry is impractical, but
em-dash is the canonical form.

3. Directory Naming

- Top-level directories: lowercase single word or hyphenated kebab-case
  (`ontology/`, `yaml-schema/`, `agent-registry/`).
- Subdirectories under `ontology/`, `agents/`, `schemas/`, `specifications/`,
  `workflows/` use kebab-case domain names (`narrative/`, `character/`).

4. Document IDs

Format: `{PREFIX}-{NNN}` where PREFIX identifies the document class:

| Prefix  | Document class                          |
|---------|-----------------------------------------|
| GFS     | Genesis Foundational Standard           |
| GO      | Genesis Ontology                        |
| GAS     | Genesis Agent Specification             |
| GSPEC   | Genesis Specification                   |
| GWS     | Genesis Workflow Specification          |
| GSS     | Genesis Schema Specification            |
| GREF    | Genesis Reference                       |
| GTMP    | Genesis Template                        |
| GSTD    | Genesis Standard                        |
| GDEC    | Genesis Decision (ADR)                  |

Numbers are zero-padded to three digits and unique within the prefix. Derived
documents carry their parent's prefix number in the `Authority` field.

5. Ontology Element Naming

- Classes: `UpperCamelCase`, singular. Example: `Character`, `SceneBeat`.
- Datatype properties: `snake_case`. Example: `motivation`, `scene_number`.
- Object properties (relationships): `UPPER_SNAKE_CASE`. Example:
  `APPEARS_IN`, `MOTIVATES`.
- Enumeration values: `UPPER_SNAKE_CASE`. Example: `EXPLICIT`, `INFERRED`.
- Ontology namespace URIs:
  `https://genesis.movieos.dev/ontology/{domain}/{name}`.

6. Code Naming (Python)

- Modules: `snake_case`.
- Classes: `UpperCamelCase`.
- Functions and variables: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.
- Private symbols: leading underscore `_snake_case`.
- Async functions: same as sync, no `async_` prefix.
- Type aliases: `UpperCamelCase` ending in a noun (`NodeRef`, `EdgeList`).

7. Code Naming (TypeScript)

- Files: `kebab-case.ts`.
- Interfaces and types: `UpperCamelCase`.
- Functions and variables: `camelCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Enums: `UpperCamelCase` with `UPPER_SNAKE_CASE` members.

8. Runtime Entity Naming

- Production ID: UUIDv4.
- PKG node ID: UUIDv4.
- PKG edge ID: UUIDv4.
- Session ID: UUIDv4 or a slug prefixed `sess_`.
- Agent ID: kebab-case slug (e.g. `character-architect`, `validation-shacl`).
- Workflow ID: UUIDv4.
- Tenant ID: kebab-case slug assigned by the platform.

9. YAML and JSON Keys

- `snake_case` for all keys.
- Booleans use `true`/`false` (YAML) and `true`/`false` (JSON).
- Dates use ISO 8601 (`YYYY-MM-DD`); datetimes use RFC 3339.
- Confidence values use the five canonical uppercase strings.

10. Branch and Commit Naming (Git)

- Branch: `{type}/{short-description}` where type is `feature`, `fix`,
  `docs`, `ont`, `spec`, `refactor`.
- Commit subject: imperative mood, max 72 chars, references Document ID when
  relevant (e.g. `spec: add GSPEC-042 Ontology Extension`).

11. Conflicts

When this Standard conflicts with a domain-specific convention (e.g. an
external ontology reuse), the external convention is adopted for the borrowed
elements only. All native Genesis elements follow this Standard.

12. Cross-References

- Coding Standards: GSTD-002
- Documentation Standards: GSTD-003
- Ontology Specification Standard: GSPEC-041