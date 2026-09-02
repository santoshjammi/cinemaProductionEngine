# PROMETHEUS — Implementation Tracking

This directory holds **per-milestone tracking artifacts**, updated as engineering proceeds. It is the engineering counterpart to the design package in `DESIGN/`.

## Contents (filled during build)

- `m0-status.md` — M0 progress, blockers, decisions.
- `m1-status.md` — M1 progress.
- `m2-status.md` — M2 progress.
- `m3-status.md` — M3 progress.
- `m4-status.md` — M4 progress.
- `m5-status.md` — M5 progress.
- `invariants.md` — GENESIS invariant codification tracker (per `DESIGN/010` and `DESIGN/016`).
- `golden-tasks.md` — golden PKP set (per `DESIGN/016` § golden repositories).
- `changelog.md` — engineering changelog.

## Per-milestone status template

```markdown
# M<N> Status

## Done conditions
- [ ] condition 1
- [ ] condition 2

## In progress
- ...

## Blockers
- ...

## Open ADRs
- ADR-XXXX: ...

## Next actions
- ...
```

## Rules

- Update this directory at every checkpoint (per `AGENTS.md` Checkpoint Protocol).
- Be deterministic and implementation-focused (per `AGENTS.md` Compression Rules).
- Do not delete historical status files; archive them in `archive/` instead.
- The runtime's operational memory files (`PROJECT_MEMORY.yaml`, `SESSION_STATE.yaml`, `CURRENT_TASK.md`, `RESTART_PROMPT.md` in `.project-ai/`) track the *active session*; this directory tracks the *product lifecycle*.

## See Also

- `gkc/IMPLEMENTATION/README.md` — the sibling product's tracking directory; the pattern this directory follows.