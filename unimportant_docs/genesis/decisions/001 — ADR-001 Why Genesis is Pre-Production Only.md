Genesis Architecture Decision Record (ADR)

ADR-001 — Why Genesis is Pre-Production Only

Document ID: ADR-001
Title: Genesis is Pre-Production Only
Version: 1.0.0
Status: Accepted
Authority: Derived from GFS-000 Constitutional Charter §15 and §16

Date: 2025-01-01
Decision Maker: Chief Architect
Reviewer: Governance Agent
Supersedes: none
Superseded By: none
Related Documents: GFS-000, GARCH-001, GARCH-002

1. Context

Genesis is the Pre-Production Intelligence System of Movie OS. From the earliest design conversations, the temptation existed to extend Genesis beyond pre-production into media generation. The reasoning was familiar: if Genesis already understands the story, characters, world, and production plan, why not let it also render concept art, generate storyboards, synthesize voices, and produce the first cut?

This temptation was strong for several reasons:

- The Production Knowledge Graph already contains the semantic inputs that media generators require. Prompt assembly would be trivial.
- Users naturally want a single tool. Splitting Genesis from the Studio Engine introduces a handoff step that some early reviewers called "unnecessary friction."
- Modern AI models blur the line between knowledge work and generation. A model that can describe a character can also draw one.
- Commercial pressure favors platforms that "do everything." A pre-production-only system is harder to position than an end-to-end pipeline.

Against this pressure stood a set of constraints that the design team could not ignore:

- The Constitutional Charter (GFS-000) declares that "knowledge precedes production" (§5) and that "nothing may enter production unless sufficient knowledge exists to justify it."
- The Charter defines a strict scope (§4) that explicitly excludes image generation, audio generation, music generation, voice generation, animation, rendering, video generation, publishing, and asset creation.
- The Charter mandates that Genesis remain "model-independent, renderer-independent, provider-independent, workflow-independent, implementation-independent" (§16).
- The Charter requires that "every decision must be traceable" (§12) and that "inference must be distinguished from fact" (§10).

Mixing knowledge work and media generation would compromise every one of these constraints. A system that both reasons about a character and renders that character has a built-in incentive to twist its reasoning to fit the renderer's strengths. A system that both validates a shot list and generates the shots cannot impartially validate its own output. A system that both certifies readiness and produces media cannot be trusted to refuse to certify when the media is poor.

The question was therefore not whether Genesis should generate media—it should not—but whether the boundary should be soft or absolute, and where exactly it should be drawn.

2. Decision

Genesis is strictly and absolutely a pre-production system. It produces knowledge, specifications, and validated production intelligence. It produces no media of any kind. The boundary between Genesis and the Studio Engine is absolute and enforced at the architecture, ontology, agent, and workflow levels.

The decision is elaborated by the following binding rules:

- No agent in the Genesis Agent Registry (GAS-001 through GAS-027) may produce, store, or reference media assets.
- No ontology concept in the Genesis Ontology (GO-001 and all derived ontologies) may describe a media artifact. Media concepts belong to downstream ontologies owned by the Studio Engine.
- No workflow in the Genesis Workflow catalog (GWS-001+) may include a media-generation step.
- No materialized view produced by the Genesis Materialization Service may be a media file. Views are structured documents (Markdown, JSON, YAML, JSON-LD, HTML).
- The only artifact that crosses the boundary from Genesis to the Studio Engine is the Production Knowledge Package (PKP), which is a serialized, signed projection of the PKG and contains no media.
- The Studio Engine may not write back into the live PKG. If revision is required, the Studio Engine returns the PKP to Genesis for re-certification.

The boundary is drawn at the issuance of the certified PKP. Everything before that point is Genesis. Everything after is Studio Engine.

3. Status

Accepted on 2025-01-01 by the Chief Architect, reviewed and approved by the Governance Agent.

No supersession is anticipated. The Charter (GFS-000 §15) declares this separation "absolute," which means any change would require constitutional amendment, not a mere ADR.

4. Consequences

4.1 Positive Consequences

- Genesis remains impartial. Because it does not generate media, its validation of production readiness cannot be biased by the quality of its own outputs.
- Genesis remains model-independent. Because it does not depend on a renderer, it survives the rise and fall of any specific generation model or provider.
- Genesis remains testable. Tests of knowledge correctness do not require rendering infrastructure. A test suite can validate the entire PKG pipeline on a laptop.
- Genesis remains swappable. Downstream engines (Studio Engine, future rendering pipelines, alternative providers) can be replaced without touching Genesis.
- Genesis remains auditable. Every decision in the PKG is traceable to evidence; no decision is hidden inside a media artifact that cannot be inspected semantically.
- Genesis remains small. The scope is bounded. The system can be fully specified without ballooning into an end-to-end production platform.
- Genesis's value is clarified. It is the source of truth, not the producer of outputs. This makes it easier to communicate what Genesis is for and what it is not for.

4.2 Negative Consequences

- Two systems are required where one might have sufficed. The Studio Engine is a separate platform with its own architecture, deployment, and governance.
- The handoff introduces a contract surface. The PKP must be stable, versioned, and well-documented, or downstream engines will misuse it.
- Interactive workflows that span the boundary (for example, "generate a concept sketch, then revise the character description based on the sketch") must round-trip through Genesis. This adds latency and complexity.
- Some user expectations will be unmet. A user who expects Genesis to "make the movie" will be disappointed and must be educated about the boundary.
- Genesis cannot self-validate its own recommendations by rendering them. Validation must be semantic, which is harder in some cases than visual inspection would be.

4.3 Neutral Consequences

- The term "pre-production" acquires a precise technical meaning within Movie OS: the set of activities that terminate at PKP issuance.
- A new vocabulary emerges around the boundary: PKP, handoff, re-certification, round-trip. Future ADRs must use these terms consistently.
- The architecture document set splits naturally into Genesis-side and Studio-side families. Cross-references must be explicit about which side a document belongs to.

5. Alternatives

5.1 Alternative 1: End-to-End Generation

Description: Genesis would extend from synopsis through final media. The PKG would feed an internal renderer; outputs would be produced and validated in one system.

Advantages:
- Single system, single deployment, single governance surface.
- No handoff contract to design or maintain.
- Tighter feedback loops between knowledge and generation.

Disadvantages:
- Validation becomes self-referential. The system validates its own media, which destroys impartiality.
- Model independence is lost. The renderer becomes a permanent dependency.
- Scope explodes. The system must master every media discipline: image, audio, music, voice, video, editing, publishing.
- Constitutional conflicts become unavoidable. GFS-000 §4 explicitly excludes media generation from Genesis's scope.

Rejection Rationale: This alternative violates the Constitutional Charter directly. It is not a lawful option under the current constitution and would require constitutional amendment to even be considered.

5.2 Alternative 2: Soft Boundary

Description: Genesis remains primarily pre-production but includes a thin "preview generation" layer that produces low-fidelity previews (storyboard sketches, voice scratch tracks) to support validation.

Advantages:
- Better interactive workflows. Previews give creators tangible feedback during discovery.
- Modest scope expansion. Only low-fidelity outputs are added.

Disadvantages:
- The soft boundary drifts. "Low fidelity" is a moving target; today's scratch track becomes tomorrow's final cut.
- Impartiality is still compromised. A system that generates previews will eventually trust its previews.
- The renderer dependency creeps in. Even preview generation requires a generator, and generators become dependencies.
- The constitutional exclusion in GFS-000 §4 is still violated, just by a smaller amount.

Rejection Rationale: The soft boundary is unstable in practice. Every system that has tried this pattern has eventually expanded until the boundary disappeared. The Constitutional Charter's choice of an absolute boundary exists precisely to prevent this drift.

5.3 Alternative 3: Genesis as Library, Studio Engine as Orchestrator

Description: Genesis would be reduced to a knowledge library with no workflow or governance of its own. The Studio Engine would orchestrate everything, calling Genesis for knowledge services.

Advantages:
- Simplest possible boundary. Genesis is a service; Studio Engine is the system.
- No PKP contract needed. Studio Engine reads the PKG directly.

Disadvantages:
- Genesis loses its constitutional authority. The Charter's mandate that "nothing may enter production unless sufficient knowledge exists to justify it" becomes unenforceable because the Studio Engine decides when knowledge is sufficient.
- Genesis loses its governance gates. Approval and certification move into the Studio Engine, where they conflict with production incentives.
- The PKG becomes a shared mutable store, which destroys canonicality.

Rejection Rationale: This alternative removes the very thing that makes Genesis valuable: the authoritative, governed, certified knowledge layer. Without its own workflow and governance, Genesis is just a database, and the Constitutional Charter's principles become advisory rather than binding.

6. Compliance

6.1 Validation Rules

The Validation Engine (S3 per GARCH-002) enforces the following invariants derived from this decision:

- No node with `ontology_type` in any media-artifact namespace may exist in the PKG.
- No edge with a predicate implying media production (e.g., `renders`, `generates_media_for`) may exist in the PKG.
- No agent specification in the Agent Registry may declare a media-producing responsibility.
- No workflow definition may include a step whose `output_type` is a media artifact.
- No materialized view produced by the Materialization Service may have a MIME type outside the declared document set (Markdown, JSON, YAML, JSON-LD, HTML, PDF).
- The PKP manifest must declare `contains_media: false` and the declaration must be verifiable by hash inspection of the package contents.

6.2 Governance Gates

- The Discovery gate, Validation gate, Review gate, and Certification gate (per GARCH-002 §6) all operate inside Genesis. No gate may be delegated to a downstream engine.
- The Certification gate refuses to issue a PKP if any validation rule above has failed.
- Any proposal to introduce media generation inside Genesis requires a constitutional amendment to GFS-000 §4 and §15, not merely a new ADR.

6.3 Audit Checks

The following audit queries against the Provenance Ledger detect violations:

- Query for any node whose `ontology_type` resolves to a concept outside the Genesis Ontology family.
- Query for any agent whose specification references a media-generation capability.
- Query for any workflow step whose `output_type` is not in the allowed view set.
- Query for any PKP whose manifest declares `contains_media: true` or whose contents fail the media-free hash check.

6.4 Amendment Process

This ADR may not be amended in place. Because the decision is derived directly from GFS-000 §15 and §16, any change requires constitutional amendment under the Governance Constitution. A superseding ADR may only be accepted after such an amendment is ratified.

7. References

- GFS-000 Constitutional Charter, §§4, 5, 10, 12, 15, 16
- GARCH-001 Enterprise Architecture, §§2, 6, 10
- GARCH-002 Reference Architecture, §§1, 6, 14
- GO-001 Genesis Core Ontology, §22 (PKG relationship)

8. Notes

This decision is the architectural cornerstone of Genesis. Every other ADR assumes it. The temptation to relax the boundary will recur with every new generation model that arrives on the market. The Constitution exists precisely so that this temptation can be resisted without re-litigating the question each time.

9. Sign-off

| Role | Name | Date | Signature |
|------|------|------|----------|
| Decision Maker | Chief Architect | 2025-01-01 | (signed) |
| Reviewer | Governance Agent | 2025-01-02 | (signed) |
| Governance Agent | Governance Agent | 2025-01-02 | (signed) |