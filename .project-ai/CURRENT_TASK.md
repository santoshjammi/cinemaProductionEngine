---
objective: Stabilize the videoGen / CINEMA PRODUCTION ENGINE pipeline from approved synopsis input to a playable final MP4.
status: paperclip_mission_loaded
done_conditions:
  - Paperclip project `videoGen` exists and mirrors TASK-001 through TASK-034.
  - GENESIS artifacts and PKP flow are locked to the approved EW001 production contract.
  - Scene 4 can be rendered with real FLUX visuals and local TTS.
  - Final MP4 is assembled and validated without placeholders.
next_actions:
  - TASK-001 — Create the Stability Baseline
  - TASK-002 — Freeze the Current Production Contract
files_in_scope:
  - .intelligence/PROJECT_MEMORY.md
  - .project-ai/PROJECT_MEMORY.yaml
  - .project-ai/project-memory.json
  - TASK_GRAPH.md
---

## Current Mission
- Run the Cinema Production Engine as a fail-closed, local-first pipeline.
- Keep GENESIS textual-only, PROMETHEUS render-only, and ORACLE validation-only.
- Prioritise the Phase 0 freeze before any generation work.

## Notes
- The mission has been mirrored to Paperclip as a dedicated `videoGen` project.
- Child tasks are grouped by the five stability phases.
