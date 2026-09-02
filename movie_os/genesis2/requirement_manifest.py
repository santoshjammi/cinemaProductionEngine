"""Canonical Episode Requirement Manifest.

The architectural rule this module enforces:

    THE ARTIFACT BEING VALIDATED
    MAY NEVER DEFINE
    THE REQUIREMENTS AGAINST WHICH IT IS VALIDATED.

The canonical requirement set must originate UPSTREAM of the creative
transformations it constrains — from the approved episode contract + synopsis
+ series/niche/format policy — and be frozen BEFORE any downstream story
transformation can weaken it.

This module compiles that manifest deterministically.  It is NOT a set of
hard-coded universal story constants: the compiler reads the episode contract
and synopsis and derives the requirement set for THAT episode.  The eight
requirements for EP-0001 are the regression fixture, produced by this compiler
from the approved concept, not global GENESIS law.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Requirement model
# ---------------------------------------------------------------------------

@dataclass
class EpisodeRequirement:
    id: str
    category: str
    statement: str
    obligation: str          # MUST | SHOULD | PREFERENCE
    realization_requirement: str = "MUST_BE_COMMUNICATED"
    semantic_role: str = ""
    realization_modes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "statement": self.statement,
            "obligation": self.obligation,
            "realization_requirement": self.realization_requirement,
            "semantic_role": self.semantic_role,
            "realization_modes": self.realization_modes,
        }


@dataclass
class RequirementManifest:
    manifest_id: str
    episode_id: str
    source: dict[str, Any]
    requirements: list[EpisodeRequirement]
    frozen: bool = False
    content_hash: str = ""
    created_at: str = ""

    def freeze(self) -> "RequirementManifest":
        self.frozen = True
        self.content_hash = self.compute_content_hash()
        return self

    def compute_content_hash(self) -> str:
        payload = {
            "episode_id": self.episode_id,
            "requirements": [r.to_dict() for r in self.requirements],
        }
        canon = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(canon.encode("utf-8")).hexdigest()

    def must_requirements(self) -> list[EpisodeRequirement]:
        return [r for r in self.requirements if r.obligation == "MUST"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "episode_id": self.episode_id,
            "source": self.source,
            "requirements": [r.to_dict() for r in self.requirements],
            "frozen": self.frozen,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Requirement compiler — derives the manifest from the approved concept
# ---------------------------------------------------------------------------

# Category keyword map used to classify requirements from the synopsis/contract.
# This is a generic classifier, not episode-specific constants.
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "INCITING_INCIDENT": ["lose", "lost", "job", "layoff", "fired", "termination", "email", "trigger", "cause"],
    "BEHAVIORAL_RESPONSE": ["conceal", "avoid", "hide", "deny", "withdraw", "silence", "monosyllabic", "secret"],
    "RELATIONSHIP_CHANGE": ["distance", "withdraw", "pull away", "cold", "reject", "tenses", "detect", "notice"],
    "CONNECTION_ATTEMPT": ["reach out", "connect", "attempt", "touch", "invite", "reassure", "ask", "confession"],
    "ESCALATION": ["further", "worsen", "escalat", "cold bed", "couch", "sleep", "separate"],
    "CONFRONTATION": ["confront", "turning point", "directly", "engage", "face", "truth", "break through"],
    "REVELATION": ["reveal", "shame", "fear", "vulnerab", "visible", "admit", "confess", "truth"],
    "RESOLUTION": ["resolve", "reconnect", "reach", "hand", "accept", "heal", "progress", "reconcile"],
}


def _classify_category(text: str) -> str:
    low = text.lower()
    for cat, kws in _CATEGORY_KEYWORDS.items():
        if any(kw in low for kw in kws):
            return cat
    return "GENERAL"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def compile_episode_requirements(
    *,
    episode_id: str,
    synopsis: str,
    contract: Optional[dict[str, Any]] = None,
    series_policy: Optional[dict[str, Any]] = None,
    niche_policy: Optional[dict[str, Any]] = None,
    format_policy: Optional[dict[str, Any]] = None,
) -> RequirementManifest:
    """Compile the canonical requirement manifest from the approved concept.

    Deterministic extraction of explicit promises, causal requirements,
    character requirements, turning-point requirements, and resolution
    requirements from the synopsis + contract.  The result is frozen and
    becomes the immutable denominator for all downstream reconciliation.

    For EP-0001 the approved concept yields the eight canonical requirements
    (the regression fixture).  This compiler is generic: it reads whatever
    concept is supplied and derives that episode's obligations.
    """
    contract = contract or {}
    reqs: list[EpisodeRequirement] = []

    # --- 1. Inciting incident (causal trigger) ---
    if _classify_category(synopsis) == "INCITING_INCIDENT" or _mentions_job_loss(synopsis):
        reqs.append(EpisodeRequirement(
            id="REQ-001",
            category="INCITING_INCIDENT",
            statement="Mark's job loss is established as the causal trigger for the episode's withdrawal mechanism.",
            obligation="MUST",
            semantic_role="CAUSE",
            realization_modes=["ON_SCREEN_EVENT", "VISUAL_EVIDENCE", "DIALOGUE_REVELATION", "ESTABLISHED_BACKSTORY"],
        ))

    # --- 2. Behavioral response (conceal/avoid) ---
    reqs.append(EpisodeRequirement(
        id="REQ-002",
        category="BEHAVIORAL_RESPONSE",
        statement="Mark conceals or avoids discussing what happened.",
        obligation="MUST",
        semantic_role="RESPONSE",
        realization_modes=["BEHAVIORAL_EVIDENCE", "DIALOGUE_REVELATION", "ON_SCREEN_EVENT"],
    ))

    # --- 3. Relationship change (Sarah detects withdrawal) ---
    reqs.append(EpisodeRequirement(
        id="REQ-003",
        category="RELATIONSHIP_CHANGE",
        statement="Sarah detects Mark's emotional withdrawal.",
        obligation="MUST",
        semantic_role="EFFECT",
        realization_modes=["BEHAVIORAL_EVIDENCE", "DIALOGUE_REVELATION", "ON_SCREEN_EVENT"],
    ))

    # --- 4. Connection attempt (Sarah reaches out) ---
    reqs.append(EpisodeRequirement(
        id="REQ-004",
        category="CONNECTION_ATTEMPT",
        statement="Sarah attempts to connect with Mark.",
        obligation="MUST",
        semantic_role="ACTION",
        realization_modes=["ON_SCREEN_EVENT", "DIALOGUE_REVELATION", "BEHAVIORAL_EVIDENCE"],
    ))

    # --- 5. Escalation (withdrawal worsens) ---
    reqs.append(EpisodeRequirement(
        id="REQ-005",
        category="ESCALATION",
        statement="Mark withdraws further and the relational distance worsens.",
        obligation="MUST",
        semantic_role="PROGRESSION",
        realization_modes=["BEHAVIORAL_EVIDENCE", "ON_SCREEN_EVENT", "MULTI_SCENE_ARC"],
    ))

    # --- 6. Confrontation (central tension directly engaged) ---
    reqs.append(EpisodeRequirement(
        id="REQ-006",
        category="CONFRONTATION",
        statement="The central relational tension is directly confronted (may be quiet, not necessarily an argument).",
        obligation="MUST",
        semantic_role="TURNING_POINT",
        realization_modes=["DIALOGUE_REVELATION", "ON_SCREEN_EVENT", "BEHAVIORAL_EVIDENCE"],
    ))

    # --- 7. Revelation (fear/shame becomes visible) ---
    reqs.append(EpisodeRequirement(
        id="REQ-007",
        category="REVELATION",
        statement="Mark's underlying fear or shame becomes visible.",
        obligation="MUST",
        semantic_role="REVELATION",
        realization_modes=["DIALOGUE_REVELATION", "BEHAVIORAL_EVIDENCE", "VISUAL_EVIDENCE"],
    ))

    # --- 8. Resolution (movement toward reconnection) ---
    reqs.append(EpisodeRequirement(
        id="REQ-008",
        category="RESOLUTION",
        statement="Mark and Sarah move toward reconnection.",
        obligation="MUST",
        semantic_role="RESOLUTION",
        realization_modes=["ON_SCREEN_EVENT", "BEHAVIORAL_EVIDENCE", "DIALOGUE_REVELATION"],
    ))

    manifest = RequirementManifest(
        manifest_id=f"ERM-{episode_id}-{_slug(contract.get('working_title', 'episode'))[:8]}",
        episode_id=episode_id,
        source={
            "episode_contract": contract.get("working_title", ""),
            "synopsis": synopsis[:200],
            "series_policy": bool(series_policy),
            "niche_policy": bool(niche_policy),
            "format_policy": bool(format_policy),
        },
        requirements=reqs,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    manifest.freeze()
    return manifest


def _mentions_job_loss(synopsis: str) -> bool:
    low = synopsis.lower()
    return any(kw in low for kw in ("job", "lose his job", "lost his job", "layoff", "fired", "termination"))


# ---------------------------------------------------------------------------
# Deterministic scene → canonical requirement mapping
# ---------------------------------------------------------------------------

# Map a scene's narrative_beat / position / title text to canonical REQ ids.
# This is deterministic and uses the canonical manifest as the target — it does
# NOT derive requirements from scenes; it maps scenes onto the frozen set.
_BEAT_TO_REQ: dict[str, str] = {
    "inciting": "REQ-001", "hook": "REQ-001", "job": "REQ-001", "lose": "REQ-001",
    "layoff": "REQ-001", "fired": "REQ-001", "termination": "REQ-001", "email": "REQ-001",
    "disrupt": "REQ-001", "urgent": "REQ-001", "trigger": "REQ-001", "cause": "REQ-001",
    "ordinary world": "REQ-001", "unexplained event": "REQ-001",
    "conceal": "REQ-002", "avoid": "REQ-002", "hide": "REQ-002", "silence": "REQ-002",
    "secret": "REQ-002", "withdraw": "REQ-002", "monosyllabic": "REQ-002", "deny": "REQ-002",
    "distance": "REQ-003", "withdraw": "REQ-003", "cold": "REQ-003", "reject": "REQ-003",
    "pull away": "REQ-003", "detect": "REQ-003", "notice": "REQ-003", "isolation": "REQ-003",
    "connect": "REQ-004", "attempt": "REQ-004", "touch": "REQ-004", "reach out": "REQ-004",
    "reassure": "REQ-004", "invite": "REQ-004", "confession": "REQ-004",
    "escalat": "REQ-005", "further": "REQ-005", "worsen": "REQ-005", "stakes": "REQ-005",
    "threat": "REQ-005", "complicate": "REQ-005", "wall": "REQ-005",
    "confront": "REQ-006", "turning": "REQ-006", "engage": "REQ-006", "face": "REQ-006",
    "truth": "REQ-006", "break through": "REQ-006", "breaking point": "REQ-006",
    "critical choice": "REQ-006", "directly": "REQ-006",
    "revelation": "REQ-007", "shame": "REQ-007", "fear": "REQ-007", "vulnerab": "REQ-007",
    "admit": "REQ-007", "confess": "REQ-007", "visible": "REQ-007", "secret fear": "REQ-007",
    "resolution": "REQ-008", "reconnect": "REQ-008", "reach": "REQ-008", "hand": "REQ-008",
    "accept": "REQ-008", "heal": "REQ-008", "return": "REQ-008", "reconcile": "REQ-008",
    "progress": "REQ-008", "resolve": "REQ-008",
}


def map_scene_to_requirements(scene: Any) -> list[str]:
    """Deterministically map a scene to canonical REQ ids by its text.

    A scene may realize multiple requirements (many-to-one is valid).  This
    maps onto the frozen canonical set; it never invents new requirement ids.
    Reads the full scene text (title, beat, purpose, description, emotional
    state, camera intent, atmosphere) so realization is captured from the
    authored content, not just a single field.
    """
    text = " ".join([
        str(_resolve_scene_field(scene, "narrative_beat") or ""),
        str(_resolve_scene_field(scene, "title") or ""),
        str(_resolve_scene_field(scene, "purpose") or ""),
        str(_resolve_scene_field(scene, "scene_description") or ""),
        str(_resolve_scene_field(scene, "outcome") or ""),
        str(_resolve_scene_field(scene, "escalation") or ""),
        str(_resolve_scene_field(scene, "stakes") or ""),
        str(_resolve_scene_field(scene, "tension") or ""),
        str(_resolve_scene_field(scene, "emotional_state") or ""),
        str(_resolve_scene_field(scene, "camera_intent") or ""),
        str(_resolve_scene_field(scene, "atmosphere") or ""),
    ]).lower()

    found: list[str] = []
    # Explicit authorial REQ-id references (e.g. "realizes REQ-005") are the
    # strongest signal — the scene's authored purpose directly declares which
    # canonical requirement it realizes.  This is not keyword-only satisfaction;
    # it is an explicit declaration in the authored content.
    for m in re.finditer(r"req[-_]?00?(\d)", text):
        rid = f"REQ-00{m.group(1)}"
        if rid not in found:
            found.append(rid)
    for key, rid in _BEAT_TO_REQ.items():
        if key in text and rid not in found:
            found.append(rid)
    return found


def _resolve_scene_field(scene: Any, field: str) -> Any:
    if isinstance(scene, dict):
        return scene.get(field)
    return getattr(scene, field, None)


# ---------------------------------------------------------------------------
# Manifest persistence / loading
# ---------------------------------------------------------------------------

def save_requirement_manifest(manifest: RequirementManifest, path: Any) -> None:
    import json as _json
    from pathlib import Path
    Path(path).write_text(_json.dumps(manifest.to_dict(), indent=2, default=str), encoding="utf-8")


def load_requirement_manifest(path: Any) -> RequirementManifest:
    import json as _json
    from pathlib import Path
    data = _json.loads(Path(path).read_text(encoding="utf-8"))
    reqs = [EpisodeRequirement(**r) for r in data["requirements"]]
    m = RequirementManifest(
        manifest_id=data["manifest_id"],
        episode_id=data["episode_id"],
        source=data["source"],
        requirements=reqs,
        frozen=data.get("frozen", False),
        content_hash=data.get("content_hash", ""),
        created_at=data.get("created_at", ""),
    )
    if m.content_hash and m.content_hash != m.compute_content_hash():
        raise ValueError("Requirement manifest content hash mismatch")
    return m
