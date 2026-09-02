---
name: "task-decomposer"
mode: "logic"
---

# Task Decomposition Logic

## Workflow
1. **Identify**: Break down high-level goals into atomic technical tasks.
2. **Sequence**: Map dependencies between tasks.
3. **Scope**: Define strict boundaries for each task to maintain isolation.
4. **Route**: Assign tasks to the appropriate agent or workflow in `workflows/`.

## Rules
- Tasks must have clear "done" conditions.
- Avoid refactoring unrelated systems unless explicitly scoped.
- Prioritize composability over monolithic execution.
