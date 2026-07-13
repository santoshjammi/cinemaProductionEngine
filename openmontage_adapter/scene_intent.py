"""SceneIntent and SceneAsset — the render-independent scene description.

These dataclasses are the contract between the orchestrator and any render
backend. Every render backend reads a ``SceneIntent`` and produces a
``SceneAsset``. The orchestrator doesn't know or care which backend did the work.

A ``SceneIntent`` is built from a videoGen scene blueprint (see
``grammar/scene_blueprint_schema.yaml``) and contains the full semantic
description of what the scene should be.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SceneIntent:
    """The semantic description of a scene to be rendered.

    This is the render-independent description. Every backend takes
    this and produces a SceneAsset. The orchestrator routes it to
    the best available backend.

    Attributes are grouped:
    - Identity (scene_id)
    - Emotional logic (emotional_state, visual_symbolism, what_is_NOT_shown)
    - Camera language (camera_language dict)
    - Audio (soundtrack_zone, narration, subtitle_emphasis)
    - Character (character_references, character_anchors)
    - Render spec (style_anchor, negative_prompts, resolution, output_path)
    - Flags (irreversible_moment, pre_moment, post_moment, shows_duality, silence_instead)
    - Metadata (duration_seconds, beat, act, phase, energy, archetype, territory)
    """

    # ---------- IDENTITY ----------
    scene_id: str
    title: str = ""

    # ---------- EMOTIONAL LOGIC ----------
    emotional_state: str = "restrained"  # restrained, numb, grief, warmth, shame, exhausted, yearning, defensive, resigned, wounded, interrupted
    emotional_subtext: str = ""  # what the audience FEELS, even if not shown
    visual_symbolism: list[str] = field(default_factory=list)  # physical_distance, low_light, downward_eye_contact, etc.
    what_is_NOT_shown: str = ""  # the emotion that must be IMPLIED, never illustrated

    # ---------- CAMERA LANGUAGE ----------
    camera_language: dict = field(default_factory=dict)
    # Expected keys: shot_size, movement, framing, depth_of_field, lens_mm, lighting_key

    # ---------- AUDIO ----------
    soundtrack_zone: str = "act_2"  # act_1, act_2, act_3, silent
    music_volume: float = 0.25
    ambient_sfx_profile: str = "internal_collapse"
    ambient_volume: float = 0.30
    silence_before_seconds: float = 0.0
    silence_after_seconds: float = 0.0
    silence_instead: bool = False

    # ---------- NARRATION ----------
    narration_text: str = ""
    narration_prosody_register: str = "default"  # default, vulnerable, fractured, emotionally_exhausted, irreversible_moment
    vocal_fracture: bool = False
    breath_pre_pad_ms: int = 0
    break_words: list[str] = field(default_factory=list)
    emphasis_words: list[str] = field(default_factory=list)

    # ---------- SUBTITLES ----------
    subtitle_emphasis_words: list[str] = field(default_factory=list)
    subtitle_pause_after_words: list[str] = field(default_factory=list)
    subtitle_phrase_pacing: bool = True
    subtitle_max_words_per_caption: int = 6

    # ---------- CHARACTER ----------
    character_references: list[Path] = field(default_factory=list)  # hero image paths for img2img
    character_anchors: list[str] = field(default_factory=list)  # condensed visual descriptors
    characters_present: list[str] = field(default_factory=list)  # character keys

    # ---------- RENDER SPEC ----------
    style_anchor: str = "cinematic photorealism, 35mm film grain, photorealistic, cinematic still, cinematic film still, shallow depth of field"
    negative_prompts: list[str] = field(default_factory=list)
    micro_behaviors: list[str] = field(default_factory=list)
    environmental_imperfections: list[str] = field(default_factory=list)
    resolution: tuple = (1024, 576)  # (width, height)
    output_path: Path = field(default_factory=lambda: Path("scene.png"))
    inference_steps: int = 30
    guidance_scale: float = 7.5
    num_candidates: int = 4
    min_clip_score: float = 0.30
    candidate_seeds: list[int] = field(default_factory=lambda: [42, 137, 1024, 7777])
    img2img_strength: float = 0.45  # how much to follow the hero reference

    # ---------- TRANSITION ----------
    in_transition: str = "cut"  # cut, fade_black, slow_dissolve, match_cut
    out_transition: str = "cut"

    # ---------- FLAGS ----------
    irreversible_moment: bool = False
    pre_moment: bool = False
    post_moment: bool = False
    shows_duality: bool = False
    is_quiet_moment: bool = False  # for ordinary-gesture anchors

    # ---------- METADATA ----------
    duration_seconds: float = 5.0
    beat: str = "internal_collapse"
    act: str = "act_2_inner_reality"
    phase: str = "collapse"
    energy: int = 5
    archetype: str = "slow_withdrawal"
    territory: str = "emotional_withdrawal"
    index: int = 0  # 1-11, position in 3-act grid

    # ---------- RAW SCENE BLUEPRINT (for backends that need full context) ----------
    raw_scene: dict = field(default_factory=dict)

    # ---------- PIPELINE HINTS ----------
    backend_hint: str | None = None  # preferred backend (overrides orchestrator)
    cost_priority: str = "balanced"  # free, balanced, quality

    def to_dict(self) -> dict:
        """Serialize for logging/debugging (excludes Path fields)."""
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Path):
                d[k] = str(v)
            elif isinstance(v, tuple):
                d[k] = list(v)
            else:
                d[k] = v
        return d


@dataclass
class SceneAsset:
    """The rendered output of a scene.

    Every render backend produces this. The orchestrator collects them
    and the composition stage assembles them into the final video.

    Attributes:
    - scene_id: matches the SceneIntent that produced it
    - image_path: the rendered still frame (1024x576 PNG)
    - duration_seconds: how long the clip should play
    - backend: which RenderBackend produced this
    - cost_usd: actual cost incurred (0.0 for local)
    - metadata: backend-specific data (model version, seed, CLIP score, etc.)
    """

    scene_id: str
    image_path: Path
    duration_seconds: float = 5.0
    backend: str = ""
    cost_usd: float = 0.0
    metadata: dict = field(default_factory=dict)
    """Backend-specific metadata. Examples:
    - For SDXL: {"model": "stabilityai/stable-diffusion-xl-base-1.0", "seed": 42, "clip_score": 0.65, "refine_rounds": 0}
    - For Flux: {"model": "flux-1.1-pro", "seed": 12345, "cost_usd": 0.05}
    - For stock footage: {"provider": "pexels", "license": "Pexels License", "original_url": "https://..."}
    """

    def to_dict(self) -> dict:
        """Serialize for logging/debugging (excludes Path fields)."""
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Path):
                d[k] = str(v)
            else:
                d[k] = v
        return d
