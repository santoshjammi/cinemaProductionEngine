Genesis Ontology (GO)
GO-301 — Production Ontology

Document ID: GO-301
Title: Production Ontology
Version: 1.0.0
Status: Specialized Ontology
Authority: Derived from GO-112 Production Planning Ontology, GO-001 Core Ontology

1. Purpose

This ontology defines the production-specific vocabulary used inside Genesis to describe how a certified Production Knowledge Package will be realized by the Studio Engine. It supplies the concepts that the Shot Planner, Prompt Builder, and the various Engineers use to describe shots, frames, renders, assets, providers, workflows, and capabilities.

This is a specialized ontology. It derives from GO-112 Production Planning Ontology and conforms to GO-001 Core Ontology. It does not redefine any Core concept.

2. Scope

In scope:
- Concepts describing the unit operations of media production.
- Concepts describing provider capabilities and selection.
- Concepts describing the workflow of producing a single asset.

Out of scope:
- The creative intent behind a shot (owned by GO-109, GO-101).
- The psychological weight of a shot (owned by GO-201).
- The actual rendering logic (owned by the Studio Engine).

3. Derivation Chain

GO-301 derives from GO-112 Production Planning Ontology. It specializes:

- Plan → ProductionPlan
- Task → ProductionTask
- Resource → Asset
- Agent → Provider
- Workflow → ProductionWorkflow

4. Core Concepts

4.1 Production
The top-level container for a single certified realization of a PKP. A Production references exactly one PKP version. It owns its own asset registry, telemetry, and revision history.

4.2 Shot
The atomic unit of media generation. A Shot is derived from a ShotPlan node in the PKG. It carries: shotId, duration, aspect ratio, composition intent, blocking, camera intent, and a list of generation tasks.

4.3 Frame
A single still image within a Shot. A Frame may be generated independently (for storyboards, key frames, references) or as part of a video sequence. Frames are the smallest addressable visual unit.

4.4 Render
The act of producing a Frame or a sequence of Frames from a Shot using a Provider. A Render is a task with inputs (prompt manifest, references), outputs (asset references), and a status lifecycle.

4.5 Asset
Any produced artifact referenced by the Studio Engine: image, audio, video, subtitle, mix. Assets are referenced by URI and tracked in the Studio Engine's asset registry. Genesis stores only the *plan* for assets, never the assets themselves.

4.6 Provider
An external service or local pipeline capable of performing a Render. Each Provider declares a Capability set. Provider selection happens in the Studio Engine, not in Genesis, but Genesis must declare the *required* capabilities so the Studio Engine can select correctly.

4.7 Workflow
A declared sequence of ProductionTasks that realizes a Shot or a Production. Workflows are owned by the Studio Engine but their *shape* is constrained by the WorkflowPlan nodes Genesis emits in the PKP.

4.8 Capability
A typed declaration of what a Provider can do: ImageGeneration, VideoGeneration, VoiceSynthesis, MusicGeneration, AudioMixing, SubtitleGeneration. Capabilities are matched against task requirements during provider selection.

4.9 ProductionTask
A single unit of work in a Workflow. Has inputs, expected outputs, required Capability, and a status. ProductionTasks are the atoms the Studio Engine schedules and tracks.

4.10 AssetReference
The pointer a ProductionTask emits when it completes. References an Asset in the Studio Engine's registry. Genesis never stores the Asset itself, only the plan that produced it.

5. Relationships

GO-301 introduces the following relationships, conforming to GO-002:

- `realizes` — A Production realizes a PKP. (Production → PKP)
- `derives_from` — A Shot derives from a ShotPlan. (Shot → ShotPlan)
- `contains` — A Shot contains Frames. (Shot → Frame)
- `produces` — A Render produces an Asset. (Render → Asset)
- `requires` — A ProductionTask requires a Capability. (ProductionTask → Capability)
- `executed_by` — A Render is executed by a Provider. (Render → Provider)
- `part_of` — A Frame is part of a Shot. (Frame → Shot)
- `references` — An AssetReference references an Asset. (AssetReference → Asset)

6. Lifecycle

All GO-301 concepts follow the GO-003 lifecycle with production-specific extensions:

- Production: Planned → InProgress → Completed → Superseded.
- Shot: Planned → Rendering → Rendered → Reviewed → Accepted → Rejected.
- Render: Queued → Running → Succeeded → Failed → Retried.
- Asset: Registered → Validated → Used → Archived.

Transitions are recorded by the Studio Engine, not by Genesis. Genesis records only the plan and the required capabilities.

7. Validation Rules

- Every Shot must reference a ShotPlan in the PKP.
- Every Render must declare a required Capability.
- Every ProductionTask must declare inputs and expected outputs.
- Every AssetReference must resolve to a registered Asset in the Studio Engine.
- A Production may not reference more than one PKP version.

8. Interaction With Agents

- GAS-010 Shot Planner authors ShotPlan nodes that GO-301 Shots derive from.
- GAS-006 Prompt Builder produces the prompt manifests that GO-301 Renders consume.
- GAS-011..016, GAS-025 Engineers consume GO-301 concepts when emitting production plans.
- GAS-019 Visual Consistency Agent validates Shot-to-Shot visual continuity using GO-301 references.

9. Boundary With the Studio Engine

GO-301 is the *last* ontology inside Genesis. The Studio Engine consumes GO-301 concepts but does not author them. Any production-side extension (e.g., a new provider type) is registered in the Studio Engine's own ontology, which may derive from GO-301 but may not modify it.

10. Non-Goals

This ontology does not define:

- The creative intent behind a shot (owned by GO-101, GO-109).
- The psychological weight of a shot (owned by GO-201).
- The actual rendering algorithms (owned by the Studio Engine).
- Provider pricing, SLA, or selection policy (owned by the Studio Engine).

11. Approval

This ontology is binding for every production plan emitted by Genesis. Conflicts with parent ontologies are resolved in favor of the parent.