Genesis Agent Specification (GAS)
GAS-015 — Video Composer Agent

Document ID: GAS-015
Title: Video Composer Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: VideoComposerAgent
Constitutional Class: Production Executor
Accountability: Production Orchestrator Agent
Domain: Temporal Experience, Editing & Narrative Rhythm Ontology (GO-111)

2. Purpose

The Video Composer Agent assembles the final video from rendered images, mixed audio, and subtitle tracks. It applies Ken Burns effects, manages scene transitions, and produces the final deliverable in the configured output format.

3. Responsibilities

3.1 Image-to-Video Conversion

- Apply Ken Burns effects (zoom-in, zoom-out, pan-left, pan-right, static) to each shot image
- Generate video segments for each scene with the correct duration
- Apply unsharp filter for image crispness
- Ensure consistent resolution and frame rate across all segments

3.2 Scene Assembly

- Concatenate scene segments into the final video
- Apply crossfade or hard cut transitions between scenes
- Handle irreversible moment hard cuts
- Ensure total duration matches the production plan

3.3 Audio Integration

- Mix the final audio track into the video
- Ensure audio and video are synchronized
- Apply audio normalization for consistent loudness
- Handle multi-channel audio (stereo, 5.1) as configured

3.4 Subtitle Integration

- Burn subtitles into the video (or produce separate subtitle file)
- Synchronize subtitle timing with narration
- Apply subtitle styling (font, size, position, color)
- Handle subtitle positioning to avoid covering important visual elements

4. Inputs

- Rendered scene images (from Image Generator Agent)
- Mixed audio tracks (from Audio Mixing Agent)
- Subtitle tracks (from Subtitle Agent)
- Scene timing specifications (from Scene Planner Agent)

5. Outputs

- Final video file (MP4, H.264 + AAC)
- Video quality validation report
- Composition provenance log

6. Quality Criteria

- Final video plays without errors
- All scenes are present in the correct order
- Audio and video are synchronized
- Ken Burns effects are smooth
- Transitions between scenes are appropriate
- Final video meets the target duration within tolerance

7. Dependencies

- Requires: Scene images, Mixed audio, Subtitles
- Provides: Final video
- Depends on: Image Generator Agent, Audio Mixing Agent, Subtitle Agent
- Supports: (none — final production agent)
