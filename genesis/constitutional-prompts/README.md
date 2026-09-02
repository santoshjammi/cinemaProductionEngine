# Constitutional Prompts — Index

**Status:** Design History Artifact
**Date:** 2026-07-21
**Purpose:** This directory preserves the prompts that generated the constitutional specifications of the Cinema Production Engine. Each prompt is a constitutional artifact in its own right, capturing not only the resulting specification but also the intent behind how it was generated.

## Rationale

The constitutional specifications (00, 001, 002, 003, 004, 005, ...) define the architectural foundation of the Cinema Production Engine. The prompts that generated them encode the design intent, the constraints, the user amendments, and the reasoning behind the architecture. Preserving the prompts:

- Makes the design history auditable.
- Enables consistent regeneration of specifications when the architecture evolves.
- Makes it easier to review or extend constitutional documents without losing the original intent.
- Captures user amendments (renames, ordering decisions, structural corrections) that shaped the final specifications.

## Catalog

| Prompt | Corresponding Specification | Status |
|--------|-----------------------------|--------|
| `prompt-001-migration.md` | `001 — GENESIS 2.0 Migration Specification.md` | Preserved |
| `prompt-002-director-intelligence.md` | `002 — Director Intelligence & Creative Reasoning Architecture Specification.md` | Preserved |
| `prompt-003-cis.md` | `003 — Creative Intent Specification (CIS) Architecture.md` | Preserved |
| `prompt-004-com.md` | `004 — Creative Object Model (COM) & Semantic Architecture Specification.md` | Preserved |
| `prompt-005-cognitive-intelligence.md` | `005 — Cognitive Intelligence Architecture & Creative Faculties Specification.md` | Preserved |

## Note on Prompt 000

The prompt that generated `00 — Cinema Production Engine Vision, Philosophy & Reference Architecture.md` predates this preservation practice. The Vision document stands as its own authoritative source; no retroactive prompt is maintained.

## Convention

Future constitutional prompts (006 onward) shall be preserved in this directory following the naming pattern `prompt-NNN-<short-name>.md`, with each prompt containing:

- The role assigned to the architect.
- The objective and required parts.
- Any user amendments that shaped the specification.
- The architectural constraints.
- The expected output.
- Design intent notes explaining the critical insights encoded in the prompt.

Prompts are immutable once the corresponding specification is frozen. Amendments to a specification generate a new prompt (e.g., `prompt-002a-director-intelligence-amendment.md`) rather than mutating the original.