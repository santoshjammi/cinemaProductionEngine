# Genesis Engine — Enterprise Knowledge Architecture

> Genesis is the **Pre-Production Intelligence System** of Movie OS.
> It transforms incomplete human creative intent into complete, validated,
> internally consistent, and production-ready structured knowledge.

## What Genesis Is

Genesis is **not** a content generator. It is **not** a rendering engine.
It is the authoritative source of truth for every production decision
*before* any media generation begins.

## Directory Structure

```
genesis/
├── agents/           AI agent definitions by role
│   ├── orchestrators/    Production orchestrator, revision
│   ├── architects/       Story, scene, shot, music, prompt
│   ├── researchers/      Domain research
│   ├── engineers/        Image, voice, music, SFX, video, subtitle
│   ├── validators/       Quality evaluation agents
│   ├── reviewers/        Psychology review
│   ├── governance/       Character & environment stewardship
│   ├── learning/         (reserved)
│   └── shared/           Cross-cutting agents
├── architecture/     Enterprise architecture, deployment models
├── assets/           Canonical reusable assets
├── compiler/         Ontology compiler, parsers, code generators
├── constitutions/    Constitutional principles (GFS-000 through GFS-009)
├── contracts/        Semantic, API, and ontology contracts
├── decisions/        Architecture Decision Records (ADRs)
├── diagrams/         Mermaid, PlantUML, Graphviz diagrams
├── docs/             Generated documentation
├── examples/         Example ontologies, workflows, outputs
├── generators/       Markdown, JSON Schema, RDF, TypeScript generators
├── governance/       Governance rules, approval processes
├── guides/           Developer and contributor guides
├── integrations/     Neo4j, GraphQL, REST, MCP, LLM integrations
├── knowledge/        Production Knowledge Graph definitions
├── manifests/        Repository, dependency, build manifests
├── meta/             Meta-models, ontology evolution
├── models/           Domain models
├── ontology/         All ontologies organized by domain
│   ├── core/             Core narrative, character, world
│   ├── foundation/       Knowledge and reasoning patterns
│   ├── semantic/         Relationships, causality, communication
│   ├── experience/       Audience, psychology, visual, audio, temporal
│   ├── execution/        Production planning
│   ├── governance/      Agency, roles, decision governance
│   ├── learning/         Evaluation, feedback, improvement
│   ├── organization/     Asset, versioning, provenance
│   ├── creativity/       Innovation, design reasoning
│   ├── strategy/         Objectives, intent evolution
│   ├── constitutional/   Wisdom, ethics, constitutional reasoning
│   ├── meta/             Integration, meta-model, evolution
│   ├── generated/        Generated ontologies
│   └── registry/         Ontology registry, namespace spec
├── patterns/         Reusable design and reasoning patterns
├── pipelines/        Production pipelines, orchestration
├── policies/         Security, governance, quality policies
├── prompts/          Canonical prompts for agents
├── references/       External references, standards, glossary
├── registry/         Ontology, agent, capability registries
├── runtime/          Runtime configuration
├── schemas/          JSON Schema, YAML, SHACL, OWL, RDF
├── specifications/   Functional, technical, architectural specs
├── standards/        Naming, coding, documentation standards
├── templates/       Reusable templates
├── tests/            Validation datasets, regression tests
├── tooling/          CLI utilities, scripts
├── validation/       Validators, quality gates
└── workflows/        Workflow definitions
    ├── authoring/        Full production
    ├── validation/       Revision
    ├── review/           Evaluation
    ├── publication/      (reserved)
    ├── generation/      Scene-only
    ├── deployment/       (reserved)
    ├── learning/        (reserved)
    └── governance/     (reserved)
```

## Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Constitutional Charter | `constitutions/00-ConstitutionCharter.md` | Supreme governing authority |
| Identity Constitution | `constitutions/01-identity-constitution.md` | What Genesis is and is not |
| Core Ontology | `ontology/core/001 — Genesis Core Ontology.md` | Canonical semantic vocabulary |
| PKG Specification | `specifications/knowledge-graph/010 — Production Knowledge Graph Specification.md` | The canonical knowledge representation |
| Agent Communication Protocol | `specifications/agents/011 — Agent Communication Protocol.md` | How agents talk to each other |
| Readiness Certification | `specifications/governance/012 — Production Readiness Certification Standard.md` | When production is ready |
| Full Production Workflow | `workflows/authoring/001 — Full Production Workflow.md` | Complete agent execution sequence |
| Agent Dependency Map | `references/methodologies/002 — Agent Dependency Map.md` | Who depends on whom |

## File Count

| Category | Files |
|----------|-------|
| Constitutions | 10 |
| Ontology | 25 |
| Agents | 27 |
| Specifications | 15 |
| Workflows | 4 |
| Schemas | 2 |
| References | 2 |
| Templates | 1 |
| **Total** | **87** (growing) |

## Reading Order

1. **Start here**: `constitutions/00-ConstitutionCharter.md`
2. **Identity**: `constitutions/01-identity-constitution.md`
3. **Core ontology**: `ontology/core/001 — Genesis Core Ontology.md`
4. **PKG spec**: `specifications/knowledge-graph/010 — Production Knowledge Graph Specification.md`
5. **Full workflow**: `workflows/authoring/001 — Full Production Workflow.md`
6. **Agent map**: `references/methodologies/002 — Agent Dependency Map.md`

## Principles

1. **Knowledge precedes production** — nothing enters production without sufficient knowledge
2. **Discovery precedes specification** — understand before specifying
3. **Reasoning precedes decision** — every decision must be explainable
4. **The synopsis is the creative problem statement** — not the screenplay
5. **Knowledge is canonical** — the PKG is the single source of truth
6. **Inference must be distinguished from fact** — five confidence levels
7. **Questions are valuable only when they reduce uncertainty**
8. **Every decision must be traceable**
9. **Consistency overrides creativity**
10. **Production readiness is measurable**