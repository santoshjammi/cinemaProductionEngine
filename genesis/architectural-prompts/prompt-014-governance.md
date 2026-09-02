# Prompt 014 — Governance & Constitutional Compliance Engine

**Status:** Architectural Prompt — Design History Artifact (Phase III)
**Date:** 2026-07-21
**Corresponding Specification:** `014 — Governance & Constitutional Compliance Engine.md`

## Role

Chief Platform Architect of the ACI Platform. Phases I and II are frozen. Phase III is in progress. 013 (Repository) is complete and reviewed.

## Objective

Define the governance operating system: the engine that validates the repository, the architecture, and the runtime against the Constitution. This is the platform's "judicial branch" — it enforces the constitutional laws (017) on every artifact and operation.

## Required Parts

Philosophy; Objectives; Principles; Architecture (governance authorities, compliance model, validation layers, drift detection, certification, reports); Components; Responsibilities; Governance; Lifecycle; Integration; Migration; Future Evolution.

## Constitutional Constraints

Derive authority from `006`. The Governance Engine is governed by L-22 (amendments require process), L-16 (validation never mutates — the engine reports, it does not fix), and `006` Part 7 (governance) and Part 9 (compliance). The engine is advisory to the Constitutional Review Board (`006` Part 7.5); it does not amend the Constitution. No implementation code, no APIs, no JSON/YAML. Remain entirely architectural.

## Output

> **014 — Governance & Constitutional Compliance Engine**

## Design Intent Notes

The Governance Engine is the platform's judicial branch. The critical insight: it never mutates (L-16 applies to governance as to validation) — it reports compliance and violations; the Constitutional Review Board and the human decide remediation. The engine operates on the repository (013) via the Architecture Registry (015), using the executable rules defined in 017. It is the mechanism that makes the Constitution enforceable, not merely aspirational.