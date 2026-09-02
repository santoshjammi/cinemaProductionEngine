Genesis Ontology (GO)
GO-201 — Psychological Cinema Ontology

Document ID: GO-201
Title: Psychological Cinema Ontology
Version: 1.0.0
Status: Specialized Ontology
Authority: Derived from GO-101 Narrative Ontology, GO-103 Human Psychology & Behavior Ontology, GO-001 Core Ontology

1. Purpose

This ontology defines the grammar-specific vocabulary for psychological cinema: films whose primary experience target is the inner life of a character rather than external plot. It supplies the concepts that the Psychology Reviewer (GAS-009) and the Story Architect (GAS-001) use to reason about psychological truth, attachment, defense, and the moments that define a psychological film.

This is a specialized ontology. It derives from GO-101 Narrative Ontology and conforms to GO-001 Core Ontology. It does not redefine any Core or Narrative concept.

2. Scope

In scope:
- Concepts that describe inner psychological states and their cinematic expression.
- Concepts that describe the relationship between psychology and narrative structure.
- Concepts that mark the moments a psychological film is built around.

Out of scope:
- Clinical psychology (GO-103 owns that).
- General narrative structure (GO-101 owns that).
- Visual grammar (GO-109 owns that).

3. Derivation Chain

GO-201 derives from GO-101 Narrative Ontology. It specializes the following GO-101 concepts:

- Experience → PsychologicalExperience
- Arc → PsychologicalArc
- Beat → PsychologicalBeat
- Moment → PsychologicalMoment
- Theme → PsychologicalTheme

It also references GO-103 for the underlying psychological vocabulary (AttachmentStyle, DefenseMechanism, EmotionalWithdrawal).

4. Core Concepts

4.1 PsychologicalTruth
The degree to which a character's behavior, dialogue, and inner state are consistent with how a real human in that situation would feel and act. PsychologicalTruth is the primary quality dimension of psychological cinema. It is scored by the Psychology Reviewer (GAS-009).

4.2 EmotionalWithdrawal
A character's progressive or sudden retreat from emotional engagement. Has direction (inward, outward), depth (surface, deep), and reversibility. Often the central arc of a psychological film.

4.3 AttachmentStyle
Inherited from GO-103. Specialized for cinema as: SecureOnScreen, AnxiousOnScreen, AvoidantOnScreen, DisorganizedOnScreen. Determines how a character responds to intimacy, loss, and threat within a scene.

4.4 DefenseMechanism
Inherited from GO-103. Cinematic specializations: ProjectionOnScreen, RationalizationOnScreen, DissociationOnScreen, IdealizationOnScreen, SplittingOnScreen. Defenses shape dialogue subtext and behavioral inconsistency.

4.5 IrreversibleMoment
A moment after which a character's psychological state cannot return to its prior equilibrium. Marked by a flag `irreversible: true`. Every psychological film must declare at least one IrreversibleMoment. It is the structural spine of the psychological arc.

4.6 AlmostMoment
A moment in which the character nearly achieves psychological change but retreats. Marked by `almost: true`. Often precedes or follows an IrreversibleMoment. Generates the specific ache that defines psychological cinema.

4.7 PsychologicalSubtext
The unspoken layer beneath dialogue and action. Carries the character's true state while the surface expresses the defense. Scored for consistency against the character's declared defense mechanism.

4.8 Witnessing
The audience's role in a psychological film: to perceive what the character cannot perceive about themselves. Witnessing is a first-class experience target, not a side effect of viewing.

4.9 EmotionalWithholding
The cinematic technique of denying the audience the emotional release they expect. Distinct from EmotionalWithdrawal (which is a character state). Withholding is a directorial choice expressed through edit, sound, and framing.

4.10 PsychologicalStakes
What the character stands to lose psychologically, as distinct from what they stand to lose situationally. Psychological cinema prioritizes PsychologicalStakes over situational stakes.

5. Relationships

GO-201 introduces the following relationships, all conforming to GO-002:

- `conceals` — PsychologicalSubtext conceals PsychologicalTruth. (DefenseMechanism → PsychologicalTruth)
- `reveals` — A moment reveals a concealed truth. (PsychologicalMoment → PsychologicalTruth)
- `blocks` — A defense blocks emotional engagement. (DefenseMechanism → EmotionalWithdrawal)
- `precedes` — An AlmostMoment often precedes an IrreversibleMoment. (AlmostMoment → IrreversibleMoment)
- `witnessed_by` — A psychological state is witnessed by the audience. (PsychologicalState → Witnessing)
- `withholds` — A scene withholds an expected emotional release. (Scene → EmotionalWithholding)

6. Lifecycle

All GO-201 concepts follow the GO-003 lifecycle: Draft → Proposed → Validated → Approved → Certified → Superseded. Psychological findings that fail validation are routed to the Psychology Reviewer for adjudication.

7. Validation Rules

- A psychological film must declare at least one IrreversibleMoment.
- Every EmotionalWithdrawal must reference a triggering DefenseMechanism.
- Every PsychologicalSubtext must reference the DefenseMechanism producing it.
- An AlmostMoment and an IrreversibleMoment may not occupy the same beat.
- PsychologicalTruth scores below the constitutional threshold block certification.

8. Interaction With Agents

- GAS-001 Story Architect authors IrreversibleMoment and AlmostMoment nodes.
- GAS-009 Psychology Reviewer scores PsychologicalTruth and validates the rules above.
- GAS-021 Emotion Score Agent uses GO-201 concepts to score emotional arc realization.
- GAS-022 Character Consistency Agent uses AttachmentStyle and DefenseMechanism to verify behavioral consistency.

9. Non-Goals

This ontology does not define:

- The clinical taxonomy of pathology (owned by GO-103).
- The visual language for expressing psychology (owned by GO-109).
- The pacing of psychological revelation (owned by GO-111).

10. Approval

This ontology is binding for every production classified as psychological cinema. Conflicts with parent ontologies are resolved in favor of the parent.