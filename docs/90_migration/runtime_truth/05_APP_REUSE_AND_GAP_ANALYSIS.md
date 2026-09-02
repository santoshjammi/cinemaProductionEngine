# 05_APP_REUSE_AND_GAP_ANALYSIS

## What to reuse vs replace

| Area | Current functionality | Recommendation | Evidence |
|---|---|---|---|
| Studio | Next.js frontend with multiple landing and pipeline views | **ADAPT** | `frontend/src/app/page.tsx`, `frontend/src/app/pipeline/[id]/page.tsx`, `frontend/src/app/genesis3/page.tsx` |
| Content Map | story / project / pipeline browsing UI already exists | **ADAPT** | `frontend/src/components/projects/*`, `frontend/src/components/story/*`, `frontend/src/components/pipeline/*` |
| Universes | not clearly modeled as first-class app object in backend/frontend | **MISSING** | no clear surfaced universe model in backend routes or frontend pages |
| Episodes | pipeline/story pages exist, but not clearly aligned to the new Episode Contract domain | **ADAPT** | `backend/app/api/v1/pipeline.py`, `frontend/src/components/pipeline/PipelineView.tsx` |
| GENESIS | Genesis3 route and Genesis2 panels exist; Genesis2 is closest to creative runtime | **ADAPT / KEEP** | `backend/app/api/v1/genesis3.py`, `frontend/src/app/genesis3/page.tsx`, `movie_os/genesis2/*` |
| Production | pipeline service and Prometheus engine/stages exist | **KEEP / ADAPT** | `backend/app/services/pipeline_service.py`, `movie_os/prometheus/*` |
| Quality / ORACLE | ORACLE docs exist, backend route for GENESIS3 certification exists, but not full independent media validation | **ADAPT** | `docs/50_execution/ORACLE_EXECUTION_CONTRACT.md`, `backend/app/api/v1/genesis3.py` |
| Distribution | frontend landing / product marketing surfaces exist, but release-packaging is not canonicalized | **ADAPT / REPLACE** | `frontend/src/app/page.tsx`; no production release manager surfaced |
| Governance | docs tree is authoritative, but app runtime has not fully adopted the contract chain | **ADAPT** | `docs/00_governance/*`, `docs/30_app/*`, `docs/40_contracts/*`, `docs/50_execution/*` |

## App capability evaluation

### 1) Studio

**Current state:** present.

Evidence:
- `frontend/src/app/page.tsx` renders a landing/studio-like marketing shell.
- `frontend/src/components/pipeline/PipelineView.tsx` is a richer operator surface.

**Reuse:** yes. The UI shell can likely stay.

**Gap:** the studio is not yet obviously centered on Episode Contract → policy resolution → frozen PKP → Oracle review.

### 2) Content Map

**Current state:** partial.

Evidence:
- `frontend/src/components/projects/StoryTable.tsx`
- `frontend/src/components/story/StoryViewer.tsx`
- `frontend/src/components/scenes/SceneTimeline.tsx`

**Reuse:** yes.

**Gap:** no explicit production/canon graph for universes, characters, continuity, releases.

### 3) Universes

**Current state:** missing as a first-class app capability.

Evidence:
- backend routes do not expose a universe resource directly in the inspected files
- frontend pages emphasize projects/pipelines/genesis rather than universe canon

**Action later:** likely add/adapt a canonical universe layer rather than recreating project pages.

### 4) Episodes

**Current state:** partial.

Evidence:
- pipeline service and pipeline route can create and track story production states
- but they are still framed as generic “pipeline” rather than contract-first episodes

**Reuse:** yes, but adapt the data model and UI labels.

### 5) GENESIS

**Current state:** split across multiple generations.

Evidence:
- `movie_os/genesis2/` is the strongest modern creative compiler path
- `movie_os/genesis/` is the older pre-production runtime
- `movie_os/genesis3/` is a new certification/QA layer

**Recommendation:** keep the existing UI hooks and the `genesis2` engine; isolate `genesis3` as a quality/review layer until it is proven or merged intentionally.

### 6) Production

**Current state:** functional and reusable.

Evidence:
- `movie_os/prometheus/pipeline.py`
- stage files under `movie_os/prometheus/stages/`
- PrometheusEngine wrapper

**Reuse:** yes. This is the strongest reusable execution nucleus.

### 7) Quality / ORACLE

**Current state:** partial.

Evidence:
- ORACLE contract docs exist
- GENESIS3 backend route exists
- but no verified media validation loop in the strongest active runtime trace

**Recommendation:** adapt the backend and UI, but do not treat it as already satisfied.

### 8) Distribution

**Current state:** UI marketing/distribution surfaces exist; release management is incomplete.

Evidence:
- landing sections in `frontend/src/components/landing/*`
- no explicit immutable release manager surfaced in the active app trace

**Recommendation:** retain the app shell, but production release semantics need a new canonical layer.

### 9) Governance

**Current state:** excellent docs, incomplete runtime enforcement.

Evidence:
- `docs/00_governance/*`
- `docs/30_app/*`
- `docs/40_contracts/*`
- `docs/50_execution/*`

**Recommendation:** keep the docs; wire the runtime to them in a narrower, contract-first flow.

## Minimum viable reuse set

Likely reusable today:

- frontend app shell and component library
- pipeline view / story editor / scene timeline / project pages
- backend FastAPI app and route scaffolding
- `movie_os.genesis2`
- `movie_os.prometheus`
- docs in `docs/00_governance`, `docs/10_psychology`, `docs/20_standards`, `docs/30_app`, `docs/40_contracts`, `docs/50_execution`

Likely to replace or heavily rewire later:

- generic pipeline wording / model
- legacy `movie_os.genesis`
- overlapping runners (`run_pipeline.py`, `run_pipeline_clean.py`)
- fragmented output root conventions
- non-contract-first runtime surfaces

## Gap summary

### Already present

- creative analysis engine
- rendering pipeline
- frontend operator surfaces
- FastAPI backend
- governance and contracts docs

### Missing for the new architecture

- explicit Episode Contract runtime model
- policy resolution loader
- registry-backed canon binding
- frozen PKP boundary enforcement
- independent ORACLE validation loop
- canonical production/release directory structure
- a single authoritative end-to-end command path
