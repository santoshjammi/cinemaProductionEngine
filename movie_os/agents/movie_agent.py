"""MovieAgent — top-level orchestrator that decides the run plan.

For now this is a thin pass-through that just stamps the thread_id
and sets current_step. In future it could branch: "audio-first"
vs "visual-first" depending on the brief.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from movie_os.agents.base import AgentBase

if TYPE_CHECKING:
    from movie_os.agents.state import MovieState


logger = logging.getLogger("movie_os.agents.movie")


class MovieAgent(AgentBase):
    name = "movie_agent"

    async def run(self, state: "MovieState") -> "MovieState":
        logger.info(
            f"MovieAgent: brief keys={list(state.get('brief', {}).keys())}"
        )
        return {"current_step": "movie_planned"}
