I think we can make this much simpler than we’ve been discussing.

Instead of thinking in terms of three documents, think in terms of three AI agents, each with one responsibility.

                    Story Factory
             Human Input
                  │
                  ▼
         Story DNA Generator
                  │
           dna.yaml (100 tokens)
                  │
                  ▼
        Context Generator
                  │
           context.md (~600 words)
                  │
                  ▼
         Story Generator
                  │
            story.md (~1200 words)
                  │
                  ▼
      Existing Production Pipeline

Each agent receives only the output of the previous one, keeping prompts small and focused.

⸻

Stage 1 — Story DNA Generator

This is the only thing that reads the user’s synopsis.

Input

A man stops initiating intimacy after marriage because repeated rejection slowly convinces him he is no longer desired.

Output

id: EW-001
title: Why Some Men Stop Initiating Intimacy After Marriage
territory: Emotional Withdrawal
cluster: Fear-Based Withdrawal
primary_mechanism: Anticipated Rejection
secondary_mechanism: Masculine Shame
archetype: Married Husband
theme: Love becomes dangerous.
premise: A husband quietly stops reaching for his wife after repeated rejection.
central_question: Can a relationship survive when fear replaces vulnerability?
core_truth: He wasn't rejected by her first. He rejected vulnerability first.
ending: Quiet Realization
emotion_curve:
  - Hope
  - Hesitation
  - Withdrawal
  - Loneliness
  - Recognition

Notice:

No story.

No characters.

No scenes.

Just decisions.

Very cheap.

⸻

Stage 2 — Context Generator

This agent NEVER invents the story.

Its only job is to create the world.

Input:

dna.yaml

Plus retrieval:

Fear-Based Withdrawal Playbook
Marriage Archetype
Visual Language
Music Language
Narration Style

Output:

# Context
## Territory
Emotional Withdrawal
## Theme
Fear slowly replacing intimacy.
## Psychological Truth
Repeated emotional pain teaches the brain that connection is dangerous.
## Characters
Arjun
36
Engineer
Quiet.
Protective.
Emotionally restrained.
Maya
34
Teacher
Warm.
Affectionate.
Busy mother.
Neither is wrong.
Both misunderstand each other.
## Relationship
Eight-year marriage.
One daughter.
Still deeply love one another.
## Emotional Atmosphere
Quiet sadness.
Long pauses.
Unspoken thoughts.
## Visual Language
Muted interiors.
Night lighting.
Distance inside shared rooms.
Hands almost touching.
## Ending Emotion
Hope mixed with grief.

Notice something?

Still…

No story.

⸻

Stage 3 — Story Generator

This is the only creative writing stage.

Input

dna.yaml
+
context.md

Task

Write the narrative.
No camera.
No prompts.
No image descriptions.
No narration.
Only the story.

Output

Act 1
Arjun used to reach for Maya every night.
She would smile.
They would laugh.
...
Act 2
After months of stress...
...
Act 3
One evening Maya quietly asks...
"When did we stop touching?"
...

Only narrative.

Nothing else.

⸻

Why this is token efficient

Instead of one huge prompt:

Generate
Context
Characters
World
Psychology
Story
Scenes
Narration
Images
Camera
Music
...

You generate:

DNA
↓
Context
↓
Story

Each agent has one responsibility.

⸻

The prompts themselves become tiny

DNA Prompt

Given the synopsis, output ONLY Story DNA.
Return valid YAML.
Do not write story.
Do not write characters.
Do not explain.

~40 tokens.

⸻

Context Prompt

Using Story DNA and retrieved playbooks, generate context.md.
Describe only the world, psychology, characters and atmosphere.
Never narrate the plot.

~50 tokens.

⸻

Story Prompt

Using Story DNA and context.md, write story.md.
Focus only on narrative.
No scene prompts.
No production notes.
No camera directions.

~35 tokens.

⸻

Why quality improves

Each model is solving exactly one problem.

Instead of asking:

Write a cinematic story with characters, psychology, narration, pacing, symbolism, visuals…

You’re asking:

Agent 1

Decide.

Agent 2

Build the world.

Agent 3

Tell the story.

LLMs are much more consistent when they specialize.

⸻

One final optimization: make the generators deterministic

Don’t let the LLM decide everything every time. Give each generator a fixed contract.

For example:

* DNA Generator always outputs the same YAML schema.
* Context Generator always produces the same Markdown sections in the same order.
* Story Generator always follows the same narrative template:
    1. Opening state
    2. Inciting incident
    3. Escalation
    4. Midpoint shift
    5. Emotional collapse
    6. Climax
    7. Resolution

This means the LLM is only filling in the unique content, not inventing the structure. That dramatically reduces token usage, improves consistency, and makes every downstream component—from scene generation to narration and video assembly—more reliable. Over time, your “Story Factory” becomes a compiler: the DNA defines what the story is, the Context defines where and why it exists, and the Story defines what actually happens. Everything after that is production, not creativity.