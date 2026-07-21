# Current Task: Complete Genesis Agent Development

## Objective
Complete all 31 Genesis agents (7 discovery + 19 PKP + 4 reviewers + 1 chief architect) so they produce only text output saved as individual files for downstream consumption.

## Constraints
- No agent creates image/audio/video — text output only
- All output saved as individual files (JSON/YAML/Markdown) in the output directory
- All 292 tests must pass
- CLI `--mock` flag must produce valid end-to-end pipeline output

## Done Conditions
- [x] All 31 agents have build_prompt, parse_response, validate
- [x] No agent creates media files
- [x] Output serialization saves individual spec files (JSON/YAML/MD)
- [x] Completion gate correctly aggregates contradictions and reviews
- [x] Discovery and review base classes have validate() methods
- [x] CLI `--mock` produces valid pipeline with 76 output files
- [x] 292 tests pass, 2 skipped

## Files in Scope
- `movie_os/genesis/` — all agent files, engine, CLI, serializers
- `tests/genesis/` — all test files
- `.project-ai/` — project status files

## Out of Scope
- Real LLM integration (LMStudio)
- Video/audio/image generation
- Studio Engine handoff
