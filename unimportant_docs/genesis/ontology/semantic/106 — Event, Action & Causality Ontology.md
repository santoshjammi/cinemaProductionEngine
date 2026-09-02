Genesis Ontology (GO)
GO-106 — Event, Action & Causality Ontology

Document ID: GO-106

Title: Genesis Event, Action & Causality Ontology

Version: 1.0.0

Status: Domain Ontology

Authority: Derived from GFS-000 through GFS-009 and GO-001 through GO-105

1. Purpose

The Genesis Event, Action & Causality Ontology establishes the canonical semantic model for representing, reasoning about, validating, and evolving events, actions, and causal structures within any Genesis production.

It defines the concepts, properties, relationships, constraints, and lifecycle semantics required to model what happens, why it happens, what it causes, and how chains of causation produce narrative transformation.

The ontology applies equally to:

* Feature films
* Short films
* YouTube essays
* Educational content
* Devotional storytelling
* Children's stories
* Interactive narratives
* Audio dramas
* Documentary reconstructions
* Future narrative formats

An Event in Genesis is not a moment.

An Event is a governed semantic unit of change.

2. Foundational Principle

**Every event is a governed unit of change.**

If nothing changes, there is no event.

If the change cannot be traced to a cause or traced forward to a consequence, the event is incomplete.

Causality is the connective tissue of narrative meaning.

3. Architectural Position

```text
Narrative
        │
Scene
        │
Event
        │
├── Trigger
├── Action
├── Participant
├── Consequence
└── CausalityChain
```

Event bridges scene and transformation.

4. Core Concepts

The Event, Action & Causality Ontology introduces the following canonical concepts:

* Event
* Action
* Activity
* StateChange
* Trigger
* Consequence
* CausalityChain
* CausalityLink
* Participant
* AgentOfChange
* Intention
* Outcome
* SideEffect
* RippleEffect
* ForkEvent
* MergeEvent

These extend the Event concept defined in GO-101.

5. Event

An Event is a governed semantic unit of change within the narrative.

An Event shall define:

* Stable Identifier
* Canonical Name
* EventType
* Participants
* Location
* Time
* Trigger
* StateBefore
* StateAfter
* Consequences
* NarrativePurpose
* Confidence
* Evidence

Every Event shall produce at least one StateChange.

Events that produce no change are not events.

6. Canonical Event Types

* NarrativeEvent — advances the story
* CharacterEvent — transforms a character state
* RelationalEvent — transforms a relationship
* EnvironmentalEvent — transforms an environment
* RevelatoryEvent — reveals hidden knowledge
* ConflictEvent — initiates, escalates, or resolves conflict
* DecisionEvent — captures a deliberate choice
* SymbolicEvent — carries thematic meaning
* OffscreenEvent — occurs outside the depicted frame but influences it
* BackgroundEvent — provides context without driving plot

7. Action

An Action is a deliberate act performed by an AgentOfChange (typically a Character).

An Action shall define:

* Agent
* Intention
* Method
* Target
* Means
* Context
* Outcome
* Cost
* SideEffect

Actions are the principal mechanism by which characters drive events.

Not every Event contains an Action; not every Action produces a single Event.

8. Activity

An Activity is a sustained pattern of Action over time.

Properties include:

* Participants
* Duration
* RepetitionPattern
* Objective
* EnvironmentalImpact
* SocialImpact

Activities provide behavioral texture rather than discrete change.

9. StateChange

A StateChange is the governed delta produced by an Event.

Properties include:

* AffectedEntity
* Property
* PreviousValue
* NewValue
* ChangeMagnitude
* Reversibility
* Visibility (to audience, to characters, to neither)

Every Event shall reference at least one StateChange.

10. Trigger

A Trigger is the governed condition that initiates an Event.

Trigger types include:

* CharacterDecision
* ExternalForce
* EnvironmentalChange
* Revelation
* Accident
* Deadline
* ConflictEscalation
* SocialPressure
* InternalUrge

Every Event shall declare its Trigger.

Events without a declared Trigger are incomplete and shall not enter the validated PKG.

11. Consequence

A Consequence is the governed downstream effect of an Event.

Properties include:

* SourceEvent
* AffectedEntity
* EffectType
* Magnitude
* Delay
* Visibility
* Reversibility
* NarrativeWeight

Consequences shall be traceable to their source Event.

12. CausalityChain

A CausalityChain is a governed sequence of Events connected by CausalityLinks.

Properties include:

* ChainId
* OriginEvent
* TerminalEvent
* Links
* TotalMagnitude
* BranchFactor
* ConvergenceFactor

CausalityChains shall be acyclic.

13. CausalityLink

A CausalityLink is a governed causal edge between two Events.

Properties include:

* SourceEvent
* TargetEvent
* LinkType (direct, indirect, contributory, enabling)
* Confidence
* Evidence
* Origin (explicit, inferred, assumed)

CausalityLinks use the `causes` predicate defined in GO-002.

14. Participant

A Participant is any entity that takes part in an Event.

Participants may be:

* Characters
* Environments
* Objects
* Groups
* Forces
* Symbols

Every Participant shall declare a ParticipantRole.

15. AgentOfChange

An AgentOfChange is the Participant whose deliberate action or decision initiates the Event.

Properties include:

* Agent
* Intention
* Capacity
* Willingness
* Responsibility

Not every Event has an AgentOfChange (e.g., environmental events), but every deliberate Event shall.

16. Intention

Intention defines the governed purpose behind an Action.

Properties include:

* ConsciousGoal
* UnconsciousDrive
* StatedMotive
* TrueMotive
* MoralFraming

Intention shall remain consistent with the agent's CharacterDNA (GO-104).

17. Outcome

An Outcome is the governed result of an Action.

Properties include:

* IntendedOutcome
* ActualOutcome
* UnintendedOutcome
* Gap (intended vs. actual)
* NarrativeSignificance

The gap between intended and actual outcome is a primary driver of dramatic irony.

18. SideEffect & RippleEffect

A SideEffect is an unintended consequence of an Action.

A RippleEffect is a consequence that propagates beyond the immediate participants.

Both shall be tracked for narrative coherence and world consistency.

19. ForkEvent & MergeEvent

A ForkEvent is an Event whose consequences diverge into multiple chains.

A MergeEvent is an Event where multiple causal chains converge.

Both are critical for modeling complex narrative structures (parallel storylines, convergent arcs).

20. Semantic Relationships

Illustrative semantic relationships include:

```text
Event
        │
causes
        │
Consequence

Action
        │
produces
        │
Event

Trigger
        │
initiates
        │
Event

Event
        │
part_of
        │
CausalityChain

Participant
        │
participates_in
        │
Event
```

All predicates shall conform to GO-002.

21. Composition Principles

An Event is composed from:

```text
Event =
    Trigger
  + Participants
  + Action (where applicable)
  + StateChange
  + Consequences
  + NarrativePurpose
```

Composition shall be preferred over monolithic event definitions.

22. Inheritance Hierarchy

```text
Thing
  ↓
Narrative Thing
  ↓
Event
  ↓
NarrativeEvent / CharacterEvent / RevelatoryEvent / ...
```

23. Event Lifecycle

Events inherit lifecycle semantics from GO-003.

```text
Proposed
   ↓
Triggered
   ↓
Depicted
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

24. Validation Rules

Events shall be validated for:

* Trigger presence
* Participant role clarity
* StateChange presence
* Consequence traceability
* CausalityChain acyclicity
* Intention–character alignment
* Plausibility within World rules (GO-105)
* Narrative purpose presence
* Confidence and evidence for inferred causality
* Constitutional compliance

25. Relationship with the Production Knowledge Graph

Events are represented in the PKG as nodes connected by CausalityLinks.

The graph stores:

* event nodes,
* trigger references,
* participant edges,
* state-change records,
* causality edges,
* lifecycle state,
* validation status.

26. Relationship with Other Ontologies

* GO-101 Narrative Ontology — events advance narrative
* GO-104 Character Ontology — characters act as AgentsOfChange
* GO-105 World & Environment Ontology — environments constrain event plausibility
* GO-107 Knowledge Ontology — events may produce revelations
* GO-108 Communication Ontology — dialogue is a class of Action
* GO-002 Semantic Relationship Catalog — provides `causes`, `precedes`, `depends_on`

27. Constitutional Invariants

The following principles are immutable:

* Every event is a governed unit of change.
* Events without triggers are incomplete.
* CausalityChains shall be acyclic.
* Inferred causality shall not be treated as fact.
* Events extend the Core Ontology.
* Events remain medium-independent.
* Creator intent governs event design.
* Validation measures semantic integrity.
* Event evolution remains governed.

28. Evolution Policy

This Ontology may evolve through additive extensions governed by the Constitutional Ontology Framework and the Governance Constitution.

Specialized event domains (e.g., Interactive Event Ontology, Documentary Event Ontology) shall inherit from this ontology rather than redefining its concepts.

29. Approval

This Ontology is approved as the canonical semantic model for events, actions, and causality within the Genesis Engine.

All event-oriented Production Knowledge Graphs, Production Knowledge Packages, domain ontologies, reasoning workflows, validation systems, and creative planning artifacts shall conform to this ontology.