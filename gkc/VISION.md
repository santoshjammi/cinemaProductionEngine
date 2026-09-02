# GKC Vision

## Why GKC Exists

Architectures decay. Not because the ideas are wrong, but because the **knowledge** in them is not executable. A constitution written in prose can be read, admired, and ignored. A runtime described in a spec can be implemented, drifted from, and forgotten. The gap between *what the architecture says* and *what the repository actually contains* is where every failure mode of long-lived software lives.

GKC exists to **close that gap by compilation**.

It treats a repository not as a pile of files, but as a **body of architectural knowledge** that can be parsed, classified, resolved, graphed, indexed, and re-emitted as machine-reasonable artifacts: registries, graphs, ontologies, and context packages. Those artifacts become the substrate that AI agents, IDEs, validators, and future runtimes consume.

---

## Why Architecture Must Become Executable

The GENESIS architecture (`000`–`018`) is a constitutional stack — 19 documents that fix the platform's ontology, runtime, governance, and developer surface. That stack is now frozen. Its job is to *be correct*. But correctness at the architectural layer does not propagate automatically to the engineering layer. Without a compiler:

- a registry drifts from the metadata architecture,
- a runtime drifts from the platform architecture,
- governance drifts from the constitution,
- agents drift from the ontology,
- and every AI coding session starts from scratch because there is no canonical context to hand it.

Compilation is the only mechanism that turns architectural invariants into engineering invariants *without relying on humans to remember them*. GKC is that compiler.

---

## Relationship to GENESIS

GENESIS is the **constitution**. GKC is the **statute law** — the operational body of rules that enforces and uses the constitution inside a specific repository.

| GENESIS | GKC |
|---|---|
| Specifies what an architecture is | Compiles what an architecture means in a given repository |
| Frozen, constitutional | Evolving, engineering |
| Documents `000`–`018` | Design package `001`–`012` |
| Read by humans, referenced by machines | Read by machines, supervised by humans |
| Authority | Operationalization |

If GKC behavior conflicts with a GENESIS document, **the GENESIS document wins**. GKC must then either change its behavior or surface an ADR requesting a constitutional amendment. GKC never silently overrides GENESIS.

---

## Relationship to AIOS

AIOS — the AI Operating System — is the downstream consumer. It schedules agents, plans work, routes prompts, and governs execution. AIOS cannot do any of that without a **knowledge substrate**: a queryable, versioned, validated view of the repository's architectural meaning.

GKC produces that substrate. AIOS consumes it.

```
GENESIS  ──frozen──►  GKC  ──compiles──►  Knowledge Substrate  ──consumed by──►  AIOS
```

GKC is therefore the **first executable component of GENESIS** and the **last component AIOS needs before it can run**. Everything between is engineering.

---

## Repository Intelligence

"Repository intelligence" is the **machine-understandable meaning** of a repository: what each artifact is, what authority it carries, what it depends on, what ontology it instantiates, and what context it contributes to any given query.

GKC produces repository intelligence through a fixed compilation pipeline (see `DESIGN/005`):

```
Repository → Scanner → Metadata → Resolver → Registry
         → Graphs → Ontology → Context → Query
```

Each stage is deterministic, cacheable, and incrementally re-runnable. Repository intelligence is not a snapshot — it is a **recompilable artifact** that tracks the repository's evolution.

---

## Knowledge Compilation

GKC is a compiler in the strict sense. Its source language is *repository content*; its target language is *machine-reasonable knowledge*.

Compiler analogues:

| LLVM | GKC |
|---|---|
| Source language (C++, Rust, ...) | Repository content (prose, code, manifests, metadata) |
| Frontend (parser, AST) | Scanner + Parser + Metadata |
| IR (LLVM IR) | Registry + Graphs + Ontology (the *Knowledge IR*) |
| Optimizer (passes) | Resolver, Context Compiler, Validation |
| Backend (codegen) | Query Engine, Context Emitter, CLI, Plugin providers |
| Linker | Composition of multiple registries / snapshots |

This framing is not decorative. It commits GKC to compiler properties: **determinism, staging, cacheability, incremental compilation, diagnosable errors, and language-agnostic frontends.** Every DESIGN doc inherits these properties.

---

## Machine Understanding

"Understanding" is overloaded. GKC does not claim a repository *means* anything in a human sense. It claims a repository can be reduced to a **set of typed, referenced, graphed facts** that an agent can reason over without re-reading the repository.

Machine understanding, as GKC defines it, is the **closure of four relationships** over a repository's artifacts:

1. **Classification** — what kind of artifact is this? (document, schema, runtime, contract, ...)
2. **Authority** — what architectural weight does it carry? (constitution, statute, guidance, deprecated, ...)
3. **Dependency** — what does it structurally depend on, and what depends on it?
4. **Ontology** — what domain concepts does it define or reference?

A repository is "understood" by GKC when all four closures are complete, consistent, and queryable. Anything less is partial compilation; GKC surfaces it as a diagnostic, not a silent gap.

---

## Success Criteria

GKC has succeeded when **all** of the following hold:

1. **A clean repository compiles end-to-end** with zero diagnostics and a fully populated registry, both graphs, and a queryable ontology.
2. **A drifting repository produces ranked diagnostics** that name the offending artifact, the violated GENESIS invariant, and the suggested resolution.
3. **An AI agent can request context for any task** and receive a token-bounded, dependency-closed, authority-aware package that is sufficient to perform the task without reading the repository directly.
4. **A developer can answer any architectural question from the CLI** in under one second on a warm cache, without opening a file.
5. **A plugin can extend GKC** without forking the compiler — adding a new artifact kind, a new graph edge, or a new context strategy via the plugin framework alone.
6. **A fresh checkout compiles in O(repository size)** with reproducible output across machines, hosts, and timestamps.
7. **AIOS can boot against GKC's output** without an additional knowledge-acquisition step.

---

## Non-Goals

GKC explicitly does **not** aim to:

- **Be an LLM.** GKC compiles; it does not generate. Generation is the runtime's job.
- **Be an agent.** GKC produces the substrate agents consume; it does not schedule, plan, or act.
- **Be an IDE.** GKC exposes a CLI and a query contract; IDEs are built on top of it.
- **Be a runtime.** GKC does not execute architectures; PROMETHEUS does.
- **Be a validator of prose meaning.** GKC validates *architectural conformance*, not whether a document is well-written.
- **Replace GENESIS.** GKC operationalizes GENESIS; it does not amend it.
- **Be a general-purpose knowledge graph.** GKC's graph is scoped to architectural knowledge inside repositories, not open-world knowledge.
- **Be language-specific.** GKC's frontend is pluggable; no host language is privileged.

---

## Future Evolution

GKC is designed to outgrow its name. Today it compiles repository knowledge; the architecture already anticipates compiling:

| Horizon | Compilable domain | What GKC adds |
|---|---|---|
| Now | Repository artifacts | Scanner, registry, graphs, context |
| Near | Ontologies and schemas | First-class ontology compilation, schema linking |
| Mid | Contracts and policies | Contract compilation, policy enforcement at compile time |
| Mid | Prompts and prompt templates | Prompt-as-artifact, prompt-context fusion |
| Far | Runtime knowledge and traces | Runtime observability feeding back into registry |
| Far | Cross-repository knowledge | Federated registries, cross-repo authority |

Because the architecture separates *what is compiled* (the frontend) from *how it is compiled* (the pipeline) and *what is emitted* (the IR + backends), each horizon is an additive extension, not a redesign. The product name — **GENESIS Knowledge Compiler** — was chosen precisely so the name does not have to change when the compilable domain grows.

---

## Naming

GKC was originally drafted as **RIC — Repository Intelligence Compiler**. The name was retired because the scope already exceeds "repository intelligence" at design time: GKC compiles *knowledge*, of which repository intelligence is the first domain. See `DECISIONS/0001-name-and-scope.md`.

---

## See Also

- `ARCHITECTURE.md` — system architecture and the map to DESIGN docs.
- `ROADMAP.md` — milestones from M0 (skeleton) to M5 (AIOS integration).
- `DESIGN/001-vision.md` — the engineering-grade vision document (this file is the product-level companion).
- `DESIGN/005-pipeline.md` — the compilation pipeline that makes the vision executable.
- `DESIGN/007-context-compiler.md` — the flagship: how GKC builds context for AI agents.