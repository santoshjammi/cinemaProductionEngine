"""Storage backend interfaces for GENESIS session and PKG state sync."""

from __future__ import annotations

from typing import Protocol, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class SessionMeta:
    session_id: str
    title: str
    state: str  # e.g. "draft", "review", "sealed"


@dataclass(frozen=True)
class NodeRecord:
    node_id: str
    type: str  # "story", "character", "scene", etc.
    payload: dict


@dataclass(frozen=True)
class EdgeRecord:
    edge_id: str
    type: str  # "leads_to", "depended_by"
    from_id: str
    to_id: str
    payload: dict


@dataclass(frozen=True)
class SpecRecord:
    spec_id: str
    type: str  # "visual", "audio", "narrative"
    content: dict


class StoreBackend(Protocol):
    """Abstract storage backend — both in-memory and Firestore implement this."""

    async def save_session_meta(self, meta: SessionMeta) -> None: ...
    async def load_session_meta(self, session_id: str) -> SessionMeta | None: ...

    async def save_node(self, node: NodeRecord) -> None: ...
    async def load_node(self, node_id: str) -> NodeRecord | None: ...
    async def list_nodes(self, *, type: str | None = None) -> Sequence[NodeRecord]: ...

    async def save_edge(self, edge: EdgeRecord) -> None: ...
    async def load_edge(self, edge_id: str) -> EdgeRecord | None: ...
    async def list_edges(self, *, type: str | None = None) -> Sequence[EdgeRecord]: ...

    async def save_spec(self, spec: SpecRecord) -> None: ...
    async def load_spec(self, spec_id: str) -> SpecRecord | None: ...
    async def list_specs(self, *, type: str | None = None) -> Sequence[SpecRecord]: ...

    async def save_pkg_state(self, session_id: str, state: dict) -> None: ...
    async def load_pkg_state(self, session_id: str) -> dict | None: ...
