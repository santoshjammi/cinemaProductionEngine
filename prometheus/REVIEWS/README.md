# PROMETHEUS — Engineering Reviews

This directory holds **adversarial review checklists** — one per DESIGN doc. A DESIGN doc must pass its review before its target milestone implementation begins.

## Review Stance

The reviewer is a skeptical runtime engineer who assumes the design is over-claimed until proven otherwise. The reviewer's job is to find places where the design makes commitments the rest of the package (or GENESIS) cannot cash. The reviewer does not approve on faith; the reviewer approves on evidence.

## Review Checklist Shape

Each review covers (mirroring the `gkc/REVIEWS/` convention):

1. **Coherence with GENESIS** — does the design conflict with `010` or any `000`–`018` document?
2. **Invariant testability** — is every stated invariant testable? Is the test defined or cross-referenced?
3. **Success criteria measurability** — is every success criterion measurable? With what tolerance?
4. **Definition risks** — are the design's definitions operational, or do they smuggle in undefined terms?
5. **Cross-doc consistency** — does the design agree with the other DESIGN docs on shared terms?
6. **Engineering risks** — what is the single hardest engineering problem this design creates?

## Review Index (populated during Phase 2)

Phase 1 writes the core DESIGN docs. Phase 2 will write the corresponding adversarial reviews:

| Review | Source DESIGN doc | Blocks milestone |
|---|---|---|
| `001-vision.md` | `DESIGN/001-vision.md` | M0 |
| `002-execution-model.md` | `DESIGN/002-execution-model.md` | M0 |
| `003-component-architecture.md` | `DESIGN/003-component-architecture.md` | M0 |
| `004-eir.md` | `DESIGN/004-eir.md` | M0 |
| `005-pipeline.md` | `DESIGN/005-pipeline.md` | M1 |
| `006-adapter-framework.md` | `DESIGN/006-adapter-framework.md` | M2 |

## See Also

- `gkc/REVIEWS/` — the sibling product's reviews; the pattern this directory follows.