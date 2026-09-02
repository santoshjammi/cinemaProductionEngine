"""Authenticated user identity for videoGen (AW-04).

Provides ``AuthBackend`` protocol, a real Firebase implementation, and a
stub that runs offline without any network calls.

Usage
-----

    # Real Firebase Auth:
    from movie_os.auth import FirebaseAuthBackend
    auth = FirebaseAuthBackend()
    await auth.initialize()
    ti = await auth.sign_in("tenant-a")

    # Offline fallback (default):
    from movie_os.auth import DummyAuthBackend, get_auth_backend
    auth = get_auth_backend()  # returns DummyAuthBackend when firebase-admin absent
"""

from .backend import AuthBackend, TenantInfo
from .firebase_auth import FirebaseAuthBackend, DummyAuthBackend


def get_auth_backend():
    """Return a working AuthBackend (real or dummy) based on availability."""
    try:
        return FirebaseAuthBackend()  # type: ignore[return-value]
    except ImportError:
        import logging
        logging.warning("firebase-admin not available; falling back to DummyAuthBackend")
        return DummyAuthBackend()


__all__ = [
    "AuthBackend",
    "TenantInfo",
    "FirebaseAuthBackend",
    "DummyAuthBackend",
    "get_auth_backend",
]
