"""Movie OS v1 — Migration Adapter.

Provides backward compatibility between legacy timeline format and new
screenplay-based production structure. Existing productions continue working
through this adapter layer.

Legacy Format (master_timeline.yaml):
    title: "..."
    synopsis: "..."
    dna: { territory, cluster, mechanism, archetype, theme }
    scenes: [ { scene_number, duration, location, ... } ]

New Format (production/):
    production.yaml — metadata
    dna.yaml — production DNA
    creative_brief.md — creative direction
    screenplay.md — structured screenplay
    outline.md — story architecture
    music_score.yaml — themes/motifs
    scene_plan.yaml — producible scenes
    shot_language.yaml — per-shot specifications
    master_timeline.yaml — references screenplay (bridge file)

Usage:
    from movie_os.migration.adapter import migrate_timeline_to_production
    production = migrate_timeline_to_legacy(timeline_path, production_dir)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from datetime import datetime

logger = logging.getLogger("movie_os.migration.adapter")


@dataclass
class MigrationResult:
    """Result of a timeline migration."""
    success: bool
    message: str
    legacy_format: dict[str, Any] | None = None
    production_dir: Path | None = None
    new_files_created: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class MigrationAdapter:
    """Bridges legacy timeline format to new screenplay-based structure.

    This adapter ensures existing productions (ew001, etc.) continue working
    while the engine migrates to the new architecture. It:
        1. Reads legacy master_timeline.yaml
        2. Maps legacy fields to new schema equivalents
        3. Generates all new production files in a target directory
        4. Creates a bridge master_timeline.yaml that references screenplay
    """

    # Mapping of legacy scene keys → new screenplay sections
    SCENE_KEY_MAP = {
        "scene_number": "scene_number",
        "duration": "duration_seconds",
        "location": "location",
        "characters": "characters",
        "emotion": "emotional_intent",
        "mood": "mood",
        "purpose": "narrative_purpose",
        "dialogue": "dialogue_beats",
        "actions": "action_lines",
        "camera": "camera_intent",
        "music": "music_intent",
    }

    # Legacy → new grammar mapping
    TERRITORY_TO_GRAMMAR = {
        "psychological_cinema": "psychological_cinema",
        "psychology": "psychological_cinema",
        "kids_story": "kids_story",
        "children": "kids_story",
        "devotional": "devotional",
        "spiritual": "devotional",
        "documentary": "documentary",
        "nonfiction": "documentary",
        "explainer": "explainer",
        "educational": "explainer",
        "shorts": "shorts",
        "vertical": "shorts",
        "narrative": "narrative_film",
        "drama": "narrative_film",
        "default": "psychological_cinema",  # safe default
    }

    def migrate_timeline_to_production(
        self,
        timeline_path: str | Path,
        production_dir: str | Path | None = None,
    ) -> MigrationResult:
        """Migrate a legacy master_timeline.yaml to new production structure.

        Args:
            timeline_path: Path to legacy master_timeline.yaml
            production_dir: Target directory for new files (defaults to timeline parent)

        Returns:
            MigrationResult with success status and created files
        """
        timeline_path = Path(timeline_path)
        if not timeline_path.exists():
            return MigrationResult(
                success=False,
                message=f"Timeline file not found: {timeline_path}",
            )

        # Load legacy timeline
        import yaml
        with open(timeline_path, 'r') as f:
            legacy_data = yaml.safe_load(f)

        # Resolve top-level key if nested
        if "master_timeline" in legacy_data:
            legacy_data = legacy_data["master_timeline"]

        # Determine production directory
        if production_dir is None:
            production_dir = timeline_path.parent / "production_new"
        production_dir = Path(production_dir)
        production_dir.mkdir(parents=True, exist_ok=True)

        # Extract legacy fields
        title = legacy_data.get("title", "") or legacy_data.get("metadata", {}).get("title", "Untitled")
        synopsis = legacy_data.get("synopsis", "") if isinstance(legacy_data, dict) else ""
        dna = legacy_data.get("dna", {}) if isinstance(legacy_data, dict) else {}
        scenes = legacy_data.get("scenes", []) if isinstance(legacy_data, dict) else []
        grammar = self._resolve_grammar(dna, legacy_data)

        # Generate all new production files
        created_files = []

        # 1. production.yaml
        prod_yaml = self._generate_production_yaml(title, dna, grammar, synopsis)
        (production_dir / "production.yaml").write_text(prod_yaml)
        created_files.append("production.yaml")

        # 2. dna.yaml
        dna_yaml = self._generate_dna_yaml(dna, title)
        (production_dir / "dna.yaml").write_text(dna_yaml)
        created_files.append("dna.yaml")

        # 3. creative_brief.md
        brief_md = self._generate_creative_brief(title, synopsis, dna, grammar)
        (production_dir / "creative_brief.md").write_text(brief_md)
        created_files.append("creative_brief.md")

        # 4. screenplay.md (from legacy scenes)
        screenplay_md = self._generate_screenplay_from_scenes(title, scenes, dna, grammar)
        (production_dir / "screenplay.md").write_text(screenplay_md)
        created_files.append("screenplay.md")

        # 5. outline.md
        outline_md = self._generate_outline_from_scenes(title, scenes, dna)
        (production_dir / "outline.md").write_text(outline_md)
        created_files.append("outline.md")

        # 6. music_score.yaml
        music_yaml = self._generate_music_score_from_scenes(title, scenes, grammar)
        (production_dir / "music_score.yaml").write_text(music_yaml)
        created_files.append("music_score.yaml")

        # 7. scene_plan.yaml
        scene_plan_yaml = self._generate_scene_plan_from_scenes(title, scenes, grammar)
        (production_dir / "scene_plan.yaml").write_text(scene_plan_yaml)
        created_files.append("scene_plan.yaml")

        # 8. Bridge master_timeline.yaml (references screenplay)
        bridge_tl = self._generate_bridge_timeline(title, grammar, production_dir)
        (production_dir / "master_timeline.yaml").write_text(bridge_tl)
        created_files.append("master_timeline.yaml (bridge)")

        # Copy legacy files for reference
        if timeline_path.exists():
            import shutil
            dest = production_dir / "legacy" / "master_timeline.yaml"
            dest.parent.mkdir(exist_ok=True)
            shutil.copy2(timeline_path, dest)
            created_files.append("legacy/master_timeline.yaml (copy)")

        warnings = []
        if not scenes:
            warnings.append("No scenes found in legacy timeline — screenplay will be minimal")
        if not dna:
            warnings.append("No DNA found — using default psychological_cinema grammar")

        return MigrationResult(
            success=True,
            message=f"Migrated '{title}' to new production structure",
            legacy_format=legacy_data,
            production_dir=production_dir,
            new_files_created=created_files,
            warnings=warnings,
        )

    def _resolve_grammar(self, dna: dict, timeline_data: dict) -> str:
        """Resolve grammar from DNA territory or explicit grammar field."""
        territory = dna.get("territory", "")
        explicit_grammar = timeline_data.get("grammar", "") or timeline_data.get("production_type", "")

        if explicit_grammar and explicit_grammar in self.TERRITORY_TO_GRAMMAR:
            return explicit_grammar

        for key, grammar in self.TERRITORY_TO_GRAMMAR.items():
            if key in territory.lower():
                return grammar

        return self.TERRITORY_TO_GRAMMAR["default"]

    def _generate_production_yaml(self, title: str, dna: dict, grammar: str, synopsis: str) -> str:
        """Generate production.yaml from legacy data."""
        now = datetime.now().strftime("%Y-%m-%d")
        return f"""# Production Metadata — {title}

## Auto-generated by MigrationAdapter

production_id: "{title.lower().replace(' ', '_')}"
title: "{title}"
version: "1.0.0"
created_by: "migration_adapter"
created_date: "{now}"
grammar: "{grammar}"
status: "in_production"

## Synopsis
{synopsis}

## Production DNA (from legacy timeline)
"""
        for key, value in dna.items():
            yaml_val = str(value).replace('\n', '\n  ')
            return f"{yaml.rstrip()}\n  {key}: {yaml_val}\n"

    def _generate_dna_yaml(self, dna: dict, title: str) -> str:
        """Generate dna.yaml from legacy DNA data."""
        yaml_str = f"# Production DNA — {title}\n\nterritory: \"{dna.get('territory', 'psychological_cinema')}\"\ncluster: \"{dna.get('cluster', '')}\"\nmechanism: \"{dna.get('mechanism', '')}\"\narchetype: \"{dna.get('archetype', '')}\"\ntheme: \"{dna.get('theme', '')}\"\npremise: \"{dna.get('premise', '')}\"\n"
        return yaml_str

    def _generate_creative_brief(self, title: str, synopsis: str, dna: dict, grammar: str) -> str:
        """Generate creative_brief.md from legacy data."""
        brief = f"""# Creative Brief — {title}

## Auto-generated by MigrationAdapter

---

## Production DNA
- **Territory:** {dna.get('territory', 'N/A')}
- **Cluster:** {dna.get('cluster', 'N/A')}
- **Mechanism:** {dna.get('mechanism', 'N/A')}
- **Archetype:** {dna.get('archetype', 'N/A')}
- **Theme:** {dna.get('theme', 'N/A')}

## Synopsis
{synopsis}

## Grammar
{grammar}

## Creative Direction
*Auto-generated from legacy timeline data. Review and refine as needed.*

---

*Generated by MigrationAdapter v1.0.0*\n"""
        return brief

    def _generate_screenplay_from_scenes(self, title: str, scenes: list[dict], dna: dict, grammar: str) -> str:
        """Generate screenplay.md from legacy scene data."""
        screenplay = f"""# {title}

## Auto-generated by MigrationAdapter from legacy timeline

---

## Production Info
- **Grammar:** {grammar}
- **Total Scenes:** {len(scenes)}
- **DNA:** {dna.get('territory', 'N/A')} / {dna.get('theme', 'N/A')}

---

"""
        for scene in scenes:
            num = scene.get("scene_number", "?")
            title_scene = scene.get("title", f"Scene {num}")
            duration = scene.get("duration_seconds", 60)
            location = scene.get("location", "Unknown")
            purpose = scene.get("purpose", "") or scene.get("narrative_purpose", "")
            emotion = scene.get("emotion", "") or scene.get("emotional_state", "")
            mood = scene.get("mood", "")
            characters = scene.get("characters", []) or scene.get("characters_present", [])
            dialogue = scene.get("dialogue", []) or scene.get("dialogues", [])
            actions = scene.get("actions", []) or scene.get("scene_description", [])
            voiceover = scene.get("voiceover", "")
            description = scene.get("scene_description", "") if not actions else ""
            shot_lang = scene.get("shot_language", {})
            ken_burns = scene.get("ken_burns_effect", "")
            music_cue = scene.get("music_cue", {}) or {}
            ambient = scene.get("ambient_cue", {}) or {}

            # Format duration as string
            if isinstance(duration, (int, float)):
                duration_str = f"{duration}s"
            else:
                duration_str = str(duration)

            # Format characters
            char_list = []
            for c in characters:
                if isinstance(c, dict):
                    char_list.append(c.get("name", c.get("key", "Unknown")))
                else:
                    char_list.append(str(c))
            chars_str = ", ".join(char_list) if char_list else "TBD"

            screenplay += f"""### SCENE {num}: {title_scene}

**Duration:** {duration_str}
**Location:** {location}
**Purpose:** {purpose}
**Emotion:** {emotion}
**Mood:** {mood}
**Characters:** {chars_str}
"""
            if description:
                screenplay += f"\n#### Scene Description\n- {description}\n"

            if voiceover:
                screenplay += f"\n#### Voiceover\n- {voiceover}\n"

            if shot_lang:
                screenplay += f"\n#### Shot Language\n"
                for key, value in shot_lang.items():
                    screenplay += f"- **{key}:** {value}\n"

            if ken_burns:
                screenplay += f"\n#### Camera Effect\n- Ken Burns: {ken_burns}\n"

            if music_cue:
                zone = music_cue.get("zone", "") or music_cue.get("theme", "")
                volume = music_cue.get("volume", "")
                screenplay += f"\n#### Music Cue\n- Zone: {zone}, Volume: {volume}\n"

            if ambient:
                beat = ambient.get("beat", "")
                desc = ambient.get("description", "")
                screenplay += f"\n#### Ambient Sound\n- Beat: {beat}, Description: {desc}\n"

            screenplay += "\n---\n\n"

        screenplay += f"\n*Generated by MigrationAdapter v1.0.0*\n"
        return screenplay

    def _generate_outline_from_scenes(self, title: str, scenes: list[dict], dna: dict) -> str:
        """Generate outline.md from legacy scene data."""
        outline = f"""# Outline — {title}

## Auto-generated by MigrationAdapter

---

## Production DNA
- **Territory:** {dna.get('territory', 'N/A')}
- **Theme:** {dna.get('theme', 'N/A')}

---

## Scene List

| # | Duration | Location | Purpose | Emotion |
|---|----------|----------|---------|---------|
"""
        for scene in scenes:
            num = scene.get("scene_number", "?")
            duration = scene.get("duration", 60)
            location = scene.get("location", "Unknown")
            purpose = scene.get("purpose", "")
            emotion = scene.get("emotion", "")
            outline += f"| {num} | {duration}s | {location} | {purpose} | {emotion} |\n"

        outline += f"\n*Generated by MigrationAdapter v1.0.0*\n"
        return outline

    def _generate_music_score_from_scenes(self, title: str, scenes: list[dict], grammar: str) -> str:
        """Generate music_score.yaml from legacy scene data."""
        score = f"""# Music Score — {title}

## Auto-generated by MigrationAdapter

---

## Themes (placeholder — refine with MusicComposerAgent)

### Theme 1: main_theme
theme_id: "main_theme"
description: "Primary theme for {grammar}"
tempo: 72
key: "C major"
mood: "warm, reflective"

---

## Scene Cues

| Scene | Duration | Music Cue | Intensity |
|-------|----------|-----------|-----------|
"""
        for scene in scenes:
            num = scene.get("scene_number", "?")
            duration = scene.get("duration", 60)
            music = scene.get("music", "auto")
            score += f"| {num} | {duration}s | {music} | auto |\n"

        score += f"\n*Generated by MigrationAdapter v1.0.0*\n"
        return score

    def _generate_scene_plan_from_scenes(self, title: str, scenes: list[dict], grammar: str) -> str:
        """Generate scene_plan.yaml from legacy scene data."""
        plan = f"""# Scene Plan — {title}

## Auto-generated by MigrationAdapter

---

## Production Info
- **Grammar:** {grammar}
- **Total Scenes:** {len(scenes)}

---

## Scene Breakdown

| # | Duration | Location | Characters | Emotion |
|---|----------|----------|------------|---------|
"""
        for scene in scenes:
            num = scene.get("scene_number", "?")
            duration = scene.get("duration", 60)
            location = scene.get("location", "Unknown")
            characters = scene.get("characters", [])
            emotion = scene.get("emotion", "")
            plan += f"| {num} | {duration}s | {location} | {', '.join(characters) if characters else 'TBD'} | {emotion} |\n"

        plan += f"\n*Generated by MigrationAdapter v1.0.0*\n"
        return plan

    def _generate_bridge_timeline(self, title: str, grammar: str, production_dir: Path) -> str:
        """Generate bridge master_timeline.yaml that references new structure."""
        timeline = f"""# Bridge Timeline — {title}

## This file bridges legacy format to new screenplay-based structure.
## The engine reads this file and maps it to the new production directory.

title: "{title}"
grammar: "{grammar}"

## References to new production files
production_dir: "production"
screenplay_path: "screenplay.md"
dna_path: "dna.yaml"
music_score_path: "music_score.yaml"
scene_plan_path: "scene_plan.yaml"

## Legacy scenes (for backward compatibility)
legacy_scenes_reference: "legacy/master_timeline.yaml"

## Status
status: "migrated"
migration_date: "{datetime.now().strftime('%Y-%m-%d')}"
migration_tool: "MigrationAdapter v1.0.0"
"""
        return timeline


# Module exports
__all__ = ["MigrationAdapter", "MigrationResult"]
