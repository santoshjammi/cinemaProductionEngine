# GKC-007 — Context Compiler

> **The flagship document.** This is what makes GKC valuable to AI agents. Everything else in GKC produces the substrate; this document defines how that substrate becomes a payload an agent can actually use.

---

## 1. Purpose

Define the Context Compiler (C11) as the component that **slices the compiled IR into a token-bounded, dependency-closed, authority-aware package** that an AI agent, IDE, or runtime can consume to perform a task without reading the repository directly.

After this document, `gkc context --task="..."` is implementable without ambiguity, and the package it produces is **provably sufficient** for the task (per the sufficiency test in § 11).

This document defines:

- the **context compilation pipeline** (slice → expand → budget → emit),
- **repository slicing** (how the IR is cut into candidate slices),
- **semantic filtering** (how slices are selected for a task),
- **dependency expansion** (how slices are closed under dependencies),
- **authority expansion** (how higher-authority artifacts are preferred),
- **prompt optimization** (how the package is laid out for an LLM),
- **token optimization** (how the package fits a budget),
- **caching and incremental updates**,
- **LLM independence** (how the same substrate serves any model),
- **sufficiency** (how we know a package is enough).

---

## 2. Why This Is the Hardest Problem in GKC

Every other stage in GKC is a function from data to data. The Context Compiler is a function from **(data, intent, constraint)** to data. The intent (task descriptor) is underspecified. The constraint (token budget) is adversarial. The output must be **sufficient** for an external system whose behavior GKC does not control.

Three failure modes make this hard:

1. **Insufficiency.** The package omits something the agent needs; the agent hallucinates or fails.
2. **Bloat.** The package includes irrelevant material; the agent's attention is diluted; context window wasted.
3. **Drift.** The package includes a low-authority artifact that contradicts a high-authority one; the agent follows the wrong one.

The design in this document addresses all three explicitly.

---

## 3. Context Compilation Pipeline

```
TaskDescriptor + TokenBudget + Snapshot
        │
        ▼
┌─────────────────────────┐
│ 1. Slice Selection      │   pick candidate slices from the IR
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 2. Semantic Filtering   │   score slices against the task
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 3. Dependency Expansion │   close under hard dependencies
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 4. Authority Expansion  │   pull in higher-authority artifacts
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 5. Budget Allocation    │   assign token budgets per slice
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 6. Rendering             │   emit each slice through a provider
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ 7. Package Assembly     │   order slices; attach metadata
└────────────┬────────────┘
             ▼
   Context Package (cached)
```

Each stage is defined below. Stages 1–4 are **pure functions** over the IR; stages 5–7 depend on the budget and the provider. The whole pipeline is **deterministic** for a fixed `(task, snapshot, budget, provider)`.

---

## 4. Slice Selection

### 4.1 Slice kinds

A slice is a typed unit of context. The kinds are:

| Kind | What it contains | When selected |
|---|---|---|
| `overview` | Repository overview: counts, top-level kinds, authority distribution | Always (one per package) |
| `artifact` | One registry entry: identity, metadata, content excerpt | When the entry is in the candidate set |
| `graph-excerpt` | A subgraph around a focal artifact | When traversal is needed to explain relationships |
| `definition` | An ontology node: term, namespace, definition | When the task references a concept |
| `diagnostic` | A ranked list of relevant diagnostics | When the affected artifacts are in the candidate set |
| `authority-chain` | The chain of authority above an artifact | When authority matters for the task |

### 4.2 Candidate set construction

The candidate set is built from the TaskDescriptor:

1. **Target artifacts** (from `target_artifacts` in the descriptor) → `artifact` slices.
2. **Target concepts** (from `target_concepts`) → `definition` slices + `artifact` slices for each artifact that declares those concepts.
3. **Full-text search** over the descriptor's `description` → top-N `artifact` slices (N is configurable; default 20).
4. **Authority traversal** from targets → `authority-chain` slices.
5. **Diagnostics** for any artifact in the candidate set → `diagnostic` slices.

The candidate set is **over-inclusive** at this stage; stages 2–5 narrow and prioritize it.

### 4.3 Slice identity

A slice's identity is `(kind, focal_artifact_id or focal_concept or "overview")`. Two slices with the same identity are merged.

---

## 5. Semantic Filtering

### 5.1 Relevance score

Each candidate slice gets a relevance score in `[0, 1]`:

- **`artifact` slice**: cosine similarity (or BM25, per ADR-Candidate-0026) between the task description and the artifact's content + metadata; multiplied by an authority weight (per § 5.2).
- **`definition` slice**: 1.0 if the task references the concept; 0.0 otherwise.
- **`graph-excerpt` slice**: 0.5 (neutral; kept if the focal artifact's score is above threshold).
- **`overview` slice**: always 1.0 (kept).
- **`diagnostic` slice**: 1.0 if the affected artifact is in the candidate set; 0.0 otherwise.
- **`authority-chain` slice**: 0.7 (kept if the focal artifact's score is above threshold).

### 5.2 Authority weight

The relevance score is multiplied by the authority weight:

| Authority level | Weight |
|---|---|
| `constitutional` | 1.5 |
| `statutory` | 1.2 |
| `guidance` | 1.0 |
| `deprecated` | 0.5 |
| `unknown` | 0.8 |

This implements "authority wins" (per `DESIGN/001` § 8.3) at the slice level.

### 5.3 Threshold

Slices with a weighted relevance below a configurable threshold (default 0.1) are dropped. The threshold is exposed via `--relevance-threshold` on the CLI.

---

## 6. Dependency Expansion

### 6.1 The dependency-closure invariant

> **Every artifact in the package has all its hard dependencies either included or transitively reachable from included slices.**

This invariant prevents insufficiency: an agent that needs artifact A also needs what A depends on.

### 6.2 Closure computation

For each `artifact` slice in the candidate set:

1. Compute the hard-dependency closure (using the dependency closure index, `DESIGN/004` § 6.5) up to a configurable depth (per ADR-Candidate-0027).
2. For each artifact in the closure, add an `artifact` slice if not already present.
3. Repeat until the closure is complete or the depth limit is hit.

### 6.3 Depth limits and escape hatches

- Default depth: 3.
- If the closure exceeds a configurable size (default 100 artifacts), the compiler stops expanding and emits a `closure-truncated` info diagnostic.
- The package's metadata records which artifacts' closures were truncated, so consumers know what might be missing.

### 6.4 Soft dependencies

Soft dependencies are **not** expanded by default. The task descriptor may request soft expansion via `expand_soft: true`.

---

## 7. Authority Expansion

### 7.1 The authority-preference invariant

> **If two artifacts cover the same concept, the higher-authority one is preferred under budget pressure.**

### 7.2 Authority expansion step

For each `artifact` slice in the candidate set:

1. Walk the authority chain upward (toward higher authority).
2. For each higher-authority artifact that covers the same concept, add it as an `artifact` slice.
3. Mark these as `authority-preferred` in the slice metadata.

This ensures the package includes the *constitutional* definition of a concept, not just a *guidance* document that mentions it.

### 7.3 Conflict detection

If two artifacts in the candidate set cover the same concept with conflicting definitions (per the ontology compiler's conflict detection), the compiler:

1. Keeps the higher-authority one.
2. Drops the lower-authority one **unless** the task explicitly references it.
3. Emits a `context-conflict` info diagnostic naming both artifacts.

---

## 8. Budget Allocation

### 8.1 The budget-allocation invariant

> **The package's total token count is ≤ the token budget. The allocation across categories is deterministic for a fixed `(task, snapshot, budget)`.**

### 8.2 Tiered allocation (per ADR-Candidate-0019)

The budget is allocated in tiers:

1. **Reserved categories** (allocated first):
   - `overview`: 500 tokens (or 5% of budget, whichever is smaller).
   - `diagnostics`: 200 tokens (or 2%, whichever is smaller).
2. **Core categories** (allocated by relevance × authority):
   - `artifact`: 60% of remaining budget.
   - `definition`: 10% of remaining.
   - `graph-excerpt`: 15% of remaining.
   - `authority-chain`: 15% of remaining.
3. **Overflow policy** (if a category exceeds its allocation):
   - Default: `drop-lowest-authority` — drop slices with the lowest authority first, then lowest relevance.
   - Configurable: `truncate` (truncate slice content), `summarize` (replace content with a one-line summary), `fail` (emit an error if the package cannot fit).

### 8.3 Slice ranking within a category

Within each category, slices are ranked by `(relevance × authority_weight, authority_level, id)`. Higher-ranked slices are kept; lower-ranked slices are dropped first under budget pressure.

### 8.4 Token accounting

- Each slice's token count is computed by the provider (per § 9.2) before budget allocation, using a fast approximation (e.g., `chars / 4`).
- The package's `total_tokens` is the sum of included slices' token counts.
- The package's metadata records the budget, the allocation, and any dropped slices.

### 8.5 Budget too small

If the budget is too small for the `overview` + `diagnostics` reservations, the compiler emits an `error` diagnostic and produces an empty package. The threshold is configurable (default: 100 tokens).

---

## 9. Rendering and Provider Framework

### 9.1 Provider interface

A provider is a function `(Slice, ModelProfile) → RenderedSlice` where `RenderedSlice` is `{ content: string, tokens: int, format: string }`.

### 9.2 Built-in providers

| Provider id | Format | Use case |
|---|---|---|
| `markdown` | Markdown | Default; works with all LLMs |
| `anthropic-xml` | Anthropic-style XML | Anthropic models |
| `openai-json` | JSON in OpenAI format | OpenAI models |
| `local-llm` | Plain text with section markers | Local LLMs with limited context |

### 9.3 Model profile

The model profile (from the task descriptor) tells the provider:

- `context_window` — total tokens the model accepts.
- `output_reservation` — tokens reserved for the model's output.
- `tool_use` — whether the model supports tool use (affects whether we include tool-use hints).
- `token_estimator` — which estimator to use (per § 8.4).

The available budget is `context_window - output_reservation`.

### 9.4 Provider selection

The task descriptor's `requested_format` selects the provider. If unspecified, the compiler picks based on the model profile:

- Anthropic model → `anthropic-xml`.
- OpenAI model → `openai-json`.
- Local model → `local-llm`.
- Unknown → `markdown`.

### 9.5 Provider failure

If the selected provider throws, the compiler falls back to `markdown` with a `provider-fallback` marker in the package metadata.

### 9.6 Plugin providers

Plugins can register new providers (per `DESIGN/008` § context provider extension point).

---

## 10. Package Assembly

### 10.1 Slice ordering

Slices are ordered in the package as:

1. `overview` (always first).
2. `definition` slices (concepts first, so the agent has vocabulary).
3. `authority-chain` slices (so the agent knows the authority context).
4. `artifact` slices (ranked by relevance × authority).
5. `graph-excerpt` slices (so the agent sees relationships).
6. `diagnostic` slices (last; so the agent can act on them).

Within each category, slices are ordered by their rank.

### 10.2 Package metadata

The package carries metadata (not part of the rendered content):

- `task_hash`, `snapshot_id`, `budget`, `provider_id` (the identity tuple).
- `total_tokens`, `allocation` (per-category token counts).
- `dropped_slices` (list of slice ids that were dropped, with reason).
- `closure_truncations` (artifacts whose dependency closure was truncated).
- `conflicts` (concept conflicts detected during authority expansion).
- `cache_key` (for cache lookup).

### 10.3 Package emission

The package is emitted as a single payload (per ADR-Candidate-0014) by default. Streaming providers can be added as plugins (per ADR-Candidate-0014 option C).

---

## 11. Caching and Incremental Updates

### 11.1 Cache key

The cache key is the package's identity tuple: `(task_hash, snapshot_id, budget, provider_id)`. A cache hit returns byte-identical package.

### 11.2 Cache invalidation

A cached package is invalidated when:

- The underlying snapshot is GC'd.
- The provider version changes.
- The user runs `gkc cache clear --context`.

### 11.3 Incremental updates

When a snapshot is updated (incremental compile), the context compiler:

1. Identifies which artifacts in the cached package's slices changed.
2. Re-builds only the affected slices.
3. Re-runs budget allocation if the affected slices' token counts changed.
4. Produces a new package (new cache key, since `snapshot_id` changed).

The old package remains in the cache until LRU eviction.

### 11.4 Warm-cache latency

Per `DESIGN/001` § 6, a second `gkc context` call for the same task on an unchanged repository returns in under 100 ms from cache. Verified by `DESIGN/011` performance tests.

---

## 12. LLM Independence

### 12.1 The LLM-independence invariant

> **The same IR produces packages for any LLM via provider selection. The substrate does not favor one model family.**

### 12.2 How it's achieved

- The IR is provider-agnostic.
- The provider is selected per task.
- The model profile carries model-specific parameters.
- No provider leaks its format into the IR or the cache key (the cache key includes `provider_id`, so different providers have different cache entries).

### 12.3 Local LLM parity

Per `DESIGN/001` § 8.6, the substrate must serve local LLMs (limited context, no tool use) and frontier LLMs (large context, tool use) from the same IR. The `local-llm` provider:

- Aggressively truncates content to fit small windows.
- Uses plain text with section markers (no XML/JSON).
- Omits tool-use hints.

The same task, run against the same snapshot with different providers, produces **semantically equivalent** packages (same artifacts, same ordering, different rendering). Verified by the sufficiency test in § 13.

---

## 13. Sufficiency Test

### 13.1 The sufficiency invariant

> **A reference agent, given only the context package, can answer repository questions about the task correctly.**

### 13.2 Test methodology

For each task in a golden task set:

1. Compile the context package.
2. Hand the package to a reference agent (per ADR-Candidate-0010: stub, local LLM, frontier LLM).
3. Ask the agent a set of questions whose answers are derivable from the package.
4. Verify the agent's answers are correct.

If any agent fails, the package is **insufficient**. The compiler emits a `sufficiency-test-failed` diagnostic naming the missing slice.

### 13.3 Golden task set

The golden task set is maintained in `IMPLEMENTATION/golden-tasks.md` and includes:

- "Explain artifact X."
- "What does artifact X depend on?"
- "What is the authority chain for artifact X?"
- "Find artifacts that conflict with artifact X."
- "What concepts does artifact X introduce?"
- "What are the open diagnostics against artifact X?"

The set grows as engineering proceeds; each new task type is added with a known-good answer.

### 13.4 Sufficiency is not a guarantee

The sufficiency test verifies the package **can** support correct answers; it does not guarantee any specific agent **will** answer correctly. GKC's contract is about the package, not the agent.

---

## 14. Failure Modes

| Failure | Behavior |
|---|---|
| Budget too small | `error` diagnostic; empty package |
| Provider exception | Fallback to `markdown`; `provider-fallback` marker |
| Required index unavailable | `error` diagnostic; package not built |
| Snapshot not found | Typed error: `snapshot-not-found` |
| Task descriptor invalid | Typed error: `invalid-task-descriptor` |
| Closure exceeds limit | `closure-truncated` info; package built with truncated closure |
| Conflict between same-concept artifacts | `context-conflict` info; lower-authority dropped unless explicitly referenced |

---

## 15. Extension Points

| Extension point | What plugins add |
|---|---|
| Context provider | New output formats |
| Slice selector | New slice kinds or selection strategies |
| Relevance scorer | New scoring algorithms (e.g., embedding-based) |
| Budget allocator | New allocation policies |
| Sufficiency tester | New test methodologies |

All extension points are registered via the plugin framework (per `DESIGN/008`).

---

## 16. Open Questions for ADR

Surfaced in `DECISIONS/007-context-compiler-adr-candidates.md`:

1. Should the context compiler support multi-turn tasks (a conversation, not a single task)?
2. Should the package include "tool definitions" for tool-use-capable LLMs?
3. Should the compiler support "interactive" context (the agent asks for more, GKC extends the package)?
4. Should the sufficiency test be run eagerly (in-pipeline) or only on demand?
5. Should the package include a "compression digest" (a summary of what was dropped)?