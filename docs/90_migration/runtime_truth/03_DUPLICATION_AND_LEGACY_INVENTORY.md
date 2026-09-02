# 03_DUPLICATION_AND_LEGACY_INVENTORY

## Classification key

- **ACTIVE** — currently participates in the real executable runtime
- **SUPPORTING** — required by active runtime but not itself a major architecture component
- **TEST_ONLY** — used only by tests
- **EXPERIMENTAL** — prototype or incomplete alternate implementation
- **DUPLICATE** — materially duplicates another implementation
- **LEGACY** — superseded by another implementation
- **UNKNOWN** — insufficient evidence

## Major implementation clusters

### GENESIS family

| Path | Classification | Evidence |
|---|---|---|
| `movie_os/genesis2/` | **ACTIVE** | used by `run_space_between_us.py`, `run_production.py`, and `movie_os.pipeline.run_full_pipeline()` |
| `movie_os/genesis/` | **LEGACY** | older top-level pre-production engine; `movie_os/pipeline.py` still imports it in older paths, but `genesis2` is the modern 12-phase engine |
| `movie_os/genesis3/` | **EXPERIMENTAL / SUPPORTING** | surfaced through backend API and docs, but not the main CLI production path |
| `tests/genesis/` | **TEST_ONLY** | test package by path/name |
| `tests/genesis2/` | **TEST_ONLY** | test package by path/name |
| `tests/genesis3/` | **TEST_ONLY** | test package by path/name |

### PROMETHEUS family

| Path | Classification | Evidence |
|---|---|---|
| `movie_os/prometheus/` | **ACTIVE** | explicit stage pipeline used by `run_space_between_us.py` and `run_prometheus_hq.py` |
| `prometheus/` | **LEGACY / DUPLICATE** | alternate top-level package in repo root; overlaps conceptually with `movie_os.prometheus` |
| `movie_os/pipeline.py` | **LEGACY / DUPLICATE** | unified wrapper that attempts Genesis2 + GENESIS3 + PrometheusEngine |
| `movie_os/prometheus/pipeline.py` | **ACTIVE** | current stage orchestrator |

### Pipeline entrypoint family

| Path | Classification | Evidence |
|---|---|---|
| `run_space_between_us.py` | **ACTIVE** | explicit full chain to Prometheus render |
| `run_prometheus_hq.py` | **SUPPORTING** | re-render only; consumes existing brief |
| `run_genesis_to_prometheus.py` | **SUPPORTING** | handoff utility; production-ready gate + Prometheus execution |
| `run_production.py` | **DUPLICATE** | overlaps with `run_space_between_us.py`, but uses a different orchestration stack |
| `run_pipeline.py` | **LEGACY / DUPLICATE** | older orchestration wrapper; imports older modules and output layout |
| `run_pipeline_clean.py` | **LEGACY / DUPLICATE** | older clean runner; same conceptual chain |
| `render_space_between_us.py` | **DUPLICATE** | direct ComfyUI/edge-tts/ffmpeg render path, bypasses the modern package boundary |

### Frontend / backend

| Path | Classification | Evidence |
|---|---|---|
| `frontend/` | **ACTIVE / SUPPORTING** | Next.js app is present and compiled; it exposes the product UI surfaces |
| `backend/` | **ACTIVE / SUPPORTING** | FastAPI backend routes are wired and include pipeline/genesis3/profiles/projects |

## Duplicate implementations by concern

### 1) Multiple GENESIS runtimes

- `movie_os/genesis/` = older pre-production runtime with discovery / PKP / reviewers / gate
- `movie_os/genesis2/` = 12-phase creative intelligence engine
- `movie_os/genesis3/` = compiler / QA / certification stack

**Conclusion:** `genesis2` is the best surviving creative-engine candidate for the new architecture. `genesis` and `genesis3` are overlapping alternate strata and should be reviewed separately before any removal.

### 2) Multiple pipeline orchestrators

- `movie_os/pipeline.py`
- `pipeline/orchestrator.py`
- `run_pipeline.py`
- `run_pipeline_clean.py`
- `run_production.py`
- `run_space_between_us.py`
- `run_genesis_to_prometheus.py`
- `render_space_between_us.py`

**Conclusion:** there is clear command duplication. The strongest complete-video path is the `run_space_between_us.py` chain; the others are alternate orchestrations or older wrappers.

### 3) Multiple output mechanisms

Observed output roots include:

- `output/space_between_us/`
- `output/videos/final/`
- `output/prometheus/`
- `output/the_space_between_us_final/`
- `artifacts/checkpoints/`
- `runtime/{tmp,logs,cache}/`
- `workspace/{imports,exports}/`
- `legacy_outputs/`

The code also references additional subpaths such as:

- `output/prometheus/films/`
- `output/prometheus/images/`
- `output/prometheus/voice/`
- `output/prometheus/music/`
- `output/prometheus/storyboard/`

### 4) Multiple configuration systems

- `config/movie_os.yaml`
- `genesis_llm.yaml`
- `movie_os/config/*`
- `backend/app/core/config.py`
- frontend environment files

**Conclusion:** configuration is still fragmented.

## Legacy evidence-only areas

The repo contains `legacy_outputs/` and `unimportant_docs/`; both are explicitly non-authoritative in the new docs tree.

Evidence:
- `docs/README.md:9-13`
- `docs/00_governance/00_AUTHORITY_AND_PRECEDENCE.md:124-136`

## Observed active/duplicate split

| Concern | Surviving runtime shape (evidence-backed) | Duplicate / legacy surfaces |
|---|---|---|
| Creative truth compilation | `movie_os.genesis2` | `movie_os.genesis`, `movie_os.genesis3`, `movie_os/pipeline.py` |
| Media production | `movie_os.prometheus` | root `prometheus/`, direct `render_space_between_us.py` |
| End-to-end film runner | `run_space_between_us.py` | `run_production.py`, `run_pipeline.py`, `run_pipeline_clean.py` |
| Web app | `frontend/` + `backend/` | large landing-page and ad surfaces unrelated to core film engine |
