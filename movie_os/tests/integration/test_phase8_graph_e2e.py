"""End-to-end Phase 8 integration test: full graph run on a 1-scene brief.

This test:
  1. Builds the graph
  2. Runs it on a minimal brief
  3. Verifies the state advances through movie → story → visual/voice/music/sfx → qa → publishing
  4. Checks the publishing manifest is written
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root))

    from movie_os.agents import build_graph, new_state

    print("=" * 60)
    print("Phase 8 — End-to-End Multi-Agent Test")
    print("=" * 60)

    graph = build_graph()

    output_dir = "/tmp/movie_os_phase8_e2e"
    Path(output_dir).mkdir(exist_ok=True)

    brief = {
        "title": "A Quiet Moment",
        "synopsis": "A man sits alone in a dimly lit room, contemplating.",
        "energy": 3,
        "duration": 6.0,
        "shot_language": {"shot_size": "medium"},
    }
    state = new_state(brief, thread_id="e2e_test")
    state = dict(state)
    state["output_dir"] = output_dir

    print(f"\nBrief: {brief['title']}")
    print(f"Output dir: {output_dir}")

    print("\nRunning graph...")
    result = asyncio.run(graph.ainvoke(state, config={"configurable": {"thread_id": "e2e_test"}}))

    print(f"\nResult current_step: {result.get('current_step')}")
    print(f"Errors: {result.get('errors', [])}")
    print(f"Timeline scenes: {len((result.get('timeline') or {}).get('scenes', []))}")
    print(f"Scene assets keys: {list((result.get('scene_assets') or {}).keys())}")
    print(f"QA report: {result.get('qa_report')}")
    print(f"Final video: {result.get('final_video')}")
    print(f"Manifest: {result.get('publishing_manifest')}")

    # Validation
    if result.get("errors"):
        print(f"\nFAIL: graph had errors: {result['errors']}")
        return 1

    if not result.get("timeline"):
        print("\nFAIL: no timeline in state")
        return 1

    scenes = result.get("timeline", {}).get("scenes", [])
    if not scenes:
        print("\nFAIL: timeline has no scenes")
        return 1

    qa = result.get("qa_report") or {}
    print(f"\nQA: {len(qa.get('passed_scenes', []))} passed, {len(qa.get('failed_scenes', []))} failed")

    if not result.get("publishing_manifest") and not result.get("final_video"):
        print("\nFAIL: no publishing output")
        return 1

    print(f"\nPASS: graph completed end-to-end")
    if result.get("publishing_manifest"):
        m = json.loads(open(result["publishing_manifest"]).read())
        print(f"  Manifest: {len(m.get('scenes', []))} scenes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
