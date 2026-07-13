"""Output saver — writes pipeline results to YAML files in proper directory structure."""

import os
import json
import yaml
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("pipeline.output")


def _safe_yaml_dump(data, f, **kwargs):
    """Safely dump data to YAML, truncating long strings and handling recursion errors."""
    class SafeDumper(yaml.Dumper):
        pass

    def _truncate_long_strings(dumper, data):
        """Truncate long strings to prevent YAML bloat."""
        if isinstance(data, str) and len(data) > 2000:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data[:2000] + '...[truncated]')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    SafeDumper.add_representer(str, _truncate_long_strings)

    try:
        yaml.dump(data, f, Dumper=SafeDumper, default_flow_style=False,
                  allow_unicode=True, sort_keys=kwargs.get('sort_keys', False))
    except (RecursionError, ValueError):
        logger.warning("YAML dump failed with recursion, converting to JSON-safe format")
        safe_data = json.loads(json.dumps(data, default=str))
        yaml.dump(safe_data, f, default_flow_style=False, allow_unicode=True,
                  sort_keys=kwargs.get('sort_keys', False))


class OutputSaver:
    """Saves pipeline outputs as YAML files in organized directories."""

    def __init__(self, base_dir: str = "output"):
        self.base_dir = base_dir

    def save(self, story: Dict[str, Any], scenes: List[Dict[str, Any]],
             dialogues: List[Dict[str, Any]], prompts: List[Dict[str, Any]],
             research: Dict[str, Any] = None) -> Dict[str, str]:
        """Save all pipeline outputs and return paths to generated files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = story.get("title", "untitled").lower().replace(" ", "-")[:30]

        # Create directory structure
        run_dir = os.path.join(self.base_dir, timestamp, topic_slug)
        os.makedirs(os.path.join(run_dir, "stories"), exist_ok=True)
        os.makedirs(os.path.join(run_dir, "scenes"), exist_ok=True)
        os.makedirs(os.path.join(run_dir, "prompts"), exist_ok=True)

        paths = {}

        # Save story.yaml
        story_path = os.path.join(run_dir, "stories", "story.yaml")
        with open(story_path, 'w') as f:
            _safe_yaml_dump(story, f)
        paths['story'] = story_path
        logger.info(f"Saved story to {story_path}")

        # Save scenes.yaml
        scenes_path = os.path.join(run_dir, "scenes", "scenes.yaml")
        with open(scenes_path, 'w') as f:
            _safe_yaml_dump(scenes, f)
        paths['scenes'] = scenes_path
        logger.info(f"Saved scenes to {scenes_path}")

        # Save dialogues.yaml
        dialogues_path = os.path.join(run_dir, "scenes", "dialogues.yaml")
        with open(dialogues_path, 'w') as f:
            _safe_yaml_dump(dialogues, f)
        paths['dialogues'] = dialogues_path
        logger.info(f"Saved dialogues to {dialogues_path}")

        # Save prompts.yaml
        prompts_path = os.path.join(run_dir, "prompts", "prompts.yaml")
        with open(prompts_path, 'w') as f:
            _safe_yaml_dump(prompts, f)
        paths['prompts'] = prompts_path
        logger.info(f"Saved prompts to {prompts_path}")

        # Save research.yaml (if research was performed)
        if research:
            research_path = os.path.join(run_dir, "stories", "research.yaml")
            with open(research_path, 'w') as f:
                _safe_yaml_dump(research, f)
            paths['research'] = research_path
            logger.info(f"Saved research to {research_path}")

        # Save manifest.yaml (summary of the run)
        manifest = {
            "run_id": timestamp,
            "story_title": story.get("title", "Untitled"),
            "num_scenes": len(scenes),
            "num_dialogues": len(dialogues),
            "num_prompts": len(prompts),
            "has_research": research is not None,
            "files": paths,
        }
        manifest_path = os.path.join(run_dir, "manifest.yaml")
        with open(manifest_path, 'w') as f:
            _safe_yaml_dump(manifest, f)
        paths['manifest'] = manifest_path
        logger.info(f"Saved manifest to {manifest_path}")

        return paths