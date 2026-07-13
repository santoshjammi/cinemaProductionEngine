"""PromptTemplate loader — load a PromptTemplate from a YAML file.

The YAML format matches the PromptTemplate Pydantic schema. Example:

    metadata:
      id: image.cinematic.v1
      version: 1.0.0
      author: movie_os
      description: Cinematic still frame prompt for psychological cinema
      role: image
      capability: image
      tags: [cinematic, psychological, image]
      supported_models: [flux-dev, sdxl, sd3]
      recommended_temperature: 0.7
      recommended_max_tokens: 1000

    variables:
      - name: subject
        type: string
        required: true
        description: The main subject of the image
      - name: mood
        type: string
        required: true
        description: The emotional mood
      - name: lighting
        type: string
        required: false
        default: "natural low-key"
      - name: lens_mm
        type: integer
        required: false
        default: 50

    constraints:
      - rule: "Maximum 50 words in the final prompt"
        severity: must
      - rule: "Always include the subject"
        severity: must
        examples_pass: ["a man sitting alone", "a woman looking out the window"]
        examples_fail: ["a person", "someone"]

    examples:
      - description: "Warm memory scene"
        input: {subject: "a couple laughing in golden hour", mood: "warm"}
        output: "cinematic photorealism, couple laughing in golden hour, warm amber light, ..."

    negative_prompts:
      - "cartoon, anime, illustration, painting, 3d render"
      - "blurry, low quality, distorted"

    body: |
      cinematic photorealism, {{subject}}, {{mood}} mood, {{lighting}},
      35mm film grain, shallow depth of field, shot on {{lens_mm}}mm lens
"""

from __future__ import annotations

from pathlib import Path

import yaml

from movie_os.domain.prompt import PromptTemplate


def load_prompt_template(path: str | Path) -> PromptTemplate:
    """Load a PromptTemplate from a YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        A validated PromptTemplate object.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the YAML is invalid or doesn't match the schema.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    return PromptTemplate.model_validate(data)


def save_prompt_template(template: PromptTemplate, path: str | Path) -> None:
    """Save a PromptTemplate to a YAML file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.safe_dump(
            template.model_dump(mode="json"),
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )


def load_all_prompts(directory: str | Path) -> dict[str, PromptTemplate]:
    """Load all prompt templates from a directory (recursively).

    Returns a dict mapping template ID -> PromptTemplate.
    """
    directory = Path(directory)
    if not directory.exists():
        return {}

    templates: dict[str, PromptTemplate] = {}
    for yaml_file in directory.rglob("*.yaml"):
        try:
            template = load_prompt_template(yaml_file)
            templates[template.metadata.id] = template
        except Exception as e:
            # Log and continue — don't let one bad file break the loader
            import logging
            logging.warning(f"Failed to load prompt template {yaml_file}: {e}")

    return templates
