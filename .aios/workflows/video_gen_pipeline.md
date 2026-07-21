---
name: "video-gen-pipeline"
type: "orchestration"
version: "2.0"
---

# VideoGen Production Pipeline (Multi-Agent)

## Reference: `specs/phase8_multi_agent.md` & `superplans/plans/createOncePublishAnywhere.md`

## Stages
1. **Project Initialization**: Create project via `ProjectService` and `OpenMontage`.
2. **Story Context Generation**: 
   - Agent `story-context-dna` generates narrative DNA using prompt engineering (`generateStoryContextDna.md`).
3. **Cinematic Production Design**: 
   - Agent `cinema-director` applies production design inputs (`cinemaProductiondesignInputs*.md`) to define the visual style.
4. **Asset Generation (Flux & ComfyUI)**: 
   - Agent `asset-generator` invokes `enhancementFluxComfyUI.md` workflows for image/video asset creation.
5. **OpenMontage Assembly**: 
   - Agents coordinate to assemble clips into a timeline (`stepWithOpenMontage.md`).
6. **Validation & Delivery**: Render and package via FFmpeg/encoding pipelines.

## Error Handling
If a stage fails (e.g., ComfyUI node crash), route to `validation/error-recovery` with specific context logs before retrying.
