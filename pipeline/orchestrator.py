"""
Pipeline Orchestrator and Stage Implementations
Manages the 5 stages: Story Generation, Scene Decomposition, Dialogue Generation, Cinematic Prompt Generation, YAML Validation
"""

import os
import sys
import json
import logging
import yaml
from typing import Dict, Any, List

# Support both package and direct execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.models import InputConfig, PipelineOutput, Scene, validate_input, InputValidationError
from config.ollama_client import OllamaClient, OllamaError
from pipeline.research import ResearchStage, ResearchContext
from backend.app.services.genesis import StorytellerAgent, PromptEngineerAgent, AudioDirectorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pipeline")

class StageError(Exception):
    def __init__(self, stage_name: str, message: str):
        self.stage_name = stage_name
        super().__init__(f"Failure in {stage_name}: {message}")

class StoryGenerator:
    """Stage 1: Story Generation — powered by local LLM."""

    def __init__(self, llm_client: OllamaClient = None, config: dict = None):
        self.llm = llm_client or OllamaClient()
        self.config = config or {}

    def generate(self, input_config: InputConfig, research_context: ResearchContext = None,
                 target_scene_count: int = 5, scene_duration_range: str = "75-90s",
                 scene_class_guidance: str = "",
                 target_runtime: str = "15-20 minutes") -> Dict[str, Any]:
        logger.info(f"[StoryGeneration] Generating story for topic: '{input_config.topic}'")

        setting_info = f"Setting: {input_config.setting}" if input_config.setting else "Setting: unspecified"
        character_info = f"Character constraints: {input_config.character_constraints}" if input_config.character_constraints else ""

        # Build research context string if available
        research_info = ""
        if research_context and research_context.combined_context:
            research_info = f"\nResearch Context:\n{research_context.to_prompt_context()}"
        else:
            research_info = "\nResearch Context: (none — generate from your own knowledge)"

        if not scene_class_guidance:
            scene_class_guidance = (
                "hook (30-60s), establishment (45-75s), dialogue (60-120s), "
                "emotional_peak (90-120s), montage (20-45s), reflection (60-90s), "
                "transition (15-30s), climax (90-120s), epilogue (45-75s)"
            )

        user_prompt = STORY_GENERATION_USER_TEMPLATE.format(
            emotional_tone=input_config.emotional_tone.value,
            topic=input_config.topic,
            platform=input_config.platform.value,
            story_length=input_config.story_length,
            pacing_style=input_config.pacing_style or "normal",
            target_audience=input_config.target_audience or "general",
            target_runtime=target_runtime,
            target_scene_count=target_scene_count,
            scene_duration_range=scene_duration_range,
            scene_class_guidance=scene_class_guidance,
            setting_info=setting_info,
            character_info=character_info,
            research_context=research_info,
        )

        messages = [
            {"role": "system", "content": STORY_GENERATION_SYSTEM},
            {"role": "user", "content": user_prompt},
        ]

        stage_cfg = self.config.get("stage_settings", {}).get("story_generation", {})
        response = self.llm.chat(
            messages,
            temperature=stage_cfg.get("temperature", 0.85),
            max_tokens=stage_cfg.get("max_tokens", 3000),
            top_p=stage_cfg.get("top_p", 0.95),
        )

        self._fallback_topic = input_config.topic
        story = self._parse_json_response(response)
        logger.info(f"[StoryGeneration] Story generated: '{story.get('title', 'Untitled')}'")
        return story

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response (handles markdown code blocks)."""
        text = text.strip()
        # Remove markdown code fences if present
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                stripped = part.strip()
                if stripped.startswith("json"):
                    stripped = stripped[4:].strip()  # Remove 'json' prefix
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON object/array in the text
        brace_start = text.find('{')
        bracket_start = text.find('[')
        
        if brace_start >= 0:
            candidate = text[brace_start:]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        if bracket_start >= 0:
            candidate = text[bracket_start:]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        # Last resort: return a fallback dict with the raw text
        logger.warning("Could not parse JSON from LLM response, using fallback")
        return {
            "title": f"Story about {self._fallback_topic}",
            "narrative": text[:500],
            "emotional_arc": {"beginning": "Start", "middle": "Middle", "end": "End"},
            "beats": [{"id": 1, "description": text[:100]}],
        }


class SceneDecomposer:
    """Stage 2: Scene Decomposition — powered by local LLM."""

    def __init__(self, llm_client: OllamaClient = None, config: dict = None):
        self.llm = llm_client or OllamaClient()
        self.config = config or {}

    def decompose(self, story_outline: Dict[str, Any],
                  scene_duration_range: str = "75-90s",
                  scene_class_guidance: str = "",
                  target_scene_count: Optional[int] = None) -> List[Dict[str, str]]:
        logger.info("[SceneDecomposition] Decomposing story into scenes")

        beats_text = "\n".join(
            f"Beat {b['id']}: {b['description']}"
            + (f" [scene_class={b['scene_class']}]" if b.get("scene_class") else "")
            for b in story_outline.get("beats", [])
        )
        num_scenes = target_scene_count or len(story_outline.get("beats", []))

        if not scene_class_guidance:
            scene_class_guidance = (
                "hook (30-60s), establishment (45-75s), dialogue (60-120s), "
                "emotional_peak (90-120s), montage (20-45s), reflection (60-90s), "
                "transition (15-30s), climax (90-120s), epilogue (45-75s)"
            )

        user_prompt = SCENE_DECOMPOSITION_USER_TEMPLATE.format(
            num_scenes=num_scenes,
            title=story_outline.get("title", "Untitled"),
            emotional_tone=story_outline.get("tone", story_outline.get("emotional_tone", "")),
            pacing=story_outline.get("pacing", "normal"),
            scene_duration_range=scene_duration_range,
            scene_class_guidance=scene_class_guidance,
            beats_text=beats_text,
        )

        messages = [
            {"role": "system", "content": SCENE_DECOMPOSITION_SYSTEM},
            {"role": "user", "content": user_prompt},
        ]

        stage_cfg = self.config.get("stage_settings", {}).get("scene_decomposition", {})
        response = self.llm.chat(
            messages,
            temperature=stage_cfg.get("temperature", 0.7),
            max_tokens=stage_cfg.get("max_tokens", 2500),
            top_p=stage_cfg.get("top_p", 0.9),
        )

        scenes = self._parse_json_response(response)
        if isinstance(scenes, str):
            scenes = json.loads(scenes)
        logger.info(f"[SceneDecomposition] Generated {len(scenes)} scenes")
        return scenes

    def _parse_json_response(self, text: str) -> Any:
        """Extract JSON from LLM response (handles markdown code blocks)."""
        text = text.strip()
        # Remove markdown code fences if present
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                stripped = part.strip()
                if stripped.startswith("json"):
                    stripped = stripped[4:].strip()  # Remove 'json' prefix
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON object/array in the text
        brace_start = text.find('{')
        bracket_start = text.find('[')
        
        if brace_start >= 0:
            candidate = text[brace_start:]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        if bracket_start >= 0:
            candidate = text[bracket_start:]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        # Last resort: return a fallback list with the raw text
        logger.warning("Could not parse JSON from LLM response, using fallback")
        return [{"id": 1, "narration": text[:200], "emotion": "calm", "camera": "wide shot", "lighting": "natural", "visual_prompt": text[:150]}]


class DialogueGenerator:
    """Stage 3: Dialogue Generation — powered by local LLM."""

    def __init__(self, llm_client: OllamaClient = None, config: dict = None):
        self.llm = llm_client or OllamaClient()
        self.config = config or {}

    def generate(self, scenes_data: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        logger.info("[DialogueGeneration] Generating dialogue for scenes")

        scenes_text = "\n".join(
            f"Scene {s['id']}: {s['narration']} (emotion: {s['emotion']})"
            for s in scenes_data
        )

        user_prompt = DIALOGUE_GENERATION_USER_TEMPLATE.format(
            title="Story",
            emotional_tone="mixed",
            scenes_text=scenes_text,
        )

        messages = [
            {"role": "system", "content": DIALOGUE_GENERATION_SYSTEM},
            {"role": "user", "content": user_prompt},
        ]

        stage_cfg = self.config.get("stage_settings", {}).get("dialogue_generation", {})
        response = self.llm.chat(
            messages,
            temperature=stage_cfg.get("temperature", 0.9),
            max_tokens=stage_cfg.get("max_tokens", 1500),
            top_p=stage_cfg.get("top_p", 0.95),
        )

        dialogues = self._parse_json_response(response)
        if isinstance(dialogues, str):
            dialogues = json.loads(dialogues)
        
        # Validate that dialogue contains actual spoken words, not visual descriptions
        for d in dialogues:
            dialogue_text = d.get("dialogue_text", "")
            # Check for common visual description patterns
            visual_patterns = ["a shot of", "close-up on", "wide shot", "camera", "lighting", "scene shows"]
            is_visual = any(pattern.lower() in dialogue_text.lower() for pattern in visual_patterns)
            if is_visual and len(dialogue_text) > 20:
                logger.warning(f"Dialogue appears to be visual description, not spoken words. Replacing with fallback.")
                d["dialogue_text"] = f"A voice speaks about {d.get('scene_id', '?')}..."
        
        logger.info(f"[DialogueGeneration] Generated {len(dialogues)} dialogue entries")
        return dialogues

    def _parse_json_response(self, text: str) -> Any:
        """Extract JSON from LLM response. Handles markdown code blocks, escaped strings, and raw JSON."""
        text = text.strip()

        # 1. Handle markdown code fences (```json ... ``` or ``` ... ```)
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                stripped = part.strip()
                if stripped.startswith("json"):
                    stripped = stripped[4:].strip()
                if not stripped:
                    continue
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    continue

        # 2. Handle escaped JSON strings (model returned a JSON string literal)
        if text.startswith('"'):
            try:
                inner = json.loads(text)
                if isinstance(inner, (dict, list)):
                    return inner
                if isinstance(inner, str):
                    return self._parse_json_response(inner)
            except (json.JSONDecodeError, TypeError):
                pass

        # 3. Try to find outermost JSON array or object by bracket matching
        def find_outermost_json(s, start_char, end_char):
            start = s.find(start_char)
            if start < 0:
                return None
            depth = 0
            in_string = False
            escape = False
            for i in range(start, len(s)):
                ch = s[i]
                if escape:
                    escape = False
                    continue
                if ch == '\\':
                    escape = True
                    continue
                if ch == '"':
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                    if depth == 0:
                        candidate = s[start:i+1]
                        try:
                            return json.loads(candidate)
                        except json.JSONDecodeError:
                            return None
            return None

        result = find_outermost_json(text, '[', ']')
        if result is not None:
            return result
        result = find_outermost_json(text, '{', '}')
        if result is not None:
            return result

        # 4. Last resort: return a fallback list with the raw text
        logger.warning("Could not parse JSON from LLM response, using fallback")
        return [{"scene_id": 1, "speaker": "Narrator", "dialogue_text": text[:200], "emotion": "calm"}]


class CinematicPromptGenerator:
    """Stage 4: Cinematic Prompt Generation — powered by local LLM."""

    def __init__(self, llm_client: OllamaClient = None, config: dict = None):
        self.llm = llm_client or OllamaClient()
        self.config = config or {}

    def generate(self, scenes_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        logger.info("[CinematicPromptGeneration] Generating cinematic prompts")

        prompts = []
        for scene in scenes_data:
            user_prompt = CINEMATIC_PROMPT_USER_TEMPLATE.format(
                scene_id=scene["id"],
                narration=scene["narration"],
                emotion=scene["emotion"],
                camera=scene["camera"],
                lighting=scene["lighting"],
            )

            messages = [
                {"role": "system", "content": CINEMATIC_PROMPT_SYSTEM},
                {"role": "user", "content": user_prompt},
            ]

            stage_cfg = self.config.get("stage_settings", {}).get("cinematic_prompt_generation", {})
            response = self.llm.chat(
                messages,
                temperature=stage_cfg.get("temperature", 0.8),
                max_tokens=stage_cfg.get("max_tokens", 2000),
                top_p=stage_cfg.get("top_p", 0.9),
            )

            prompt_data = self._parse_json_response(response)
            if isinstance(prompt_data, str):
                prompt_data = json.loads(prompt_data)

            # Ensure consistent structure
            prompts.append({
                "scene_id": scene["id"],
                "prompt": prompt_data.get("prompt", f"Cinematic scene: {scene['narration']}"),
                "negative_prompt": prompt_data.get("negative_prompt", "blurry, low quality, deformed"),
                "style_tags": prompt_data.get("style_tags", ["cinematic", "dramatic"]),
            })

        logger.info(f"[CinematicPromptGeneration] Generated {len(prompts)} prompts")
        return prompts

    def _parse_json_response(self, text: str) -> Any:
        """Extract JSON from LLM response. Handles markdown code blocks, escaped strings, and raw JSON."""
        text = text.strip()
        
        # First, try to handle escaped JSON strings (e.g., from CinematicPromptGenerator)
        if text.startswith('"') and text.endswith('"'):
            try:
                # Unescape the outer quotes
                inner_text = json.loads(text)
                if isinstance(inner_text, str):
                    return self._parse_json_response(inner_text)
                return inner_text
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Handle markdown code fences
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                stripped = part.strip()
                if stripped.startswith("json"):
                    stripped = stripped[4:].strip()
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON object/array in the text by looking for { or [
        brace_start = text.find('{')
        bracket_start = text.find('[')
        
        candidates = []
        if brace_start >= 0:
            candidates.append(text[brace_start:])
        if bracket_start >= 0:
            candidates.append(text[bracket_start:])
        
        for candidate in candidates:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        
        # Last resort: return fallback
        logger.warning("Could not parse JSON from LLM response, using fallback")
        return {"prompt": text[:200], "negative_prompt": "blurry", "style_tags": ["cinematic"]}

class YAMLValidator:
    """Stage 5: YAML Validation"""
    
    def validate(self, story: Dict, scenes: List[Dict], prompts: List[Dict]) -> bool:
        print("[YAMLValidation] Validating output structures")
        
        # Check mandatory fields in scenes
        mandatory_fields = ['id', 'narration', 'emotion', 'camera', 'lighting', 'visual_prompt']
        for scene in scenes:
            for field in mandatory_fields:
                if field not in scene or not scene[field]:
                    raise StageError("YAML Validation", f"Scene {scene.get('id')} missing required field: {field}")
            
            if not scene['narration']:
                 raise StageError("YAML Validation", f"Scene {scene['id']} has empty narration")
        
        # Check prompt consistency (simple check)
        if len(prompts) != len(scenes):
             raise StageError("YAML Validation", "Mismatch between number of scenes and prompts")
             
        return True

class MetricsCollector:
    """Collects PRD-specified metrics: yaml_validation_pass_rate, scene_completion_rate,
    emotional_arc_score, visual_prompt_quality_score."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.metrics = {
            'yaml_validation_pass_rate': 0.0,
            'scene_completion_rate': 0.0,
            'emotional_arc_score': 0.0,
            'visual_prompt_quality_score': 0.0,
        }
        self._total_validations = 0
        self._passed_validations = 0

    def record_validation_pass(self):
        """Record a successful YAML validation."""
        self._total_validations += 1
        self._passed_validations += 1
        self.metrics['yaml_validation_pass_rate'] = (
            self._passed_validations / self._total_validations if self._total_validations > 0 else 0.0
        )

    def record_scene_completion(self, scenes: List[Dict[str, Any]]):
        """Calculate scene completion rate based on mandatory fields present."""
        if not scenes:
            self.metrics['scene_completion_rate'] = 0.0
            return

        mandatory_fields = ['id', 'narration', 'emotion', 'camera', 'lighting', 'visual_prompt']
        total_fields = len(scenes) * len(mandatory_fields)
        completed_fields = 0
        for scene in scenes:
            for field in mandatory_fields:
                if field in scene and scene[field]:
                    completed_fields += 1
        self.metrics['scene_completion_rate'] = completed_fields / total_fields if total_fields > 0 else 0.0

    def record_emotional_arc(self, scenes: List[Dict[str, Any]]):
        """Calculate emotional arc score: ratio of unique emotions across scenes."""
        if not scenes:
            self.metrics['emotional_arc_score'] = 0.0
            return

        emotions = [s.get('emotion', '') for s in scenes if s.get('emotion')]
        unique_emotions = set(emotions)
        # Score: higher when emotions vary (progression), normalized by scene count
        self.metrics['emotional_arc_score'] = len(unique_emotions) / len(scenes) if scenes else 0.0

    def record_visual_prompt_quality(self, prompts: List[Dict[str, Any]]):
        """Calculate visual prompt quality: average presence of key visual elements."""
        if not prompts:
            self.metrics['visual_prompt_quality_score'] = 0.0
            return

        quality_keywords = ['cinematic', 'lighting', 'shot', 'camera', 'atmosphere', 'detailed', 'resolution']
        scores = []
        for p in prompts:
            text = p.get('prompt', '').lower()
            hits = sum(1 for kw in quality_keywords if kw in text)
            scores.append(hits / len(quality_keywords))
        self.metrics['visual_prompt_quality_score'] = sum(scores) / len(scores) if scores else 0.0

    def get_metrics(self) -> Dict[str, float]:
        return dict(self.metrics)

    def save(self):
        """Save metrics to YAML file if enabled in config."""
        metrics_cfg = self.config.get('metrics', {})
        if not metrics_cfg.get('enabled', False):
            return

        output_file = metrics_cfg.get('output_file', 'pipeline/metrics/metrics.yaml')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            yaml.dump(self.metrics, f, default_flow_style=False)
        logger.info(f"[Metrics] Saved to {output_file}")


class Pipeline:
    """Main Pipeline Orchestrator — wired to local LLM with dual-model support."""

    def __init__(self, llm_client: OllamaClient = None, config: dict = None):
        self.config = config or {}
        endpoint = self.config.get("llm", {}).get("endpoint", "http://localhost:11434")

        # Resolve models by role from config
        models_cfg = self.config.get("models", {})
        orchestrator_model = models_cfg.get("orchestrator", {}).get("model", "qwen2.5:32b")
        creative_writer_model = models_cfg.get("creative_writer", {}).get("model", "deepseek-coder-v2:latest")

        # If a single llm_client is provided, use it for all stages (backward compat)
        # Otherwise create role-specific clients
        if llm_client is not None:
            self.orchestrator_llm = llm_client
            self.creative_writer_llm = llm_client
        else:
            self.orchestrator_llm = OllamaClient(endpoint=endpoint, model=orchestrator_model)
            self.creative_writer_llm = OllamaClient(endpoint=endpoint, model=creative_writer_model)

        self.story_gen = StoryGenerator(self.orchestrator_llm, self.config)
        self.scene_decomposer = SceneDecomposer(self.orchestrator_llm, self.config)
        self.dialogue_gen = DialogueGenerator(self.creative_writer_llm, self.config)
        self.prompt_gen = CinematicPromptGenerator(self.orchestrator_llm, self.config)
        self.validator = YAMLValidator()
        self.metrics = MetricsCollector(self.config)
        self.research_stage = ResearchStage(self.config)

    def run(self, raw_input: Dict[str, Any]) -> PipelineOutput:
        """Runs the full pipeline with LLM-powered stages."""
        logger.info("\n=== Starting Text Cinema Engine Pipeline ===")

        # 1. Validate Inputs
        try:
            input_config = validate_input(raw_input)
        except InputValidationError as e:
            raise StageError("Input Validation", str(e))

        logger.info(f"Input validated: topic='{input_config.topic}', tone={input_config.emotional_tone.value}, platform={input_config.platform.value}")

        # 1.5. Research Phase (internet research for grounding)
        research_context = None
        if self.config.get("research", {}).get("enabled", True):
            try:
                research_context = self.research_stage.research(input_config.topic)
            except Exception as e:
                logger.warning(f"Research phase failed (non-fatal): {e}")
                research_context = ResearchContext(topic=input_config.topic)

        # 2. Story Generation (LLM - orchestrator, with research context)
        story_outline = self.story_gen.generate(input_config, research_context=research_context)

        # 3. Scene Decomposition (LLM - orchestrator)
        scenes_data = self.scene_decomposer.decompose(story_outline)

        # 4. Dialogue Generation (LLM - creative_writer)
        dialogues = self.dialogue_gen.generate(scenes_data)

        # 5. Cinematic Prompt Generation (LLM - orchestrator)
        prompts = self.prompt_gen.generate(scenes_data)

        # 6. YAML Validation
        try:
            is_valid = self.validator.validate(story_outline, scenes_data, prompts)
            if not is_valid:
                raise StageError("YAML Validation", "Validation failed")
        except StageError as e:
            logger.error(f"Validation failed: {e}")
            raise

        # 7. Collect metrics
        self.metrics.record_validation_pass()
        self.metrics.record_scene_completion(scenes_data)
        self.metrics.record_emotional_arc(scenes_data)
        self.metrics.record_visual_prompt_quality(prompts)
        self.metrics.save()

        logger.info("=== Pipeline Completed Successfully ===\n")

        return PipelineOutput(
            story_yaml_content=story_outline,
            scenes_yaml_content=scenes_data,
            dialogues_yaml_content=dialogues,
            prompts_yaml_content=prompts,
            research_context=research_context.to_dict() if research_context else None,
        )


class PipelineOrchestrator:
    """Legacy orchestrator — kept for backward compatibility."""

    def __init__(self):
        self.stages = [
            'story_generation',
            'scene_decomposition', 
            'dialogue_generation',
            'cinematic_prompt_generation',
            'yaml_validation'
        ]
        
    def execute_stage(self, stage_name, data):
        logger.info(f"Executing {stage_name}...")
        return data
        
    def validate_yaml(self, yaml_data):
        """Validate generated YAML output."""
        try:
            parsed = yaml.safe_load(yaml_data)
            return True, "Valid YAML"
        except yaml.YAMLError as e:
            return False, f"Invalid YAML: {str(e)}"
            
    def generate_yaml_output(self, pipeline_result):
        """Generate YAML output from pipeline results."""
        yaml_output = {
            'story': pipeline_result['story'],
            'scenes': pipeline_result['scenes'],
            'prompts': pipeline_result['prompts']
        }
        return yaml.dump(yaml_output, default_flow_style=False)
