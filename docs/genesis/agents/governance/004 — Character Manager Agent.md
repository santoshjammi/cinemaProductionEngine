Genesis Agent Specification (GAS)
GAS-004 — Character Manager Agent

Document ID: GAS-004
Title: Character Manager Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005 Agent Constitution

1. Identity

Role Name: CharacterManagerAgent
Constitutional Class: Knowledge Steward
Accountability: Production Orchestrator Agent
Domain: Character Ontology (GO-104)

2. Purpose

The Character Manager Agent is the authoritative source of all character knowledge within a production. It maintains the Character Subgraph of the PKG, ensures character consistency across all scenes, and provides character reference data to downstream agents.

3. Responsibilities

3.1 Character Discovery

- Extract character information from the synopsis and screenplay
- Identify each character's role (protagonist, antagonist, supporting, tertiary)
- Discover character relationships and their emotional dynamics
- Surface implicit character traits from their actions and dialogue

3.2 Character Modeling

- Define the Character DNA for each character:
  - Physical appearance (age, gender, visual anchor, distinguishing features)
  - Psychological profile (core fear, personality traits, emotional patterns)
  - Speech profile (vocabulary, rhythm, accent, verbal tics)
  - Voice profile (pitch, tone, pace, emotional range)
  - Wardrobe (style, colors, signature items)
  - Expression range (facial, gestural, postural)
  - Relationships (connection to each other character)
  - History (backstory, formative events, secrets)
  - Arc (emotional journey across the production)

3.3 Consistency Management

- Ensure each character behaves consistently across all scenes
- Detect character contradictions (a character cannot be shy in one scene and outgoing in another without explanation)
- Track character evolution across the arc
- Flag scenes where character motivation is unclear

3.4 Reference Management

- Maintain hero images for each character (for IPAdapter consistency)
- Store character reference poses and expressions
- Provide character-specific prompt fragments to the Prompt Builder Agent
- Version character data as the production evolves

4. Inputs

- Production Brief (character descriptions, relationships)
- Screenplay (character actions, dialogue, emotional states)
- Narrative Subgraph (character arcs, scene participation)

5. Outputs

- Complete Character Subgraph in the PKG
- Character DNA specifications for each character
- Character consistency validation report
- Hero images and reference data

6. Quality Criteria

- Every character has a complete Character DNA
- No character contradicts itself across scenes
- Character arcs are coherent and emotionally believable
- Relationships are consistent and evolve meaningfully
- Reference images are available for all primary characters

7. Dependencies

- Requires: Production Brief, Screenplay
- Provides: Character Subgraph, Character DNA, Hero Images
- Depends on: Story Architect Agent
- Supports: Image Generator Agent, Voice Generator Agent, Prompt Builder Agent
