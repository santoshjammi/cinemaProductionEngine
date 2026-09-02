# ADR Candidates — GKC-007 Context Compiler

> Decisions surfaced by `DESIGN/007-context-compiler.md`.

---

## ADR-Candidate-0039 — Multi-turn task support

**Context.** § 3 models a task as a single TaskDescriptor. Should the compiler support multi-turn conversations?

**Options.**
- **A. No.** Each `gkc context` call is independent; the caller maintains conversation state.
- **B. Yes, via a session id.** The compiler maintains conversation state; each call extends the package.
- **C. Yes, via a growing task descriptor.** The caller appends prior turns to the descriptor; the compiler treats it as one large task.

**Recommendation.** A for M3. No multi-turn. The caller (AIOS, IDE) is better positioned to maintain conversation state. GKC's contract is per-task. A later horizon can revisit B if real usage demands it.

**Blocking impact.** Blocks M3. Must be resolved before M3.

---

## ADR-Candidate-0040 — Tool definitions in the package

**Context.** For tool-use-capable LLMs, should the package include tool definitions (e.g., "you can call `gkc explain` for more context")?

**Options.**
- **A. No.** The package is pure context; tools are the agent runtime's concern.
- **B. Yes, in a dedicated `tool-definitions` slice.** The package includes tool definitions the agent can call back.
- **C. Configurable per model profile.** `tool_use: true` profiles get tool definitions; others don't.

**Recommendation.** C. Configurable. Tool-use models benefit from tool definitions; non-tool models don't. The model profile (§ 9.3) already carries `tool_use`; reusing it is clean. The `markdown` and `local-llm` providers omit tool definitions; `anthropic-xml` and `openai-json` include them when `tool_use: true`.

**Blocking impact.** Blocks M3 provider implementation. Must be resolved before M3.

---

## ADR-Candidate-0041 — Interactive context (agent pulls more)

**Context.** Should the compiler support an interactive mode where the agent requests more context mid-task?

**Options.**
- **A. No.** One-shot compilation; the agent works with what it gets.
- **B. Yes, via a follow-up call.** The agent calls `gkc context --extends=<prev-package-id> --focus="<new focus>")`.
- **C. Yes, via a long-running session.** A `gkc context serve` mode with streaming.

**Recommendation.** A for M3; revisit B at M5. One-shot matches the compiler model and is simpler. B is appealing but adds session state and cache complexity. C is a post-M5 evolution.

**Blocking impact.** Blocks M3. Must be resolved before M3.

---

## ADR-Candidate-0042 — Eager sufficiency test

**Context.** Should the sufficiency test (§ 13) run eagerly (in-pipeline) or only on demand?

**Options.**
- **A. On demand only.** The test runs when the user invokes `gkc context --verify`.
- **B. Eager, in-pipeline.** Every context compile runs the sufficiency test; failure blocks the package.
- **C. Eager for golden tasks; on demand otherwise.** Hybrid.

**Recommendation.** A. On demand. Eager testing couples context compilation to a reference agent (an LLM or stub), violating the "no LLM calls in the compiler" constraint (per the prompt) and adding latency. The test is a verification tool, not a pipeline stage.

**Blocking impact.** Blocks M3 sufficiency harness. Must be resolved before M3.

---

## ADR-Candidate-0043 — Compression digest in the package

**Context.** Should the package metadata include a digest of what was dropped (so the agent knows what it doesn't know)?

**Options.**
- **A. No.** The agent works with what it has; dropped slices are in the metadata for the caller, not the agent.
- **B. Yes, in a `dropped-summary` slice.** A short summary of dropped content is included for the agent.
- **C. Configurable.** `--include-dropped-summary` flag.

**Recommendation.** C. Configurable, default off. The metadata already records dropped slices (§ 10.2) for the caller. Including a summary in the agent-facing content helps the agent know to ask for more, but adds tokens. Make it opt-in.

**Blocking impact.** Blocks M3 package assembly. Must be resolved before M3.