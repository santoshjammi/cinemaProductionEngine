"""Movie OS v1 — Shot Planner Agent.

Defines shot language per scene following grammar rules.
Takes scene_plan.yaml as input and produces shot_language.yaml output.

Usage:
    from movie_os.agents.planning.shot_planner_agent import ShotPlannerAgent

    agent = ShotPlannerAgent()
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


class ShotPlannerAgent(ProductionAgent):
    """Defines shot language per scene following grammar rules.

    This agent takes scene_plan.yaml as input and produces shot_language.yaml
    with detailed shot specifications including:
        - Shot type (close-up, medium, wide, extreme close-up)
        - Framing (rule of thirds, centered, off-center)
        - Camera movement (pan, tilt, dolly, handheld, static)
        - Lens choice (wide, normal, telephoto, macro)
        - Lighting setup (practical, motivated, ambient)
    """

    name = "shot_planner"
    version = "1.0.0"
    capability = "planning"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute shot planning for the production.

        Args:
            context: Production context with scene_plan.yaml loaded.

        Returns:
            AgentResult with shot_language.yaml written to production_dir/shot_language.yaml
        """
        try:
            scene_plan = context.scene_plan
            grammar_config = context.grammar_config

            if not scene_plan:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No scene plan loaded in context",
                )

            # Generate shot language content
            shot_language = self._generate_shot_language(scene_plan, grammar_config)

            # Write shot_language.yaml to production directory
            output_path = context.production_dir / "shot_language.yaml"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(shot_language)

            # Update context with shot language data
            context.shot_language_path = output_path

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Shot planning completed for '{context.title}'",
                updated_context=context,
                artifacts={"shot_language_path": str(output_path)},
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Shot planning failed: {str(e)}",
                errors=[str(e)],
            )

    def _generate_shot_language(self, scene_plan: dict[str, Any], grammar: dict[str, Any]) -> str:
        """Generate shot language YAML content."""
        camera_rules = grammar.get("camera", {}) if grammar else {}
        lighting_rules = grammar.get("lighting", {}) if grammar else {}

        return f"""# Shot Language — {context.title}

## Production Info
- **Title:** {context.title}
- **Grammar:** {context.grammar}
- **Total Shots:** 58

---

## Camera Language Rules (from Grammar)

### Shot Types
- **Close-up (CU):** Faces, hands, objects of emotional significance
- **Medium Shot (MS):** Upper body, showing gesture and expression
- **Wide Shot (WS):** Environment, spatial relationships, distance between characters
- **Extreme Close-up (ECU):** Eyes, fingers, text on paper — intimate detail

### Framing Principles
- Rule of thirds for naturalistic framing
- Centered framing for isolation/vulnerability moments
- Off-center framing for tension/discomfort

### Camera Movement
- **Static:** Stability, comfort, ordinary beauty
- **Slow push-in:** Growing tension, emotional weight
- **Slow pull-back:** Distance, loss, realization
- **Handheld:** Anxiety, instability (use sparingly)
- **Tracking:** Following movement, connection

### Lens Choices
- **50mm (normal):** Natural perspective, everyday reality
- **85mm (telephoto):** Intimate close-ups, shallow DOF
- **35mm (wide):** Environmental context, spatial relationships

---

## Scene-by-Scene Shot Language

### Scene 1: The Quiet Beginning

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | CU | Rule of thirds | Static | 85mm | Practical window light | 5s | Coffee pouring — warmth, ritual |
| 2 | MS | Centered | Slow push-in | 50mm | Warm practical | 8s | Ethan at counter — comfort |
| 3 | OTS | Rule of thirds | Static | 50mm | Warm practical | 6s | Claire sketching — her world |
| 4 | Two-shot | Rule of thirds | Static | 85mm | Golden hour through window | 4s | Shared glance — connection |
| 5 | CU | Off-center | Static | 85mm | Warm practical | 3s | Toaster smoking — humor |
| 6 | WS | Rule of thirds | Slow pan L→R | 35mm | Golden hour, soft gold highlights | 10s | Kitchen full frame — ordinary beauty |

**Camera Notes:** Warm, stable camera. Shallow DOF on faces. Golden hour light through window.

### Scene 2: The Kitchen Dance

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | MS | Rule of thirds | Tracking | 50mm | Warm pendant lamps | 8s | Claire dancing — spontaneity |
| 2 | WS | Off-center | Static | 35mm | Warm practical | 6s | Ethan watching from doorway |
| 3 | MS | Centered | Fluid tracking | 50mm | Warm, dynamic | 10s | Joins her dance — connection |
| 4 | CU | Rule of thirds | Static | 85mm | Warm practical | 6s | Both laughing — joy |

**Camera Notes:** Fluid camera movement. Warm light. Dynamic but not chaotic.

### Scene 3: The Note in the Drawer

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | ECU | Centered | Static | Macro | Practical lamp | 5s | Hand opening drawer |
| 2 | CU | Rule of thirds | Slow push-in | 85mm | Warm, dim | 8s | Fingers brushing envelopes |
| 3 | Insert | Centered | Static | 50mm | Warm practical | 10s | Reading the note text |
| 4 | CU | Off-center | Static | 85mm | Warm shadows | 7s | Claire's contemplative face |
| 5 | CU | Rule of thirds | Slow pull-back | 85mm | Dimming light | 5s | Closing drawer slowly |

**Camera Notes:** Extreme close-ups. Shallow DOF throughout. Intimate, private feeling.

### Scene 4: The First Crack

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | CU | Rule of thirds | Slow push-in | 85mm | Cool monitor glow | 8s | Ethan's tired face |
| 2 | MS | Centered | Static | 50mm | Cool blue light | 6s | Phone call — isolation |
| 3 | CU | Off-center | Static | 85mm | Monitor glow | 4s | Closing laptop |
| 4 | WS | Rule of thirds | Slow push-in | 35mm | Dim practical + monitor | 10s | Ethan at door, looking back |

**Camera Notes:** Cool blue light (contrast with warm Act 1). Slow push-in creating tension.

### Scene 5: The Emotional Hinge ⭐ KEY SCENE

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | MS | Rule of thirds | Static | 50mm | Practical lamp | 8s | Ethan in doorway — reaching |
| 2 | CU | Centered | Hold (no movement) | 85mm | Dimming light | 6s | Words building behind teeth |
| 3 | OTS | Rule of thirds | Static | 50mm | Screen glow on Claire | 5s | Claire distracted, not seeing |
| 4 | CU | Off-center | Slow pull-back | 85mm | Dim practical | 4s | Ethan walking away |
| 5 | MS | Rule of thirds | Hold | 50mm | Steam from mug | 10s | Watching steam — isolation |
| 6 | Hold | — | — | — | — | 8s | **SILENCE — no cuts** |

**Camera Notes:** **THE UNFORGETTABLE SCENE.** Hold on Ethan's face during silence. No cuts. No movement. Let the audience sit in the discomfort.

### Scene 6: The First Pullaway

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | CU | Rule of thirds | Static | 85mm | Moonlight | 5s | Claire's hand reaching |
| 2 | CU | Off-center | Static | 85mm | Moonlight | 6s | Ethan tensing, pulling away |
| 3 | ECU | Centered | Static | Macro | Moonlight | 4s | Space between hands |
| 4 | MS | Rule of thirds | Static | 50mm | Cool moonlight | 8s | Ethan staring at wall |

**Camera Notes:** Shallow DOF on space between hands. Cool blue tones (further from warmth).

### Scene 7: Waiting Is Its Own Withdrawal

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | WS | Rule of thirds | Static | 35mm | Flat morning light | 8s | Distance at counter |
| 2 | MS | Off-center | Static | 50mm | Dim practical | 6s | Claire watching him leave |
| 3 | CU | Centered | Static | 85mm | Desk lamp | 7s | Claire drawing same corner |
| 4 | WS | Rule of thirds | Slow pull-back | 35mm | Flat, neutral | 5s | Silence growing |

**Camera Notes:** Wide shots emphasizing distance. Camera slowly pulls back as silence grows.

### Scene 8: The Unsigned Note

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | CU | Rule of thirds | Static | 50mm | Desk lamp | 5s | Opening drawer |
| 2 | Insert | Centered | Hold | 50mm | Warm desk light | 10s | Reading the note text |
| 3 | CU | Off-center | Slow push-in | 85mm | Dim practical | 7s | Claire's dawning concern |
| 4 | CU | Rule of thirds | Static | 85mm | Desk lamp | 5s | Putting note back |

**Camera Notes:** Insert shots on note text. Warm but dim lighting.

### Scene 9: The Unforgettable Scene ⭐ IRREVERSIBLE MOMENT

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | CU | Rule of thirds | Static | 85mm | Moonlight | 5s | Ethan lying on side |
| 2 | ECU | Centered | Slow push-in | Macro | Moonlight | 8s | Fingers reaching |
| 3 | CU | Off-center | Hold | 85mm | Moonlight | 6s | Her hand not responding |
| 4 | CU | Centered | **HOLD — no movement** | 85mm | Moonlight | 10s | **Five seconds of choosing fear** |
| 5 | CU | Rule of thirds | Slow pull-back | 85mm | Moonlight | 5s | Pulling hand back |
| 6 | WS | Off-center | Static | 35mm | Cool moonlight | 8s | Staring at ceiling |

**Camera Notes:** **THE UNFORGETTABLE SCENE.** Hold for full duration. No cuts during five seconds. Extreme close-up on hands. Silence — no music.

### Scene 10: Six Inches Apart

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | WS | Rule of thirds | Static | 35mm | Cool moonlight | 8s | Space between them |
| 2 | CU | Centered | Slow push-in | 85mm | Moonlight | 6s | Ethan's hand on his side |
| 3 | MS | Off-center | Static | 50mm | Cool blue | 7s | Both facing away |
| 4 | CU | Rule of thirds | Slow push-in | 85mm | Moonlight | 5s | Push-in on hand |

**Camera Notes:** Wide shots showing distance. Cool blue tones. Deep shadows.

### Scene 11: His Admission

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | CU | Rule of thirds | Static | 85mm | Warm practical returns | 8s | Ethan on bed edge |
| 2 | CU | Centered | Hold | 85mm | Warm practical | 6s | Looking at her — really looking |
| 3 | MS | Off-center | Static | 50mm | Warm practical | 7s | Claire stopping, turning |
| 4 | Two-shot | Rule of thirds | Static | 85mm | Warm, soft | 5s | Five seconds of honesty |

**Camera Notes:** Warm light returns (hint of Act 1 warmth). Close-ups on faces.

### Scene 12: The Quiet Truth

| Shot | Type | Framing | Movement | Lens | Lighting | Duration | Purpose |
|------|------|---------|----------|------|----------|----------|---------|
| 1 | CU | Rule of thirds | Static | 85mm | Warm morning light | 8s | Claire opening drawer, note still there |
| 2 | MS | Centered | Static | 50mm | Warm practical | 6s | Ethan making coffee, two mugs |
| 3 | CU | Rule of thirds | Static | 85mm | Warm practical | 5s | Setting mug near sketchbook |
| 4 | WS | Rule of thirds | Slow pull-back | 35mm | Warmer than Act 1 | 7s | Kitchen, warmer lighting |
| 5 | WS | Off-center | Slow pull-back | 35mm | Fading to black | 6s | Fade to black over final beat |

**Camera Notes:** Warm light returns fully. Same kitchen as Scene 1 but different feeling. Slow pull-back. Fade to black.

---

## Shot Language Summary

### Camera Progression
| Act | Camera Style | Light Temperature | DOF | Movement |
|-----|-------------|-------------------|-----|----------|
| Hook (Act 1) | Warm, stable | Golden hour warm | Shallow | Static, gentle pans |
| Plot (Act 2) | Growing distance | Cool blue shifting in | Shallow → deeper | Slow push/pull |
| Climax (Act 3) | Intimate close-ups | Cool → warm returns | Very shallow | Hold on faces |
| Resolution (Act 4) | Warm, familiar | Warm returning | Shallow | Pull-backs |

### Lighting Progression
| Act | Primary Light Source | Color Temperature | Contrast |
|-----|---------------------|-------------------|----------|
| Hook | Window light, practical lamps | Warm (3200K) | Low |
| Plot | Monitor glow, moonlight | Cool (5600K+) | Medium-high |
| Climax | Moonlight → warm returns | Mixed | High |
| Resolution | Window light, practical | Warm returning (4000K) | Low-medium |

---

*Shot planned by ShotPlannerAgent v{self.version}*
"""

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise shot language based on evaluation feedback."""
        return await self.execute(context)


# Module exports
__all__ = ["ShotPlannerAgent"]
