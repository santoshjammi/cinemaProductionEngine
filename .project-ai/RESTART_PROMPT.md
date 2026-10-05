# Restart Prompt

## Current Focus
EP-0001 timeline is verified on `genesis` (78aabeda). Conversation-proof Phase 1 smoke
(3:D001, Sarah close-up) is COMPLETE: MuseTalk 1.5 MLX fp16 runs natively on M1 Max,
mouth articulates correctly, proof MP4 produced.

## Verified Facts
- Canonical entry: run_prometheus_ep0001.py -> PrometheusPipeline (6 stages) consuming
  frozen PKP-EP-0001-v1.yaml (RUN-20260828-161752). Tests green (editing 7/7, prom 78/78).
- Smoke isolated venv .venv-musetalk (py3.11, torch-free). Model mlx-community/MuseTalk-1.5-
  fp16 @ ad54104 (1.9GB). Port xocialize/musetalk-mlx @ c6eb30e. Licenses MIT, commercial OK.
- proof_3D001.mp4: h264+aac, 1122x1402, 25fps, 3.52s, decodes. 16.7s generate, RSS 2.23GB.
- Mouth articulation REAL: oral cavity 7px(closed f68)->15px(open f14), 88/88 frames.

## Current Block
- Composite is below commercial grade: pasting 256px model output on sharp portrait causes
  mouth softness / mask-boundary seam. Torch-free path (no bisenet face-parse blend) is the
  cause. Sync itself is correct.

## Unfinished Work (Board decision required)
1. Approve/deny bisenet face-parse blend dependency (pulls torch + small face-parsing model)
   to reach commercial-grade composite for the 4-line proof.
2. If approved: integrate blend, re-run 3:D001 fully, repeat for 3:D002-3:D004 (Mark close-ups
   + Sarah silent reactions), assemble 12-20s proof MP4 on the corrected timeline.
3. Full EP-0001 final MP4 still requires FLUX scene-image generation (out of earlier scope).

## Constraints
- Preserve frozen GENESIS, exact dialogue, existing voices/music, character identities.
- Do NOT integrate conflicting providers or modify GENESIS.
- Do NOT claim a commercial final film until a clean decodable MP4 exists on disk.

## Files in Scope (this increment)
- .workspace-musetalk/ (smoke_3d001.py, dist model, deliverables/, io/)
- .venv-musetalk/ (isolated env)
- run_prometheus_ep0001.py, movie_os/prometheus/stages/*.py
- productions/EP-0001/runs/RUN-20260828-161752/genesis/pkp/PKP-EP-0001-v1.yaml

## Next Action
Board: decide on bisenet blend dependency. If approved, refine composite to commercial grade;
if not, deliver the 256px composite as proof-of-sync only.
