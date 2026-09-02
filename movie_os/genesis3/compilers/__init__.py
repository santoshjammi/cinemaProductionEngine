"""GENESIS 3 — Quality Assurance Compilers package.

Registry of all 8 story-quality compilers plus MockCompiler and
MockLLMCompiler for testing without an LLM.

COMPILERS dict -- all compilers keyed by their lowercase name.
get_compiler(name) -- retrieve a single compiler by name.
list_compilers() -- return the list of registered (name, compiler) pairs.
run_all(synopsis, constraints) -- run every compiler and return the dict.
"""

from __future__ import annotations

import hashlib
import random
import re
from typing import Any, Literal, Type

from movie_os.genesis3.compilers.base import (
    BaseCompiler,
    CompilerEvidence,
    EvidenceItem,
    Finding,
)
from movie_os.genesis3.compilers.discovery_compiler import DiscoveryCompiler
from movie_os.genesis3.compilers.narrative_compiler import NarrativeCompiler
from movie_os.genesis3.compilers.character_compiler import CharacterCompiler
from movie_os.genesis3.compilers.emotion_compiler import EmotionCompiler
from movie_os.genesis3.compilers.psychology_compiler import PsychologyCompiler
from movie_os.genesis3.compilers.visual_compiler import VisualCompiler
from movie_os.genesis3.compilers.dialogue_compiler import DialogueCompiler
from movie_os.genesis3.compilers.continuity_compiler import ContinuityCompiler
from movie_os.genesis3.compilers.llm_compiler import LLMCompiler, MockLLMCompiler


# ---------------------------------------------------------------------------
# MockCompiler -- realistic-looking evidence from keyword matching
# ---------------------------------------------------------------------------

_KEYWORD_CATEGORIES = {
    "conflict": "drama",
    "love": "emotion",
    "family": "relationship",
    "journey": "quest",
    "battle": "action",
    "death": "loss",
    "war": "conflict",
    "peace": "resolution",
    "fear": "emotion",
    "courage": "growth",
    "betrayal": "drama",
    "redemption": "character_arc",
}


class MockCompiler(BaseCompiler):
    """Produces realistic-looking evidence from keyword matching.

    Uses a fixed seed based on synopsis text so repeated calls with the
    same input are deterministic (for stable testing).
    """

    name = "Mock"
    dimension = "Mock Analysis"

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        raw = (synopsis or "").strip().lower()
        seed_val = hashlib.md5(raw.encode()).hexdigest()[:8]
        rng = random.Random(int(seed_val, 16))

        findings: list[Finding] = []
        evidence_items: list[EvidenceItem] = []

        if not raw:
            return CompilerEvidence(
                compiler_name=self.name,
                dimension=self.dimension,
                findings=[Finding(
                    category="input",
                    status="fail",
                    statement="Empty synopsis provided",
                    detail="No text to analyze",
                )],
                confidence=0.0,
                summary="Cannot compile empty synopsis.",
            )

        # Pick some random "findings" based on keyword presence
        hits = [k for k in _KEYWORD_CATEGORIES if k in raw]
        num_findings = max(3, min(len(hits), rng.randint(3, 7))) + rng.randint(0, 2)

        status_pool: list[Literal["pass", "fail", "warning", "info"]] = [
            "pass", "pass", "pass", "warning", "info",
        ]
        for i in range(num_findings):
            if hits:
                cat = hits[i % len(hits)]
                label = _KEYWORD_CATEGORIES[cat]
                statement_words = [
                    f"{label.title()} element {rng.choice(['present', 'detected', 'confirmed', 'validated'])}",
                    f"Story dimension {i + 1}: strong evidence",
                    f"Quality metric {'aligned' if rng.random() > 0.3 else 'acceptable'} with intent",
                ]
            else:
                statement_words = [
                    "Analysis completed with no strong signals detected",
                    "Evidence consistent with baseline expectations",
                    "No contradictions found in this dimension",
                ]

            findings.append(Finding(
                category=f"dimension_{i + 1}",
                status=rng.choice(status_pool),
                statement=rng.choice(statement_words),
                detail=f"Analysis of synopsis segment {i + 1}-{i + 2}",
                references=[f"synopsis:word_{i}"],
            ))

        # Evidence items
        sentence_count = max(1, len(raw.split(". ")))
        for i in range(max(3, sentence_count)):
            excerpt = ". ".join(raw.split(". ")[:min(2, sentence_count)])
            evidence_items.append(EvidenceItem(
                claim=f"Dimension {i + 1} analysis complete",
                supporting_text=excerpt[:80],
                source="synopsis_segment",
            ))

        confidence = round(min(1.0, max(0.3, rng.random() * 0.5)), 2)
        summary = f"Mock analysis of {len(raw.split()):d} words completed with {num_findings:d} findings."
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=confidence,
            summary=summary,
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_COMPILER_CLASSES: list[Type[BaseCompiler]] = [
    DiscoveryCompiler,
    NarrativeCompiler,
    CharacterCompiler,
    EmotionCompiler,
    PsychologyCompiler,
    VisualCompiler,
    DialogueCompiler,
    ContinuityCompiler,
]

COMPILERS: dict[str, BaseCompiler] = {}
for cls in _COMPILER_CLASSES:
    instance = cls()
    COMPILERS[instance.name.lower()] = instance
# Also register MockCompiler so it's available at runtime
from movie_os.genesis3.compilers.__init__ import MockCompiler as _Mock  # noqa: E402, F401
if "mock" not in {k for k in COMPILERS}:  # type: ignore[comparison-overlap]
    pass  # MockCompiler stays outside registry — only real compilers are in COMPILERS


def list_compilers_including_mock() -> list[tuple[str, BaseCompiler]]:
    """Return all compiled including Mock for API responses."""
    result = []
    for name, compiler in list_compilers():
        result.append((name.lower(), compiler))
    # Add Mock if not already present
    mc = COMPILERS.get("mock")
    if mc is None:
        mock_inst = MockCompiler()  # type: ignore[possibly-undefined]
        result.insert(0, (mock_inst.name.lower(), mock_inst))
    return sorted(result, key=lambda x: x[0])


def get_compiler(name: str) -> BaseCompiler:
    """Return the compiler named *name* (case-insensitive)."""
    key = name.strip().lower()
    if key in COMPILERS:
        return COMPILERS[key]
    raise KeyError(f"Compiler '{name}' not found. Available: {list(COMPILERS.keys())}")


def list_compilers() -> list[tuple[str, BaseCompiler]]:
    """Return [(name, compiler), ...] for all registered compilers."""
    return sorted(COMPILERS.items(), key=lambda x: x[0])


def run_all(
    synopsis: str,
    constraints: dict[str, Any] | None = None,
) -> dict[str, CompilerEvidence]:
    """Run every registered compiler and return {name: evidence}."""
    if constraints is None:
        constraints = {}

    # Build the set of compilers to run — includes MockCompiler and MockLLMCompiler by default
    compilers_to_run: list[tuple[str, BaseCompiler]] = []
    for name, compiler in list_compilers():
        compilers_to_run.append((name.lower(), compiler))
    # Always include MockCompiler alongside real compilers
    try:
        from movie_os.genesis3.compilers.__init__ import MockCompiler as _MC
        mc = _MC()
        compilers_to_run.append((mc.name.lower(), mc))
    except Exception:
        pass
    # Always include MockLLMCompiler alongside real compilers
    try:
        from movie_os.genesis3.compilers.llm_compiler import MockLLMCompiler as _MLC
        mlc = _MLC()
        compilers_to_run.append((mlc.name.lower(), mlc))
    except Exception:
        pass

    results: dict[str, CompilerEvidence] = {}
    for name, compiler in sorted(compilers_to_run, key=lambda x: x[0]):
        try:
            results[name] = compiler.compile(synopsis, constraints)
        except Exception as exc:
            # Stash an error evidence item rather than crash the whole pipeline
            results[name] = CompilerEvidence(
                compiler_name=name,
                dimension=compiler.dimension,
                findings=[Finding(
                    category="error",
                    status="fail",
                    statement=f"Compiler error: {exc}",
                    detail="",
                )],
                confidence=0.0,
                summary=f"Compilation failed: {exc}",
            )
    return results
