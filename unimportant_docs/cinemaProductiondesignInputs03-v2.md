I would give the agent a definitive answer rather than leaving these as open questions. At this point, you want to freeze the baseline and avoid further design churn.

⸻

Final Decisions — Cinema Production Engine v1 Baseline

1. Screenplay Format

Decision: Use a custom Movie OS Screenplay Specification.

Do not use a traditional Hollywood screenplay format.

Do not use free-form prose.

Instead, define a structured Markdown specification optimized for AI agents and production.

Each scene should contain standardized sections such as:

* Scene Metadata
* Narrative Purpose
* Emotional Intent
* Characters
* Dialogue
* Actions
* Emotional Beats
* Silence / Pauses
* Narration (optional)
* Director Notes
* Camera Intent
* Music Intent

This screenplay becomes the single canonical creative artifact.

Everything else is derived from it.

⸻

2. Grammar Storage

Decision: Store grammars inside Movie OS.

movie_os/
    grammars/
        psychological_cinema/
        kids_story/
        devotional/
        documentary/
        explainer/
        shorts/

Productions simply reference the grammar.

Example:

production:
  grammar: psychological_cinema

The grammar defines the creative rules.

The production contains the story.

The engine executes the grammar.

⸻

3. Timeline Compatibility

Decision: Maintain backward compatibility.

Never break existing productions.

Instead implement:

Legacy Timeline
↓
Migration Adapter
↓
Internal Timeline Model

All new engine features should operate on the new internal model.

Older productions should continue working without modification.

⸻

Additional Design Decisions

Production Folder

Adopt the canonical production structure.

productions/
    psychological/
        ew001/
            production.yaml
            dna.yaml
            research.md
            creative_brief.md
            director_notes.md
            outline.md
            screenplay.md
            music_score.yaml
            master_timeline.yaml
            manifest.yaml
            production_rules.yaml
            prompts/
            characters/
            environments/
            assets/
            renders/
            metadata/

A production folder must contain everything required to reproduce the production.

⸻

Canonical Source Hierarchy

The production should always flow in one direction:

Idea
↓
Research
↓
DNA
↓
Creative Brief
↓
Outline
↓
Screenplay
↓
Master Timeline
↓
Shot List
↓
Frame List
↓
Assets
↓
Render
↓
Evaluation
↓
Publishing

No downstream artifact should modify upstream creative content.

⸻

Production Grammar

The engine must never contain logic like:

if production_type == "kids":

Instead:

Production
↓
Grammar
↓
Rules
↓
Pipeline Configuration
↓
Execution

Each grammar defines:

* dialogue style
* pacing
* camera language
* music language
* narration rules
* lighting
* prompt templates
* evaluation criteria

⸻

Screenplay Ownership

The screenplay answers:

What happens?

The timeline answers:

How do we produce it?

The render pipeline answers:

How do we generate it?

Maintain this separation throughout the architecture.

⸻

Music Architecture

Use two layers.

Global

music_score.yaml

Defines:

* themes
* leitmotifs
* instruments
* emotional palette
* recurring musical identities

Scene

The timeline only references:

music:
  theme: loneliness
  intensity: 0.4
  transition: crossfade

Avoid duplicating detailed music configuration across scenes.

⸻

Characters

Treat characters as reusable production assets.

Instead of:

characters/
    ethan.md

Use:

characters/
    ethan/
        identity.yaml
        appearance.yaml
        psychology.yaml
        voice.yaml
        relationships.yaml
        reference_images/

This enables reuse across productions.

⸻

Environments

Apply the same pattern.

environments/
    apartment/
        identity.yaml
        lighting.yaml
        ambience.yaml
        camera.yaml
        reference_images/

Environments become reusable cinematic assets.

⸻

Production-Specific Files

Introduce three new files.

creative_brief.md

Defines:

* target audience
* emotional outcome
* viewer transformation
* runtime
* reference works
* production goals

director_notes.md

Defines:

* pacing philosophy
* visual language
* acting style
* emotional constraints
* cinematic intent

production_rules.yaml

Contains production-specific overrides such as:

* preferred voices
* subtitle behavior
* output targets
* camera restrictions
* rendering overrides

These are production-level decisions rather than grammar-level defaults.

⸻

Version Every Schema

Every structured document should include metadata similar to:

schema: movie_os.production.v1
version: 1.0.0
created_by:
updated_at:

This makes future migrations manageable.

⸻

Implementation Guidance

Proceed with Phase 1 using ew001 as the reference implementation only.

Do not design the architecture specifically for ew001.

Instead:

* Design the generic architecture first.
* Implement it using ew001.
* Ensure every design decision is reusable by future production grammars.

ew001 is a validation project, not the architectural template.

⸻

Success Criteria for Phase 1

Phase 1 is complete when:

* The new production folder structure is implemented.
* The Movie OS Screenplay Specification is defined and documented.
* story.md has been migrated to screenplay.md.
* The grammar system is operational and production-selectable.
* creative_brief.md, director_notes.md, and production_rules.yaml exist and are integrated.
* music_score.yaml is separated from scene-level cues.
* master_timeline.yaml references the screenplay rather than duplicating creative content.
* Existing productions continue to function through backward compatibility adapters.
* No production-specific logic has been embedded into the engine.

Once these criteria are met, you will have a stable foundation on which to build provider abstractions, ComfyUI/FLUX integration, prompt orchestration, character memory, and the remaining phases without needing another architectural redesign.