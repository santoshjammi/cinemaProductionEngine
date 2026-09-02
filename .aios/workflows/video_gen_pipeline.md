---
name: "video-gen-pipeline"
type: "orchestration"
version: "1.0"
---

# Video Generation Workflow

## Stages
1. **Scripting / Prompting**: User provides creative direction. (Agents: `creative-director`)
2. **Storyboarding / Context Setup**: Generate assets and scene descriptions. (Agents: `storyboarder`, Memories: `domain_knowledge`)
3. **Generation**: Route to appropriate rendering engines or model profiles. (Routing: `model_profiles/`)
4. **Validation**: Check for technical compliance, frame rates, and quality. (Validation: `quality_gates`)
5. **Compilation / Delivery**: Finalize and package output. (Execution: `delivery-runner`)

## Error Handling
If a stage fails, route to `validation/error-recovery` with specific context logs before retrying.
