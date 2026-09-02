# Prompt 013 — Repository & Metadata Architecture

**Status:** Architectural Prompt — Design History Artifact (Phase III)
**Date:** 2026-07-21
**Corresponding Specification:** `013 — Repository & Metadata Architecture.md`

## Role

Chief Platform Architect of the ACI Platform. Phases I (Constitution, 000–006) and II (Runtime Architecture, 007–012) are complete, frozen, and ratified. Phase III transforms the architecture into a self-governing engineering platform.

## Objective

Define the canonical repository architecture: the directory taxonomy, document hierarchy, naming conventions, metadata model, versioning model, folder ownership, artifact lifecycle, repository evolution, and repository governance. This specification makes the repository itself an architectural artifact governed by the Constitution.

## Required Parts

Philosophy; Objectives; Principles; Architecture (directory taxonomy, document hierarchy, naming conventions, metadata model, versioning model, folder ownership); Components; Responsibilities; Governance; Lifecycle; Integration; Migration; Future Evolution.

## Constitutional Constraints

Derive authority from `006`. The repository is the platform's physical manifestation; its structure must reflect the constitutional tiers (Tier 0 Constitution, Tier 1 runtime constitutions, Tier 2 specifications, Tier 3 standards, Tier 4 guides). No implementation code, no APIs, no JSON/YAML, no schemas, no vendor tooling. Remain entirely architectural.

## Output

> **013 — Repository & Metadata Architecture**

## Design Intent Notes

The repository is not a folder structure; it is the constitutional architecture's physical form. The critical insight: the repository's directory taxonomy must mirror the document tier hierarchy from `006` Part 1.5, so that any contributor (human or AI agent) can locate an artifact by its constitutional tier. The metadata model makes every document machine-readable, enabling the Governance Engine (014) and Architecture Registry (015) to operate on the repository as a graph.