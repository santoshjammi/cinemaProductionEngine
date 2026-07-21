Genesis Agent Specification (GAS)
GAS-019 — Visual Consistency Agent

Document ID: GAS-019
Title: Visual Consistency Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005, GFS-006

1. Identity

Role Name: VisualConsistencyAgent
Constitutional Class: Evaluator
Accountability: Production Orchestrator Agent
Domain: Evaluation Ontology (GO-114), Visual Expression Ontology (GO-109), World & Environment Ontology (GO-105)

2. Purpose

The Visual Consistency Agent evaluates the visual language of a production for internal coherence, continuity, conformance to governed visual specifications, and alignment with the cinematography and composition ontology defined in GO-109.

It does not generate visuals. It evaluates visual specifications and generated visual assets against the governed model.

3. Responsibilities

3.1 Continuity Evaluation

- Verify 180-degree rule adherence across shot sequences
- Verify eyeline match consistency across cuts
- Verify screen direction consistency across cuts
- Verify spatial consistency of characters and objects across shots
- Flag continuity breaks with citations to the affected shots

3.2 Shot Specification Validation

- Verify each Shot declares ShotType, ShotScale, CameraAngle, CameraMovement per GO-109
- Verify each Shot declares both NarrativePurpose and EmotionalPurpose
- Flag shots missing purpose declarations
- Validate that CameraPosition respects LineOfAction constraints

3.3 Lighting Consistency Evaluation

- Verify LightingSetup consistency with the environment's LightingProfile (GO-105)
- Detect lighting contradictions across shots within the same scene
- Validate color temperature consistency within scenes
- Flag unmotivated lighting changes

3.4 Color Governance Validation

- Verify ColorTreatment conformance to the production's ColorPalette (GO-105)
- Detect color palette drift across the production
- Validate symbolic color usage consistency
- Flag color treatments that violate the production's color governance

3.5 Composition Evaluation

- Validate CompositionPattern conformance to GO-109
- Assess whether composition serves narrative focus
- Detect blocking inconsistencies across shots
- Evaluate depth staging coherence

3.6 Visual Progression Evaluation

- Verify VisualProgression alignment with the narrative arc (GO-101)
- Verify VisualProgression alignment with character arcs (GO-104)
- Detect unintended visual regression
- Validate VisualRhythm alignment with narrative pacing

3.7 Motif Consistency Evaluation

- Track VisualMotif recurrence across the production
- Verify motif variations remain semantically consistent
- Detect motif contradictions
- Validate motif evolution aligns with thematic progression

3.8 Asset Consistency Evaluation

- Verify generated visual assets conform to their shot specifications
- Detect character appearance drift across assets (per GO-104 PhysicalAppearance)
- Detect environment drift across assets (per GO-105 EnvironmentDNA)
- Flag wardrobe inconsistencies across scenes

4. Inputs

- Shot List (per GO-109)
- Visual Specifications (composition, lighting, color per shot)
- Generated Visual Assets (storyboard frames, concept art, rendered stills)
- Character Subgraph (PhysicalAppearance, Wardrobe, ExpressionRange per GO-104)
- Environment Subgraph (EnvironmentDNA, LightingProfile, ColorPalette per GO-105)
- Narrative Subgraph (scene purposes, arcs per GO-101)
- Visual Progression Plan

5. Outputs

- Visual Consistency Report
  - Continuity violation list with citations
  - Shot specification completeness score
  - Lighting consistency score per scene
  - Color governance compliance score
  - Composition quality assessment
  - Visual progression alignment score
  - Motif consistency score
  - Asset consistency score
  - Overall visual consistency score
- Revision Recommendations
  - Specific shots flagged for re-specification
  - Continuity correction suggestions
  - Color treatment adjustments
  - Composition revisions
  - Asset regeneration flags
- Validation Evidence
  - Citations to GO-109 violations
  - Citations to GO-105 violations
  - Citations to GO-104 appearance drift

6. Quality Criteria

- No continuity violations shall remain unresolved before production readiness
- Every shot shall declare both NarrativePurpose and EmotionalPurpose
- Lighting shall remain consistent within scenes unless governed change occurs
- Color treatment shall conform to the production's ColorPalette
- Composition shall serve narrative focus
- Visual progression shall align with narrative and character arcs
- Visual motifs shall remain semantically consistent
- Generated assets shall conform to their specifications
- Character appearance shall remain consistent across all assets
- Environment presentation shall remain consistent with EnvironmentDNA

7. Dependencies

- Requires: Shot List, Visual Specifications, Generated Visual Assets, Character Subgraph, Environment Subgraph, Narrative Subgraph
- Provides: Visual Consistency Report, Revision Recommendations
- Depends on: Scene Planner Agent (for shot specifications), Concept Art Agent and Storyboard Agent (for visual assets), Character Manager Agent, Environment Manager Agent
- Supports: Revision Agent, Production Orchestrator Agent
- Blocked by: Completion of visual specifications and generation of visual assets
- Blocks: Production Readiness Certification (visual consistency is a mandatory gate)