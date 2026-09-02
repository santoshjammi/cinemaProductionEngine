# PROMETHEUS — Decisions Index

This directory holds **ADR candidates** (surfaced by DESIGN docs, awaiting ratification) and **ratified ADRs** (decisions that govern the implementation).

## ADR Process

1. A DESIGN doc surfaces a decision as a candidate in its `DECISIONS/00N-*-adr-candidates.md` file.
2. The candidate is reviewed (per the corresponding `REVIEWS/00N-*.md`).
3. Ratified candidates become ADRs (moved or copied to `DECISIONS/ADR-XXXX.md` with status `Ratified`).
4. ADRs are numbered sequentially from 0001.
5. ADRs are immutable once ratified; supersession requires a new ADR.

## Constitutional Primacy

PROMETHEUS engineering ADRs govern the **engineering product** only. They may not amend GENESIS (`000`–`018`). If a DESIGN doc or an ADR candidate conflicts with `010 — PROMETHEUS Runtime Architecture.md` or any GENESIS document:

- The GENESIS document wins.
- The ADR candidate must either change to align with GENESIS, or escalate as a request for **constitutional revision** (not an engineering ADR).

Engineering ADRs and constitutional amendments are two different tracks and must never be confused.

## Candidate Index (populated during Phase 2)

This index will list ADR candidates surfaced by each DESIGN doc, the milestone they block, and their status. Phase 1 design docs will populate candidate files in `DECISIONS/00N-*-adr-candidates.md` as they are written.

| Source | Candidates | Blocking milestone | Status |
|---|---|---|---|
| `001-vision` | (to be surfaced in Phase 2) | M0 | pending |
| `004-eir` | (to be surfaced in Phase 2) | M0 | pending |
| `005-pipeline` | (to be surfaced in Phase 2) | M1 | pending |
| `006-adapter-framework` | (to be surfaced in Phase 2) | M2 | pending |
| `009-cli` | (to be surfaced in Phase 2) | M0 | pending |
| `012-recovery` | (to be surfaced in Phase 2) | M2 | pending |

## Blocking ADRs for M0

The following must be ratified before M0 implementation begins (to be enumerated as DESIGN docs are written):

- **Implementation language** — the reference implementation's host language. All contracts remain language-neutral regardless.
- **Concurrency model** — threads, actors, async, or a mix; affects determinism and the event bus.
- **EIR serialization format** — JSON, MessagePack, Protobuf, or a custom binary form; must be language-neutral and versioned.
- **Workspace location** — same-repo or separate-repo for the reference implementation.

Most of these have clear recommendations in their candidate files; ratification is expected to be quick.

## See Also

- `DECISIONS/README.md` in `gkc/` — the sibling product's ADR index; the pattern this directory follows.
- `010 — PROMETHEUS Runtime Architecture.md` (repo root) — the constitutional authority ADRs must respect.