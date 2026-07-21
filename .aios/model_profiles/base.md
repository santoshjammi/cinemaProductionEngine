---
name: "local-model-profile"
mode: "config"
version: "2.0"
---

# Local-First Model Configuration (LM Studio Integration)

## Context from `docs/notImp_defaultSettings.jsonc`
The platform relies heavily on local inference via LM Studio running on `localhost:1234`.

## Defaults
- **Provider**: LM Studio (`http://localhost:1234`)
- **Max Input Tokens**: 131072 (Context window)
- **Max Output Tokens**: 16384
- **Reasoning Effort**: Enabled for complex planning tasks.
- **Tool Calling**: Enabled (specifically for Qwen, Llama 3.1+, or Mistral).

## Usage in `videoGen`
- Use local models for storyboarding and context generation (e.g., Flux for images).
- Escalate to cloud APIs only for high-fidelity video encoding or specialized assets if local resources are exhausted.
