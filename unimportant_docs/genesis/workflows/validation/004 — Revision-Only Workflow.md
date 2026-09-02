Genesis Workflow Specification (GWS)
GWS-004 — Revision-Only Workflow

Document ID: GWS-004
Title: Revision-Only Workflow
Version: 1.0.0
Status: Workflow Specification
Authority: Derived from GFS-005, GFS-006

1. Purpose

This Workflow defines a reduced execution sequence for running only the revision loop against an existing production. It is used when evaluation reports identify issues that need correction without re-running the full production pipeline. It modifies the canonical Production Knowledge Graph and produces a version bump.

2. Foundational Principle

**Revision is scoped and auditable.**

The Revision-Only Workflow shall modify only the assets and PKG nodes identified by the Revision Plan. All changes shall be recorded in the revision history with full provenance. The revision loop shall terminate within the configured maximum iteration count.

3. When to Use

- Evaluation reports identify specific, scoped issues in a completed production
- Targeted revisions are required without full re-execution
- Iterative refinement cycles after a full production run
- Post-evaluation corrections flagged by the Revision Agent

4. When Not to Use

- When a full re-generation is required — use GWS-001
- When only evaluation is required (no changes) — use GWS-003
- When the issues are unrecoverable — escalate to the Governance Agent

5. Workflow Stages

### 5.1 Stage 0: Initiation

Agent: Revision Agent

Input:
- Evaluation reports (from GWS-003 or the evaluation stage of GWS-001)
- Production Knowledge Graph (current state)
- Production plan
- Revision policy (max iterations, oscillation thresholds)

Output:
- Revision Plan (scoped work packages per agent)

Actions:
- Analyze evaluation reports to identify root causes
- Classify issues by domain (story, dialogue, visual, audio, emotion, character, platform)
- Determine which agents need to revise their output
- Estimate scope and impact of each revision
- Prioritize revisions by severity, dependency, and blast radius
- Detect scope conflicts and resolve using precedence rules from GWS-003
- Produce a Revision Plan with scoped work packages

### 5.2 Stage 1: Creative Revision (Conditional)

Condition: Story or dialogue issues are present in the evaluation reports

Agents:
- Story Architect Agent
- Screenplay Writer Agent
- Dialogue Writer Agent

Scope: Affected scenes only

Input:
- Revision Plan (creative work package)
- Current screenplay, narrative subgraph, dialogue script

Output:
- Revised screenplay, narrative subgraph, dialogue script

Actions:
- Revise only the scenes and dimensions flagged in the Revision Plan
- Record all changes in the revision history
- Do not modify assets outside the assigned scope

### 5.3 Stage 2: Planning Revision (Conditional)

Condition: Visual or audio planning issues are present in the evaluation reports

Agents:
- Scene Planner Agent
- Shot Planner Agent
- Music Composer Agent
- Prompt Builder Agent

Scope: Affected scenes only

Input:
- Revision Plan (planning work package)
- Revised screenplay (if Stage 1 ran)
- Current Shot Plan, Music Score Specification

Output:
- Revised Shot Plan, Music Score Specification, shot prompts

Actions:
- Revise only the plans and prompts flagged in the Revision Plan
- Re-validate revised plans per their format specifications
- Record all changes in the revision history

### 5.4 Stage 3: Execution Revision (Conditional)

Condition: Generation issues are present in the evaluation reports, or Stages 1–2 produced revised plans

Agents:
- Image Generator Agent
- Voice Generator Agent
- Music Generator Agent
- SFX Generator Agent

Scope: Affected assets only

Input:
- Revision Plan (execution work package)
- Revised shot prompts, music cues, sound design notes

Output:
- Revised generated assets

Actions:
- Regenerate only the assets flagged in the Revision Plan
- Reuse unchanged assets from the canonical PKG
- Record all new assets with provenance in the asset store

### 5.5 Stage 4: Re-Assembly (Conditional)

Condition: Stages 1–3 produced revised assets

Agents:
- Audio Mixing Agent
- Video Composer Agent

Input:
- Revised assets

Output:
- Revised assembled cut

Actions:
- Re-mix and re-assemble only the affected scenes
- Stitch revised scenes into the existing assembled cut

### 5.6 Stage 5: Re-Evaluation

Agents: All evaluation agents that reported issues in the triggering evaluation cycle

Input:
- Revised assets and assembled cut

Output:
- Updated evaluation reports

Actions:
- Re-evaluate only the dimensions and scenes that were revised
- Produce updated evaluation reports with pass/warn/fail per dimension
- Detect any new issues introduced by the revisions

### 5.7 Stage 6: Certification

Agent: Revision Agent (quality gate), Governance Agent (final certification)

Input:
- Updated evaluation reports

Output:
- Quality Gate Report
- Recertification decision

Actions:
- Verify that revisions addressed the identified issues
- Detect oscillating revisions (A→B→A) and flag for human review
- If all dimensions pass: certify and recommend promotion
- If issues remain and iteration count < max: loop back to Stage 0
- If issues remain and iteration count = max: escalate to the Governance Agent
- Produce a Quality Gate Report with pass/warn/fail verdict per dimension

6. Conditional Logic

- Stage 1 runs only if story or dialogue issues are present
- Stage 2 runs only if visual or audio planning issues are present, or if Stage 1 produced revised creative output
- Stage 3 runs only if generation issues are present, or if Stages 1–2 produced revised plans
- Stage 4 runs only if Stages 1–3 produced revised assets
- Stage 5 always runs (re-evaluation is mandatory)
- Stage 6 always runs (certification is mandatory)

7. Revision Loop Rules

- The revision loop shall terminate within the configured maximum iteration count (default: 3)
- Each iteration shall be recorded in the revision history with full provenance
- Oscillating revisions (A→B→A) shall be detected and flagged for human review
- Each iteration shall scope revisions to the minimum affected asset set
- No agent shall modify assets outside its assigned revision scope
- Conflicts between evaluation agents shall be resolved using precedence rules from GWS-003

8. Error Handling

- If a revision agent fails, retry up to the configured retry limit
- If a revision agent fails after retries, skip and mark the dimension as unresolved
- If re-evaluation fails, escalate to the Governance Agent
- If the revision loop exceeds the maximum iteration count, escalate to the Governance Agent
- All errors shall be recorded in the revision history

9. Inputs

- Evaluation reports
- Production Knowledge Graph (read/write)
- Production plan
- Revision policy

10. Outputs

- Revised PKG (version bump)
- Revision history (immutable log)
- Quality Gate Report
- Recertification decision

11. Constitutional Invariants

- Revision is scoped and auditable
- All changes shall be recorded in the revision history with full provenance
- The revision loop shall terminate within the configured maximum iteration count
- No agent shall modify assets outside its assigned revision scope
- Workflow evolution remains governed