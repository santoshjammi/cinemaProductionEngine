# Prompt 011 — ORACLE Validation Architecture

**Status:** Architectural Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `011 — ORACLE Validation Architecture.md`

---

## Role

You are the Chief Enterprise Architect of the ACI Platform. Phase II is in progress. 007–010 are complete and reviewed.

## Objective

Generate the architectural specification for **ORACLE** — the independent validation authority. ORACLE verifies that media matches intent and decisions; it never mutates artifacts (L-16) and validates against the CIS/CIR/PKP, not against its own creative judgment (L-17).

## Required Parts

1. **Validation Philosophy** — Why validation is independent; why it never mutates; why it validates against intent and decisions, not opinion.
2. **Validation Layers** — The layered validation model (constitution, semantic, creative, runtime, compliance).
3. **Constitution Validation** — Verifying constitutional law compliance across all artifacts.
4. **Semantic Validation** — Verifying COM invariants (`004` Part 5) and CIR/PKP graph integrity.
5. **Creative Validation** — Verifying media against CIR decisions (drift detection) and CIS intent.
6. **Runtime Validation** — Verifying media against PKP specifications (structural, visual, audio, continuity).
7. **Compliance** — Constitutional compliance certification (per `006` Part 9).
8. **Metrics** — The Creative Metrics (`002` Part 11) as validation measurements.
9. **Certification** — Constitutional certification of a production (`006` Part 9.3).
10. **Audit** — Constitutional auditing (`006` Part 9.2).
11. **Risk** — Risk classification of validation findings.
12. **Violation Reporting** — How violations are reported and remediated (`006` Part 9.4–9.5).
13. **Governance** — ORACLE evolution under the Constitution.

## Constitutional Constraints

- Derive authority from `006` (Constitution). ORACLE is governed by L-16 (validation never mutates), L-17 (validation is against intent and decisions).
- ORACLE reads the PKP (`009`), the CIR (`007`), the CIS (`003`), and the media (from `010` via ATLAS). It writes only validation reports.
- ORACLE does not call GENESIS, PROMETHEUS, or the human directly; it communicates through ATLAS.
- Architecture only — no implementation, code, YAML, JSON, schemas, or APIs.

## Output

> **011 — ORACLE Validation Architecture**

---

## Design Intent Notes

ORACLE is the platform's independent validation authority. The critical insight: ORACLE never mutates (L-16) and validates against intent and decisions, not its own opinion (L-17). This makes validation advisory, not authoritative — ORACLE reports, the human and the Board decide. ORACLE's drift detection (media vs. CIR via `cir_origin`) is the trigger for surgical revision, closing the platform's quality loop. ORACLE also performs constitutional compliance certification (`006` Part 9), making it the enforcer of the Constitution itself — the platform's "judicial branch."