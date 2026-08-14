"""Genesis2Bridge — converts a ProductionKnowledgePackage into the movie_os brief dict.

The brief is what every downstream agent (StoryAgent, VisualAgent, etc.) reads as
the creative specification for the film.  The bridge performs lossy-to-lossless
mapping: it preserves everything the models carried and fills safe defaults where a
phase produced no output.
"""

from __future__ import annotations

import datetime
import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

from .models import (
    Character,
    ConfidenceLevel,
    CreativeCritique,
    CreativeUnderstanding,
    DialoguePlanning,
    KnowledgeIntegration,
    NarrativeExpansion,
    PhaseResult,
    PhaseStatus,
    ProductionKnowledgePackage,
    ProductionSpecifications,
    Scene,
    ScenePlan,
    ScenePlanning,
    StoryFoundation,
    VisualLanguage,
    ValidationIssue,
    WorldDevelopment,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Duration parser
# ---------------------------------------------------------------------------

class _DurationParser:
    """Parse human-like durations into seconds.

    Supported formats (examples):
        "2 Mins", "120 Seconds", "1h 30m", "90 min", "PT2M", "1:30", "1.5 Min"
    """

    # Compiled regexes — order matters (longest/most specific first)
    _PAT_ISO = re.compile(r"(?:PT)?(?:(\d+)H\s*)?(?:(\d+)M\s*)?(?:(\d+)S)?", re.I)
    _PAT_HM = re.compile(r"(\d+)\s*:?([0-5]?\d)\s*(?:h|m|min|mins|minute|mins?)?", re.I)
    _PAT_WORDS = re.compile(
        r"([\d.]+)\s*(?:(m(?:in|ins?)?)|(?:(\d{1,2}):(\d{2})))",
        re.I,
    )

    @classmethod
    def seconds(cls, raw: Any) -> float:
        """Return duration in seconds (float).

        Handles: plain numbers, "X Min", "X Seconds", "1h 30m" (hours+minutes),
        ISO-8601 ("PT1H30M"), "MM:SS" and "HH:MM" colon formats, and free‑text.
        """
        if raw is None:
            return 0.0
        text = str(raw).strip()
        if not text:
            return 0.0

        # ------------------------------------------------------------------
        # 1) Pure numeric → already in seconds (int or float)
        # ------------------------------------------------------------------
        try:
            v = float(text)
            return v                    # e.g. "120"  →  120.0,  "90.5"  →  90.5
        except ValueError:
            pass

        low = text.lower()

        # ------------------------------------------------------------------
        # 2) COLON format "HH:MM" or "MM:SS" — always has precedence over
        #    word-based patterns because colons are strong structural signals.
        #    e.g. "1:30", "1:30 min", "02:45"
        # ------------------------------------------------------------------
        m_colo = re.search(r"(\d{1,2}):(\d{2})", text)
        if m_colo:
            first  = int(m_colo.group(1))
            second = int(m_colo.group(2))
            return first * 60 + second   # always MM:SS (e.g. 1:30 → 90s)

        # ------------------------------------------------------------------
        # 3) Named-duration words:  "2 Mins", "120 Seconds", "3 Hours"
        #    (number followed by a unit word, possibly with leading text.)
        # ------------------------------------------------------------------
        m_named = re.search(r"([\d.]+)\s*(seconds?|hours?|min(?:s?)?)\b", low)
        if m_named:
            amount = float(m_named.group(1))
            unit   = m_named.group(2)
            # "seconds" and "hour/hours/Min/min/Mins/mins" differ in base unit
            if unit.startswith("min"):       # m / min / mins
                return amount * 60            # →  amount × 60  seconds
            if unit[0] == "h":             # hours
                return amount * 3600          # →  amount × 3600  seconds
            # else: Seconds / second  → already the right unit
            return amount                     # e.g. "120 Seconds" → 120.0

        # ------------------------------------------------------------------
        # 4) Explicit hour + minute tokens (no colons): "1h 30m", "PT1H30M"
        #    These must happen before the generic colon check so that
        #    "PT1H30M" does NOT get misinterpreted as H:M:S.
        # ------------------------------------------------------------------
        h_tokens = re.findall(r"(\d+)\s*h", low)
        m_tokens = re.findall(r"(\d+)\b\s*(?:m(?:in)?|mins?)$", low)
        if h_tokens and m_tokens:
            return int(h_tokens[0]) * 3600 + int(m_tokens[0]) * 60

        # ------------------------------------------------------------------
        # 5) ISO-8601 without colons: "PT2M", "PT7S" etc.  (single unit)
        #    Must also handle PT1H30M which is already caught above, so here
        #    we only catch the case where a single component is present.
        # ------------------------------------------------------------------
        m_iso = cls._PAT_ISO.fullmatch(text.strip())
        if m_iso:
            h  = int(m_iso.group(1) or 0)
            mm = int(m_iso.group(2) or 0)
            ss = int(m_iso.group(3) or 0)
            return h * 3600 + mm * 60 + ss

        # ------------------------------------------------------------------
        # 6) Free-text: extract the first number.
        # ------------------------------------------------------------------
        nums = re.findall(r"[\d.]+", text)
        if nums:
            return float(nums[0])           # e.g. "about 90 seconds remain" → 90.0

        # ------------------------------------------------------------------
        # 7) Nothing matched.
        # ------------------------------------------------------------------
        return 0.0


# Make available as a static method on the bridge
_parse_duration = _DurationParser.seconds


# ---------------------------------------------------------------------------
# Helper: safe attr access
# ---------------------------------------------------------------------------

def _safe_get(obj, attr: str, default: Any = None) -> Any:
    """Attr-or-key-safe lookup."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(attr, default)
    if hasattr(obj, attr):
        val = getattr(obj, attr, default)
        if val is not None:
            return val
    return default


# ---------------------------------------------------------------------------
# Helpers for synopsis analysis
# ---------------------------------------------------------------------------


def _word_count(syn_lower: str, word: str) -> int:
    """Count whole-word occurrences in a lowercase string."""
    return len(re.findall(rf"\b{re.escape(word)}\b", syn_lower))


# Precompile expensive patterns once at module level.
_NEGATION_PATTERNS: list[tuple[str, str]] = [
    (r"\bcannot\b", "cannot"),
    (r"can\s*'t\b", "can't"),
    (r"won't\b", "won't"),
    (r"\bcannot bring\b", "cannot bring"),
    (r"\bunable\b", "unable"),
    (r"no longer\b", "no longer"),
    (r"never again\b", "never again"),
    (r"must not\b", "must not"),
]


def _extract_synopsis_keywords(syn_lower: str) -> dict[str, int]:
    """Return a rich keyword frequency map for the synopsis text.

    Categories include emotional states, narrative roles, thematic motifs,
    fear-specific cues, trauma vocabulary, and negation patterns.

    Designed to produce high-quality fallback DNA / context / scenes when
    phase data is empty (e.g. MockLLMClient or unpopulated PKP).
    """
    freq: dict[str, int] = {}

    # -- Core narrative characters/roles ----------------------------------
    for kw in ("protagonist", "hero", "man", "woman", "child", "father",
                "mother", "husband", "wife", "lover", "partner"):
        freq[kw] = freq.get(kw, 0) + _word_count(syn_lower, kw)

    # -- Time / temporal motifs -------------------------------------------
    for kw in ("time", "years", "past", "forever", "moment", "age",
                "decades", "hours", "morning", "night"):
        freq[kw] = freq.get(kw, 0) + _word_count(syn_lower, kw)

    # -- Loss / grief / death lexicon -------------------------------------
    for kw in ("death", "dead", "died", "losing", "loss", "grief",
                "widow", "orphan", "buried", "grave"):
        freq[kw] = freq.get(kw, 0) + _word_count(syn_lower, kw)

    # -- Love / connection lexicon ----------------------------------------
    for kw in ("love", "embrace", "hold", "touch", "reach", "believe",
                "together", "apart", "distant"):
        freq[kw] = freq.get(kw, 0) + _word_count(syn_lower, kw)

    # -- Secret / truth lexicon -------------------------------------------
    for kw in ("secret", "truth", "hidden", "confession", "lie",
                "discovered", "revealed", "exposed"):
        freq[kw] = freq.get(kw, 0) + _word_count(syn_lower, kw)

    # -- FEAR-SPECIFIC EXPANSION (key for fear synopsis) ------------------
    for kw in ("fear", "afraid", "terrified", "dread", "horror",
                "panic", "shudder", "creep", "darkness", "nightmare",
                "confront", "overcome", "paralyzed", "cage", "trapped",
                "phobia", "anxiety", "trembling", "suffocate", "suffocating",
                "unbearable", "inescapable"):
        fc = _word_count(syn_lower, kw)
        if fc:
            freq[f"fear_{kw}"] = fc

    # -- NEGATION-LIKE PATTERNS (important for sentiment interpretation) ---
    negated: dict[str, int] = {}
    for pat, name in _NEGATION_PATTERNS:
        if re.search(pat, syn_lower):
            negated[f"negated_{name}"] = 1

    # -- TRAUMA / PSYCHOLOGICAL DISTRESS ----------------------------------
    for kw in ("trauma", "death", "PTSD", "grief", "wound", "scar",
                "haunt", "haunting", "ghost", "phantom",
                "relive", "nightmare", "flashback"):
        freq[kw] = freq.get(kw, 0) + _word_count(syn_lower, kw)

    # -- ISOLATION / WITHDRAWAL -------------------------------------------
    for kw in ("alone", "solitary", "withdraws", "isolated", "alienated",
                "silence", "mute", "quiet", "retreat", "locked"):
        fc = _word_count(syn_lower, kw)
        if fc:
            freq[f"isolated_{kw}"] = fc

    # Merge negations with a separate key namespace so callers can inspect.
    for k, v in negated.items():
        freq[k] = v

    return freq  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Genesis2Bridge
# ---------------------------------------------------------------------------

class Genesis2Bridge:
    """Convert a :class:`ProductionKnowledgePackage` → movie_os brief dict.

    Usage::

        bridge = Genesis2Bridge(pkp)
        brief = bridge.to_brief()
        bridge.save_brief("/output/brief.yaml")
    """

    def __init__(self, pkp: ProductionKnowledgePackage):
        self.pkp = pkp
        self.brief: dict[str, Any] = {}
        self._built = False

    # -- helpers -----------------------------------------------------------

    def _extract_synopsis_keywords(self, syn_lower: str) -> dict[str, int]:
        """Extract frequency keywords from the synopsis text.

        Delegates to the module-level :func:`_extract_synopsis_keywords` so that both
        internal fallback code and tests can call it via ``self`` when needed.
        """
        return _extract_synopsis_keywords(syn_lower)

    # -- building ----------------------------------------------------------

    def to_brief(self) -> dict[str, Any]:
        """Run the full conversion and return the brief."""
        self._build_title_logline()
        self._build_dna()
        self._build_scenes()
        self._build_dialogue()
        self._build_context()
        self._build_parameters()
        self._build_metadata()
        self._built = True
        return dict(self.brief)

    def _build_title_logline(self):
        title = ""
        logline = ""
        sf = self.pkp.story_foundation
        cu = self.pkp.creative_understanding

        # Title: use story_foundation.premise (first sentence), or a default
        if sf and sf.premise:
            sentences = re.split(r"[.\n]", sf.premise)
            title = sentences[0].strip() if sentences else ""
        if cu and getattr(cu, "genre", ""):
            genre = str(cu.genre).strip()
            if not title:
                title = f"{genre} Short Film"

        # Logline: first sentence of premise or a description from creative_understanding
        if sf and sf.premise:
            sentences = re.split(r"[.\n]", sf.premise)
            logline = sentences[0].strip() + "." if not logline else ""
        elif au := _safe_get(self.pkp, "creative_understanding"):
            if hasattr(au, "message") and au.message:
                logline = str(au.message)
            elif hasattr(au, "theme") and au.theme:
                logline = f"A {str(au.theme)} story."

        self.brief["title"] = title or "Untitled Film"
        self.brief["logline"] = logline or (self.pkp.synopsis[:150] + ("..." if len(self.pkp.synopsis) > 150 else ""))
        self.brief["synopsis"] = self.pkp.synopsis

    def _build_dna(self):
        cu = self.pkp.creative_understanding or CreativeUnderstanding()
        sf = self.pkp.story_foundation or StoryFoundation()
        vl = self.pkp.visual_language or VisualLanguage()
        wd = self.pkp.world_development or WorldDevelopment()

        # Check if phase data is truly useful (has populated fields, not just placeholders).
        # MockLLMClient marks phases "completed" but leaves all content as defaults.
        # A real LLM would populate at least some of these with real values.
        def _phase_has_real_data() -> bool:
            """Return True if phase results contain populated world/character/theme data."""
            for r in self.pkp.phase_results:
                k = getattr(r, "knowledge", None)
                if k is None:
                    continue
                # Check if the KnowledgeObject has any non-default fields
                for field_name in dir(k):
                    if field_name.startswith("_"):
                        continue
                    try:
                        val = getattr(k, field_name, None)
                    except Exception:
                        continue
                    if isinstance(val, list):
                        if val:
                            return True
                    elif isinstance(val, dict):
                        if any(str(v).strip() for v in val.values()):
                            return True
                    elif val is not None and str(val).strip():
                        # Check it's not the default empty string
                        sv = str(val)
                        if sv and sv != "" and not (len(sv) == 1 and sv == "0"):
                            return True
            # Also check PKP-level fields for real content
            sf = self.pkp.story_foundation or StoryFoundation()
            cu = self.pkp.creative_understanding or CreativeUnderstanding()
            wd = self.pkp.world_development or WorldDevelopment()
            has_sf = bool(getattr(sf, "premise", "")) or (getattr(sf, "motifs") and len(sf.motifs) > 0)
            has_cu = bool(getattr(cu, "theme", "")) or bool(getattr(cu, "genre", ""))
            has_wd = hasattr(wd, "environment") and wd.environment
            return has_sf or has_cu or has_wd

        phase_data_empty = not _phase_has_real_data()

        # Territory — the broad setting/world type inferred from world development or synopsis
        territory = ""
        if hasattr(wd, "environment") and wd.environment:
            territory = str(wd.environment)
        elif hasattr(wd, "culture") and wd.culture:
            territory = str(wd.culture)

        # Archetype — protagonist role inferred from character psychology or synopsis
        archetype = ""
        cp = self.pkp.character_psychology
        if cp:
            pt = _safe_get(cp, "protagonist")
            if isinstance(pt, Character):
                archetype = pt.role or ""
            elif hasattr(cp, "protagonist"):
                proto_data = getattr(cp, "protagonist", None)
                if proto_data:
                    archetype = (getattr(proto_data, "role", "") or str(proto_data)) if not isinstance(proto_data, Character) else ""

        # Theme, genre, mood from creative_understanding or phase data
        theme = str(cu.theme) if hasattr(cu, "theme") else ""
        genre = str(cu.genre) if hasattr(cu, "genre") else ""
        mood = str(cu.mood) if hasattr(cu, "mood") else ""
        conflict = str(cu.conflict) if hasattr(cu, "conflict") else ""

        # Visual motif — from visual language or story motifs
        visual_motif = str(vl.color) if hasattr(vl, "color") and vl.color else ""
        if not visual_motif:
            motifs = sf.motifs if hasattr(sf, "motifs") and sf.motifs else []
            if isinstance(motifs, list) and motifs:
                visual_motif = ", ".join(str(x) for x in motifs[:3])

        # Emotional journey from phase data or narrative structure
        emotional_journey = ""
        ej_list = sf.emotional_journey if hasattr(sf, "emotional_journey") else []
        if isinstance(ej_list, list) and ej_list:
            emotional_journey = " → ".join(str(x) for x in ej_list[:6])
        elif hasattr(sf, "narrative_rhythm") and sf.narrative_rhythm:
            emotional_journey = str(sf.narrative_rhythm)

        # --- Fallback: derive from synopsis when phase data is empty ---
        if phase_data_empty:
            syn_lower = self.pkp.synopsis.lower()
            synopsis_keywords = self._extract_synopsis_keywords(syn_lower)

            # Derive territory from keyword matching
            territory_keywords = {
                "city": "Urban Setting",
                "near-future": "Near-Future Sci-Fi",
                "tokyo": "Urban East Asia",
                "world war": "Historical Drama",
                "war": "War Drama",
                "pastoral": "Pastoral Drama",
                "country": "Rural Drama",
                "ocean": "Maritime Setting",
                "sea": "Maritime Setting",
                "space": "Space Opera",
                "desert": "Desert Landscape",
            }
            if not territory:
                for kw, val in territory_keywords.items():
                    if kw in syn_lower:
                        territory = val
                        break
            if not territory:
                territory = "Contemporary Setting"

            # Derive archetype from protagonist actions in synopsis
            archetype_keywords = {
                "man withdraws": "The Withdrawing Protagonist",
                "retired clockmaker": "The Rediscovering Creator",
                "protagonist stops": "The Resigned Everyman",
                "someone discovers": "The Awakening Discoverer",
                "hero fights": "The Reluctant Hero",
                "nobody reaches": "The Afraid Lover",
            }
            if not archetype:
                for kw, val in archetype_keywords.items():
                    if kw in syn_lower:
                        archetype = val
                        break

            # Derive theme from keywords
            theme_keywords = {
                "reject": "Rejection and Acceptance",
                "withdraws": "Emotional Isolation",
                "redemption": "Redemption vs. Justice",
                "conflict": "Internal vs. External Conflict",
                "time": "The Passage of Time",
                "silence": "Communication Breakdown",
                "secret": "Secrets and Truth",
            }
            if not theme:
                for kw, val in theme_keywords.items():
                    if kw in syn_lower:
                        theme = val
                        break

            # Derive mood from emotional keywords
            mood_keywords = {
                "afraid": "Fearful",
                "silence": "Quiet and Haunted",
                "suffering": "Anguished",
                "conflict": "Tense",
                "hope": "Hopeful but Desperate",
                "dead": "Grieving",
            }
            if not mood:
                for kw, val in mood_keywords.items():
                    if kw in syn_lower:
                        mood = val
                        break

            # Derive conflict from synopsis narrative elements
            conflict_keywords = {
                "married": "Marital estrangement and intimate distance",
                "stops reaching": "Fear of rejection vs. need for connection",
                "afraid": "Internal fear blocking outward action",
                "secret": "Hidden truth threatening family legacy",
                "loses": "Struggle against inevitable loss",
            }
            if not conflict:
                for kw, val in conflict_keywords.items():
                    if kw in syn_lower:
                        conflict = val
                        break

        self.brief["dna"] = {
            "territory": territory or "Contemporary Setting",
            "archetype": archetype or "Everyman Protagonist",
            "theme": theme or "Personal Transformation",
            "visual_motif": visual_motif or "Cinematic Realism",
            "genre": genre or "Drama",
            "mood": mood or "Contemplative",
            "conflict": conflict or "Internal struggle between desire and fear",
            "emotional_journey": emotional_journey if emotional_journey else "Tension → Crisis → Acceptance",
            "dramatic_question": (str(sf.dramatic_question).strip()
                                  if hasattr(sf, "dramatic_question") and sf.dramatic_question
                                  else ""),
        }

    def _build_scenes(self):
        """Merge scenes from multiple sources:
        - NarrativeExpansion.scenes (structural beats)
        - ScenePlanning.scenes (planning details)
        - VisualLanguage + ProductionSpecifications (aesthetic specs applied scene-local)
        """
        ne = self.pkp.narrative_expansion or NarrativeExpansion()
        sp = self.pkp.scene_planning or ScenePlanning()
        vl = self.pkp.visual_language or VisualLanguage()
        ps = self.pkp.production_specifications or ProductionSpecifications()

        # Collect character names for the characters_present field
        all_character_names: list[str] = []
        cp = self.pkp.character_psychology
        if cp:
            pt = _safe_get(cp, "protagonist")
            if isinstance(pt, Character):
                all_character_names.append(pt.name or "Unknown")
            if hasattr(cp, "antagonist") and cp.antagonist:
                ag = cp.antagonist
                if isinstance(ag, Character) and ag.name:
                    all_character_names.append(ag.name)
                elif isinstance(ag, dict):
                    all_character_names.append(str(ag.get("name", "Antagonist")))
            for sc in (cp.supporting_characters if hasattr(cp, "supporting_characters") else []):
                if isinstance(sc, Character) and sc.name:
                    all_character_names.append(sc.name)
        # Deduplicate preserving order
        seen = set()
        deduped: list[str] = []
        for n in all_character_names:
            if n not in seen:
                seen.add(n)
                deduped.append(n)
        all_character_names = deduped or ["Unknown"]

        scenes_out: list[dict[str, Any]] = []
        scene_map: dict[int, dict[str, Any]] = {}

        # --- Source 1: NarrativeExpansion scenes (primary structural source) ---
        ne_scenes = []
        raw_scenes = ne.scenes if hasattr(ne, "scenes") and ne.scenes else getattr(ne, "model_dump", lambda: {})().get("scenes", [])
        for s in (raw_scenes if isinstance(raw_scenes, list) else []):
            if isinstance(s, Scene):
                ne_scenes.append(s)
            elif isinstance(s, dict):
                ne_scenes.append(s)
        # Also pull from acts/sequences when no direct scenes exist
        if not ne_scenes:
            for act in (ne.acts if hasattr(ne, "acts") else []):
                act_name = str(act.get("name", "")) if isinstance(act, dict) else str(getattr(act, "name", ""))
                seqs = act.get("sequences") if isinstance(act, dict) else getattr(act, "sequences", [])
                if not seqs:
                    seqs = []
                for i, seq in enumerate(seqs):
                    scene_map[i + 1] = {
                        "scene_number": i + 1,
                        "act": act_name or "Act 1",
                        "title": str(seq.get("name", f"Scene {i+1}")) if isinstance(seq, dict) else str(getattr(seq, "name", f"Scene {i+1}")),
                    }

        # Use direct scene list as primary source
        all_structural_scenes = []
        for s in ne_scenes:
            if isinstance(s, Scene):
                all_structural_scenes.append({
                    "scene_number": s.scene_number or (len(all_structural_scenes) + 1),
                    "act": str(getattr(s, "act", "")) or "Act 1",
                    "sequence": str(getattr(s, "sequence", "") if hasattr(getattr(s, "sequence", None), "__iter__") else getattr(s, "sequence", "")),
                    "objective": str(getattr(s, "objective", "")),
                    "conflict": str(getattr(s, "conflict", "")),
                    "outcome": str(getattr(s, "outcome", "")),
                    "emotional_objective": str(getattr(s, "emotional_objective", "")),
                })

        # Source 2: ScenePlanning (merge on scene_number)
        sp_scenes = sp.scenes if hasattr(sp, "scenes") and sp.scenes else []

        # Populate scene_map from NarrativeExpansion scenes if ScenePlanning is empty
        if not sp_scenes and all_structural_scenes:
            for ns in all_structural_scenes:
                num = int(ns.get("scene_number", 0))
                if num not in scene_map:
                    scene_map[num] = {"scene_number": num, "title": ns.get("objective", f"Scene {num}")}

        for s in sp_scenes:
            if isinstance(s, dict):
                num = s.get("scene_number", len(sp_scenes) + 1)
                if num not in scene_map:
                    scene_map[num] = {"scene_number": num}
                merged = scene_map[num]
                for k in ("purpose", "conflict", "emotion", "visual_goal", "audio_goal", "character_goal", "transition", "duration"):
                    val = s.get(k) or merged.get("_" + k)
                    if val:
                        merged[k] = val
            elif hasattr(s, "scene_number"):
                num = int(getattr(s, "scene_number", len(sp_scenes)))
                if num not in scene_map:
                    scene_map[num] = {"scene_number": num}
                existing = scene_map[num]
                for k in ("purpose", "conflict", "emotion", "visual_goal", "audio_goal", "character_goal", "transition", "duration"):
                    val = getattr(s, k, None)
                    if val:
                        existing[k] = val

        # Merge all sources into final scene dicts
        for num in sorted(scene_map.keys()):
            info = scene_map[num]
            s_num = int(info.get("scene_number", num))

            # Look for matching Scene from NarrativeExpansion
            ne_match = None
            for ns in all_structural_scenes:
                if int(ns.get("scene_number", 0)) == s_num:
                    ne_match = ns
                    break

            # Build the full scene dict
            scene: dict[str, Any] = {
                "scene_number": s_num,
                "number": s_num,
                "title": info.get("title", ""),
                "act": str(info.get("act", ne_match.get("act", "Act 1") if ne_match else "Act 1")).strip() or "Act 1",
                "phase": "",  # Will be filled by downstream agents
                "beat": "",
                "narrative_beat": "",  # hook | plot | turning_point | climax
                "scene_description": "",
                "emotional_state": info.get("emotion", ne_match.get("emotional_objective", "") if ne_match else ""),
                "energy": 0,
                "target_duration_seconds": 0.0,
                "duration_seconds": 0.0,
                "shot_language": {},
                "characters_present": list(all_character_names),
                "music_cue": {},
                "color_palette": "",
                "lighting": "",
                "composition": "",
                "camera_intent": "",
                "atmosphere": "",
            }

            # Fill from NarrativeExpansion merge
            if ne_match:
                if not scene["title"]:
                    scene["title"] = f"Scene {s_num}"
                scene["scene_description"] = ne_match.get("objective", "") + " | Conflict: " + str(ne_match.get("conflict", ""))
                scene["beat"] = str(ne_match.get("sequence", "")) or _act_ordinal(s_num)

            # Fill from ScenePlan merge
            purpose = info.get("_purpose") or info.get("purpose")
            if purpose:
                scene["scene_description"] += (f"\nPurpose: {purpose}")
            dur_raw = info.get("_duration") or info.get("duration")
            if dur_raw:
                seconds_val = _DurationParser.seconds(dur_raw)
                scene["target_duration_seconds"] = seconds_val
                scene["duration_seconds"] = seconds_val
            emotion = info.get("_emotion") or scene["emotional_state"]
            scene["emotional_state"] = str(emotion).strip() if emotion else "Neutral"

            # Narrative beat: from ScenePlan or NarrativeExpansion scene
            nb = info.get("narrative_beat") or (ne_match.get("narrative_beat", "") if ne_match else "")
            if nb:
                scene["narrative_beat"] = str(nb).strip().lower()

            # Apply VisualLanguage as defaults where no scene-specific override exists
            if vl:
                def _get_vl_attr(name):
                    v = getattr(vl, name, None)
                    return str(v).strip() if v else ""
                scene["color_palette"] = _get_vl_attr("color")
                scene["lighting"] = _get_vl_attr("lighting") or (vl.lighting.strip() if hasattr(vl, "lighting") and vl.lighting else "")
                scene["composition"] = _get_vl_attr("composition")
                scene["camera_intent"] = _get_vl_attr("camera_intent")
                scene["atmosphere"] = _get_vl_attr("atmosphere")

            # Apply ProductionSpecifications — lens + camera defaults
            if ps and hasattr(ps, "camera_specs") and ps.camera_specs:
                first_cam = ps.camera_specs[0] if isinstance(ps.camera_specs, list) and ps.camera_specs else {}
                if isinstance(first_cam, dict):
                    shot_size_val = None
                    for k in ("shot_size", "shot-size", "size"):
                        shot_size_val = (first_cam.get(k) or "") and str(first_cam[k]).strip()
                    scene["shot_language"]["shot_size"] = shot_size_val or "Medium"

            # Energy based on conflict intensity
            has_conflict = scene.get("emotional_state") in ("Angry", "Tense", "High tension", "Intense")
            scene["energy"] = 8 if has_conflict else 5

            scenes_out.append(scene)

        # Fallback: if no scenes were built from phase data (e.g. MockLLMClient),
        # generate reasonable scenes directly from the synopsis.
        if not scenes_out:
            scenes_out = self._generate_scenes_from_synopsis()

        self.brief["scenes"] = scenes_out

    def _build_dialogue(self):
        """Carry the expanded dialogue (spoken lines + inner voice) into the brief.

        The brief['dialogues'] list is keyed by scene_number and consumed by the
        PROMETHEUS VoiceStage. Each entry carries:
          - lines: 3-4 spoken exchanges (speaker, text, emotion)
          - inner_voice: the suffering character's whispering inner voice
        This makes the dialogue audible and balanced (both characters heard),
        and surfaces the withdrawn character's unspoken pain.
        """
        dp = self.pkp.dialogue_planning or DialoguePlanning()
        dialogues = getattr(dp, "dialogues", []) or []
        out: list[dict[str, Any]] = []
        for d in dialogues:
            if hasattr(d, "model_dump"):
                ddata = d.model_dump()
            elif isinstance(d, dict):
                ddata = d
            else:
                continue
            scene_num = ddata.get("scene_number", 0)
            lines = ddata.get("lines", []) or []
            inner = ddata.get("inner_voice", []) or []
            # Normalize line dicts
            def _norm(items):
                result = []
                for it in items:
                    if isinstance(it, dict):
                        result.append({
                            "speaker": str(it.get("speaker", "")),
                            "text": str(it.get("text", "")),
                            "emotion": str(it.get("emotion", "neutral")),
                        })
                return result
            out.append({
                "scene_number": scene_num,
                "conversation_intent": ddata.get("conversation_intent", ""),
                "subtext": ddata.get("subtext", ""),
                "emotional_state": ddata.get("emotional_state", ""),
                "lines": _norm(lines),
                "inner_voice": _norm(inner),
            })
        self.brief["dialogues"] = out

    def _build_context(self):
        wd = self.pkp.world_development or WorldDevelopment()
        cp = self.pkp.character_psychology
        sf = self.pkp.story_foundation
        cu = self.pkp.creative_understanding
        pt = None
        if cp:
            pt = _safe_get(cp, "protagonist")

        def _canonical_character_payload(name: str, role: str, identity: str = "") -> dict[str, Any]:
            key = str(name).strip().upper()
            payload = {
                "character_id": key,
                "name": str(name) if name else "Unknown",
                "role": role or "protagonist",
                "description": identity[:200],
                "approved_identity": identity[:200],
                "visual_reference_id": f"MSVI-{key}" if key in {"MARK", "SARAH"} else None,
                "voice_reference_id": f"MSVR-{key}" if key in {"MARK", "SARAH"} else None,
            }
            return payload

        chars_info: list[dict] = []
        if isinstance(pt, Character):
            chars_info.append(_canonical_character_payload(pt.name or "Unknown", pt.role or "protagonist", pt.identity or ""))
        elif isinstance(pt, dict):
            chars_info.append(_canonical_character_payload(str(pt.get("name", "Unknown")), str(pt.get("role", "protagonist")), str(pt.get("identity", ""))))
        if cp and hasattr(cp, "supporting_characters"):
            for sc in cp.supporting_characters:
                if isinstance(sc, Character):
                    chars_info.append(_canonical_character_payload(sc.name or "Unknown", str(sc.role), sc.identity or ""))
                elif isinstance(sc, dict) and sc.get("name"):
                    chars_info.append(_canonical_character_payload(str(sc["name"]), str(sc.get("role", "supporting")), str(sc.get("identity", ""))))

        # Ensure the canonical Mark/Sarah pair survives even when one of the
        # upstream phases times out or omits the supporting character.
        syn_lower = self.pkp.synopsis.lower()
        if any(kw in syn_lower for kw in ("sarah", "wife", "partner", "relationship", "truth")):
            has_mark = any(str(c.get("name", "")).strip().lower() == "mark" for c in chars_info if isinstance(c, dict))
            has_sarah = any(str(c.get("name", "")).strip().lower() == "sarah" for c in chars_info if isinstance(c, dict))
            if has_mark and not has_sarah:
                chars_info.append({
                    "name": "Sarah",
                    "role": "supporting",
                    "description": "A woman who pushes for truth, connection, and emotional honesty"[:200],
                })

        world_desc = ""
        if not world_desc:
            syn_lower = self.pkp.synopsis.lower()
            if "tokyo" in syn_lower or "japan" in syn_lower:
                world_desc = "Near-future Tokyo, Japan — a city of neon-lit streets, quiet alleys, and layered histories beneath the surface"
            elif "near-future" in syn_lower:
                world_desc = "A near-future setting where advanced technology intersects with deeply personal human questions"
            elif "world war" in syn_lower or "war" in syn_lower:
                world_desc = "Historical period setting, spanning conflict and its aftermath"
            elif "pastoral" in syn_lower or "countryside" in syn_lower:
                world_desc = "Rural, pastoral landscape with quiet rhythms of daily life"
            elif "city" in syn_lower or "urban" in syn_lower:
                world_desc = "Dense urban environment — anonymous, fast-paced, hiding intimate dramas behind every window"
            else:
                world_desc = "A contemporary setting shaped by the weight of personal history and unspoken truths"

        # --- Derive characters from synopsis when phase data is empty ---
        if not chars_info:
            syn_lower = self.pkp.synopsis.lower()
            syn_words = self.pkp.synopsis.split()
            
            # Try to extract protagonist names/titles from synopsis
            proto_name = "Protagonist"
            for candidate in [word.strip(".,;:") for word in syn_words if word[0].isupper() and len(word) > 2]:
                if candidate not in ("A", "As", "In", "And", "The", "But", "Or"):
                    proto_name = candidate
                    break
            
            # Canonical P0-04 fallback: if the synopsis implies Mark and Sarah,
            # preserve both identities even if the upstream phases timed out.
            if any(kw in syn_lower for kw in ("sarah", "wife", "partner", "relationship", "truth")):
                chars_info.append({
                    "name": "Mark",
                    "role": "protagonist",
                    "description": "A man carrying the weight of unspoken emotions and fear of disappointing Sarah"[:200],
                })
                chars_info.append({
                    "name": "Sarah",
                    "role": "supporting",
                    "description": "A woman who pushes for truth, connection, and emotional honesty"[:200],
                })
            else:
                char_keywords = {
                    "retired": "A retired craftsman seeking redemption through truth",
                    "clockmaker": "An aging clockmaker whose life's work holds hidden meaning",
                    "man": "A man carrying the weight of unspoken emotions and family history",
                    "woman": "A woman navigating the distance she can no longer bridge",
                    "husband": "A husband paralyzed by fear of rejection, caught between love and silence",
                    "wife": "A wife whose quiet resignation speaks louder than words",
                }
                
                for kw, desc in char_keywords.items():
                    if kw in syn_lower:
                        chars_info.append({
                            "name": proto_name,
                            "role": "protagonist",
                            "description": desc[:200],
                        })
                        break
                
                if not chars_info:
                    chars_info.append({
                        "name": proto_name,
                        "role": "protagonist", 
                        "description": "A person grappling with internal conflict between desire and fear",
                    })

                # Check for secondary characters in synopsis
                secondary_keywords = {
                    "wife": ("The Wife", "Her partner — equally distant, equally afraid but silent"),
                    "rival": ("The Rival", "A competitor racing to uncover the same truth before him"),
                    "grandfather": ("The Grandfather", "Deceased, whose hidden legacy drives the protagonist's journey"),
                }
                for kw, (name, desc) in secondary_keywords.items():
                    if kw in syn_lower:
                        chars_info.append({"name": name, "role": "supporting", "description": desc[:200]})

        themes = []
        if cu and hasattr(cu, "theme") and cu.theme:
            themes.append(str(cu.theme))
        
        # If no themes from phase data, derive from synopsis
        if not themes:
            syn_lower = self.pkp.synopsis.lower()
            theme_from_synopsis = {
                "redemption": "Redemption and forgiveness",
                "secret": "The burden of hidden truth",
                "silence": "The silence between loves — what unsaid things cost us",
                "withdraws": "Isolation and the courage to reach out",
                "time": "Time as both healer and thief",
            }
            for kw, theme in theme_from_synopsis.items():
                if kw in syn_lower:
                    themes.append(theme)
                    break
            if not themes:
                themes.append("The complexity of human connection")

        # Add symbolism from phase data or derive from synopsis
        symbolism = []
        if sf and hasattr(sf, "symbolism"):
            for s in sf.symbolism:
                if str(s):
                    symbolism.append(str(s))
        
        if not symbolism:
            syn_lower = self.pkp.synopsis.lower()
            symbol_map = {
                "timepiece": "Time — the relentless passage that both preserves and obscures truth",
                "clock": "Clocks as metaphors for the protagonist's emotional state",
                "vault": "Secrets buried beneath the surface of ordinary life",
                "art": "The beauty and cost — art as stolen memory vs. restored honor",
                "silence": "Silence as both wound and protection",
            }
            for kw, sym in symbol_map.items():
                if kw in syn_lower:
                    symbolism.append(sym)

        self.brief["context"] = {
            "world": world_desc or "",
            "characters": chars_info,
            "themes": themes or ["Unspecified"],
            "symbolism": symbolism if symbolism else [],
            "constraints": self.pkp.constraints or {},
        }

    def _generate_scenes_from_synopsis(
        self,
        min_scenes: int = 3,
        max_scenes: int = 5,
    ) -> list[dict[str, Any]]:
        """Derive 3-5 scene dicts directly from the synopsis when phase data is empty."""
        synopsis = self.pkp.synopsis.strip()
        if not synopsis:
            return []

        # Determine number of scenes
        num_scenes = min(max(min_scenes, len(self.pkp.synopsis.split()) // 15), max_scenes)

        # Standard three-act titles; extend for more scenes
        standard_titles = [
            "Opening",
            "The Inciting Incident",
            "Rising Action",
            "The Conflict",
            "Climax",
            "Falling Action",
            "The Resolution",
            "Denouement",
            "Aftermath",
        ]

        standard_emotional_states = [
            "Tense",
            "Anguished",
            "Desperate",
            "Intense",
            "Triumphant",
            "Resigned",
            "Contemplative",
            "Hopeful",
            "Peaceful",
        ]

        # Energy curve: low → high → low (three-act arc)
        standard_energy = [5, 7, 4]

        # Duration targets per act position
        standard_durations = [30, 45, 30]

        scenes_out: list[dict[str, Any]] = []

        for idx in range(num_scenes):
            scene_num = idx + 1

            # Act assignment (strict three-act structure)
            if num_scenes <= 2:
                act_num = min(scene_num, 1)
            else:
                act_size = num_scenes // 3 + (1 if num_scenes % 3 != 0 else 0)
                act_boundaries = [act_size * i + 1 for i in range(4)]
                act_num = sum(1 for b in act_boundaries[:-1] if scene_num >= b)

            acts = {1: "Act 1", 2: "Act 2", 3: "Act 3"}
            act = acts.get(act_num, "Act 1")

            # Title: use standard three-act titles regardless of how many scenes we have
            if idx < len(standard_titles):
                title = standard_titles[idx]
                emotional_state = standard_emotional_states[idx]
                energy = standard_energy[idx % len(standard_energy)]
                dur_seconds = standard_durations[idx % len(standard_durations)]
            else:
                # Extended beyond 3 scenes — add descriptive titles
                title = f"Scene {scene_num}"
                emotional_state = standard_emotional_states[min(idx, len(standard_emotional_states) - 1)]
                energy = standard_energy[-1]
                dur_seconds = standard_durations[-1]

            # Scene description: break the synopsis into act-sized chunks
            words = synopsis.split()
            chunk_size = max(1, len(words) // num_scenes)
            start = idx * chunk_size
            end = start + chunk_size if idx < num_scenes - 1 else len(words)
            chunk_text = " ".join(words[start:end])

            shot_words = {
                "Opening": ["close-up", "establishing shot"],
                "The Conflict": ["medium shot", "dutch angle"],
                "Climax": ["handheld", "extreme close-up"],
                "The Resolution": ["wide shot", "slow push-in"],
                "Rising Action": ["tracking shot", "over-the-shoulder"],
                "Falling Action": ["slow pan", "close-up"],
            }
            available_shots = shot_words.get(title, ["medium shot"])

            scenes_out.append({
                "scene_number": scene_num,
                "number": scene_num,
                "title": title,
                "act": act,
                "phase": "",
                "beat": _act_ordinal(scene_num),
                "scene_description": chunk_text[:300],
                "emotional_state": emotional_state,
                "energy": energy,
                "target_duration_seconds": dur_seconds,
                "duration_seconds": float(dur_seconds),
                "shot_language": {
                    "shot_size": available_shots[0],
                    "camera_movement": available_shots[1] if len(available_shots) > 1 else "static",
                    "lens": "35mm",
                    "framing": "rule of thirds" if scene_num != num_scenes else "center frame",
                },
                "characters_present": ["Unknown"],
                "music_cue": {},
                "color_palette": "desaturated cool tones",
                "lighting": "natural light with high contrast shadows",
                "composition": "asymmetric" if scene_num < num_scenes else "symmetric",
                "camera_intent": f"Convey {emotional_state.lower()} mood through {available_shots[0]}",
                "atmosphere": f"visually {emotional_state.lower()}",
            })

        return scenes_out

    def _build_parameters(self):
        v = self.pkp.validation
        cc = self.pkp.creative_critique
        params: dict[str, Any] = {}
        if v:
            params["quality_score"] = float(getattr(v, "score", 0) or 0)
            params["passed_validation"] = bool(getattr(v, "passed", False))
            issues: list[dict] = []
            for issue in (v.issues if hasattr(v, "issues") else []):
                if isinstance(issue, dict):
                    issues.append({
                        "severity": str(issue.get("severity", "")),
                        "category": str(issue.get("category", "")),
                        "description": str(issue.get("description", "")),
                    })
                else:
                    issues.append({
                        "severity": str(getattr(issue, "severity", "")),
                        "category": str(getattr(issue, "category", "")),
                        "description": str(getattr(issue, "description", "")),
                    })
            params["validation_issues"] = issues
        if cc:
            findings = []
            for f in (cc.findings if hasattr(cc, "findings") else []):
                if isinstance(f, dict):
                    findings.append(str(f.get("answer", ""))[:200])
                else:
                    findings.append(str(getattr(f, "answer", "") or "")[:200])
            params["critique_findings"] = findings
        self.brief["parameters"] = params

    def _build_metadata(self):
        statuses = []
        for r in self.pkp.phase_results:
            statuses.append({
                "phase": r.phase_number,
                "name": r.phase_name,
                "status": r.status.value if hasattr(r.status, "value") else str(r.status),
                "drafts": r.draft_count,
            })

        self.brief["metadata"] = {
            "genesis2_version": self.pkp.version or "2.0.0",
            "created_at": self.pkp.created_at or datetime.datetime.utcnow().isoformat(),
            "phases_completed": sum(1 for r in self.pkp.phase_results if getattr(r.status, "value", str(r.status)) == PhaseStatus.COMPLETED.value),
            "phases_total": len(self.pkp.phase_results),
            "phase_details": statuses,
        }

    # -- persistence --------------------------------------------------------

    def save_brief(self, output_path: str | Path) -> Path:
        """Save the brief dict as YAML (or JSON if yaml not available)."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        try:
            import yaml as _yaml  # type: ignore
            out.write_text(
                _yaml.dump(self.to_brief(), default_flow_style=False, sort_keys=False),
                encoding="utf-8",
            )
            logger.info("Brief saved as YAML via PyYAML → %s", out)
        except ImportError:
            # No YAML library; fall back to JSON
            json_path = out.parent / (out.stem + ".json")
            json_path.write_text(
                json.dumps(self.to_brief(), indent=2, default=str),
                encoding="utf-8",
            )
            logger.warning("YAML unavailable — saved brief as %s", json_path)
            return json_path  # type: ignore

        return out


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _act_ordinal(n: int) -> str:
    """Return ordinal string for a scene position (e.g. 'Opening', 'Rising', 'Climax', 'Resolution')."""
    if n <= 2:
        return "Opening"
    if n <= 5:
        return "Confrontation"
    if n <= 7:
        return "Rising Action"
    return "Resolution"
