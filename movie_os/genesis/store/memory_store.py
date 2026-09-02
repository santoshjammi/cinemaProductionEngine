"""In-memory store backend for GENESIS session and PKG state sync.

Used when use_firestore=False (the default). Provides identical API to
FirestoreStore so callers never need to branch on backend type.
"""

from __future__ import annotations

import copy
import json
from typing import Sequence


class InMemoryStore:
    """Dict-backed ephemeral store. All data is lost on process exit."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, object]] = {}
        self._nodes: dict[str, dict[str, object]] = {}
        self._edges: dict[str, dict[str, object]] = {}
        self._specs: dict[str, dict[str, object]] = {}
        self._pkg_state: dict[str, dict] = {}

    # -- session meta --------------------------------------------------

    async def save_session_meta(self, meta) -> None:
        key = meta.session_id  # type: ignore[attr-defined]
        if key not in self._sessions:
            self._sessions[key] = {}
        payload = {
            "session_id": meta.session_id,
            "title": meta.title,
            "state": meta.state,
        }
        self._sessions[key] = payload

    async def load_session_meta(self, session_id: str):
        data = self._sessions.get(session_id)
        if data is None:
            return None
        from .backend import SessionMeta
        return SessionMeta(
            session_id=data["session_id"],
            title=data["title"],
            state=data["state"],
        )

    # -- nodes ---------------------------------------------------------

    async def save_node(self, node) -> None:
        self._nodes[node.node_id] = {  # type: ignore[attr-defined]
            "node_id": node.node_id,
            "type": node.type,
            "payload": copy.deepcopy(node.payload),  # type: ignore[attr-defined]
        }

    async def load_node(self, node_id: str):
        data = self._nodes.get(node_id)
        if data is None:
            return None
        from .backend import NodeRecord
        return NodeRecord(
            node_id=data["node_id"],
            type=data["type"],
            payload=data["payload"],
        )

    async def list_nodes(self, *, type: str | None = None) -> Sequence:
        records = []
        from .backend import NodeRecord
        for data in self._nodes.values():
            if type is not None and data["type"] != type:
                continue
            records.append(NodeRecord(
                node_id=data["node_id"],
                type=data["type"],
                payload=data["payload"],
            ))
        return records

    # -- edges ---------------------------------------------------------

    async def save_edge(self, edge) -> None:
        self._edges[edge.edge_id] = {  # type: ignore[attr-defined]
            "edge_id": edge.edge_id,
            "type": edge.type,
            "from_id": edge.from_id,  # type: ignore[attr-defined]
            "to_id": edge.to_id,  # type: ignore[attr-defined]
            "payload": copy.deepcopy(edge.payload),  # type: ignore[attr-defined]
        }

    async def load_edge(self, edge_id: str):
        data = self._edges.get(edge_id)
        if data is None:
            return None
        from .backend import EdgeRecord
        return EdgeRecord(
            edge_id=data["edge_id"],
            type=data["type"],
            from_id=data["from_id"],
            to_id=data["to_id"],
            payload=data["payload"],
        )

    async def list_edges(self, *, type: str | None = None) -> Sequence:
        records = []
        from .backend import EdgeRecord
        for data in self._edges.values():
            if type is not None and data["type"] != type:
                continue
            records.append(EdgeRecord(
                edge_id=data["edge_id"],
                type=data["type"],
                from_id=data["from_id"],
                to_id=data["to_id"],
                payload=data["payload"],
            ))
        return records

    # -- specs ---------------------------------------------------------

    async def save_spec(self, spec) -> None:
        self._specs[spec.spec_id] = {  # type: ignore[attr-defined]
            "spec_id": spec.spec_id,
            "type": spec.type,  # type: ignore[attr-defined]
            "content": copy.deepcopy(spec.content),  # type: ignore[attr-defined]
        }

    async def load_spec(self, spec_id: str):
        data = self._specs.get(spec_id)
        if data is None:
            return None
        from .backend import SpecRecord
        return SpecRecord(
            spec_id=data["spec_id"],
            type=data["type"],
            content=data["content"],
        )

    async def list_specs(self, *, type: str | None = None) -> Sequence:
        records = []
        from .backend import SpecRecord
        for data in self._specs.values():
            if type is not None and data["type"] != type:
                continue
            records.append(SpecRecord(
                spec_id=data["spec_id"],
                type=data["type"],
                content=data["content"],
            ))
        return records

    # -- pkg state -----------------------------------------------------

    async def save_pkg_state(self, session_id: str, state: dict) -> None:
        self._pkg_state[session_id] = copy.deepcopy(state)

    async def load_pkg_state(self, session_id: str):
        data = self._pkg_state.get(session_id)
        if data is None:
            return None
        return copy.deepcopy(data)
