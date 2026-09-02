# Prompt 010 — PROMETHEUS Runtime Architecture

**Status:** Architectural Prompt — Design History Artifact
**Date:** 2026-07-21
**Corresponding Specification:** `010 — PROMETHEUS Runtime Architecture.md`

---

## Role

You are the Chief Enterprise Architect of the ACI Platform. Phase II is in progress. 007 (CIR), 008 (Compiler), 009 (PKP) are complete and reviewed.

## Objective

Generate the architectural specification for the **PROMETHEUS Runtime** — the execution engine that renders the PKP (`009`) into media. PROMETHEUS is NOT creative reasoning, NOT decision making, NOT cognition. It is a pure executor governed by L-14 (execution never changes intent) and L-15 (execution never invents creativity).

## Required Parts

1. **Runtime Philosophy** — Why the runtime is a pure executor; why it has zero creative authority; why it is deterministic.
2. **Execution Model** — How the runtime reads the PKP and produces media; the execution pipeline.
3. **Media Rendering** — The rendering components (image, video, voice, music, audio, subtitle) and their contracts.
4. **Resource Scheduling** — How rendering resources are scheduled; parallel rendering; dependency order.
5. **Runtime Services** — The services the runtime provides (provider abstraction, capability registry, asset emission).
6. **Execution Contracts** — The PKP-PROMETHEUS contract (from 009 Part 12.1); the PROMETHEUS-ATLAS contract.
7. **Runtime Optimization** — Performance optimization within the bounds of determinism.
8. **Error Handling** — How the runtime handles rendering failures; fallback providers.
9. **Deterministic Rendering** — Same PKP + same providers → same media; the replay contract (addressing the provider non-determinism gap from reviews 008/009).
10. **Runtime Extensibility** — How the runtime is extended for new providers and new media types.
11. **Platform Independence** — The runtime is not tied to a specific OS, cloud, or hardware.
12. **Governance** — Runtime evolution under the Constitution.

## Constitutional Constraints

- Derive authority from `006` (Constitution). PROMETHEUS is governed by L-14 (execution never changes intent), L-15 (execution never invents creativity), L-18 (knowledge outlives media).
- PROMETHEUS reads the PKP (`009`) from ATLAS (`012`); it does not read the CIR or the CIS.
- PROMETHEUS writes media to ATLAS; it does not write to the PKP, CIR, or CIS.
- Architecture only — no implementation, code, YAML, JSON, schemas, or APIs.

## Output

> **010 — PROMETHEUS Runtime Architecture**

---

## Design Intent Notes

PROMETHEUS is the platform's pure executor. The critical insight: PROMETHEUS has zero creative authority (L-15). It reads the PKP — which carries *what to render* — and renders it, without exercising creative judgment. This is what makes the platform's output deterministic and its creative decisions traceable: if PROMETHEUS could invent, the media would not trace to the CIR, and ORACLE could not detect drift. The runtime's determinism (same PKP + same providers → same media) is the final link in the platform's deterministic replay chain (CIS → CIR → PKP → media). The provider non-determinism gap (flagged in reviews 008/009) is addressed here: where a provider is irreducibly non-deterministic, PROMETHEUS records the specific output used, enabling replay from the recorded output rather than from the provider.