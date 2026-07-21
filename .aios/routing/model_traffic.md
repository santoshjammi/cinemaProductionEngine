---
name: "model-routing"
mode: "config"
version: "1.0"
---

# Model Routing & Traffic Management

## Routing Logic
- **Complex Reasoning** -> High-capacity models (e.g., O3, Claude Opus)
- **Rapid Execution** -> Optimized inference models (e.g., Sonnet, GPT-4o)
- **Specialized Tasks** -> Dedicated profiles in `model_profiles/`

## Constraints
- Monitor context window usage to prevent overflow during video generation pipelines.
