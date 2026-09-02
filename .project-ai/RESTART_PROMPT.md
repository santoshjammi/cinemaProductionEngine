# Restart Prompt

## Current Focus
ComfyUI freeze is fixed, and VRAM memory optimization is integrated so models are actively released when generation finishes. `pipeline/run_v7.py` and `verify_pipeline.py` are fully functional and pass all tests and E2E validation checks.

## Unfinished Work
1. Tune LLM prompt configurations for PKP-02/05/09/10 to avoid missing required fields under deepseek-coder-v2.
2. Resolve PKP-15 (Blueprint) generation from the dependency chain.
3. Wire the Genesis backend APIs into the frontend panels.

## Constraints
- Pipeline requires local Ollama (port 11434) and ComfyUI (port 8188) to be running for real generation.
- Python tests must use the local virtual environment `venv/bin/pytest`.

## Files in Scope
- `movie_os/genesis/` — all agent files, engine, CLI, serializers, mock_data
- `movie_os/workflows/` — comfyui client and workflow templates
- `pipeline/` — generation and audio pipeline scripts

## Next Action
To tune the PKP prompt templates:
```bash
venv/bin/python -m movie_os.genesis run --synopsis ./synopsis/001-psychology-emotional-withdrawal.md --output ./output/genesis/
```
