Genesis Ontology (GO)
GO-104 — Character Ontology

Document ID: GO-104

Title: Genesis Character Ontology

Version: 1.0.0

Status: Domain Ontology

Authority: Derived from GFS-000 through GFS-009 and GO-001 through GO-102

1. Purpose

The Genesis Character Ontology establishes the canonical semantic model for representing, reasoning about, validating, and evolving characters within any Genesis production.

It defines the concepts, properties, relationships, constraints, and lifecycle semantics required to model intentional participants in a narrative — independent of medium, technology, or creative genre.

The ontology applies equally to:

* Feature films
* Short films
* YouTube essays
* Educational content
* Devotional storytelling
* Children's stories
* Interactive narratives
* Audio dramas
* Documentary subjects
* Future narrative formats

A Character in Genesis is not a person.

A Character is an intentional semantic entity that drives narrative transformation and audience experience.

2. Foundational Principle

**Characters are governed transformation engines, not biographies.**

A character is defined by what they want, what they fear, what they believe, how they change, and how they create audience experience.

Backstory, appearance, and voice are instruments that serve transformation — not the character itself.

3. Architectural Position

```text
Audience Experience
        │
Narrative
        │
Character
        │
├── Identity
├── Psychology
├── Voice
├── Appearance
├── Relationships
├── History
└── Development Arc
```

Character bridges narrative and world.

4. Core Concepts

The Character Ontology introduces the following canonical concepts:

* Character
* CharacterDNA
* PhysicalAppearance
* PsychologicalProfile
* SpeechProfile
* VoiceProfile
* Wardrobe
* ExpressionRange
* Relationship
* CharacterHistory
* DevelopmentArc

These extend the Character Domain of GO-001.

5. CharacterDNA

CharacterDNA is the canonical, immutable identity signature of a character.

A CharacterDNA shall define:

* Stable Identifier
* Canonical Name
* Archetype
* Core Motivation
* Core Fear
* Core Belief
* Core Wound
* Core Need
* Moral Axis
* Transformation Vector

The CharacterDNA is the semantic anchor that all other character sub-profiles reference.

The DNA is intentionally stable across revisions; surface traits may change, the DNA shall not.

6. PhysicalAppearance

PhysicalAppearance defines the embodied presentation of a character.

Properties include:

* BodyType
* Height
* Build
* SkinTone
* HairStyle
* HairColor
* EyeColor
* FacialFeatures
* DistinguishingMarks
* AgeAppearance
* Posture
* Gait
* PhysicalCondition

PhysicalAppearance shall remain consistent with the character's history, environment, and physical capability.

7. PsychologicalProfile

PsychologicalProfile defines the internal architecture of a character.

Properties include:

* PersonalityTraits
* AttachmentStyle
* EmotionalBaseline
* EmotionalRange
* CognitiveStyle
* DefenseMechanisms
* Values
* Biases
* BlindSpots
* SelfImage
* ShadowSelf
* MoralReasoning

The PsychologicalProfile governs plausibility of action, reaction, and dialogue.

8. SpeechProfile

SpeechProfile defines how a character uses language.

Properties include:

* VocabularyRegister
* SentenceLength
* SyntaxPattern
* Rhythm
* VerbalTics
* PreferredPhrases
* AvoidedPhrases
* MetaphorDomain
* HumorStyle
* SilenceBehavior
* InterruptBehavior
* DisclosureStyle

SpeechProfile is the canonical input for dialogue generation and consistency validation.

9. VoiceProfile

VoiceProfile defines the sonic identity of a character.

Properties include:

* Pitch
* Tone
* Resonance
* Pace
* Accent
* Dialect
* IntonationPattern
* Breathiness
* VocalWeight
* AgeOfVoice
* EmotionalColor
* VoiceReference

VoiceProfile informs downstream voice synthesis but remains medium-independent.

10. Wardrobe

Wardrobe defines the visual presentation of the character through clothing and accessories.

Properties include:

* DefaultOutfit
* SceneVariants
* ColorPalette
* Fabric
* FormalityLevel
* Condition
* Accessories
* Grooming
* WardrobeProgression

Wardrobe shall reflect psychological state, social position, and narrative progression.

11. ExpressionRange

ExpressionRange defines the emotional vocabulary available to a character's face and body.

Properties include:

* BaselineExpression
* ActiveExpressions
* SuppressedExpressions
* MicroexpressionTendency
* PhysicalTells
* EmotionalLeakage
* RestraintLevel
* ExpressiveFlexibility

ExpressionRange governs performance direction and visual consistency.

12. Relationship

A Relationship is a governed semantic edge between two characters (or between a character and a world entity).

Properties include:

* Source
* Target
* RelationshipType
* PowerAxis
* IntimacyLevel
* TrustLevel
* ConflictAxis
* History
* CurrentState
* EvolutionVector

Canonical relationship types include:

* Ally
* Antagonist
* Mentor
* Rival
* Family
* Romantic
* Authority
* Dependent
* Stranger
* Mirror

Relationships are bidirectional but not necessarily symmetric.

13. CharacterHistory

CharacterHistory defines events prior to the narrative present.

Properties include:

* OriginEvent
* WoundingEvent
* FormativeEvents
* LostRelationships
* AcquiredSkills
* Failures
* Triumphs
* Secrets
* UnresolvedWounds
* CulturalBackground

CharacterHistory shall remain consistent with the character's PsychologicalProfile and SpeechProfile.

14. DevelopmentArc

A DevelopmentArc defines the governed transformation of a character across the narrative.

Properties include:

* ArcType
* StartState
* MidpointState
* EndState
* TransformationTrigger
* ResistancePoint
* Breakpoint
* IntegrationPoint
* CostOfTransformation
* ResolutionState

Canonical arc types include:

* Growth Arc
* Fall Arc
* Redemption Arc
* Awakening Arc
* Tragic Arc
* Flat Arc (the character changes the world, not themselves)
* Corruption Arc
* Healing Arc

An arc shall be causally connected to narrative events defined in GO-101.

15. Semantic Relationships

Illustrative semantic relationships include:

```text
Character
        │
has
        │
CharacterDNA

Character
        │
participates_in
        │
Scene

Character
        │
undergoes
        │
DevelopmentArc

Character
        │
relates_to
        │
Character

Character
        │
expresses_through
        │
SpeechProfile
```

Additional governed relationships include:

* wants, fears, believes, needs, hides, reveals, mirrors, opposes, mentors, betrays, forgives, abandons, protects.

16. Composition Principles

A Character is composed from:

```text
Character =
    CharacterDNA
  + PhysicalAppearance
  + PsychologicalProfile
  + SpeechProfile
  + VoiceProfile
  + Wardrobe
  + ExpressionRange
  + CharacterHistory
  + Relationships
  + DevelopmentArc
```

Composition shall be preferred over monolithic character definitions.

17. Inheritance Hierarchy

```text
Thing
  ↓
Creative Thing
  ↓
Narrative Thing
  ↓
Character
  ↓
Protagonist / Antagonist / Supporting / Background
```

Specialized character classes inherit core properties and add role-specific constraints.

18. Character Lifecycle

Characters inherit lifecycle semantics from GO-003.

```text
Proposed
   ↓
Discovered
   ↓
Defined
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

Lifecycle progression reflects character maturity, not narrative position.

19. Validation Rules

Characters shall be validated for:

* DNA completeness (motivation, fear, belief, wound, need present)
* Psychological plausibility of actions
* SpeechProfile consistency across all scenes
* VoiceProfile consistency across all scenes
* Appearance consistency across all scenes
* Relationship coherence (no orphan or contradictory edges)
* Arc presence for every character with meaningful screen time
* Arc causality (transformation traceable to events)
* History–psychology alignment
* Creator intent alignment
* Constitutional compliance

Validation evaluates the character model, not actor performance.

20. Relationship with the Production Knowledge Graph

Characters are represented in the PKG as interconnected semantic objects.

The graph stores:

* character nodes,
* DNA attributes,
* sub-profiles,
* relationship edges,
* arc progression,
* lifecycle state,
* validation status.

The ontology defines meaning; the PKG records instances.

21. Relationship with Other Ontologies

* GO-101 Narrative Ontology — characters participate in scenes and arcs
* GO-102 Audience Experience Ontology — characters produce audience emotion
* GO-105 World & Environment Ontology — characters inhabit environments
* GO-108 Communication Ontology — characters speak through dialogue
* GO-103 Human Psychology & Behavior Ontology — informs PsychologicalProfile
* GO-109 Visual Expression Ontology — informs Appearance, Wardrobe, ExpressionRange

22. Constitutional Invariants

The following principles are immutable:

* Characters are governed transformation engines.
* CharacterDNA is canonical and stable.
* Characters extend the Core Ontology.
* Characters remain medium-independent.
* Relationships carry semantic meaning.
* Arcs model transformation, not chronology.
* Creator intent governs character decisions.
* Validation measures semantic integrity.
* Character evolution remains governed.

23. Evolution Policy

The Character Ontology may evolve through additive extensions governed by the Constitutional Ontology Framework and the Governance Constitution.

Specialized character domains (e.g., Mythological Character Ontology, AI Character Ontology) shall inherit from this ontology rather than redefining its concepts.

24. Approval

This Ontology is approved as the canonical semantic model for characters within the Genesis Engine.

All character-oriented Production Knowledge Graphs, Production Knowledge Packages, domain ontologies, reasoning workflows, validation systems, and creative planning artifacts shall conform to this ontology.