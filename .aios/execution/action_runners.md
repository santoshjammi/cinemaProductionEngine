---
name: "action-runners"
mode: "executor"
version: "1.0"
---

# Action Execution & Tool Mappings

## Available Runners
- **code-runner**: Executes sandboxed shell commands for production tasks.
- **video-compiler**: Manages FFmpeg/encoding pipelines for generation.
- **file-system-agent**: Handles structured reading/writing across `.aios/` and `docs/`.

## Execution Rules
- All runners must validate against `policies/compliance_and_safety.md`.
- Output must be deterministic and mapped to the appropriate context or memory store.
