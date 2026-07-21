import sys
import os
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.services.project_service import ProjectService
from config.models import EmotionalTone, validate_input, InputValidationError
from config.ollama_client import OllamaClient
from pipeline.orchestrator import (
    Pipeline, StageError, StoryGenerator, SceneDecomposer,
    DialogueGenerator, CinematicPromptGenerator, YAMLValidator, MetricsCollector,
)
from pipeline.research import ResearchStage, ResearchContext
from pipeline.output_saver import OutputSaver
from pipeline.scene_file_writer import SceneFileWriter
from backend.app.core.config import settings

logger = logging.getLogger("pipeline_service")


class PipelineService:
    """Wraps the existing text pipeline for FastAPI use."""

    def __init__(self):
        self._pipelines: dict[str, dict] = {}
        self._config = self._load_config()
        self._skip_execution = False
        self._project_service = ProjectService()
        self._backfill_default_project()

    def _load_config(self) -> dict:
        config_path = Path(settings.config_path)
        if config_path.exists():
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def _backfill_default_project(self):
        default = self._project_service.get_default_project()
        if not default:
            return
        for pid, state in self._pipelines.items():
            if not state.get("project_id"):
                state["project_id"] = default.id
                self._project_service.add_story_to_project(
                    default.id, pid, state.get("topic", ""), state.get("status", "pending")
                )

    async def start_pipeline(self, topic: str, tone: Optional[str] = None,
                             length: str = "conversational", platform: str = "cinematic",
                             enable_research: bool = True,
                             project_id: Optional[str] = None,
                             producer_brief: Optional[dict] = None,
                             profile_id: Optional[str] = None) -> dict:
        pipeline_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        state = {
            "id": pipeline_id,
            "topic": topic,
            "status": "running",
            "project_id": project_id,
            "stages": [
                {"name": "research", "status": "pending", "started_at": None, "completed_at": None, "error": None},
                {"name": "story", "status": "pending", "started_at": None, "completed_at": None, "error": None},
                {"name": "scenes", "status": "pending", "started_at": None, "completed_at": None, "error": None},
                {"name": "dialogues", "status": "pending", "started_at": None, "completed_at": None, "error": None},
                {"name": "prompts", "status": "pending", "started_at": None, "completed_at": None, "error": None},
                {"name": "validation", "status": "pending", "started_at": None, "completed_at": None, "error": None},
            ],
            "research": None,
            "story": None,
            "scenes": None,
            "dialogues": None,
            "prompts": None,
            "metrics": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }

        # Map free-form tone to valid EmotionalTone enum
        valid_tones = {e.value for e in EmotionalTone}
        if tone and tone.lower() in valid_tones:
            mapped_tone = tone.lower()
        else:
            mapped_tone = "wonder"

        config_data = {
            "topic": topic,
            "emotional_tone": mapped_tone,
            "story_length": length,
            "platform": platform if platform != "cinematic" else "youtube",
        }

        # Attach the GENESIS production profile so downstream stages
        # (story beats, scene decomposition) can derive scene count and
        # per-scene duration targets.
        try:
            from backend.app.services.profile_service import get_profile, derive_scene_count
            profile = get_profile(profile_id)
            config_data["production_profile"] = profile
            config_data["target_scene_count"] = derive_scene_count(profile_id)
        except Exception as e:
            logger.warning("Could not load production profile: %s", e)

        # Pass the full producer brief to the orchestrator for prompt generation
        if producer_brief:
            config_data["producer_brief"] = producer_brief

        # Validate before passing to pipeline (which also validates internally)
        validate_input(config_data)

        if not enable_research:
            self._config.setdefault("research", {})["enabled"] = False

        self._pipelines[pipeline_id] = state

        if project_id:
            self._project_service.add_story_to_project(project_id, pipeline_id, topic, "running")

        if not self._skip_execution:
            # Run pipeline in thread
            import asyncio
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self._run_pipeline, pipeline_id, config_data)
        else:
            # Test mode - mark as completed immediately
            self._pipelines[pipeline_id]["status"] = "completed"
            for s in self._pipelines[pipeline_id]["stages"]:
                s["status"] = "completed"

        return self._get_pipeline_response(pipeline_id)

    def _set_stage_status(self, pipeline_id: str, stage_name: str, status: str, error: str = None):
        state = self._pipelines.get(pipeline_id)
        if not state:
            return
        now = datetime.utcnow().isoformat()
        for s in state["stages"]:
            if s["name"] == stage_name:
                s["status"] = status
                s["error"] = error
                if status == "running" and not s["started_at"]:
                    s["started_at"] = now
                if status in ("completed", "failed"):
                    s["completed_at"] = now
        state["updated_at"] = now

    def _run_pipeline(self, pipeline_id: str, raw_input: dict):
        state = self._pipelines[pipeline_id]
        try:
            from config.prompts import (
                STORY_GENERATION_SYSTEM, STORY_GENERATION_USER_TEMPLATE,
                SCENE_DECOMPOSITION_SYSTEM, SCENE_DECOMPOSITION_USER_TEMPLATE,
                DIALOGUE_GENERATION_SYSTEM, DIALOGUE_GENERATION_USER_TEMPLATE,
                CINEMATIC_PROMPT_SYSTEM, CINEMATIC_PROMPT_USER_TEMPLATE,
            )

            input_config = validate_input(raw_input)

            # Initialize pipeline components
            endpoint = self._config.get("llm", {}).get("endpoint", "http://localhost:11434")
            models_cfg = self._config.get("models", {})
            orchestrator_model = models_cfg.get("orchestrator", {}).get("model", "qwen2.5:32b")
            creative_writer_model = models_cfg.get("creative_writer", {}).get("model", "deepseek-coder-v2:latest")

            orchestrator_llm = OllamaClient(endpoint=endpoint, model=orchestrator_model)
            creative_writer_llm = OllamaClient(endpoint=endpoint, model=creative_writer_model)

            story_gen = StoryGenerator(orchestrator_llm, self._config)
            scene_decomposer = SceneDecomposer(orchestrator_llm, self._config)
            dialogue_gen = DialogueGenerator(creative_writer_llm, self._config)
            prompt_gen = CinematicPromptGenerator(orchestrator_llm, self._config)
            validator = YAMLValidator()
            metrics = MetricsCollector(self._config)
            research_stage = ResearchStage(self._config)

            # Derive production profile parameters (soft guidance)
            profile = raw_input.get("production_profile") or {}
            runtime_cfg = profile.get("runtime", {})
            scene_policy = profile.get("scene_policy", {})
            target_minutes = runtime_cfg.get("target_minutes", 18)
            min_min = runtime_cfg.get("minimum_minutes", 15)
            max_min = runtime_cfg.get("maximum_minutes", 20)
            target_runtime = f"{min_min}-{max_min} minutes (target {target_minutes})"
            dur_range = scene_policy.get("preferred_scene_duration_seconds", [75, 90])
            scene_duration_range = f"{dur_range[0]}-{dur_range[1]}s"
            target_scene_count = raw_input.get("target_scene_count") or 14

            scene_classes = profile.get("scene_classes", {})
            if scene_classes:
                scene_class_guidance = ", ".join(
                    f"{cls} ({v['duration_seconds'][0]}-{v['duration_seconds'][1]}s): {v.get('purpose','')}"
                    for cls, v in scene_classes.items()
                )
            else:
                scene_class_guidance = ""

            # Stage 0: Research
            self._set_stage_status(pipeline_id, "research", "running")
            research_context = None
            if self._config.get("research", {}).get("enabled", True):
                try:
                    research_context = research_stage.research(input_config.topic)
                except Exception as e:
                    logger.warning(f"Research phase failed (non-fatal): {e}")
                    research_context = ResearchContext(topic=input_config.topic)
            self._set_stage_status(pipeline_id, "research", "completed")

            # Stage 1: Story Generation
            self._set_stage_status(pipeline_id, "story", "running")
            story_outline = story_gen.generate(
                input_config,
                research_context=research_context,
                target_scene_count=target_scene_count,
                scene_duration_range=scene_duration_range,
                scene_class_guidance=scene_class_guidance,
                target_runtime=target_runtime,
            )
            self._set_stage_status(pipeline_id, "story", "completed")

            # Stage 2: Scene Decomposition
            self._set_stage_status(pipeline_id, "scenes", "running")
            scenes_data = scene_decomposer.decompose(
                story_outline,
                scene_duration_range=scene_duration_range,
                scene_class_guidance=scene_class_guidance,
                target_scene_count=target_scene_count,
            )
            self._set_stage_status(pipeline_id, "scenes", "completed")

            # Stage 3: Dialogue Generation
            self._set_stage_status(pipeline_id, "dialogues", "running")
            dialogues = dialogue_gen.generate(scenes_data)
            self._set_stage_status(pipeline_id, "dialogues", "completed")

            # Stage 4: Cinematic Prompts
            self._set_stage_status(pipeline_id, "prompts", "running")
            prompts = prompt_gen.generate(scenes_data)
            self._set_stage_status(pipeline_id, "prompts", "completed")

            # Stage 5: Validation + Metrics
            self._set_stage_status(pipeline_id, "validation", "running")
            try:
                is_valid = validator.validate(story_outline, scenes_data, prompts)
                if not is_valid:
                    raise StageError("YAML Validation", "Validation failed")
            except StageError as e:
                logger.error(f"Validation failed: {e}")
                raise

            metrics.record_validation_pass()
            metrics.record_scene_completion(scenes_data)
            metrics.record_emotional_arc(scenes_data)
            metrics.record_visual_prompt_quality(prompts)
            metric_data = metrics.get_metrics()
            self._set_stage_status(pipeline_id, "validation", "completed")

            # Assemble result
            from pipeline.orchestrator import PipelineOutput
            result = PipelineOutput(
                story_yaml_content=story_outline,
                scenes_yaml_content=scenes_data,
                dialogues_yaml_content=dialogues,
                prompts_yaml_content=prompts,
                research_context=research_context.to_dict() if research_context else None,
            )

            self._update_from_result(pipeline_id, result, metric_data, raw_input)
            project_id = state.get("project_id")
            if project_id:
                self._project_service.update_story_status(project_id, pipeline_id, "completed")

        except Exception as e:
            logger.exception(f"Pipeline {pipeline_id} failed")
            state["status"] = "failed"
            state["error"] = str(e)
            state["updated_at"] = datetime.utcnow().isoformat()
            project_id = state.get("project_id")
            if project_id:
                self._project_service.update_story_status(project_id, pipeline_id, "failed")

    def _update_from_result(self, pipeline_id: str, result, metric_data: dict = None, raw_input: dict = None):
        state = self._pipelines[pipeline_id]
        topic = state["topic"]

        state["status"] = "completed"
        state["updated_at"] = datetime.utcnow().isoformat()

        if result.research_context:
            rc = result.research_context
            state["research"] = {
                "topic": rc.get("topic", topic),
                "summary": rc.get("summary", ""),
                "sources": [
                    {"title": s.get("title", ""), "url": s.get("url", ""), "snippet": s.get("snippet", "")}
                    for s in (rc.get("sources") or [])
                ],
                "key_findings": rc.get("key_findings", []),
            }

        # Story
        story = result.story_yaml_content
        state["story"] = {
            "title": story.get("title", f"Story about {topic}"),
            "logline": story.get("logline", story.get("narrative", "")[:120]),
            "synopsis": story.get("narrative", story.get("synopsis", "")),
            "emotional_tone": story.get("emotional_tone", "wonder"),
            "themes": story.get("themes", []),
            "target_audience": story.get("target_audience", "general"),
            "research_context": story.get("research_context"),
        }

        # Scenes
        scenes = result.scenes_yaml_content
        state["scenes"] = [
            {
                "scene_number": s.get("id", i + 1),
                "title": s.get("title", s.get("narration", "")[:60]),
                "description": s.get("narration", ""),
                "location": s.get("location", s.get("camera", "unknown")),
                "characters": s.get("characters", []),
                "emotional_beat": s.get("emotion", "neutral"),
                "duration": s.get("duration", "80s"),
                "scene_class": s.get("scene_class", ""),
            }
            for i, s in enumerate(scenes)
        ]

        # Dialogues
        dialogues = result.dialogues_yaml_content
        scene_dialogues: dict[int, list] = {}
        for d in dialogues:
            sn = d.get("scene_id", d.get("sceneNumber", 1))
            if sn not in scene_dialogues:
                scene_dialogues[sn] = []
            scene_dialogues[sn].append({
                "character": d.get("character", d.get("speaker", "Narrator")),
                "dialogue": d.get("dialogue", d.get("dialogue_text", "")),
                "emotion": d.get("emotion", "neutral"),
                "delivery": d.get("delivery", "normal"),
            })
        state["dialogues"] = [
            {"scene_number": sn, "dialogues": lines}
            for sn, lines in sorted(scene_dialogues.items())
        ]

        # Prompts
        prompts = result.prompts_yaml_content
        state["prompts"] = [
            {
                "scene_number": p.get("scene_id", p.get("sceneNumber", i + 1)),
                "cinematic_prompt": p.get("prompt", p.get("cinematic_prompt", "")),
                "visual_style": p.get("visual_style", p.get("style", "cinematic")),
                "camera_angle": p.get("camera_angle", p.get("camera", "wide")),
                "lighting": p.get("lighting", "dramatic"),
                "color_palette": p.get("color_palette", []),
            }
            for i, p in enumerate(prompts)
        ]

        # Metrics
        if metric_data:
            state["metrics"] = {
                "yaml_validation_pass_rate": metric_data.get("yaml_validation_pass_rate", 1.0),
                "scene_completion_rate": metric_data.get("scene_completion_rate", 1.0),
                "emotional_arc_score": metric_data.get("emotional_arc_score", 0.85),
                "visual_prompt_quality_score": metric_data.get("visual_prompt_quality_score", 0.9),
                "total_scenes": len(scenes),
                "total_duration": metric_data.get("total_duration"),
            }
        else:
            state["metrics"] = {
                "yaml_validation_pass_rate": 1.0,
                "scene_completion_rate": 1.0,
                "emotional_arc_score": 0.85,
                "visual_prompt_quality_score": 0.9,
                "total_scenes": len(scenes),
                "total_duration": None,
            }

        # Save to disk (YAML files) and canonical scenes.json
        try:
            saver = OutputSaver()
            paths = saver.save(
                result.story_yaml_content,
                scenes,
                result.dialogues_yaml_content,
                result.prompts_yaml_content,
                research=result.research_context,
            )
            # Extract the run_dir from the saved scenes path
            scenes_yaml_path = paths.get("scenes", "")
            run_dir = Path(scenes_yaml_path).parent.parent if scenes_yaml_path else saver.base_dir

            writer = SceneFileWriter(run_dir)
            writer.write(
                story=result.story_yaml_content if isinstance(result.story_yaml_content, dict) else {},
                scenes=[dict(s) if hasattr(s, "__dict__") else s for s in result.scenes_yaml_content],
                dialogues=result.dialogues_yaml_content or [],
                prompts=result.prompts_yaml_content or [],
            )
        except Exception as e:
            logger.warning(f"Failed to save output: {e}")

    def get_pipeline(self, pipeline_id: str) -> Optional[dict]:
        state = self._pipelines.get(pipeline_id)
        if state is None:
            return None
        return self._get_pipeline_response(pipeline_id)

    def _get_pipeline_response(self, pipeline_id: str) -> dict:
        state = self._pipelines[pipeline_id]
        return {
            "id": state["id"],
            "topic": state["topic"],
            "status": state["status"],
            "project_id": state.get("project_id"),
            "stages": state["stages"],
            "research": state["research"],
            "story": state["story"],
            "scenes": state["scenes"],
            "dialogues": state["dialogues"],
            "prompts": state["prompts"],
            "metrics": state["metrics"],
            "error": state["error"],
            "created_at": state["created_at"],
            "updated_at": state["updated_at"],
        }

    def retry_stage(self, pipeline_id: str, stage: str) -> Optional[dict]:
        state = self._pipelines.get(pipeline_id)
        if state is None:
            return None

        for s in state["stages"]:
            if s["name"] == stage:
                s["status"] = "pending"
                s["error"] = None
                s["started_at"] = None
                s["completed_at"] = None

        state["status"] = "running"
        state["updated_at"] = datetime.utcnow().isoformat()

        # Re-run from this stage
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self._rerun_from_stage, pipeline_id, stage)

        return self._get_pipeline_response(pipeline_id)

    def _rerun_from_stage(self, pipeline_id: str, stage: str):
        state = self._pipelines[pipeline_id]
        try:
            if self._skip_execution:
                for s in state["stages"]:
                    s["status"] = "completed"
                state["status"] = "completed"
                state["updated_at"] = datetime.utcnow().isoformat()
                return

            pipeline = Pipeline(llm_client=None, config=self._config)
            raw_input = {
                "topic": state["topic"],
                "emotional_tone": "wonder",
                "story_length": "medium",
                "platform": "youtube",
            }
            result = pipeline.run(raw_input)
            self._update_from_result(pipeline_id, result)
        except Exception as e:
            logger.exception(f"Pipeline {pipeline_id} retry failed")
            state["status"] = "failed"
            state["error"] = str(e)
            state["updated_at"] = datetime.utcnow().isoformat()

    def import_script(self, script: dict, project_id: Optional[str] = None) -> dict:
        """Inject a pre-written script directly as a completed pipeline,
        bypassing the LLM stages. The script dict must contain:
        topic, story, scenes, dialogues, prompts.
        """
        pipeline_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        state = {
            "id": pipeline_id,
            "topic": script.get("topic", "Imported script"),
            "status": "completed",
            "project_id": project_id,
            "stages": [
                {"name": "research", "status": "completed",
                 "started_at": now, "completed_at": now, "error": None},
                {"name": "story", "status": "completed",
                 "started_at": now, "completed_at": now, "error": None},
                {"name": "scenes", "status": "completed",
                 "started_at": now, "completed_at": now, "error": None},
                {"name": "dialogues", "status": "completed",
                 "started_at": now, "completed_at": now, "error": None},
                {"name": "prompts", "status": "completed",
                 "started_at": now, "completed_at": now, "error": None},
                {"name": "validation", "status": "completed",
                 "started_at": now, "completed_at": now, "error": None},
            ],
            "research": script.get("research"),
            "story": script.get("story"),
            "scenes": script.get("scenes"),
            "dialogues": script.get("dialogues"),
            "prompts": script.get("prompts"),
            "metrics": {
                "yaml_validation_pass_rate": 1.0,
                "scene_completion_rate": 1.0,
                "emotional_arc_score": 0.95,
                "visual_prompt_quality_score": 0.9,
                "total_scenes": len(script.get("scenes", [])),
                "total_duration": None,
            },
            "error": None,
            "created_at": now,
            "updated_at": now,
        }

        self._pipelines[pipeline_id] = state

        if project_id:
            self._project_service.add_story_to_project(
                project_id, pipeline_id, state["topic"], "completed"
            )

        return self._get_pipeline_response(pipeline_id)

    def get_history(self) -> list[dict]:
        return [
            self._get_pipeline_response(pid)
            for pid, state in sorted(
                self._pipelines.items(),
                key=lambda x: x[1]["created_at"],
                reverse=True,
            )
        ][:20]
