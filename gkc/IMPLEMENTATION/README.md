# GKC — Implementation Tracking

This directory holds **per-milestone tracking artifacts**, updated as engineering proceeds. It is the engineering counterpart to the design package in `DESIGN/`.

## Contents (filled during build)

- `m0-status.md` — M0 progress, blockers, decisions.
- `m1-status.md` — M1 progress.
- `m2-status.md` — M2 progress.
- `m3-status.md` — M3 progress.
- `m4-status.md` — M4 progress.
- `m5-status.md` — M5 progress.
- `invariants.md` — GENESIS invariant codification tracker (per `DESIGN/005` and `DESIGN/011`).
- `golden-tasks.md` — golden task set (per `DESIGN/007` § 13 and `DESIGN/011` § 13.2).
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