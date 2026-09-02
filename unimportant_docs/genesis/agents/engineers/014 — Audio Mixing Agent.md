Genesis Agent Specification (GAS)
GAS-014 — Audio Mixing Agent

Document ID: GAS-014
Title: Audio Mixing Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: AudioMixingAgent
Constitutional Class: Production Executor
Accountability: Production Orchestrator Agent
Domain: Audio, Music, Sound Design & Silence Ontology (GO-110)

2. Purpose

The Audio Mixing Agent combines voice, music, and SFX tracks into a single mixed audio track per scene. It manages volume levels, fade in/out transitions, silence zones, and ensures the final audio mix is balanced and emotionally appropriate.

3. Responsibilities

3.1 Audio Mixing

- Mix voice, music, and SFX tracks into a single scene audio track
- Apply volume normalization across all tracks
- Manage fade in/out transitions at scene boundaries
- Handle silence zones (silence_before, silence_after, silence_instead)

3.2 Volume Management

- Set voice volume as the primary audio layer
- Set music volume to support without competing (default 0.6)
- Set SFX volume to enhance without distracting
- Apply dynamic range compression for consistent loudness

3.3 Scene Transitions

- Apply fade in at the start of each scene (1.5s default)
- Apply fade out at the end of each scene (1.5s default, 3s for final scene)
- Handle hard cuts for irreversible moments
- Ensure seamless transitions between scenes

3.4 Asset Management

- Store mixed audio in the asset store with metadata
- Tag audio with scene number and mix parameters
- Register mixed audio assets for downstream agents
- Track mixing provenance (source tracks, volumes, fades)

4. Inputs

- Voice audio tracks (from Voice Generator Agent)
- Music audio tracks (from Music Generator Agent)
- SFX audio tracks (from SFX Generator Agent)
- Scene timing specifications (from Scene Planner Agent)

5. Outputs

- Mixed audio track per scene
- Audio mix validation report
- Mixing provenance log

6. Quality Criteria

- Voice is clearly audible above music and SFX
- Music supports without competing
- SFX enhances without distracting
- Fade transitions are smooth
- Final loudness is consistent across all scenes

7. Dependencies

- Requires: Voice, Music, SFX audio tracks
- Provides: Mixed audio tracks
- Depends on: Voice Generator Agent, Music Generator Agent, SFX Generator Agent
- Supports: Video Composer Agent
