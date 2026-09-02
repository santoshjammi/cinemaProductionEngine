# ADR Candidates — GKC-005 Pipeline

> Decisions surfaced by `DESIGN/005-pipeline.md`.

---

## ADR-Candidate-0029 — Context stage: pipeline stage vs. separate service

**Context.** Stage 11 is lazy. Should it be a true pipeline stage or a separate on-demand service that reads snapshots?

**Options.**
- **A. Pipeline stage (current).** Runs in the build session; lazy flag controls eager vs. lazy. Same process; simpler.
- **B. Separate service.** A long-running `gkc serve` process that loads snapshots and answers context requests. Decoupled; new operational burden.
- **C. CLI subcommand.** No stage; `gkc context` reads a snapshot and builds the package on demand. Simplest; no caching across calls except on-disk.

**Recommendation.** C. CLI subcommand. Matches the use case (on-demand context) without introducing a service. Caching is on-disk via the context cache (per § 4.1). A service (B) can be added later if latency demands it.

**Blocking impact.** Blocks `DESIGN/007` and `DESIGN/009`. Must be resolved before M3.

---

## ADR-Candidate-0030 — Partial snapshot loadability

**Context.** § 7.3 says partial snapshots are not sealable. Should they be loadable at all?

**Options.**
- **A. Strict rejection.** Partial snapshots cannot be loaded; consumers must request a full compile.
- **B. Loadable with `unbuilt` markers.** Consumers can load and inspect what's present; queries against unbuilt components return `unbuilt` errors.
- **C. Configurable per consumer.** Some consumers (e.g., `gkc stats`) accept partial; others (AIOS) require full.

**Recommendation.** B. Loadable with markers. Enables debugging (you can inspect a partial compile's state) and lets `gkc stats` work after a partial compile. AIOS and other downstream consumers can require full snapshots by policy.

**Blocking impact.** Blocks `DESIGN/010` storage reader. Must be resolved before M1.

---

## ADR-Candidate-0031 — Stage cache sharing across workspaces

**Context.** § 4.1 says stage cache is per-workspace. Should it be shared?

**Options.**
- **A. Per-workspace.** Each workspace has its own stage cache. Reproducible; disk duplication.
- **B. Shared global cache.** One cache; all workspaces share. Less duplication; cross-workspace contention.
- **C. Per-workspace primary, shared secondary.** Workspace cache first; global cache as fallback.

**Recommendation.** A. Per-workspace. Reproducibility (per `DESIGN/001` § 7.1) requires the workspace's cache be self-contained. Sharing introduces nondeterminism (one workspace's cache depends on another's history).

**Blocking impact.** Blocks `DESIGN/010`. Must be resolved before M0.

---

## ADR-Candidate-0032 — Cached diagnostics in incremental compile

**Context.** When a stage's output is cached (cache hit), should its diagnostics be re-emitted from the cache or recomputed?

**Options.**
- **A. Re-emit from cache.** Diagnostics are part of the stage output; cached output includes cached diagnostics. Fast; deterministic.
- **B. Recompute.** Diagnostics are recomputed even on cache hit. Slower; matches "fresh diagnostics" intuition.
- **C. Re-emit with cache marker.** Re-emit but tag each diagnostic with `from-cache: true`.

**Recommendation.** A. Re-emit from cache. Diagnostics are part of the stage's typed output; cache hits return the full output including diagnostics. This preserves determinism and is the simplest correct behavior.

**Blocking impact.** Blocks M1 incremental diagnostics. Must be resolved before M1.

---

## ADR-Candidate-0033 — Stage retry on transient failure

**Context.** Should the pipeline runner retry a stage that fails with a transient error (e.g., a filesystem hiccup)?

**Options.**
- **A. No retry.** Failures are final; the user re-runs.
- **B. Configurable retry with backoff.** Stages declare if they are retryable; runner retries up to N times with backoff.
- **C. Automatic for idempotent stages only.** Stages declare idempotency; runner retries only idempotent stages.

**Recommendation.** A. No retry. Simplicity favors the user re-running. Retry adds complexity (backoff, partial state) and risks masking real issues. A later horizon can add C if needed.

**Blocking impact.** Blocks M0 failure policy. Must be resolved before M0.