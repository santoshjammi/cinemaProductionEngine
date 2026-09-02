# Prompt 012 — ATLAS Knowledge Architecture

**Status:** Architectural Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `012 — ATLAS Knowledge Architecture.md`

---

## Role

You are the Chief Enterprise Architect of the ACI Platform. Phase II is in progress. 007–011 are complete and reviewed. This is the final Phase II specification.

## Objective

Generate the architectural specification for **ATLAS** — the Knowledge Operating System of the ACI Platform. ATLAS persists all artifacts (CIS, CIR, PKP, media, validation reports) with provenance, supports retrieval for reasoning and learning, and enables cross-production and cross-runtime knowledge sharing.

## Required Parts

1. **Knowledge Philosophy** — Why knowledge outlives media; why ATLAS is the single persistence authority; why it makes no creative decisions.
2. **Knowledge Objects** — What ATLAS stores (all COM objects in all states, all artifacts, all reports).
3. **Creative Memory** — Director Memory (`002` Part 6) and faculty enrichments (`005` Part 4.3) as ATLAS-persisted knowledge.
4. **Learning** — How the Learning Faculty (`005` Part 3.3.11) uses ATLAS for precedent and pattern updates.
5. **Experience** — Cross-production experience as a knowledge corpus.
6. **Semantic Search** — How ATLAS supports the Semantic Query Model (`004` Part 7) across all stored knowledge.
7. **Reasoning Support** — How ATLAS provides precedent to the Creative Mind during reasoning.
8. **Knowledge Evolution** — How knowledge grows, is retained, and is governed over time.
9. **Cross-Runtime Knowledge** — How knowledge is shared across runtimes (cinema, games, books, etc.).
10. **Institutional Memory** — The platform's constitutional history, ADRs, prompts, and reviews as ATLAS-persisted knowledge.
11. **Knowledge Governance** — Retention, deprecation, access control under the Constitution.
12. **Lifecycle** — The lifecycle of knowledge objects from creation to indefinite preservation.

## Constitutional Constraints

- Derive authority from `006` (Constitution). ATLAS is governed by L-18 (knowledge outlives media), L-19 (history is immutable), L-20 (learning never rewrites history).
- ATLAS is the only system that writes to persistent storage on behalf of the engine (`001` §2.1). It makes no creative decisions (L-15 applies to ATLAS as a non-creative body).
- ATLAS persists artifacts from all pillars (GENESIS, PROMETHEUS, ORACLE) but does not call them.
- Architecture only — no implementation, code, YAML, JSON, schemas, APIs, or database structures.

## Output

> **012 — ATLAS Knowledge Architecture**

---

## Design Intent Notes

ATLAS is the platform's Knowledge Operating System. The critical insight: ATLAS is the *only* system that touches durable storage (`001` §2.1, invariant 4), making it the single persistence authority. This centralization is what ensures provenance integrity (L-5, L-9) and history immutability (L-19) across the platform. ATLAS is not a database; it is a knowledge OS that governs how all artifacts are stored, versioned, retrieved, and learned from. It is the platform's long-term memory — the layer that outlives every model, every runtime, and every technology. ATLAS also holds the platform's institutional memory: the constitutional documents, the ADRs, the prompts, and the reviews that constitute the platform's design history.