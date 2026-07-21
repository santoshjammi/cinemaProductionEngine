"""Genesis data models — Pydantic models for the Production Knowledge Graph."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    """Five-level knowledge confidence classification."""
    EXPLICIT = "explicit"      # Directly stated in synopsis
    INFERRED = "inferred"      # Strongly implied (>80% confidence)
    CONFIRMED = "confirmed"     # Validated by cross-checking
    ASSUMED = "assumed"         # Reasonable default (40-80% confidence)
    UNKNOWN = "unknown"         # Cannot determine (<40% confidence)


class KnowledgeNode(BaseModel):
    """A node in the Production Knowledge Graph."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str                          # e.g. "character", "scene", "theme"
    label: str                         # Human-readable name
    properties: dict[str, Any] = Field(default_factory=dict)
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    provenance: str = ""               # Which agent created this node


class KnowledgeEdge(BaseModel):
    """An edge in the Production Knowledge Graph."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str                          # e.g. "precedes", "causes", "depends_on"
    source_id: str
    target_id: str
    properties: dict[str, Any] = Field(default_factory=dict)
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    provenance: str = ""


class Specification(BaseModel):
    """A single PKP specification (PKP-00 through PKP-18)."""
    spec_id: str                       # e.g. "PKP-06"
    spec_name: str                     # e.g. "Character Specification"
    phase: str                         # e.g. "C", "A", "G"
    content: dict[str, Any] = Field(default_factory=dict)
    yaml_content: str = ""             # Serialized YAML
    markdown_content: str = ""         # Serialized Markdown
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    dependencies: list[str] = Field(default_factory=list)
    validation_status: str = "pending"  # pending, passed, failed
    validation_errors: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PKGState(BaseModel):
    """The complete state of a Production Knowledge Graph."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    synopsis: str = ""
    constraints: dict[str, Any] = Field(default_factory=dict)
    nodes: list[KnowledgeNode] = Field(default_factory=list)
    edges: list[KnowledgeEdge] = Field(default_factory=list)
    specifications: dict[str, Specification] = Field(default_factory=dict)
    discovery_results: dict[str, Any] = Field(default_factory=dict)
    questions: list[dict[str, Any]] = Field(default_factory=list)
    completeness_scores: dict[str, float] = Field(default_factory=dict)
    overall_completeness: float = 0.0
    current_stage: str = "init"        # init, discovery, pkp, review, gate, complete
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentResult(BaseModel):
    """Result of a single agent execution."""
    agent_name: str
    spec_id: str = ""
    status: str = "success"            # success, failed, skipped, revision_needed
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    errors: list[str] = Field(default_factory=list)
    questions: list[dict[str, Any]] = Field(default_factory=list)
    output: dict[str, Any] = Field(default_factory=dict)