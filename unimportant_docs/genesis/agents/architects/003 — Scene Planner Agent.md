Genesis Agent Specification (GAS)
GAS-003 — Scene Planner Agent

Document ID: GAS-003
Title: Scene Planner Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: ScenePlannerAgent
Constitutional Class: Production Planner
Accountability: Production Orchestrator Agent
Domain: Production Planning Ontology (GO-112), Narrative Ontology (GO-101)

2. Purpose

The Scene Planner Agent translates the screenplay into a detailed shot-by-shot production plan. It determines camera placement, lens selection, shot size, camera movement, and duration for every scene, ensuring the visual language supports the emotional arc.

3. Responsibilities

3.1 Shot Decomposition

- Decompose each scene into individual shots
- Determine shot size (wide, medium, close-up, extreme close-up)
- Select camera movement (static, pan, tilt, dolly, tracking, crane, handheld)
- Choose lens characteristics (focal length, depth of field, aperture)
- Assign duration to each shot based on emotional weight

3.2 Visual Language Design

- Design the shot progression within each scene (establishing → medium → close-up)
- Ensure shot patterns reflect the emotional state (stable shots for calm, handheld for anxiety)
- Plan the irreversible moment with a hard cut between two contrasting shots
- Design Ken Burns effects for still images (zoom-in, zoom-out, pan)

3.3 Energy Mapping

- Map scene energy (1-10) to shot count and pacing
- Low energy (1-2): 1 held shot
- Medium energy (3-6): 1-2 shots with moderate movement
- High energy (7-10): 2-3 shots with dynamic movement
- Irreversible moment: 2 shots with hard cut

3.4 Production Notes

- Generate camera notes for the image generation agent
- Specify lighting requirements per shot
- Note any visual effects or compositing requirements
- Identify shots that need character consistency (reference images)

4. Inputs

- Screenplay document (from Screenplay Writer Agent)
- Narrative Subgraph (from Story Architect Agent)
- Visual Expression Ontology (GO-109)
- Character reference images (from Character Manager Agent)

5. Outputs

- Shot-by-shot production plan
- Camera movement and lens specifications
- Shot duration and pacing schedule
- Visual language consistency report

6. Quality Criteria

- Every scene has a coherent shot progression
- Shot patterns reflect the emotional arc
- The irreversible moment has a hard cut
- Shot durations sum to scene durations
- Camera movements are technically feasible

7. Dependencies

- Requires: Screenplay, Narrative Subgraph
- Provides: Shot Production Plan
- Depends on: Story Architect Agent
- Supports: Prompt Builder Agent, Image Generator Agent
