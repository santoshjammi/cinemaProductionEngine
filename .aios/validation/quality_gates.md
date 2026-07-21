---
name: "quality-gates"
mode: "validator"
version: "1.0"
---

# Quality Gates & Verification Logic

## Pre-Execution Gates
- Validate user intent against `compilers/intent_mapping.md`.
- Ensure required agents and resources are available in `agents/` and `memories/`.

## Post-Execution Gates
- **Code Quality**: Syntax checks, linting, and adherence to platform standards.
- **Video Specs**: Resolution, frame rate, codec compliance (e.g., H.264/H.265).
- **Safety & Policy**: Cross-reference outputs against `policies/compliance_and_safety.md`.

## Error Recovery Protocol
If a gate fails:
1. Log the failure in the active context (`contexts/`).
2. Route to `planners/task-decomposer` for scoped correction.
3. Re-validate before proceeding.
