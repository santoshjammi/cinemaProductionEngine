---
name: "base-model-profile"
mode: "config"
version: "1.0"
---

# Base Model Configuration

## Defaults
- **Temperature**: 0.7 (Balanced creativity and precision)
- **Max Tokens**: 4096 (Standard context window)
- **System Prompt**: Loads `.aios/prompts/core_interaction.md`
- **Knowledge Injection**: Injects `.aios/memories/schema.yaml` upon initialization

## Customization
Specific profiles for video generation should override these defaults to optimize for token-heavy context windows and deterministic output.
