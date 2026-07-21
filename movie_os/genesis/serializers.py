"""Output serialization — saves Genesis specifications as individual files.

Each specification is saved in three formats:
- JSON: machine-readable, preserves full structure
- YAML: human-readable, good for version control diffs
- Markdown: human-readable, good for review and documentation

The output directory structure is:
  <output_dir>/
    genesis_result.json          # Full pipeline result (combined)
    specifications/
      PKP-00 — Vision Specification.json
      PKP-00 — Vision Specification.yaml
      PKP-00 — Vision Specification.md
      PKP-01 — Creative Strategy Specification.json
      ...
      CHIEF — Chief Architect Review.json
      ...
    discovery/
      intent.json
      themes.json
      ...
    reviews/
      story_review.json
      ...
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Specification
from .pkg import ProductionKnowledgeGraph


def _sanitize_filename(name: str) -> str:
    """Convert a spec name to a safe filename fragment."""
    return name.replace("/", "—").replace(":", "—").replace(" ", " ")


def _dict_to_markdown(data: dict[str, Any], title: str, level: int = 2) -> str:
    """Convert a nested dict to a Markdown document."""
    lines = [f"{'#' * level} {title}", ""]
    for key, value in data.items():
        if key == "confidence":
            continue
        if isinstance(value, dict):
            lines.append(f"### {key.replace('_', ' ').title()}")
            lines.append("")
            for k, v in value.items():
                if isinstance(v, (list, dict)):
                    lines.append(f"**{k.replace('_', ' ').title()}**:")
                    lines.append("")
                    lines.append(f"```json")
                    lines.append(json.dumps(v, indent=2, default=str))
                    lines.append("```")
                    lines.append("")
                else:
                    lines.append(f"- **{k.replace('_', ' ').title()}**: {v}")
            lines.append("")
        elif isinstance(value, list):
            lines.append(f"### {key.replace('_', ' ').title()}")
            lines.append("")
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"- {json.dumps(item, default=str)}")
                else:
                    lines.append(f"- {item}")
            lines.append("")
        else:
            lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    return "\n".join(lines)


def _dict_to_yaml(data: dict[str, Any]) -> str:
    """Convert a dict to YAML format (simple implementation, no PyYAML dependency)."""
    lines = []

    def _serialize(value: Any, indent: int = 0) -> str:
        prefix = "  " * indent
        if isinstance(value, dict):
            if not value:
                return "{}"
            items = []
            for k, v in value.items():
                items.append(f"{prefix}{k}:")
                items.append(_serialize(v, indent + 1))
            return "\n".join(items)
        elif isinstance(value, list):
            if not value:
                return "[]"
            items = []
            for item in value:
                if isinstance(item, dict):
                    items.append(f"{prefix}-")
                    for k, v in item.items():
                        items.append(f"{prefix}  {k}: {_serialize(v, 0)}")
                else:
                    items.append(f"{prefix}- {_serialize(item, 0)}")
            return "\n".join(items)
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif value is None:
            return "null"
        else:
            s = str(value)
            if ":" in s or s.startswith(("{", "[", "'", '"')):
                return f"'{s}'"
            return s

    for key, value in data.items():
        lines.append(f"{key}:")
        lines.append(_serialize(value, 1))
    return "\n".join(lines)


def save_specification_files(
    spec: Specification,
    output_dir: Path,
) -> list[Path]:
    """Save a single specification as JSON, YAML, and Markdown files.

    Returns the list of paths written.
    """
    specs_dir = output_dir / "specifications"
    specs_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{spec.spec_id} — {spec.spec_name}"
    written: list[Path] = []

    # JSON
    json_path = specs_dir / f"{base_name}.json"
    json_path.write_text(
        json.dumps(spec.content, indent=2, default=str),
        encoding="utf-8",
    )
    written.append(json_path)

    # YAML
    yaml_path = specs_dir / f"{base_name}.yaml"
    yaml_path.write_text(_dict_to_yaml(spec.content), encoding="utf-8")
    written.append(yaml_path)

    # Markdown
    md_path = specs_dir / f"{base_name}.md"
    md_content = _dict_to_markdown(spec.content, spec.spec_name)
    md_path.write_text(md_content, encoding="utf-8")
    written.append(md_path)

    return written


def save_discovery_files(
    pkg: ProductionKnowledgeGraph,
    output_dir: Path,
) -> list[Path]:
    """Save all discovery results as individual JSON files."""
    disc_dir = output_dir / "discovery"
    disc_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for key, value in pkg.get_all_discovery_results().items():
        path = disc_dir / f"{key}.json"
        path.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")
        written.append(path)

    return written


def save_review_files(
    pkg: ProductionKnowledgeGraph,
    output_dir: Path,
) -> list[Path]:
    """Save all review results as individual JSON files."""
    review_dir = output_dir / "reviews"
    review_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    review_keys = [
        "story_review",
        "character_review",
        "narrative_review",
        "psychology_review",
    ]
    for key in review_keys:
        value = pkg.get_discovery_result(key)
        if value is not None:
            path = review_dir / f"{key}.json"
            path.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")
            written.append(path)

    return written


def save_all_output(
    result: dict[str, Any],
    pkg: ProductionKnowledgeGraph,
    output_dir: str | Path,
) -> dict[str, list[Path]]:
    """Save all Genesis output to the given directory.

    Returns a dict mapping category names to lists of written file paths.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    written: dict[str, list[Path]] = {
        "result": [],
        "specifications": [],
        "discovery": [],
        "reviews": [],
    }

    # 1. Full result JSON
    result_path = out / "genesis_result.json"
    result_path.write_text(
        json.dumps(result, indent=2, default=str),
        encoding="utf-8",
    )
    written["result"].append(result_path)

    # 2. Individual specification files
    for spec in pkg.get_all_specifications().values():
        written["specifications"].extend(save_specification_files(spec, out))

    # 3. Discovery results
    written["discovery"].extend(save_discovery_files(pkg, out))

    # 4. Review results
    written["reviews"].extend(save_review_files(pkg, out))

    return written
