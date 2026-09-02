# PROMETHEUS — Engineering Prompts

This directory holds **engineering prompts** — one per DESIGN doc — that drive an implementation agent to build the subsystem described in that DESIGN doc. A prompt is not implementation code; it is the engineering scaffolding that makes the design testable.

## Prompt Structure

Each prompt follows this shape (mirroring the `gkc/PROMPTS/` convention):

1. **Objective** — what the prompt establishes, at the skeleton or full level.
2. **Inputs** — the authoritative DESIGN doc and any cross-references.
3. **Scope** — the concrete items to implement.
4. **Out of Scope** — what belongs to other prompts.
5. **Done Conditions** — testable, evidence-based completion criteria.
6. **Constraints** — invariants that must not be violated.
7. **Deliverables** — the artifacts the prompt produces.

## Prompt Index (populated during Phase 2)

Phase 1 writes the core DESIGN docs. Phase 2 will write the corresponding engineering prompts:

| Prompt | Source DESIGN doc | Target milestone |
|---|---|---|
| `001-vision.md` | `DESIGN/001-vision.md` | M0 |
| `002-execution-model.md` | `DESIGN/002-execution-model.md` | M0 |
| `003-component-architecture.md` | `DESIGN/003-component-architecture.md` | M0 |
| `004-eir.md` | `DESIGN/004-eir.md` | M0 |
| `005-pipeline.md` | `DESIGN/005-pipeline.md` | M1 |
| `006-adapter-framework.md` | `DESIGN/006-adapter-framework.md` | M2 |

## See Also

- `gkc/PROMPTS/` — the sibling product's prompts; the pattern this directory follows.