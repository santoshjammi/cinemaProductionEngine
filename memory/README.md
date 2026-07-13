# Movie OS v1 — Production Memory System

## Purpose

The Production Memory System is the **competitive moat** of the Cinema Production Engine. Every completed production contributes to a growing knowledge base that makes future productions better, faster, and more reliable.

> **This folder is your competitive advantage. It accumulates over time.**
>
> Every video you produce should leave a trace here. The traces are the IP.
> Models and tools commoditize. Accumulated emotional intelligence does not.

---

## Architecture

```
memory/
├── README.md                    # This file
├── failures/                    # What failed and why
│   ├── {production_id}/         # Per-production failure logs
│   │   ├── evaluation.yaml      # Failed evaluation scores
│   │   ├── revision_history.md  # What was revised and why
│   │   └── root_cause.md        # Root cause analysis
├── feedback/                    # Expert feedback patterns
│   ├── raw/                     # Raw expert feedback (date_source)
│   ├── synthesized/             # Synthesized rules
│   └── {production_id}/         # Per-production feedback
│       ├── expert_reviews.yaml  # Expert review results
│       └── pattern_analysis.md  # Patterns across reviews
├── retention/                   # Viewer retention insights
│   ├── {production_id}/         # Per-production retention data
│   │   ├── retention_curve.yaml # Retention by timestamp
│   │   └── dropoff_points.md    # Where viewers left
├── winning_patterns/            # What worked across productions
│   ├── themes/                  # Successful theme patterns
│   │   └── {theme_name}.yaml
│   ├── dialogue/                # Effective dialogue patterns
│   │   └── {pattern_type}.yaml
│   ├── visual/                  # Successful visual patterns
│   │   └── {style_name}.yaml
│   └── music/                   # Effective music patterns
│       └── {mood_name}.yaml
├── character_reuse/             # Reusable character definitions
│   └── {character_name}.yaml
└── environment_reuse/           # Reusable environment definitions
    └── {environment_name}.yaml
```

## What lives here

| Folder | What goes in | Why |
|--------|--------------|-----|
| `feedback/` | Expert feedback (raw + synthesized) | The rules that govern quality. Never override without updating the canonical spec. |
| `retention/` | Where viewers drop off, where they rewatch | The pacing observations. Which scenes land, which scenes lose people. |
| `winning_patterns/` | What works — specific scenes, voiceovers, transitions | The IP. Reuse these. |
| `failures/` | What didn't work — and WHY | Prevents repeating mistakes. |
| `character_reuse/` | Character definitions that proved effective | Avoid re-generating good characters from scratch |
| `environment_reuse/` | Environment definitions that proved effective | Avoid re-generating good environments from scratch |

## How to use this

### Adding feedback
- Drop the raw expert feedback in `feedback/raw/<date>_<source>.md`
- Synthesize into `feedback/synthesized.md` (or update an existing rule file)
- Update the canonical video spec / scene schema if the rule applies to all videos

### Adding retention data
- After publishing a video, observe analytics
- Note where viewers drop off, where they rewatch
- Write `retention/VID##_<date>.md` with observations
- This data informs future pacing decisions

### Adding winning patterns
- When a scene works, write it down: `winning_patterns/<territory>_<pattern>.md`
- Include: the scene, why it worked, what emotional logic it hit
- This becomes a library of proven scenes

### Adding failures
- When a scene doesn't work, write it down: `failures/<date>_<scene>.md`
- Include: the scene, why it didn't work, what to do differently
- This prevents repeating mistakes

---

## How It Works (Automated)

### 1. On Production Completion (Success)

When a production passes all evaluation thresholds:

```python
# In ProductionOrchestratorAgent.execute()
if all_passed:
    # Log winning patterns
    await _log_winning_patterns(context, result)
    
    # Extract reusable characters/environments
    await _extract_reusable_assets(context)
    
    # Update retention data (if viewer metrics available)
    if context.retention_data:
        await _update_retention(context)
```

### 2. On Production Failure

When any evaluation score falls below threshold:

```python
# In RevisionAgent.execute()
if failed_categories:
    # Log failure with root cause analysis
    await _log_failure(context, failed_categories)
    
    # Update failure patterns for future prevention
    await _update_failure_patterns(context)
```

### 3. Before Next Production

When starting a new production:

```python
# In ProductionOrchestratorAgent.execute()
# Load relevant patterns from memory
relevant_patterns = await _load_relevant_patterns(context)

# Inject patterns into agent prompts
context.memory_patterns = relevant_patterns
```

## Memory Patterns Loaded Per Grammar

| Grammar | Patterns Loaded | Source |
|---------|----------------|--------|
| psychological_cinema | Emotional withdrawal patterns, subtext-heavy dialogue examples | `winning_patterns/dialogue/` |
| kids_story | Age-appropriate language patterns, safe content rules | `feedback/kids_story/` |
| devotional | Sacred text accuracy patterns, reverent music motifs | `winning_patterns/music/` |
| documentary | Factual verification patterns, expert interview structures | `feedback/documentary/` |
| explainer | Clarity patterns, visual support examples | `winning_patterns/visual/` |
| shorts | Hook patterns (first 3s), scroll-stopping techniques | `winning_patterns/dialogue/` |
| narrative_film | Character arc patterns, cinematic language examples | `winning_patterns/themes/` |

## Integration with Evaluation Agents

Each evaluation agent writes to memory:

| Agent | Memory Location | What's Logged |
|-------|----------------|---------------|
| StoryQualityAgent | `failures/{id}/evaluation.yaml` | Failed dimensions, scores |
| DialogueQualityAgent | `winning_patterns/dialogue/` | Effective dialogue patterns |
| VisualConsistencyAgent | `winning_patterns/visual/` | Successful visual styles |
| AudioMixAgent | `failures/{id}/revision_history.md` | What was adjusted |
| EmotionScoreAgent | `feedback/{id}/pattern_analysis.md` | Emotional impact patterns |
| CharacterConsistencyAgent | `character_reuse/` | Reusable character definitions |
| YouTubeReadinessAgent | `retention/{id}/dropoff_points.md` | Predicted dropoff points |

## Compression Rules

Memory entries MUST follow these rules:

1. **Deterministic** — Same input always produces same output
2. **Implementation-focused** — No narrative, no speculation
3. **Minimize tokens** — Brief bullet points, not prose
4. **Actionable** — Every entry must be usable by future productions

Good:
```yaml
failures:
  - category: dialogue_quality
    score: 0.65
    threshold: 0.70
    root_cause: "characters spoke in complete essays"
    fix_applied: "fragmented dialogue, added pauses"
    result_score: 0.82
```

Bad:
```yaml
failures:
  - category: dialogue_quality
    score: 0.65
    threshold: 0.70
    root_cause: "I think the characters might have been speaking too formally, 
                 which could be because the writer was trying to make them sound 
                 educated but ended up making them unnatural"
```

## Task Isolation Rules

Before loading memory patterns:

1. Read `CURRENT_TASK.md` for active scope
2. Verify pattern relevance to current grammar
3. Only load patterns from same or compatible grammars
4. Never inject patterns from unrelated content types

Example:
- Current grammar: `kids_story`
- Load: `winning_patterns/dialogue/kids_story/`, `feedback/kids_story/`
- Skip: `winning_patterns/dialogue/psychological_cinema/` (too complex)

## Resumability Rules

At end of every production:

1. Update relevant memory files
2. Compress execution state
3. Remove obsolete details
4. Preserve only actionable engineering state

## Production Memory Lifecycle

```
New Production → Load Relevant Patterns → Execute Pipeline → 
Evaluate → Log Results (Success/Failure) → 
Extract Reusable Assets → Update Memory → 
Next Production Loads Updated Memory
```

---

## What does NOT live here

- **Tools** (those are in scripts/, backend/)
- **Generated assets** (those are in output/videos/)
- **Prompts in detail** (those are in PROMPT_LIBRARY.yaml, FORMULA.md)

---

*Production Memory System v1.0 — The moat that grows with every production*
- **Raw code** (that's in scripts/, backend/, app/)

This folder is for **accumulated wisdom**, not artifacts.

---

## Compounding effect

After 10 videos, you should have:
- 10 winning patterns you can reuse
- 5-10 documented failures
- 30+ pieces of feedback synthesized into rules
- A clear sense of what works in your territory

After 50 videos, the memory system should be **smarter than any one video**.
After 100, it should be smarter than any single human reviewer.

That's the moat. Tools commoditize. Memory compounds.
