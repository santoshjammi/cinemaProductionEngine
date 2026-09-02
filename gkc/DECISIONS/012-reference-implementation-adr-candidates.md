# ADR Candidates — GKC-012 Reference Implementation

> Decisions surfaced by `DESIGN/012-reference-implementation.md`.

---

## ADR-Candidate-0010 — Implementation language

**Context.** § 2 lists four candidate languages with criteria. The reference implementation must pick one for M0.

**Options.**
- **A. Rust.** Strong on determinism, concurrency, distribution; plugin ABI via WASM or dynamic crates.
- **B. Go.** Strong on concurrency, distribution, team familiarity; plugin ABI via Go plugins (Linux) or RPC.
- **C. TypeScript/Node.** Strong on team familiarity; weaker on serialization, distribution.
- **D. Python.** Strong on team familiarity; weaker on serialization, distribution, performance.

**Recommendation.** A. Rust. The compiler framing (determinism, staging, incrementality, cacheability) maps naturally to Rust's strengths; single-binary distribution matches the local-first invariant; the WASM plugin ABI aligns with the post-M5 process-isolation horizon. The learning curve is offset by the design's language independence — the design docs are language-neutral, so the implementation is a pure engineering effort.

**Blocking impact.** Blocks M0. Must be ratified before M0 starts.

---

## ADR-Candidate-0011 — Distribution mechanism

**Context.** GKC ships as a CLI. How is it distributed?

**Options.**
- **A. Standalone binary via GitHub releases.** Single binary; no package manager dependency; cross-platform.
- **B. Package managers (brew, apt, cargo, npm, pip).** Multiple; each has its own update mechanism.
- **C. Both.** Binary as primary; package manager wrappers as community-maintained.

**Recommendation.** A for M0–M5. Standalone binary. Package manager support is a post-M5 community effort. The binary distribution matches the local-first invariant and keeps the release process simple.

**Blocking impact.** Blocks M5 release. Must be ratified before M5.

---

## ADR-Candidate-0064 — Reference implementation repo location

**Context.** Should the reference implementation live in the same repo as the design package, or in a separate repo?

**Options.**
- **A. Same repo (`videoGen/gkc/`).** Design and code together; single PR for design + implementation changes.
- **B. Separate repo.** Design is one repo; implementation is another; cross-references via URLs.
- **C. Same repo initially; split at M5.** Start together; split when the design stabilizes.

**Recommendation.** A. Same repo. Design and implementation co-evolve during M0–M5; splitting adds friction. Revisit at M5 if the design package stabilizes and the implementation outgrows the repo.

**Blocking impact.** Blocks M0. Must be ratified before M0.

---

## ADR-Candidate-0065 — Formal verification of core invariants

**Context.** § 9.2 mentions architecture stability. Should the core invariants (determinism, incrementality, staging) be formally verified?

**Options.**
- **A. No formal verification.** Tests are sufficient.
- **B. Partial — verify determinism and staging.** Use a proof assistant for the core invariants only.
- **C. Full formal verification.** Prove all invariants.

**Recommendation.** A for M0–M5. No formal verification. The invariant tests (per `DESIGN/011` § 9) provide strong empirical assurance. Formal verification is a post-M5 research effort.

**Blocking impact.** None for M0–M5.

---

## ADR-Candidate-0066 — Watch mode

**Context.** § 9.1 mentions `gkc serve` as a post-M5 horizon. Should there also be a `gkc watch` mode that re-compiles on file change?

**Options.**
- **A. No watch mode.** Users run `gkc scan` manually after changes.
- **B. `gkc watch`.** Watches the repository; re-compiles incrementally on file change.
- **C. `gkc watch` as a plugin.** A plugin adds watch mode via the storage backend extension.

**Recommendation.** B. `gkc watch` at M5 (minor version bump; additive). IDE integration is a primary use case for GKC; watch mode is essential for IDE responsiveness. It composes naturally with the incremental compile infrastructure.

**Blocking impact.** Blocks M5 IDE integration. Must be ratified before M5.