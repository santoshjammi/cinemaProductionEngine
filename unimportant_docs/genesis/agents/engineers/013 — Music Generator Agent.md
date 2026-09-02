Genesis Agent Specification (GAS)
GAS-013 — Music Generator Agent

Document ID: GAS-013
Title: Music Generator Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: MusicGeneratorAgent
Constitutional Class: Production Executor
Accountability: Production Orchestrator Agent
Domain: Audio, Music, Sound Design & Silence Ontology (GO-110)

2. Purpose

The Music Generator Agent composes and generates the musical score for the production. It translates the emotional arc, scene moods, and music cues into generated music tracks that support the narrative without overwhelming it.

3. Responsibilities

3.1 Score Composition

- Generate music tracks for each act based on the emotional arc
- Compose scene-specific music that reflects the scene's mood and energy
- Generate dramatic stings for irreversible moments
- Ensure music supports rather than competes with narration

3.2 Music Cue Management

- Translate music cue specifications (zone, volume, tempo, key) into generation parameters
- Manage music volume relative to narration and SFX
- Handle silence zones where music should be absent
- Generate ambient beds for scenes without specific musical requirements

3.3 Emotional Modulation

- Ensure music reflects the emotional arc (warm in Act 1, tense in Act 2, resolved in Act 3)
- Modulate music intensity to match scene energy
- Use musical motifs that recur across the production
- Avoid music that telegraphs emotion (sad music for sad scenes)

3.4 Asset Management

- Store generated music in the asset store with metadata
- Tag music with act, scene, mood, and emotional zone
- Register music assets for downstream agents
- Track generation provenance (zone, mood, tempo, timestamp)

4. Inputs

- Narrative Subgraph (emotional arc, scene moods)
- Music cue specifications (from Scene Planner Agent)
- Music generation provider configuration

5. Outputs

- Generated music tracks per act and scene
- Dramatic sting for irreversible moment
- Music consistency validation report
- Generation provenance log

6. Quality Criteria

- Every scene has appropriate music or intentional silence
- Music supports the emotional arc without overwhelming it
- Dramatic stings are impactful but not melodramatic
- Music volume is balanced with narration
- All music is properly tagged and stored

7. Dependencies

- Requires: Narrative Subgraph, Music cue specifications
- Provides: Generated music tracks
- Depends on: Scene Planner Agent, Story Architect Agent
- Supports: Audio Mixing Agent
