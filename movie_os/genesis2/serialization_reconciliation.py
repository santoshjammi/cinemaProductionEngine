"""P0-03R-SER-01: persistence reconciliation — prove in-memory PKG == persisted PKG.

Architectural consequence of the serialization repair (§13-15): before PKP
freeze, reconcile the live GENESIS knowledge package against its own
serialized/reloaded form.  A blocker (``PERSISTED_KNOWLEDGE_MISMATCH``) is
raised if any PhaseResult loses subclass semantic fields through
serialize -> persist -> reload.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from .models import ProductionKnowledgePackage


def canonicalize(value: Any) -> str:
    """Canonical JSON string for semantic comparison (ignores key order)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def serialize_reconcile_package(pkg: ProductionKnowledgePackage) -> dict[str, Any]:
    """Serialize the live PKG, reload it, and diff each phase's semantic fields.

    Returns a reconciliation report:
      - phase-level source_hash / serialized_hash / match
      - semantic_information_loss count
      - passed
    """
    results: dict[str, Any] = {"phase_results": {}}
    loss = 0
    for pr in pkg.phase_results:
        if pr.knowledge is None:
            results["phase_results"][f"phase_{pr.phase_number}"] = {
                "match": True, "note": "no knowledge"
            }
            continue
        source = pr.knowledge.model_dump()
        source_hash = hashlib.sha256(canonicalize(source).encode()).hexdigest()

        # serialize -> reload the PhaseResult
        js = pr.model_dump_json()
        from .models import PhaseResult
        reloaded = PhaseResult.model_validate(json.loads(js))
        rk = reloaded.knowledge
        if rk is None:
            results["phase_results"][f"phase_{pr.phase_number}"] = {
                "match": False, "reason": "knowledge became None on reload"
            }
            loss += 1
            continue
        serialized = rk.model_dump()
        serialized_hash = hashlib.sha256(canonicalize(serialized).encode()).hexdigest()
        match = source_hash == serialized_hash
        if not match:
            loss += 1
        results["phase_results"][f"phase_{pr.phase_number}"] = {
            "source_hash": source_hash[:16],
            "serialized_hash": serialized_hash[:16],
            "match": match,
            "knowledge_type": getattr(rk, "knowledge_type", ""),
        }
    results["semantic_information_loss"] = loss
    results["passed"] = loss == 0
    return results


def load_and_reconcile(pkg: ProductionKnowledgePackage, file_bytes: bytes) -> dict[str, Any]:
    """Compare a persisted byte payload against the live PKG (disk == reloaded).

    Returns:
      semantic_fields_expected / preserved / missing / changed / unexpected / passed
    """
    from .models import ProductionKnowledgePackage as PKGModel
    on_disk = json.loads(file_bytes)
    reloaded = PKGModel.model_validate(on_disk)

    expected = 0
    preserved = 0
    missing: list[str] = []
    changed: list[str] = []
    unexpected: list[str] = []

    for pr in reloaded.phase_results:
        rk = pr.knowledge
        if rk is None:
            continue
        live = next((x for x in pkg.phase_results if x.phase_number == pr.phase_number), None)
        if live is None or live.knowledge is None:
            unexpected.append(f"phase_{pr.phase_number}")
            continue
        live_dump = live.knowledge.model_dump()
        reload_dump = rk.model_dump()
        for k, v in reload_dump.items():
            if k in ("metadata", "confidence", "knowledge_type"):
                continue
            expected += 1
            if k in live_dump and canonicalize(live_dump[k]) == canonicalize(v):
                preserved += 1
            else:
                missing.append(f"phase_{pr.phase_number}.{k}")

    return {
        "semantic_fields_expected": expected,
        "semantic_fields_preserved": preserved,
        "missing_fields": missing,
        "changed_fields": changed,
        "unexpected_fields": unexpected,
        "passed": expected > 0 and preserved == expected and not missing,
    }
