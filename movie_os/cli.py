"""Movie OS CLI — a thin command-line client.

The CLI is intentionally minimal in Phase 1. It supports:

  - config show         — display the loaded config
  - config validate     — validate a config file
  - config init <path>  — write a default config file
  - capabilities list   — list registered capabilities

Future commands (Phase 4+):

  - generate            — run the full pipeline
  - story factory ...   — run the story factory
  - character ...       — manage character DNA
  - render ...          — render a scene

Usage:
    python -m movie_os config show
    python -m movie_os config validate path/to/config.yaml
    python -m movie_os config init path/to/config.yaml
    python -m movie_os capabilities list
    python -m movie_os --config path/to/config.yaml <command>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = _build_parser()

    # --help and no-args both print help and exit 0
    if argv is None or "--help" in argv or "-h" in argv or len(argv) == 0:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    # If a subparser was used but no subcommand given, show help
    if hasattr(args, "command") and args.command is None:
        parser.print_help()
        return 0
    # Handle sub-commands that have their own sub-subparsers
    for sub_attr, sub_cmd in [
        ("config_command", "config"),
        ("cap_command", "capabilities"),
        ("char_command", "character"),
        ("env_command", "environment"),
        ("asset_command", "asset"),
    ]:
        if hasattr(args, sub_attr) and getattr(args, sub_attr) is None and getattr(args, "command", None) == sub_cmd:
            # Find the subparser and print its help
            for action in parser._actions:
                if hasattr(action, "choices") and sub_cmd in (action.choices or {}):
                    sub = action.choices[sub_cmd]
                    sub.print_help()
                    return 0
            parser.print_help()
            return 0

    try:
        if args.command == "config":
            return _handle_config(args)
        elif args.command == "capabilities":
            return _handle_capabilities(args)
        elif args.command == "character":
            return _handle_character(args)
        elif args.command == "environment":
            return _handle_environment(args)
        elif args.command == "asset":
            return _handle_asset(args)
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
    except SystemExit:
        raise
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="movie_os",
        description="Movie OS — Local AI Movie Operating System CLI",
    )
    parser.add_argument(
        "--config", "-c",
        default=None,
        help="Path to movie_os.yaml config file (default: config/movie_os.yaml)",
    )
    subparsers = parser.add_subparsers(dest="command")

    # config command
    config_parser = subparsers.add_parser("config", help="Config management")
    config_sub = config_parser.add_subparsers(dest="config_command")
    config_sub.add_parser("show", help="Show the loaded config")
    config_sub.add_parser("validate", help="Validate a config file")
    config_init = config_sub.add_parser("init", help="Write a default config file")
    config_init.add_argument("path", help="Path to write the default config to")

    # capabilities command
    cap_parser = subparsers.add_parser("capabilities", help="Capability management")
    cap_sub = cap_parser.add_subparsers(dest="cap_command")
    cap_sub.add_parser("list", help="List registered capabilities")

    # character command
    char_parser = subparsers.add_parser("character", help="Character management")
    char_sub = char_parser.add_subparsers(dest="char_command")
    char_sub.add_parser("list", help="List all characters")
    char_show = char_sub.add_parser("show", help="Show a character's details")
    char_show.add_argument("key", help="Character key")
    char_delete = char_sub.add_parser("delete", help="Delete a character")
    char_delete.add_argument("key", help="Character key")

    # environment command
    env_parser = subparsers.add_parser("environment", help="Environment management")
    env_sub = env_parser.add_subparsers(dest="env_command")
    env_sub.add_parser("list", help="List all environments")
    env_show = env_sub.add_parser("show", help="Show an environment's details")
    env_show.add_argument("key", help="Environment key")
    env_delete = env_sub.add_parser("delete", help="Delete an environment")
    env_delete.add_argument("key", help="Environment key")

    # asset command (Phase 9)
    asset_parser = subparsers.add_parser("asset", help="Asset store management (--db comes before subcommand)")
    asset_parser.add_argument("--db", default=".movie_os/assets.db", help="Path to the SQLite db")
    asset_sub = asset_parser.add_subparsers(dest="asset_command")
    asset_init = asset_sub.add_parser("init", help="Initialize the asset store")
    asset_list = asset_sub.add_parser("list", help="List assets")
    asset_list.add_argument("--type", "-t", default=None, help="Filter by type (image/audio/video/...)")
    asset_list.add_argument("--limit", "-n", type=int, default=20)
    asset_search = asset_sub.add_parser("search", help="Search by tag")
    asset_search.add_argument("--tag", action="append", required=True, help="Tag to search (can be repeated)")
    asset_search.add_argument("--all", action="store_true", help="Match all tags (AND) instead of any (OR)")
    asset_search.add_argument("--limit", "-n", type=int, default=20)
    asset_find = asset_sub.add_parser("find", help="Semantic search")
    asset_find.add_argument("query", help="Search query text")
    asset_find.add_argument("--k", type=int, default=5, help="Top K results")
    asset_show = asset_sub.add_parser("show", help="Show asset details")
    asset_show.add_argument("asset_id", help="Asset ID")
    asset_tag = asset_sub.add_parser("tag", help="Add tag(s) to an asset")
    asset_tag.add_argument("asset_id", help="Asset ID")
    asset_tag.add_argument("--add", action="append", required=True, help="Tag to add (can be repeated)")
    asset_rollback = asset_sub.add_parser("rollback", help="Roll back to a prior version")
    asset_rollback.add_argument("asset_id", help="Asset ID")
    asset_rollback.add_argument("version", type=int, help="Version to roll back to")
    asset_migrate = asset_sub.add_parser("migrate", help="Migrate data from existing registries")
    asset_migrate.add_argument("--from-data-layer", action="store_true", help="Migrate from CharacterRegistry/EnvironmentRegistry")

    return parser


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _handle_config(args: argparse.Namespace) -> int:
    from movie_os.config import load_config, load_config_from_dict, write_default_config, ConfigError

    if args.config_command == "show":
        config = load_config(args.config)
        print(_format_config(config))
        return 0

    elif args.config_command == "validate":
        if not args.config:
            print("Error: --config / -c is required for validate", file=sys.stderr)
            return 1
        try:
            config = load_config(args.config)
        except ConfigError as e:
            print(f"INVALID: {e}", file=sys.stderr)
            return 1
        except FileNotFoundError as e:
            print(f"NOT FOUND: {e}", file=sys.stderr)
            return 1
        print(f"VALID: {args.config}")
        print(f"  Providers: {sum(len(g.options) for g in [config.providers.image, config.providers.video, config.providers.voice, config.providers.music, config.providers.story, config.providers.translation, config.providers.research])}")
        print(f"  Capabilities enabled: {sum(1 for c in [config.capabilities.image, config.capabilities.video, config.capabilities.voice, config.capabilities.music, config.capabilities.story, config.capabilities.translation, config.capabilities.research] if c.enabled)}")
        return 0

    elif args.config_command == "init":
        write_default_config(args.path)
        print(f"Wrote default config to {args.path}")
        return 0

    else:
        print("Usage: movie_os config {show|validate|init}", file=sys.stderr)
        return 1


def _handle_capabilities(args: argparse.Namespace) -> int:
    from movie_os.config import load_config
    from movie_os.capabilities import (
        ImageCapability, VideoCapability, VoiceCapability, MusicCapability,
        StoryCapability, TranslationCapability, ResearchCapability,
    )

    if args.cap_command == "list":
        try:
            config = load_config(args.config)
        except Exception:
            config = None

        all_caps = [
            ("image", ImageCapability),
            ("video", VideoCapability),
            ("voice", VoiceCapability),
            ("music", MusicCapability),
            ("story", StoryCapability),
            ("translation", TranslationCapability),
            ("research", ResearchCapability),
        ]

        print(f"{'CAPABILITY':<15} {'VERSION':<10} {'PROVIDER (default)':<25} {'ENABLED'}")
        print("-" * 70)
        for name, cls in all_caps:
            cap = cls()
            provider_label = "(none)"
            enabled = "?"
            if config is not None:
                p = config.provider_for(name)
                if p:
                    label, _ = p
                    provider_label = label
                cap_cfg = getattr(config.capabilities, name, None)
                if cap_cfg is not None:
                    enabled = "yes" if cap_cfg.enabled else "no"
            print(f"{name:<15} {cap.version:<10} {provider_label:<25} {enabled}")
        return 0

    else:
        print("Usage: movie_os capabilities {list}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _format_value(value):
    """Format a value for display — enums as their string, etc."""
    from enum import Enum
    if isinstance(value, Enum):
        return value.value
    return value


def _format_config(config) -> str:
    """Format a MovieOSConfig for display."""
    import io
    buf = io.StringIO()
    buf.write(f"Movie OS Config (version {config.version})\n")
    buf.write("=" * 50 + "\n\n")

    buf.write("[project]\n")
    buf.write(f"  name: {config.project.name}\n")
    buf.write(f"  output_dir: {config.project.output_dir}\n")
    buf.write(f"  log_level: {_format_value(config.project.log_level)}\n")
    buf.write(f"  cache_dir: {config.project.cache_dir}\n")
    buf.write("\n")

    buf.write("[providers]\n")
    for cap_name in ["image", "video", "voice", "music", "story", "translation", "research"]:
        group = getattr(config.providers, cap_name)
        buf.write(f"  {cap_name}:\n")
        buf.write(f"    default: {group.default or '(none)'}\n")
        if group.options:
            for label, opt in group.options.items():
                buf.write(f"    {label}:\n")
                buf.write(f"      enabled: {opt.enabled}\n")
                buf.write(f"      cost_per_call_usd: {opt.cost_per_call_usd}\n")
                if opt.settings:
                    buf.write(f"      settings:\n")
                    for k, v in opt.settings.items():
                        buf.write(f"        {k}: {v}\n")
        else:
            buf.write(f"    (no providers configured)\n")
    buf.write("\n")

    buf.write("[capabilities]\n")
    for cap_name in ["image", "video", "voice", "music", "story", "translation", "research"]:
        cap_cfg = getattr(config.capabilities, cap_name)
        buf.write(f"  {cap_name}: enabled={cap_cfg.enabled} budget_usd={cap_cfg.budget_usd}\n")
    buf.write("\n")

    buf.write("[rendering]\n")
    buf.write(f"  aspect_ratio: {_format_value(config.rendering.aspect_ratio)}\n")
    buf.write(f"  resolution: {config.rendering.resolution}\n")
    buf.write(f"  quality: {_format_value(config.rendering.quality)}\n")
    buf.write(f"  output_format: {config.rendering.output_format}\n")
    buf.write(f"  video_codec: {_format_value(config.rendering.video_codec)}\n")
    buf.write(f"  audio_codec: {_format_value(config.rendering.audio_codec)}\n")
    buf.write(f"  fps: {config.rendering.fps}\n")
    buf.write("\n")

    buf.write("[pipeline]\n")
    buf.write(f"  steps: {[s.value for s in config.pipeline.steps]}\n")
    buf.write(f"  skip: {[s.value for s in config.pipeline.skip]}\n")
    buf.write(f"  auto_approve: {config.pipeline.auto_approve}\n")
    buf.write(f"  parallel: {config.pipeline.parallel}\n")

    return buf.getvalue()


# ---------------------------------------------------------------------------
# Character & Environment handlers
# ---------------------------------------------------------------------------

def _handle_character(args: argparse.Namespace) -> int:
    from movie_os.data_layer import get_character_registry

    if args.char_command == "list":
        registry = get_character_registry()
        chars = registry.list()
        if not chars:
            print("No characters in registry.")
            return 0
        print(f"{'KEY':<25} {'NAME':<30} {'AGE':<5} {'ROLE':<15} {'HERO?'}")
        print("-" * 90)
        for char in chars:
            has_hero = "yes" if registry.has_hero_image(char.key) else "no"
            print(f"{char.key:<25} {char.name:<30} {char.physical.age:<5} {char.role:<15} {has_hero}")
        print(f"\nTotal: {len(chars)} characters")
        return 0

    elif args.char_command == "show":
        registry = get_character_registry()
        char = registry.get(args.key)
        if char is None:
            print(f"Character '{args.key}' not found.", file=sys.stderr)
            return 1
        print(f"Key:        {char.key}")
        print(f"Name:       {char.name}")
        print(f"Role:       {char.role}")
        print(f"Age:        {char.physical.age}")
        print(f"Gender:     {char.physical.gender}")
        print(f"Visual:     {char.physical.visual_anchor}")
        print(f"Has hero:   {registry.has_hero_image(char.key)}")
        if registry.has_hero_image(char.key):
            print(f"Hero path:  {registry.get_hero_image_path(char.key)}")
        print(f"Tags:       {', '.join(char.tags) if char.tags else '(none)'}")
        if char.psychological.core_fear:
            print(f"Core fear:  {char.psychological.core_fear}")
        if char.psychological.personality_traits:
            print(f"Traits:     {', '.join(char.psychological.personality_traits)}")
        if char.relationships:
            print(f"Relationships:")
            for r in char.relationships:
                print(f"  - {r.relationship_type} ({r.other_character_id})")
        return 0

    elif args.char_command == "delete":
        registry = get_character_registry()
        existed = registry.delete(args.key)
        if existed:
            print(f"Deleted character '{args.key}'")
        else:
            print(f"Character '{args.key}' not found.", file=sys.stderr)
            return 1
        return 0

    else:
        print("Usage: movie_os character {list|show <key>|delete <key>}", file=sys.stderr)
        return 1


def _handle_environment(args: argparse.Namespace) -> int:
    from movie_os.data_layer import get_environment_registry

    if args.env_command == "list":
        registry = get_environment_registry()
        envs = registry.list()
        if not envs:
            print("No environments in registry.")
            return 0
        print(f"{'KEY':<25} {'NAME':<40} {'TYPE':<10} {'STYLE':<15} {'HERO?'}")
        print("-" * 100)
        for env in envs:
            has_hero = "yes" if registry.has_hero_image(env.key) else "no"
            print(f"{env.key:<25} {env.name:<40} {env.location_type:<10} {env.architectural_style:<15} {has_hero}")
        print(f"\nTotal: {len(envs)} environments")
        return 0

    elif args.env_command == "show":
        registry = get_environment_registry()
        env = registry.get(args.key)
        if env is None:
            print(f"Environment '{args.key}' not found.", file=sys.stderr)
            return 1
        print(f"Key:        {env.key}")
        print(f"Name:       {env.name}")
        print(f"Type:       {env.location_type}")
        print(f"Style:      {env.architectural_style}")
        print(f"Description: {env.description}")
        print(f"Has hero:   {registry.has_hero_image(env.key)}")
        if registry.has_hero_image(env.key):
            print(f"Hero path:  {registry.get_hero_image_path(env.key)}")
        if env.lighting.primary_source:
            print(f"Lighting:   {env.lighting.primary_source} ({env.lighting.color_temperature})")
        if env.palette.dominant:
            print(f"Palette:    dominant={env.palette.dominant}, accent={env.palette.accent}")
        if env.ambience.room_tone:
            print(f"Ambience:   {env.ambience.room_tone}")
        if env.camera_positions:
            print(f"Camera positions: {len(env.camera_positions)}")
        if env.variants:
            print(f"Variants:   {len(env.variants)} (time/weather)")
        return 0

    elif args.env_command == "delete":
        registry = get_environment_registry()
        existed = registry.delete(args.key)
        if existed:
            print(f"Deleted environment '{args.key}'")
        else:
            print(f"Environment '{args.key}' not found.", file=sys.stderr)
            return 1
        return 0

    else:
        print("Usage: movie_os environment {list|show <key>|delete <key>}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Asset store (Phase 9)
# ---------------------------------------------------------------------------

def _handle_asset(args: argparse.Namespace) -> int:
    from movie_os.asset_store import AssetStore, AssetType

    if args.asset_command == "init":
        db_path = Path(args.db)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        store = AssetStore(db_path=db_path)
        # Force the schema to be created
        _ = store.list()
        store.close()
        print(f"Initialized asset store at {db_path}")
        return 0

    if args.asset_command == "migrate":
        return _handle_asset_migrate(args)

    # All other commands need a store
    if not args.db:
        print("Error: --db is required (or set ASSET_DB env var)", file=sys.stderr)
        return 1
    store = AssetStore(db_path=args.db)
    try:
        if args.asset_command == "list":
            from movie_os.asset_store import AssetType as AT
            type_filter = AT(args.type) if args.type else None
            assets = store.list(type=type_filter, limit=args.limit)
            if not assets:
                print("No assets found.")
                return 0
            print(f"{'ID':<40} {'TYPE':<12} {'TAGS':<30} {'VERSION'}")
            print("-" * 90)
            for a in assets:
                tags = ", ".join(a.tags[:5]) if a.tags else ""
                print(f"{a.id:<40} {a.type.value:<12} {tags:<30} v{a.current_version}")
            print(f"\nTotal: {len(assets)} assets")
            return 0

        elif args.asset_command == "search":
            from movie_os.asset_store.search import tag_search
            results = tag_search(
                store.conn,
                *args.tag,
                match_all=args.all,
                limit=args.limit,
            )
            if not results:
                print("No matching assets.")
                return 0
            for a in results:
                print(f"{a.id}\t{a.type.value}\t{','.join(a.tags)}")
            return 0

        elif args.asset_command == "find":
            from movie_os.asset_store.embeddings import EmbeddingIndex
            idx = EmbeddingIndex(store)
            results = idx.search(args.query, k=args.k)
            if not results:
                print("No matching assets.")
                return 0
            for asset, distance in results:
                print(f"{asset.id}\tdistance={distance:.4f}\t{asset.prompt or asset.path.name}")
            return 0

        elif args.asset_command == "show":
            a = store.get(args.asset_id)
            print(f"ID:           {a.id}")
            print(f"Type:         {a.type.value}")
            print(f"Path:         {a.path}")
            print(f"Tags:         {', '.join(a.tags) if a.tags else '(none)'}")
            print(f"Prompt:       {a.prompt or '(none)'}")
            print(f"Model:        {a.model or '(none)'}")
            print(f"Seed:         {a.seed}")
            print(f"Current ver:  v{a.current_version}")
            print(f"Created:      {a.created_at}")
            print(f"Updated:      {a.updated_at}")
            versions = store.versions(a.id)
            print(f"All versions: {', '.join(f'v{v.version}' for v in versions)}")
            return 0

        elif args.asset_command == "tag":
            a = store.tag(args.asset_id, *args.add)
            print(f"Tagged {a.id}: {', '.join(a.tags)}")
            return 0

        elif args.asset_command == "rollback":
            a = store.rollback(args.asset_id, target_version=args.version)
            print(f"Rolled back {a.id} to v{a.current_version} → {a.path}")
            return 0

        else:
            print("Usage: movie_os asset {init|list|search|find|show|tag|rollback|migrate}", file=sys.stderr)
            return 1
    finally:
        store.close()


def _handle_asset_migrate(args: argparse.Namespace) -> int:
    """Migrate data from CharacterRegistry / EnvironmentRegistry to the asset store."""
    from movie_os.asset_store import AssetStore, AssetType
    from movie_os.data_layer import get_character_registry, get_environment_registry

    if not args.db:
        print("Error: --db is required", file=sys.stderr)
        return 1
    store = AssetStore(db_path=args.db)
    try:
        migrated = 0
        if args.from_data_layer:
            # Migrate characters
            char_reg = get_character_registry()
            for char in char_reg.list():
                # Skip if already exists with the same key
                if store.get_or_none(f"character:{char.key}") is not None:
                    continue
                # The character.yaml is the source of truth — copy it as the asset
                yaml_path = char_reg.root / char.key / "character.yaml"
                if yaml_path.exists():
                    a = store.create(
                        AssetType.CHARACTER,
                        yaml_path,
                        tags=["character", char.role] + (char.tags or []),
                        prompt=char.name,
                        metadata={"key": char.key, "name": char.name, "role": char.role},
                    )
                    # If there's a hero image, add it as a version
                    if char_reg.has_hero_image(char.key):
                        hero_path = char_reg.get_hero_image_path(char.key)
                        if hero_path and hero_path.exists():
                            store.create_version(a.id, hero_path, notes="hero image")
                    migrated += 1
            # Migrate environments
            env_reg = get_environment_registry()
            for env in env_reg.list():
                if store.get_or_none(f"environment:{env.key}") is not None:
                    continue
                yaml_path = env_reg.root / env.key / "environment.yaml"
                if yaml_path.exists():
                    a = store.create(
                        AssetType.ENVIRONMENT,
                        yaml_path,
                        tags=["environment", env.location_type, env.architectural_style],
                        prompt=env.name,
                        metadata={"key": env.key, "name": env.name},
                    )
                    if env_reg.has_hero_image(env.key):
                        hero_path = env_reg.get_hero_image_path(env.key)
                        if hero_path and hero_path.exists():
                            store.create_version(a.id, hero_path, notes="hero image")
                    migrated += 1
        print(f"Migrated {migrated} records to {args.db}")
        return 0
    finally:
        store.close()


if __name__ == "__main__":
    sys.exit(main())
