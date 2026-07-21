---
name: "intent-compiler"
mode: "logic"
---

# Intent-to-Execution Compiler

## Purpose
Translates user intent into structured, executable logic.

## Mapping Logic
- **Feature / New Functionality** -> `planners/` + `workflows/video-gen-pipeline`
- **Bug / Failure** -> `agents/debugger` + `validation/error-recovery`
- **Refactoring / Simplification** -> `agents/architect` + `policies/code-quality`
- **Architecture / Planning** -> `planners/task-decomposer` + `memories/project_memory`

## Output Format
{
  "intent": "<parsed_user_goal>",
  "mapped_skill": "<skill_name>",
  "required_agents": ["<agent_1>", "<agent_2>"],
  "validation_gates": ["<gate_1>", "<gate_2>"]
}
