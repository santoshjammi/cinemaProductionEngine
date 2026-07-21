Genesis Workflow Specification (GWS)
GWS-002 — Scene-Only Workflow

Document ID: GWS-002
Title: Scene-Only Workflow
Version: 1.0.0
Status: Workflow Specification
Authority: Derived from GFS-005

1. Purpose

This Workflow defines a reduced execution sequence for generating a single scene or a small number of scenes. It is used for iteration, testing, and refinement without running the full production pipeline. It is the primary workflow for rapid prototyping of visual style, prompt tuning, audio balance, and character consistency checks.

The workflow operates on a temporary working state derived from the canonical Production Knowledge Graph. It does not modify the PKG unless the creator explicitly promotes the scene output.

2. Foundational Principle

**Scene-Only is non-canonical by default.**

The Scene-Only Workflow shall operate on a copy of the relevant PKG subgraph. Results are written to a temporary working area. Promotion to the canonical PKG requires explicit creator approval via the Production Orchestrator Agent.

3. When to Use

- Rapid iteration on a specific scene's visuals, audio, or pacing
- Testing new prompts, character designs, or lighting setups
- Debugging visual or audio issues in a single scene
- A/B comparison of alternative shot plans for one scene
- Validating a single scene before committing to full production

4. When Not to Use

- When the full production needs to be generated — use GWS-001
- When only evaluation is required — use GWS-003
- When revisions to an existing production are required — use GWS-004
- When cross-scene consistency must be validated — use GWS-001

5. Workflow Stages

### 5.1 Stage 0: Initiation

Agent: Production Orchestrator Agent

Input:
- Scene brief (single scene description or scene number referencing the PKG)
- Production Knowledge Graph (read access)

Output:
- Scene production plan
- Working state handle

Actions:
- Verify the scene brief is well-formed
- Snapshot the relevant PKG subgraph (Scene, Character, Environment, Visual Style)
- Determine which agents are in scope for this scene
- Confirm the workflow is non-canonical by default

### 5.2 Stage 1: Scene Planning

Agent: Scene Planner Agent

Input:
- Scene brief
- Snapshotted subgraph

Output:
- Shot Plan for the scene (per GSPEC-009)

Actions:
- Decompose the scene into shots
- Assign shot sizes, camera movements, durations
- Build prompt context per shot

### 5.3 Stage 2: Prompt Building

Agent: Prompt Builder Agent

Input:
- Shot Plan
- Character references
- Visual Style node

Output:
- Shot prompts (one per frame)

Actions:
- Compose prompts from the Prompt Library and Shot Plan
- Inject character anchors, environment anchors, style qualifiers
- Apply negative prompts where required

### 5.4 Stage 3: Execution (Parallel)

Agents (executed in parallel):
- Image Generator Agent
- Voice Generator Agent (if dialogue or narration present)
- Music Generator Agent (if music cue assigned)
- SFX Generator Agent (if ambient or spot effects required)

Input:
- Shot prompts, scene context, music cue, sound design notes

Output:
- Generated scene assets (images, voice tracks, music track, SFX tracks)

Parallel Execution Rules:
- All execution agents shall run concurrently
- No agent shall block another
- Each agent operates on the working state snapshot
- Agents shall not communicate with each other during execution
- Agent failures shall be reported but shall not abort the workflow
- Timeouts shall be governed by the Scene Production Plan

### 5.5 Stage 4: Assembly

Agents:
- Audio Mixing Agent
- Video Composer Agent

Input:
- Generated scene assets

Output:
- Rendered scene video

Actions:
- Mix voice, music, and SFX per the scene's ducking profile
- Assemble images into a timed sequence per the Shot Plan
- Combine audio and video into a single rendered scene

### 5.6 Stage 5: Evaluation

Agents (executed in parallel):
- Visual Consistency Agent
- Audio Mix Quality Agent
- Emotion Score Agent (optional)

Input:
- Rendered scene

Output:
- Scene quality report

Actions:
- Evaluate visual consistency against the Visual Style node
- Evaluate audio mix quality against loudness and balance targets
- Evaluate emotional trajectory for the scene (optional)
- Produce a consolidated scene quality report

### 5.7 Stage 6: Reporting

Agent: Production Orchestrator Agent

Input:
- Rendered scene
- Scene quality report

Output:
- Scene iteration report
- Promotion recommendation

Actions:
- Present the rendered scene and quality report to the creator
- Recommend one of: accept and promote, revise (re-run Scene-Only), or escalate

6. Parallel Execution Rules

- Stage 3 execution agents shall run in parallel
- Stage 5 evaluation agents shall run in parallel
- No inter-agent communication is permitted during parallel stages
- Each agent operates on a read-only snapshot of the working state
- Agent failures shall be reported as unavailable; the workflow shall continue with available agents

7. Error Handling

- If the Scene Planner Agent fails, abort the workflow and report
- If a Stage 3 agent fails, mark its output as unavailable and continue with remaining agents
- If assembly fails due to missing assets, report the missing assets and retry the failed Stage 3 agent
- If evaluation fails, present the rendered scene without a quality report and flag for manual review
- All errors shall be recorded in the working state for auditability

8. Usage Notes

- Use for rapid iteration on specific scenes
- Use for testing new prompts or character designs
- Use for debugging visual or audio issues
- Does not modify the canonical PKG unless explicitly promoted
- Promoted scenes replace their canonical counterparts and trigger a PKG version bump

9. Dependencies

- Requires: Scene brief, PKG read access, working state allocation
- Provides: Rendered scene, scene quality report, promotion recommendation
- Depends on: Scene Planner Agent, Prompt Builder Agent, Image/Voice/Music/SFX Generator Agents, Audio Mixing Agent, Video Composer Agent, Visual Consistency Agent, Audio Mix Quality Agent
- Does not modify: Canonical PKG (unless promoted)
- May trigger: Full Production Workflow (GWS-001) if the creator chooses to expand

10. Constitutional Invariants

- Scene-Only is non-canonical by default
- Parallel execution shall not permit inter-agent communication
- All generated assets shall carry provenance
- Workflow evolution remains governed