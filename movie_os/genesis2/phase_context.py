"""Reusable per-phase context compilation for Genesis2.

This module compiles deterministic, dependency-driven context packets from:
- artifact registry entries
- canonical requirements
- active policy
- an established fact register

It preserves provenance on every included artifact reference and rejects any
compilation that would truncate mandatory information.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Iterable

from pydantic import BaseModel, Field, model_validator


class EstablishedFactRegister(BaseModel):
    """Structured register of facts established by authoritative artifacts."""

    facts: dict[str, dict[str, Any]] = Field(default_factory=dict)

    def add_fact(
        self,
        key: str,
        value: Any,
        *,
        source_artifact_id: str,
        source_content_hash: str,
        source_field: str,
    ) -> None:
        self.facts[key] = {
            "value": value,
            "source_artifact_id": source_artifact_id,
            "source_content_hash": source_content_hash,
            "source_field": source_field,
        }

    def materialize(self, keys: Iterable[str] | None = None) -> dict[str, Any]:
        if keys is None:
            return {key: item["value"] for key, item in self.facts.items()}
        return {key: self.facts[key]["value"] for key in keys if key in self.facts}


class ArtifactReference(BaseModel):
    artifact_id: str
    content_hash: str
    fields_or_fragments_consumed: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class DependencyManifest(BaseModel):
    phase_name: str
    required_artifact_ids: list[str] = Field(default_factory=list)
    required_fact_keys: list[str] = Field(default_factory=list)
    required_policy_keys: list[str] = Field(default_factory=list)


class RunContext(BaseModel):
    production_id: str
    run_id: str
    policy_id: str
    policy_hash: str
    requirement_manifest_hash: str
    mode: str = "RUNTIME"
    source_run_id: str = ""
    source_episode_id: str = ""


class PhaseContextPacket(BaseModel):
    phase_name: str
    packet_id: str
    episode_id: str = ""
    run_id: str = ""
    target_phase: str = ""
    target_unit: str = ""
    policy_hash: str = ""
    requirement_manifest_hash: str = ""
    mode: str = "RUNTIME"
    source_run_id: str = ""
    source_episode_id: str = ""
    dependency_manifest: DependencyManifest
    canonical_requirements: dict[str, Any]
    active_policy: dict[str, Any]
    established_facts: dict[str, Any]
    artifact_references: list[ArtifactReference] = Field(default_factory=list)
    context_size_chars: int = 0
    context_size_bytes: int = 0
    content_hash: str = ""


@dataclass(frozen=True)
class _ArtifactPayload:
    artifact_id: str
    content_hash: str
    payload: dict[str, Any]


class PhaseContextCompiler:
    """Compile a per-phase packet from authoritative sources only."""

    def __init__(self, max_context_chars: int = 12_000):
        self.max_context_chars = max_context_chars

    def compile(
        self,
        *,
        phase_name: str,
        target_unit: str | None = None,
        artifact_registry: dict[str, dict[str, Any]],
        canonical_requirements: dict[str, Any],
        active_policy: dict[str, Any],
        dependency_manifest: DependencyManifest,
        run_context: RunContext,
        established_fact_register: EstablishedFactRegister | None = None,
    ) -> PhaseContextPacket:
        established_fact_register = established_fact_register or EstablishedFactRegister()
        if run_context.production_id != active_policy.get("episode_id"):
            raise ValueError("CONTEXT_PACKET_PROVENANCE_MISMATCH: episode/run identity mismatch")
        target_unit = target_unit or dependency_manifest.phase_name
        selected = self._select_artifacts(artifact_registry, dependency_manifest)

        artifact_refs: list[ArtifactReference] = []
        artifact_payloads: list[dict[str, Any]] = []
        for artifact in selected:
            src_episode = str(artifact.payload.get("source_episode_id", ""))
            src_run = str(artifact.payload.get("source_run_id", ""))
            if src_episode and src_episode != run_context.production_id:
                raise ValueError("CONTEXT_PACKET_PROVENANCE_MISMATCH: source episode mismatch")
            if run_context.mode == "RUNTIME" and src_run and src_run != run_context.run_id:
                raise ValueError("CONTEXT_PACKET_PROVENANCE_MISMATCH: source run mismatch")
            consumed = self._infer_consumed_fields(artifact.payload, dependency_manifest)
            artifact_refs.append(
                ArtifactReference(
                    artifact_id=artifact.artifact_id,
                    content_hash=artifact.content_hash,
                    fields_or_fragments_consumed=consumed,
                    provenance=dict(artifact.payload.get("provenance", {})),
                )
            )
            artifact_payloads.append(
                {
                    "artifact_id": artifact.artifact_id,
                    "content_hash": artifact.content_hash,
                    "fields_or_fragments_consumed": consumed,
                    "provenance": dict(artifact.payload.get("provenance", {})),
                    "payload": self._trim_payload(artifact.payload, consumed),
                }
            )

        packet = PhaseContextPacket(
            phase_name=phase_name,
            packet_id=self._packet_id(phase_name, target_unit, canonical_requirements, active_policy, artifact_refs, run_context),
            episode_id=run_context.production_id,
            run_id=run_context.run_id,
            target_phase=phase_name,
            target_unit=target_unit,
            policy_hash=run_context.policy_hash,
            requirement_manifest_hash=run_context.requirement_manifest_hash,
            mode=run_context.mode,
            source_run_id=run_context.source_run_id,
            source_episode_id=run_context.source_episode_id,
            dependency_manifest=dependency_manifest,
            canonical_requirements=canonical_requirements,
            active_policy=active_policy,
            established_facts=established_fact_register.materialize(dependency_manifest.required_fact_keys),
            artifact_references=artifact_refs,
        )

        packed = {
            "phase_name": packet.phase_name,
            "episode_id": packet.episode_id,
            "run_id": packet.run_id,
            "target_phase": packet.target_phase,
            "target_unit": packet.target_unit,
            "policy_hash": packet.policy_hash,
            "requirement_manifest_hash": packet.requirement_manifest_hash,
            "mode": packet.mode,
            "source_run_id": packet.source_run_id,
            "source_episode_id": packet.source_episode_id,
            "dependency_manifest": packet.dependency_manifest.model_dump(),
            "canonical_requirements": canonical_requirements,
            "active_policy": active_policy,
            "established_facts": packet.established_facts,
            "artifact_references": [ref.model_dump() for ref in packet.artifact_references],
            "artifact_payloads": artifact_payloads,
        }
        packed_json = json.dumps(packed, sort_keys=True, separators=(",", ":"), default=str)
        if len(json.dumps(canonical_requirements, sort_keys=True, default=str)) > self.max_context_chars:
            raise ValueError("mandatory canonical requirements exceed context budget")
        if len(json.dumps(active_policy, sort_keys=True, default=str)) > self.max_context_chars:
            raise ValueError("mandatory active policy exceeds context budget")
        if len(json.dumps(packet.established_facts, sort_keys=True, default=str)) > self.max_context_chars:
            raise ValueError("mandatory established facts exceed context budget")
        if len(packed_json) > self.max_context_chars:
            raise ValueError("compilation would truncate mandatory information")

        packet.context_size_chars = len(packed_json)
        packet.context_size_bytes = len(packed_json.encode("utf-8"))
        packet.content_hash = hashlib.sha256(packed_json.encode("utf-8")).hexdigest()
        return packet

    def _select_artifacts(
        self,
        artifact_registry: dict[str, dict[str, Any]],
        dependency_manifest: DependencyManifest,
    ) -> list[_ArtifactPayload]:
        selected: list[_ArtifactPayload] = []
        for artifact_id in dependency_manifest.required_artifact_ids:
            if artifact_id not in artifact_registry:
                raise KeyError(f"missing required artifact: {artifact_id}")
            payload = artifact_registry[artifact_id]
            selected.append(
                _ArtifactPayload(
                    artifact_id=artifact_id,
                    content_hash=str(payload.get("content_hash", "")),
                    payload=payload,
                )
            )
        return selected

    def _infer_consumed_fields(self, artifact: dict[str, Any], dependency_manifest: DependencyManifest) -> list[str]:
        keys = dependency_manifest.required_fact_keys + dependency_manifest.required_policy_keys
        consumed: list[str] = []
        for key in keys:
            if key in artifact:
                consumed.append(key)
                continue
            for top_key, value in artifact.items():
                if isinstance(value, dict) and key in value:
                    consumed.append(key)
                    break
        if not consumed:
            consumed = [k for k in artifact.keys() if k not in {"artifact_id", "content_hash", "provenance"}]
        return consumed

    def _trim_payload(self, payload: dict[str, Any], consumed: list[str]) -> dict[str, Any]:
        trimmed: dict[str, Any] = {}
        for key in consumed:
            if key in payload:
                trimmed[key] = payload[key]
                continue
            for top_key, value in payload.items():
                if isinstance(value, dict) and key in value:
                    trimmed[key] = value[key]
                    break
        return trimmed

    def _packet_id(
        self,
        phase_name: str,
        target_unit: str,
        canonical_requirements: dict[str, Any],
        active_policy: dict[str, Any],
        artifact_refs: list[ArtifactReference],
        run_context: RunContext,
    ) -> str:
        seed = {
            "production_id": run_context.production_id,
            "run_id": run_context.run_id,
            "phase_name": phase_name,
            "target_unit": target_unit,
            "policy_hash": run_context.policy_hash,
            "requirement_manifest_hash": run_context.requirement_manifest_hash,
            "canonical_requirements": canonical_requirements,
            "active_policy": active_policy,
            "artifact_ids": [r.artifact_id for r in artifact_refs],
            "source_hashes": [r.content_hash for r in artifact_refs],
        }
        return hashlib.sha256(json.dumps(seed, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
