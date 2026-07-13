"""Movie OS v1 — Research Agent.

Researches topic, psychology, cultural context for a production.
Takes idea/creative_brief as input and produces research.md output.

Usage:
    from movie_os.agents.creative.research_agent import ResearchAgent

    agent = ResearchAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


logger = logging.getLogger("movie_os.agents.creative.research_agent")


class ResearchAgent(ProductionAgent):
    """Researches topic, psychology, cultural context for a production.

    This agent takes the creative brief and dna.yaml as input and produces
    comprehensive research.md output that informs subsequent agents.

    Responsibilities:
        - Research psychological mechanisms relevant to the production
        - Gather cultural context and authenticity details
        - Identify emotional triggers and viewer resonance points
        - Compile reference materials and source citations
    """

    name = "research_agent"
    version = "1.0.0"
    capability = "research"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute research for the production.

        Uses local LLM (Ollama) to generate comprehensive research based on
        DNA and creative brief. Falls back to template if LLM is unavailable.

        Args:
            context: Production context with dna.yaml and creative_brief loaded.

        Returns:
            AgentResult with research.md written to production_dir/research.md
        """
        try:
            # Load input data from context
            dna = context.dna
            creative_brief = context.creative_brief

            if not dna:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No DNA data loaded in context",
                )

            if not creative_brief:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No creative brief loaded in context",
                )

            # Try LLM-based research first
            research_content = None
            try:
                research_content = await self._generate_research_with_llm(dna, creative_brief, context)
                logger.info(f"Research generated via LLM ({len(research_content)} chars)")
            except Exception as llm_error:
                logger.warning(f"LLM research failed, falling back to template: {llm_error}")

            if not research_content:
                research_content = self._generate_research_template(dna, creative_brief, context)

            # Write research.md to production directory
            output_path = context.production_dir / "research.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(research_content)

            # Update context with research data
            context.research_path = output_path

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Research completed for '{context.title}'",
                updated_context=context,
                artifacts={"research_path": str(output_path)},
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Research failed: {str(e)}",
                errors=[str(e)],
            )

    async def _generate_research_with_llm(self, dna: dict[str, Any], brief: dict[str, Any], context: ProductionContext) -> str:
        """Generate research content using local LLM (Ollama)."""
        from movie_os.llm.client import get_llm_client

        llm = get_llm_client()
        if not llm.is_available():
            logger.warning("LLM not available, falling back to template")
            return None

        territory = dna.get("territory", "unknown")
        cluster = dna.get("cluster", "unknown")
        mechanism = dna.get("mechanism", "unknown")
        archetype = dna.get("archetype", "unknown")
        theme = dna.get("theme", "unknown")

        target_audience = brief.get("target_audience", "general")
        primary_emotion = brief.get("primary_emotion", "unknown")
        desired_outcome = brief.get("desired_viewer_outcome", "")
        reference_works = brief.get("reference_works", [])
        target_runtime = brief.get("target_runtime", "14 minutes")

        system_prompt = f"""You are a senior film researcher and psychology consultant for a Cinema Production Engine.
Your job is to produce comprehensive, accurate research that will inform the screenplay writing team.

Grammar: {context.grammar if hasattr(context, 'grammar') and context.grammar else 'psychological_cinema'}
Production: {context.title if hasattr(context, 'title') and context.title else 'Untitled'}

Rules:
- Be specific and actionable, not generic
- Ground psychological insights in established research
- Provide concrete examples from film/literature
- Always maintain the grammar's creative constraints
- Never suggest melodrama or villain-making
- Focus on emotional authenticity and cause-and-effect"""

        user_prompt = f"""Research this production based on the following DNA and creative brief.

## Production DNA
- Territory: {territory}
- Cluster: {cluster}
- Mechanism: {mechanism}
- Archetype: {archetype}
- Theme: {theme}

## Creative Brief
- Target Audience: {target_audience}
- Primary Emotion: {primary_emotion}
- Desired Viewer Outcome: {desired_outcome}
- Target Runtime: {target_runtime}
- Reference Works: {', '.join(reference_works) if reference_works else 'N/A'}

## Required Research Sections

### 1. Psychological Mechanism Analysis
Deep dive into {mechanism.replace('_', ' ')}. Explain:
- How it manifests in behavior (show, don't tell)
- What triggers it
- How it escalates over time
- Why it's relatable to the target audience

### 2. Character Psychology
For characters involved in this territory:
- What do they want vs. what do they need?
- What keeps them stuck?
- What would it cost them to change?
- How does their psychology show in dialogue (hesitation, deflection, subtext)?

### 3. Cultural Context
- Social dynamics relevant to {territory}
- Authentic details that ground the story
- Common misconceptions to avoid

### 4. Emotional Triggers & Viewer Resonance
- Specific moments that will create recognition
- Scenes that build empathy (not pity)
- The hope element — how does it emerge naturally?

### 5. Reference Materials
- Academic/clinical sources (real, not fabricated)
- Films that handle this territory well (and why)
- Films that get it wrong (and why)

### 6. Production Notes for Screenplay Team
- Dialogue style recommendations
- Pacing guidance
- Visual language suggestions
- Music approach
- What to avoid at all costs

Format as a structured Markdown document with clear headings and bullet points."""

        response = llm.generate(system_prompt, user_prompt, temperature=0.8, max_tokens=4096)

        if not response.success:
            logger.warning(f"LLM research failed: {response.error}")
            return None

        # Wrap LLM output in proper format
        return f"""# Research — {context.title if hasattr(context, 'title') and context.title else 'Untitled'}

## Production DNA
- **Territory:** {territory}
- **Cluster:** {cluster}
- **Mechanism:** {mechanism}
- **Archetype:** {archetype}

---

{response.content}

---

*Generated by ResearchAgent v{self.version} via LLM ({response.model_used})*
"""

    def _generate_research_template(self, dna: dict[str, Any], brief: dict[str, Any], context: ProductionContext) -> str:
        """Generate research content using template (fallback when LLM unavailable)."""
        territory = dna.get("territory", "unknown")
        cluster = dna.get("cluster", "unknown")
        mechanism = dna.get("mechanism", "unknown")
        archetype = dna.get("archetype", "unknown")

        target_audience = brief.get("target_audience", "general")
        primary_emotion = brief.get("primary_emotion", "unknown")

        research = f"""# Research — {context.title if hasattr(context, 'title') and context.title else 'Untitled'}

## Production DNA
- **Territory:** {territory}
- **Cluster:** {cluster}
- **Mechanism:** {mechanism}
- **Archetype:** {archetype}

## Psychological Mechanisms

### {mechanism.replace('_', ' ').title()}
{self._get_mechanism_description(mechanism)}

### Related Psychological Concepts
1. **Anticipatory Anxiety** — Fear of negative outcomes prevents action
2. **Avoidance Coping** — Withdrawing from situations that trigger discomfort
3. **Emotional Suppression** — Inhibiting emotional expression despite internal experience
4. **Attachment Withdrawal** — Pulling away from intimacy when vulnerability feels risky

## Cultural Context

### Target Audience: {target_audience}
- Primary emotion to evoke: {primary_emotion}
- Cultural touchpoints relevant to this territory
- Social dynamics that amplify or mitigate the mechanism

## Emotional Triggers

### Viewer Resonance Points
1. **Recognition** — "I've experienced this"
2. **Empathy** — "I understand why they feel this way"
3. **Reflection** — "This makes me think about my own life"
4. **Hope** — "There's a path forward even without resolution"

## Reference Materials

### Academic Sources
- Attachment theory research (Bowlby, Ainsworth)
- Avoidance coping literature (Carver, Scheier)
- Emotional suppression studies (Gross, Hayes)

### Cultural References
- Films: {brief.get('reference_works', ['Marriage Story', 'Manchester by the Sea'])}
- Literary parallels to explore
- Documentary precedents

## Production Notes

### Authenticity Checklist
- [ ] Dialogue reflects real speech patterns (hesitation, deflection, subtext)
- [ ] Emotional progression follows cause-and-effect chain
- [ ] Characters avoid melodrama and over-explanation
- [ ] Silence and stillness carry emotional weight
- [ ] No villains — withdrawal caused by mutual misunderstanding

### Grammar Alignment
This research should inform the screenplay through:
- **Dialogue style:** Naturalistic, unfinished, subtext-heavy
- **Pacing:** Deliberate, stillness-focused
- **Camera language:** Intimate closeups, shallow DOF
- **Music:** Piano-driven with strings undertones
- **Lighting:** Natural shadows, practical sources

---
*Generated by ResearchAgent v{self.version} (template mode — LLM unavailable)*
"""
        return research

    def _get_mechanism_description(self, mechanism: str) -> str:
        """Get description for a psychological mechanism."""
        descriptions = {
            "anticipated_rejection": "Fear of negative outcomes prevents initiating intimacy. The person waits for certainty before acting, but certainty never comes — the fear itself becomes the barrier.",
            "fear_of_intimacy": "Closeness feels destabilizing. After moments of genuine connection, the nervous system triggers withdrawal as a regulation strategy.",
            "emotional_exhaustion": "Accumulated stress depletes emotional bandwidth. The person functions externally but shuts down internally — not dramatically, but quietly.",
            "fear_of_loss": "Safety triggers fear because there's now something to lose. Distance is created unconsciously before attachment can deepen.",
            "shame_based_withdrawal": "Needs feel shameful. Hyper-independence becomes identity — asking for help feels like reducing one's value.",
        }
        return descriptions.get(mechanism, f"Mechanism: {mechanism.replace('_', ' ').title()}")

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise research based on evaluation feedback."""
        # Research revision would re-run with updated parameters
        return await self.execute(context)


# Module exports
__all__ = ["ResearchAgent"]
