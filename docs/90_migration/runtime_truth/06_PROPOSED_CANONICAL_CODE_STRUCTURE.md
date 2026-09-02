# 06_PROPOSED_CANONICAL_CODE_STRUCTURE

## Goal

Minimize the number of live runtime families while preserving the parts already working.

## Proposed surviving structure

```text
videoGen/
├── docs/
│   ├── 00_governance/
│   ├── 10_psychology/
│   ├── 20_standards/
│   ├── 30_app/
│   ├── 40_contracts/
│   ├── 50_execution/
│   └── 90_migration/
├── frontend/
├── backend/
├── movie_os/
│   ├── genesis2/          # canonical creative compiler
│   ├── prometheus/        # canonical production executor
│   ├── genesis3/          # quarantine until proven or intentionally merged
│   ├── auth/
│   ├── data_layer/
│   ├── providers/
│   ├── workflows/
│   └── llm/
├── productions/
│   └── EP-xxxx/
│       ├── contract/
│       ├── policy/
│       ├── genesis/
│       ├── runs/
│       │   └── RUN-xxxx/
│       ├── oracle/
│       └── releases/
└── tests/
```

## Canonical runtime choices

### GENESIS to survive

**Survivor candidate:** `movie_os/genesis2/`

Why:
- it is the active 12-phase creative engine in the best end-to-end runner
- it cleanly produces PKP artifacts
- it is the main bridge target for downstream Prometheus execution

Keep:
- `engine.py`
- `bridge.py`
- `models.py`
- `phases/`
- `llm_client.py`
- `llm_providers.py`

Quarantine/review:
- `movie_os/genesis/`
- `movie_os/genesis3/`

### PROMETHEUS to survive

**Survivor candidate:** `movie_os/prometheus/`

Why:
- it is the active media production boundary
- it has a clear stage pipeline and final film stage
- it already produces staged media artifacts and a final MP4

Keep:
- `pipeline.py`
- `engine.py`
- `stages/*`
- `models.py`
- `progress.py`
- `mock_provider.py`

Quarantine/review:
- root-level `prometheus/` package if not needed by tests or compatibility

### Main entrypoint to survive

**Survivor candidate:** `run_space_between_us.py`

Why:
- it is the clearest complete-video chain from synopsis → PKP → brief → Prometheus render
- it exercises the active runtime family directly
- it reaches the final assembly boundary with fewer extra layers than `run_production.py`

Secondary support runner:
- `run_prometheus_hq.py` for re-rendering from existing brief only

Likely retire or fold into support:
- `run_pipeline.py`
- `run_pipeline_clean.py`
- `run_production.py`
- `render_space_between_us.py`
- `run_genesis_to_prometheus.py`

## Proposed production directory canon

The docs require a production-scoped layout like:

```text
productions/
  EP-xxxx/
    contract/
    policy/
    genesis/
    runs/
      RUN-xxxx/
    oracle/
    releases/
```

### Current gap

Current runtime writes into many mutable roots such as:
- `output/space_between_us/`
- `output/prometheus/`
- `output/videos/final/`
- `output/the_space_between_us_final/`
- `artifacts/checkpoints/`

This must eventually collapse into a single production-scoped release tree.

## What survives in the app layer

### Keep

- frontend shell and pipeline/story UI components
- backend FastAPI service scaffolding
- route structure where it already wraps the production engine

### Adapt

- pipeline terminology
- Genesis3 integration points
- output path handling
- runtime status models

### Replace later

- marketing-first default homepage as the dominant app face for production work
- generic pipeline abstractions that obscure episode/contract/release semantics

## Migration principle

Keep the working media engine, but move authority upward into the docs-defined contract chain.

In other words:

1. preserve the working render mechanics
2. add contract/policy/canon enforcement around them
3. consolidate output paths and run manifests
4. retire duplicate runners only after the canonical path is stable
