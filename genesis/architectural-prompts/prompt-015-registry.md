# Prompt 015 — Architecture Registry

**Status:** Architectural Prompt — Design History Artifact (Phase III)
**Date:** 2026-07-21
**Corresponding Specification:** `015 — Architecture Registry.md`

## Role

Chief Platform Architect. Phases I–II frozen. Phase III in progress. 013 (Repository) and 014 (Governance Engine) complete and reviewed.

## Objective

Define the machine-readable registry for every architectural artifact in the repository. The Registry is the platform's "card catalog" — it indexes every document, every specification, every ADR, every ontology term, and every schema, with its identity, authority, dependencies, status, and version. The Governance Engine (014) and the Developer Platform (018) operate on the Registry.

## Required Parts

Philosophy; Objectives; Principles; Architecture (artifact catalogue, identifier model, dependencies, authority graph, ownership graph, specification catalogue, version registry, review registry, status registry, discovery model); Components; Responsibilities; Governance; Lifecycle; Integration; Migration; Future Evolution.

## Constitutional Constraints

Derive authority from `006`. The Registry is governed by L-4 (shared semantic model — the Registry is the architectural analog of the COM), L-5 (objects have identity, provenance, lifecycle). The Registry is read by the Governance Engine (014) and the Developer Platform (018); it is populated from the repository (013) and the metadata (016). No implementation code, no APIs, no JSON/YAML. Remain entirely architectural.

## Output

> **015 — Architecture Registry**

## Design Intent Notes

The Registry is the platform's machine-readable map of itself. The critical insight: it is to the repository what the PKG is to a production — a typed graph of artifacts with identity, relationships, and provenance. The Registry enables the Governance Engine to validate the architecture as a graph (not as text), and enables AI agents to discover and navigate the architecture without reading every document.