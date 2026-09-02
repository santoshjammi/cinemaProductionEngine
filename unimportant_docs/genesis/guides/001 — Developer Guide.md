Genesis Guide (GDE)
GDE-001 — Developer Guide

Document ID: GDE-001
Title: Genesis Developer Guide
Version: 1.0.0
Status: Guide
Authority: Derived from GFS-000, GFS-009

1. Purpose

This guide tells a developer how to work inside the Genesis Engine
documentation repository. It covers repository layout, file naming, document
anatomy, how to add a new agent, how to add a new ontology, how to add a new
specification, and how to validate your work before opening a pull request.

Genesis is a documentation-first system. There is no runnable code in this
repository. Every artifact is a Markdown document governed by the
constitutional hierarchy. If you are looking for the runtime implementation,
it lives in `movie_os/` outside this `docs/genesis/` tree.

2. Repository Layout

Genesis uses an Enterprise Knowledge Architecture with ~30 top-level
directories. Each directory has one purpose and must not be repurposed.

| Directory | Purpose |
|-----------|---------|
| `agents/` | Agent specifications by role |
| `architecture/` | Enterprise architecture and deployment models |
| `constitutions/` | Foundational standards (GFS-000 through GFS-009) |
| `contracts/` | Semantic, API, and ontology contracts |
| `decisions/` | Architecture Decision Records |
| `diagrams/` | Mermaid reference diagrams |
| `docs/` | Long-form companion documentation |
| `examples/` | Filled-in production examples |
| `generators/` | Spec generators and scaffolders |
| `governance/` | Governance policies and registries |
| `guides/` | How-to guides for developers and contributors |
| `integrations/` | External integration contracts |
| `knowledge/` | Knowledge graph definitions, taxonomies, vocabulary |
| `manifests/` | Repository and dependency manifests |
| `meta/` | Meta-models and evolution frameworks |
| `models/` | Domain models |
| `ontology/` | Ontologies by domain |
| `patterns/` | Reusable design patterns |
| `pipelines/` | Production pipelines |
| `policies/` | Enforced policies |
| `prompts/` | Prompt templates |
| `references/` | External references and glossary |
| `registry/` | Registries (agents, ontologies, taxonomies) |
| `runtime/` | Runtime contracts |
| `schemas/` | JSON Schema, YAML Schema, SHACL, OWL |
| `specifications/` | Format, protocol, and standard specifications |
| `standards/` | Adopted external standards |
| `templates/` | Blank templates for new productions |
| `tests/` | Test specifications |
| `tooling/` | Tooling contracts |
| `validation/` | Validation rules and contracts |
| `workflows/` | Workflow definitions by type |

3. File Naming Convention

Every file follows the pattern:

```
NNN — Title.md
```

- `NNN` is a zero-padded number unique within the directory.
- The separator is an em-dash (`—`, U+2014), not a hyphen.
- The title is in Title Case.
- Files are Markdown only.

Numbering schemes:

- Constitutions: GFS-000 through GFS-009 (top-level), GFS-010+ (derived)
- Ontology: GO-001 through GO-006 (core), GO-101+ (domain)
- Agents: GAS-001 through GAS-027
- Specifications: GSPEC-001+ and GFS-010+ for foundational specs
- Workflows: GWS-001+
- Schemas: GSS-001+
- References: GREF-001+
- Templates: GTMP-001+
- Diagrams: GD-001+
- Guides: GDE-001+

4. Document Anatomy

Every document begins with a header block. The block is mandatory; a
document without it is invalid and will be rejected by the linter.

```
Genesis <Type> (<Abbreviation>)
<ABBREV>-<NNN> — <Title>

Document ID: <ABBREV>-<NNN>
Title: <Title>
Version: 1.0.0
Status: <Status>
Authority: Derived from <parent documents>
```

Valid Status values:

- Foundational — only for constitutions.
- Core Ontology — only for GO-001.
- Agent Specification — for agents.
- Foundational Standard — for derived GFS specs.
- Specification — for GSPEC documents.
- Workflow — for GWS documents.
- Guide — for GDE documents.
- Reference Diagram — for GD documents.
- Reference — for GREF documents.
- Template — for GTMP documents.
- Draft — for work in progress.

5. Adding a New Agent

1. Determine the agent's constitutional class: orchestrator, architect,
   engineer, validator, governance, researcher, reviewer, shared, learning,
   publisher.
2. Place the file in `agents/<class>/NNN — Title.md`. Pick the next free
   number in `GAS-NNN`.
3. Use the format of an existing agent spec (see `agents/architects/001 —
   Story Architect Agent.md` for a canonical template).
4. The spec must define: Identity, Purpose, Responsibilities, Inputs,
   Outputs, Reasoning Process, Quality Criteria, Dependencies.
5. Register the agent in the Agent Registry (see `registry/`).
6. Add an entry to the Agent Dependency Graph (GD-002) if the agent has
   non-obvious dependencies.

6. Adding a New Ontology

1. Determine the domain: core, semantic, constitutional, creativity,
   experience, execution, foundation, governance, learning, meta,
   organization, registry, strategy.
2. Place the file in `ontology/<domain>/NNN — Title.md` using the next free
   `GO-NNN` number.
3. The ontology must derive from GO-001 Core Ontology. It may extend, it
   may never redefine.
4. Register the ontology in `ontology/registry/` and in the Ontology
   Registry contract under `contracts/`.
5. Follow the Ontology Modeling Guide (GDE-003) for the full derivation
   procedure.

7. Adding a New Specification

1. Determine the category: product, architecture, runtime, governance,
   implementation, integrations, deployment, enterprise, compiler,
   knowledge-graph, ontology.
2. Place the file in `specifications/<category>/NNN — Title.md` using the
   next free `GSPEC-NNN` (or `GFS-NNN` for foundational specs).
3. Every specification must define: scope, invariants, validation
   requirements, compliance criteria, and the documents it derives from.

8. Adding a New Workflow

1. Determine the type: authoring, validation, review, generation,
   governance, publication, learning, deployment.
2. Place the file in `workflows/<type>/NNN — Title.md` using the next free
   `GWS-NNN`.
3. Every workflow must reference the Full Production Workflow (GWS-001)
   as the baseline and declare its place in the lifecycle.

9. Validation Approach

Genesis is documentation-first, so "testing" means structural and
constitutional validation, not unit tests.

Before opening a pull request, run:

- `bash tooling/lint-docs.sh` — checks naming, header block, status values,
  and numbering uniqueness.
- `bash tooling/validate-cross-refs.sh` — checks that every `GFS-NNN`,
  `GO-NNN`, `GAS-NNN`, `GWS-NNN`, `GSPEC-NNN` reference points to a real
  file.
- `bash tooling/check-ontology-derivation.sh` — checks that every
  domain ontology declares its parent in GO-001 or another domain
  ontology.
- `bash tooling/check-agent-registry.sh` — checks that every agent spec
  is registered and that the registry has no orphans.

If any check fails, fix the document. Do not modify the linter to make
the check pass; the linter encodes constitutional invariants.

10. Pull Request Checklist

- File name follows `NNN — Title.md` with an em-dash.
- Header block is present and complete.
- Status value is from the canonical set.
- All cross-references resolve.
- The new document is registered in the relevant registry.
- No document exceeds 600 lines; split if longer.
- No document is under 150 lines of real content; expand if shorter.
- The PR description links the document to its parent documents in the
  constitutional hierarchy.

11. Common Mistakes

- Using a hyphen instead of an em-dash in the filename.
- Omitting the Authority line in the header.
- Defining a new concept in a domain ontology that contradicts GO-001.
- Declaring an agent without specifying its inputs and outputs.
- Writing a specification without validation requirements.
- Adding a workflow that does not reference GWS-001.

12. Getting Help

- Read the Constitutional Charter (GFS-000) first.
- Read the Ontology Modeling Guide (GDE-003) before touching ontology.
- Read the Contributor Guide (GDE-002) before opening a PR.
- Read the Genesis Meta-Model (GMM-001) if you are changing how Genesis
  describes itself.