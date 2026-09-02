# 02_ENTRYPOINT_AND_DEPENDENCY_MAP

## Entrypoint inventory

| Command / module | Role | Evidence |
|---|---|---|
| `python run_space_between_us.py` | closest complete-video runtime | `run_space_between_us.py:1-145` |
| `python run_production.py` | broader orchestration path | `run_production.py:1-410` |
| `python run_prometheus_hq.py` | re-render Prometheus only | `run_prometheus_hq.py:1-64` |
| `python render_space_between_us.py` | direct render path | `render_space_between_us.py:1-49` |
| `python run_genesis_to_prometheus.py --synopsis ...` | Genesis → PROMETHEUS handoff | `run_genesis_to_prometheus.py:1-107` |
| `movie_os.pipeline.run_full_pipeline()` | library entrypoint / older unified path | `movie_os/pipeline.py:1-149` |

## Dependency map: `run_space_between_us.py`

```text
run_space_between_us.py
  ├─ movie_os.genesis2.Genesis2Engine
  │   ├─ movie_os.genesis2.llm_client.LLMClient
  │   ├─ movie_os.genesis2.llm_providers.LLMConfig
  │   └─ movie_os.genesis2.phases.PHASE_CLASSES
  ├─ movie_os.genesis2.bridge.Genesis2Bridge
  │   └─ movie_os.genesis2.models
  └─ movie_os.prometheus.pipeline.PrometheusPipeline
      ├─ movie_os.prometheus.models.ProductionCertificate
      ├─ movie_os.prometheus.stages.storyboard_stage.StoryboardStage
      ├─ movie_os.prometheus.stages.image_stage.ImageGenerationStage
      ├─ movie_os.prometheus.stages.voice_stage.VoiceStage
      ├─ movie_os.prometheus.stages.music_stage.MusicStage
      ├─ movie_os.prometheus.stages.editing_stage.EditingStage
      └─ movie_os.prometheus.stages.film_stage.FilmStage
```

## Dependency map: `run_production.py`

```text
run_production.py
  ├─ movie_os.genesis2.Genesis2Engine
  ├─ movie_os.genesis2.MockLLMClient (fallback)
  ├─ movie_os.genesis2.bridge.Genesis2Bridge
  ├─ movie_os.agents.graph.build_graph / run_graph
  └─ movie_os.prometheus.engine.PrometheusEngine
      └─ movie_os.prometheus.pipeline.PrometheusPipeline
```

Evidence:
- `run_production.py:34-37`
- `run_production.py:218-410`

## Dependency map: `run_genesis_to_prometheus.py`

```text
run_genesis_to_prometheus.py
  ├─ movie_os.genesis.engine.GenesisEngine
  ├─ movie_os.genesis.llm_factory.create_client
  ├─ movie_os.genesis2.genesis_to_prometheus.GenesisPrometheusAdapter
  └─ movie_os.prometheus.engine.PrometheusEngine
```

Evidence:
- `run_genesis_to_prometheus.py:45-104`

## Dependency map: `render_space_between_us.py`

```text
render_space_between_us.py
  ├─ ComfyUI HTTP API
  ├─ edge_tts
  ├─ ffmpeg / ffprobe
  └─ local assets/music
```

This path does not use Genesis2 or Prometheus as a package; it is a direct render script.

Evidence:
- `render_space_between_us.py:1-31`
- `render_space_between_us.py:89-259`
- `render_space_between_us.py:260-493`

## Dependency map: library runtime surfaces

### `movie_os.genesis2.engine.Genesis2Engine`

- `PHASE_CLASSES` drives the 12-phase pipeline
- `save_package()` writes PKP artifacts
- `run_with_ollama()` uses Ollama

Evidence:
- `movie_os/genesis2/engine.py:31-229`

### `movie_os.prometheus.pipeline.PrometheusPipeline`

- creates 6 stages
- injects progress tracker if available
- stage order is fixed
- stage outputs are appended to context

Evidence:
- `movie_os/prometheus/pipeline.py:48-333`

### `movie_os.prometheus.engine.PrometheusEngine`

- lightweight wrapper around `PrometheusPipeline`
- converts pipeline result to dict with `stage_summary` / `artifact_dicts`

Evidence:
- `movie_os/prometheus/engine.py:14-99`

## Notable runtime dependencies

### External / system dependencies

- Ollama / local LLM endpoint
- ComfyUI at `http://127.0.0.1:8188`
- edge-tts
- ffmpeg / ffprobe

Evidence:
- `run_space_between_us.py:56-58`, `109-125`
- `movie_os/prometheus/stages/image_stage.py:36-46`, `78-107`
- `movie_os/prometheus/stages/voice_stage.py:184-212`
- `movie_os/prometheus/stages/film_stage.py:34-158`

## Active vs supporting vs duplicate status

| Component | Classification | Evidence |
|---|---|---|
| `run_space_between_us.py` | ACTIVE | direct 3-step end-to-end chain to final render |
| `run_production.py` | ACTIVE / DUPLICATE | broader alternate runtime; overlaps heavily |
| `run_genesis_to_prometheus.py` | ACTIVE / SUPPORTING | handoff utility, not full film assembly by itself |
| `render_space_between_us.py` | ACTIVE / DUPLICATE | direct renderer, but separate from Genesis2/PROMETHEUS chain |
| `movie_os.pipeline` | LEGACY / DUPLICATE | older unified pipeline, still present |
| `movie_os.genesis` | LEGACY / DUPLICATE | older pre-production engine |
| `movie_os.genesis2` | ACTIVE | modern 12-phase PKP engine |
| `movie_os.prometheus` | ACTIVE | current production execution boundary |
| `movie_os.genesis3` | EXPERIMENTAL / SUPPORTING | exists in app/API, but not the primary video path |

## Notes on command reachability

- `run_space_between_us.py` reaches real media generation artifacts via Prometheus stages.
- `run_production.py` additionally reaches `movie_os.agents.graph` and `GENESIS3` style certification flow.
- `movie_os.pipeline.run_full_pipeline()` executes Genesis2, attempts GENESIS3, then PrometheusEngine; it is a library convenience wrapper, not the clearest CLI authority.
