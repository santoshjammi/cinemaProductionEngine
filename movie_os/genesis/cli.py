"""Genesis CLI — command-line interface for the Pre-Production Intelligence System.

Subcommands:
    run        Run the full Genesis pipeline.
    discover   Run only the discovery phase.
    spec       Run a single PKP specification by ID.
    validate   Validate a completed PKG.
    gate       Check production readiness via the completion gate.
    agents     List all known Genesis agents.
    state      Show the state of a Genesis session.

Usage:
    python -m movie_os.genesis run --synopsis ./synopsis/001.md
    python -m movie_os.genesis run --synopsis ./synopsis/001.md --mock
    python -m movie_os.genesis run --synopsis ./synopsis/001.md --output ./output/genesis/
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

from .engine import GenesisEngine
from .llm_client import LLMClient, MockLLMClient
from .models import ConfidenceLevel
from .pkg import ProductionKnowledgeGraph
from .session import SessionManager


logger = logging.getLogger("movie_os.genesis.cli")


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _read_synopsis_file(path: str) -> tuple[str, dict[str, Any]]:
    """Read a synopsis file in the structured format.

    Supported sections (all optional except SYNOPSIS):
        STORY <id> — <title>
        TITLE
        CORE_FEAR
        SYNOPSIS
        KEY_CHARACTERS
        EMOTIONAL_ARC
        ENDING
        OPTIONAL CONSTRAINTS

    Returns (synopsis_text, constraints_dict).
    The synopsis_text includes all structured fields as a JSON preamble
    so the Genesis agents receive the full context.
    """
    content = Path(path).read_text(encoding="utf-8")

    # Split on OPTIONAL CONSTRAINTS if present
    constraints: dict[str, Any] = {}
    if "OPTIONAL CONSTRAINTS" in content.upper():
        idx = content.upper().index("OPTIONAL CONSTRAINTS")
        body = content[:idx]
        constraints_part = content[idx + len("OPTIONAL CONSTRAINTS"):]
        for line in constraints_part.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()
                if value.lower() in ("true", "false"):
                    constraints[key] = value.lower() == "true"
                elif value.replace("-", "").replace(".", "").isdigit():
                    constraints[key] = float(value) if "." in value else int(value)
                else:
                    constraints[key] = value
    else:
        body = content

    # Parse structured sections
    sections = _parse_structured_synopsis(body)

    # Build the synopsis text that Genesis agents receive
    # Include all structured fields as a preamble
    parts = []
    if sections.get("title"):
        parts.append(f"TITLE: {sections['title']}")
    if sections.get("core_fear"):
        parts.append(f"CORE FEAR: {sections['core_fear']}")
    if sections.get("key_characters"):
        parts.append(f"CHARACTERS: {sections['key_characters']}")
    if sections.get("emotional_arc"):
        parts.append(f"EMOTIONAL ARC: {sections['emotional_arc']}")
    if sections.get("ending"):
        parts.append(f"ENDING: {sections['ending']}")
    if sections.get("synopsis"):
        parts.append("")
        parts.append(sections["synopsis"])

    synopsis_text = "\n".join(parts) if parts else body.strip()

    # Merge parsed fields into constraints for downstream use
    for key in ("title", "core_fear", "key_characters", "emotional_arc", "ending"):
        if sections.get(key):
            constraints[key] = sections[key]

    return synopsis_text.strip(), constraints


def _parse_structured_synopsis(text: str) -> dict[str, str]:
    """Parse a structured synopsis into its component sections.

    Recognized section headers (case-insensitive):
        STORY <id> — <title>
        TITLE
        CORE_FEAR
        SYNOPSIS
        KEY_CHARACTERS
        EMOTIONAL_ARC
        ENDING
    """
    import re

    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    # Ordered list of section headers to detect
    header_patterns = [
        (r"^STORY\s+\S+\s*[—\-]\s*(.+)$", "title"),       # STORY 01 — Title
        (r"^TITLE\s*$", "title_header"),
        (r"^CORE_FEAR\s*$", "core_fear"),
        (r"^SYNOPSIS\s*$", "synopsis"),
        (r"^KEY_CHARACTERS\s*$", "key_characters"),
        (r"^EMOTIONAL_ARC\s*$", "emotional_arc"),
        (r"^ENDING\s*$", "ending"),
    ]

    def _flush():
        if current_key and current_lines:
            val = "\n".join(current_lines).strip()
            if val:
                sections[current_key] = val

    for line in text.split("\n"):
        stripped = line.strip()

        # Check for STORY <id> — <title> pattern
        m = re.match(r"^STORY\s+\S+\s*[—\-]\s*(.+)$", stripped, re.IGNORECASE)
        if m:
            _flush()
            sections["title"] = m.group(1).strip()
            current_key = None
            current_lines = []
            continue

        # Check for other section headers
        matched = False
        for pattern, key in header_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                _flush()
                current_key = key
                current_lines = []
                matched = True
                break

        if matched:
            continue

        # Accumulate content for current section
        if current_key:
            current_lines.append(line)

    _flush()

    return sections


def _read_json(path: Optional[str]) -> dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _check_llm(url: str) -> bool:
    """Check if the LLM server is reachable. Returns True if available."""
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(f"{url}/v1/models", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except (urllib.error.URLError, ConnectionError, OSError):
        return False


def _build_llm(args: argparse.Namespace) -> LLMClient | MockLLMClient:
    if getattr(args, "mock", False):
        from .mock_data import build_rich_mock_llm
        return build_rich_mock_llm()

    from .llm_factory import create_client

    return create_client(
        config_path=getattr(args, "llm_config", None),
        backend=getattr(args, "backend", None),
        model=getattr(args, "model", None),
        llm_url=getattr(args, "llm_url", None),
    )


def _format_result(result: dict[str, Any], output_dir: Optional[str] = None) -> None:
    """Print the Genesis result in a clean, human-readable format.

    If output_dir is specified, also save the full result as JSON and
    individual specification files.
    """

    def _get(obj, key, default=None):
        """Get a value from either a dict or a Pydantic model."""
        if hasattr(obj, "model_dump"):
            return obj.model_dump().get(key, default)
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default) if hasattr(obj, key) else default

    # Summary header
    print()
    print("=" * 60)
    print("  GENESIS — Pre-Production Intelligence System")
    print("=" * 60)
    print()

    # Session info
    print(f"  Session:     {str(result.get('session_id', 'N/A'))[:12]}...")
    print(f"  Completeness: {result.get('overall_completeness', 0):.0%}")
    print()

    # Discovery results
    discovery = result.get("discovery_results", [])
    print(f"  Discovery Agents ({len(discovery)}):")
    for r in discovery:
        status = _get(r, "status", "unknown")
        status_icon = "✅" if status == "success" else "❌"
        name = _get(r, "agent_name", "?")
        conf = _get(r, "confidence", "unknown")
        print(f"    {status_icon} {name} (confidence: {conf})")
    print()

    # PKP results
    pkp = result.get("pkp_results", [])
    print(f"  PKP Specifications ({len(pkp)}):")
    for r in pkp:
        status = _get(r, "status", "unknown")
        if status == "success":
            status_icon = "✅"
        elif status == "skipped":
            status_icon = "⏭️"
        else:
            status_icon = "❌"
        spec_id = _get(r, "spec_id", "?")
        name = _get(r, "agent_name", "?")
        conf = _get(r, "confidence", "unknown")
        print(f"    {status_icon} {spec_id} — {name} (confidence: {conf})")
    print()

    # Review results
    reviews = result.get("review_results", [])
    print(f"  Review Agents ({len(reviews)}):")
    for r in reviews:
        status = _get(r, "status", "unknown")
        status_icon = "✅" if status == "success" else "❌"
        name = _get(r, "agent_name", "?")
        print(f"    {status_icon} {name}")
    print()

    # Gate result
    gate = result.get("gate_result", {})
    gate_passed = gate.get("passed", False)
    gate_icon = "✅ PASSED" if gate_passed else "❌ FAILED"
    print(f"  Completion Gate: {gate_icon}")
    if not gate_passed:
        blockers = gate.get("blockers", [])
        print(f"  Blockers ({len(blockers)}):")
        for b in blockers:
            print(f"    ⛔ {b}")
    print()

    # Specifications summary
    specs = result.get("specifications", {})
    if specs:
        print(f"  Specifications Produced ({len(specs)}):")
        for sid, info in sorted(specs.items()):
            if sid == "_pkg":
                continue
            name = info.get("spec_name", "?") if isinstance(info, dict) else str(info)
            conf = info.get("confidence", "?") if isinstance(info, dict) else "?"
            val = info.get("validation_status", "?") if isinstance(info, dict) else "?"
            print(f"    {sid}: {name} (confidence: {conf}, validation: {val})")
    else:
        print("  Specifications Produced: 0")
    print()

    # Save to output directory if specified
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        # Save full result as JSON
        (out / "genesis_result.json").write_text(
            json.dumps(result, indent=2, default=str), encoding="utf-8"
        )

        # Save individual specification, discovery, and review files
        from .serializers import save_all_output
        written = save_all_output(result, result.get("_pkg"), out)
        total = sum(len(v) for v in written.values())
        print(f"  Output saved to: {out} ({total} files)")
    print("=" * 60)


# ----------------------------------------------------------------------
# Subcommand handlers
# ----------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> int:
    synopsis, file_constraints = _read_synopsis_file(args.synopsis)
    json_constraints = _read_json(args.constraints)
    constraints = {**file_constraints, **json_constraints}

    llm = _build_llm(args)
    output_dir = getattr(args, "output", None)

    print(f"\n🎬 Genesis Engine — Starting pre-production pipeline...", file=sys.stderr)
    print(f"   Synopsis: {args.synopsis}", file=sys.stderr)
    if constraints:
        print(f"   Constraints: {constraints}", file=sys.stderr)
    print(file=sys.stderr)

    engine = GenesisEngine(llm=llm, db_path=args.db or ":memory:")
    result = engine.run(synopsis=synopsis, constraints=constraints)

    _format_result(result, output_dir)
    return 0 if result.get("gate_result", {}).get("passed") else 1


def cmd_discover(args: argparse.Namespace) -> int:
    import asyncio

    synopsis, file_constraints = _read_synopsis_file(args.synopsis)
    json_constraints = _read_json(args.constraints)
    constraints = {**file_constraints, **json_constraints}

    llm = _build_llm(args)

    print(f"\n🔍 Genesis Discovery — Running 7 discovery agents...", file=sys.stderr)

    engine = GenesisEngine(llm=llm, db_path=args.db or ":memory:")
    pkg = ProductionKnowledgeGraph(args.db or ":memory:")
    pkg.synopsis = synopsis
    pkg.constraints = constraints
    pkg.save_state()

    results = asyncio.run(engine._run_discovery(pkg))

    print(f"\n{'=' * 60}")
    print(f"  Discovery Results ({len(results)} agents)")
    print(f"{'=' * 60}")
    for r in results:
        status_icon = "✅" if r.status == "success" else "❌"
        print(f"  {status_icon} {r.agent_name} (confidence: {r.confidence.value})")
        if r.errors:
            for e in r.errors:
                print(f"      Error: {e}")
    print(f"{'=' * 60}")
    return 0


def cmd_spec(args: argparse.Namespace) -> int:
    import asyncio

    spec_id = args.id.upper()
    if not spec_id.startswith("PKP"):
        spec_id = f"PKP-{spec_id.zfill(2)}"

    synopsis, file_constraints = _read_synopsis_file(args.synopsis)
    json_constraints = _read_json(args.constraints)
    constraints = {**file_constraints, **json_constraints}

    llm = _build_llm(args)

    print(f"\n📝 Genesis — Running single spec: {spec_id}", file=sys.stderr)

    engine = GenesisEngine(llm=llm, db_path=args.db or ":memory:")
    pkg = ProductionKnowledgeGraph(args.db or ":memory:")
    pkg.synopsis = synopsis
    pkg.constraints = constraints
    pkg.save_state()

    agent = _instantiate_pkp_agent(spec_id, llm)
    if agent is None:
        print(f"❌ Unknown spec id: {spec_id}", file=sys.stderr)
        return 2

    result = asyncio.run(agent.run(pkg))

    print(f"\n{'=' * 60}")
    print(f"  {spec_id} — {agent.spec_name}")
    print(f"{'=' * 60}")
    print(f"  Status:     {result.status}")
    print(f"  Confidence: {result.confidence.value}")
    if result.errors:
        print(f"  Errors:")
        for e in result.errors:
            print(f"    ⛔ {e}")
    if result.output:
        print(f"  Output:")
        print(json.dumps(result.output, indent=2, default=str))
    print(f"{'=' * 60}")
    return 0 if result.status == "success" else 1


def cmd_validate(args: argparse.Namespace) -> int:
    pkg = ProductionKnowledgeGraph(args.pkg)
    specs = pkg.get_all_specifications()
    issues: list[dict[str, Any]] = []
    for sid, spec in specs.items():
        if spec.validation_status == "failed":
            issues.append({"spec_id": sid, "errors": spec.validation_errors})
        for dep_id in spec.dependencies:
            if not pkg.has_specification(dep_id):
                issues.append({"spec_id": sid, "missing_dependency": dep_id})

    print(f"\n{'=' * 60}")
    print(f"  PKG Validation")
    print(f"{'=' * 60}")
    print(f"  Specifications: {len(specs)}")
    print(f"  Issues: {len(issues)}")
    if issues:
        print(f"\n  ❌ Validation issues:")
        for i in issues:
            print(f"    {i}")
    else:
        print(f"\n  ✅ All specifications valid")
    print(f"{'=' * 60}")
    return 0 if not issues else 1


def cmd_gate(args: argparse.Namespace) -> int:
    from .completion_gate import PreProductionCompletionGate

    pkg = ProductionKnowledgeGraph(args.pkg)
    gate = PreProductionCompletionGate()
    result = gate.check(pkg)

    print(f"\n{'=' * 60}")
    print(f"  Pre-Production Completion Gate")
    print(f"{'=' * 60}")
    print(f"  Result: {'✅ PASSED' if result.passed else '❌ FAILED'}")
    print()
    for c in result.criteria:
        icon = "✅" if c["passed"] else "❌"
        print(f"  {icon} {c['name']}: {c['detail']}")
    if result.blockers:
        print(f"\n  ⛔ Blockers ({len(result.blockers)}):")
        for b in result.blockers:
            print(f"    {b}")
    print(f"{'=' * 60}")
    return 0 if result.passed else 1


def cmd_agents(args: argparse.Namespace) -> int:
    agents = _list_all_agents()

    print(f"\n{'=' * 60}")
    print(f"  Genesis Agents ({len(agents)})")
    print(f"{'=' * 60}")
    print()

    # Group by kind
    by_kind: dict[str, list] = {}
    for a in agents:
        kind = a.get("kind", "unknown")
        by_kind.setdefault(kind, []).append(a)

    kind_labels = {
        "discovery": "Discovery Agents (7)",
        "pkp": "PKP Domain Agents (19)",
        "reviewer": "Review Agents (4)",
        "chief": "Chief Architect (1)",
    }

    for kind in ["discovery", "pkp", "reviewer", "chief"]:
        items = by_kind.get(kind, [])
        if not items:
            continue
        print(f"  {kind_labels.get(kind, kind)}:")
        for a in items:
            name = a.get("name", "?")
            spec_id = a.get("spec_id", a.get("review_key", a.get("analysis_key", "")))
            spec_name = a.get("spec_name", "")
            print(f"    {spec_id:<14} {name:<30} {spec_name}")
        print()

    print(f"  Total: {len(agents)} agents")
    print(f"{'=' * 60}")
    return 0


def cmd_state(args: argparse.Namespace) -> int:
    sm = SessionManager(args.db or ":memory:")
    session = sm.get_session(args.session)
    if session is None:
        print(f"❌ Session not found: {args.session}", file=sys.stderr)
        return 1

    print(f"\n{'=' * 60}")
    print(f"  Session State: {args.session[:12]}...")
    print(f"{'=' * 60}")
    print(f"  Stage:       {session['stage']}")
    print(f"  Synopsis:    {session['synopsis'][:100]}...")
    print(f"  Constraints: {session['constraints']}")
    print(f"  Created:     {session['created_at']}")
    print(f"  Updated:     {session['updated_at']}")
    print(f"{'=' * 60}")
    return 0


# ----------------------------------------------------------------------
# Agent registry
# ----------------------------------------------------------------------

def _instantiate_pkp_agent(spec_id: str, llm: LLMClient | MockLLMClient) -> Optional[Any]:
    """Instantiate a PKP agent by spec id. Returns None if unknown."""
    from .pkp_agents.vision_agent import VisionAgent
    from .pkp_agents.creative_strategy_agent import CreativeStrategyAgent
    from .pkp_agents.project_agent import ProjectAgent
    from .pkp_agents.research_agent import ResearchAgent
    from .pkp_agents.story_agent import StoryAgent
    from .pkp_agents.world_agent import WorldAgent
    from .pkp_agents.character_agent import CharacterAgent
    from .pkp_agents.relationship_agent import RelationshipAgent
    from .pkp_agents.psychology_agent import PsychologyAgent
    from .pkp_agents.narrative_agent import NarrativeAgent
    from .pkp_agents.directorial_agent import DirectorialAgent
    from .pkp_agents.production_design_agent import ProductionDesignAgent
    from .pkp_agents.audio_intent_agent import AudioIntentAgent
    from .pkp_agents.editing_language_agent import EditingLanguageAgent
    from .pkp_agents.animation_intent_agent import AnimationIntentAgent
    from .pkp_agents.blueprint_agent import BlueprintAgent
    from .pkp_agents.distribution_agent import DistributionAgent
    from .pkp_agents.quality_agent import QualityAgent
    from .pkp_agents.knowledge_graph_agent import KnowledgeGraphAgent

    registry = {
        "PKP-00": VisionAgent,
        "PKP-01": CreativeStrategyAgent,
        "PKP-02": ProjectAgent,
        "PKP-03": ResearchAgent,
        "PKP-04": StoryAgent,
        "PKP-05": WorldAgent,
        "PKP-06": CharacterAgent,
        "PKP-07": RelationshipAgent,
        "PKP-08": PsychologyAgent,
        "PKP-09": NarrativeAgent,
        "PKP-10": DirectorialAgent,
        "PKP-11": ProductionDesignAgent,
        "PKP-12": AudioIntentAgent,
        "PKP-13": EditingLanguageAgent,
        "PKP-14": AnimationIntentAgent,
        "PKP-15": BlueprintAgent,
        "PKP-16": DistributionAgent,
        "PKP-17": QualityAgent,
        "PKP-18": KnowledgeGraphAgent,
    }
    cls = registry.get(spec_id)
    if cls is None:
        return None
    return cls(llm)


def _list_all_agents() -> list[dict[str, Any]]:
    """Return metadata for all known Genesis agents."""
    from .chief_architect import ChiefArchitect
    from .reviewers.story_reviewer import StoryReviewer
    from .reviewers.character_reviewer import CharacterReviewer
    from .reviewers.narrative_reviewer import NarrativeReviewer
    from .reviewers.psychology_reviewer import PsychologyReviewer
    from .discovery.intent_analyst import IntentAnalyst
    from .discovery.theme_analyst import ThemeAnalyst
    from .discovery.emotion_analyst import EmotionAnalyst
    from .discovery.conflict_analyst import ConflictAnalyst
    from .discovery.audience_analyst import AudienceAnalyst
    from .discovery.gap_analyst import GapAnalyst
    from .discovery.question_planner import QuestionPlanner

    mock = MockLLMClient()
    agents: list[dict[str, Any]] = []

    # Discovery agents (run first)
    for cls in (
        IntentAnalyst, ThemeAnalyst, EmotionAnalyst, ConflictAnalyst,
        AudienceAnalyst, GapAnalyst, QuestionPlanner,
    ):
        agent = cls(mock)
        agents.append({
            "name": agent.name,
            "analysis_key": agent.analysis_key,
            "kind": "discovery",
        })

    # PKP agents
    for spec_id in [
        "PKP-00", "PKP-01", "PKP-02", "PKP-03", "PKP-04", "PKP-05",
        "PKP-06", "PKP-07", "PKP-08", "PKP-09", "PKP-10", "PKP-11",
        "PKP-12", "PKP-13", "PKP-14", "PKP-15", "PKP-16", "PKP-17",
        "PKP-18",
    ]:
        agent = _instantiate_pkp_agent(spec_id, mock)
        if agent is not None:
            agents.append({
                "name": agent.name,
                "spec_id": agent.spec_id,
                "spec_name": agent.spec_name,
                "phase": agent.phase,
                "dependencies": agent.dependencies,
                "kind": "pkp",
            })

    # Reviewers
    for cls in (StoryReviewer, CharacterReviewer, NarrativeReviewer, PsychologyReviewer):
        agent = cls(mock)
        agents.append({
            "name": agent.name,
            "review_key": agent.review_key,
            "specs_to_review": agent.specs_to_review,
            "kind": "reviewer",
        })

    # Chief Architect
    chief = ChiefArchitect(mock)
    agents.append({
        "name": chief.name,
        "spec_id": chief.spec_id,
        "spec_name": chief.spec_name,
        "phase": chief.phase,
        "dependencies": chief.dependencies,
        "kind": "chief",
    })

    return agents


# ----------------------------------------------------------------------
# Argument parser
# ----------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="genesis",
        description="Genesis — Pre-Production Intelligence System",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--db", default=None, help="Path to PKG SQLite database")
    parser.add_argument("--mock", action="store_true", help="Use MockLLMClient (no real LLM calls)")
    parser.add_argument("--backend", default=None, choices=["auto", "ollama", "lmstudio", "hf"],
                        help="LLM backend (default: auto-detect)")
    parser.add_argument("--llm-url", default=None, help="LLM API base URL")
    parser.add_argument("--llm-key", default=None, help="LLM API key")
    parser.add_argument("--model", default=None, help="LLM model name")
    parser.add_argument("--llm-config", default=None, help="Path to LLM config YAML file")

    sub = parser.add_subparsers(dest="command", required=True)

    # run
    p_run = sub.add_parser("run", help="Run the full Genesis pipeline")
    p_run.add_argument("--synopsis", required=True, help="Path to synopsis text file")
    p_run.add_argument("--constraints", default=None, help="Path to constraints JSON file")
    p_run.add_argument("--output", "-o", default=None, help="Output directory for results")
    p_run.set_defaults(func=cmd_run)

    # discover
    p_disc = sub.add_parser("discover", help="Run only the discovery phase")
    p_disc.add_argument("--synopsis", required=True, help="Path to synopsis text file")
    p_disc.add_argument("--constraints", default=None, help="Path to constraints JSON file")
    p_disc.set_defaults(func=cmd_discover)

    # spec
    p_spec = sub.add_parser("spec", help="Run a single PKP specification")
    p_spec.add_argument("--id", required=True, help="Spec ID, e.g. 06 or PKP-06")
    p_spec.add_argument("--synopsis", required=True, help="Path to synopsis text file")
    p_spec.add_argument("--constraints", default=None, help="Path to constraints JSON file")
    p_spec.set_defaults(func=cmd_spec)

    # validate
    p_val = sub.add_parser("validate", help="Validate a completed PKG")
    p_val.add_argument("--pkg", required=True, help="Path to PKG SQLite database")
    p_val.set_defaults(func=cmd_validate)

    # gate
    p_gate = sub.add_parser("gate", help="Check production readiness")
    p_gate.add_argument("--pkg", required=True, help="Path to PKG SQLite database")
    p_gate.set_defaults(func=cmd_gate)

    # agents
    p_agents = sub.add_parser("agents", help="List all agents")
    p_agents_sub = p_agents.add_subparsers(dest="subcommand")
    p_agents_list = p_agents_sub.add_parser("list", help="List all agents")
    p_agents_list.set_defaults(func=cmd_agents)
    p_agents.set_defaults(func=cmd_agents)

    # state
    p_state = sub.add_parser("state", help="Show PKG state for a session")
    p_state.add_argument("--session", required=True, help="Session ID")
    p_state.set_defaults(func=cmd_state)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if getattr(args, "verbose", False) else logging.WARNING,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 2
    return func(args)


if __name__ == "__main__":
    sys.exit(main())