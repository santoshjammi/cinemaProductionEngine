Genesis Reference (GREF)
GREF-002 — Agent Dependency Map

Document ID: GREF-002
Title: Agent Dependency Map
Version: 1.0.0
Status: Reference
Authority: Derived from GAS-001 through GAS-027

1. Purpose

This Reference provides a visual map of agent dependencies within the Genesis Engine. It shows which agents depend on which, enabling parallel execution planning and impact analysis.

2. Dependency Graph

Stage 0: Initiation
  ProductionOrchestratorAgent
    ↓ (creates session, dispatches)

Stage 1: Discovery
  ResearchAgent
    ↓ (provides domain knowledge)

Stage 2: Creative Design (Parallel)
  ┌─────────────────┬─────────────────┬─────────────────┐
  │                 │                 │                 │
  StoryArchitect   CharacterMgr     EnvironmentMgr
  │                 │                 │                 │
  └────────┬────────┴────────┬────────┴────────┬────────┘
           │                 │                 │
           ▼                 ▼                 ▼
Stage 3: Creative Production (Sequential)
  PsychologyReviewerAgent
    ↓
  ScreenplayWriterAgent
    ↓
  DialogueWriterAgent
    ↓

Stage 4: Production Planning (Sequential)
  ScenePlannerAgent
    ↓
  ShotPlannerAgent
    ↓
  MusicComposerAgent
    ↓
  PromptBuilderAgent
    ↓

Stage 5: Production Execution (Parallel)
  ┌──────────┬──────────┬──────────┬──────────┐
  │          │          │          │          │
  ImageGen  VoiceGen  MusicGen   SFXGen
  │          │          │          │          │
  └─────┬────┴─────┬────┴─────┬────┴─────┬────┘
         │          │          │          │
         ▼          ▼          ▼          ▼
Stage 6: Post-Production (Sequential)
  AudioMixingAgent
    ↓
  SubtitleAgent
    ↓
  VideoComposerAgent
    ↓

Stage 7: Evaluation (Parallel)
  ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┐
  │      │      │      │      │      │      │      │
StoryQ  DialQ  VisCon  AudioQ EmoSc  CharCon YTReady
  │      │      │      │      │      │      │      │
  └──┬───┴──┬───┴──┬───┴──┬───┴──┬───┴──┬───┴──┬───┘
     │      │      │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼      ▼      ▼
Stage 8: Revision (Conditional)
  RevisionAgent
    ↓ (loops back to affected stage)

Stage 9: Certification
  GovernanceAgent

3. Parallel Execution Groups

Group A (Stage 2): StoryArchitect, CharacterManager, EnvironmentManager
  - No dependencies between them
  - All depend on ResearchAgent
  - All provide input to PsychologyReviewerAgent

Group B (Stage 5): ImageGenerator, VoiceGenerator, MusicGenerator, SFXGenerator
  - No dependencies between them
  - All depend on PromptBuilderAgent
  - All provide input to AudioMixingAgent

Group C (Stage 7): All 7 evaluation agents
  - No dependencies between them
  - All depend on VideoComposerAgent
  - All provide input to RevisionAgent

4. Critical Path

The critical path (longest dependency chain) is:
ResearchAgent → StoryArchitectAgent → PsychologyReviewerAgent → ScreenplayWriterAgent → DialogueWriterAgent → ScenePlannerAgent → ShotPlannerAgent → MusicComposerAgent → PromptBuilderAgent → ImageGeneratorAgent → AudioMixingAgent → SubtitleAgent → VideoComposerAgent → EvaluationAgents → RevisionAgent → GovernanceAgent

This is 16 sequential stages. Parallel groups reduce wall-clock time but do not reduce the critical path length.
