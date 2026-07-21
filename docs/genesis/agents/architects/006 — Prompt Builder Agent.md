Genesis Agent Specification (GAS)
GAS-006 — Prompt Builder Agent

Document ID: GAS-006
Title: Prompt Builder Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: PromptBuilderAgent
Constitutional Class: Production Planner
Accountability: Production Orchestrator Agent
Domain: Visual Expression Ontology (GO-109), Production Planning Ontology (GO-112)

2. Purpose

The Prompt Builder Agent constructs the image generation prompts for every shot in the production. It combines scene context, character data, environment data, shot specifications, and visual style guidelines into structured prompts that downstream image generators can execute.

3. Responsibilities

3.1 Prompt Construction

- Build a prompt for each shot combining:
  - Scene description (what is happening)
  - Character appearance (who is in the shot)
  - Environment description (where the shot takes place)
  - Shot specification (camera angle, lens, movement)
  - Lighting design (source, color, mood)
  - Color palette (dominant and accent colors)
  - Style qualifiers (cinematic, photorealistic, film grain, etc.)

3.2 Prompt Optimization

- Ensure prompts are within the image model's context window
- Prioritize the most important visual elements
- Remove redundant or conflicting instructions
- Add negative prompts to avoid common artifacts

3.3 Character Consistency

- Include character visual anchors in every prompt
- Reference hero images for IPAdapter when available
- Ensure the same character looks the same across shots
- Vary expressions and poses while maintaining identity

3.4 Environment Consistency

- Include environment visual anchors in every prompt
- Ensure the same location looks consistent across shots
- Track lighting changes that reflect the emotional arc
- Maintain color palette consistency per location

4. Inputs

- Shot Production Plan (from Scene Planner Agent)
- Character Subgraph (from Character Manager Agent)
- World Subgraph (from Environment Manager Agent)
- Visual Style Guide (from Production Brief)
- Prompt Library (reusable prompt fragments)

5. Outputs

- Structured prompts for every shot
- Negative prompts for every shot
- Reference image paths for IPAdapter
- Prompt consistency validation report

6. Quality Criteria

- Every shot has a complete, executable prompt
- Character descriptions are consistent across all prompts
- Environment descriptions are consistent across all prompts
- Prompts fit within the image model's context window
- Style qualifiers are appropriate for the production's visual tone

7. Dependencies

- Requires: Shot Production Plan, Character Subgraph, World Subgraph
- Provides: Shot Prompts, Reference Image Paths
- Depends on: Scene Planner Agent, Character Manager Agent, Environment Manager Agent
- Supports: Image Generator Agent
