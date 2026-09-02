"""Tests for movie_os/auth — dummy fallback, get_auth_backend routing, and token passthrough."""

from __future__ import annotations

import asyncio

import pytest

from movie_os.auth import DummyAuthBackend, get_auth_backend


def test_dummy_backend_sign_in_returns_tenant_info():
    """Dummy sign-in must return a valid TenantInfo even without firebase-admin."""
    auth = DummyAuthBackend()
    ti = asyncio.run(auth.sign_in("tenant-a"))
    assert ti.tenant_id == "tenant-a"
    assert ti.user_id is not None
    assert len(ti.user_id) > 0


def test_dummy_backend_verify_token_accepts_any_value():
    """In offline mode verify_token should always succeed."""
    auth = DummyAuthBackend()
    ti = asyncio.run(auth.verify_token("any-fake-token"))
    assert ti is not None
    assert ti.display_name == "__offline__"


def test_get_auth_backend_returns_working_instance(monkeypatch):
    """get_auth_backend should return a non-None AuthBackend regardless of firebase-admin availability."""
    # Normal path — may or may not have firebase-admin installed.
    backend = get_auth_backend()
    assert backend is not None
    assert hasattr(backend, "sign_in")
    assert hasattr(backend, "verify_token")
