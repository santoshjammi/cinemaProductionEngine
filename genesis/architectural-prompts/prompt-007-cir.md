# Prompt 007 — Creative Intent Record (CIR) Architecture

**Status:** Architectural Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `007 — Creative Intent Record (CIR) Architecture.md` (located at repository root)
**Purpose:** Preserve the intent behind the architectural specification. Part of the project's institutional memory.

---

## Role

You are the Chief Enterprise Architect of the Artificial Creative Intelligence (ACI) Platform. The Constitutional Foundation (000–006) is complete and frozen. You are in Phase II: transforming constitutional intent into executable architecture.

## Objective

Generate the architectural specification for the **Creative Intent Record (CIR)** — the canonical Intermediate Representation (IR) of Artificial Creativity. The CIR represents the completed result of Creative Cognition (`005`) and Directorial Decision-Making (`002`). It is the executable creative representation consumed by the compiler (`008`, future).

The CIR was introduced at the constitutional level in `002` Part 12 and referenced throughout 003–006. This specification elevates it from a constitutional concept to a full architectural specification: the IR of the platform.

## Required Parts

1. **Philosophy** — Why the CIR is the IR of Artificial Creativity; why it sits between cognition and compilation; why it is not the CIS (intent) and not the PKP (compiled output).
2. **Architecture** — The CIR's structural architecture: nodes, edges, subgraphs, root, partitions.
3. **Intermediate Representation** — The CIR as IR: how it represents creative decisions in a form the compiler consumes; the analog to an AST in a traditional compiler.
4. **Decision Graph** — The CIR as a graph of Creative Decisions (`004` §2.3.52); dependency edges; causal edges; conflict edges; the Creative Decision Graph (CDG) from `002` Part 4 as the CIR's core subgraph.
5. **Creative Provenance** — Every CIR node's provenance chain: CIS domain → faculty enrichment → director decision → CIR node.
6. **Alternatives** — Rejected alternatives as first-class CIR records, enabling revision without re-rolling.
7. **Confidence** — The ADR-004 five-level taxonomy applied to every CIR node.
8. **Review** — Human review of CIR nodes; the review gate before freeze.
9. **Versioning** — GFS-003 immutable revisions; CIR versions; the CIR hash.
10. **Traceability** — Upstream to CIS; downstream to PKP artifacts via `cir_origin`.
11. **Freeze Rules** — When and how the CIR becomes immutable; the Chief Director's freeze authority; the pre-freeze validation.
12. **Compiler Interface** — How the compiler (`008`) reads the CIR; the contract between CIR and compiler.
13. **Human Interaction** — How the human reviews, amends, overrides, and locks CIR nodes.
14. **Governance** — CIR evolution under the Constitution; compatibility; deprecation.
15. **Migration** — Integration with the existing constitutional architecture.

## Constitutional Constraints

- Derive authority from the ACI Constitution (`006`).
- The CIR is governed by constitutional laws L-6 (cognition precedes decision), L-8 (decision authority is defined), L-9 (every decision has provenance), L-10 (every decision is explainable), L-11 (decision precedes compilation), L-19 (history is immutable).
- Do not redefine the CIR concept (it is defined in `002` Part 12 and constitutionalized in `006`).
- Do not duplicate the CIS (`003`), the COM (`004`), or the PKP (`009`, future).
- Architecture only — no implementation, code, YAML, JSON, schemas, or APIs.

## Output

> **007 — Creative Intent Record (CIR) Architecture**

---

## Design Intent Notes

The CIR is the pivotal artifact of the ACI Platform: it is where creative cognition becomes executable creative representation. The critical insight: the CIR is the IR of Artificial Creativity, analogous to an AST in a traditional compiler. It captures *why* each creative decision exists (provenance, alternatives, rationale) in a form the compiler can traverse deterministically. The CIR/PKP separation (CIR = reasoning, PKP = compiled executable) is what enables surgical revision: a drift report names a CIR node, and only that node and its downstream dependents re-enter the pipeline.