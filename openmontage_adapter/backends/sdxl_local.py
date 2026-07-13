"""SDXLLocalBackend — the default render backend for videoGen.

This wraps the existing M1 Max SDXL pipeline (`scripts/generate_from_yaml.py:SDXLGenerator`)
so it can be invoked through the render abstraction layer. It is free
(local), fast (MPS), and supports character consistency via img2img from
hero references.

Usage:

    from openmontage_adapter import SceneIntent, SDXLLocalBackend

    intent = SceneIntent(scene_id="vid01-08", ...)
    backend = SDXLLocalBackend(manifest_yaml="path/to/manifest.yaml")
    asset = backend.render(intent)
"""

from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from typing import ClassVar

from ..render_backend import BackendError, RenderBackend
from ..scene_intent import SceneAsset, SceneIntent

logger = logging.getLogger("sdxl_local_backend")


class SDXLLocalBackend(RenderBackend):
    """The local SDXL backend on M1 Max.

    Wraps `scripts/generate_from_yaml.py:SDXLGenerator`. Free, local,
    supports img2img from hero references for character consistency.

    The backend needs a manifest YAML (with model config, characters,
    visual_system, etc.). It loads the SDXLGenerator on first use.
    """

    name: ClassVar[str] = "sdxl-local"
    cost_per_scene_usd: ClassVar[float] = 0.0  # free, local
    quality_score: ClassVar[float] = 0.75
    supports_img2img: ClassVar[bool] = True
    supports_character_consistency: ClassVar[bool] = True
    max_resolution: ClassVar[tuple] = (1024, 1024)

    def __init__(
        self,
        manifest_yaml: str | Path,
        output_dir: str | Path = "output/videos",
        sdxl_generator_script: str | Path | None = None,
    ):
        """Initialize the SDXL backend.

        Args:
            manifest_yaml: Path to the video manifest YAML (with model,
                characters, visual_system, etc.). The backend passes this
                to SDXLGenerator.
            output_dir: Where to write rendered assets.
            sdxl_generator_script: Path to generate_from_yaml.py. Defaults
                to scripts/generate_from_yaml.py relative to this file.
        """
        self.manifest_yaml = Path(manifest_yaml)
        self.output_dir = Path(output_dir)
        if sdxl_generator_script is None:
            # Default: scripts/generate_from_yaml.py relative to project root
            # __file__ is openmontage_adapter/backends/sdxl_local.py
            project_root = Path(__file__).resolve().parents[2]
            sdxl_generator_script = project_root / "scripts" / "generate_from_yaml.py"
        self.sdxl_generator_script = Path(sdxl_generator_script)
        self._generator = None  # lazy load
        self._manifest = None

    def _load_generator(self):
        """Lazily load the SDXLGenerator (loads SDXL model on first use).

        This is slow (~30s for model load). We defer it until the first
        render call so backends that aren't used don't pay the cost.
        """
        if self._generator is not None:
            return self._generator

        if not self.sdxl_generator_script.exists():
            raise BackendError(
                self.name, "?",
                f"SDXLGenerator script not found at {self.sdxl_generator_script}",
            )

        # Load the manifest YAML
        import yaml
        with open(self.manifest_yaml) as f:
            manifest = yaml.safe_load(f)
        # Inject manifest path so the generator can find character hero references
        manifest["__manifest_path__"] = str(self.manifest_yaml)
        self._manifest = manifest

        # Dynamically import generate_from_yaml
        spec = importlib.util.spec_from_file_location(
            "generate_from_yaml", self.sdxl_generator_script,
        )
        if spec is None or spec.loader is None:
            raise BackendError(
                self.name, "?",
                f"Failed to load SDXLGenerator module from {self.sdxl_generator_script}",
            )
        module = importlib.util.module_from_spec(spec)
        # Ensure scripts/ is on sys.path so generate_from_yaml's imports work
        scripts_dir = str(self.sdxl_generator_script.parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        spec.loader.exec_module(module)

        self._generator = module.SDXLGenerator(self._manifest, str(self.output_dir))
        logger.info("SDXLLocalBackend: generator loaded from %s", self.sdxl_generator_script)
        return self._generator

    def can_render(self, scene_intent: SceneIntent) -> bool:
        """SDXL local can render anything — it's the default backend.

        Returns False only if the SDXLGenerator script is missing.
        """
        return self.sdxl_generator_script.exists()

    def render(self, scene_intent: SceneIntent) -> SceneAsset:
        """Render the scene using the local SDXL pipeline.

        This calls SDXLGenerator.generate_scene_image() which:
        1. Builds the SDXL prompt from the scene (with STYLE_ANCHOR + char anchors)
        2. Generates 4 candidate images (different seeds)
        3. Scores each with CLIP
        4. Selects the best
        5. Refines if score < 0.30 (max 2 rounds)
        6. Saves to scene_images/scene_NNN.png
        """
        try:
            gen = self._load_generator()
        except Exception as e:
            raise BackendError(self.name, scene_intent.scene_id, f"Failed to load SDXL generator: {e}", e)

        # Build the scene dict that SDXLGenerator expects.
        # SDXLGenerator.generate_scene_image reads scene_number, scene_description,
        # characters_present, visual_cause_of_emotion, shot_language, beat, phase,
        # ken_burns_effect. We map SceneIntent -> this dict.
        scene_dict = self._intent_to_scene_dict(scene_intent)

        try:
            result = gen.generate_scene_image(self._pipeline_id(scene_intent), scene_dict)
        except Exception as e:
            raise BackendError(self.name, scene_intent.scene_id, f"SDXL generation failed: {e}", e)

        # The result has clip_score, used_character_reference, etc.
        image_path = self.output_dir / self._pipeline_id(scene_intent) / "scene_images" / f"scene_{scene_intent.index:03d}.png"
        if not image_path.exists():
            raise BackendError(
                self.name, scene_intent.scene_id,
                f"Image not found at expected path: {image_path}",
            )

        return SceneAsset(
            scene_id=scene_intent.scene_id,
            image_path=image_path,
            duration_seconds=scene_intent.duration_seconds,
            backend=self.name,
            cost_usd=0.0,
            metadata={
                "model": "stabilityai/stable-diffusion-xl-base-1.0",
                "clip_score": result.get("clip_score", 0.0),
                "used_character_reference": result.get("used_character_reference", False),
                "refine_rounds": result.get("refine_rounds", 0),
                "img2img_strength": scene_intent.img2img_strength,
            },
        )

    def _pipeline_id(self, scene_intent: SceneIntent) -> str:
        """Derive the pipeline_id from the manifest stem.

        The SDXLGenerator writes to output_dir/<pipeline_id>/scene_images/.
        We use the manifest stem (matching the existing pipeline behavior).
        """
        return self.manifest_yaml.stem.lower().replace("_sdxl", "").replace("_revised", "")

    def _intent_to_scene_dict(self, intent: SceneIntent) -> dict:
        """Translate a SceneIntent into the scene dict SDXLGenerator expects.

        SDXLGenerator.generate_scene_image reads:
        - scene_number (1-indexed)
        - title (optional)
        - scene_description (the main prompt content)
        - visual_cause_of_emotion (body language)
        - characters_present (list of character keys)
        - shot_language (dict with shot_size, lighting_key, lens_mm, depth_of_field)
        - beat (for warmth cue override)
        - phase (for warmth cue override)
        - ken_burns_effect (not used by image gen but expected)

        The scene_description is built from the SceneIntent's
        emotional_state, visual_symbolism, micro_behaviors, and
        environmental_imperfections. This is the "semantic directing"
        translation described in grammar/visual_grammar.yaml.
        """
        # Build the scene description from semantic tokens
        desc_parts = []

        # Translate emotional_state -> visual cause
        emotion_to_visual = {
            "restrained": "hand frozen mid-reach, jaw clenched, body rigid",
            "numb": "blank stare, slack jaw, mechanical movements",
            "grief": "motionless, eyes open but unfocused, hand hovering",
            "warmth": "leaning on shoulder, eyes closed, peaceful smile",
            "shame": "head bowed, hunched shoulders, avoiding eye contact",
            "exhausted": "heavy eyes, slumped posture, delayed response",
            "yearning": "looking at something unseen, hands open on knees",
            "defensive": "arms crossed, body angled away, jaw tight",
            "resigned": "head slightly down, hands still, no expression",
            "wounded": "lip pressed, eyes wet but not crying, body still",
            "interrupted": "starts a motion, stops, returns hand to where it was",
        }
        emotion_visual = emotion_to_visual.get(intent.emotional_state, "")
        if emotion_visual:
            desc_parts.append(emotion_visual)

        # Translate visual_symbolism tokens
        symbol_translations = {
            "physical_distance": "two figures in same frame but not touching",
            "low_light": "low light, shadows, single light source",
            "downward_eye_contact": "looking at hands, not meeting eyes",
            "unfinished_gesture": "hand starts to reach, stops, returns",
            "imperfection": "wrinkled sheets, unwashed mug, dust, fingerprints",
            "parallel_suffering": "both figures alone in different rooms",
            "nighttime_honesty": "after midnight, single light source, can't sleep",
            "transition_object": "door not quite closed, phone face-down",
        }
        for sym in intent.visual_symbolism:
            translation = symbol_translations.get(sym, sym.replace("_", " "))
            desc_parts.append(translation)

        # Add micro-behaviors as concrete actions
        behavior_translations = {
            "unfinished_movements": "hand starts to reach, stops, returns",
            "hesitation": "body language catches itself mid-action",
            "redirected_attention": "looks at her, looks away before she can look back",
            "almost_touching": "two hands on the same surface, two inches of air between them",
            "almost_speaking": "lips part as if to say something, then close",
            "emotional_withdrawal": "body folds inward, makes itself smaller",
        }
        for beh in intent.micro_behaviors:
            translation = behavior_translations.get(beh, beh.replace("_", " "))
            desc_parts.append(translation)

        # Add environmental imperfections
        for imp in intent.environmental_imperfections:
            desc_parts.append(imp.replace("_", " "))

        # If we have a raw_scene with scene_description, prefer that (it's already authored)
        if intent.raw_scene.get("scene_description"):
            # Use the authored description but cap it at 65 words
            authored = intent.raw_scene["scene_description"]
            words = authored.split()
            if len(words) > 65:
                authored = " ".join(words[:65])
            # Replace the semantic translation with the authored description
            desc_parts = [authored]

        scene_description = ", ".join(desc_parts)

        # Build the scene dict
        scene_dict = {
            "scene_number": intent.index,
            "title": intent.title,
            "scene_description": scene_description,
            "visual_cause_of_emotion": intent.raw_scene.get("visual_cause_of_emotion", emotion_visual),
            "characters_present": intent.characters_present,
            "shot_language": intent.camera_language or {},
            "beat": intent.beat,
            "phase": intent.phase,
            "ken_burns_effect": intent.raw_scene.get("ken_burns_effect", "ken-burns"),
        }

        # If the raw_scene has more fields, merge them in
        for key in ("duration_hint", "irreversible_moment", "pre_moment", "post_moment",
                     "shows_duality", "silence_instead", "silence_before", "silence_after",
                     "voiceover", "micro_behaviors", "environmental_imperfections"):
            if key in intent.raw_scene:
                scene_dict[key] = intent.raw_scene[key]

        return scene_dict