"""ShotPlanner — auto-generates Shots and Frames for a Scene.

A Scene is the dramatic beat. A Shot is a single camera setup. A Frame
is a single still image. The existing pipeline produces 1 image per
scene (effectively 1 shot, 1 frame). This planner upgrades the
hierarchy so scenes can have multiple shots/frames.

Rules:

    Shot count per scene:
        - Default: 1 shot
        - wide / extreme_wide: 2 shots (establish + push-in)
        - close-up: 1 shot (intimate, no need to cut)
        - irreversible_moment: 2 shots (the v5.2 hard cut)
        - energy >= 7 (warm): 2-3 shots
        - energy <= 2 (collapse): 1 shot (held)
        - duration > 15s: 2 shots

    Frame count per shot:
        - Default: 1 frame
        - irreversible_moment: 2 frames (hard cut)

This is a heuristic planner. In the future, a story-level LLM can
generate shot lists explicitly. For now, the planner produces
sensible defaults.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from movie_os.domain.story import Scene, Shot, Frame
from movie_os.domain.character import CharacterDNA
from movie_os.data_layer.character_registry import CharacterRegistry


logger = logging.getLogger("movie_os.domain.shot_planner")


class ShotPlanner:
    """Auto-generates Shots and Frames for a Scene.

    Usage:
        planner = ShotPlanner()
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
    """

    def __init__(self, character_registry: Optional[CharacterRegistry] = None):
        """Initialize with an optional character registry for hero image lookup.

        If provided, the planner will use character hero images as
        IPAdapter references for character consistency.
        """
        self.character_registry = character_registry

    def plan_shots(self, scene: Scene) -> list[Shot]:
        """Generate shots for a scene based on its properties.

        Returns a list of Shot objects (1-3).
        """
        shot_count = self._decide_shot_count(scene)
        shots = []

        for i in range(1, shot_count + 1):
            shot = self._build_shot(scene, i, shot_count)
            shots.append(shot)

        return shots

    def plan_frames(self, shot: Shot, scene: Scene) -> list[Frame]:
        """Generate frames for a shot.

        For most shots: 1 frame.
        For the irreversible moment: 2 frames (for the hard cut).
        """
        frame_count = 2 if scene.irreversible_moment else 1
        frames = []

        for i in range(1, frame_count + 1):
            frame = self._build_frame(shot, scene, i, frame_count)
            frames.append(frame)

        return frames

    def _decide_shot_count(self, scene: Scene) -> int:
        """Decide how many shots a scene should have.

        Order matters — earlier checks win:
          1. Irreversible moment: always 2 (the v5.2 hard cut)
          2. Low energy (≤ 2): 1 shot (held — the moment is so quiet it doesn't need a cut)
          3. High energy (≥ 7): 2-3 shots (dynamic, more camera work)
          4. Wide/extreme_wide + medium energy: 2 shots (establish + push-in)
          5. Close-up: 1 shot (intimate, no need to cut)
          6. Long duration (>15s) + medium energy: 2 shots
        """
        # Irreversible moment: always 2 (the v5.2 hard cut)
        if scene.irreversible_moment:
            return 2

        energy = scene.energy
        shot_size = scene.shot_language.get("shot_size", "medium")

        # Low energy: held, no matter the shot size
        if energy is not None and energy <= 2:
            return 1

        # High energy: more dynamic
        if energy is not None and energy >= 7:
            return 3

        # Close-ups: held (intimate moment)
        if shot_size in ("close-up", "extreme_close-up"):
            return 1

        # Wide/establishing shots at medium energy: establish + push-in
        if shot_size in ("wide", "extreme_wide"):
            return 2

        # Long duration: 2 shots
        if scene.target_duration_seconds > 15:
            return 2

        return 1

    def _build_shot(self, scene: Scene, index: int, total: int) -> Shot:
        """Build a single Shot object for a scene."""
        shot_size = scene.shot_language.get("shot_size", "medium")
        lens_mm = scene.shot_language.get("lens_mm", 50)
        base_movement = self._decide_movement(scene, index, total)

        # Generate a visual_intent per shot
        visual_intent = self._visual_intent_for_shot(scene, index, total)

        shot = Shot(
            id=uuid.uuid4(),
            number=index,
            shot_size=shot_size,
            camera_movement=base_movement,
            lens_mm=lens_mm,
            duration_seconds=scene.target_duration_seconds / total if scene.target_duration_seconds > 0 else 0,
            visual_intent=visual_intent,
            prompt_context={
                "scene_description": scene.scene_description,
                "scene_description_alt": scene.scene_description_alt,
                "mood": scene.emotional_state,
                "lighting_key": scene.shot_language.get("lighting_key", "natural_shadows"),
                "characters": scene.characters_present,
            },
        )

        return shot

    def _build_frame(self, shot: Shot, scene: Scene, index: int, total: int) -> Frame:
        """Build a single Frame for a shot."""
        # For the irreversible moment with 2 frames, use scene_description_alt for the second
        if scene.irreversible_moment and index == 2 and scene.scene_description_alt:
            description = scene.scene_description_alt
        else:
            description = shot.prompt_context.get("scene_description", "")

        # Look up character hero images for IPAdapter reference
        reference_image_ids = []
        if self.character_registry:
            for char_key in shot.prompt_context.get("characters", []):
                hero = self.character_registry.get_hero_image_path(char_key)
                if hero:
                    # Store as a UUID for now (we'll resolve at render time)
                    reference_image_ids.append(uuid.uuid4())

        return Frame(
            id=uuid.uuid4(),
            number=index,
            description=description,
            visual_cause_of_emotion=scene.visual_cause_of_emotion,
            workflow="default" if not scene.irreversible_moment else "ipadapter",
            model="sdxl" if not scene.irreversible_moment else "flux",
            reference_image_ids=reference_image_ids,
        )

    def _decide_movement(self, scene: Scene, index: int, total: int) -> str:
        """Decide the camera movement for a specific shot."""
        if scene.irreversible_moment:
            # The v5.2 hard cut — first shot holds, second shot is the cut
            return "static" if index == 1 else "push-in"

        shot_size = scene.shot_language.get("shot_size", "medium")

        if total == 1:
            # Single shot — Ken Burns effect chosen by the scene's ken_burns_effect
            return "static"  # the Ken Burns effect is applied during assembly

        if total == 2:
            # Two shots — establish then push-in
            return "static" if index == 1 else "push-in"

        if total == 3:
            # Three shots — establish, push-in, close-up
            return ["static", "push-in", "push-in"][index - 1]

        return "static"

    def _visual_intent_for_shot(self, scene: Scene, index: int, total: int) -> str:
        """Generate a visual intent description for a shot."""
        shot_size = scene.shot_language.get("shot_size", "medium")
        base = scene.scene_description

        if total == 1:
            return f"{base} (single {shot_size} shot)"

        if total == 2:
            if index == 1:
                return f"{base} (establishing {shot_size} shot, held)"
            else:
                # Second shot: closer or different angle
                closer = "close-up" if shot_size in ("wide", "extreme_wide") else "tight close-up"
                return f"{base} ({closer} shot, the cut-in)"

        if total == 3:
            if index == 1:
                return f"{base} (establishing {shot_size} shot)"
            elif index == 2:
                return f"{base} (mid-shot, hands, objects)"
            else:
                return f"{base} (close-up, the face, the final beat)"

        return base


# Convenience function
def plan_scene(scene: Scene, character_registry: Optional[CharacterRegistry] = None) -> Scene:
    """Plan shots and frames for a scene in place. Returns the same scene with shots populated.

    Usage:
        scene = MasterTimeline.scenes[0]
        scene = plan_scene(scene, character_registry)
        # scene.shots is now populated
        # scene.shots[0].frames is now populated
    """
    planner = ShotPlanner(character_registry=character_registry)
    shots = planner.plan_shots(scene)
    for shot in shots:
        shot.frames = planner.plan_frames(shot, scene)
    scene.shots = shots
    return scene
