# AGENTS.md — Genesis Engine Agent Guide

## Purpose

This file provides guidance to AI coding agents (Claude Code, Cursor, Copilot,
etc.) when working within the Genesis Engine documentation repository.

## What Genesis Is

Genesis is the **Pre-Production Intelligence System** of Movie OS. It transforms
incomplete human creative intent into complete, validated, internally consistent,
and production-ready structured knowledge.

Genesis is **not** a content generator, rendering engine, or animation system.
It is the authoritative source of truth for every production decision *before*
any media generation begins.

## Repository Structure

The repository uses an **Enterprise Knowledge Architecture** with ~30 top-level
directories. Each directory has a specific purpose and should not be repurposed.

| Directory | What goes here | What does NOT go here |
|-----------|---------------|----------------------|
| `agents/` | Agent specs by role (orchestrators, architects, engineers, etc.) | Agent implementations (those go in `movie_os/agents/`) |
| `architecture/` | Enterprise architecture, deployment models | Specific product specs |
| `constitutions/` | Foundational standards (GFS-000 through GFS-009) | Anything that can be changed without constitutional amendment |
| `contracts/` | Semantic, API, ontology contracts | Implementation code |
| `decisions/` | Architecture Decision Records (ADRs) | General documentation |
| `ontology/` | All ontologies by domain (core, semantic, experience, etc.) | Product specifications |
| `specifications/` | Format, protocol, and standard specifications | Implementation code |
| `schemas/` | JSON Schema, YAML Schema, SHACL, OWL | Runtime data |
| `workflows/` | Workflow definitions by type (authoring, validation, etc.) | Implementation code |
| `templates/` | Blank templates for new productions | Filled-in examples (those go in `examples/`) |
| `references/` | External references, standards, glossary | Original content |

## File Naming Convention

All files follow the pattern:
```
NNN — Title.md
```

Where `NNN` is a zero-padded number unique within the directory. The em-dash
(—) is preferred but a regular dash (-) is acceptable.

Numbering schemes:
- **Constitutions**: GFS-000 through GFS-009 (top-level), GFS-010+ (derived)
- **Ontology**: GO-001 through GO-006 (core), GO-101 through GO-119 (domain)
- **Agents**: GAS-001 through GAS-027
- **Specifications**: GSPEC-001+
- **Workflows**: GWS-001+
- **Schemas**: GSS-001+
- **References**: GREF-001+
- **Templates**: GTMP-001+

## Working with Genesis

### When adding a new agent spec
1. Determine the agent's role (orchestrator, architect, engineer, validator, etc.)
2. Place it in the appropriate `agents/<role>/` subdirectory
3. Follow the format of existing agent specs (identity, purpose, responsibilities, inputs, outputs, quality criteria, dependencies)

### When adding a new ontology
1. Determine the domain (core, semantic, experience, execution, etc.)
2. Place it in the appropriate `ontology/<domain>/` subdirectory
3. Follow the GO-NNN numbering scheme

### When adding a new specification
1. Determine the category (product, architecture, runtime, governance, etc.)
2. Place it in the appropriate `specifications/<category>/` subdirectory
3. Follow the GSPEC-NNN numbering scheme

### When adding a new workflow
1. Determine the type (authoring, validation, review, generation, etc.)
2. Place it in the appropriate `workflows/<type>/` subdirectory

## Constitutional Hierarchy

The Constitutional Charter (`constitutions/00-ConstitutionCharter.md`) is the
highest governing authority. Every other document — ontologies, specifications,
workflows, agents, implementations — must conform to it. If a lower-level
document conflicts with the Charter, the Charter prevails.

## Genesis Engine Boundary

Genesis ends at the conclusion of pre-production. The Studio Engine (Movie OS
pipeline) begins only after Genesis certifies production readiness. No media
generation capability exists inside Genesis. This separation is absolute.

## Key Constraints

- Every document must have a Document ID, Version, and Status
- Every agent spec must define inputs, outputs, and dependencies
- Every specification must define validation requirements
- Every ontology must derive from the Core Ontology (GO-001)
- Every workflow must reference the Full Production Workflow (GWS-001) as the baseline