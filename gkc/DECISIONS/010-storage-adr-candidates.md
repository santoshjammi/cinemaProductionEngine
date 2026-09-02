# ADR Candidates — GKC-010 Storage

> Decisions surfaced by `DESIGN/010-storage.md`.

---

## ADR-Candidate-0054 — Encryption at rest

**Context.** § 14 does not mention encryption. Should storage support encryption at rest?

**Options.**
- **A. No.** Storage is plain; users encrypt the workspace directory with OS-level tools (FileVault, LUKS, etc.).
- **B. Optional, per-workspace.** `config.storage.encrypted: true` encrypts snapshot and cache files with a key derived from a passphrase.
- **C. Per-snapshot.** Each snapshot is independently encrypted.

**Recommendation.** A. No for M0–M5. OS-level encryption is simpler and more reliable than application-level encryption. A later horizon can add B for specific use cases (e.g., portable workspaces).

**Blocking impact.** None for M0–M5.

---

## ADR-Candidate-0055 — Workspace manifest signing

**Context.** § 14.3 mentions optional workspace manifest signing. Should it be required?

**Options.**
- **A. No signing.** The manifest is plain; integrity is per-blob.
- **B. Optional signing.** Workspaces may generate a local keypair and sign the manifest.
- **C. Required signing.** Every workspace has a keypair; manifest is always signed.

**Recommendation.** A. No signing for M0–M5. Per-blob content addressing already provides integrity; manifest signing adds key management complexity. Revisit if tampering becomes a real threat.

**Blocking impact.** None for M0–M5.

---

## ADR-Candidate-0056 — Snapshot deduplication

**Context.** Should snapshots share content (e.g., identical registry entries across snapshots are stored once)?

**Options.**
- **A. No dedup.** Each snapshot is self-contained. Simple; disk-heavy.
- **B. Content-addressed dedup.** Identical blobs (registry, graphs) are stored once and referenced by multiple snapshots.
- **C. Per-entry dedup.** Individual entries are stored once; snapshots reference them.

**Recommendation.** A. No dedup for M0–M5. Self-contained snapshots are simpler, easier to reason about, and easier to GC. Disk is cheap; complexity is expensive. Revisit at post-M5 if snapshot storage becomes a measured problem.

**Blocking impact.** Blocks M0. Must be resolved before M0.

---

## ADR-Candidate-0057 — Stage cache across GKC versions

**Context.** § 6.1 does not say whether the stage cache is invalidated on GKC version change.

**Options.**
- **A. Invalidate on any version change.** Conservative; cache misses on every upgrade.
- **B. Invalidate on major version only.** Minor/patch versions reuse the cache.
- **C. Include GKC version in cache key.** Per-version caches; no invalidation needed.

**Recommendation.** C. Include GKC version in the cache key (it's already part of the snapshot cache key per `DESIGN/004` § 2.2). This is the cleanest: no invalidation logic; old entries are LRU-evicted naturally.

**Blocking impact.** Blocks M0 stage cache. Must be resolved before M0.

---

## ADR-Candidate-0058 — Multi-write cache transactions

**Context.** Should storage support transactions across multiple cache writes (e.g., writing stage cache + context cache atomically)?

**Options.**
- **A. No.** Each cache write is independent; atomicity is per-write.
- **B. Yes, via a transaction API.** `begin_transaction` / `commit` / `rollback`.
- **C. Batch writes.** A `write_batch` operation writes multiple entries atomically.

**Recommendation.** A. No transactions. Each cache write is independent and atomic. Multi-write transactions add complexity for no current use case; the pipeline's stage-by-stage commit already provides the necessary atomicity.

**Blocking impact.** Blocks M0. Must be resolved before M0.