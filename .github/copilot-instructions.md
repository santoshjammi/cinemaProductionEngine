# Copilot Instructions

When coding in this repository:
- **Local LLM Constraints**: Keep prompt templates, system instructions, and file reads context-efficient (minimizing tokens) to support local inference engines (Qwen2.5-Coder-32B, Deepseek-Coder-v2).
- **Architecture**: Follow the modular pipeline design: Domain Model -> Capability Registry -> Providers -> Media Engines.
- **Languages**: Python >=3.8 for backend/core, Next.js/TypeScript for frontend.
- **Bug Fixes**: Prioritize fixing the Pydantic dictionary lookup in `graph.py` and the fallback method call in `client.py`.
