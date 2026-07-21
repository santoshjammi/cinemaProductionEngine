Genesis Specification (GSPEC)
GSPEC-011 — Production Plan Format

Document ID: GSPEC-011
Title: Production Plan Format Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GO-112 Production Planning Ontology

1. Purpose

This Specification defines the format for a Production Plan — the complete execution plan for a Genesis production session. The Production Plan is produced by the Production Orchestrator Agent and consumed by all downstream agents to understand stage ordering, dependencies, resource estimates, checkpoints, and fallback strategy. It is the authoritative source of truth for how a production will be executed.

2. Format

production_plan:
  production_id: "uuid"
  plan_id: "uuid"
  created_at: "ISO 8601"
  created_by: "string (agent name)"
  workflow_id: "string (GWS identifier, e.g. GWS-001)"
  estimated_duration_minutes: number
  distribution_target: "string (e.g. 'youtube', 'internal_archive')"

  scope:
    scene_count: integer
    character_count: integer
    environment_count: integer
    estimated_shot_count: integer
    estimated_frame_count: integer

  stages:
    - name: "string (unique stage name)"
      description: "string"
      agents: ["string (agent names or GAS IDs)"]
      parallel: boolean
      estimated_duration_minutes: number
      dependencies: ["string (stage names that must complete first)"]
      required_inputs: ["string (asset or PKG node references)"]
      outputs: ["string (asset or PKG node references)"]
      condition: "string (optional, condition under which this stage runs)"

  resources:
    compute:
      image_generation:
        count: integer
        estimated_per_unit_minutes: number
      voice_generation:
        count: integer
        estimated_per_unit_minutes: number
      music_generation:
        count: integer
        estimated_per_unit_minutes: number
      sfx_generation:
        count: integer
        estimated_per_unit_minutes: number
    storage:
      estimated_total_gb: number
    estimated_cost: "string (optional)"

  checkpoints:
    - stage: "string (stage name)"
      description: "string (what is validated at this checkpoint)"
      validation_required: boolean
      validator_agents: ["string (optional, agents that must pass)"]

  fallback:
    retry_limit: integer
    timeout_minutes: integer
    skip_on_failure: ["string (agent names that may be skipped)"]
    escalate_to: "string (agent name, default: GovernanceAgent)"

  termination:
    success_criteria: "string (description of completion conditions)"
    max_revisions: integer
    max_runtime_minutes: number

3. Field Definitions

- production_id: UUID of the parent production
- plan_id: Unique identifier for this plan version
- created_at: ISO 8601 timestamp of plan creation
- created_by: Agent that produced the plan (normally ProductionOrchestratorAgent)
- workflow_id: Identifier of the workflow this plan instantiates
- estimated_duration_minutes: Total estimated wall-clock duration
- distribution_target: Intended distribution platform
- scope: Summary of production scope
- stages: Ordered list of execution stages
- stages.name: Unique stage identifier
- stages.agents: Agents invoked during this stage
- stages.parallel: Whether agents in this stage run concurrently
- stages.dependencies: Stages that must complete before this stage begins
- stages.required_inputs: Assets or PKG nodes required to start this stage
- stages.outputs: Assets or PKG nodes produced by this stage
- stages.condition: Optional condition under which the stage runs (for conditional workflows)
- resources: Estimated resource requirements
- checkpoints: Validation gates between stages
- checkpoints.validation_required: Whether a validator must pass before the next stage begins
- checkpoints.validator_agents: Agents that must pass the checkpoint
- fallback: Failure handling policy
- fallback.retry_limit: Maximum retries per agent
- fallback.timeout_minutes: Per-agent timeout
- fallback.skip_on_failure: Agents whose failure does not abort the production
- fallback.escalate_to: Agent to escalate unrecoverable failures to
- termination: Conditions for ending the session
- termination.max_revisions: Maximum revision loop iterations
- termination.max_runtime_minutes: Hard wall-clock limit

4. Validation Rules

- All stage names must be unique within the plan
- Stage dependencies must reference existing stage names
- No circular dependencies between stages
- Estimated durations must be positive numbers
- At least one checkpoint must be defined
- resources.compute.*.count must be non-negative
- resources.storage.estimated_total_gb must be non-negative
- fallback.retry_limit must be a non-negative integer
- fallback.timeout_minutes must be a positive integer
- termination.max_revisions must be a non-negative integer
- termination.max_runtime_minutes must be a positive number
- workflow_id must reference a registered workflow (GWS-001 through GWS-004)
- Every stage must have at least one agent
- Every stage must have a description
- Checkpoint stage names must reference existing stages
- If a stage is marked parallel, it must have more than one agent

5. Example

production_plan:
  production_id: "a1b2c3d4-..."
  plan_id: "p1l2a3n4-..."
  created_at: "2026-07-19T10:00:00Z"
  created_by: "ProductionOrchestratorAgent"
  workflow_id: "GWS-001"
  estimated_duration_minutes: 95
  distribution_target: "youtube"

  scope:
    scene_count: 12
    character_count: 2
    environment_count: 4
    estimated_shot_count: 38
    estimated_frame_count: 60

  stages:
    - name: "narrative_architecture"
      description: "Build narrative subgraph and scene structure"
      agents: ["StoryArchitectAgent"]
      parallel: false
      estimated_duration_minutes: 10
      dependencies: []
      required_inputs: ["ProductionBrief"]
      outputs: ["NarrativeSubgraph", "SceneStructure"]
    - name: "scene_planning"
      description: "Produce shot plans for all scenes"
      agents: ["ScenePlannerAgent"]
      parallel: false
      estimated_duration_minutes: 15
      dependencies: ["narrative_architecture"]
      required_inputs: ["NarrativeSubgraph"]
      outputs: ["ShotPlans"]
    - name: "generation"
      description: "Generate images, voice, music, and SFX in parallel"
      agents: ["ImageGeneratorAgent", "VoiceGeneratorAgent", "MusicGeneratorAgent", "SFXGeneratorAgent"]
      parallel: true
      estimated_duration_minutes: 40
      dependencies: ["scene_planning"]
      required_inputs: ["ShotPlans", "MusicScoreSpecification"]
      outputs: ["ImageAssets", "VoiceAssets", "MusicAssets", "SFXAssets"]
    - name: "assembly"
      description: "Mix audio and compose video"
      agents: ["AudioMixingAgent", "VideoComposerAgent"]
      parallel: false
      estimated_duration_minutes: 15
      dependencies: ["generation"]
      required_inputs: ["ImageAssets", "VoiceAssets", "MusicAssets", "SFXAssets"]
      outputs: ["AssembledCut"]
    - name: "evaluation"
      description: "Run all evaluation agents in parallel"
      agents: ["StoryQualityAgent", "DialogueQualityAgent", "VisualConsistencyAgent", "AudioMixQualityAgent", "EmotionScoreAgent", "CharacterConsistencyAgent", "YouTubeReadinessAgent"]
      parallel: true
      estimated_duration_minutes: 10
      dependencies: ["assembly"]
      required_inputs: ["AssembledCut"]
      outputs: ["EvaluationReports"]

  resources:
    compute:
      image_generation:
        count: 60
        estimated_per_unit_minutes: 0.5
      voice_generation:
        count: 12
        estimated_per_unit_minutes: 0.2
      music_generation:
        count: 12
        estimated_per_unit_minutes: 0.3
      sfx_generation:
        count: 24
        estimated_per_unit_minutes: 0.1
    storage:
      estimated_total_gb: 5.5

  checkpoints:
    - stage: "scene_planning"
      description: "Validate shot plans before generation"
      validation_required: true
      validator_agents: ["ProductionOrchestratorAgent"]
    - stage: "assembly"
      description: "Validate assembled cut before evaluation"
      validation_required: true
      validator_agents: ["VisualConsistencyAgent", "AudioMixQualityAgent"]
    - stage: "evaluation"
      description: "Certify production readiness"
      validation_required: true
      validator_agents: ["RevisionAgent"]

  fallback:
    retry_limit: 2
    timeout_minutes: 30
    skip_on_failure: ["YouTubeReadinessAgent"]
    escalate_to: "GovernanceAgent"

  termination:
    success_criteria: "All mandatory evaluation agents pass and Revision Agent certifies readiness"
    max_revisions: 3
    max_runtime_minutes: 240

6. Usage

- Produced by: Production Orchestrator Agent (GAS-026)
- Consumed by: All downstream agents (for stage context), Revision Agent (for revision scoping), Governance Agent (for escalation context)
- Stored in: Production Knowledge Graph as a ProductionPlan node linked to the production
- Versioned: Each plan revision produces a new version; previous versions are retained for auditability
- Validated by: Production Orchestrator Agent before dispatch begins

7. Evolution Policy

This Specification may evolve through additive extensions governed by the Specification Governance Framework. New optional fields may be added without breaking existing plans. Removal or renaming of existing fields requires a major version bump and a migration plan.