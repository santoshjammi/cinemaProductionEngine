Genesis Agent Specification (GAS)
GAS-005 — Environment Manager Agent

Document ID: GAS-005
Title: Environment Manager Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: EnvironmentManagerAgent
Constitutional Class: Knowledge Steward
Accountability: Production Orchestrator Agent
Domain: World & Environment Ontology (GO-105)

2. Purpose

The Environment Manager Agent is the authoritative source of all world and environment knowledge within a production. It maintains the World Subgraph of the PKG, ensures environmental consistency, and provides location reference data to downstream agents.

3. Responsibilities

3.1 World Discovery

- Extract world information from the synopsis and screenplay
- Define the setting (time period, geographic location, cultural context)
- Identify all locations where scenes take place
- Discover the emotional atmosphere of each environment

3.2 Environment Modeling

- Define the Environment DNA for each location:
  - Location type (interior, exterior, urban, natural, liminal)
  - Architectural style (Victorian, modern, industrial, organic)
  - Lighting profile (primary source, color temperature, intensity, shadows)
  - Color palette (dominant, accent, emotional temperature)
  - Sound ambience (room tone, ambient sounds, silence quality)
  - Camera positions (available angles, sight lines, constraints)
  - Variants (time of day, weather, seasonal changes)

3.3 Consistency Management

- Ensure environments are consistent across scenes set in the same location
- Track environmental changes (a room that gets darker as the story progresses)
- Flag scenes where the environment contradicts the emotional state
- Maintain a canonical description of each location

3.4 Reference Management

- Maintain hero images for each environment (for IPAdapter consistency)
- Store environment reference images (lighting studies, color palettes)
- Provide environment-specific prompt fragments to the Prompt Builder Agent

4. Inputs

- Production Brief (setting, time period, locations)
- Screenplay (scene descriptions, atmosphere notes)
- Narrative Subgraph (scene locations, emotional states)

5. Outputs

- Complete World Subgraph in the PKG
- Environment DNA specifications for each location
- Environmental consistency validation report
- Hero images and reference data

6. Quality Criteria

- Every location has a complete Environment DNA
- Environments are consistent across scenes
- Environmental changes are tracked and meaningful
- Lighting and color support the emotional arc
- Reference images are available for all primary locations

7. Dependencies

- Requires: Production Brief, Screenplay
- Provides: World Subgraph, Environment DNA, Hero Images
- Depends on: Story Architect Agent
- Supports: Image Generator Agent, Prompt Builder Agent
