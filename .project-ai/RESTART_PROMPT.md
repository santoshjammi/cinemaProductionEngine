# Restart Prompt - Movie OS Cinema Production Engine

The repository has been successfully bootstrapped with a complete AI Operating System (AIOS) under `.ai/`, `.github/`, and root directories.

## Current Focus
Apply code fixes to resolve critical bugs identified during the initial verification and testing:
1. Fix the Pydantic configuration dictionary lookup bug in `movie_os/agents/graph.py` (line 111).
2. Fix the legacy fallback method name bug in the Ollama client `movie_os/llm/client.py` (line 114).

## Next Actions
- Inspect `movie_os/agents/graph.py` around line 111 and replace `config.get(...)` with attribute or dict conversions.
- Inspect `movie_os/llm/client.py` around line 114 and correct the fallback function name to `_generate_legacy`.
- Run pytest verification checks.
