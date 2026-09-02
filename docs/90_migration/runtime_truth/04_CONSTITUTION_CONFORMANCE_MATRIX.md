# 04_CONSTITUTION_CONFORMANCE_MATRIX

Legend: **PASS / PARTIAL / MISSING / VIOLATION / UNKNOWN**

## Conformance matrix

| Required capability | Current implementation | Status | Evidence |
|---|---|---|---|
| Episode Contract | `docs/40_contracts/EPISODE_CONTRACT.schema.yaml` exists, but no clear runtime bind-in was evidenced in the active runner | **PARTIAL** | docs + active runner trace lacks explicit episode-contract load step |
| Effective Policy Snapshot | Schema exists in docs; runtime not clearly loading it in the active complete-video path | **PARTIAL** | `docs/40_contracts/EFFECTIVE_POLICY_SNAPSHOT.schema.yaml`; no explicit load in `run_space_between_us.py` |
| RPCO classification | Clearly referenced in docs; no runtime evidence in the active runner | **MISSING** | no direct runtime trace found in `run_space_between_us.py` / `movie_os.prometheus` |
| Mark & Sarah canon loading | Mark/Sarah identities are hardcoded in `generate_films.py` and voiced/image-anchored in render stages, but not canon-loaded from authoritative registries in the main runner | **PARTIAL** | `generate_films.py:154-171`; `movie_os/prometheus/stages/image_stage.py:150-155`; `movie_os/prometheus/stages/voice_stage.py:27-35` |
| Continuity loading | Some scene continuity data exists in brief scenes, but no explicit registry-backed continuity loader in the active runner | **PARTIAL** | `docs/10_psychology/10_mark_sarah/04_MARK_SARAH_CONTINUITY_REGISTRY.yaml` exists; runner evidence absent |
| GENESIS owns exact dialogue | `Genesis2Engine` produces dialogue planning and the bridge feeds it downstream | **PASS** | `docs/50_execution/GENESIS_EXECUTION_CONTRACT.md:19-35`; `movie_os/genesis2/engine.py:127-148` |
| Emotional scene state | Scene emotional state is present in Genesis2-generated scenes and propagated into Prometheus brief | **PASS** | `generate_films.py:217-239`; `movie_os/prometheus/stages/music_stage.py:58-93` |
| Frozen PKP | PKP objects are produced and written, but the freeze boundary is not visibly enforced as an immutable contract in the runtime trace | **PARTIAL** | `run_space_between_us.py:74-102`; `docs/50_execution/GENESIS_EXECUTION_CONTRACT.md:48-60` |
| PROMETHEUS execution-only boundary | PROMETHEUS mainly executes stage artifacts and does not obviously rewrite creative meaning in the active pipeline | **PARTIAL** | `docs/50_execution/PROMETHEUS_EXECUTION_CONTRACT.md:29-40`; stage code shows execution focus, but no formal boundary check |
| Stable visual identity | Image prompts hardcode Mark/Sarah visual anchors; identity registry binding is not evidenced in the active path | **PARTIAL** | `movie_os/prometheus/stages/image_stage.py:150-155` |
| Stable voice identity | Voice mapping is hardcoded by speaker name; registry-based canon binding not evidenced | **PARTIAL** | `movie_os/prometheus/stages/voice_stage.py:27-35`, `42-47` |
| Shot-level lip-sync requirement | Film stage renders video over audio, but a dedicated visible-mouth lip-sync subsystem is not evidenced | **MISSING** | `docs/20_standards/MOTION_AND_LIPSYNC_STANDARD.md:13-37`; active code shows only Ken Burns / audio mix |
| Immutable production run manifest | Prometheus stages emit artifacts/results, but immutable run manifest generation is not clearly evidenced in the active runner trace | **PARTIAL** | `docs/50_execution/PROMETHEUS_EXECUTION_CONTRACT.md:53-59` |
| ORACLE independent validation | ORACLE contract exists; active runtime path does not show a real independent validation step before finalization | **MISSING** | `docs/50_execution/ORACLE_EXECUTION_CONTRACT.md:5-59` |
| Anti-AI-slop blocking gates | Standards/docs exist, but runtime gate enforcement is not clearly evidenced in the active runner | **PARTIAL** | `docs/20_standards/ANTI_AI_SLOP_QUALITY_STANDARD.md` exists; no active gate trace found |
| Production-specific artifact paths | Multiple production output roots exist, but they are fragmented and not yet aligned to the new `productions/EP-xxxx/...` layout | **VIOLATION** | `run_space_between_us.py`, `render_space_between_us.py`, `run_production.py` each write to different roots |
| Approved master/release concept | A final MP4 is produced, but the approved master/release concept is not enforced as a distinct runtime artifact class | **PARTIAL** | `docs/30_app/DOMAIN_MODEL.md:90-97`; `movie_os/prometheus/stages/film_stage.py:182-241` |

## Focused notes

### What is strongest today

- Exact dialogue synthesis exists in Genesis2 and flows downstream.
- Scene emotional state is preserved enough to influence music selection and visual prompt shaping.
- A final video file can be produced by the Prometheus film stage.

### What is weakest today

- No obvious runtime enforcement of Episode Contract → Policy Snapshot → PKP freeze → Oracle validation as a strict constitutional chain.
- No explicit runtime load of Mark/Sarah canonical registries in the active complete-video command.
- No dedicated lip-sync subsystem is demonstrated in the strongest active path.
- Output locations are not yet canonicalized to the new production structure.
