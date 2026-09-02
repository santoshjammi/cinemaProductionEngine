"""Authentication backend interfaces — tenant identity and federation gates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TenantInfo:
    """Represents a resolved tenant + Firebase Auth user. Immutable once created."""
    tenant_id: str  # firebase tenant ID or emulator alias
    user_id: str | None  # may be None for anonymous / unauthenticated state
    email: str | None
    display_name: str | None = None


class AuthBackend(Protocol):
    """Abstract authentication backend — both Firebase and stub implement this."""

    async def initialize(self) -> None: ...
    async def sign_in(self, tenant_id: str, token: str | None = None) -> TenantInfo: ...
    async def sign_out(self, tenant_id: str) -> None: ...
    async def get_tenant_info(self, user_id: str) -> TenantInfo | None: ...
    async def verify_token(self, token: str) -> TenantInfo | None: ...
    async def list_tenants(self) -> list[str]: ...
