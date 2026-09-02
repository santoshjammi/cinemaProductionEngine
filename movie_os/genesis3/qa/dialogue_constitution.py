"""Dialogue Constitution - evaluates authenticity, subtext, character voice, plot advancement."""

from __future__ import annotations

from typing import Any, Dict, List, Literal
from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, StandardCheck


class DialogueConstitution(BaseConstitution):
    name = "dialogue"
    standards = [
        "authenticity",
        "subtext_presence",
        "character_voice_distinctiveness",
        "plot_advancement",
    ]

    _THRESHOLD_PASS = 0.7
    _THRESHOLD_CONDITIONAL = 0.4

    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        checked: List[StandardCheck] = []
        dialogue_data = evidence.get("dialogue", {})
        lines = dialogue_data.get("lines", [])
        total_lines = len(lines)

        # --- authenticity ---
        natural_phrasing_count = 0
        cliches_found = 0
        for line in lines:
            if isinstance(line, dict):
                if not line.get("is_cliche", False):
                    natural_phrasing_count += 1
                if line.get("cliche_detected"):
                    cliches_found += int(1)

        authenticity_score_val = max(natural_phrasing_count / max(total_lines, 1) - (cliches_found * 0.1), 0.0)
        checked.append(StandardCheck(
            standard_name="authenticity",
            status=self._s(authenticity_score_val), score=round(authenticity_score_val, 4),
            evidence_used=[str(f"natural_phrases={natural_phrasing_count}"), str(f"cliches={cliches_found}")],
            reasoning="Dialogue must sound natural for the character and setting, avoiding cliches.",
            failure_reasons=[] if authenticity_score_val >= self._THRESHOLD_PASS else [
                f"{cliches_found} cliche(s) detected"
            ],
        ))

        # --- subtext_presence ---
        has_implied_meaning = any(
            isinstance(l, dict) and l.get("has_subtext") for l in lines
        )
        double_talk_count = sum(1 for l in lines if isinstance(l, dict) and l.get("double_talk"))
        subtext_score_val = (0.5 if has_implied_meaning else 0.0) + \
                            (0.3 if double_talk_count > 0 else 0.0) + \
                            (0.2 if total_lines > 0 and any(
                                isinstance(l, dict) and l.get("context_aware") for l in lines
                            ) else 0.0)

        checked.append(StandardCheck(
            standard_name="subtext_presence",
            status=self._s(subtext_score_val), score=round(subtext_score_val, 4),
            evidence_used=[str(f"subtext_lines={double_talk_count}"), "has_implied_meaning" if has_implied_meaning else "no_subtext"],
            reasoning="Good dialogue communicates beneath the surface — emotions and intentions lurk below.",
            failure_reasons=[] if subtext_score_val >= self._THRESHOLD_PASS else ["Dialogue too literal on the surface"],
        ))

        # --- character_voice_distinctiveness ---
        voices = {}
        for line in lines:
            if isinstance(line, dict):
                speaker = line.get("speaker", "unknown")
                vocab_set = frozenset(str(line.get("words", [])).lower().split())
                if speaker not in voices:
                    voices[speaker] = set()
                voices[speaker].update(vocab_set)

        distinct_scores = []
        speakers_list = list(voices.keys())
        for i, s1 in enumerate(speakers_list):
            for s2 in speakers_list[i+1:]:
                overlap = len(voices[s1] & voices[s2]) / max(len(voices[s1] | voices[s2]), 1)
                distinct_scores.append(1 - overlap)

        avg_distinctness = sum(distinct_scores) / max(len(distinct_scores), 1) if speakers_list else 0.5
        voice_score_val = avg_distinctness * 0.6 + (0.4 if len(speakers_list) >= 2 else 0.0)

        checked.append(StandardCheck(
            standard_name="character_voice_distinctiveness",
            status=self._s(voice_score_val), score=round(voice_score_val, 4),
            evidence_used=[str(f"speakers={len(speakers_list)}"), str(f"distinctness={avg_distinctness:.2f}")],
            reasoning="Each character must have a unique linguistic fingerprint — vocab, rhythm, phrasing.",
            failure_reasons=[] if voice_score_val >= self._THRESHOLD_PASS else ["Voices not sufficiently distinct"],
        ))

        # --- plot_advancement ---
        advances_plot = any(
            isinstance(l, dict) and l.get("advances_plot") for l in lines
        )
        reveals_character = any(
            isinstance(l, dict) and l.get("reveals_character") for l in lines
        )
        carries_scene_weight = bool(dialogue_data.get("scene_weight_score", 0.5)) >= 0.4

        plot_score_val = (0.35 if advances_plot else 0.0) + \
                         (0.35 if reveals_character else 0.0) + \
                         (0.3 if carries_scene_weight else 0.0)

        checked.append(StandardCheck(
            standard_name="plot_advancement",
            status=self._s(plot_score_val), score=round(plot_score_val, 4),
            evidence_used=["advances" if advances_plot else "static", "reveals" if reveals_character else "exposes"],
            reasoning="Dialogue must drive the scene forward — reveal character or move plot.",
            failure_reasons=[] if plot_score_val >= self._THRESHOLD_PASS else ["Dialogue is decorative not functional"],
        ))

        status, overall, summary, recs = self._aggregate(checked)
        return ConstitutionReview(
            constitution_name=self.name, status=status,
            standards_checked=checked, overall_score=overall,
            summary=summary, recommendations=recs,
        )

    def _s(self: "DialogueConstitution", score: float) -> Literal["PASS", "FAIL", "CONDITIONAL"]:
        if score >= self._THRESHOLD_PASS:
            return "PASS"
        if score >= self._THRESHOLD_CONDITIONAL:
            return "CONDITIONAL"
        return "FAIL"
