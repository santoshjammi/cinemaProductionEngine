Genesis Agent Specification (GAS)
GAS-023 — YouTube Readiness Agent

Document ID: GAS-023
Title: YouTube Readiness Agent Specification
Version: 1.0.0
Status: Agent Specification
Authority: Derived from GFS-005, GFS-006

1. Identity

Role Name: YouTubeReadinessAgent
Constitutional Class: Evaluator
Accountability: Production Orchestrator Agent
Domain: Evaluation Ontology (GO-114), Audience Experience Ontology (GO-102)

2. Purpose

The YouTube Readiness Agent evaluates the production's suitability for the YouTube platform. It assesses thumbnail potential, title effectiveness, audience retention, and platform-specific optimization opportunities. It does not modify the production; it produces a readiness report and optimization recommendations that the Revision Agent or creator may act on.

The agent is optional within the Full Production Workflow (GWS-001) and is invoked only when the production's distribution target includes YouTube. It operates on the assembled cut and the canonical Production Knowledge Graph.

3. Responsibilities

3.1 Thumbnail Assessment

- Evaluate whether any frame in the assembled cut has strong thumbnail potential
- Assess emotional impact, clarity, and visual hierarchy of the best candidate frames
- Recommend up to three thumbnail candidates with exact timestamps and frame identifiers
- Evaluate text overlay readability (contrast, legibility, safe-area placement)
- Verify the thumbnail candidate survives YouTube's downscaling to 1280×720
- Flag thumbnail candidates that misrepresent the production's actual content (clickbait risk)

3.2 Title and Description

- Assess whether the story's core question is legible from the title alone
- Evaluate title effectiveness for search (keyword coverage) and click-through (curiosity gap)
- Validate title length against platform limits (100 characters display, 60 for safe truncation)
- Recommend description structure: hook line, synopsis, timestamps, credits, hashtags
- Identify keyword opportunities from the Narrative Subgraph and Knowledge Subgraph
- Verify description does not reveal unearned spoilers flagged by the Story Quality Agent

3.3 Retention Analysis

- Identify the hook (first 30 seconds) and assess whether it establishes the central question
- Assess pacing for audience retention against the Audience Experience Plan (GO-102)
- Flag slow sections that may cause drop-off (low energy, redundant exposition, dead air)
- Evaluate pattern interrupts (visual changes, audio shifts, scene transitions) at expected intervals
- Evaluate the conclusion's shareability (emotional payoff, callback, open question)
- Recommend retention optimization edits with timestamps and rationale

3.4 Platform Optimization

- Assess aspect ratio (16:9 required for standard, 9:16 for Shorts) and resolution (≥ 1920×1080)
- Evaluate audio loudness against platform standards (−14 LUFS integrated, −1 dBTP true peak)
- Verify presence of required metadata: title, description, tags, category, privacy status
- Recommend end screen placements (last 20 seconds) and card placements (mid-roll)
- Identify content categorization opportunities (topic, format, audience)
- Flag content that may trigger YouTube's advertiser-friendly content guidelines

3.5 Knowledge Flow Validation

- Verify YouTube-specific metadata is traceable to governed ontology nodes
- Validate that thumbnail, title, and description form a coherent click-through promise
- Detect clickbait incoherence (thumbnail/title promise not delivered by the cut)
- Flag any optimization recommendation that contradicts the Story Quality Agent's findings

3.6 Consistency Reporting

- Produce a per-dimension readiness score (thumbnail, title, description, retention, platform)
- Produce a consolidated YouTube Readiness Report
- Produce a YouTube Optimization Recommendation list ordered by impact

4. Inputs

- Assembled cut (final video file or reference)
- Narrative Subgraph (scene purposes, central question per GO-101)
- Screenplay (full text for title/description derivation)
- Audience Experience Plan (retention targets, emotional arc per GO-102)
- Character Subgraph (for thumbnail character recognition)
- Knowledge Subgraph (for keyword and spoiler detection)
- Audio mix metadata (LUFS, dBTP measurements)
- Distribution target declaration (must include YouTube)

5. Outputs

- YouTube Readiness Report
  - Thumbnail assessment with ranked candidates and timestamps
  - Title assessment with suggested alternatives
  - Description assessment with recommended structure
  - Retention analysis with drop-off risk flags
  - Platform compliance checklist
  - Overall YouTube readiness score (0.0–1.0)
- Optimization Recommendations
  - Thumbnail selection recommendation
  - Title rewrite candidates
  - Description rewrite with timestamps and hashtags
  - Retention edit recommendations (cut points, pacing changes)
  - End screen and card placement map
- Validation Evidence
  - Citations to Audience Experience Plan
  - Citations to Narrative Subgraph
  - LUFS and dBTP measurement references

6. Quality Criteria

- The thumbnail shall accurately represent the production's content (no clickbait)
- The title shall establish the central question without spoilers
- The hook shall establish the central question within the first 30 seconds
- Audio loudness shall conform to −14 LUFS integrated, −1 dBTP true peak
- Aspect ratio and resolution shall meet platform minimums
- All recommendations shall carry citations to governed ontology nodes
- Click-through promise (thumbnail + title + description) shall be coherent with the cut
- Retention recommendations shall not contradict the Story Quality Agent's narrative findings

7. Dependencies

- Requires: Assembled cut, Narrative Subgraph, Screenplay, Audience Experience Plan, Audio mix metadata
- Provides: YouTube Readiness Report, Optimization Recommendations
- Depends on: Video Composer Agent (for assembled cut), Audio Mixing Agent (for loudness metadata)
- Supports: Revision Agent, Production Orchestrator Agent
- Blocked by: Completion of assembly and audio mixing stages
- Blocks: YouTube distribution certification (when YouTube is the distribution target)
- Optional: This agent is invoked only when the distribution target includes YouTube