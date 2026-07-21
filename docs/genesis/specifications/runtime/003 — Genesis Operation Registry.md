Genesis Specification (GSPEC)
GSPEC-003 — Genesis Operation Registry

Document ID: GSPEC-003
Title: Genesis Operation Registry
Version: 1.0.0
Status: Specification
Authority: Derived from GFS-011

1. Purpose

This Registry defines all operations that can be requested via the Agent Communication Protocol (GFS-011). Each operation has a unique identifier, input schema, output schema, and responsible agent type.

2. Operation Categories

2.1 Discovery Operations (OP-DIS-*)

OP-DIS-001: research_topic — Research a topic and return findings
  Agent: ResearchAgent
  Input: { topic: string, depth: string }
  Output: { findings: array, confidence: string }

OP-DIS-002: identify_gaps — Identify knowledge gaps in the PKG
  Agent: ResearchAgent
  Input: { subgraph_ids: array }
  Output: { gaps: array, priorities: array }

2.2 Narrative Operations (OP-NAR-*)

OP-NAR-001: design_narrative — Design the narrative structure
  Agent: StoryArchitectAgent
  Input: { brief: object, characters: array }
  Output: { narrative_subgraph: object }

OP-NAR-002: write_screenplay — Write the screenplay
  Agent: ScreenplayWriterAgent
  Input: { narrative_subgraph: object }
  Output: { screenplay: string, scenes: array }

OP-NAR-003: write_dialogue — Write dialogue for scenes
  Agent: DialogueWriterAgent
  Input: { screenplay: string, characters: array }
  Output: { dialogue: array }

OP-NAR-004: review_psychology — Review psychological accuracy
  Agent: PsychologyReviewerAgent
  Input: { narrative_subgraph: object, characters: array }
  Output: { validation_report: object }

2.3 Character Operations (OP-CHA-*)

OP-CHA-001: model_character — Model a character's DNA
  Agent: CharacterManagerAgent
  Input: { name: string, role: string, description: string }
  Output: { character_dna: object }

OP-CHA-002: validate_consistency — Validate character consistency
  Agent: CharacterConsistencyAgent
  Input: { character_subgraph: object }
  Output: { consistency_report: object }

2.4 Environment Operations (OP-ENV-*)

OP-ENV-001: model_environment — Model an environment's DNA
  Agent: EnvironmentManagerAgent
  Input: { name: string, type: string, description: string }
  Output: { environment_dna: object }

2.5 Planning Operations (OP-PLN-*)

OP-PLN-001: plan_scenes — Decompose screenplay into scenes
  Agent: ScenePlannerAgent
  Input: { screenplay: string }
  Output: { scene_plan: array }

OP-PLN-002: plan_shots — Decompose scenes into shots
  Agent: ShotPlannerAgent
  Input: { scene_plan: array }
  Output: { shot_plan: array }

OP-PLN-003: compose_music — Design music score
  Agent: MusicComposerAgent
  Input: { narrative_subgraph: object }
  Output: { music_score: object }

OP-PLN-004: build_prompts — Build image generation prompts
  Agent: PromptBuilderAgent
  Input: { shot_plan: array, characters: array, environments: array }
  Output: { shot_prompts: array }

2.6 Generation Operations (OP-GEN-*)

OP-GEN-001: generate_images — Generate images for shots
  Agent: ImageGeneratorAgent
  Input: { shot_prompts: array }
  Output: { images: array }

OP-GEN-002: generate_voice — Generate voice audio
  Agent: VoiceGeneratorAgent
  Input: { narration: string, dialogue: array }
  Output: { voice_audio: array }

OP-GEN-003: generate_music — Generate music tracks
  Agent: MusicGeneratorAgent
  Input: { music_score: object }
  Output: { music_tracks: array }

OP-GEN-004: generate_sfx — Generate sound effects
  Agent: SFXGeneratorAgent
  Input: { scene_plan: array, environments: array }
  Output: { sfx_tracks: array }

2.7 Post-Production Operations (OP-POST-*)

OP-POST-001: mix_audio — Mix audio tracks
  Agent: AudioMixingAgent
  Input: { voice: array, music: array, sfx: array }
  Output: { mixed_audio: array }

OP-POST-002: generate_subtitles — Generate subtitle tracks
  Agent: SubtitleAgent
  Input: { narration: string, dialogue: array, timing: array }
  Output: { subtitle_files: array }

OP-POST-003: compose_video — Compose final video
  Agent: VideoComposerAgent
  Input: { images: array, audio: array, subtitles: array }
  Output: { final_video: string }

2.8 Evaluation Operations (OP-EVAL-*)

OP-EVAL-001: evaluate_story — Evaluate story quality
  Agent: StoryQualityAgent
  Input: { narrative_subgraph: object, screenplay: string }
  Output: { evaluation_report: object }

OP-EVAL-002: evaluate_dialogue — Evaluate dialogue quality
  Agent: DialogueQualityAgent
  Input: { dialogue: array, characters: array }
  Output: { evaluation_report: object }

OP-EVAL-003: evaluate_visuals — Evaluate visual consistency
  Agent: VisualConsistencyAgent
  Input: { images: array, shot_plan: array }
  Output: { evaluation_report: object }

OP-EVAL-004: evaluate_audio — Evaluate audio mix quality
  Agent: AudioMixQualityAgent
  Input: { mixed_audio: array }
  Output: { evaluation_report: object }

OP-EVAL-005: evaluate_emotion — Evaluate emotional impact
  Agent: EmotionScoreAgent
  Input: { narrative_subgraph: object, screenplay: string }
  Output: { evaluation_report: object }

OP-EVAL-006: evaluate_characters — Evaluate character consistency
  Agent: CharacterConsistencyAgent
  Input: { character_subgraph: object, screenplay: string }
  Output: { evaluation_report: object }

OP-EVAL-007: evaluate_youtube — Evaluate YouTube readiness
  Agent: YouTubeReadinessAgent
  Input: { final_video: string, narrative_subgraph: object }
  Output: { evaluation_report: object }

2.9 Orchestration Operations (OP-ORC-*)

OP-ORC-001: create_production — Create a new production session
  Agent: ProductionOrchestratorAgent
  Input: { brief: object }
  Output: { session_id: string, production_plan: object }

OP-ORC-002: revise_production — Revise production based on evaluation
  Agent: RevisionAgent
  Input: { evaluation_reports: array, production_plan: object }
  Output: { revision_plan: object }

OP-ORC-003: certify_readiness — Certify production readiness
  Agent: GovernanceAgent
  Input: { production_knowledge_package: object }
  Output: { certificate: object }
