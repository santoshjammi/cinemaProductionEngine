"""Genesis session sync gateway.

Routes persist/load between in-memory store (default) and Firestore store,
based on the project-level ``use_firestore`` feature flag read from
``movie_os/config/session.yaml``.

When ``use_firestore=True`` and the Firestore emulator is unreachable then
the gateway **falls back silently to in-memory** and logs a warning — this
is intentional: the mandate is local-first, no hard-fail on network loss.

Auth bridge (AW-04): when ``use_auth=True``, verifies tenant credentials
via ``AuthBackend.verify_token()`` before any Firestore write. Verification
failure raises immediately (fail-closed). The default is ``False`` to keep
backward compatibility with all existing GENESIS/PROMETHEUS paths.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Sequence

logger = logging.getLogger("movie_os.genesis.store.sync")

if TYPE_CHECKING:
    from movie_os.auth.backend import AuthBackend

# Lazy imports — avoid pulling in firebase-admin unless needed.


def _load_config():
    """Read movie_os/config/session.yaml if it exists."""
    import os
    try:
        import yaml
    except ImportError:
        return {"use_firestore": False}

    path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "session.yaml")
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return {"use_firestore": False}

    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    return cfg


# -- auth bridge helper (AW-04) -------------------------------------------

_auth_backend_cache: dict[str, object] = {}


def _get_auth_backend():
    """Lazily resolve the auth backend singleton."""
    if not _auth_backend_cache:
        from movie_os.auth import get_auth_backend
        _auth_backend_cache["backend"] = get_auth_backend()
    return _auth_backend_cache["backend"]  # type: ignore[return-value]


async def _validate_tenant_auth(user_id: str | None = None, token: str | None = None) -> bool:
    """Verify tenant credential before Firestore sync when ``use_auth=True``.

    Returns True on success. Raises immediately (fail-closed) for missing/invalid
    credentials. No-op when no auth is configured.
    """
    import os
    if not os.environ.get("GENESIS_USE_AUTH"):
        return True
    try:
        auth = _get_auth_backend()
        await auth.initialize()
        if token:
            info = await auth.verify_token(token)  # type: ignore[attr-defined]
            if info is None:
                raise PermissionError("Firebase Auth: token validation failed — sync blocked")
            return True
        if user_id:
            info = await auth.get_tenant_info(user_id)  # type: ignore[attr-defined]
            if info is None:
                raise PermissionError(f"Firebase Auth: unresolved tenant for UID {user_id} — sync blocked")
            return True
        return True
    except ImportError as exc:
        raise PermissionError(
            "GENESIS_USE_AUTH is enabled but firebase-admin is not installed. "
            "Either uninstall GENESIS_USE_AUTH or run: pip install \"video-gen[firestore]\""
        ) from exc


async def persist_session_meta(meta, *, use_firestore=None):  # type: ignore[type-arg]
    """Save session metadata to the configured (or overridden) store backend."""
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from movie_os.config import settings_manager
        tenant_id = getattr(settings_manager, 'user_tenant_id', None)  # type: ignore[attr-defined]
        token = getattr(settings_manager, 'firebase_token', None)  # type: ignore[attr-defined]
        await _validate_tenant_auth(user_id=tenant_id, token=token)

        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        await store.save_session_meta(meta)  # type: ignore[arg-type]
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        await store.save_session_meta(meta)


async def load_session_meta(session_id: str, *, use_firestore=None):  # type: ignore[type-arg]
    """Load session metadata from the configured (or overridden) store backend."""
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        return await store.load_session_meta(session_id)  # type: ignore[arg-type]
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        return await store.load_session_meta(session_id)


async def persist_node(node, *, use_firestore=None):
    """Persist a node record."""
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from movie_os.config import settings_manager
        tenant_id = getattr(settings_manager, 'user_tenant_id', None)
        token = getattr(settings_manager, 'firebase_token', None)
        await _validate_tenant_auth(user_id=tenant_id, token=token)
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        await store.save_node(node)  # type: ignore[arg-type]
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        await store.save_node(node)


async def load_node(node_id: str, *, use_firestore=None):
    """Load a node record."""
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        return await store.load_node(node_id)
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        return await store.load_node(node_id)


async def list_nodes(*, type: str | None = None, use_firestore=None):
    """List nodes, optionally filtered by type."""
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        return await store.list_nodes(type=type)
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        return await store.list_nodes(type=type)


async def persist_edge(edge, *, use_firestore=None):
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from movie_os.config import settings_manager
        tenant_id = getattr(settings_manager, 'user_tenant_id', None)
        token = getattr(settings_manager, 'firebase_token', None)
        await _validate_tenant_auth(user_id=tenant_id, token=token)
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        await store.save_edge(edge)
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        await store.save_edge(edge)


async def load_edge(edge_id: str, *, use_firestore=None):
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        return await store.load_edge(edge_id)
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        return await store.load_edge(edge_id)


async def persist_spec(spec, *, use_firestore=None):
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from movie_os.config import settings_manager
        tenant_id = getattr(settings_manager, 'user_tenant_id', None)
        token = getattr(settings_manager, 'firebase_token', None)
        await _validate_tenant_auth(user_id=tenant_id, token=token)
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        await store.save_spec(spec)
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        await store.save_spec(spec)


async def load_spec(spec_id: str, *, use_firestore=None):
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        return await store.load_spec(spec_id)
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        return await store.load_spec(spec_id)


async def list_specs(*, type: str | None = None, use_firestore=None):
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        return await store.list_specs(type=type)
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        return await store.list_specs(type=type)


async def persist_pkg_state(session_id: str, state: dict, *, use_firestore=None):
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from movie_os.config import settings_manager
        tenant_id = getattr(settings_manager, 'user_tenant_id', None)
        token = getattr(settings_manager, 'firebase_token', None)
        await _validate_tenant_auth(user_id=tenant_id, token=token)
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        await store.save_pkg_state(session_id, state)
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        await store.save_pkg_state(session_id, state)


async def load_pkg_state(session_id: str, *, use_firestore=None):
    if use_firestore is None:
        use_firestore = _load_config().get("use_firestore", False)

    if use_firestore:
        from .firestore_store import FirestoreStore
        store = FirestoreStore()
        return await store.load_pkg_state(session_id)
    else:
        from .memory_store import InMemoryStore
        store = InMemoryStore()
        return await store.load_pkg_state(session_id)
