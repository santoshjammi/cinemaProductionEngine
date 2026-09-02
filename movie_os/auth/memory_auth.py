"""Stub authentication backend for local-first / offline mode.

Accepts any token string as valid and returns a default local tenant
when ``get_tenant_info()`` or ``verify_token()`` is called.

Preserves existing behaviour when ``use_auth=False`` — no auth gate runs:
every write proceeds unconditionally (the design brief calls this "InMemoryAuth",
we alias it ``DummyAuthBackend`` for clarity).
"""

from __future__ import annotations

import os

from .backend import AuthBackend, TenantInfo


class DummyAuthBackend(AuthBackend):  # noqa: N801
    """No-op / dummy auth backend for offline-local-first use."""

    async def initialize(self) -> None:
        pass

    async def sign_in(self, tenant_id: str, token: str | None = None) -> TenantInfo:
        uid = os.environ.get("GENESIS_USER_ID", "local-dev")  # type: ignore[arg-type]
        return TenantInfo(
            tenant_id=tenant_id,
            user_id=uid,
            email=None,
            display_name="Local Dev",
        )

    async def sign_out(self, tenant_id: str) -> None:
        pass

    async def get_tenant_info(self, user_id: str) -> TenantInfo | None:
        return TenantInfo(
            tenant_id=f"tenants/{user_id}/metadata",
            user_id=user_id,
            email=None,
            display_name=f"user({user_id[:6]})",
        )

    async def verify_token(self, token: str) -> TenantInfo | None:
        return TenantInfo(
            tenant_id="tenants/local-dev/metadata",
            user_id=os.environ.get("GENESIS_USER_ID", "local-dev"),  # type: ignore[arg-type]
            email=None,
            display_name=None,
        )

    async def list_tenants(self) -> list[str]:
        return ["tenants/local-dev/metadata"]
