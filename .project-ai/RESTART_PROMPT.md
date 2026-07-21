# Restart Prompt

## Current Focus
Genesis Engine is complete: 31 agents, 292 tests, output serialization (76 files per run). Ready for real LLM integration and Studio Engine handoff.

## Unfinished Work
1. Connect to real LLM: start LMStudio, run `python -m movie_os.genesis run --synopsis <file>`
2. Implement LangGraph state machine in `genesis/graph.py` (currently sequential in engine.py)
3. Connect Genesis output to Studio Engine per `docs/genesis/specifications/integrations/007 — Genesis-Studio Engine Integration.md`
4. Run full E2E with real synopsis once LLM is connected

## Constraints
- All agents produce only text output (no image/audio/video)
- Output saved as individual files (JSON/YAML/Markdown) in the output directory
- LLM must be running on `http://127.0.0.1:1234` (LMStudio default) or use `--mock`
- 292 tests pass, 2 skipped

## Files in Scope
- `movie_os/genesis/` — all agent files, engine, CLI, serializers, mock_data
- `tests/genesis/` — all test files
- `docs/genesis/specifications/` — PKP specs and integration docs

## Next Action
Start LMStudio on port 1234, then run:
```bash
python -m movie_os.genesis run --synopsis ./synopsis/001-psychology-emotional-withdrawal.md --output ./output/genesis/
```
