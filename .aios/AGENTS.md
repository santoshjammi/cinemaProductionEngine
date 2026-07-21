---
name: "aios-manifest"
version: "1.0"
---

# AIOS Manifest (`.aios/`)

This directory serves as the cognitive backbone for `videoGen`. It houses the specifications, memories, and orchestrations that guide how AI agents reason about, plan, and execute within the production system.

## Purpose
- **Separation of Concerns**: Keeps the "brain" (reasoning models) independent from the "body" (production code).
- **Resilience**: Allows the orchestration layer to evolve without breaking platform standards.
- **Contextual Depth**: Provides agents with persistent, domain-specific memory and logic.

## Directory Structure
- `agents/`: Persona definitions and role boundaries.
- `prompts/`: Core interaction templates and intent triggers.
- `memories/`: Long-term context, RAG stores, and persistent state.
- `contexts/`: Transient session states and temporary workspace data.
- `planners/`: Task decomposition logic and dependency mapping.
- `compilers/`: Logic for translating natural language intent into executable steps.
- `workflows/`: End-to-end process definitions (e.g., video generation pipelines).
- `policies/`: Guardrails, safety protocols, and compliance standards (e.g., DPDP).
- `routing/`: Model selection logic and traffic management profiles.
- `model_profiles/`: Configuration templates for different LLMs/VMs.
- `execution/`: Action runners, tool definitions, and script mappings.
- `validation/`: Quality gates, verification logic, and acceptance criteria.
- `knowledge/`: Domain-specific facts, technical documentation, and reference data.
