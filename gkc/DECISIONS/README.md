# GKC — Decisions Index

This directory holds **ADR candidates** (surfaced by DESIGN docs, awaiting ratification) and **ratified ADRs** (decisions that govern the implementation).

## Ratified ADRs

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](0001-name-and-scope.md) | GKC Name and Scope | Ratified |

## ADR Candidates (by source DESIGN doc)

| Source | Candidates | Blocking milestone |
|---|---|---|
| [001 Vision](001-vision-adr-candidates.md) | 0001–0010 (self-describing IR, context stage, plugin recovery, snapshots, validator, network, warm cache, hardware, authority tie-break, reference agent) | M0–M3 |
| [002 Domain Model](002-domain-model-adr-candidates.md) | 0011–0018 (authority stratification, multi-version registry, repo identity, context payload, plugin scope, diagnostic ids, kind extensibility, ontology namespaces) | M0–M2 |
| [003 Component Architecture](003-component-architecture-adr-candidates.md) | 0019–0023 (budget allocation, plugin sandbox, indexer as stage, plugin deps, storage transactions) | M0–M5 |
| [004 Data Model](004-data-model-adr-candidates.md) | 0024–0028 (identifier index, partial loading, search index, closure depth, compression) | M0–M3 |
| [005 Pipeline](005-pipeline-adr-candidates.md) | 0029–0033 (context stage, partial snapshots, stage cache sharing, cached diagnostics, retry) | M0–M3 |
| [006 Query Engine](006-query-engine-adr-candidates.md) | 0034–0038 (pagination, streaming, cross-session cache, plugin mutations, programmatic API) | M2 |
| [007 Context Compiler](007-context-compiler-adr-candidates.md) | 0039–0043 (multi-turn, tool definitions, interactive, eager sufficiency, compression digest) | M3 |
| [008 Plugin Framework](008-plugin-framework-adr-candidates.md) | 0044–0048 (hot-reload, signatures, built-ins as plugins, per-plugin policy, priority field) | M0 |
| [009 CLI](009-cli-adr-candidates.md) | 0049–0053 (serve mode, streaming, diff, completion, config subcommand) | M0–M5 |
| [010 Storage](010-storage-adr-candidates.md) | 0054–0058 (encryption, manifest signing, dedup, cross-version cache, multi-write tx) | M0 |
| [011 Testing](011-testing-adr-candidates.md) | 0059–0063 (fuzzing, snapshot testing, coverage enforcement, perf scope, model pinning) | M0–M3 |
| [012 Reference Implementation](012-reference-implementation-adr-candidates.md) | 0010–0011, 0064–0066 (implementation language, distribution, repo location, formal verification, watch mode) | M0–M5 |

## ADR Process

1. A DESIGN doc surfaces a decision as a candidate in its `DECISIONS/00N-*-adr-candidates.md` file.
2. The candidate is reviewed (per the corresponding `REVIEWS/00N-*.md`).
3. Ratified candidates become ADRs (moved or copied to `DECISIONS/ADR-XXXX.md` with status `Ratified`).
4. ADRs are numbered sequentially from 0001.
5. ADRs are immutable once ratified; supersession requires a new ADR.

## Blocking ADRs for M0

The following must be ratified before M0 implementation begins:

- **ADR-0010** — Implementation language (from 012-adr-candidates)
- **ADR-0003** — Plugin failures recoverable per-artifact (from 001-adr-candidates)
- **ADR-0004** — Complete snapshots only (from 001-adr-candidates)
- **ADR-0006** — Network access definition (from 001-adr-candidates)
- **ADR-0015** — Plugins per-workspace (from 002-adr-candidates)
- **ADR-0031** — Stage cache per-workspace (from 005-adr-candidates)
- **ADR-0033** — No stage retry (from 005-adr-candidates)
- **ADR-0044** — No hot-reload (from 008-adr-candidates)
- **ADR-0045** — Hash-only integrity (from 008-adr-candidates)
- **ADR-0046** — Built-ins as internal plugins (from 008-adr-candidates)
- **ADR-0047** — Workspace-level capability policy (from 008-adr-candidates)
- **ADR-0048** — Priority field in manifest (from 008-adr-candidates)
- **ADR-0049** — No serve mode (from 009-adr-candidates)
- **ADR-0056** — No snapshot dedup (from 010-adr-candidates)
- **ADR-0057** — GKC version in cache key (from 010-adr-candidates)
- **ADR-0058** — No multi-write transactions (from 010-adr-candidates)
- **ADR-0061** — Soft coverage fail (from 011-adr-candidates)
- **ADR-0064** — Same-repo implementation (from 012-adr-candidates)

Most of these have clear recommendations in their candidate files; ratification is expected to be quick.