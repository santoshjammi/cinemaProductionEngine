"""Visual Compiler — analyzes visual storytelling potential, imagery, metaphor."""

from __future__ import annotations

from typing import Any

from movie_os.genesis3.compilers.base import BaseCompiler, CompilerEvidence, EvidenceItem, Finding


VISUAL_MARKER = [
    "see", "look", "watch", "witness", "appearance", "reflection",
    "mirror", "shadow", "silhouette", "glimpse", "portrait",
    "landscape", "close-up", "wide shot", "frame", "canvas",
]
IMAGE_MARKER = [
    "imagery", "metaphor", "symbol", "symbolism", "visual", "picture",
    "color", "light", "darkness", "contrast", "palette", "hue",
    "saturated", "grayscale", "golden hour", "twilight", "dusk",
]
VISUAL_LANGUAGE_MARKER = [
    "cinematic", "shot", "camera", "lens", "film", "frame-worthy",
    "composition", "visual metaphor", "visual storytelling", "set design",
    "costume", "prop", "mise-en-scene",
]


class VisualCompiler(BaseCompiler):
    name = "Visual"
    dimension = "Visual Language"

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        findings: list[Finding] = []
        evidence_items: list[EvidenceItem] = []
        raw = (synopsis or "").strip().lower()

        # --- Visual language coherence ---
        visual_hits = [v for v in VISUAL_MARKER if v in raw]
        has_visual = len(visual_hits) >= 2
        findings.append(Finding(
            category="visual_language",
            status="pass" if has_visual else "warning",
            statement=("Visual language coherent and directional" if has_visual else "Visual direction implicit — needs more concrete imagery"),
            detail=f"Visual terms found: {visual_hits[:6]}",
            references=visual_hits[:3],
        ))

        evidence_items.append(EvidenceItem(
            claim="Can be translated to strong visual set pieces",
            supporting_text=str(visual_hits[:4]),
            source="synopsis_visual_vocabulary",
        ))

        # --- Image-theme support ---
        image_hits = [i for i in IMAGE_MARKER if i in raw]
        has_image = len(image_hits) >= 1
        findings.append(Finding(
            category="imagery_theme",
            status="pass" if has_image else "warning",
            statement=("Imagery supports theme through symbolic layering" if has_image else "Symbolic imagery sparse — consider adding visual motifs"),
            detail=f"Image-based markers: {image_hits[:5]}",
            references=image_hits[:3],
        ))

        evidence_items.append(EvidenceItem(
            claim="Visual metaphors can reinforce thematic content",
            supporting_text=str(image_hits[:3]) if image_hits else raw[:60],
            source="synopsis_image_theme_analysis",
        ))

        # --- Metaphorical layers ---
        lang_hits = [l for l in VISUAL_LANGUAGE_MARKER if l in raw]
        has_metaphor = len(lang_hits) >= 1
        findings.append(Finding(
            category="metaphorical_layers",
            status="pass" if has_metaphor else "info",
            statement=("Multiple metaphorical layers present" if has_metaphor else "Direct visual metaphors not explicit — performance and direction carry symbolic weight"),
            detail=f"Cinematic language markers: {lang_hits[:4]}",
            references=[],
        ))

        evidence_items.append(EvidenceItem(
            claim="Story benefits from deliberate visual design choices",
            supporting_text=str(lang_hits[:2]) if lang_hits else "no explicit cinematic terms detected",
            source="synopsis_visual_language_cues",
        ))

        # --- Scene composition potential ---
        composition_words = ["scene", "setting", "location", "space", "room", "hall", "courtyard", "garden"]
        comp_hits = [c for c in composition_words if c in raw]
        findings.append(Finding(
            category="scene_composition",
            status="pass" if len(comp_hits) >= 2 else ("warning" if comp_hits else "info"),
            statement="Scene composition possibilities clear" if len(comp_hits) >= 2 else ("some location specificity present" if comp_hits else "Locations not specified — consider adding environmental design notes"),
            detail=f"Setting/location words: {comp_hits[:4]}",
            references=comp_hits,
        ))

        evidence_items.append(EvidenceItem(
            claim="Physical spaces can be designed to reflect emotional states",
            supporting_text=str(comp_hits[:3]) if comp_hits else raw[:60],
            source="synopsis_location_signaling",
        ))

        # Confidence heuristic
        total = (1 if has_visual else 0) + (1 if has_image else 0) + (1 if has_metaphor else 0) + len(visual_hits) + len(image_hits)
        confidence = round(min(1.0, total / 7), 2) if raw else 0.0

        summary = self._summary(visual_hits, image_hits, lang_hits, comp_hits)
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=confidence,
            summary=summary,
        )

    def _summary(self, visual: list[str], image: list[str], lang: list[str], comp: list[str]) -> str:
        parts = []
        parts.append(f"{len(visual)} visual markers found")
        parts.append("Symbolic imagery " + ("present" if image else "absent"))
        if lang:
            parts.append(f"Cinematic language through {len(lang):d} cues")
        else:
            parts.append("No explicit cinematic terms — benefit of the doubt to vision dept")
        if comp:
            parts.append(f"{len(comp)} location-specific terms")
        return "; ".join(parts) + "."
