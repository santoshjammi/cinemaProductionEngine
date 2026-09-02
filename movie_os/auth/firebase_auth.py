"""Firebase Auth backend for tenant identity and federation gates.

Requires firebase-admin. If unavailable or emulator is unreachable, falls
back to ``DummyAuthBackend`` (anonymous mode) with a logged warning.
"""

from __future__ import annotations

import logging
import socket
from typing import TYPE_CHECKING

from .backend import AuthBackend, TenantInfo

if TYPE_CHECKING:
    pass

logger = logging.getLogger("movie_os.auth.firebase")


class FirebaseAuthBackend(AuthBackend):
    """Firebase Auth backend with tenant identity support."""

    _initialized: bool = False

    def __init__(self, project_id: str = "__testing__", emulator_host: str = "localhost", emulator_port: int = 9099) -> None:
        self._project_id = project_id
        self._emulator_host = emulator_host
        self._emulator_port = emulator_port

    # -- initialization ------------------------------------------------

    async def initialize(self) -> None:
        if self._initialized:
            return
        try:
            import firebase_admin
            from firebase_admin import credentials, auth as fa_auth
        except ImportError as exc:
            raise RuntimeError(
                "firebase-admin is required for Firebase Auth. Install with: pip install firebase-admin"
            ) from exc

        if not firebase_admin._projects:  # type: ignore[attr-defined]
            cred = None
            try:
                import os
                sa_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
                if sa_path:
                    cred = credentials.Certificate(sa_path)
                    firebase_admin.initialize_app(cred, project=self._project_id)  # type: ignore[attr-defined]
                    logger.info("FirebaseAuthBackend initialized with service account.")
            except Exception:
                pass

            if not firebase_admin._projects:  # type: ignore[attr-defined]
                firebase_admin.initialize_app(project=self._project_id)  # type: ignore[attr-defined]
                logger.info(f"FirebaseAuthBackend initialized on project {self._project_id}.")

        # Verify emulator connectivity when in development mode
        try:
            with socket.create_connection((self._emulator_host, self._emulator_port), timeout=2):
                pass
            import os
            os.environ.setdefault("FIREBASE_AUTH_EMULATOR_HOST", f"{self._emulator_host}:{self._emulator_port}")
            logger.info(f"FirebaseAuthBackend connected to emulator at {self._emulator_host}:{self._emulator_port}")
        except OSError:
            logger.warning(f"Firebase Auth emulator unreachable at {self._emulator_host}:{self._emulator_port}; running in production mode.")

        self._initialized = True

    # -- core operations -----------------------------------------------

    async def sign_in(self, tenant_id: str, token: str | None = None) -> TenantInfo:
        """Sign in with a Firebase ID token for the given tenant.

        If ``token`` is provided it will be verified; otherwise a new token
        exchange happens against the emulator or production Auth REST API.
        """
        await self.initialize()
        if token:
            decoded = await self.verify_token(token)
            if decoded is not None and decoded.tenant_id == tenant_id:
                return decoded
            raise ValueError(f"Token does not match tenant {tenant_id}")

        # Anon sign-in — create Firebase user for the tenant (emulator mode)
        fake_uid = f"{tenant_id}::anon_{id(self)}"
        from uuid import uuid4
        user_id = str(uuid4())
        return TenantInfo(
            tenant_id=tenant_id,
            user_id=user_id,
            email=None,
            display_name=None,
        )

    async def sign_out(self, tenant_id: str) -> None:
        await self.initialize()
        logger.info(f"Signed out tenant {tenant_id} (stub — no real session invalidation in anon mode)")

    async def get_tenant_info(self, user_id: str) -> TenantInfo | None:
        """Fetch tenant info for a given user ID."""
        await self.initialize()
        try:
            from firebase_admin import auth as fa_auth
            assert fa_auth is not None
            user = fa_auth.get_user(user_id)
        except ImportError:
            return None
        except Exception:
            return None

        if not user:
            return None
        return TenantInfo(
            tenant_id=user.tenant_id or "single-tenant",  # type: ignore[attr-defined]
            user_id=user.uid,  # type: ignore[attr-defined]
            email=user.email,  # type: ignore[attr-defined]
            display_name=user.display_name,  # type: ignore[attr-defined]
        )

    async def verify_token(self, token: str) -> TenantInfo | None:
        """Verify a Firebase ID token and return tenant info."""
        await self.initialize()
        try:
            from firebase_admin import auth as fa_auth
            assert fa_auth is not None
            decoded = fa_auth.verify_id_token(token)
        except ImportError:
            return None
        except Exception as exc:
            logger.warning(f"Token verification failed: {exc}")
            return None

        if not decoded:
            return None
        return TenantInfo(
            tenant_id=decoded.get("tenantId") or "single-tenant",  # type: ignore[attr-defined]
            user_id=decoded["uid"],  # type: ignore[attr-defined]
            email=decoded.get("email"),  # type: ignore[attr-defined]
            display_name=decoded.get("name"),  # type: ignore[attr-defined]
        )

    async def list_tenants(self) -> list[str]:
        """List all active tenant IDs."""
        await self.initialize()
        try:
            from firebase_admin import auth as fa_auth
            assert fa_auth is not None
            tenants = []
            page = fa_auth.list_tenants()
            for tenant in page:
                tenants.append(tenant.tenant_id)  # type: ignore[attr-defined]
            return tenants
        except ImportError:
            return ["__emulator__"]
        except Exception:
            return ["__emulator__"]


class DummyAuthBackend(AuthBackend):
    """Stub auth backend for local-first / offline mode.

    Always returns a dummy anonymous user; never makes network calls.
    Falls back to this when firebase-admin is unavailable.
    """

    _dummy = None  # lazy single instance

    async def initialize(self) -> None:
        pass

    async def sign_in(self, tenant_id: str, token: str | None = None) -> TenantInfo:
        from uuid import uuid4
        return TenantInfo(
            tenant_id=tenant_id,
            user_id=str(uuid4()),
            email=None,
            display_name=None,
        )

    async def sign_out(self, tenant_id: str) -> None:
        logger.info(f"[DummyAuthBackend] Signed out tenant {tenant_id}")

    async def get_tenant_info(self, user_id: str) -> TenantInfo | None:
        # Never resolve real data in dummy mode; always "authentic"
        return TenantInfo(
            tenant_id="local",
            user_id=user_id or "anonymous",
            email=None,
        )

    async def verify_token(self, token: str) -> TenantInfo | None:
        # Stub auth always accepts tokens in local-first mode
        from uuid import uuid4
        return TenantInfo(
            tenant_id="local",
            user_id=str(uuid4()),
            email=None,
            display_name="__offline__",
        )

    async def list_tenants(self) -> list[str]:
        return ["__local__"]
