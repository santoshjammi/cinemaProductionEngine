Genesis Workflow Specification (GWS)
GWS-001 — Full Production Workflow

Document ID: GWS-001
Title: Full Production Workflow
Version: 1.0.0
Status: Workflow Specification
Authority: Derived from GFS-005, GFS-010, GFS-011

1. Purpose

This Workflow defines the complete agent execution sequence for a full Genesis production. It specifies the order of agent invocations, parallel execution paths, decision points, and revision loops.

2. Workflow Stages

2.1 Stage 0: Initiation

Agents: Production Orchestrator Agent
Input: Production Brief
Output: Production Plan, Session ID

The Production Orchestrator Agent receives the brief, validates it, creates a production session, and designs the production plan.

2.2 Stage 1: Discovery

Agents: Research Agent
Input: Production Brief
Output: Research findings integrated into PKG

The Research Agent identifies knowledge gaps, conducts research, and populates the PKG with domain knowledge.

2.3 Stage 2: Creative Design (Parallel)

Agents (parallel):
- Story Architect Agent
- Character Manager Agent
- Environment Manager Agent

Input: Production Brief, Research findings
Output: Narrative Subgraph, Character Subgraph, World Subgraph

These three agents work in parallel to establish the creative foundation. The Story Architect designs the narrative structure. The Character Manager models each character. The Environment Manager defines each location.

2.4 Stage 3: Creative Production (Sequential)

Agents (sequential):
- Psychology Reviewer Agent
- Screenplay Writer Agent
- Dialogue Writer Agent

Input: Narrative Subgraph, Character Subgraph, World Subgraph
Output: Screenplay, Dialogue Script, Narration Script

The Psychology Reviewer validates the creative foundation. The Screenplay Writer materializes the narrative into prose. The Dialogue Writer generates character dialogue.

2.5 Stage 4: Production Planning (Sequential)

Agents (sequential):
- Scene Planner Agent
- Shot Planner Agent
- Music Composer Agent
- Prompt Builder Agent

Input: Screenplay, Character Subgraph, World Subgraph
Output: Scene Plan, Shot Plan, Music Score, Shot Prompts

These agents translate the creative output into a detailed production plan.

2.6 Stage 5: Production Execution (Parallel)

Agents (parallel):
- Image Generator Agent
- Voice Generator Agent
- Music Generator Agent
- SFX Generator Agent

Input: Shot Prompts, Character References, Music Score
Output: Generated images, voice audio, music tracks, SFX tracks

These agents execute the production plan in parallel, generating all media assets.

2.7 Stage 6: Post-Production (Sequential)

Agents (sequential):
- Audio Mixing Agent
- Subtitle Agent
- Video Composer Agent

Input: Generated media assets
Output: Mixed audio, Subtitle files, Final video

These agents assemble the final output from the generated assets.

2.8 Stage 7: Evaluation (Parallel)

Agents (parallel):
- Story Quality Agent
- Dialogue Quality Agent
- Visual Consistency Agent
- Audio Mix Quality Agent
- Emotion Score Agent
- Character Consistency Agent
- YouTube Readiness Agent

Input: All production outputs
Output: Evaluation reports

All evaluation agents run in parallel to assess the production quality.

2.9 Stage 8: Revision (Conditional)

If any evaluation agent reports critical issues:
  Agent: Revision Agent
  Action: Dispatch revision requests to affected agents
  Loop: Return to the appropriate stage

If all evaluations pass:
  Proceed to Stage 9

2.10 Stage 9: Certification

Agent: Governance Agent
Input: Evaluation reports, Production Knowledge Package
Output: Production Readiness Certificate

The Governance Agent reviews all outputs and certifies production readiness.

3. Parallel Execution Rules

- Agents in the same parallel block may execute in any order
- Agents in different parallel blocks must execute in order
- Parallel execution is limited by available compute resources
- The Production Orchestrator Agent monitors all parallel execution

4. Revision Loop Rules

- Maximum 3 revision cycles per production
- Each revision cycle must address at least one critical issue
- If no progress is made after 2 cycles, escalate to Governance Agent
- The Revision Agent tracks all revision history

5. Error Handling

- If any agent fails, the Production Orchestrator Agent determines recovery
- Non-critical agent failures may be skipped
- Critical agent failures trigger the revision loop
- Unrecoverable errors terminate the production session
