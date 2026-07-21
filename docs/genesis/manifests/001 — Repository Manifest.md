Genesis Manifest (GMF)
GMF-001 — Repository Manifest

Document ID: GMF-001
Title: Repository Manifest
Version: 1.0.0
Status: Manifest
Authority: Derived from GFS-000, GFS-009

1. Purpose

This manifest describes the Genesis Engine documentation repository at a
single glance: directory inventory, document counts, version, lineage,
and the constitutional boundaries the repository must respect. It is the
first document a reviewer or auditor should read to orient themselves.

2. Repository Identity

- Name: Genesis Engine
- Scope: Pre-Production Intelligence System of Movie OS
- Repository path: `docs/genesis/`
- Governing authority: Constitutional Charter (GFS-000)
- Canonical representation: Production Knowledge Graph (GFS-010)
- Boundary: Genesis ends at production readiness; the Studio Engine
  begins beyond. No media generation capability exists inside Genesis
  (GFS-000 §15).

3. Version

- Repository version: 1.0.0
- Lineage: derived from GFS-000 through GFS-009
- Evolution policy: additive; documents are never deleted, only
  deprecated (GMM-002).
- Compatibility: every document is backward-compatible within a MAJOR
  version.

4. Directory Inventory

The repository is organized into ~30 top-level directories. Each
directory has one purpose; none is repurposed.

| Directory | Document Type | ID Prefix | Count (approx.) |
|-----------|---------------|-----------|------------------|
| `agents/` | Agent specs by role | GAS-NNN | 27 |
| `architecture/` | Enterprise architecture | — | 3 |
| `constitutions/` | Foundational standards | GFS-NNN | 11 |
| `contracts/` | Semantic, API, ontology contracts | — | 4 |
| `decisions/` | Architecture Decision Records | ADR-NNN | 5 |
| `diagrams/` | Mermaid reference diagrams | GD-NNN | 4 |
| `docs/` | Companion long-form docs | — | 0–2 |
| `examples/` | Filled-in production examples | — | 0 |
| `generators/` | Spec generators and scaffolders | — | 0 |
| `governance/` | Governance policies | — | 3 |
| `guides/` | How-to guides | GDE-NNN | 3 |
| `integrations/` | External integration contracts | — | 0 |
| `knowledge/` | PKG definition, taxonomies, vocabulary | GKR-NNN | 3 |
| `manifests/` | Repository and dependency manifests | GMF-NNN | 2 |
| `meta/` | Meta-models and evolution frameworks | GMM-NNN | 2 |
| `models/` | Domain models | GDM-NNN | 4 |
| `ontology/` | Ontologies by domain | GO-NNN | 14+ |
| `patterns/` | Reusable design patterns | — | 9 |
| `pipelines/` | Production pipelines | — | 0 |
| `policies/` | Enforced policies | — | 4 |
| `prompts/` | Prompt templates | — | 0 |
| `references/` | External references and glossary | GREF-NNN | 6 |
| `registry/` | Registries | — | 0 |
| `runtime/` | Runtime contracts | — | 0 |
| `schemas/` | JSON Schema, SHACL, OWL | GSS-NNN | 7 |
| `specifications/` | Format, protocol, standard specs | GSPEC-NNN / GFS-NNN | 12 |
| `standards/` | Adopted external standards | — | 0 |
| `templates/` | Blank templates | GTMP-NNN | 10 |
| `tests/` | Test specifications | — | 0 |
| `tooling/` | Tooling and linters | — | 0 |
| `validation/` | Validation rules and contracts | — | 0 |
| `workflows/` | Workflow definitions | GWS-NNN | 9 |

5. Document Counts

- Constitutional documents: 11 (GFS-000 through GFS-010).
- Core ontologies: 6 (GO-001 through GO-006, planned).
- Domain ontologies: 8+ (GO-101 onward).
- Agent specifications: 27 (GAS-001 through GAS-027).
- Workflow definitions: 9 (GWS-001 onward, by type).
- Reference diagrams: 4 (GD-001 through GD-004).
- Guides: 3 (GDE-001 through GDE-003).
- Knowledge references: 3 (GKR-001 through GKR-003).
- Manifests: 2 (GMF-001, GMF-002).
- Meta-models: 2 (GMM-001, GMM-002).
- Domain models: 4 (GDM-001 through GDM-004).

6. Numbering Schemes

| Prefix | Domain | Range |
|--------|--------|-------|
| GFS | Foundational Standards | 000–009 (charter tier), 010+ (derived) |
| GO | Ontology | 001–006 (core), 101+ (domain) |
| GAS | Agent Specifications | 001–027 |
| GWS | Workflows | 001+ |
| GSPEC | Specifications | 001+ |
| GSS | Schemas | 001+ |
| GREF | References | 001+ |
| GTMP | Templates | 001+ |
| GD | Diagrams | 001+ |
| GDE | Guides | 001+ |
| GKR | Knowledge References | 001+ |
| GMF | Manifests | 001+ |
| GMM | Meta-Models | 001+ |
| GDM | Domain Models | 001+ |
| ADR | Decision Records | 001+ |

7. File Conventions

- Naming: `NNN — Title.md` with an em-dash (U+2014).
- Header block: mandatory on every document (Document ID, Title,
  Version, Status, Authority).
- Length: 150–600 lines of real content.
- Format: Markdown only.
- Cross-references: use the full ID (e.g., `GFS-010`, `GO-001`).

8. Constitutional Boundaries

The repository is governed by the Charter (GFS-000) and the derived
constitutions. Every document must conform. If a lower-level document
conflicts with the Charter, the Charter prevails (GFS-000 §17).

Hard boundaries:

- No media generation capability inside Genesis.
- No implementation code in this repository.
- No document may redefine a Core Ontology concept.
- No agent may operate outside its declared constitutional class.
- No workflow may bypass the lifecycle state machine (GO-003, GD-004).

9. Dependencies

External dependencies (software, models, runtimes) are listed in the
Dependency Manifest (GMF-002). Internal cross-document dependencies are
encoded in each document's Authority and Dependencies sections and are
validated by `tooling/validate-cross-refs.sh`.

10. Maintenance

This manifest is maintained by the maintainers and updated whenever:

- A new top-level directory is added.
- A new numbering scheme is introduced.
- The repository MAJOR version changes.
- A constitutional amendment alters the directory contract.

The manifest is referenceable; it is not constitutional. It may be
updated by a normal PR with maintainer approval.