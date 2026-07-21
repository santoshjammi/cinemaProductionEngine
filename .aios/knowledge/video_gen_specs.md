---
name: "video-generation-specs"
type: "domain_facts"
version: "2.0"
---

# VideoGen Technical & Creative Specs

## Technical Stack (from `specs/phase9_asset_store.md` & `PRD_v1.yaml`)
- **Backend**: Python/FastAPI, ProjectService (`backend/app/services/project_service.py`).
- **Frontend**: React with Playwright for E2E testing.
- **AI Core**: LM Studio (Local-first), Flux (Enhancement), ComfyUI (Workflow Engine).
- **Assembly**: OpenMontage (Timeline/Clip management).

## Creative Production Rules
- **Production Design Inputs**: Must strictly follow `cinemaProductiondesignInputs01.md` (and v2/v3) for visual consistency.
- **Story DNA**: All prompts must be derived from the `generateStoryContextDna.md` logic to maintain narrative continuity.

## Domain Glossary
- **AIGC**: AI-Generated Content (specifically Flux/ComfyUI pipelines).
- **DNA**: Narrative "Source Code" for a specific story arc in `videoGen`.
- **OpenMontage**: The timeline-based assembly engine.
