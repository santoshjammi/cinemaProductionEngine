# Prompt 016 — Machine Readable Architecture Metadata

**Status:** Architectural Prompt — Phase III
**Corresponding Specification:** `016 — Machine Readable Architecture Metadata.md`

## Role

Chief Platform Architect. Phase III in progress. 013–015 complete.

## Objective

Define the metadata contract attached to every specification and architectural artifact in the repository. The metadata makes every document machine-readable, enabling the Registry (015) and the Governance Engine (014) to operate on the repository as a graph.

## Required Parts

Philosophy; Objectives; Principles; Architecture (metadata taxonomy, canonical fields, version semantics, authority references, dependency references, review references, ADR references, ontology references, schema references, validation requirements); Components; Responsibilities; Governance; Lifecycle; Integration; Migration; Future Evolution.

## Constitutional Constraints

Derive from `006`. Metadata is mandatory (013 RP-3). No JSON/YAML (the metadata model is architectural; its projection into a specific format is an implementation concern). Remain architectural.

## Output

> **016 — Machine Readable Architecture Metadata**