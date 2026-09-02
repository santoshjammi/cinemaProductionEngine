Genesis Agent Specification (GAS)
GAS-011 — Image Generator Agent

Document ID: GAS-011
Title: Image Generator Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: ImageGeneratorAgent
Constitutional Class: Production Executor
Accountability: Production Orchestrator Agent
Domain: Visual Expression Ontology (GO-109)

2. Purpose

The Image Generator Agent executes the shot prompts produced by the Prompt Builder Agent. It dispatches each prompt to the configured image generation provider (FLUX, SDXL, etc.), manages reference images for character consistency, and validates the output before storing it in the asset store.

3. Responsibilities

3.1 Image Generation

- Receive structured prompts from the Prompt Builder Agent
- Dispatch prompts to the configured image generation provider
- Manage seed values for reproducibility
- Handle retry logic for failed generations

3.2 Character Consistency

- Load character hero images for IPAdapter when specified
- Ensure the same character appears consistently across shots
- Manage reference image caching for performance

3.3 Quality Validation

- Verify generated images are not blank or corrupted
- Check image resolution matches specifications
- Validate that images contain expected content (basic CLIP scoring)
- Flag low-quality generations for re-render

3.4 Asset Management

- Store generated images in the asset store with metadata
- Tag images with scene number, shot ID, character, and environment
- Register image assets for downstream agents
- Track generation provenance (model, seed, prompt, timestamp)

4. Inputs

- Shot prompts (from Prompt Builder Agent)
- Character reference images (from Character Manager Agent)
- Environment reference images (from Environment Manager Agent)
- Image generation provider configuration

5. Outputs

- Generated images stored in the asset store
- Image quality validation report
- Generation provenance log

6. Quality Criteria

- Every shot has a corresponding generated image
- Character appearance is consistent across all shots
- Environment appearance is consistent across all shots
- Images meet minimum quality thresholds
- All images are properly tagged and stored

7. Dependencies

- Requires: Shot prompts, Reference images
- Provides: Generated images
- Depends on: Prompt Builder Agent, Character Manager Agent, Environment Manager Agent
- Supports: Video Composer Agent, Audio Mixing Agent
