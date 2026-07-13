# Spec: Text Cinema Engine — Full Pipeline with UI & Video Generation

## Objective

Build a complete, production-ready application that takes a simple story prompt from the user and generates a full cinematic video through an AI pipeline:

```
User Prompt → Story → Scenes → Dialogues → Cinematic Prompts → Video Clips → Final Video
```

**User Flow:**
1. User enters a story idea (topic, tone, platform, length)
2. System runs internet research (optional) for grounding
3. LLM generates structured emotional story with beats
4. LLM decomposes story into cinematic scenes (camera, lighting, visual prompts)
5. LLM generates spoken dialogues for each scene
6. LLM creates detailed cinematic prompts for video generation
7. Video model generates clips for each scene
8. Clips are assembled into final video with optional narration/dialogue overlay
9. User can preview, regenerate individual scenes, and export final video

**Success Criteria:**
- End-to-end pipeline runs in < 10 minutes for a 60-second video
- UI is responsive, accessible (WCAG 2.1 AA), and visually polished
- Each stage is inspectable and regeneratable
- Final video exports as MP4 with optional audio narration
- All existing CLI functionality preserved

---

## Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend Framework | Next.js | 14+ (App Router) |
| Language | TypeScript | 5+ |
| Styling | Tailwind CSS | 3.4+ |
| State Management | Zustand + React Query | latest |
| UI Components | Radix UI + custom | latest |
| Video Generation | Stable Video Diffusion (diffusers) | latest |
| Backend | FastAPI | 0.9+ |
| LLM | Ollama (local) | latest |
| Text Pipeline | Existing Python pipeline | — |
| Testing | Vitest + Playwright | latest |
| Linting | ESLint + Prettier | latest |

---

## Commands

```bash
# Frontend
cd frontend
npm run dev          # Development server (localhost:3000)
npm run build        # Production build
npm run test         # Unit tests (Vitest)
npm run test:e2e     # E2E tests (Playwright)
npm run lint         # ESLint + Prettier check

# Backend
cd backend
python -m uvicorn main:app --reload  # Dev server (localhost:8000)
python -m pytest                    # Unit tests
python -m pytest --cov              # Coverage

# Video Generation (requires GPU)
python scripts/generate_video.py --prompt "..." --output clip.mp4

# Full Pipeline (CLI - existing)
python main.py --topic "..." --tone fear --length long --platform youtube
```

---

## Project Structure

```
video-gen/
├── frontend/                     # Next.js App Router
│   ├── src/
│   │   ├── app/                  # App Router pages
│   │   │   ├── page.tsx          # Landing / prompt input
│   │   │   ├── pipeline/[id]/    # Pipeline view (dynamic)
│   │   │   │   ├── page.tsx      # Main pipeline view
│   │   │   │   ├── story/        # Story editor
│   │   │   │   ├── scenes/       # Scene timeline
│   │   │   │   ├── video/        # Video player + generation
│   │   │   │   └── layout.tsx    # Pipeline shell
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ui/               # Base components (Button, Card, Input, etc.)
│   │   │   ├── pipeline/
│   │   │   │   ├── PipelineView.tsx
│   │   │   │   ├── StageIndicator.tsx
│   │   │   │   ├── ProgressBar.tsx
│   │   │   ├── story/
│   │   │   │   ├── StoryEditor.tsx
│   │   │   │   ├── BeatsList.tsx
│   │   │   │   ├── EmotionalArc.tsx
│   │   │   ├── scenes/
│   │   │   │   ├── SceneTimeline.tsx
│   │   │   │   ├── SceneCard.tsx
│   │   │   │   ├── SceneEditor.tsx
│   │   │   │   ├── CameraLighting.tsx
│   │   │   ├── video/
│   │   │   │   ├── VideoPlayer.tsx
│   │   │   │   ├── ClipGenerator.tsx
│   │   │   │   ├── VideoAssembler.tsx
│   │   │   ├── research/
│   │   │   │   ├── ResearchPanel.tsx
│   │   │   │   ├── SourceList.tsx
│   │   │   ├── common/
│   │   │   │   ├── LoadingSkeleton.tsx
│   │   │   │   ├── ErrorBoundary.tsx
│   │   │   │   ├── EmptyState.tsx
│   │   │   │   ├── RegenerateButton.tsx
│   │   ├── lib/
│   │   │   ├── api.ts            # API client
│   │   │   ├── store.ts          # Zustand store
│   │   │   ├── types.ts          # Shared types
│   │   │   ├── utils.ts
│   │   ├── hooks/
│   │   │   ├── usePipeline.ts
│   │   │   ├── useVideoGeneration.ts
│   │   │   └── useDebounce.ts
│   │   └── styles/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── backend/                      # FastAPI
│   ├── app/
│   │   ├── main.py               # FastAPI app entry
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── pipeline.py   # Pipeline CRUD + run
│   │   │   │   ├── video.py      # Video generation endpoints
│   │   │   │   ├── research.py   # Research endpoints
│   │   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── pipeline_service.py
│   │   │   ├── video_service.py
│   │   │   └── research_service.py
│   │   ├── models/
│   │   │   ├── pipeline.py       # Pydantic models
│   │   │   └── video.py
│   │   └── core/
│   │       ├── config.py
│   │       └── exceptions.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── pipeline/                     # Existing Python text pipeline
│   ├── orchestrator.py
│   ├── research.py
│   ├── output_saver.py
│   └── ...
│
├── scripts/
│   ├── generate_video.py         # Video generation script
│   └── assemble_video.py         # FFmpeg assembly
│
├── SPEC.md                       # This file
├── docker-compose.yml
└── README.md
```

---

## Code Style

### Component Pattern (Composition over Configuration)

```tsx
// Good: Composable
<PipelineView>
  <PipelineHeader title="Ashen Echoes" />
  <StageIndicator currentStage={2} stages={STAGES} />
  <PipelineContent>
    <SceneTimeline scenes={scenes} onRegenerate={handleRegenerate} />
  </PipelineContent>
</PipelineView>

// Avoid: Over-configured
<PipelineView
  title="Ashen Echoes"
  currentStage={2}
  stages={STAGES}
  renderScene={...}
  renderStage={...}
/>
```

### Naming Conventions

- Components: `PascalCase` (e.g., `SceneTimeline.tsx`)
- Hooks: `use` + `PascalCase` (e.g., `usePipeline.ts`)
- Types: `PascalCase` + `Type` suffix (e.g., `PipelineStageType`)
- Constants: `SCREAMING_SNAKE_CASE` (e.g., `STAGES`)
- Functions: `camelCase` (e.g., `runPipeline`)

### Styling (Tailwind)

```tsx
// Good: Uses design system tokens
<div className="flex items-center gap-3 p-4 bg-surface border border-border rounded-lg">
  <h3 className="text-lg font-semibold text-text-primary">Title</h3>
</div>

// Bad: Arbitrary values
<div style={{ padding: '13px', backgroundColor: '#1a1a2e' }}>
  <h3 style={{ fontSize: '18.5px' }}>Title</h3>
</div>
```

---

## Testing Strategy

| Level | Framework | Location | Coverage Target |
|-------|-----------|----------|-----------------|
| Unit | Vitest | `src/components/**/*.test.tsx` | 80% |
| Integration | Vitest | `src/hooks/**/*.test.ts` | 70% |
| E2E | Playwright | `e2e/**/*.spec.ts` | Critical paths |
| Backend Unit | pytest | `backend/tests/` | 80% |

### Test Levels

- **Unit:** Individual components, hooks, utils (isolated, fast)
- **Integration:** API routes, service layers, store interactions
- **E2E:** Full user flows (prompt → video export)

---

## Boundaries

### Always Do
- Run `npm run lint` and `npm run test` before commits
- Use semantic color tokens (`text-text-primary`, `bg-surface`)
- Include loading, error, and empty states
- Test keyboard navigation (Tab through entire flow)
- Follow existing Python pipeline patterns

### Ask First
- Adding new Python dependencies (especially ML models)
- Changing database schema (if added)
- Modifying CI/CD config
- Video model selection (SVD vs AnimateDiff vs ModelScope)

### Never Do
- Commit secrets or API keys
- Edit `node_modules` or vendor directories
- Remove failing tests without fixing
- Use raw hex colors or arbitrary pixel values
- Skip accessibility (WCAG 2.1 AA)

---

## Success Criteria

1. **UI Quality**
   - [ ] Responsive at 320px, 768px, 1024px, 1440px
   - [ ] Zero console errors in dev
   - [ ] All interactive elements keyboard accessible
   - [ ] Screen reader traverses entire pipeline
   - [ ] Loading skeletons, error boundaries, empty states everywhere

2. **Pipeline Functionality**
   - [ ] Prompt → story generation works
   - [ ] Story → scenes decomposition works
   - [ ] Scene → dialogues works
   - [ ] Scene → cinematic prompts works
   - [ ] Each stage regeneratable independently
   - [ ] Research phase toggleable

3. **Video Generation**
   - [ ] Single scene → video clip works
   - [ ] All scenes → clips works
   - [ ] Clips assembled into final MP4
   - [ ] Optional narration/dialogue overlay
   - [ ] Export downloads MP4

4. **Performance**
   - [ ] Pipeline view loads < 2s
   - [ ] Stage transitions < 500ms
   - [ ] Video generation progress tracked

---

## Open Questions

1. **Video Model:** Stable Video Diffusion (SVD) vs AnimateDiff vs ModelScope? SVD is higher quality but slower. AnimateDiff faster but lower quality.
2. **Audio:** Generate TTS narration? Use ElevenLabs API or local TTS (XTTS)? For now, skip audio and focus on video.
3. **GPU Requirements:** SVD needs 8GB+ VRAM. Should we support CPU fallback (very slow) or require GPU?
4. **Storage:** Where to store generated clips/videos? Local filesystem for MVP, S3 later.
5. **Authentication:** Multi-user? For MVP, single-user local app (no auth).

---

## Assumptions I'm Making

1. This is a **web application** (Next.js + FastAPI), not native mobile
2. **GPU available** for video generation (8GB+ VRAM for SVD)
3. **Ollama running locally** with required models (qwen2.5:32b, deepseek-coder-v2)
4. **Single-user local app** — no authentication, no multi-tenancy
5. **Python pipeline unchanged** — backend calls existing `pipeline/` modules
6. **Video generation is async** — polling for progress, not streaming
7. **MP4 output** using FFmpeg assembly

→ Correct me now or I'll proceed with these.