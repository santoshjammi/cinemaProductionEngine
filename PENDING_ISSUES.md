# videoGen — Pending Issues

> These issues have been identified but are set aside for separate handling.
> They are not in the active kanban queue.

---

## ComfyUI Freeze

**Status:** ⏸️ Pending — to be handled separately by Santosh

**Symptoms:**
The video pipeline keeps freezing on ComfyUI during generation. Multiple reports across sessions.

**Root cause investigation needed:**
- Model loading memory pressure (qwen3.6 was consuming 29 GB)
- Blocking network/subprocess calls without timeouts
- ComfyUI workflow configuration

**References:**
- Kanban tasks consolidated into `fix-comfyui-freeze` (cancelled — pending)
- Original duplicate tasks: f8014338, d30aec05, 6f42e1c2, 7724e1d4, 0a18147, 033e92b1, 82efcabb, a8e67fae, 5523490, 0601b606, fe10ef29, 2faf2276

**Related:**
- `pipeline/run_v7.py` — main pipeline entry point
- `pipeline/orchestrator.py` — orchestrator with potential blocking calls
- ComfyUI workflow JSON files

---

## ComfyUI Workflow Optimization

**Status:** ⏸️ Pending

**Task:** Optimize Flux model loading in ComfyUI to reduce idle memory from 12 GB and speed up generation.

**Kanban reference:** `a447e1d8` (ready → moved to pending)

---

## Fixed (July 28, 2026)

### ✅ No conversations — FIXED
- **Problem:** Scenes had generic narration placeholders with no actual dialogue
- **Fix:** Replaced `pipeline/scenes/scenes.yaml` with real MARK/SARAH dialogue-driven scenes across all 5 beats (hook → establishment → dialogue → emotional_peak → resolution)
- **Files changed:** `scenes.yaml`, `run_v7.py`

### ✅ No voiceovers — FIXED  
- **Problem:** TTS pipeline received no dialogue lines to synthesize
- **Fix:** Updated `run_v7.py` to read `dialogue_lines` directly from scenes.yaml. Both BrianNeural (MARK) and AriaNeural (SARAH) voices are generated per scene with emotion-aware prosody
- **Files changed:** `run_v7.py`, `scenes.yaml`

### ✅ Character inconsistency — FIXED
- **Problem:** No character appearance descriptors in image prompts; every frame got a different person
- **Fix:** Replaced `prompts.yaml` with full visual descriptions that include MARK and SARAH's complete physical appearances in every scene. Added deterministic fallback module for standalone content generation
- **Files changed:** `prompts.yaml`, created `deterministic_fallback.py`

### ✅ Video mixing — FIXED
- **Problem:** Audio mixing pipeline had nothing to mix (no TTS outputs)
- **Fix:** The entire chain is now connected: scenes.yaml → dialogue lines → TTS per character → audio_pipeline.py → video assembly
- **Files changed:** `run_v7.py`

### ✅ Standalone generation — NEW
- **Problem:** Pipeline required both Ollama AND ComfyUI to produce content
- **Fix:** Created `pipeline/deterministic_pipeline.py` which generates complete video assets without requiring any LLM inference or external services
- **Files changed:** created `deterministic_pipeline.py`, `deterministic_fallback.py`

---

*Last updated: 28 July 2026*
