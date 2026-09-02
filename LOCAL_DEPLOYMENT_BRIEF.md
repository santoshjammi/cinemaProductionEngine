# Genesis Pipeline — Final Execution Brief

## Overview
All creative and engineering tasks for "The Space Between Us" are **complete**. The pipeline is ready to execute a genuine vertical slice of Scene 4 using real FLUX rendering and local audio synthesis.

## Completed Engineering Tasks
1.  **Narrative & Dialogue:** Replaced all placeholders with the final `scenes.yaml` (Hook -> Asymmetrical Dinner -> Silent Rupture).
2.  **Audio Mixer:** Fixed zero-byte file issues and implemented emotion-aware ducking profiles (-6dB to -12dB) for the emotional peak of Scene 4.
3.  **FLUX Integration:** Created a strict FLUX workflow (`flux_workflow_scene4_final.json`) that enforces character consistency via CLIP/TE5 conditioning.

## Required Local Execution (Codex Desktop App)
To complete the "genuine" vertical slice, run the following in your local environment where ComfyUI dependencies are installed:

```bash
cd /Users/santosh/Desktop/projects/videoGen

# 1. Launch ComfyUI with FLUX bf16 model
python3 models/ComfyUI/main.py --listen 127.0.0.1 --port 8188

# 2. Submit the Scene 4 Workflow
curl -X POST "http://localhost:8188/prompt" \
     -H "Content-Type: application/json" \
     -d @pipeline/flux_workflow_scene4_final.json

# 3. Run the final pipeline assembly
python3 pipeline/run_v7.py --fail-closed
```

## Final Status Check
*   **Visuals:** FLUX bf16 on Apple Silicon (Expected runtime: ~4-5 mins).
*   **Dialogue:** Local Kokelo/Piper TTS (Preferred) or `edge_tts` fallback.
*   **Video:** FFmpeg assembly of real assets into final MP4.

Once the FLUX image is generated and saved to `output/the_space_between_us_v10/images/scene_4_*`, the "genuine" milestone is achieved.
