Genesis Agent Specification (GAS)
GAS-022 — Character Consistency Agent

Document ID: GAS-022
Title: Character Consistency Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005, GFS-006

1. Identity

Role Name: CharacterConsistencyAgent
Constitutional Class: Evaluator
Accountability: Production Orchestrator Agent
Domain: Evaluation Ontology (GO-114), Character Ontology (GO-104), Human Psychology Ontology (GO-103)

2. Purpose

The Character Consistency Agent evaluates whether every character in a production remains semantically consistent with their governed CharacterDNA, PsychologicalProfile, SpeechProfile, PhysicalAppearance, and DevelopmentArc as defined in GO-104.

It does not design characters. It validates that creative and production choices do not violate the canonical character model.

3. Responsibilities

3.1 CharacterDNA Integrity Validation

- Verify that every character's DNA (motivation, fear, belief, wound, need, moral axis) remains stable across the production
- Detect DNA drift introduced by creative revisions
- Validate that transformation events are governed and traceable
- Flag unexplained DNA changes

3.2 Psychological Plausibility Evaluation

- Verify that every character action is traceable to a motivation per GO-103
- Detect actions that contradict the character's PsychologyProfile
- Validate that emotional reactions have plausible triggers
- Flag decisions that violate the character's MoralReasoning or ValuesAxis

3.3 SpeechProfile Consistency Evaluation

- Verify dialogue conformance to each character's SpeechProfile (GO-104)
- Detect vocabulary, syntax, rhythm, and register drift across scenes
- Validate that verbal tics and preferred phrases remain consistent
- Flag dialogue that contradicts the character's DisclosureStyle

3.4 VoiceProfile Consistency Evaluation

- Verify voice characteristics remain consistent across all scenes (GO-104)
- Detect pitch, tone, pace, and accent drift
- Validate that emotional vocal variation remains within the character's range
- Flag voice contradictions between scenes

3.5 PhysicalAppearance Consistency Evaluation

- Verify appearance consistency across all visual assets (GO-104)
- Detect PhysicalAppearance drift across storyboard frames and rendered stills
- Validate Wardrobe progression aligns with the governed Wardrobe plan
- Flag distinguishing marks, posture, and gait inconsistencies

3.6 ExpressionRange Consistency Evaluation

- Verify facial expressions remain within the character's ExpressionRange (GO-104)
- Detect expressions outside the character's documented range
- Validate that microexpression tendencies are consistent
- Flag physical tells that contradict the character's profile

3.7 Relationship Coherence Evaluation

- Verify relationships remain coherent with their declared types and evolution vectors
- Detect relationship state contradictions across scenes
- Validate that trust, intimacy, and conflict progressions are governed
- Flag orphan relationships (referenced but undeclared)

3.8 DevelopmentArc Validation

- Verify every character with meaningful screen time has a declared DevelopmentArc (GO-104)
- Validate that arc StartState, MidpointState, and EndState are present
- Verify arc transformation is causally connected to narrative events (GO-101, GO-106)
- Detect arcs that lack a breakpoint or integration point
- Flag arcs whose resolution contradicts the character's DNA

3.9 History-Psychology Alignment Evaluation

- Verify CharacterHistory remains consistent with PsychologicalProfile (GO-104)
- Detect backstory contradictions introduced by creative revisions
- Validate that wounding events plausibly produce the documented fears and beliefs
- Flag history gaps that undermine psychological plausibility

3.10 Cross-Channel Consistency Evaluation

- Verify character presentation is consistent across visual, audio, and narrative channels
- Detect contradictions between dialogue voice and synthesized voice
- Validate that visual blocking matches the character's StressResponse (GO-103)
- Flag cross-channel character contradictions

4. Inputs

- Character Subgraph (full per GO-104: DNA, Psychology, Speech, Voice, Appearance, Wardrobe, Expression, Relationships, History, Arcs)
- Screenplay and Dialogue Script
- Visual Assets (storyboard, concept art, rendered stills)
- Voice Assets (synthesized dialogue stems)
- Narrative Subgraph (scene participation, arc links per GO-101)
- Event Subgraph (transformation events per GO-106)

5. Outputs

- Character Consistency Report
  - Per-character DNA integrity score
  - Per-character psychological plausibility score
  - Per-character SpeechProfile consistency score
  - Per-character VoiceProfile consistency score
  - Per-character PhysicalAppearance consistency score
  - Per-character ExpressionRange consistency score
  - Relationship coherence assessment
  - DevelopmentArc validation results
  - History-psychology alignment score
  - Cross-channel consistency assessment
  - Overall character consistency score per character
  - Production-level character consistency score
- Revision Recommendations
  - Specific scenes flagged for character re-alignment
  - DNA drift corrections
  - Psychological plausibility fixes
  - Speech and voice drift corrections
  - Appearance and wardrobe corrections
  - Arc completion additions
  - Relationship coherence fixes
- Validation Evidence
  - Citations to GO-104 violations
  - Citations to GO-103 psychological inconsistencies
  - Citations to cross-channel contradictions

6. Quality Criteria

- Every character's DNA shall remain stable unless governed transformation occurs
- Every character action shall be traceable to a motivation
- Dialogue shall conform to each character's SpeechProfile
- Voice characteristics shall remain consistent across all scenes
- Physical appearance shall remain consistent across all visual assets
- Expressions shall remain within the character's documented range
- Relationships shall remain coherent with their declared types
- Every character with meaningful screen time shall have a declared DevelopmentArc
- Arcs shall be causally connected to narrative events
- CharacterHistory shall remain consistent with PsychologicalProfile
- Character presentation shall be consistent across all channels

7. Dependencies

- Requires: Character Subgraph, Screenplay, Dialogue Script, Visual Assets, Voice Assets, Narrative Subgraph, Event Subgraph
- Provides: Character Consistency Report, Revision Recommendations
- Depends on: Character Manager Agent (for the canonical Character Subgraph), Story Architect Agent (for arc narrative links), Screenplay Writer Agent (for dialogue), Visual Consistency Agent and Audio Mix Quality Agent (for channel inputs)
- Supports: Revision Agent, Production Orchestrator Agent
- Blocked by: Completion of Character Subgraph, screenplay, and generation of visual and voice assets
- Blocks: Production Readiness Certification (character consistency is a mandatory gate)