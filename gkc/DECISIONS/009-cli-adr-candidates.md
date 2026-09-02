# ADR Candidates — GKC-009 CLI

> Decisions surfaced by `DESIGN/009-cli.md`.

---

## ADR-Candidate-0049 — `gkc serve` long-running mode

**Context.** § 3 lists 13 subcommands; none is `serve`. Should we add a long-running mode?

**Options.**
- **A. No.** The CLI is one-shot; AIOS / IDEs run `gkc` as a subprocess per request.
- **B. Yes, `gkc serve`.** A long-running process that holds the IR in memory and answers queries via a local socket.
- **C. Optional plugin.** A plugin can add a serve mode via the storage backend extension point.

**Recommendation.** A. No serve mode for M0–M5. The one-shot model matches the compiler framing and the local-first invariant. A serve mode adds operational complexity (lifecycle, sockets, auth) not justified by current use cases. Revisit at post-M5.

**Blocking impact.** Blocks M0. Must be resolved before M0.

---

## ADR-Candidate-0050 — `gkc context` streaming output

**Context.** § 4.6 implies single-payload output. Should `gkc context` stream?

**Options.**
- **A. No.** Single payload to stdout; matches ADR-Candidate-0014.
- **B. Yes, with `--stream`.** Slices are emitted one at a time as they're produced.
- **C. Via provider.** Providers decide whether to stream.

**Recommendation.** A. No streaming for M3. Single payload matches the context package model (per `DESIGN/007` § 10.3). Streaming adds complexity for marginal benefit; context packages are bounded by the token budget and fit in memory.

**Blocking impact.** Blocks M3. Must be resolved before M3.

---

## ADR-Candidate-0051 — `gkc diff` subcommand

**Context.** Should there be a `gkc diff <a> <b>` subcommand for comparing snapshots?

**Options.**
- **A. Yes.** Add `gkc diff` as a 14th subcommand.
- **B. No; use `gkc snapshot diff` (a subcommand of a hypothetical `gkc snapshot`).**
- **C. Defer.** Not in M0–M5; revisit at post-M5.

**Recommendation.** C. Defer. The current 13-subcommand set is stable; adding `diff` breaks the stability promise. If diff becomes needed, add it as a major version bump. For now, `gkc snapshot list` + manual comparison suffices.

**Blocking impact.** None for M0–M5.

---

## ADR-Candidate-0052 — Shell completion

**Context.** Should the CLI ship shell completion scripts?

**Options.**
- **A. Yes, generated.** `gkc completion bash` outputs a script; users source it.
- **B. Yes, hand-written.** Ship scripts for bash, zsh, fish in the distribution.
- **C. No.** Defer; users roll their own.

**Recommendation.** A. Generated. The CLI spec is the source of truth; generating completion from it avoids drift. Add `gkc completion <shell>` as a 14th subcommand at M5 (minor version bump; additive).

**Blocking impact.** Blocks M5 polish. Must be resolved before M5.

---

## ADR-Candidate-0053 — `gkc config` subcommand

**Context.** § 8 describes config but there's no subcommand to edit it.

**Options.**
- **A. No subcommand.** Users edit `config.json` directly.
- **B. `gkc config get/set`.** Programmatic access to config.
- **C. `gkc config edit`.** Opens the config in `$EDITOR`.

**Recommendation.** A. No subcommand for M0–M5. The config is a JSON file; users edit it directly. A `config` subcommand adds surface area without clear benefit. Revisit if non-technical users become a target audience.

**Blocking impact.** None for M0–M5.