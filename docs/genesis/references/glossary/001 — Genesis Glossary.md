Genesis References (GREF)
GREF-001 — Genesis Glossary

Document ID: GREF-001
Title: Genesis Glossary
Version: 1.0.0
Status: Reference
Authority: Derived from GFS-000

1. Purpose

This glossary defines every term, acronym, and concept used across the Genesis Engine documentation. It is the canonical reference for disambiguating language across constitutions, ontologies, specifications, workflows, agents, schemas, and templates.

2. Document Identifier Conventions

- GFS — Genesis Foundational Standard. Constitutional-level document.
- GO — Genesis Ontology. Domain ontology specification.
- GAS — Genesis Agent Specification. Agent role definition.
- GSPEC — Genesis Specification. Format, protocol, or product standard.
- GWS — Genesis Workflow Specification. Workflow definition.
- GSS — Genesis Schema Specification. Data schema definition.
- GREF — Genesis Reference. Reference, glossary, or bibliography entry.
- GTMP — Genesis Template. Blank production template.
- GDEC — Genesis Decision. Architecture Decision Record.
- GEX — Genesis Example. Worked example of a production.

3. Core Artifacts

- PKG — Production Knowledge Graph. The canonical graph representation of all production knowledge. Knowledge is canonical; files are not.
- PKP — Production Knowledge Package. The materialized, distributable artifact containing the PKG, all derived documents, validation reports, and the Production Readiness Certificate.
- PRC — Production Readiness Certificate. Issued by the Governance Agent after all validation gates pass.
- Production Brief — The initial input containing synopsis, constraints, territory, and creative intent.
- Synopsis — The creative problem statement. Not the screenplay, not the story. The initial expression of human creative intent.
- Production Plan — The execution plan produced by the Production Orchestrator Agent.
- Session — A single execution of the Genesis Engine on one production brief.

4. Knowledge Classifications

- Explicit — Knowledge stated directly in the brief or source material.
- Inferred — Knowledge derived by reasoning from explicit knowledge.
- Confirmed — Inferred knowledge that has been validated by the creator or an authoritative agent.
- Assumed — Knowledge accepted without evidence for the purpose of progression. Must be flagged.
- Unknown — Knowledge gaps that must be resolved before production readiness.

5. Confidence Levels

- High — Evidence is strong, consistent, and validated. Ready for production.
- Medium — Evidence is sufficient but not fully validated. May proceed with monitoring.
- Low — Evidence is weak or partial. Must be resolved before downstream use.
- Insufficient — No usable evidence. Triggers a discovery cycle or creator question.
- Conflicted — Multiple sources disagree. Triggers reconciliation before use.

6. Constitutional Roles

- Orchestrator — Coordinates the session, dispatches agents, manages lifecycle.
- Architect — Designs narrative, character, world, scene, shot, and prompt structures.
- Engineer — Generates content: screenplay, dialogue, music, prompts.
- Validator — Evaluates outputs against quality, consistency, and readiness criteria.
- Reviewer — Performs constitutional, psychological, and domain review.
- Researcher — Discovers external knowledge and fills knowledge gaps.
- Governor — Makes governance decisions, certifies readiness, amends production.
- Publisher — Packages and distributes the certified PKP.
- Learner — Extracts feedback and patterns from completed productions.

7. Production States

- Initiated — Session created, brief accepted.
- Discovering — Research and knowledge extraction in progress.
- Designing — Creative foundation being structured.
- Producing — Content and media plan being generated.
- Evaluating — Validation agents assessing outputs.
- Revising — Revision loop active, addressing critical issues.
- Certifying — Governance Agent reviewing for readiness.
- Certified — Production Readiness Certificate issued.
- Published — PKP packaged and distributed.
- Failed — Unrecoverable error; session terminated.
- Archived — Production completed and stored for learning.

8. Agents (Selected)

- Production Orchestrator Agent (GAS-026) — Top-level coordinator.
- Research Agent — Discovers knowledge and fills gaps.
- Story Architect Agent (GAS-001) — Designs narrative structure.
- Character Manager Agent — Models characters and psychology.
- Environment Manager Agent — Defines locations and world.
- Screenplay Writer Agent (GAS-002) — Materializes narrative into screenplay prose.
- Dialogue Writer Agent — Generates character dialogue.
- Scene Planner Agent (GAS-003) — Plans scenes and sequences.
- Shot Planner Agent (GAS-010) — Designs shots and camera language.
- Music Composer Agent (GAS-024) — Composes musical score.
- Prompt Builder Agent (GAS-006) — Builds media generation prompts.
- Story Quality Agent (GAS-017) — Evaluates narrative structure.
- Dialogue Quality Agent (GAS-018) — Evaluates dialogue effectiveness.
- Visual Consistency Agent (GAS-019) — Validates visual continuity.
- Audio Mix Quality Agent (GAS-020) — Validates audio mix.
- Emotion Score Agent (GAS-021) — Measures emotional modulation.
- Character Consistency Agent (GAS-022) — Validates character behavior.
- YouTube Readiness Agent (GAS-023) — Validates platform readiness.
- Governance Agent — Certifies production readiness.
- Revision Agent (GAS-027) — Coordinates revision loops.
- Feedback Learning Agent — Learns from evaluation feedback.
- Pattern Extraction Agent — Extracts reusable patterns.
- Production Publisher Agent — Packages the PKP.
- Documentation Publisher Agent — Generates documentation from the PKG.

9. Ontology Domains

- Core Ontology (GO-001) — Foundational concepts shared by all domains.
- State & Lifecycle Ontology (GO-003) — Production states and transitions.
- Narrative Ontology (GO-101) — Story structure, beats, arcs.
- Character Ontology (GO-104) — Character identity, psychology, arc.
- World & Environment Ontology (GO-105) — Locations, environments, world rules.
- Event, Action & Causality Ontology (GO-106) — Events and causal chains.
- Knowledge, Information & Revelation Ontology (GO-107) — Knowledge flow.
- Human Psychology & Behavior Ontology (GO-103) — Psychological modeling.
- Production Planning Ontology (GO-112) — Planning structures.
- Evaluation Ontology (GO-114) — Evaluation criteria and reports.

10. Validation Concepts

- Validation Gate — A checkpoint that must pass before progression.
- Critical Issue — A defect that blocks production readiness.
- Revision Loop — The cycle of revising outputs to address critical issues.
- Consistency Override — The principle that consistency overrides creativity.
- Traceability — Every decision must record origin, evidence, dependencies, confidence.
- Provenance — The lineage of a knowledge node from source to current state.

11. Infrastructure Terms

- Genesis Engine — The Pre-Production Intelligence System itself.
- Movie OS — The broader system that Genesis is part of.
- Studio Engine — The downstream engine that begins after Genesis certifies readiness.
- Compiler — The system that compiles ontologies, schemas, and specifications into executable form.
- Registry — The catalog of agents, ontologies, schemas, and templates.
- Manifest — The declaration of a production's structure and contents.

12. Governance Terms

- Amendment — A formal change to a constitutional document.
- Proposal — A submitted request for a governance decision.
- Waiver — An approved exception to a constitutional rule.
- Escalation — Routing of an unrecoverable issue to the Governance Agent.
- Constitutional Hierarchy — The precedence order: GFS-000 supreme, all else derived.

13. Publication Terms

- Packaging — Assembling the PKG, documents, reports, and certificate into the PKP.
- Distribution — Delivering the PKP to downstream engines or archives.
- Materialization — Generating a document view from the canonical PKG.
- Versioning — Maintaining the version history of a PKP across revisions.

14. Learning Terms

- Feedback Loop — The cycle of using evaluation results to improve future productions.
- Pattern — A reusable structure extracted from one or more completed productions.
- Ontology Refinement — Updating an ontology based on learning outcomes.

15. Boundary Terms

- Pre-Production — The Genesis responsibility scope. Ends at certification.
- Production — Media generation and assembly. Owned by Studio Engine.
- Post-Production — Final edit, mix, packaging. Owned by Studio Engine.
- Media Generation — Explicitly outside Genesis scope.

16. Notes on Usage

Terms defined here must be used consistently across all Genesis documents. When a term is introduced in a new document, it must either appear in this glossary or be added here. Conflicting definitions are architectural defects and must be resolved under the consistency override principle.