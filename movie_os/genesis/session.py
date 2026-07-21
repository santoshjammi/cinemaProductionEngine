"""Session Manager — manages Genesis production sessions.

Each Genesis run is a session. The session tracks:
- The synopsis and constraints
- The current stage (discovery, pkp, review, gate, complete)
- Checkpoint state for resume
- The PKG itself
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .pkg import ProductionKnowledgeGraph


logger = logging.getLogger("movie_os.genesis.session")


SESSION_SCHEMA = """
CREATE TABLE IF NOT EXISTS genesis_sessions (
    session_id TEXT PRIMARY KEY,
    synopsis TEXT NOT NULL,
    constraints TEXT DEFAULT '{}',
    stage TEXT DEFAULT 'init',
    pkg_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class SessionManager:
    """Manages Genesis production sessions with checkpointing."""

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.executescript(SESSION_SCHEMA)
            self._conn.commit()
        return self._conn

    def create_session(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
    ) -> str:
        """Create a new Genesis session. Returns the session ID."""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            """INSERT INTO genesis_sessions
               (session_id, synopsis, constraints, stage, pkg_path, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, synopsis, json.dumps(constraints or {}),
             "init", None, now, now),
        )
        self.conn.commit()
        logger.info(f"Created Genesis session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get session metadata."""
        row = self.conn.execute(
            "SELECT * FROM genesis_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "session_id": row["session_id"],
            "synopsis": row["synopsis"],
            "constraints": json.loads(row["constraints"]),
            "stage": row["stage"],
            "pkg_path": row["pkg_path"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def update_stage(self, session_id: str, stage: str) -> None:
        """Update the session stage."""
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "UPDATE genesis_sessions SET stage = ?, updated_at = ? WHERE session_id = ?",
            (stage, now, session_id),
        )
        self.conn.commit()

    def set_pkg_path(self, session_id: str, pkg_path: str) -> None:
        """Set the PKG database path for a session."""
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            "UPDATE genesis_sessions SET pkg_path = ?, updated_at = ? WHERE session_id = ?",
            (pkg_path, now, session_id),
        )
        self.conn.commit()

    def list_sessions(self) -> list[dict[str, Any]]:
        """List all sessions."""
        rows = self.conn.execute(
            "SELECT * FROM genesis_sessions ORDER BY created_at DESC"
        ).fetchall()
        return [
            {
                "session_id": r["session_id"],
                "synopsis": r["synopsis"][:100] + "..." if len(r["synopsis"]) > 100 else r["synopsis"],
                "stage": r["stage"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None