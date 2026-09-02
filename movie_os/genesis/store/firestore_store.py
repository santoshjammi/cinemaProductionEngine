"""Firebase Firestore-backed store backend for GENESIS session and PKG state sync.

Requires firebase-admin + an active Emulator Suite (Firestore on localhost:8080).
Raises RuntimeError immediately if the emulator is unreachable when use_firestore=True.
"""

from __future__ import annotations

import copy
import logging
import socket
from typing import Sequence

logger = logging.getLogger("movie_os.genesis.store.firestore")


class FirestoreStore:
    """Firebase Firestore-backed store. Fail-closed: raises if emulator is down."""

    _db = None  # lazy-initialized db instance

    def __init__(self, project_id: str = "__testing__", emulator_host: str = "localhost", emulator_port: int = 8080) -> None:
        self._project_id = project_id
        self._emulator_host = emulator_host
        self._emulator_port = emulator_port

    # -- connection / initialization -----------------------------------

    def _ensure_firebase_initialized(self) -> None:
        if self._db is not None:
            return
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
        except ImportError as exc:
            raise RuntimeError(
                "firebase-admin is required for FirestoreStore. Install with: pip install firebase-admin"
            ) from exc

        if not firebase_admin._projects:  # type: ignore[attr-defined]
            cred = None
            try:
                import os
                sa_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
                if sa_path:
                    cred = credentials.Certificate(sa_path)
                    firebase_admin.initialize_app(cred, project=self._project_id)  # type: ignore[attr-defined]
                    logger.info("Firebase initialized with service account.")
            except Exception:
                pass

            if not firebase_admin._projects:  # type: ignore[attr-defined]
                firebase_admin.initialize_app(project=self._project_id)  # type: ignore[attr-defined]
                logger.info(f"Firebase initialized on project {self._project_id}.")

        try:
            assert firestore is not None
            self._db = firestore.client()
        except Exception:
            raise RuntimeError("firebase_admin.firestore module unavailable; cannot create Firestore client.")

    def _ensure_emulator_connected(self) -> None:
        """Verify emulator is listening, then connect."""
        try:
            with socket.create_connection((self._emulator_host, self._emulator_port), timeout=2):
                pass
        except OSError as exc:
            raise RuntimeError(
                f"Firestore emulator unreachable at {self._emulator_host}:{self._emulator_port}. "
                "Start it with: firebase emulators:start --only firestore"
            ) from exc

        self._ensure_firebase_initialized()

        # Tell Firestore client to use emulator
        try:
            from firebase_admin import firestore
            assert firestore is not None
            if hasattr(firestore, 'EMULATOR_HOST_PORT'):
                import os
                os.environ.setdefault('FIRESTORE_EMULATOR_HOST', f'{self._emulator_host}:{self._emulator_port}')
        except Exception:
            pass

        self._db = firestore.client()
        logger.info(f"FirestoreStore connected to emulator at {self._emulator_host}:{self._emulator_port}")

    # -- collection helpers --------------------------------------------

    @property
    def _session_path(self) -> str:
        return "sessions"

    def _node_ref(self, session_id: str) -> object:
        return self._db.collection(self._session_path).document(session_id).collection("nodes")  # type: ignore[union-attr]

    def _edge_ref(self, session_id: str) -> object:
        return self._db.collection(self._session_path).document(session_id).collection("edges")

    def _spec_ref(self, session_id: str) -> object:
        return self._db.collection(self._session_path).document(session_id).collection("specs")

    # -- session meta --------------------------------------------------

    async def save_session_meta(self, meta) -> None:  # type: ignore[type-arg]
        self._ensure_emulator_connected()
        doc_ref = self._db.collection(self._session_path).document(meta.session_id)  # type: ignore[union-attr, attr-defined]
        doc_ref.set({
            "session_id": meta.session_id,
            "title": meta.title,
            "state": meta.state,
        }, merge=True)

    async def load_session_meta(self, session_id: str):
        self._ensure_emulator_connected()
        doc = self._db.collection(self._session_path).document(session_id).get()  # type: ignore[union-attr]
        if not doc.exists:
            return None
        from .backend import SessionMeta
        d = doc.to_dict()
        return SessionMeta(
            session_id=d["session_id"],
            title=d["title"],
            state=d["state"],
        )

    # -- nodes ---------------------------------------------------------

    async def save_node(self, node) -> None:  # type: ignore[type-arg]
        self._ensure_emulator_connected()
        # nodes belong to a session; use collectionGroup queries for lookups
        ref = self._node_ref("PLACEHOLDER").document(node.node_id)  # type: ignore[attr-defined]
        ref.set({
            "node_id": node.node_id,
            "type": node.type,
            "payload": copy.deepcopy(node.payload),
        }, merge=True)

    async def load_node(self, node_id: str):
        self._ensure_emulator_connected()
        query = self._db.collectionGroup("nodes").where("node_id", "==", node_id).limit(1)  # type: ignore[union-attr]
        result: Sequence = []
        for doc in query.stream():
            result.append(doc.to_dict())  # type: ignore[union-attr]
        if not result:
            return None
        from .backend import NodeRecord
        return NodeRecord(
            node_id=result[0]["node_id"],
            type=result[0]["type"],
            payload=result[0].get("payload", {}),
        )

    async def list_nodes(self, *, type: str | None = None) -> Sequence:
        self._ensure_emulator_connected()
        query = self._db.collectionGroup("nodes").stream()  # type: ignore[union-attr]
        records: Sequence = []
        from .backend import NodeRecord
        for doc in query:
            d = doc.to_dict()  # type: ignore[union-attr]
            if type is not None and d.get("type") != type:
                continue
            records.append(NodeRecord(
                node_id=d["node_id"],
                type=d["type"],
                payload=d.get("payload", {}),
            ))
        return records

    # -- edges ---------------------------------------------------------

    async def save_edge(self, edge) -> None:  # type: ignore[type-arg]
        self._ensure_emulator_connected()
        ref = self._edge_ref("PLACEHOLDER").document(edge.edge_id)  # type: ignore[attr-defined]
        ref.set({
            "edge_id": edge.edge_id,
            "type": edge.type,
            "from_id": edge.from_id,
            "to_id": edge.to_id,
            "payload": copy.deepcopy(edge.payload),
        }, merge=True)

    async def load_edge(self, edge_id: str):
        self._ensure_emulator_connected()
        query = self._db.collectionGroup("edges").where("edge_id", "==", edge_id).limit(1)  # type: ignore[union-attr]
        result: Sequence = []
        for doc in query.stream():
            result.append(doc.to_dict())  # type: ignore[union-attr]
        if not result:
            return None
        from .backend import EdgeRecord
        d = result[0]
        return EdgeRecord(
            edge_id=d["edge_id"],
            type=d["type"],
            from_id=d["from_id"],
            to_id=d["to_id"],
            payload=d.get("payload", {}),
        )

    async def list_edges(self, *, type: str | None = None) -> Sequence:
        self._ensure_emulator_connected()
        query = self._db.collectionGroup("edges").stream()  # type: ignore[union-attr]
        records: Sequence = []
        from .backend import EdgeRecord
        for doc in query:
            d = doc.to_dict()  # type: ignore[union-attr]
            if type is not None and d.get("type") != type:
                continue
            records.append(EdgeRecord(
                edge_id=d["edge_id"],
                type=d["type"],
                from_id=d["from_id"],
                to_id=d["to_id"],
                payload=d.get("payload", {}),
            ))
        return records

    # -- specs ---------------------------------------------------------

    async def save_spec(self, spec) -> None:  # type: ignore[type-arg]
        self._ensure_emulator_connected()
        ref = self._spec_ref("PLACEHOLDER").document(spec.spec_id)  # type: ignore[attr-defined]
        ref.set({
            "spec_id": spec.spec_id,
            "type": spec.type,
            "content": copy.deepcopy(spec.content),
        }, merge=True)

    async def load_spec(self, spec_id: str):
        self._ensure_emulator_connected()
        query = self._db.collectionGroup("specs").where("spec_id", "==", spec_id).limit(1)  # type: ignore[union-attr]
        result: Sequence = []
        for doc in query.stream():
            result.append(doc.to_dict())  # type: ignore[union-attr]
        if not result:
            return None
        from .backend import SpecRecord
        d = result[0]
        return SpecRecord(
            spec_id=d["spec_id"],
            type=d["type"],
            content=d.get("content", {}),
        )

    async def list_specs(self, *, type: str | None = None) -> Sequence:
        self._ensure_emulator_connected()
        query = self._db.collectionGroup("specs").stream()  # type: ignore[union-attr]
        records: Sequence = []
        from .backend import SpecRecord
        for doc in query:
            d = doc.to_dict()  # type: ignore[union-attr]
            if type is not None and d.get("type") != type:
                continue
            records.append(SpecRecord(
                spec_id=d["spec_id"],
                type=d["type"],
                content=d.get("content", {}),
            ))
        return records

    # -- pkg state -----------------------------------------------------

    async def save_pkg_state(self, session_id: str, state: dict) -> None:  # type: ignore[type-arg]
        self._ensure_emulator_connected()
        doc_ref = self._db.collection(self._session_path).document(session_id).collection("metadata").document("pkg_state")
        doc_ref.set(state, merge=True)

    async def load_pkg_state(self, session_id: str):
        self._ensure_emulator_connected()
        doc = self._db.collection(self._session_path).document(session_id).collection("metadata").document("pkg_state").get()
        if not doc.exists:
            return None
        return dict(doc.to_dict())
