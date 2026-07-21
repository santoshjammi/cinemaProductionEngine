"""Production Knowledge Graph — the canonical knowledge store.

The PKG is the single source of truth for all pre-production knowledge.
It stores nodes (entities), edges (relationships), and specifications
(PKP-00 through PKP-18) in SQLite with an in-memory cache.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional

from .models import (
    ConfidenceLevel,
    KnowledgeEdge,
    KnowledgeNode,
    PKGState,
    Specification,
)


logger = logging.getLogger("movie_os.genesis.pkg")


SCHEMA = """
CREATE TABLE IF NOT EXISTS pkg_nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    label TEXT NOT NULL,
    properties TEXT DEFAULT '{}',
    confidence TEXT NOT NULL,
    created_at TEXT NOT NULL,
    provenance TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS pkg_edges (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    properties TEXT DEFAULT '{}',
    confidence TEXT NOT NULL,
    created_at TEXT NOT NULL,
    provenance TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS pkg_specs (
    spec_id TEXT PRIMARY KEY,
    spec_name TEXT NOT NULL,
    phase TEXT NOT NULL,
    content TEXT DEFAULT '{}',
    yaml_content TEXT DEFAULT '',
    markdown_content TEXT DEFAULT '',
    confidence TEXT NOT NULL,
    dependencies TEXT DEFAULT '[]',
    validation_status TEXT DEFAULT 'pending',
    validation_errors TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pkg_state (
    session_id TEXT PRIMARY KEY,
    synopsis TEXT DEFAULT '',
    constraints TEXT DEFAULT '{}',
    discovery_results TEXT DEFAULT '{}',
    questions TEXT DEFAULT '[]',
    completeness_scores TEXT DEFAULT '{}',
    overall_completeness REAL DEFAULT 0.0,
    current_stage TEXT DEFAULT 'init',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class ProductionKnowledgeGraph:
    """The canonical knowledge store for Genesis.

    For v1, uses SQLite with JSON serialization.
    For v2, can be swapped to Neo4j without changing the API.
    """

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self._state = PKGState()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.executescript(SCHEMA)
            self._conn.commit()
        return self._conn

    @property
    def state(self) -> PKGState:
        return self._state

    @property
    def synopsis(self) -> str:
        return self._state.synopsis

    @synopsis.setter
    def synopsis(self, value: str) -> None:
        self._state.synopsis = value

    @property
    def constraints(self) -> dict[str, Any]:
        return self._state.constraints

    @constraints.setter
    def constraints(self, value: dict[str, Any]) -> None:
        self._state.constraints = value

    # ------------------------------------------------------------------
    # Node operations
    # ------------------------------------------------------------------

    def add_node(self, node: KnowledgeNode) -> None:
        """Add a node to the graph."""
        self.conn.execute(
            """INSERT OR REPLACE INTO pkg_nodes
               (id, type, label, properties, confidence, created_at, provenance)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (node.id, node.type, node.label,
             json.dumps(node.properties), node.confidence.value,
             node.created_at, node.provenance),
        )
        self.conn.commit()
        self._state.nodes.append(node)

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""
        row = self.conn.execute(
            "SELECT * FROM pkg_nodes WHERE id = ?", (node_id,)
        ).fetchone()
        if row is None:
            return None
        return KnowledgeNode(
            id=row["id"], type=row["type"], label=row["label"],
            properties=json.loads(row["properties"]),
            confidence=ConfidenceLevel(row["confidence"]),
            created_at=row["created_at"], provenance=row["provenance"],
        )

    def get_nodes_by_type(self, node_type: str) -> list[KnowledgeNode]:
        """Get all nodes of a given type."""
        rows = self.conn.execute(
            "SELECT * FROM pkg_nodes WHERE type = ?", (node_type,)
        ).fetchall()
        return [
            KnowledgeNode(
                id=r["id"], type=r["type"], label=r["label"],
                properties=json.loads(r["properties"]),
                confidence=ConfidenceLevel(r["confidence"]),
                created_at=r["created_at"], provenance=r["provenance"],
            )
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Edge operations
    # ------------------------------------------------------------------

    def add_edge(self, edge: KnowledgeEdge) -> None:
        """Add an edge to the graph."""
        self.conn.execute(
            """INSERT OR REPLACE INTO pkg_edges
               (id, type, source_id, target_id, properties, confidence, created_at, provenance)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (edge.id, edge.type, edge.source_id, edge.target_id,
             json.dumps(edge.properties), edge.confidence.value,
             edge.created_at, edge.provenance),
        )
        self.conn.commit()
        self._state.edges.append(edge)

    def get_edges_from(self, node_id: str) -> list[KnowledgeEdge]:
        """Get all edges originating from a node."""
        rows = self.conn.execute(
            "SELECT * FROM pkg_edges WHERE source_id = ?", (node_id,)
        ).fetchall()
        return [self._row_to_edge(r) for r in rows]

    def get_edges_to(self, node_id: str) -> list[KnowledgeEdge]:
        """Get all edges pointing to a node."""
        rows = self.conn.execute(
            "SELECT * FROM pkg_edges WHERE target_id = ?", (node_id,)
        ).fetchall()
        return [self._row_to_edge(r) for r in rows]

    def _row_to_edge(self, row: sqlite3.Row) -> KnowledgeEdge:
        return KnowledgeEdge(
            id=row["id"], type=row["type"],
            source_id=row["source_id"], target_id=row["target_id"],
            properties=json.loads(row["properties"]),
            confidence=ConfidenceLevel(row["confidence"]),
            created_at=row["created_at"], provenance=row["provenance"],
        )

    # ------------------------------------------------------------------
    # Specification operations
    # ------------------------------------------------------------------

    def set_specification(self, spec: Specification) -> None:
        """Add or update a specification."""
        self.conn.execute(
            """INSERT OR REPLACE INTO pkg_specs
               (spec_id, spec_name, phase, content, yaml_content, markdown_content,
                confidence, dependencies, validation_status, validation_errors,
                created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (spec.spec_id, spec.spec_name, spec.phase,
             json.dumps(spec.content), spec.yaml_content, spec.markdown_content,
             spec.confidence.value, json.dumps(spec.dependencies),
             spec.validation_status, json.dumps(spec.validation_errors),
             spec.created_at, spec.updated_at),
        )
        self.conn.commit()
        self._state.specifications[spec.spec_id] = spec

    def get_specification(self, spec_id: str) -> Optional[Specification]:
        """Get a specification by ID (e.g. 'PKP-06')."""
        if spec_id in self._state.specifications:
            return self._state.specifications[spec_id]
        row = self.conn.execute(
            "SELECT * FROM pkg_specs WHERE spec_id = ?", (spec_id,)
        ).fetchone()
        if row is None:
            return None
        spec = Specification(
            spec_id=row["spec_id"], spec_name=row["spec_name"], phase=row["phase"],
            content=json.loads(row["content"]),
            yaml_content=row["yaml_content"],
            markdown_content=row["markdown_content"],
            confidence=ConfidenceLevel(row["confidence"]),
            dependencies=json.loads(row["dependencies"]),
            validation_status=row["validation_status"],
            validation_errors=json.loads(row["validation_errors"]),
            created_at=row["created_at"], updated_at=row["updated_at"],
        )
        self._state.specifications[spec_id] = spec
        return spec

    def get_all_specifications(self) -> dict[str, Specification]:
        """Get all specifications."""
        rows = self.conn.execute("SELECT spec_id FROM pkg_specs").fetchall()
        for row in rows:
            self.get_specification(row["spec_id"])
        return self._state.specifications

    def has_specification(self, spec_id: str) -> bool:
        """Check if a specification exists."""
        return self.get_specification(spec_id) is not None

    # ------------------------------------------------------------------
    # Discovery results
    # ------------------------------------------------------------------

    def set_discovery_result(self, key: str, value: Any) -> None:
        """Store a discovery result (e.g. 'intent_analysis', 'theme_analysis')."""
        self._state.discovery_results[key] = value

    def get_discovery_result(self, key: str) -> Optional[Any]:
        """Get a discovery result by key."""
        return self._state.discovery_results.get(key)

    def get_all_discovery_results(self) -> dict[str, Any]:
        """Get all discovery results."""
        return self._state.discovery_results

    # ------------------------------------------------------------------
    # Questions
    # ------------------------------------------------------------------

    def add_question(self, question: dict[str, Any]) -> None:
        """Add a question for the human creator."""
        self._state.questions.append(question)

    def get_questions(self) -> list[dict[str, Any]]:
        """Get all pending questions."""
        return self._state.questions

    def answer_question(self, index: int, answer: str) -> None:
        """Answer a question and remove it from pending."""
        if 0 <= index < len(self._state.questions):
            self._state.questions[index]["answer"] = answer
            self._state.questions[index]["answered"] = True

    # ------------------------------------------------------------------
    # Completeness
    # ------------------------------------------------------------------

    def set_completeness(self, domain: str, score: float) -> None:
        """Set the completeness score for a domain (0.0 to 1.0)."""
        self._state.completeness_scores[domain] = score
        scores = list(self._state.completeness_scores.values())
        self._state.overall_completeness = sum(scores) / len(scores) if scores else 0.0

    def get_overall_completeness(self) -> float:
        """Get the overall knowledge completeness score."""
        return self._state.overall_completeness

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Persist the current state to SQLite."""
        self.conn.execute(
            """INSERT OR REPLACE INTO pkg_state
               (session_id, synopsis, constraints, discovery_results, questions,
                completeness_scores, overall_completeness, current_stage,
                created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (self._state.session_id, self._state.synopsis,
             json.dumps(self._state.constraints),
             json.dumps(self._state.discovery_results),
             json.dumps(self._state.questions),
             json.dumps(self._state.completeness_scores),
             self._state.overall_completeness,
             self._state.current_stage,
             self._state.created_at, self._state.updated_at),
        )
        self.conn.commit()

    def load_state(self, session_id: str) -> bool:
        """Load a saved state by session ID. Returns True if found."""
        row = self.conn.execute(
            "SELECT * FROM pkg_state WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row is None:
            return False
        self._state = PKGState(
            session_id=row["session_id"],
            synopsis=row["synopsis"],
            constraints=json.loads(row["constraints"]),
            discovery_results=json.loads(row["discovery_results"]),
            questions=json.loads(row["questions"]),
            completeness_scores=json.loads(row["completeness_scores"]),
            overall_completeness=row["overall_completeness"],
            current_stage=row["current_stage"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        return True

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None