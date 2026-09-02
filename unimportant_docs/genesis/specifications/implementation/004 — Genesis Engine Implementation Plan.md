# Implementation Plan: Genesis Engine

## Overview

Build the Genesis Engine — a Python-based pre-production intelligence system with 30 agents that transform a synopsis into a complete, validated Production Knowledge Package (PKP) containing 19 specifications.

## Architecture Decisions

1. **PKG as SQLite + adjacency lists** — not a full graph DB. SQLite for v1, swappable to Neo4j later. The PKG is a dict-of-dicts in memory, persisted to SQLite.

2. **One LLM call per agent** — not one giant prompt. Each agent makes its own LLM call with its own prompt. This enables checkpointing, error recovery, and parallel execution where possible.

3. **LangGraph for orchestration** — same framework as the existing Movie OS agents. State graph with conditional edges for review loops.

4. **Mock LLM for testing** — tests never call a real LLM. A `MockLLMClient` returns canned responses based on the agent type.

5. **Master prompt as template** — the master prompt from the ChatGPT conversation is split into per-agent prompts stored in YAML.

## Task List

### Phase 1: Foundation (PKG + Models + LLM Client)

- [ ] **Task 1: PKG Data Models**
  - Acceptance: `KnowledgeNode`, `KnowledgeEdge`, `ConfidenceLevel`, `Specification`, `PKGState` Pydantic models exist and validate
  - Verify: `pytest movie_os/tests/test_genesis_models.py -v`
  - Files: `movie_os/genesis/models.py`, `movie_os/tests/test_genesis_models.py`
  - Size: S

- [ ] **Task 2: PKG Store**
  - Acceptance: `ProductionKnowledgeGraph` class can create/read/update nodes, edges, and specifications in SQLite. Supports `get_specification()`, `set_specification()`, `get_node()`, `add_edge()`, `query_subgraph()`.
  - Verify: `pytest movie_os/tests/test_genesis_pkg.py -v`
  - Files: `movie_os/genesis/pkg.py`, `movie_os/tests/test_genesis_pkg.py`
  - Size: M

- [ ] **Task 3: LLM Client**
  - Acceptance: `LLMClient` class talks to LMStudio (local) with fallback to OpenAI. `MockLLMClient` returns canned responses. `generate(prompt) -> str` works.
  - Verify: `pytest movie_os/tests/test_genesis_models.py -v` (includes LLM client tests)
  - Files: `movie_os/genesis/llm_client.py`, `movie_os/tests/test_genesis_models.py`
  - Size: S

- [ ] **Task 4: Session Manager**
  - Acceptance: `SessionManager` creates sessions, tracks state, supports checkpoint/resume via SQLite.
  - Verify: `pytest movie_os/tests/test_genesis_pkg.py -v` (includes session tests)
  - Files: `movie_os/genesis/session.py`
  - Size: S

### Checkpoint: Foundation
- [ ] All model tests pass
- [ ] PKG store tests pass
- [ ] LLM client tests pass (with mock)
- [ ] Session manager tests pass

### Phase 2: Agent Base Classes + Prompts

- [ ] **Task 5: Agent Base Classes**
  - Acceptance: `DiscoveryAgent`, `PKPAgent`, `ReviewAgent` base classes exist with the standard lifecycle: `receive → gather_context → reason → draft → self_review → cross_validate → resolve_conflicts → assign_confidence → update_pkg → publish`. Each has `run(pkg) -> Result`.
  - Verify: `pytest movie_os/tests/test_genesis_discovery.py -v` (base class tests)
  - Files: `movie_os/genesis/discovery/base.py`, `movie_os/genesis/pkp_agents/base.py`, `movie_os/genesis/reviewers/base.py`
  - Size: M

- [ ] **Task 6: Agent Prompt Templates**
  - Acceptance: YAML files with prompt templates for all 30 agents. Each prompt has: role, instructions, input_schema, output_schema, example.
  - Verify: `python -c "from movie_os.genesis.prompts import load_prompts; p = load_prompts(); assert len(p) >= 30"`
  - Files: `movie_os/genesis/prompts/discovery_prompts.yaml`, `movie_os/genesis/prompts/pkp_prompts.yaml`, `movie_os/genesis/prompts/review_prompts.yaml`, `movie_os/genesis/prompts/__init__.py`
  - Size: M

### Checkpoint: Agent Infrastructure
- [ ] Base classes tested
- [ ] All 30 prompt templates load

### Phase 3: Discovery Agents (7 agents)

- [ ] **Task 7: Intent Analyst**
  - Acceptance: Given a synopsis, extracts creative intent, emotional transformation, territory, theme. Writes to PKG with confidence.
  - Verify: `pytest movie_os/tests/test_genesis_discovery.py::TestIntentAnalyst -v`
  - Files: `movie_os/genesis/discovery/intent_analyst.py`
  - Size: S

- [ ] **Task 8: Theme Analyst**
  - Acceptance: Extracts primary/secondary themes, symbolic motifs, psychological truth from synopsis + intent.
  - Verify: `pytest movie_os/tests/test_genesis_discovery.py::TestThemeAnalyst -v`
  - Files: `movie_os/genesis/discovery/theme_analyst.py`
  - Size: S

- [ ] **Task 9: Emotion Analyst**
  - Acceptance: Maps emotional arc, identifies modulation points, irreversible moment, almost moment.
  - Verify: `pytest movie_os/tests/test_genesis_discovery.py::TestEmotionAnalyst -v`
  - Files: `movie_os/genesis/discovery/emotion_analyst.py`
  - Size: S

- [ ] **Task 10: Conflict Analyst**
  - Acceptance: Identifies central conflict, internal vs external, power dynamics, triggers.
  - Verify: `pytest movie_os/tests/test_genesis_discovery.py::TestConflictAnalyst -v`
  - Files: `movie_os/genesis/discovery/conflict_analyst.py`
  - Size: S

- [ ] **Task 11: Audience Analyst**
  - Acceptance: Determines target audience, emotional state, transformation, objections.
  - Verify: `pytest movie_os/tests/test_genesis_discovery.py::TestAudienceAnalyst -v`
  - Files: `movie_os/genesis/discovery/audience_analyst.py`
  - Size: S

- [ ] **Task 12: Knowledge Gap Analyst**
  - Acceptance: Classifies all knowledge as EXPLICIT/INFERRED/CONFIRMED/ASSUMED/UNKNOWN. Identifies critical gaps.
  - Verify: `pytest movie_os/tests/test_genesis_discovery.py::TestGapAnalyst -v`
  - Files: `movie_os/genesis/discovery/gap_analyst.py`
  - Size: S

- [ ] **Task 13: Question Planner**
  - Acceptance: Generates targeted questions only for critical unknowns with confidence < 60%. Each question has: why, what depends on it, confidence %, suggested default.
  - Verify: `pytest movie_os/tests/test_genesis_discovery.py::TestQuestionPlanner -v`
  - Files: `movie_os/genesis/discovery/question_planner.py`
  - Size: S

### Checkpoint: Discovery Pipeline
- [ ] All 7 discovery agents tested
- [ ] Discovery pipeline runs end-to-end on a test synopsis
- [ ] Knowledge gap analysis produces correct confidence classifications

### Phase 4: PKP Domain Agents (19 agents — batched by phase)

- [ ] **Task 14: Phase A Agents (Vision, Creative Strategy, Project)**
  - Acceptance: 3 agents generate PKP-00, PKP-01, PKP-02 from discovery results.
  - Verify: `pytest movie_os/tests/test_genesis_pkp_agents.py::TestPhaseA -v`
  - Files: `movie_os/genesis/pkp_agents/vision_agent.py`, `creative_strategy_agent.py`, `project_agent.py`
  - Size: M

- [ ] **Task 15: Phase B Agents (Research, Story, World)**
  - Acceptance: 3 agents generate PKP-03, PKP-04, PKP-05 from Phase A results.
  - Verify: `pytest movie_os/tests/test_genesis_pkp_agents.py::TestPhaseB -v`
  - Files: `movie_os/genesis/pkp_agents/research_agent.py`, `story_agent.py`, `world_agent.py`
  - Size: M

- [ ] **Task 16: Phase C Agents (Character, Relationship, Psychology)**
  - Acceptance: 3 agents generate PKP-06, PKP-07, PKP-08 from Phase B results.
  - Verify: `pytest movie_os/tests/test_genesis_pkp_agents.py::TestPhaseC -v`
  - Files: `movie_os/genesis/pkp_agents/character_agent.py`, `relationship_agent.py`, `psychology_agent.py`
  - Size: M

- [ ] **Task 17: Phase D Agent (Narrative)**
  - Acceptance: Narrative agent generates PKP-09 from story + psychology.
  - Verify: `pytest movie_os/tests/test_genesis_pkp_agents.py::TestPhaseD -v`
  - Files: `movie_os/genesis/pkp_agents/narrative_agent.py`
  - Size: S

- [ ] **Task 18: Phase E Agents (Directorial, Production Design, Audio, Editing, Animation)**
  - Acceptance: 5 agents generate PKP-10 through PKP-14 from narrative.
  - Verify: `pytest movie_os/tests/test_genesis_pkp_agents.py::TestPhaseE -v`
  - Files: `movie_os/genesis/pkp_agents/directorial_agent.py`, `production_design_agent.py`, `audio_intent_agent.py`, `editing_language_agent.py`, `animation_intent_agent.py`
  - Size: M

- [ ] **Task 19: Phase F Agent (Production Blueprint)**
  - Acceptance: Blueprint agent generates PKP-15 from all previous specs.
  - Verify: `pytest movie_os/tests/test_genesis_pkp_agents.py::TestPhaseF -v`
  - Files: `movie_os/genesis/pkp_agents/blueprint_agent.py`
  - Size: S

- [ ] **Task 20: Phase G Agents (Distribution, Quality, Knowledge Graph)**
  - Acceptance: 3 agents generate PKP-16, PKP-17, PKP-18.
  - Verify: `pytest movie_os/tests/test_genesis_pkp_agents.py::TestPhaseG -v`
  - Files: `movie_os/genesis/pkp_agents/distribution_agent.py`, `quality_agent.py`, `knowledge_graph_agent.py`
  - Size: M

### Checkpoint: PKP Generation
- [ ] All 19 PKP agents tested
- [ ] Full PKP generation pipeline runs on test synopsis
- [ ] All 19 specifications produced with confidence levels

### Phase 5: Review Agents + Chief Architect

- [ ] **Task 21: Review Agents (Story, Character, Narrative Reviewers)**
  - Acceptance: 3 reviewers validate consistency across specs. Can flag contradictions and request revisions.
  - Verify: `pytest movie_os/tests/test_genesis_reviewers.py -v`
  - Files: `movie_os/genesis/reviewers/story_reviewer.py`, `character_reviewer.py`, `narrative_reviewer.py`
  - Size: M

- [ ] **Task 22: Chief Architect**
  - Acceptance: Chief Architect maintains consistency, resolves conflicts, enforces grammar, approves completion.
  - Verify: `pytest movie_os/tests/test_genesis_engine.py::TestChiefArchitect -v`
  - Files: `movie_os/genesis/chief_architect.py`
  - Size: S

### Checkpoint: Review Loop
- [ ] Reviewers catch at least 1 contradiction in test cases
- [ ] Chief Architect can resolve conflicts and approve specs

### Phase 6: Orchestration + Completion Gate + CLI

- [ ] **Task 23: LangGraph Orchestration**
  - Acceptance: `build_genesis_graph()` creates the full LangGraph state machine with: discovery → PKP phases A-G → review → completion gate. Supports checkpointing.
  - Verify: `pytest movie_os/tests/test_genesis_engine.py::TestGraph -v`
  - Files: `movie_os/genesis/graph.py`
  - Size: M

- [ ] **Task 24: Completion Gate**
  - Acceptance: `PreProductionCompletionGate` checks all 8 criteria and returns PASS/FAIL with details.
  - Verify: `pytest movie_os/tests/test_genesis_gate.py -v`
  - Files: `movie_os/genesis/completion_gate.py`
  - Size: S

- [ ] **Task 25: Genesis Engine (top-level orchestrator)**
  - Acceptance: `GenesisEngine.run(synopsis)` runs the full pipeline and returns a complete PKP.
  - Verify: `pytest movie_os/tests/test_genesis_engine.py::TestEngine -v`
  - Files: `movie_os/genesis/engine.py`
  - Size: M

- [ ] **Task 26: CLI**
  - Acceptance: `python -m movie_os.genesis run/discover/spec/validate/gate/agents/state` all work.
  - Verify: `python -m movie_os.genesis --help` shows all commands
  - Files: `movie_os/genesis/cli.py`, `movie_os/genesis/__main__.py`
  - Size: S

### Checkpoint: Full Pipeline
- [ ] LangGraph orchestrates all 30 agents
- [ ] Completion gate works
- [ ] CLI works
- [ ] Full pipeline runs end-to-end

### Phase 7: Integration Test

- [ ] **Task 27: End-to-End Integration Test**
  - Acceptance: Given a real synopsis, the full pipeline produces all 19 specs, passes validation, and certifies readiness.
  - Verify: `pytest movie_os/tests/integration/test_genesis_e2e.py -v`
  - Files: `movie_os/tests/integration/test_genesis_e2e.py`
  - Size: M

### Checkpoint: Complete
- [ ] All 27 tasks complete
- [ ] All tests pass
- [ ] Full synopsis → PKP works end-to-end
- [ ] Ready for Studio Engine handoff

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM responses too long/short | Medium | Strict output schema validation + retry on parse failure |
| LLM hallucinates knowledge | High | Confidence scoring + cross-validation + review agents |
| Agent dependencies circular | Medium | Static dependency graph in PKP spec definitions |
| LLM unavailable | Low | Mock LLM for tests; graceful error handling in production |
| PKG grows too large for SQLite | Low | SQLite handles millions of rows; Neo4j migration path defined |

## Open Questions

- Which LLM model? (Default: Qwen3-Coder via LMStudio, configurable)
- One big prompt or many small? (Decision: many small — one per agent)
- SQLite or graph DB? (Decision: SQLite for v1, swappable later)