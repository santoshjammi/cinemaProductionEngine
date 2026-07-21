Genesis Workflow Specification (GWS)
GWS-003 — Evaluation-Only Workflow

Document ID: GWS-003
Title: Evaluation-Only Workflow
Version: 1.0.0
Status: Workflow Specification
Authority: Derived from GFS-005, GFS-006

1. Purpose

This Workflow defines a reduced execution sequence for running only the evaluation agents against an existing production. It is used for quality assessment, regression testing, and A/B comparison without re-executing creative or production stages.

The workflow does not modify the Production Knowledge Graph. It produces evaluation reports and revision recommendations only.

2. Foundational Principle

**Evaluation is non-destructive.**

The Evaluation-Only Workflow shall never alter the canonical Production Knowledge Graph or any production asset.

All findings are produced as separate evaluation artifacts that may be reviewed, accepted, or discarded by the Production Orchestrator Agent.

3. When to Use

- Quality assessment of a completed production
- A/B comparison of different production versions
- Regression testing after revisions
- Pre-certification readiness check
- Periodic quality monitoring of archived productions
- Evaluation of imported productions not built within Genesis

4. When Not to Use

- When creative or production work is incomplete — use the Full Production Workflow (GWS-001)
- When the Production Knowledge Graph is missing or corrupt — use the Recovery Workflow
- When modifications to the PKG are required — use the Revision Workflow (GWS-004)

5. Workflow Stages

### 5.1 Stage 0: Initiation

Agent: Production Orchestrator Agent

Input:
- Production Knowledge Package (PKG)
- Assembled production assets (screenplay, visuals, audio, assembled cut)
- Evaluation scope (full, partial, single-domain)

Output:
- Evaluation plan
- Scope declaration
- Agent dispatch schedule

Actions:
- Verify PKG integrity
- Verify all required assets are present
- Determine which evaluation agents are in scope
- Confirm evaluation is non-destructive

### 5.2 Stage 1: Parallel Evaluation

Agents (executed in parallel):
- Story Quality Agent (GAS-017)
- Dialogue Quality Agent (GAS-018)
- Visual Consistency Agent (GAS-019)
- Audio Mix Quality Agent (GAS-020)
- Emotion Score Agent (GAS-021)
- Character Consistency Agent (GAS-022)
- YouTube Readiness Agent (where applicable)

Input:
- Production Knowledge Graph
- Screenplay
- Generated assets (visual, audio, assembled cut)
- Character Subgraph
- Environment Subgraph
- Narrative Subgraph
- Audience Experience Plan

Output:
- Per-agent evaluation reports
- Per-agent revision recommendations
- Per-agent validation evidence

Parallel Execution Rules:
- All evaluation agents shall execute concurrently
- No evaluation agent shall block another
- No evaluation agent shall modify shared state
- Each agent operates on a read-only snapshot of the PKG
- Agents shall not communicate with each other during evaluation
- Agent timeouts shall be governed by the Evaluation Plan

### 5.3 Stage 2: Synthesis

Agent: Revision Agent

Input:
- All evaluation reports from Stage 1
- Per-agent revision recommendations
- Per-agent validation evidence

Output:
- Consolidated evaluation report
- Prioritized revision recommendation list
- Cross-agent conflict resolution notes
- Overall production quality score

Actions:
- Merge findings from all evaluation agents
- Detect contradictions between agent findings
- Resolve contradictions using governed precedence rules
- Prioritize revisions by severity and impact
- Produce a single consolidated evaluation artifact

### 5.4 Stage 3: Reporting

Agent: Production Orchestrator Agent

Input:
- Consolidated evaluation report
- Prioritized revision recommendation list

Output:
- Final evaluation report
- Production readiness indicator (for evaluation-only context)
- Recommended next action

Actions:
- Present the consolidated report to the creator or orchestrator
- Indicate whether the production would pass full readiness certification
- Recommend one of: accept, revise, regenerate, or escalate

6. Parallel Execution Rules

- All Stage 1 evaluation agents shall run in parallel
- Each agent shall receive an identical read-only snapshot of the PKG
- No inter-agent communication is permitted during Stage 1
- Agent failures shall not abort the workflow; failed agents shall be reported as unavailable in the synthesis
- Timeouts shall be governed per the Evaluation Plan
- Resource contention shall be managed by the Production Orchestrator Agent

7. Precedence Rules for Conflicting Findings

When evaluation agents produce conflicting findings, the following precedence applies:

1. Constitutional violations (any agent) — highest precedence
2. Character Consistency Agent findings — over Dialogue Quality Agent on voice matters
3. Visual Consistency Agent findings — over Story Quality Agent on visual continuity
4. Audio Mix Quality Agent findings — over Emotion Score Agent on audio-emotion matters
5. Emotion Score Agent findings — over Story Quality Agent on emotional trajectory
6. Story Quality Agent findings — default precedence on narrative matters

Conflicts that cannot be resolved by precedence shall be flagged for human review.

8. Inputs

- Production Knowledge Package (read-only)
- Screenplay
- Generated visual assets
- Generated audio assets
- Assembled cut
- Evaluation scope declaration
- Evaluation plan

9. Outputs

- Per-agent evaluation reports
- Consolidated evaluation report
- Prioritized revision recommendation list
- Production readiness indicator
- Recommended next action

10. Quality Criteria

- The workflow shall not modify the PKG
- All in-scope evaluation agents shall complete or be reported as unavailable
- All findings shall carry citations to governed ontologies
- All inferred findings shall carry confidence and evidence
- The consolidated report shall reconcile conflicts explicitly
- The production readiness indicator shall be defensible against the findings

11. Dependencies

- Requires: Production Knowledge Package, Screenplay, Generated Assets, Assembled Cut
- Provides: Consolidated Evaluation Report, Revision Recommendations
- Depends on: All evaluation agents (GAS-017 through GAS-022), Revision Agent, Production Orchestrator Agent
- Does not modify: Production Knowledge Graph, any production asset
- May trigger: Revision Workflow (GWS-004) if revisions are accepted

12. Constitutional Invariants

- Evaluation is non-destructive.
- All evaluation agents shall operate on read-only snapshots.
- Parallel evaluation shall not permit inter-agent communication.
- Findings shall carry citations and evidence.
- Inferred findings shall carry confidence.
- Conflicts shall be reconciled explicitly.
- The workflow shall remain platform-independent.
- Workflow evolution remains governed.

13. Evolution Policy

This Workflow may evolve through additive extensions governed by the Workflow Governance Framework.

New evaluation agents may be added to Stage 1 without breaking the workflow, provided they conform to the parallel execution rules.