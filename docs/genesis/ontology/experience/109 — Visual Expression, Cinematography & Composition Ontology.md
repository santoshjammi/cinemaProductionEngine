Genesis Ontology (GO)
GO-109 — Visual Expression, Cinematography & Composition Ontology

Document ID: GO-109

Title: Genesis Visual Expression, Cinematography & Composition Ontology

Version: 1.0.0

Status: Domain Ontology

Authority: Derived from GFS-000 through GFS-009 and GO-001 through GO-108

1. Purpose

The Genesis Visual Expression, Cinematography & Composition Ontology establishes the canonical semantic model for representing, reasoning about, validating, and evolving the visual language of any Genesis production.

It defines the concepts, properties, relationships, constraints, and lifecycle semantics required to model shot types, camera movements, lighting setups, composition patterns, color theory, and visual progression — independent of any specific camera, renderer, or production technology.

The ontology applies equally to:

* Feature films
* Short films
* YouTube productions
* Educational content
* Devotional storytelling
* Children's stories
* Interactive narratives
* Animated productions
* Documentary productions
* Future visual formats

Visual expression in Genesis is not decoration.

Visual expression is governed semantic communication.

2. Foundational Principle

**Every visual choice is a governed semantic act.**

Shot, angle, movement, light, color, and composition shall serve narrative, character, emotion, and audience experience.

Visual choices that do not serve meaning shall be flagged as decoration.

3. Architectural Position

```text
Scene
        │
Shot
        │
├── ShotType
├── CameraMovement
├── LightingSetup
├── CompositionPattern
├── ColorTreatment
└── VisualProgression
```

Visual expression bridges scene and presentation.

4. Core Concepts

The Visual Expression, Cinematography & Composition Ontology introduces the following canonical concepts:

* Shot
* ShotType
* ShotScale
* CameraAngle
* CameraMovement
* CameraPosition
* LightingSetup
* CompositionPattern
* ColorTreatment
* ColorPalette
* VisualMotif
* VisualProgression
* VisualRhythm
* DepthStaging
* BlockingPattern
* LensPerspective
* FocusStrategy
* TransitionType

These extend the World Domain of GO-001 and the Environment sub-profiles of GO-105.

5. Shot

A Shot is the canonical governed unit of visual expression.

A Shot shall define:

* Stable Identifier
* Scene
* ShotType
* ShotScale
* CameraAngle
* CameraMovement
* LightingSetup
* CompositionPattern
* ColorTreatment
* Subject
* NarrativePurpose
* EmotionalPurpose
* Duration
* Confidence
* Evidence

Every Shot shall declare both a NarrativePurpose and an EmotionalPurpose.

6. ShotType

ShotType defines the governed functional category of a shot.

Canonical types include:

* EstablishingShot
* WideShot
* FullShot
* MediumShot
* CloseUp
* ExtremeCloseUp
* OverTheShoulder
* PointOfView
* InsertShot
* ReactionShot
* TwoShot
* GroupShot
* AerialShot
* Cutaway
* InsertDetail
* MontageShot

7. ShotScale

ShotScale defines the governed framing size relative to the subject.

Canonical scale values include:

* ExtremeWide
* Wide
* MediumWide
* Medium
* MediumClose
* CloseUp
* ExtremeCloseUp

ShotScale shall be selected to serve the intended audience experience (GO-102).

8. CameraAngle

CameraAngle defines the governed vertical and horizontal relationship of camera to subject.

Canonical angles include:

* EyeLevel
* HighAngle
* LowAngle
* DutchTilt
* TopDown
* WormsEye
* Overhead
* ShoulderLevel

Angle carries semantic meaning: power, vulnerability, disorientation, omniscience.

9. CameraMovement

CameraMovement defines the governed motion of the camera during a shot.

Canonical movements include:

* Static
* Pan
* Tilt
* Dolly
* Truck
* Tracking
* Crane
* Steadicam
* Handheld
* ZoomIn
* ZoomOut
* RackFocus
* WhipPan
* Gimbal
* Drone
* CombinationMove

Every movement shall declare its narrative and emotional justification.

Movement without justification shall be flagged.

10. CameraPosition

CameraPosition defines the governed spatial placement of the camera.

Properties include:

* SpatialPosition
* Height
* Distance
* AngleToSubject
* LineOfAction
* LineOfCrossing
* CoverageRole

CameraPosition shall respect the 180-degree rule unless a governed crossing is justified.

11. LightingSetup

LightingSetup defines the governed lighting design of a shot.

Properties include:

* KeyLight (position, intensity, quality)
* FillLight
* BackLight
* AmbientLight
* PracticalLights
* ColorTemperature
* ContrastRatio
* ShadowBehavior
* LightingStyle (naturalistic, stylized, chiaroscuro, high-key, low-key, silhouette)

LightingSetup shall remain consistent with the environment's LightingProfile (GO-105).

12. CompositionPattern

CompositionPattern defines the governed arrangement of visual elements within the frame.

Canonical patterns include:

* RuleOfThirds
* GoldenRatio
* CenterComposition
* Symmetry
* Asymmetry
* LeadingLines
* FramingWithinFrame
* NegativeSpace
* DepthLayering
* DiagonalComposition
* TriangularComposition
* HeadroomControl
* LookRoomControl
* BlockingPattern

Composition shall serve narrative focus and emotional intent.

13. ColorTreatment

ColorTreatment defines the governed chromatic identity of a shot.

Properties include:

* PaletteReference (to GO-105 ColorPalette)
* Saturation
* Contrast
* Brightness
* HueShift
* ColorGrade
* SymbolicColorUsage
* EmotionalColorMapping

ColorTreatment shall remain consistent with the production's color governance.

14. ColorPalette

ColorPalette is defined in GO-105 and specialized here for shot-level application.

Properties include:

* DominantColors
* AccentColors
* EmotionalAssociation
* CharacterAssociation
* SymbolicAssociation
* ProgressionAcrossNarrative

15. VisualMotif

A VisualMotif is a governed recurring visual element that carries thematic meaning.

Properties include:

* MotifElement
* SymbolicMeaning
* RecurrencePattern
* VariationPattern
* EvolutionAcrossNarrative

Motifs shall be tracked across the PKG for thematic consistency.

16. VisualProgression

VisualProgression defines the governed evolution of visual language across the narrative.

Properties include:

* StartVisualState
* MidpointVisualState
* EndVisualState
* ProgressionDriver
* ProgressionCurve
* Justification

VisualProgression shall align with the narrative arc (GO-101) and character arcs (GO-104).

17. VisualRhythm

VisualRhythm defines the governed pacing of visual information.

Properties include:

* ShotDurationDistribution
* CutFrequency
* MovementFrequency
* StillnessPeriods
* RhythmPattern (steady, accelerating, decelerating, pulsing)

VisualRhythm shall align with the narrative pacing domain of GO-101.

18. DepthStaging

DepthStaging defines the governed use of depth within the frame.

Properties include:

* ForegroundElements
* MidgroundElements
* BackgroundElements
* DepthLayersActive
* DepthSymbolism

19. BlockingPattern

BlockingPattern defines the governed spatial arrangement of subjects within the shot.

Properties include:

* SubjectPositions
* MovementPaths
* PowerGeometry
* RelationshipGeometry
* SpatialTension

20. LensPerspective

LensPerspective defines the governed optical characteristics of the shot.

Properties include:

* FocalLengthClass (wide, normal, telephoto, macro)
* DepthOfField
* PerspectiveCompression
* DistortionBehavior

LensPerspective is medium-independent; it describes intent, not equipment.

21. FocusStrategy

FocusStrategy defines the governed use of focus within the shot.

Properties include:

* FocusSubject
* FocusPulls
* RackFocusTargets
* SelectiveFocus
* DeepFocus
* ShallowFocus

22. TransitionType

TransitionType defines the governed movement between shots.

Canonical transitions include:

* HardCut
* MatchCut
* JumpCut
* Dissolve
* Fade
* Wipe
* WhipPanTransition
* SmashCut
* LCut
* JCut

Transitions shall declare narrative or emotional justification.

23. Semantic Relationships

Illustrative semantic relationships include:

```text
Scene
        │
contains
        │
Shot

Shot
        │
governed_by
        │
CompositionPattern

Shot
        │
serves
        │
NarrativePurpose

LightingSetup
        │
derives_from
        │
LightingProfile

VisualMotif
        │
supports
        │
Theme
```

All predicates shall conform to GO-002.

24. Composition Principles

A Shot is composed from:

```text
Shot =
    ShotType
  + ShotScale
  + CameraAngle
  + CameraMovement
  + CameraPosition
  + LightingSetup
  + CompositionPattern
  + ColorTreatment
  + Subject
  + NarrativePurpose
  + EmotionalPurpose
```

25. Inheritance Hierarchy

```text
Thing
  ↓
Creative Thing
  ↓
Visual Thing
  ↓
Shot
  ↓
LiveAction / Animated / Hybrid / Generative
```

26. Visual Lifecycle

Shots inherit lifecycle semantics from GO-003.

```text
Proposed
   ↓
Designed
   ↓
Reasoned
   ↓
Validated
   ↓
Approved
   ↓
Production Ready
   ↓
Deprecated
   ↓
Archived
```

27. Validation Rules

Visual expression shall be validated for:

* NarrativePurpose presence
* EmotionalPurpose presence
* Composition coherence
* Lighting–environment consistency (GO-105)
* Color governance compliance
* Continuity (180-degree rule, eyeline match, screen direction)
* Movement justification
* Transition justification
* Motif consistency
* VisualProgression alignment with narrative arc
* Creator intent alignment
* Constitutional compliance

28. Relationship with the Production Knowledge Graph

Shots are represented in the PKG as nodes connected by transition edges.

The graph stores:

* shot nodes,
* composition references,
* lighting references,
* color references,
* motif references,
* progression edges,
* lifecycle state,
* validation status.

29. Relationship with Other Ontologies

* GO-101 Narrative Ontology — shots serve scenes
* GO-104 Character Ontology — shots frame characters
* GO-105 World & Environment Ontology — shots visualize environments
* GO-102 Audience Experience Ontology — shots produce audience emotion
* GO-111 Temporal Experience Ontology — visual rhythm informs editing
* GO-002 Semantic Relationship Catalog — provides `contains`, `serves`, `supports`

30. Constitutional Invariants

The following principles are immutable:

* Every visual choice is a governed semantic act.
* Shots shall declare narrative and emotional purpose.
* Visual expression extends the Core Ontology.
* Visual expression remains medium-independent.
* Continuity shall be governed.
* Color governance shall be respected.
* Creator intent governs visual design.
* Validation measures semantic integrity.
* Visual evolution remains governed.

31. Evolution Policy

This Ontology may evolve through additive extensions governed by the Constitutional Ontology Framework and the Governance Constitution.

Specialized visual domains (e.g., Animated Cinematography Ontology, VR Cinematography Ontology) shall inherit from this ontology rather than redefining its concepts.

32. Approval

This Ontology is approved as the canonical semantic model for visual expression, cinematography, and composition within the Genesis Engine.

All visual-oriented Production Knowledge Graphs, Production Knowledge Packages, domain ontologies, reasoning workflows, validation systems, and creative planning artifacts shall conform to this ontology.