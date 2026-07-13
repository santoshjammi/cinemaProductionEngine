"""AgentBase — shared scaffolding for all agents.

Each agent:
  - has a unique `name`
  - holds a reference to the CapabilityRegistry
  - implements `run(state) -> state` (the work the agent does)
  - logs start/end times
  - appends errors to state.errors instead of raising

Keeping these concerns in one place means the actual agent logic
stays focused on the creative work.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from movie_os.capabilities import CapabilityRegistry
    from movie_os.agents.state import MovieState


logger = logging.getLogger("movie_os.agents")


@dataclass
class AgentContext:
    """Runtime context shared between agents.

    Bundles things every agent needs (registry, settings, asset store)
    so we don't have to plumb them through the LangGraph state.
    """
    registry: "CapabilityRegistry | None" = None
    output_dir: str = "output"
    settings: dict[str, Any] = field(default_factory=dict)
    asset_store: Any = None  # AssetStore | None — forward ref to avoid cycle
    quality: str = "draft"  # FLUX quality: draft/production/high_quality


class AgentBase(ABC):
    """Base class for all Movie OS agents."""

    name: str = "agent_base"

    def __init__(self, context: AgentContext):
        self.context = context

    @property
    def registry(self) -> "CapabilityRegistry | None":
        return self.context.registry

    def get_capability(self, capability_name: str):
        """Get a capability from the registry. Raises CapabilityNotFoundError."""
        if self.registry is None:
            from movie_os.capabilities import CapabilityNotFoundError
            raise CapabilityNotFoundError(capability_name)
        return self.registry.get(capability_name)

    def try_get_capability(self, capability_name: str):
        """Get a capability or None if no registry or capability not registered."""
        if self.registry is None:
            return None
        return self.registry.try_get(capability_name)

    @abstractmethod
    async def run(self, state: "MovieState") -> "MovieState":
        """Execute the agent's work and return the (possibly updated) state.

        Agents should NOT mutate the input state in place. Return a
        shallow copy with the keys they want to change. LangGraph
        merges this into the prior state.
        """
        ...

    async def __call__(self, state: "MovieState") -> "MovieState":
        """LangGraph node wrapper — logs and handles errors.

        Agents return partial updates. We pass those updates through
        unchanged — LangGraph merges them into the prior state.
        """
        t0 = time.time()
        logger.info(f"[{self.name}] start")
        try:
            new_state = await self.run(state)
            elapsed = time.time() - t0
            logger.info(
                f"[{self.name}] done in {elapsed:.2f}s "
                f"(current_step={new_state.get('current_step', '?')})"
            )
            return new_state
        except Exception as e:
            logger.exception(f"[{self.name}] failed: {e}")
            return {
                "errors": [f"{self.name}: {type(e).__name__}: {e}"],
                "current_step": f"{self.name}_failed",
            }


def make_state_updater(**changes) -> Callable[["MovieState"], "MovieState"]:
    """Build a state-update function from key=value changes.

    Useful for graph nodes that don't need their own class — e.g.
    the `route_after_qa` decision function.
    """
    def _update(state: "MovieState") -> "MovieState":
        out = dict(state)
        out.update(changes)
        return out  # type: ignore[return-value]
    return _update
