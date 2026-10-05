---
objective: "EP-0001 production timeline correctness + identify remaining work for natural animated conversation."
status: verified_live_on_genesis
done_conditions:
  - Branch genesis (78aabeda) is the active production path (was main cbd6a62c, which lacked movie_os/prometheus sources).
  - 18 authoritative lines scheduled once, in PKP order; scene_ids {1,2,3}; no fabrication / no first-audio fallback.
  - Timeline and render schedule agree (DEFAULT_PAUSE=0.7; film adds +0.7 last-pause + 2.0s tail).
  - Missing/invalid MP4 raises RuntimeError (film_ok requires exist+size+ffprobe decode).
  - 7 focused regression tests pass (test_editing_timeline.py); 78 focused prometheus tests pass.
next_actions:
  - Full EP-0001 final-film render requires scene images (none on disk) -> FLUX/ComfyUI asset generation, OUT OF SCOPE of this increment.
  - Natural animated conversation: see report — required capability missing (no phoneme/lip-sync; SVD is motion only).
files_in_scope:
  - run_prometheus_ep0001.py, movie_os/prometheus/pipeline.py
  - movie_os/prometheus/stages/{editing,film,voice}_stage.py
  - tests/prometheus/test_editing_timeline.py
  - productions/EP-0001/runs/RUN-20260828-161752/genesis/pkp/PKP-EP-0001-v1.yaml
---

## Verified Production Path (this increment)
Canonical entry: run_prometheus_ep0001.py → PrometheusPipeline → 6 stages
(Frozen PKP RUN-20260828-161752 consumed). Correct timeline verified end-to-end
with the 18 real voice clips + 3 music clips. No code was changed this increment:
commit 78aabeda already implements the fix and is the active branch.

## Key facts
- SC02-SH09 has audible_speaker MARK but active line 2:D001 (SARAH); active renderer
  does NOT consume audible_speaker — non-blocking, not fixed.
- previous/next_shot_id all self/anchor (<SC>-SH00 or null); not consumed by renderer —
  non-blocking.
- SVD local motion (stable-video-diffusion-img2vid-xt) is image→video MOTION, not
  phoneme/mouth lip-sync. No wav2lip / mouth-sync / alternating-speaker animation
  exists. "Required capability missing." for natural conversation.
