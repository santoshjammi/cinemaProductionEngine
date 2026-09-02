# Prompt 018 — GENESIS Developer Platform

**Status:** Architectural Prompt — Phase III
**Corresponding Specification:** `018 — GENESIS Developer Platform.md`

## Role

Chief Platform Architect. Phase III in progress. 013–017 complete. This is the final Phase III specification.

## Objective

Define the engineering platform — the tooling, CLI, IDE integration, automation, and developer workflows that engineers and AI agents use to interact with the ACI Platform's repository, architecture, and governance. This specification makes the platform usable.

## Required Parts

Philosophy; Objectives; Principles; Architecture (CLI, repository tooling, architecture linting, graph generation, specification validation, dependency visualization, architecture reports, documentation generation, AI integration, IDE integration, automation, developer workflows); Components; Responsibilities; Governance; Lifecycle; Integration; Migration; Future Evolution.

## Constitutional Constraints

Derive from `006`. The Developer Platform operates on the repository (013), via the Registry (015), using the metadata (016), enforcing the rules (017), through the Governance Engine (014). The platform is a tool; it has no creative authority, no decision authority, no governance authority. No implementation code, no APIs (the platform defines the architecture of the tooling, not the tooling itself). Remain architectural.

## Output

> **018 — GENESIS Developer Platform**

## Design Intent Notes

The Developer Platform is the platform's "IDE" — the interface through which engineers and AI agents interact with the architecture. The critical insight: the platform is a consumer of the Registry (015) and the Governance Engine (014), not a parallel system. It provides discovery, validation, visualization, and authoring tooling, all operating on the architectural graph. The platform makes the architecture executable for engineering teams and AI agents, reducing ambiguity to the point where implementation can begin.