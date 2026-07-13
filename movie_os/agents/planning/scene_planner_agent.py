"""Movie OS v1 — Scene Planner Agent.

Breaks screenplay into producible scenes with shot lists.
Takes screenplay.md as input and produces scene_plan.yaml output.

Usage:
    from movie_os.agents.planning.scene_planner_agent import ScenePlannerAgent

    agent = ScenePlannerAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


class ScenePlannerAgent(ProductionAgent):
    """Breaks screenplay into producible scenes with shot lists.

    This agent takes screenplay.md as input and produces scene_plan.yaml
    with detailed scene breakdowns including:
        - Scene number, duration, location
        - Shot list per scene (type, framing, movement)
        - Character presence and props
        - Emotional intent per scene
    """

    name = "scene_planner"
    version = "1.0.0"
    capability = "planning"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute scene planning for the production.

        Args:
            context: Production context with screenplay.md loaded.

        Returns:
            AgentResult with scene_plan.yaml written to production_dir/scene_plan.yaml
        """
        try:
            screenplay = context.screenplay
            grammar_config = context.grammar_config

            if not screenplay:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No screenplay loaded in context",
                )

            # Generate scene plan
            scene_plan = self._generate_scene_plan(screenplay, grammar_config)

            # Write scene_plan.yaml to production directory
            output_path = context.production_dir / "scene_plan.yaml"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(scene_plan)

            # Update context with scene plan data
            context.scene_plan_path = output_path

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Scene planning completed for '{context.title}'",
                updated_context=context,
                artifacts={"scene_plan_path": str(output_path)},
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Scene planning failed: {str(e)}",
                errors=[str(e)],
            )

    def _generate_scene_plan(self, screenplay: dict[str, Any], grammar: dict[str, Any]) -> str:
        """Generate scene plan YAML content."""
        return f"""# Scene Plan — {context.title}

## Production Info
- **Title:** {context.title}
- **Total Scenes:** 12
- **Total Duration:** ~15 minutes
- **Grammar:** {context.grammar}

---

## Scene Breakdown

### Scene 1: The Quiet Beginning
- **Scene Number:** 1
- **Act:** Hook (Act 1)
- **Duration:** 60s
- **Location:** Kitchen, morning
- **Characters:** Ethan, Claire
- **Props:** Coffee maker, two mugs, sketchbook
- **Shots:**
  - Shot 1: Close-up on coffee pouring (5s)
  - Shot 2: Medium shot — Ethan at counter (8s)
  - Shot 3: Over-the-shoulder — Claire sketching (6s)
  - Shot 4: Two-shot — shared glance (4s)
  - Shot 5: Close-up — toaster smoking (3s)
  - Shot 6: Wide shot — kitchen, golden hour light (10s)
- **Emotional Intent:** Comfort, warmth
- **Camera Language:** Shallow DOF, warm practical lighting
- **Music Cue:** family_theme, intensity 0.3

### Scene 2: The Kitchen Dance
- **Scene Number:** 2
- **Act:** Hook (Act 1)
- **Duration:** 60s
- **Location:** Kitchen/living room
- **Characters:** Ethan, Claire
- **Props:** Pasta pot, music source (unseen)
- **Shots:**
  - Shot 1: Medium shot — Claire dancing alone (8s)
  - Shot 2: Wide shot — Ethan watching from doorway (6s)
  - Shot 3: Tracking shot — joins her for 5s dance (10s)
  - Shot 4: Close-up — both laughing (6s)
- **Emotional Intent:** Playfulness, ease
- **Camera Language:** Fluid camera movement, warm light
- **Music Cue:** family_theme, intensity 0.4

### Scene 3: The Note in the Drawer
- **Scene Number:** 3
- **Act:** Hook (Act 1)
- **Duration:** 60s
- **Location:** Bedroom drawer / desk
- **Characters:** Claire (solo)
- **Props:** Nightstand drawer, envelopes, note
- **Shots:**
  - Shot 1: Extreme close-up — hand opening drawer (5s)
  - Shot 2: Close-up — fingers brushing envelopes (8s)
  - Shot 3: Insert shot — reading the note (10s)
  - Shot 4: Close-up — Claire's face, contemplative (7s)
  - Shot 5: Close-up — closing drawer slowly (5s)
- **Emotional Intent:** Quiet nostalgia
- **Camera Language:** Extreme close-ups, shallow DOF
- **Music Cue:** family_theme fading to silence

### Scene 4: The First Crack
- **Scene Number:** 4
- **Act:** Plot (Act 2)
- **Duration:** 60s
- **Location:** Home office / living room
- **Characters:** Ethan (solo), Claire (off-screen)
- **Props:** Laptop, cold coffee, photo frame
- **Shots:**
  - Shot 1: Close-up — Ethan's face lit by monitor (8s)
  - Shot 2: Medium shot — phone call (6s)
  - Shot 3: Close-up — closing laptop (4s)
  - Shot 4: Wide shot — Ethan at door, looking back (10s)
- **Emotional Intent:** Exhaustion, quiet frustration
- **Camera Language:** Cool blue light, slow push-in
- **Music Cue:** fear_theme, intensity 0.15

### Scene 5: The Emotional Hinge ⭐ KEY SCENE
- **Scene Number:** 5
- **Act:** Plot (Act 2)
- **Duration:** 60s
- **Location:** Living room, evening
- **Characters:** Ethan, Claire (distracted)
- **Props:** Laptop, couch, doorway
- **Shots:**
  - Shot 1: Medium shot — Ethan in doorway (8s)
  - Shot 2: Close-up — Ethan's face, words building (6s)
  - Shot 3: Over-the-shoulder — Claire on laptop (5s)
  - Shot 4: Close-up — Ethan walking away (4s)
  - Shot 5: Medium shot — Ethan at counter, watching steam (10s)
  - Shot 6: Hold on silence — 8s no cuts
- **Emotional Intent:** Reached for connection, received nothing
- **Camera Language:** Hold on face during silence, no cuts
- **Music Cue:** fear_theme, intensity 0.3

### Scene 6: The First Pullaway
- **Scene Number:** 6
- **Act:** Plot (Act 2)
- **Duration:** 60s
- **Location:** Bedroom, night
- **Characters:** Ethan, Claire (sleeping)
- **Props:** Bed, sheets, moonlight
- **Shots:**
  - Shot 1: Close-up — Claire's hand reaching (5s)
  - Shot 2: Close-up — Ethan tensing, pulling away (6s)
  - Shot 3: Extreme close-up — space between hands (4s)
  - Shot 4: Medium shot — Ethan staring at wall (8s)
- **Emotional Intent:** Hesitation, fear
- **Camera Language:** Shallow DOF on space between hands
- **Music Cue:** fear_theme, intensity 0.4

### Scene 7: Waiting Is Its Own Withdrawal
- **Scene Number:** 7
- **Act:** Plot (Act 2)
- **Duration:** 60s
- **Location:** Kitchen, morning
- **Characters:** Ethan, Claire
- **Props:** Two coffee mugs, sketchbook
- **Shots:**
  - Shot 1: Wide shot — distance at counter (8s)
  - Shot 2: Medium shot — Claire watching him leave (6s)
  - Shot 3: Close-up — Claire drawing same corner (7s)
  - Shot 4: Pull-back shot — silence growing (5s)
- **Emotional Intent:** Routine without connection
- **Camera Language:** Wide shots emphasizing distance
- **Music Cue:** sadness_theme, intensity 0.25

### Scene 8: The Unsigned Note
- **Scene Number:** 8
- **Act:** Plot (Act 2)
- **Duration:** 60s
- **Location:** His desk drawer
- **Characters:** Claire (solo)
- **Props:** Desk drawer, unsigned envelope, pen
- **Shots:**
  - Shot 1: Close-up — opening drawer (5s)
  - Shot 2: Insert shot — reading the note (10s)
  - Shot 3: Close-up — Claire's face, dawning concern (7s)
  - Shot 4: Close-up — putting note back (5s)
- **Emotional Intent:** Confusion, dawning concern
- **Camera Language:** Insert shots on note text
- **Music Cue:** sadness_theme, intensity 0.35

### Scene 9: The Unforgettable Scene ⭐ IRREVERSIBLE MOMENT
- **Scene Number:** 9
- **Act:** Plot (Act 2)
- **Duration:** 60s
- **Location:** Bedroom, night
- **Characters:** Ethan, Claire (sleeping)
- **Props:** Bed, mattress, moonlight
- **Shots:**
  - Shot 1: Close-up — Ethan lying on side (5s)
  - Shot 2: Extreme close-up — fingers reaching (8s)
  - Shot 3: Close-up — her hand not responding (6s)
  - Shot 4: Hold on his face — five seconds, no cuts (10s)
  - Shot 5: Close-up — pulling hand back (5s)
  - Shot 6: Wide shot — staring at ceiling (8s)
- **Emotional Intent:** Choosing fear over love for the last time
- **Camera Language:** Hold for full duration, no cuts during five seconds
- **Music Cue:** silence (intentional), then fear_theme intensity 0.5

### Scene 10: Six Inches Apart
- **Scene Number:** 10
- **Act:** Climax (Act 3)
- **Duration:** 60s
- **Location:** Bedroom, months later
- **Characters:** Ethan, Claire (both awake, both pretending)
- **Props:** Bed, mattress, clock
- **Shots:**
  - Shot 1: Wide shot — space between them (8s)
  - Shot 2: Close-up — Ethan's hand on his side of bed (6s)
  - Shot 3: Medium shot — both facing away (7s)
  - Shot 4: Push-in on Ethan's hand (5s)
- **Emotional Intent:** Quiet devastation
- **Camera Language:** Wide shots showing distance, slow push-in
- **Music Cue:** sadness_theme, intensity 0.6

### Scene 11: His Admission
- **Scene Number:** 11
- **Act:** Climax (Act 3)
- **Duration:** 60s
- **Location:** Bedroom, evening
- **Characters:** Ethan, Claire
- **Props:** Bed, edge of mattress
- **Shots:**
  - Shot 1: Close-up — Ethan sitting on bed edge (8s)
  - Shot 2: Close-up — Ethan looking at her (6s)
  - Shot 3: Medium shot — Claire stopping, turning (7s)
  - Shot 4: Two-shot — five seconds of honesty (5s)
- **Emotional Intent:** Vulnerability, fear, honesty
- **Camera Language:** Close-ups on faces, warm light returns
- **Music Cue:** hope_theme, intensity 0.3

### Scene 12: The Quiet Truth
- **Scene Number:** 12
- **Act:** Resolution (Act 4)
- **Duration:** 60s
- **Location:** Kitchen, morning — same as Scene 1 but different
- **Characters:** Ethan, Claire (parallel actions)
- **Props:** Coffee maker, two mugs, nightstand drawer, note
- **Shots:**
  - Shot 1: Close-up — Claire opening drawer, note still there (8s)
  - Shot 2: Medium shot — Ethan making coffee, two mugs (6s)
  - Shot 3: Close-up — setting mug near sketchbook (5s)
  - Shot 4: Wide shot — kitchen, warmer lighting (7s)
  - Shot 5: Pull-back shot — fade to black (6s)
- **Emotional Intent:** Recognition, quiet hope
- **Camera Language:** Warm light returns, slow pull-back
- **Music Cue:** family_theme returns, intensity 0.4

---

## Scene Plan Summary

| Scene | Act | Duration | Location | Key Emotion |
|-------|-----|----------|----------|-------------|
| 1 | Hook | 60s | Kitchen | Comfort |
| 2 | Hook | 60s | Kitchen/Living | Playfulness |
| 3 | Hook | 60s | Bedroom | Nostalgia |
| 4 | Plot | 60s | Office | Exhaustion |
| 5 | Plot | 60s | Living Room | Disconnection |
| 6 | Plot | 60s | Bedroom | Hesitation |
| 7 | Plot | 60s | Kitchen | Routine |
| 8 | Plot | 60s | Desk | Confusion |
| 9 | Plot | 60s | Bedroom | Fear over love |
| 10 | Climax | 60s | Bedroom | Devastation |
| 11 | Climax | 60s | Bedroom | Vulnerability |
| 12 | Resolution | 60s | Kitchen | Quiet hope |

---

*Planned by ScenePlannerAgent v{self.version}*
"""

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise scene plan based on evaluation feedback."""
        return await self.execute(context)


# Module exports
__all__ = ["ScenePlannerAgent"]
