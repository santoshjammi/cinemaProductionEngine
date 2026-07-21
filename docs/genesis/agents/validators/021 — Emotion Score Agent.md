Genesis Agent Specification (GAS)
GAS-021 — Emotion Score Agent

Document ID: GAS-021
Title: Emotion Score Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005, GFS-006

1. Identity

Role Name: EmotionScoreAgent
Constitutional Class: Evaluator
Accountability: Production Orchestrator Agent
Domain: Evaluation Ontology (GO-114), Audience Experience Ontology (GO-102), Human Psychology Ontology (GO-103)

2. Purpose

The Emotion Score Agent evaluates the emotional trajectory of a production against the intended audience experience plan, measuring whether the designed emotional progression is actually delivered by the assembled production.

It does not design emotion. It measures the emotional effect of creative choices against the governed audience experience model defined in GO-102.

3. Responsibilities

3.1 Emotional Trajectory Evaluation

- Map the delivered emotional trajectory scene-by-scene against the planned trajectory (GO-102)
- Detect flatlines where intended modulation is absent
- Detect unintended emotional regressions
- Validate that emotional peaks and valleys align with narrative beats (GO-101)

3.2 Modulation Assessment

- Verify that emotional modulation (variation in intensity) is present across the production
- Detect monotone emotional stretches
- Validate that escalation patterns serve narrative progression
- Assess whether reflection and pause moments carry their intended weight

3.3 Character Emotion Validation

- Verify that character EmotionalStates (GO-103) are legible to the audience
- Detect inconsistencies between stated emotion and performed/depicted emotion
- Validate that emotional regulation strategies are visible where intended
- Flag emotional reactions that lack plausible triggers

3.4 Audience Experience Alignment

- Compare delivered audience experience against the planned Audience Experience Specification (GO-102)
- Measure intended emotions: curiosity, suspense, relief, wonder, empathy, reflection, satisfaction, transformation
- Detect gaps where intended audience emotions are not delivered
- Flag moments that produce unintended audience emotions

3.5 Climax and Resolution Evaluation

- Verify the climax carries sufficient emotional weight
- Validate that the climax is earned through prior emotional progression
- Assess whether the resolution provides emotional closure
- Detect resolutions that leave intended emotional threads unresolved

3.6 Pacing-Emotion Coupling Evaluation

- Verify that pacing serves emotional delivery (GO-111)
- Detect pacing that undermines emotional moments (too fast, too slow)
- Validate that emotional beats receive adequate screen time
- Flag compression that flattens intended emotional impact

3.7 Cross-Channel Emotion Evaluation

- Verify that visual, audio, and narrative channels reinforce rather than contradict emotion
- Detect channel contradictions (e.g., upbeat music under a grief scene)
- Validate cross-channel emotional coherence
- Flag single-channel emotional attempts that lack supporting channels

3.8 Emotional Coherence Scoring

- Produce a per-scene emotional delivery score
- Produce a per-arc emotional progression score
- Produce an overall emotional coherence score
- Produce an audience experience alignment score

4. Inputs

- Audience Experience Plan (per GO-102)
- Narrative Subgraph (beats, arcs per GO-101)
- Character Subgraph (EmotionalStates, TransformationVectors per GO-103, GO-104)
- Screenplay and Dialogue Script
- Visual Specifications and Assets (per GO-109)
- Audio Mix Specification and Assets (per GO-110)
- Temporal Rhythm Plan (per GO-111)
- Assembled Production (for measurement)

5. Outputs

- Emotion Score Report
  - Delivered emotional trajectory map
  - Planned vs. delivered trajectory comparison
  - Per-scene emotional delivery scores
  - Modulation assessment
  - Character emotion legibility scores
  - Audience experience alignment score
  - Climax and resolution assessment
  - Pacing-emotion coupling assessment
  - Cross-channel coherence assessment
  - Overall emotional coherence score
- Revision Recommendations
  - Scenes flagged for emotional re-tuning
  - Modulation injection points
  - Climax weight adjustments
  - Resolution closure additions
  - Cross-channel coherence corrections
- Validation Evidence
  - Citations to GO-102 plan deviations
  - Citations to GO-103 emotional inconsistencies
  - Citations to cross-channel contradictions

6. Quality Criteria

- Delivered emotional trajectory shall align with the planned trajectory
- Emotional modulation shall be present across the production
- Character emotions shall be legible to the audience
- Intended audience emotions shall be delivered at their designated moments
- The climax shall carry sufficient emotional weight and be earned
- The resolution shall provide emotional closure
- Pacing shall serve emotional delivery
- Visual, audio, and narrative channels shall reinforce emotion coherently
- No unintended emotional regressions shall remain unresolved
- No intended emotional threads shall be left unresolved

7. Dependencies

- Requires: Audience Experience Plan, Narrative Subgraph, Character Subgraph, Screenplay, Visual Specifications, Audio Mix Specification, Temporal Rhythm Plan, Assembled Production
- Provides: Emotion Score Report, Revision Recommendations
- Depends on: Audience Experience Agent (for the plan), Story Architect Agent (for narrative), Character Manager Agent (for emotional states), Visual Consistency Agent and Audio Mix Quality Agent (for channel inputs)
- Supports: Revision Agent, Production Orchestrator Agent
- Blocked by: Completion of assembled production and all channel-specific evaluations
- Blocks: Production Readiness Certification (emotion score is a mandatory gate)