Genesis Pipeline (GPIPE)
GPIPE-003 — Production Pipeline

Document ID: GPIPE-003
Title: Production Pipeline
Version: 1.0.0
Status: Pipeline
Authority: Derived from GFS-000, GFS-005, GWS-001

1. Purpose

The Production Pipeline defines the canonical sequence by which Genesis transforms the Creative Knowledge Subgraph into a complete Production Knowledge Package ready for hand-off to downstream engines. Production planning in Genesis is the act of translating creative knowledge into typed specifications, blueprints, and deliverables that downstream engines can execute without reinterpreting the creator's intent.

In Genesis, the production pipeline does not generate media. The Charter's architectural boundary is absolute: Genesis ends at pre-production. This pipeline produces the knowledge that downstream engines consume.

2. Inputs

- Creative Knowledge Subgraph (from GPIPE-002): Narrative, Character, World.
- Registered ontologies: GO-107 Knowledge, GO-301+ Production ontologies.
- Workflow Manifest (GWS-001) for the chosen production type.
- Reasoning Catalog rules applicable to production planning.

3. Outputs

- Screenplay Document — scene-by-scene screenplay materialized from the Narrative Subgraph.
- Production Plan — phases, milestones, deliverables, dependencies.
- Asset Specifications — typed specs for every asset downstream engines must generate (image, voice, music, SFX, animation).
- Prompt Library — canonical prompts for each downstream generator, derived from the PKG.
- Production Knowledge Package — the assembled, validated, certified package handed to downstream engines.

4. Stages

4.1 Screenplay Generation

The Screenplay Writer Agent produces the Screenplay Document from the Narrative and Character Subgraphs. Each scene, beat, dialogue line, and action is a typed PKG node. The Dialogue Writer Agent refines dialogue using the Character Subgraph's voice patterns. Structural validation (GP-VAL-001) gates the output.

4.2 Scene Planning

The Scene Planner Agent decomposes the Screenplay Document into typed Scene Plans: per scene, the staging, blocking, shot intent, emotional beat, and required assets. Each Scene Plan references the Narrative Subgraph's Beat it materializes.

4.3 Shot Planning

The Shot Planner Agent decomposes each Scene Plan into Shot Plans: per shot, the framing, camera intent, subject, action, and duration range. Shot Plans reference Scene Plans and Character/World Subgraphs.

4.4 Music Planning

The Music Composer Agent runs only if the Narrative Subgraph declares a music motif. The agent produces a Music Plan: per scene, the musical intent, motif references, emotional beat alignment, and duration. The plan references the Narrative Subgraph.

4.5 Asset Specification Fan-Out

Image, Voice, SFX, and Animation spec agents run in parallel (GP-WF-002). Each produces typed Asset Specifications for every asset the downstream engines must generate. Each spec references the Shot Plan or Scene Plan it serves.

4.6 Prompt Building

The Prompt Builder Agent compiles canonical prompts for each downstream generator from the Asset Specifications and the PKG. Prompts are materialized views of knowledge (Charter, Fifth Principle) — they are not canonical. The PKG is canonical; the prompts are derivatives.

4.7 Production Planning

The Production Planner Agent assembles the Production Plan: phases, milestones, deliverables, dependencies, and review gates. The plan references every artifact produced above and declares the hand-off sequence to downstream engines.

4.8 Validation

Structural, semantic, and completeness validation run across the assembled Production Knowledge Package. Any failure routes to the responsible agent.

4.9 Readiness Certification

The Governance Agent runs the Production Readiness approval chain (GP-GOV-001): Structural Validator → Semantic Validator → Completeness Validator → Governance Agent → Chief Architect. On approval, the Production Readiness Certificate is issued.

4.10 Packaging

The Publisher assembles the validated PKG, the Screenplay Document, the Production Plan, the Asset Specifications, the Prompt Library, and the Production Readiness Certificate into the Production Knowledge Package. The package is the single hand-off artifact to downstream engines.

5. Exit Criteria

The Production Pipeline is complete when:

- The Screenplay Document is committed and validated.
- Scene Plans, Shot Plans, Music Plan (if applicable), and Asset Specifications are committed.
- The Prompt Library is committed.
- The Production Plan is committed.
- The Production Knowledge Package passes all three validation layers.
- The Production Readiness Certificate is issued.
- The Production Knowledge Package is handed to downstream engines.

6. Hand-off

The Production Knowledge Package is the authoritative input to the Studio Engine and downstream media generation. Downstream engines may not re-derive creative decisions; they may only execute the specifications in the package. If a downstream engine finds a defect, it must return the package to Genesis for revision — it may not patch it locally.

7. Anti-Patterns

- Generating media inside Genesis — the architectural boundary is absolute.
- Letting the Screenplay Writer invent characters not in the Character Subgraph.
- Treating the Prompt Library as canonical — the PKG is canonical; prompts are derivatives.
- Handing off the package without the Production Readiness Certificate.
- Allowing downstream engines to patch the package locally.
- Skipping the Music Composer because "music is optional" when the Narrative Subgraph declares a motif.

8. Worked Example

Continuing the devotional drama:

- Screenplay Writer produces a 12-scene screenplay from the Narrative Subgraph.
- Scene Planner decomposes into 12 Scene Plans; Shot Planner into 38 Shot Plans.
- Music Composer runs (motif declared): produces Music Plan with 8 cues.
- Asset spec fan-out: 38 image specs, 6 voice specs, 12 SFX specs, 2 animation specs.
- Prompt Builder compiles 58 canonical prompts.
- Production Planner assembles the plan: 5 phases, 14 milestones.
- Validation passes; readiness chain signs; certificate issued.
- Package handed to Studio Engine.