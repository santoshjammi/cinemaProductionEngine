# 018 — GENESIS Developer Platform

**Status:** Platform Engineering Specification — Phase III
**Version:** 1.0.0
**Date:** 2026-07-21
**Derives Authority From:** `006` (Constitution); `013` (Repository); `014` (Governance Engine); `015` (Registry); `016` (Metadata); `017` (Validation Rules).
**Precedence:** Below the Constitution. This specification defines the **GENESIS Developer Platform** — the engineering tooling that makes the architecture usable by engineers and AI agents.
**Scope:** Developer philosophy, CLI architecture, repository tooling, architecture linting, graph generation, specification validation, dependency visualization, architecture reports, documentation generation, AI integration, IDE integration, automation, developer workflows, future extensibility.

---

## Table of Contents

1. [Philosophy](#1-philosophy)
2. [Objectives](#2-objectives)
3. [Principles](#3-principles)
4. [Architecture](#4-architecture)
5. [Components](#5-components)
6. [Responsibilities](#6-responsibilities)
7. [Governance](#7-governance)
8. [Lifecycle](#8-lifecycle)
9. [Integration](#9-integration)
10. [Migration](#10-migration)
11. [Future Evolution](#11-future-evolution)

---

# 1. Philosophy

## 1.1 The Architecture Must Be Usable

A constitutional architecture that cannot be operated is a document, not a platform. The GENESIS Developer Platform is the engineering layer that makes the ACI Platform's architecture **usable**: it provides the tooling through which engineers and AI agents discover, navigate, validate, author, and govern the architecture's artifacts.

The Developer Platform is not a creative system; it has no creative authority (`006` Part 4). It is not a governance system; it has no governance authority (`006` Part 7). It is a **tool layer** that operates on the repository (`013`), via the Registry (`015`), using the metadata (`016`), enforcing the rules (`017`), through the Governance Engine (`014`).

## 1.2 Constitutional Derivation

| Law | How it governs the Developer Platform |
|-----|--------------------------------------|
| L-22 (Amendments Require Process) | The platform's tooling for authoring artifacts enforces the governance process. |
| L-25 (Human Supremacy) | The platform's automation does not override human authority; AI-assisted authoring requires human review. |

---

# 2. Objectives

| # | Objective |
|---|-----------|
| O-1 | **Discovery**: engineers and AI agents can discover artifacts via the Registry (015). |
| O-2 | **Validation**: engineers can validate artifacts via the Governance Engine (014). |
| O-3 | **Visualization**: engineers can visualize the authority graph, dependency graph, and repository structure. |
| O-4 | **Authoring**: engineers and AI agents can author artifacts with metadata (016) and governance compliance. |
| O-5 | **Automation**: routine operations (metadata backfill, naming normalization, drift detection) are automated. |
| O-6 | **AI-native**: AI agents can use the platform to operate on the architecture without human guidance for routine operations. |
| O-7 | **IDE integration**: the platform integrates with development environments for real-time validation and navigation. |

---

# 3. Principles

| # | Principle |
|---|-----------|
| DP-1 | **The platform is a consumer, not a system.** The platform consumes the Registry (015) and the Governance Engine (014); it does not define its own architecture. |
| DP-2 | **The platform has no authority.** The platform is a tool; it does not decide, does not govern, does not create. |
| DP-3 | **The platform is runtime-independent.** The platform's tooling operates on architectural artifacts, which are runtime-independent. |
| DP-4 | **The platform is AI-native.** The platform's interfaces are machine-usable, enabling AI agents to operate alongside engineers. |

---

# 4. Architecture

## 4.1 The CLI Architecture

The Developer Platform's primary interface is a **CLI (Command Line Interface)** — the `genesis` command (or equivalent), with subcommands for each tool:

| Command | What it does |
|---------|-------------|
| `genesis discover <query>` | Queries the Registry (015) for artifacts. |
| `genesis validate [artifact]` | Runs the Governance Engine (014) on an artifact or the whole repository. |
| `genesis graph [type]` | Generates a visualization of the authority graph, dependency graph, or repository structure. |
| `genesis lint [artifact]` | Runs architecture linting: checks naming, metadata, cross-references. |
| `genesis report [type]` | Generates an architecture report (compliance, drift, dependency, authority). |
| `genesis docs [artifact]` | Generates documentation from an artifact's metadata and content. |
| `genesis author <type>` | Scaffolds a new artifact with a metadata header (016). |
| `genesis review <artifact>` | Scaffolds an architecture review for an artifact. |
| `genesis adr <title>` | Scaffolds a new ADR. |

The CLI is the engineer's and AI agent's primary interface. The CLI's commands are thin wrappers around the Registry, the Governance Engine, and the platform's generators.

## 4.2 Repository Tooling

| Tool | What it does |
|------|-------------|
| **Metadata Backfill Tool** | Adds metadata headers (016) to existing documents. |
| **Naming Normalization Tool** | Renames documents per the naming convention (013 Part 4.4). |
| **Cross-Reference Checker** | Verifies that all cross-references in documents point to existing artifacts. |
| **Drift Detector** | Runs the Governance Engine's drift detection (014 Part 4.3) on the repository. |

## 4.3 Architecture Linting

Architecture linting is the lightweight, fast validation of artifacts against the naming, metadata, and reference rules (017 Parts 4.7–4.8). Linting runs on every commit (via CI integration) and produces findings (warnings and advisories; blocking findings are escalated to the Governance Engine).

## 4.4 Repository Graph Generation

The platform generates visualizations of:

| Graph | What it visualizes |
|-------|-------------------|
| **Authority graph** | Which artifact derives authority from which (015 Part 4.3). |
| **Dependency graph** | Which artifact depends on which (015 Part 4.4). |
| **Repository structure** | The directory taxonomy and document hierarchy (013 Part 4.2). |
| **Ownership graph** | Which body owns which directory (013 Part 4.3). |

Graphs are generated from the Registry (015) and rendered as diagrams (the rendering format is an implementation concern).

## 4.5 Specification Validation

The platform provides full specification validation via the Governance Engine (014):

| Validation type | What it validates |
|-----------------|-------------------|
| **Constitutional** | Law compliance (017 Part 4.2). |
| **Architectural** | Specification compliance (017 Part 4.3). |
| **Semantic** | COM invariant compliance (017 Part 4.3). |
| **Repository** | Structure and metadata (017 Part 4.7). |

## 4.6 Dependency Visualization

The platform visualizes dependency relationships:

- **Forward dependencies**: what does this artifact depend on?
- **Reverse dependencies**: what depends on this artifact?
- **Impact analysis**: if this artifact changes, what is affected?

## 4.7 Architecture Reports

The platform generates reports:

| Report | Content |
|--------|---------|
| **Compliance report** | The Governance Engine's findings for the repository or an artifact. |
| **Drift report** | Detected architecture drift (014 Part 4.3). |
| **Dependency report** | An artifact's dependencies and dependents. |
| **Authority report** | An artifact's authority chain (up to the Constitution). |
| **Coverage report** | Which artifacts have reviews, ADRs, and metadata. |

## 4.8 Documentation Generation

The platform generates documentation from artifacts' metadata and content:

- **Architecture overview**: a generated document describing the repository's structure and the authority graph.
- **Artifact index**: a generated index of all artifacts, their types, statuses, and versions.
- **Cross-reference map**: a generated map of all cross-references between artifacts.

Generated documentation is marked as derived (not authoritative); the source artifacts are authoritative.

## 4.9 AI Integration

The platform is AI-native: AI agents use the platform's CLI and Registry to operate on the architecture. AI agent operations:

| Operation | AI agent capability | Human oversight |
|-----------|---------------------|-----------------|
| **Discovery** | Full (agents query the Registry freely). | None. |
| **Validation** | Full (agents run the Governance Engine). | None. |
| **Authoring** | Agents draft artifacts with metadata. | Human review and ratification required. |
| **Metadata backfill** | Agents add metadata to existing documents. | Human review. |
| **Structural changes** | Not permitted. | Governance approval required (013 Part 7.1). |
| **Constitutional amendments** | Not permitted. | Human ratification required (`006` Part 8.1). |

## 4.10 IDE Integration

The platform integrates with development environments (VS Code, Cursor, etc.) for:

- **Real-time metadata validation**: the IDE flags missing or invalid metadata as the author writes.
- **Cross-reference navigation**: the IDE provides go-to-definition for cross-references.
- **Architecture visualization**: the IDE displays the authority and dependency graphs inline.
- **Linting**: the IDE runs architecture linting on save.

## 4.11 Automation

| Automation | Trigger | Effect |
|------------|---------|--------|
| **Commit linting** | Git commit. | Runs architecture linting; blocks on blocking findings. |
| **Release validation** | Release tag. | Runs full Governance Engine validation; blocks on blocking findings. |
| **Drift detection** | Periodic / on commit. | Runs drift detection; reports findings. |
| **Registry rebuild** | On commit. | Rebuilds the Registry from the repository. |

## 4.12 Developer Workflows

| Workflow | Steps |
|----------|-------|
| **Author a specification** | `genesis author spec` → draft with metadata → `genesis lint` → `genesis validate` → human review → `genesis review` → human ratification → `genesis publish`. |
| **Amend a specification** | Edit the document → update metadata version → `genesis lint` → `genesis validate` → human review → human ratification. |
| **Author an ADR** | `genesis adr` → draft → human review → ratification. |
| **Investigate drift** | `genesis report drift` → review findings → `genesis report authority` (for affected artifacts) → remediation. |
| **Onboard a new contributor** | `genesis discover "constitution"` → `genesis graph authority` → `genesis docs overview`. |

---

# 5. Components

| Component | What it is |
|-----------|-----------|
| **CLI** | The `genesis` command with subcommands (Part 4.1). |
| **Repository Tools** | Metadata backfill, naming normalization, cross-reference checker, drift detector (Part 4.2). |
| **Linter** | Architecture linting (Part 4.3). |
| **Graph Generator** | Authority, dependency, repository, ownership graphs (Part 4.4). |
| **Validator** | Specification validation via the Governance Engine (Part 4.5). |
| **Report Generator** | Compliance, drift, dependency, authority, coverage reports (Part 4.7). |
| **Documentation Generator** | Architecture overview, artifact index, cross-reference map (Part 4.8). |
| **IDE Integration** | Real-time validation, navigation, visualization (Part 4.10). |
| **Automation** | CI/CD integration for commit linting, release validation, drift detection (Part 4.11). |

---

# 6. Responsibilities

| Body | Developer Platform responsibility |
|------|--------------------------------|
| **Engineers** | Use the platform to discover, validate, author, and govern artifacts. |
| **AI agents** | Use the platform for routine operations under human oversight. |
| **Governance Engine (014)** | The platform invokes the Governance Engine; the platform does not validate itself. |
| **Registry (015)** | The platform queries the Registry; the platform does not index itself. |

---

# 7. Governance

| Change type | Authority |
|--------------|-----------|
| **New CLI command** | Architectural amendment to this specification. |
| **New tool** | Architectural amendment to this specification. |
| **New automation** | Architectural amendment to this specification. |

## 7.1 Constitutional Compliance

| Law | Compliance |
|-----|------------|
| L-22 | The platform's authoring tooling enforces the governance process (metadata, review, ratification). |
| L-25 | AI-assisted authoring requires human review and ratification. |

---

# 8. Lifecycle

The Developer Platform's lifecycle follows the platform's evolution:

```
platform designed → CLI implemented → tools implemented → IDE integration deployed → automation deployed → (evolution: new commands, new tools)
```

The platform's components are implemented incrementally, per the migration phases (Part 10).

---

# 9. Integration

| Spec | Integration |
|------|-------------|
| `013` (Repository) | The platform operates on the repository. |
| `014` (Governance Engine) | The platform invokes the Governance Engine for validation. |
| `015` (Registry) | The platform queries the Registry for discovery and navigation. |
| `016` (Metadata) | The platform's authoring tooling generates and validates metadata. |
| `017` (Validation Rules) | The platform's linter and validator apply the rules. |
| `012` (ATLAS) | The platform's reports are persisted in ATLAS. |

---

# 10. Migration

## 10.1 Migration Phases

### Phase DEV-1 — CLI Core
- Implement the `genesis` CLI with the `discover`, `validate`, `lint`, and `graph` commands.

### Phase DEV-2 — Repository Tools
- Implement the metadata backfill, naming normalization, cross-reference checker, and drift detector.

### Phase DEV-3 — Report and Documentation Generation
- Implement the report generator and the documentation generator.

### Phase DEV-4 — IDE Integration
- Implement the IDE integration (VS Code extension or equivalent).

### Phase DEV-5 — Automation
- Implement the CI/CD integration (commit linting, release validation, drift detection).

### Phase DEV-6 — AI Integration
- Implement the AI agent interfaces (machine-usable CLI, Registry query API).

## 10.2 Backward Compatibility

| Existing artifact | Compatibility | Action |
|-------------------|---------------|--------|
| Existing repository | **Preserved.** The platform operates on it. | None. |
| Existing tooling (`scripts/`, `movie_os/cli.py`) | **Preserved.** The platform is additive; existing tooling may be migrated to the platform over time. | None. |

## 10.3 Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Tool proliferation.** Too many tools may overwhelm engineers. | Low | The CLI is the single entry point; tools are subcommands. |
| **AI agent overreach.** AI agents may perform operations beyond their authority. | Medium | Part 4.9 defines AI agent capabilities and human oversight requirements; the Governance Engine (014) validates agent operations. |

---

# 11. Future Evolution

## 11.1 Natural Language Interface
The platform may evolve to accept natural language queries ("which specs define the CIR?"), translated by AI to Registry queries.

## 11.2 Real-Time Architecture Visualization
The platform may evolve to provide real-time, interactive architecture visualization in the IDE or a web dashboard.

## 11.3 Cross-Repository Platform
For multiple runtimes, the platform may operate across repositories, providing cross-runtime architecture discovery and governance.

## 11.4 Self-Documenting Platform
The platform may evolve to generate its own documentation from its architecture, making the platform self-documenting.

---

## Architectural Rules (Restated)

This specification produced no implementation code. It defines the GENESIS Developer Platform as the engineering tool layer — the CLI, repository tools, linter, graph generator, validator, report generator, documentation generator, IDE integration, and automation — that makes the architecture usable by engineers and AI agents. The platform is a consumer (DP-1), has no authority (DP-2), is runtime-independent (DP-3), and is AI-native (DP-4).

---

## Cross-References

| Reference | Relevance |
|-----------|-----------|
| `006` (Constitution) | L-22, L-25 govern the platform. |
| `013` (Repository) | The platform operates on the repository. |
| `014` (Governance Engine) | The platform invokes the Governance Engine. |
| `015` (Registry) | The platform queries the Registry. |
| `016` (Metadata) | The platform generates and validates metadata. |
| `017` (Validation Rules) | The platform applies the rules. |
| `012` (ATLAS) | Persists the platform's reports. |
| `005` (Creative Mind) | The platform's AI integration enables AI agents to operate on the architecture, analogous to how the Creative Mind operates on creative content. |

---

**End of Specification.**