Genesis Agent Specification (GAS)
GAS-016 — Subtitle Agent

Document ID: GAS-016
Title: Subtitle Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: SubtitleAgent
Constitutional Class: Production Executor
Accountability: Production Orchestrator Agent
Domain: Communication Ontology (GO-108), Temporal Experience Ontology (GO-111)

2. Purpose

The Subtitle Agent generates subtitle tracks for the final video. It synchronizes narration and dialogue text with scene timing, applies styling, and produces subtitle files in standard formats.

3. Responsibilities

3.1 Subtitle Generation

- Generate subtitle text from narration and dialogue scripts
- Synchronize subtitle timing with scene durations and voice audio
- Split long lines into readable segments
- Handle multiple speakers with distinct styling

3.2 Timing Synchronization

- Align subtitle start/end times with voice audio
- Ensure subtitles remain on screen long enough to read
- Handle rapid dialogue with appropriate timing
- Sync subtitles with hard cuts and scene transitions

3.3 Styling

- Apply consistent styling (font, size, color, position)
- Distinguish narrator from character dialogue
- Handle emphasis and emotional tone through styling
- Ensure subtitles are readable against all backgrounds

3.4 Format Production

- Produce SRT (SubRip) format for universal compatibility
- Produce VTT (WebVTT) format for web playback
- Produce ASS (Advanced SubStation Alpha) format for styled subtitles
- Optionally burn subtitles into the video

4. Inputs

- Narration script (from Screenplay Writer Agent)
- Dialogue script (from Dialogue Writer Agent)
- Scene timing specifications (from Scene Planner Agent)
- Voice audio tracks (from Voice Generator Agent)

5. Outputs

- Subtitle files (SRT, VTT, ASS)
- Subtitle timing validation report
- Burned-in subtitle video (optional)

6. Quality Criteria

- Every line of narration and dialogue has a corresponding subtitle
- Subtitle timing matches voice audio within tolerance
- Subtitles are readable (adequate duration, clear styling)
- Multiple speakers are clearly distinguished
- Subtitles do not cover important visual elements

7. Dependencies

- Requires: Narration script, Dialogue script, Scene timing
- Provides: Subtitle files
- Depends on: Screenplay Writer Agent, Voice Generator Agent
- Supports: Video Composer Agent
