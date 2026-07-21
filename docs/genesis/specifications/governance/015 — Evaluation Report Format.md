Genesis Specification (GSPEC)
GSPEC-012 — Evaluation Report Format

Document ID: GSPEC-012
Title: Evaluation Report Format Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GO-114 Evaluation Ontology

1. Purpose

This Specification defines the format for evaluation reports produced by all evaluation agents in the Genesis Engine. Every evaluation agent (Story Quality, Dialogue Quality, Visual Consistency, Audio Mix Quality, Emotion Score, Character Consistency, YouTube Readiness) shall produce a report conforming to this format. The Revision Agent consumes these reports to plan revisions, and the Production Orchestrator Agent consumes them to decide readiness.

2. Format

evaluation_report:
  report_id: "uuid"
  agent: "string (evaluating agent name)"
  agent_id: "string (GAS identifier, e.g. GAS-017)"
  production_id: "uuid"
  evaluated_at: "ISO 8601 timestamp"
  evaluation_scope: "full | partial | single-domain"
  overall_score: number (0.0-1.0)
  pass_verdict: boolean

  dimensions:
    - name: "string (dimension name, e.g. 'voice_consistency')"
      score: number (0.0-1.0)
      weight: number (0.0-1.0)
      status: "PASS | WARN | FAIL"
      findings:
        - finding_id: "uuid"
          severity: "CRITICAL | HIGH | MEDIUM | LOW | INFO"
          category: "string (e.g. 'voice_drift', 'subtext_missing')"
          description: "string (what was found)"
          location: "string (scene number, character key, timestamp, asset id)"
          evidence: "string (citation to governed ontology node or asset)"
          confidence: number (0.0-1.0)
          recommendation: "string (suggested corrective action)"
          target_agent: "string (agent responsible for the revision)"

  summary:
    critical_count: integer
    high_count: integer
    medium_count: integer
    low_count: integer
    info_count: integer
    dimension_count: integer
    passing_dimension_count: integer

  recommendations:
    - priority: "CRITICAL | HIGH | MEDIUM | LOW"
      action: "string (short action label)"
      target_agent: "string (agent that should perform the revision)"
      description: "string (detailed revision instruction)"
      affected_scenes: ["integer"]
      affected_assets: ["uuid"]

  metadata:
    workflow_id: "string (GWS identifier)"
    iteration: integer (revision loop iteration, 0 for first evaluation)
    duration_seconds: number

3. Field Definitions

- report_id: Unique identifier for this report
- agent: Human-readable name of the evaluating agent
- agent_id: GAS identifier of the evaluating agent
- production_id: UUID of the evaluated production
- evaluated_at: ISO 8601 timestamp of evaluation completion
- evaluation_scope: Scope of this evaluation
- overall_score: Weighted aggregate score across all dimensions
- pass_verdict: True if no CRITICAL findings exist and overall_score ≥ pass threshold
- dimensions: List of evaluated dimensions with scores and findings
- dimensions.name: Dimension identifier
- dimensions.score: Dimension score (0.0–1.0)
- dimensions.weight: Relative weight of this dimension; weights across dimensions must sum to 1.0
- dimensions.status: Pass/warn/fail status for this dimension
- findings: List of specific findings within the dimension
- findings.severity: Severity classification
- findings.location: Precise location of the finding (scene, character, timestamp, asset)
- findings.evidence: Citation to the governed ontology node or asset that supports the finding
- findings.confidence: Confidence in the finding (0.0–1.0); 1.0 for cited facts, <1.0 for inferences
- findings.recommendation: Suggested corrective action
- findings.target_agent: Agent responsible for performing the revision
- summary: Aggregate counts of findings by severity
- recommendations: Prioritized list of revision recommendations
- metadata: Workflow and iteration context

4. Validation Rules

- overall_score must be between 0.0 and 1.0
- Every dimension score must be between 0.0 and 1.0
- Dimension weights must sum to 1.0 (±0.001 tolerance)
- If any CRITICAL finding exists, pass_verdict must be false
- If overall_score is below the pass threshold (default 0.7), pass_verdict must be false
- Each recommendation must have a target_agent
- Each finding must have a location
- Each finding must have evidence citing a governed ontology node or asset
- Inferred findings (confidence < 1.0) must carry an explicit confidence value
- findings.target_agent must reference a registered agent in the Agent Registry
- recommendations.affected_scenes must reference existing scenes in the PKG
- recommendations.affected_assets must reference existing assets in the asset store
- evaluated_at must be a valid ISO 8601 timestamp
- agent_id must match a registered GAS identifier

5. Example

evaluation_report:
  report_id: "r1e2p3o4-..."
  agent: "DialogueQualityAgent"
  agent_id: "GAS-018"
  production_id: "a1b2c3d4-..."
  evaluated_at: "2026-07-19T14:32:00Z"
  evaluation_scope: "full"
  overall_score: 0.82
  pass_verdict: true

  dimensions:
    - name: "voice_consistency"
      score: 0.88
      weight: 0.4
      status: "PASS"
      findings:
        - finding_id: "f1-..."
          severity: "MEDIUM"
          category: "voice_drift"
          description: "Claire's register shifts from informal to formal in scene 4"
          location: "scene 4, character: claire"
          evidence: "GO-104 SpeechProfile claire.informal_register"
          confidence: 1.0
          recommendation: "Rewrite claire's lines in scene 4 to match informal register"
          target_agent: "DialogueWriterAgent"
    - name: "subtext_quality"
      score: 0.75
      weight: 0.3
      status: "WARN"
      findings:
        - finding_id: "f2-..."
          severity: "HIGH"
          category: "exposition"
          description: "Scene 7 contains expository dialogue that tells instead of shows"
          location: "scene 7, exchange 3"
          evidence: "GO-108 InteractionProtocol exposition_flag"
          confidence: 0.9
          recommendation: "Convert expository lines to action or subtext"
          target_agent: "ScreenplayWriterAgent"
    - name: "dramatic_effectiveness"
      score: 0.83
      weight: 0.3
      status: "PASS"
      findings: []

  summary:
    critical_count: 0
    high_count: 1
    medium_count: 1
    low_count: 0
    info_count: 0
    dimension_count: 3
    passing_dimension_count: 2

  recommendations:
    - priority: "HIGH"
      action: "rewrite_exposition"
      target_agent: "ScreenplayWriterAgent"
      description: "Convert expository dialogue in scene 7 exchange 3 to action or subtext"
      affected_scenes: [7]
      affected_assets: []

  metadata:
    workflow_id: "GWS-003"
    iteration: 0
    duration_seconds: 42.5

6. Usage

- Produced by: All evaluation agents (GAS-017 through GAS-023)
- Consumed by: Revision Agent (for revision planning), Production Orchestrator Agent (for readiness decisions)
- Stored in: Production Knowledge Graph as EvaluationReport nodes linked to the production
- Versioned: Each re-evaluation produces a new report; previous reports are retained for auditability

7. Evolution Policy

This Specification may evolve through additive extensions governed by the Specification Governance Framework. New optional fields may be added without breaking existing reports. Removal or renaming of existing fields requires a major version bump and a migration plan.