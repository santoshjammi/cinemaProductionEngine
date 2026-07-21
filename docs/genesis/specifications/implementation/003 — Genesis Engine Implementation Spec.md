# Spec: Genesis Engine — Pre-Production Intelligence System

## Objective

Build the Genesis Engine: a Python-based pre-production intelligence system that transforms a synopsis into a complete, validated Production Knowledge Package (PKP) containing 19 specifications. Genesis performs NO media generation — it only discovers, reasons, validates, and organizes creative knowledge.

The system uses 30 specialized agents (7 Discovery + 19 PKP Domain + 3 Review + 1 Chief Architect) that collaborate via a Production Knowledge Graph (PKG). Each agent owns one specification, follows a standard lifecycle (Receive → Reason → Draft → Self-Review → Cross-Validate → Publish), and assigns confidence levels to all knowledge.

**Success criteria:**
- Given a synopsis, Genesis produces all 19 PKP specifications as structured YAML + Markdown
- Discovery agents extract maximum knowledge from the synopsis automatically
- The system only asks the human when confidence < 60% on a critical decision
- All specifications are cross-validated for consistency
- A Pre-Production Completion Gate certifies readiness before handoff to Studio Engine
- The system runs on local LLM (LMStudio) with fallback to OpenAI/Claude
- All 30 agents have unit tests proving they advance the PKG correctly

## Tech Stack

- **Python 3.11+** — same as Movie OS
- **Pydantic v2** — PKG data models, agent state, specifications
- **LangGraph 1.2+** — agent orchestration, state graph, checkpointing
- **SQLite** — PKG storage (graph as adjacency lists + metadata)
- **PyYAML** — specification serialization
- **LMStudio** — local LLM for agent reasoning (Qwen3-Coder or similar)
- **Existing Movie OS** — `movie_os.capabilities`, `movie_os.config`, `movie_os.asset_store`

## Commands

```bash
# Run Genesis on a synopsis
python -m movie_os.genesis run --synopsis path/to/synopsis.md

# Run with constraints
python -m movie_os.genesis run --synopsis synopsis.md --constraints constraints.yaml

# Run only discovery stage
python -m movie_os.genesis discover --synopsis synopsis.md

# Run only a specific PKP specification
python -m movie_os.genesis spec --id 06 --synopsis synopsis.md

# Validate a completed PKP
python -m movie_os.genesis validate --pkg path/to/pkg.json

# Check production readiness
python -m movie_os.genesis gate --pkg path/to/pkg.json

# List all agents
python -m movie_os.genesis agents list

# Show PKG state
python -m movie_os.genesis state --session <session_id>

# Tests
./venv/bin/python -m pytest movie_os/tests/test_genesis_*.py -v
```

## Project Structure

```
movie_os/genesis/
├── __init__.py                    # Public API
├── engine.py                      # GenesisEngine — top-level orchestrator
├── pkg.py                         # ProductionKnowledgeGraph — graph store
├── models.py                      # Pydantic models: KnowledgeNode, KnowledgeEdge, Confidence, Specification
├── session.py                     # SessionManager — lifecycle, checkpointing
├── completion_gate.py              # PreProductionCompletionGate — readiness certification
├── llm_client.py                  # LLM client (LMStudio/OpenAI) with fallback
├── master_prompt.py               # The master prompt template
│
├── discovery/                     # 7 Discovery Agents
│   ├── __init__.py
│   ├── base.py                    # DiscoveryAgent base class
│   ├── intent_analyst.py          # 1. Intent Analyst
│   ├── theme_analyst.py           # 2. Theme Analyst
│   ├── emotion_analyst.py         # 3. Emotion Analyst
│   ├── conflict_analyst.py        # 4. Conflict Analyst
│   ├── audience_analyst.py        # 5. Audience Analyst
│   ├── gap_analyst.py             # 6. Knowledge Gap Analyst
│   └── question_planner.py        # 7. Question Planner
│
├── pkp_agents/                    # 19 PKP Domain Agents
│   ├── __init__.py
│   ├── base.py                    # PKPAgent base class
│   ├── vision_agent.py            # 8.  PKP-00 Vision
│   ├── creative_strategy_agent.py # 9.  PKP-01 Creative Strategy
│   ├── project_agent.py           # 10. PKP-02 Project
│   ├── research_agent.py          # 11. PKP-03 Research
│   ├── story_agent.py             # 12. PKP-04 Story
│   ├── world_agent.py             # 13. PKP-05 World
│   ├── character_agent.py         # 14. PKP-06 Character
│   ├── relationship_agent.py      # 15. PKP-07 Relationship
│   ├── psychology_agent.py        # 16. PKP-08 Psychology
│   ├── narrative_agent.py         # 17. PKP-09 Narrative
│   ├── directorial_agent.py       # 18. PKP-10 Directorial Language
│   ├── production_design_agent.py # 19. PKP-11 Production Design
│   ├── audio_intent_agent.py      # 20. PKP-12 Audio Intent
│   ├── editing_language_agent.py  # 21. PKP-13 Editing Language
│   ├── animation_intent_agent.py  # 22. PKP-14 Animation Intent
│   ├── blueprint_agent.py         # 23. PKP-15 Production Blueprint
│   ├── distribution_agent.py      # 24. PKP-16 Distribution
│   ├── quality_agent.py           # 25. PKP-17 Quality
│   └── knowledge_graph_agent.py   # 26. PKP-18 Knowledge Graph
│
├── reviewers/                     # 3 Review Agents
│   ├── __init__.py
│   ├── base.py                    # ReviewAgent base class
│   ├── story_reviewer.py          # 27. Story Reviewer
│   ├── character_reviewer.py      # 28. Character Reviewer
│   └── narrative_reviewer.py      # 29. Narrative Reviewer
│
├── chief_architect.py             # 30. Genesis Chief Architect
│
├── graph.py                       # LangGraph state machine wiring
├── cli.py                         # CLI subcommands
│
└── prompts/                       # Agent prompt templates
    ├── discovery_prompts.yaml     # Prompts for 7 discovery agents
    ├── pkp_prompts.yaml           # Prompts for 19 PKP agents
    └── review_prompts.yaml        # Prompts for 3 review agents

movie_os/tests/
├── test_genesis_pkg.py            # PKG store tests
├── test_genesis_models.py         # Pydantic model tests
├── test_genesis_discovery.py      # Discovery agent tests
├── test_genesis_pkp_agents.py     # PKP agent tests
├── test_genesis_reviewers.py      # Review agent tests
├── test_genesis_gate.py           # Completion gate tests
├── test_genesis_engine.py         # End-to-end engine tests
└── integration/
    └── test_genesis_e2e.py        # Full synopsis → PKP test
```

## Code Style

```python
"""PKP-06: Character Agent — generates the Character Specification."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from movie_os.genesis.pkp_agents.base import PKPAgent, PKPResult
from movie_os.genesis.models import ConfidenceLevel
from movie_os.genesis.pkg import ProductionKnowledgeGraph


class CharacterAgent(PKPAgent):
    """Owns PKP-06: Character Specification."""
    
    spec_id = "PKP-06"
    spec_name = "Character Specification"
    dependencies = ["PKP-04", "PKP-05"]  # Story, World
    
    async def run(self, pkg: ProductionKnowledgeGraph) -> PKPResult:
        story = pkg.get_specification("PKP-04")
        world = pkg.get_specification("PKP-05")
        prompt = self.build_prompt(synopsis=pkg.synopsis, story=story, world=world)
        draft = await self.llm.generate(prompt)
        validated = self.validate(draft)
        confidence = self.assess_confidence(validated, pkg)
        pkg.set_specification(self.spec_id, validated, confidence)
        return PKPResult(spec_id=self.spec_id, status="published", confidence=confidence)
```

- One file per agent, under 200 lines
- Every agent inherits from `PKPAgent` or `DiscoveryAgent`
- Agents never call other agents directly — they read from and write to the PKG
- All LLM calls go through `llm_client.py` (never direct HTTP)
- Confidence levels are explicit on every knowledge item

## Testing Strategy

- **Unit tests** (`test_genesis_*.py`): each agent given a known PKG state produces a known result
- **Integration test** (`test_genesis_e2e.py`): full synopsis → 19 specs → completion gate
- **Mock LLM**: tests use a mock LLM that returns canned responses — no real LLM calls in tests
- **Coverage target**: 80% on the genesis package

## Boundaries

- **Always do**: validate every specification against its dependencies, assign confidence levels, record provenance
- **Ask first**: changing the PKG schema, adding new agent types, changing the master prompt
- **Never do**: generate images/audio/video, call external APIs (except LLM), skip validation

## Success Criteria

1. `python -m movie_os.genesis run --synopsis synopsis.md` produces all 19 PKP specs
2. Discovery agents extract ≥ 80% of knowledge automatically from the synopsis
3. The system asks ≤ 5 questions to the human (only for critical unknowns)
4. Cross-validation catches at least 1 contradiction in test cases
5. The completion gate correctly blocks incomplete PKPs
6. All 30 agents have unit tests
7. The full pipeline runs in < 5 minutes on a local LLM

## Open Questions

- Which LLM model to use as default? (Qwen3-Coder via LMStudio is the current default)
- Should the PKG use SQLite or a proper graph database? (SQLite for v1, Neo4j later)
- Should the master prompt be one big call or many small calls? (Many small calls — one per agent — for better error handling and checkpointing)