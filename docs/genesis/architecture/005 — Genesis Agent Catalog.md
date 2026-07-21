Genesis Architecture Specification (GAS)
GARCH-005 — Genesis Agent Catalog

Document ID: GARCH-005
Title: Genesis Agent Catalog
Version: 1.0.0
Status: Architecture Specification
Authority: Derived from GARCH-001, GFS-005 Agent Constitution, GAS-001..027

1. Purpose

This document enumerates every specialized agent in the Genesis Engine, its contract, and its interactions. It is the authoritative catalog used by the Workflow Engine, the Agent Runtime, and the Governance Engine to dispatch, supervise, and audit agent activity.

Agents are stateless reasoners over the stateful Production Knowledge Graph. No agent owns knowledge. Every agent contributes assertions to the PKG, and every assertion carries provenance and confidence.

2. Agent Classification

Agents are grouped by constitutional role:

- Orchestrators — coordinate multi-step workflows.
- Architects — author high-level structure (story, scenes, shots, prompts).
- Engineers — generate or transform artifacts in their domain.
- Validators — score and verify specific quality dimensions.
- Reviewers — provide adversarial or domain-specific review.
- Researchers — gather external evidence and references.
- Governance — manage canonical registries and approvals.
- Learning — extract reusable patterns from completed productions.
- Publishers — materialize and emit certified artifacts.

3. Agent Catalog

The full catalog contains 31 agents. Each entry lists: ID, name, role class, primary responsibility, inputs, outputs, dependencies.

3.1 Orchestrators
- GAS-026 Production Orchestrator — Orchestrator. Drives the Full Production Workflow (GWS-001). Inputs: creative intent, PKG snapshot. Outputs: workflow plan, dispatch orders. Depends on: Workflow Engine, Agent Runtime.
- GAS-027 Revision Agent — Orchestrator. Drives revision of an existing PKG/PKP. Inputs: revision request, prior PKP. Outputs: revised PKG diff, re-validation orders. Depends on: Workflow Engine, Validation Engine.

3.2 Architects
- GAS-001 Story Architect — Architect. Decomposes intent into narrative spine, themes, audience experience targets. Inputs: creative intent. Outputs: narrative structure nodes, theme nodes. Depends on: GO-101 Narrative Ontology.
- GAS-002 Screenplay Writer — Architect. Expands narrative into scenes and dialogue. Inputs: narrative structure. Outputs: scene nodes, dialogue nodes. Depends on: GO-101, GO-108.
- GAS-003 Scene Planner — Architect. Decomposes scenes into beats, shots, staging. Inputs: scene nodes. Outputs: beat nodes, shot plan nodes. Depends on: GO-101, GO-109.
- GAS-006 Prompt Builder — Architect. Builds provider-ready prompts from PKG subgraphs. Inputs: shot plan, style subgraph. Outputs: prompt manifests. Depends on: GARCH-003 Semantic Layer.
- GAS-010 Shot Planner — Architect. Plans shot composition, camera, blocking. Inputs: scene plan, world constraints. Outputs: shot nodes, composition nodes. Depends on: GO-109.
- GAS-024 Music Composer — Architect. Designs musical score plan and cues. Inputs: scene rhythm, emotional arc. Outputs: score plan nodes, cue nodes. Depends on: GO-110.

3.3 Engineers
- GAS-011 Image Generator — Engineer. Generates still images per shot plan. Inputs: prompt manifest. Outputs: image asset references (metadata only). Depends on: Studio Engine interface (post-handoff).
- GAS-012 Voice Generator — Engineer. Generates voice performances. Inputs: dialogue, voice profile. Outputs: voice asset references. Depends on: Studio Engine interface.
- GAS-013 Music Generator — Engineer. Generates score audio. Inputs: score plan. Outputs: music asset references. Depends on: Studio Engine interface.
- GAS-014 Audio Mixing Agent — Engineer. Mixes dialogue, score, SFX. Inputs: audio asset references. Outputs: mix plan. Depends on: Studio Engine interface.
- GAS-015 Video Composer — Engineer. Composes final video sequence. Inputs: shot list, mix plan. Outputs: composition plan. Depends on: Studio Engine interface.
- GAS-016 Subtitle Agent — Engineer. Generates subtitle tracks. Inputs: dialogue, timing. Outputs: subtitle manifests. Depends on: GO-108.
- GAS-025 SFX Generator — Engineer. Generates sound effects plan. Inputs: scene events. Outputs: SFX plan nodes. Depends on: GO-110.

3.4 Validators
- GAS-017 Story Quality Agent — Validator. Scores narrative coherence, pacing, arc integrity. Inputs: narrative subgraph. Outputs: validation findings. Depends on: GFS-006.
- GAS-018 Dialogue Quality Agent — Validator. Scores dialogue naturalness, voice consistency. Inputs: dialogue subgraph. Outputs: validation findings.
- GAS-019 Visual Consistency Agent — Validator. Scores visual continuity across shots. Inputs: shot subgraph, style subgraph. Outputs: validation findings.
- GAS-020 Audio Mix Quality Agent — Validator. Scores mix balance and clarity. Inputs: mix plan. Outputs: validation findings.
- GAS-021 Emotion Score Agent — Validator. Scores emotional arc realization. Inputs: narrative + scene subgraph. Outputs: validation findings.
- GAS-022 Character Consistency Agent — Validator. Scores character voice and behavior consistency. Inputs: character subgraph. Outputs: validation findings.
- GAS-023 YouTube Readiness Agent — Validator. Scores platform-specific readiness. Inputs: full PKG projection. Outputs: validation findings.

3.5 Reviewers
- GAS-009 Psychology Reviewer — Reviewer. Adversarial review of psychological truth, attachment, defense mechanisms. Inputs: narrative + character subgraph. Outputs: review findings. Depends on: GO-103, GO-201.

3.6 Researchers
- GAS-007 Research Agent — Researcher. Gathers external references, precedents, factual evidence. Inputs: knowledge gap. Outputs: reference nodes, evidence nodes. Depends on: GREF registry.

3.7 Governance
- GAS-004 Character Manager — Governance. Maintains canonical character registry. Inputs: character assertions. Outputs: character registry updates. Depends on: GO-104.
- GAS-005 Environment Manager — Governance. Maintains canonical world/environment registry. Inputs: world assertions. Outputs: world registry updates. Depends on: GO-105.

3.8 Learning
- GAS-L01 Feedback Learning Agent — Learning. Ingests post-production feedback into pattern library. Inputs: production feedback. Outputs: pattern nodes. Depends on: GWS-013.
- GAS-L02 Pattern Extraction Agent — Learning. Extracts reusable patterns from completed PKGs. Inputs: certified PKP. Outputs: pattern library entries.

3.9 Publishers
- GAS-P01 Production Publisher — Publisher. Materializes the certified PKP and emits handoff. Inputs: certified PKG. Outputs: PKP artifact. Depends on: GARCH-007.
- GAS-P02 Documentation Publisher — Publisher. Materializes human-readable documentation projections. Inputs: PKG. Outputs: markdown documents. Depends on: GARCH-003.

4. Common Agent Contract

Every agent, regardless of role, must conform to the following contract:

- Identity: stable GAS-NNN identifier and version.
- Inputs: a typed subgraph request expressed against the Semantic Layer.
- Outputs: a set of assertions, each with provenance and confidence.
- Side effects: writes only to the PKG via the Knowledge Layer; never to files, caches, or external stores.
- Idempotence: re-running with identical inputs yields identical assertions (no duplicate writes).
- Observability: emits audit events for every action.
- Failure mode: produces a structured failure report; never raises silently.

5. Interaction Model

Agents do not call each other directly. All interactions are mediated by the Workflow Engine and the Message Bus:

- An agent receives a *task* from the Workflow Engine.
- It reads from the PKG via the Semantic Layer.
- It writes assertions to the PKG via the Knowledge Layer.
- It emits a *completion* or *failure* event to the Message Bus.
- The Workflow Engine decides the next dispatch based on workflow state and validation findings.

6. Supervision

The Governance Engine supervises every agent. Agents that violate the constitution, the ontology, or the validation rules are flagged. Repeated violations trigger suspension of the agent's write privileges pending review.

7. Extension Policy

New agents may be added only through:
- A new GAS-NNN specification.
- Approval by the Governance Engine.
- Registration in the Agent Registry.
- Conformance to the common agent contract.

8. Approval

This catalog is the authoritative enumeration of Genesis agents. All workflow definitions must reference agents by their GAS-NNN identifier as listed here.