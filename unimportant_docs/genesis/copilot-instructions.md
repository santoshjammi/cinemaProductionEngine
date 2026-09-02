Copilot Instructions — Genesis Engine Repository

Document ID: GMS-COPILOT
Title: Copilot Instructions
Version: 1.0.0
Status: Guide
Authority: Derived from AGENTS.md and GMS-000

1. Purpose

This file instructs AI coding assistants (GitHub Copilot, OpenAI Codex, Claude Code, Cursor, OpenCode, and similar tools) working in the Genesis Engine documentation repository. It explains how to read the specs, how to extend the architecture, and what conventions to follow.

If you are an AI assistant and you have been asked to work in this repository, read this file first.

2. What Genesis Is

Genesis is the **Pre-Production Intelligence System** of Movie OS. It transforms incomplete human creative intent into complete, validated, internally consistent, and production-ready structured knowledge.

Genesis is **not** a content generator, rendering engine, or animation system. It is the authoritative source of truth for every production decision *before* any media generation begins.

3. Repository Layout

The repository uses an Enterprise Knowledge Architecture with ~30 top-level directories. Each directory has a specific purpose and should not be repurposed.

| Directory | What goes here | What does NOT go here |
|-----------|---------------|----------------------|
| `agents/` | Agent specs by role | Agent implementations |
| `architecture/` | Enterprise architecture, deployment models | Product specs |
| `constitutions/` | GFS-000 through GFS-009 | Anything changeable without amendment |
| `contracts/` | Semantic, API, ontology contracts | Implementation code |
| `decisions/` | Architecture Decision Records | General documentation |
| `ontology/` | All ontologies by domain | Product specifications |
| `specifications/` | Format, protocol, standard specs | Implementation code |
| `schemas/` | JSON Schema, YAML Schema, SHACL, OWL | Runtime data |
| `workflows/` | Workflow definitions by type | Implementation code |
| `templates/` | Blank templates | Filled-in examples |
| `references/` | External references, glossary | Original content |

4. File Naming Convention

All files follow the pattern:

```
NNN — Title.md
```

Where `NNN` is a zero-padded number unique within the directory. The em-dash (—) is preferred; a regular dash (-) is acceptable.

Numbering schemes:
- **Constitutions**: GFS-000 through GFS-009 (top-level), GFS-010+ (derived).
- **Ontology**: GO-001 through GO-006 (core), GO-101 through GO-119 (domain), GO-201+ (specialized), GO-301+ (production), GO-200+ (generated).
- **Agents**: GAS-001 through GAS-027, plus learning and publisher agents.
- **Architecture**: GARCH-001 through GARCH-009.
- **Specifications**: GSPEC-001+.
- **Workflows**: GWS-001+.
- **Schemas**: GSS-001+.
- **References**: GREF-001+.
- **Templates**: GTMP-001+.

5. Document Header Block

Every document must open with a header block:

```
<Family> Specification
<Doc-ID> — <Title>

Document ID: <Doc-ID>
Title: <Title>
Version: <semver>
Status: <status>
Authority: <parent documents>
```

Statuses include: Foundational, Core Ontology, Domain Ontology, Specialized Ontology, Architecture Specification, Registry, Master Specification, Guide.

6. Constitutional Hierarchy

The Constitutional Charter (`constitutions/00-ConstitutionCharter.md`, GFS-000) is the highest governing authority. Every other document — ontologies, specifications, workflows, agents, implementations — must conform to it. If a lower-level document conflicts with the Charter, the Charter prevails.

7. Genesis Boundary

Genesis ends at the conclusion of pre-production. The Studio Engine (Movie OS pipeline) begins only after Genesis certifies production readiness. No media generation capability exists inside Genesis. This separation is absolute.

8. How to Read the Specs

Start with:
1. `00_Vision.md` — top-level vision and master spec index.
2. `01_Architecture.md` — 4-layer and 7-layer architecture overview.
3. `02_Constitution.md` — consolidated constitutional summary.
4. `03_GFS.md` — per-standard overview.
5. `04_GO.md` — per-ontology overview.
6. `05_KnowledgeGraph.md` — PKG structure and queries.
7. `06_Runtime.md` — session lifecycle and dispatch.
8. `07_Compiler.md` — ontology compiler pipeline.
9. `08_Generators.md` — generator catalog.

Then dive into the relevant `architecture/`, `ontology/`, `agents/`, or `workflows/` directory.

9. How to Extend the Architecture

When adding a new agent spec:
1. Determine the agent's role (orchestrator, architect, engineer, validator, reviewer, researcher, governance, learning, publisher).
2. Place it in the appropriate `agents/<role>/` subdirectory.
3. Follow the format of existing agent specs: identity, purpose, responsibilities, inputs, outputs, quality criteria, dependencies.
4. Register the agent in `architecture/005 — Genesis Agent Catalog.md`.

When adding a new ontology:
1. Determine the domain (core, semantic, experience, execution, governance, learning, organization, registry, strategy, creativity, foundation, meta, generated).
2. Place it in the appropriate `ontology/<domain>/` subdirectory.
3. Follow the GO-NNN numbering scheme for the appropriate tier.
4. Ensure the ontology derives from GO-001 (directly or transitively).
5. Register the ontology in `04_GO.md`.

When adding a new specification:
1. Determine the category (product, architecture, runtime, governance, etc.).
2. Place it in the appropriate `specifications/<category>/` subdirectory.
3. Follow the GSPEC-NNN numbering scheme.
4. Define validation requirements.

When adding a new workflow:
1. Determine the type (authoring, validation, review, generation, governance).
2. Place it in the appropriate `workflows/<type>/` subdirectory.
3. Reference GWS-001 (Full Production Workflow) as the baseline.

10. Key Constraints

- Every document must have a Document ID, Version, and Status.
- Every agent spec must define inputs, outputs, and dependencies.
- Every specification must define validation requirements.
- Every ontology must derive from the Core Ontology (GO-001).
- Every workflow must reference the Full Production Workflow (GWS-001) as the baseline.
- No document may contradict a higher-authority document.
- No implementation may treat a projection (file, manifest, prompt) as canonical.

11. Coding Standards

- Implementations live outside this repository (typically in `movie_os/`). This repository is the specification.
- Implementations must satisfy every interface declared in `architecture/002 — Reference Architecture.md`.
- No implementation may write to the PKG outside an agent's constitutional authority.
- No implementation may produce media. Media generation belongs to the Studio Engine.

12. Documentation Standards

- Every document opens with the header block defined in §5.
- Documents are numbered uniquely within their directory.
- Cross-references use the document ID (e.g., `GARCH-005`), not file paths.
- No document may contradict a higher-authority document.
- Em-dash (—) is preferred in filenames; regular dash (-) is acceptable.

13. When You Are Unsure

- Read `00_Vision.md` first.
- Read the relevant GFS standard.
- Read the relevant GARCH document.
- Read the relevant GO ontology.
- If still unsure, do not invent. Record the uncertainty and escalate to governance.

14. What Not to Do

- Do not create media generation capabilities inside Genesis.
- Do not write implementations in this repository; this is the specification.
- Do not skip the header block.
- Do not repurpose directories.
- Do not contradict a higher-authority document.
- Do not treat a projection as canonical.
- Do not commit without verifying the file naming and header conventions.

15. Approval

These instructions are binding for every AI coding assistant working in this repository.