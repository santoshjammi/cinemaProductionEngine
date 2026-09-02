Genesis Agent Specification (GAS)
GAS-012 — Voice Generator Agent

Document ID: GAS-012
Title: Voice Generator Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: VoiceGeneratorAgent
Constitutional Class: Production Executor
Accountability: Production Orchestrator Agent
Domain: Audio, Music, Sound Design & Silence Ontology (GO-110)

2. Purpose

The Voice Generator Agent synthesizes narration and dialogue audio for every scene. It dispatches text to the configured voice provider (EdgeTTS, etc.), manages voice profiles for character consistency, and stores the output in the asset store.

3. Responsibilities

3.1 Narration Synthesis

- Receive narration text from the Screenplay Writer Agent
- Dispatch text to the configured voice synthesis provider
- Manage voice selection per character (narrator, protagonist, supporting)
- Handle prosody overrides (rate, pitch, volume, emphasis)

3.2 Dialogue Synthesis

- Receive dialogue lines from the Dialogue Writer Agent
- Assign distinct voices to each character
- Manage emotional tone per line (fracture, whisper, intensity)
- Ensure dialogue timing matches scene duration

3.3 Voice Consistency

- Maintain consistent voice profiles across all scenes
- Adjust vocal delivery to reflect character emotional state
- Track vocal fracture moments for emotional impact
- Provide voice reference data to the Audio Mixing Agent

3.4 Asset Management

- Store generated audio in the asset store with metadata
- Tag audio with scene number, character, and emotional state
- Register audio assets for downstream agents
- Track generation provenance (voice, rate, pitch, timestamp)

4. Inputs

- Narration script (from Screenplay Writer Agent)
- Dialogue script (from Dialogue Writer Agent)
- Character voice profiles (from Character Manager Agent)
- Voice synthesis provider configuration

5. Outputs

- Generated narration audio per scene
- Generated dialogue audio per character per scene
- Voice consistency validation report
- Generation provenance log

6. Quality Criteria

- Every scene with narration has corresponding audio
- Character voices are distinct and consistent
- Vocal delivery matches the emotional state
- Audio duration matches scene duration
- All audio is properly tagged and stored

7. Dependencies

- Requires: Narration script, Dialogue script, Voice profiles
- Provides: Generated voice audio
- Depends on: Screenplay Writer Agent, Dialogue Writer Agent, Character Manager Agent
- Supports: Audio Mixing Agent
