"""Genesis2 Context Manager (SAI-85 / TASK-005).

Loads actual approved parent artifact content into task-specific context
capsules. Every generation task (story, beat, scene, dialogue, screenplay,
shot, image, video, audio) receives a capsule scoped to exactly what it needs
from the frozen production contract/PKP — nothing more, nothing less.

The capsule is deterministic: it is derived entirely from the contract/PKP +
the caller-supplied parent artifact, never from live LLM output.
"""

from __future__ import annotations

import json
from typing import Any, Optional

# The nine supported generation task types.
ALL_TASK_TYPES = [
    "generate_story",
    "generate_beat",
    "generate_scene",
    "generate_dialogue",
    "generate_screenplay",
    "generate_shot",
    "generate_image",
    "generate_video",
    "generate_audio",
]

# Which parent-artifact slice each task actually consumes.
_PARENT_KEY = {
    "generate_story": None,                       # whole contract
    "generate_beat": "beat_graph",
    "generate_scene": "scenes",
    "generate_dialogue": "exact_dialogue_text",
    "generate_screenplay": "scenes",
    "generate_shot": "shots",
    "generate_image": "visual_bible",
    "generate_video": "visual_bible",
    "generate_audio": "sound",
}

_TASK_CONSTRAINTS = {
    "generate_dialogue": {"max_words": 28, "new_characters_forbidden": True,
                          "reconciliation_forbidden": True, "forbidden_exposition": True},
    "generate_beat": {"chain_in_order": True},
    "generate_scene": {"scene_logic_chain_required": True},
    "generate_screenplay": {"runtime_min_s": 60, "runtime_max_s": 90},
    "generate_shot": {"one_visual_action_per_shot": True},
    "generate_image": {"medium": "image", "still": True, "consistency_anchor": True},
    "generate_video": {"medium": "video", "motion_deterministic": True},
    "generate_audio": {"medium": "audio", "honour_silence_map": True},
}


class ContextManager:
    """Deterministic, task-scoped context capsule builder.

    `contract` is the immutable production contract/PKP (a dict or JSON path).
    `parent_artifact` is the immediate upstream approved artifact for this task.
    """

    def __init__(self, contract: dict[str, Any] | str):
        if isinstance(contract, str):
            with open(contract) as f:
                self.contract: dict[str, Any] = json.load(f)
        else:
            self.contract = contract or {}

    def _truth(self) -> dict[str, Any]:
        c = self.contract
        characters = c.get("characters") or []
        if isinstance(characters, list) and characters and isinstance(characters[0], dict):
            char_ids = [ch.get("id") for ch in characters if isinstance(ch, dict)]
        elif isinstance(characters, dict):  # {MARK:{...}, SARAH:{...}}
            char_ids = list(characters.keys())
        else:
            char_ids = list(c.get("character_ids") or [])
        story = c.get("story", {}) if isinstance(c.get("story"), dict) else {}
        return {
            "production_id": c.get("production_id") or c.get("episode_id") or "",
            "contract_id": c.get("contract_id") or c.get("episode_contract_id") or "",
            "contract_version": c.get("contract_version", "1.0"),
            "immutable_constraints": {
                "characters": char_ids,
                "ending_type": c.get("ending") or story.get("ending", ""),
                "mechanism": (c.get("core_conflict", {}) or {}).get("withdrawal_mechanism")
                            or story.get("primary_mechanism", ""),
                "tone_tags": c.get("tone") or [],
            },
        }

    @staticmethod
    def _select_parent(task_type: str, parent: Any) -> Any:
        """Narrow the parent artifact to the slice this task consumes."""
        if parent is None:
            return None
        want = _PARENT_KEY.get(task_type)
        if want is None:
            return parent
        if isinstance(parent, dict):
            for key in (want, want + "s"):
                if key in parent:
                    return parent[key]
        return parent

    def get_capsule(self, task_type: str, parent_artifact: Any = None) -> dict[str, Any]:
        """Return the context capsule for a specific generation task."""
        capsule: dict[str, Any] = dict(self._truth())
        capsule["task_type"] = task_type

        if parent_artifact is not None:
            capsule["parent_memory"] = self._select_parent(task_type, parent_artifact)

        constraints = _TASK_CONSTRAINTS.get(task_type)
        if constraints:
            capsule["constraints"] = constraints

        return capsule

    def supported_tasks(self) -> list[str]:
        return list(ALL_TASK_TYPES)
