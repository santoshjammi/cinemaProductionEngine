"""Structured Scene Logic (SAI-86 / TASK-006).

Enforces the canonical per-scene dramatic chain:

    Incoming State → Character Intent → Obstacle → Trigger
    → Observable Behaviour → Partner Interpretation → Consequence
    → Scene Turn → Outgoing State

Produces a deterministic, machine-checkable SceneLogic record. The validator
rejects a scene missing any required link (fail-closed), so GENESIS never
certifies a scene without its full dramatic causality — this is what makes a
scene a real turning point rather than a static image.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional


# The canonical order of the dramatic chain.
SCENE_LOGIC_CHAIN = [
    "incoming_state",
    "character_intent",
    "obstacle",
    "trigger",
    "observable_behaviour",
    "partner_interpretation",
    "consequence",
    "scene_turn",
    "outgoing_state",
]


@dataclass
class SceneLogicLink:
    """One link in a scene's dramatic chain."""

    step: str            # name of the chain step (see SCENE_LOGIC_CHAIN)
    text: str            # the semantic content of this link
    confidence: str = "confirmed"

    def is_valid(self) -> bool:
        return bool(self.text and self.text.strip())


@dataclass
class SceneLogic:
    """The full 9-step dramatic chain for one scene."""

    scene_id: int
    links: list[SceneLogicLink] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Return the list of missing/invalid chain steps (empty = complete)."""
        self.missing.clear()
        by_step = {l.step: l for l in self.links}
        for step in SCENE_LOGIC_CHAIN:
            link = by_step.get(step)
            if link is None or not link.is_valid():
                self.missing.append(step)
        return list(self.missing)

    def is_complete(self) -> bool:
        return not self.validate()

    @staticmethod
    def from_primitives(scene_id: int, **kwargs: str) -> "SceneLogic":
        """Build a SceneLogic from the classic {step: text} keyword form."""
        links = [
            SceneLogicLink(step=step, text=str(kwargs.get(step, "")).strip(), confidence="confirmed")
            for step in SCENE_LOGIC_CHAIN
        ]
        return SceneLogic(scene_id=scene_id, links=links)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["missing"] = self.missing or (SCENE_LOGIC_CHAIN if not self.is_complete() else [])
        return d


def build_scene_logic(scene_id: int, raw: dict[str, Any] | None = None) -> SceneLogic:
    """Build a validated SceneLogic from a scene primitive dict.

    Recognizes the chain keys (snake_case) plus a few alias forms
    (e.g. 'trigger', 'obstacle'). Missing links are recorded on `.missing`.
    """
    raw = raw or {}
    kwargs = {}
    for step in SCENE_LOGIC_CHAIN:
        # Accept primary key or the "scene_{step}" prefixed alias.
        kwargs[step] = raw.get(step) or raw.get(f"scene_{step}") or raw.get(step.replace("_", ""), "")
    return SceneLogic.from_primitives(scene_id, **kwargs)


def enforce_scene_logic(scene: SceneLogic) -> list[str]:
    """Validate a SceneLogic, returning a fail-closed list of errors.

    Returns [] if the dramatic chain is complete; otherwise the missing
    steps (caller should treat any non-empty list as a blocking failure).
    """
    return scene.validate()
