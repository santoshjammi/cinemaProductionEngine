"""Master Timeline — the platform-agnostic source of truth for a story.

Why this exists (from docs/superpowers/plans/createOncePublishAnywhere.md):

    Story
    ↓
    Scene Manifest
    ↓
    Master Timeline   ← this file
    ↓
    Exports (16:9, 9:16, 1:1 — deferred for now)

The Master Timeline is the "movie." Every exporter reads it. The story
doesn't change between platforms; only the rendering does.

Schema (v1.0):

    master_timeline:
      version: "1.0"
      source:
        dna_file: stories/.../dna.yaml
        context_file: stories/.../context.md
        story_file: stories/.../story.md
      dna: { ... dna.yaml contents ... }
      metadata:
        title: ...
        id: ...
        territory: ...
        target_duration_seconds: 300
        total_scenes: 11
      characters:
        - key: husband
          name: James
          anchors: [ ... ]
      scenes:
        - scene_number: 1
          title: ...
          act: act_1_observation
          phase: hook
          beat: opening_hook
          duration_seconds: 25
          duration_hint: 20-30s
          emotional_state: tense_restraint
          energy: 3
          voiceover: "No one notices the exact night it happens."
          dialogues: []                    # empty for monologues, populated for dialogue scenes
          scene_description: "He lies in bed..."
          visual_cause_of_emotion: "Hand starts to reach..."
          shot_language: { shot_size, lighting_key, lens_mm, depth_of_field }
          characters_present: [husband, wife]
          ken_burns_effect: ken-burns
          music_cue:
            zone: act_1
            volume: 0.35
          ambient_cue:
            beat: opening_hook
            description: "Bedroom at night — fan hum, breathing"
          sfx_layers: []                   # for the irreversible moment
          silence_engine: { silence_before: 0, silence_after: 0, silence_instead: false }
          vocal_fracture: false
          irreversible_moment: false
          export_profiles: {}              # deferred — schema field exists, exporters TBD

This is a SUPERSET of the current pipeline's manifest format. The adapter
in master_timeline_to_manifest.py reads this and produces the manifest
the existing pipeline expects, so the pipeline doesn't need to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


SCHEMA_VERSION = "1.0"


@dataclass
class DialogueLine:
    """A single line of dialogue within a scene.

    For monologues, scenes have empty dialogues. For dialogue scenes,
    dialogues are the primary content and voiceover may be empty or
    a brief narrator interjection.
    """
    character: str          # character key (e.g., "husband")
    line: str               # the spoken line
    timing: str = ""        # optional timing hint (e.g., "early", "mid", "late")
    emotion: str = ""       # optional emotion tag (e.g., "tired", "defensive")


@dataclass
class MusicCue:
    """Which music zone to use for this scene and at what volume."""
    zone: str               # "act_1", "act_2", "act_3", or "none"
    volume: float = 0.3     # 0.0 = silent, 1.0 = full


@dataclass
class AmbientCue:
    """Which ambient SFX profile to use for this scene."""
    beat: str               # beat name (e.g., "opening_hook")
    description: str = ""   # human-readable description


@dataclass
class ShotLanguage:
    """Camera and lens specification for image generation."""
    shot_size: str = "medium"           # close-up, medium, wide, extreme_wide
    lighting_key: str = "natural_shadows"  # warm_low_light, natural_shadows, practical_lighting
    lens_mm: int = 50
    depth_of_field: str = "shallow"     # shallow, soft, deep


@dataclass
class SilenceEngine:
    """v5.0 silence engine flags — pre/post ambient-only gaps."""
    silence_before: float = 0.0
    silence_after: float = 0.0
    silence_instead: bool = False


@dataclass
class Scene:
    """A single scene in the Master Timeline."""
    scene_number: int
    title: str
    act: str
    phase: str
    beat: str
    duration_seconds: float = 12.0
    duration_hint: str = "20-30s"
    emotional_state: str = "neutral"
    energy: int = 5
    voiceover: str = ""
    dialogues: list[DialogueLine] = field(default_factory=list)
    scene_description: str = ""
    scene_description_alt: str = ""  # v5.2 — for irreversible_moment hard cut
    visual_cause_of_emotion: str = ""
    shot_language: ShotLanguage = field(default_factory=ShotLanguage)
    characters_present: list[str] = field(default_factory=list)
    ken_burns_effect: str = "ken-burns"
    music_cue: MusicCue = field(default_factory=lambda: MusicCue(zone="act_1"))
    ambient_cue: AmbientCue = field(default_factory=lambda: AmbientCue(beat=""))
    sfx_layers: list[str] = field(default_factory=list)
    silence_engine: SilenceEngine = field(default_factory=SilenceEngine)
    vocal_fracture: bool = False
    irreversible_moment: bool = False
    pre_moment: bool = False
    post_moment: bool = False
    shows_duality: bool = False
    export_profiles: dict[str, Any] = field(default_factory=dict)


@dataclass
class Character:
    """A character in the story."""
    key: str
    name: str
    role: str = ""
    anchors: list[str] = field(default_factory=list)
    emotional_range: list[str] = field(default_factory=list)


@dataclass
class MasterTimeline:
    """The platform-agnostic source of truth for a story."""
    version: str = SCHEMA_VERSION
    dna: dict[str, Any] = field(default_factory=dict)
    source: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    characters: list[Character] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)

    @property
    def total_duration_seconds(self) -> float:
        return sum(s.duration_seconds for s in self.scenes)

    @property
    def total_scenes(self) -> int:
        return len(self.scenes)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dict suitable for YAML dumping."""
        return {
            "master_timeline": {
                "version": self.version,
                "source": self.source,
                "dna": self.dna,
                "metadata": {
                    **self.metadata,
                    "total_scenes": self.total_scenes,
                    "total_duration_seconds": self.total_duration_seconds,
                },
                "characters": [
                    {
                        "key": c.key,
                        "name": c.name,
                        "role": c.role,
                        "anchors": c.anchors,
                        "emotional_range": c.emotional_range,
                    }
                    for c in self.characters
                ],
                "scenes": [
                    {
                        "scene_number": s.scene_number,
                        "title": s.title,
                        "act": s.act,
                        "phase": s.phase,
                        "beat": s.beat,
                        "duration_seconds": s.duration_seconds,
                        "duration_hint": s.duration_hint,
                        "emotional_state": s.emotional_state,
                        "energy": s.energy,
                        "voiceover": s.voiceover,
                        "dialogues": [
                            {
                                "character": d.character,
                                "line": d.line,
                                "timing": d.timing,
                                "emotion": d.emotion,
                            }
                            for d in s.dialogues
                        ],
                        "scene_description": s.scene_description,
                        "scene_description_alt": s.scene_description_alt,
                        "visual_cause_of_emotion": s.visual_cause_of_emotion,
                        "shot_language": {
                            "shot_size": s.shot_language.shot_size,
                            "lighting_key": s.shot_language.lighting_key,
                            "lens_mm": s.shot_language.lens_mm,
                            "depth_of_field": s.shot_language.depth_of_field,
                        },
                        "characters_present": s.characters_present,
                        "ken_burns_effect": s.ken_burns_effect,
                        "music_cue": {
                            "zone": s.music_cue.zone,
                            "volume": s.music_cue.volume,
                        },
                        "ambient_cue": {
                            "beat": s.ambient_cue.beat,
                            "description": s.ambient_cue.description,
                        },
                        "sfx_layers": s.sfx_layers,
                        "silence_engine": {
                            "silence_before": s.silence_engine.silence_before,
                            "silence_after": s.silence_engine.silence_after,
                            "silence_instead": s.silence_engine.silence_instead,
                        },
                        "vocal_fracture": s.vocal_fracture,
                        "irreversible_moment": s.irreversible_moment,
                        "pre_moment": s.pre_moment,
                        "post_moment": s.post_moment,
                        "shows_duality": s.shows_duality,
                        "export_profiles": s.export_profiles,
                    }
                    for s in self.scenes
                ],
            }
        }

    def save(self, path: str | Path) -> None:
        """Write to a YAML file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(
                self.to_dict(),
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=100,
            )

    @classmethod
    def load(cls, path: str | Path) -> "MasterTimeline":
        """Load from a YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MasterTimeline":
        """Parse from a dict (e.g., loaded from YAML or built by the Scene Structurer)."""
        # Handle both {"master_timeline": {...}} and flat dicts
        root = data.get("master_timeline", data)

        characters = [
            Character(
                key=c["key"],
                name=c.get("name", c["key"]),
                role=c.get("role", ""),
                anchors=c.get("anchors", []),
                emotional_range=c.get("emotional_range", []),
            )
            for c in root.get("characters", [])
        ]

        scenes = []
        for s in root.get("scenes", []):
            shot = s.get("shot_language", {})
            music = s.get("music_cue", {})
            ambient = s.get("ambient_cue", {})
            silence = s.get("silence_engine", {})
            dialogues = [
                DialogueLine(
                    character=d["character"],
                    line=d["line"],
                    timing=d.get("timing", ""),
                    emotion=d.get("emotion", ""),
                )
                for d in s.get("dialogues", [])
            ]
            scenes.append(
                Scene(
                    scene_number=s["scene_number"],
                    title=s.get("title", f"Scene {s['scene_number']}"),
                    act=s.get("act", "act_1_observation"),
                    phase=s.get("phase", ""),
                    beat=s.get("beat", ""),
                    duration_seconds=float(s.get("duration_seconds", 12.0)),
                    duration_hint=s.get("duration_hint", "20-30s"),
                    emotional_state=s.get("emotional_state", "neutral"),
                    energy=int(s.get("energy", 5)),
                    voiceover=s.get("voiceover", ""),
                    dialogues=dialogues,
                    scene_description=s.get("scene_description", ""),
                    scene_description_alt=s.get("scene_description_alt", ""),
                    visual_cause_of_emotion=s.get("visual_cause_of_emotion", ""),
                    shot_language=ShotLanguage(
                        shot_size=shot.get("shot_size", "medium"),
                        lighting_key=shot.get("lighting_key", "natural_shadows"),
                        lens_mm=int(shot.get("lens_mm", 50)),
                        depth_of_field=shot.get("depth_of_field", "shallow"),
                    ),
                    characters_present=s.get("characters_present", []),
                    ken_burns_effect=s.get("ken_burns_effect", "ken-burns"),
                    music_cue=MusicCue(
                        zone=music.get("zone", "act_1"),
                        volume=float(music.get("volume", 0.3)),
                    ),
                    ambient_cue=AmbientCue(
                        beat=ambient.get("beat", ""),
                        description=ambient.get("description", ""),
                    ),
                    sfx_layers=s.get("sfx_layers", []),
                    silence_engine=SilenceEngine(
                        silence_before=float(silence.get("silence_before", 0.0)),
                        silence_after=float(silence.get("silence_after", 0.0)),
                        silence_instead=bool(silence.get("silence_instead", False)),
                    ),
                    vocal_fracture=bool(s.get("vocal_fracture", False)),
                    irreversible_moment=bool(s.get("irreversible_moment", False)),
                    pre_moment=bool(s.get("pre_moment", False)),
                    post_moment=bool(s.get("post_moment", False)),
                    shows_duality=bool(s.get("shows_duality", False)),
                    export_profiles=s.get("export_profiles", {}),
                )
            )

        return cls(
            version=root.get("version", SCHEMA_VERSION),
            dna=root.get("dna", {}),
            source=root.get("source", {}),
            metadata=root.get("metadata", {}),
            characters=characters,
            scenes=scenes,
        )
