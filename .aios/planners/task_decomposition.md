---
name: "task-decomposer"
mode: "logic"
---

# Task Decomposition Logic (Multi-Agent Focus)

## Reference: `specs/phase8_multi_agent.md`

## Workflow
1. **Identify**: Is this a creative task (requires narrative context) or a technical task (requires file system/code changes)?
2. **Sequence**: 
   - Creative -> Story Context DNA -> Production Design -> Asset Gen.
   - Technical -> ProjectService Update -> OpenMontage Integration.
3. **Route**: Assign to `cinema-director` (creative) or `system-architect` (technical).

## Rules
- Always verify state against `PROJECT_MEMORY.yaml` before starting multi-agent work.
