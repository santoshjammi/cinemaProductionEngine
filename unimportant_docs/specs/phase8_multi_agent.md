# Spec: Phase 8 — Multi-Agent Orchestration (LangGraph)

## Objective

Build a multi-agent orchestration layer on top of the existing
CapabilityRegistry. Seven specialized agents collaborate via a
LangGraph state machine to turn a story brief into a finished video.
The orchestrator is the user-facing entry point — it replaces the
existing `scripts/psychological_pipeline.py` invocation with a
declarative `python -m movie_os make --brief ...` CLI.

**Why LangGraph**: battle-tested framework with built-in state
management, cycles, persistence, and human-in-the-loop hooks. Matches
the production-grade feel the rest of Movie OS already has.

**Why seven agents**: each represents a distinct creative concern
(story, visual, voice, music, QA, publishing) plus a top-level
"Movie" agent that coordinates. Smaller agents stay focused; larger
agents become spaghetti.

**Success criteria**:
- A user can run `python -m movie_os make --brief <path>` and get a
  finished `output/<name>/final.mp4` (audio + images + subtitles
  composited)
- The Movie Agent decides which sub-agents to call based on the
  brief — at minimum Story, Visual, Voice, Music, QA
- Agents communicate via a shared `MovieState` TypedDict, not via
  global variables
- The graph is checkpointed after every node so a long render can
  resume from the last successful step
- All 7 agents have unit tests proving they advance the state
  correctly given a valid input
- A integration test runs the full graph end-to-end on a tiny
  1-scene brief and produces a valid video file

## Tech Stack

- **LangGraph** (`langgraph>=0.2`) — state graph, checkpointing
- **LangChain Core** (`langchain-core>=0.3`) — message types
- **Pydantic v2** — state schema
- **Movie OS CapabilityRegistry** (existing) — agent tool calls
- **SQLite** (via `langgraph.checkpoint.sqlite`) — checkpoint store
- **Python 3.11+** — same as the rest of the project

## Commands

```bash
# Run the multi-agent pipeline
python -m movie_os make --brief videoContentStructure/.../brief.md

# Run just one agent (for debugging)
python -m movie_os agent story_agent --input brief.yaml

# Inspect the state at a checkpoint
python -m movie_os state --thread <thread_id>

# Resume from a checkpoint
python -m movie_os make --brief brief.md --resume <thread_id>
```

## Project Structure

```
movie_os/agents/
├── __init__.py
├── base.py              # AgentBase + AgentContext
├── state.py             # MovieState (Pydantic + TypedDict)
├── graph.py             # LangGraph StateGraph wiring
├── checkpoints.py       # SQLite checkpoint store
├── movie_agent.py       # Top-level orchestrator
├── story_agent.py       # Master Timeline + Scene DNA
├── visual_agent.py      # FLUX image rendering
├── voice_agent.py       # EdgeTTS narration
├── music_agent.py       # Procedural music + sting
├── sfx_agent.py         # Procedural SFX
├── qa_agent.py          # Quality checks (file exists, durations)
├── publishing_agent.py  # Final composition (ffmpeg concat)
└── tools.py             # LangChain tool wrappers for capabilities

movie_os/tests/
├── test_phase8_agents.py
├── test_phase8_graph.py
├── test_phase8_state.py
└── integration/
    └── test_phase8_e2e.py
```

## The Seven Agents

### 1. MovieAgent (orchestrator)
- **Input**: brief path
- **Decision**: which sub-agents to call and in what order
- **Output**: full state with all artifacts
- **Tools**: reads brief, decides phase (story-first vs voice-first)

### 2. StoryAgent
- **Input**: brief + DNA context
- **Capability**: `story.generate_timeline`
- **Output**: Master Timeline (acts/scenes/shots/frames)
- **Also handles**: shot planning (Phase 7) and prompt generation

### 3. VisualAgent
- **Input**: timeline + character registry
- **Capability**: `image.render` (FLUX via ComfyUI)
- **Output**: rendered scene images (1 per shot, or N for IPAdapter)
- **Tracks**: which scenes need re-render (failed QA)

### 4. VoiceAgent
- **Input**: timeline.voiceover + character voices
- **Capability**: `voice.synthesize` (EdgeTTS)
- **Output**: wav files per scene + manifest

### 5. MusicAgent
- **Input**: timeline.music_cue + scene mood
- **Capability**: `music.generate` (procedural) + `music.sting`
- **Output**: music wav per scene, mixed with `mix_scene_audio`

### 6. SFXAgent
- **Input**: timeline.sfx_layers + scene state
- **Capability**: `sfx.generate` (procedural)
- **Output**: SFX wav per scene

### 7. QAAgent
- **Input**: rendered images + voice + music
- **Checks**: file exists, duration in range, peak loudness,
  image is not blank, irreversible_moment has hard cut
- **Output**: QA report (pass/fail per scene)
- **Triggers**: re-render request back to VisualAgent

### 8. PublishingAgent
- **Input**: all scene assets + QA pass
- **Capability**: `video.compose` (ffmpeg)
- **Output**: final mp4 + thumbnail + metadata

## State Schema (MovieState)

```python
class MovieState(TypedDict):
    thread_id: str
    brief: dict
    dna: dict
    timeline: Optional[dict]  # Master Timeline
    scene_assets: dict[int, dict]  # scene_number -> {image, voice, music, sfx}
    qa_report: Optional[dict]
    errors: list[str]
    current_step: str
    next_action: Optional[str]
```

## Code Style

```python
class StoryAgent(AgentBase):
    name = "story_agent"

    async def run(self, state: MovieState) -> MovieState:
        brief = state["brief"]
        timeline = await self.capabilities["story.generate_timeline"].execute(
            TimelineIntent(brief=brief, dna=state["dna"])
        )
        state["timeline"] = timeline.to_dict()
        state["current_step"] = "story_done"
        return state
```

- One file per agent, no bigger than 300 lines
- Agents never call other agents directly — they update state and
  the graph decides what's next
- Errors are appended to `state["errors"]`; the graph routes to QA
  on errors

## Testing Strategy

- **Unit tests** (`test_phase8_agents.py`): each agent given a known
  input produces a known state delta
- **Graph tests** (`test_phase8_graph.py`): the StateGraph routes
  correctly given a mock state
- **State tests** (`test_phase8_state.py`): state schema validates,
  pydantic model is correct
- **Integration test** (`test_phase8_e2e.py`): 1-scene brief runs
  through the full graph (mocking heavy capabilities like ComfyUI)
- **Coverage target**: 80% on the agents package

## Boundaries

- **Always do**: validate state with Pydantic before graph transitions,
  checkpoint after every node, log every agent's start/end
- **Ask first**: adding new external services (Tavily, etc),
  changing the state schema, changing agent responsibility boundaries
- **Never do**: hardcode model names in agents (use CapabilityRegistry),
  mutate global state from inside an agent, skip QA

## Phasing

- **8.1**: State schema, AgentBase, LangGraph scaffold, 1 working
  agent (StoryAgent) end-to-end
- **8.2**: Add VisualAgent, VoiceAgent, MusicAgent
- **8.3**: Add QAAgent with re-render loops
- **8.4**: Add SFXAgent, PublishingAgent
- **8.5**: Checkpointing, resume, integration test

## Open Questions

- (none — clarified with user)
