"""prometheus_scene_runner — The Builder's orchestrator for Scene 4.

Handles:
  - ComfyUI startup & readiness checking
  - FLUX image generation workflow submission
  - TTS voiceover synthesis
  - Audio/music mixing via ffmpeg
  - Final video assembly
  - Output validation & manifest sealing

Dead man's switch & retry helpers from SAI-18 are imported at the module level.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time as _time
import uuid
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from builder.comfyui_runner import ComfyUIClient, ComfyUISession

logger = logging.getLogger("prometheus_scene_runner")

# ---------------------------------------------------------------------------
# Dead man's switch & retry helpers — SAI-18 blocking call resilience
# ---------------------------------------------------------------------------

import contextlib as _ctx
import functools as _ft


class DeadMansSwitchTimeoutError(RuntimeError):
    """Raised when a pipeline stage fails to report progress within its timeout window."""
    pass


def dead_mans_switch(timeout_seconds: int = 600, progress_interval: float = 10.0):
    """Decorator that aborts a stage if it runs too long without yielding control."""
    def decorator(func):
        @_ft.wraps(func)
        def wrapper(*args, **kwargs):
            import time as _time
            start = _time.time()
            attempts = 0
            
            while True:
                attempts += 1
                try:
                    return func(*args, **kwargs)
                except DeadMansSwitchTimeoutError as e:
                    raise
                except Exception as e:
                    elapsed = _time.time() - start
                    if elapsed > timeout_seconds:
                        raise DeadMansSwitchTimeoutError(
                            f"Stage \'{func.__name__}\' timed out after {elapsed:.1f}s "
                            f"(limit: {timeout_seconds}s, attempts={attempts})."
                        ) from e
                    wait = min(0.5 * (2 ** attempts), 30)
                    logger.warning(
                        "[SAI-18] Stage \'%s\' failed (attempt %d): %s — retrying in %.1fs",
                        func.__name__, attempts, e, wait,
                    )
                    _time.sleep(wait)
        return wrapper
    return decorator


class RetryableAPIError(Exception):
    """An API call that may succeed on retry (transient GPU/memory failure)."""
    pass


def with_retry(max_attempts: int = 3, base_delay: float = 1.0):
    """Retry a ComfyUI API call with exponential backoff for transient failures."""
    def decorator(func):
        @_ft.wraps(func)
        async def wrapper(*args, **kwargs):
            import time as _time
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (RetryableAPIError, Exception) as exc:
                    err_msg = str(exc).lower()
                    is_transient = any(kw in err_msg for kw in [
                        "oom", "out of memory", "gpu", "vram", 
                        "memory", "timeout", "busy", "reload",
                        "refused", "connection", "no data"
                    ])
                    if not is_transient or attempt == max_attempts - 1:
                        raise
                    wait = base_delay * (2 ** attempt)
                    logger.warning(
                        "[SAI-18] %s failed (attempt %d/%d): %s — retrying in %.1fs",
                        func.__name__, attempt + 1, max_attempts, exc, wait,
                    )
                    await _time.sleep(wait)
                    last_exc = exc
            raise last_exc
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# ComfyUI root & defaults
# ---------------------------------------------------------------------------

COMFYUI_ROOT = Path("/Users/santosh/Desktop/projects/videoGen/models/ComfyUI")
DEFAULT_PORT = 8188
DEFAULT_HOST = "127.0.0.1"
API_BASE = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Scene4Result:
    """Final result of the Scene 4 pipeline."""
    status: str = "pending"
    
    # Generated assets
    generated_image_path: Optional[str] = None
    dialogue_audio_path: Optional[str] = None
    mixed_audio_path: Optional[str] = None
    final_scene_mp4_path: Optional[str] = None
    
    # Manifest & admission
    package_sealed: bool = False
    builder_admission: str = ""
    
    # Metadata
    workflow_path: Optional[str] = None
    prompt_used: Optional[str] = None
    visual_generation: dict[str, Any] = field(default_factory=dict)
    tts_generation: dict[str, Any] = field(default_factory=dict)
    audio_generation: dict[str, Any] = field(default_factory=dict)
    
    # File sizes & timing
    file_sizes: dict[str, int] = field(default_factory=dict)
    durations: dict[str, float] = field(default_factory=dict)
    total_render_seconds: float = 0.0
    production_ready: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        d = {
            "status": self.status,
            "generated_image_path": self.generated_image_path,
            "dialogue_audio_path": self.dialogue_audio_path,
            "mixed_audio_path": self.mixed_audio_path,
            "final_scene_mp4_path": self.final_scene_mp4_path,
            "package_sealed": self.package_sealed,
            "builder_admission": self.builder_admission,
            "workflow_path": self.workflow_path,
            "prompt_used": self.prompt_used,
            "visual_generation": self.visual_generation,
            "tts_generation": self.tts_generation,
            "audio_generation": self.audio_generation,
            "file_sizes": self.file_sizes,
            "durations": self.durations,
            "total_render_seconds": round(self.total_render_seconds, 2),
            "production_ready": self.production_ready,
        }
        return d


# ---------------------------------------------------------------------------
# Scene4PipelineRunner
# ---------------------------------------------------------------------------

class Scene4PipelineRunner:
    """Orchestrates Scene 4 generation through ComfyUI image generation + TTS + audio mixing."""

    def __init__(self, output_dir: str = "/tmp/scene4_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.result = Scene4Result()

    @dead_mans_switch(timeout_seconds=600)
    def run(self, scene_data: dict[str, Any]) -> Scene4Result:
        """Run the full Scene 4 pipeline end-to-end."""
        logger.info("[Scene4] Starting pipeline for scene")
        
        # Step 1: Generate image via ComfyUI
        if not self._generate_image(scene_data):
            self.result.status = "failed"
            self.result.builder_admission = "image generation failed"
            return self.result
        
        # Step 2: Generate TTS voiceover
        self._synthesize_voiceover(scene_data)
        
        # Step 3: Generate background music
        self._generate_music(scene_data)
        
        # Step 4: Mix audio layers
        self._mix_audio(scene_data)
        
        # Step 5: Assemble video clip
        self._assemble_clip(scene_data)
        
        # Step 6: Validate output
        self._validate_output()
        
        self.result.status = "completed"
        return self.result

    def _generate_image(self, scene_data: dict[str, Any]) -> bool:
        """Generate FLUX image via ComfyUI workflow."""
        logger.info("[Scene4] Generating image via FLUX...")
        
        client = ComfyUIClient()
        session = client.start_session()
        
        if not session.is_comfyui_available():
            print("[Runner] ComfyUI server not responding on localhost:8188", flush=True)
            started = self._start_comfyui_briefly()
            if not started:
                return False
            # Probe /system_stats until ready (up to 60s)
            deadline = _time.time() + 60
            while _time.time() < deadline:
                try:
                    session.api_get("/system_stats")
                    break
                except Exception:
                    _time.sleep(2)
            else:
                print("[Runner] ComfyUI did not become ready within 60s", flush=True)
                return False
        
        prompt_text = scene_data.get("prompt_text", "") if hasattr(self, 'image_prompt_data') else ""
        
        # Get workflow from optimized templates
        from builder.comfyui_runner import ComfyUIWorkflowGenerator
        workflow = ComfyUIWorkflowGenerator.generate(
            prompt=prompt_text or scene_data.get("visual_prompt", "a cinematic scene"),
            negative_prompt=scene_data.get("negative_prompt", ""),
            width=1024,
            height=576,
            quality="production",
        )
        
        self.result.workflow_path = str(self.output_dir / f"workflow_{uuid.uuid4().hex[:8]}.json")
        workflow_path = Path(self.result.workflow_path)
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        with open(workflow_path, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        try:
            result_data = client.submit_workflow(session, workflow)
            prompt_id = result_data.get("prompt_id", "")
            if not prompt_id:
                print("[Runner] No prompt ID returned from ComfyUI API", flush=True)
                return False
            
            # Wait for completion (up to 300s)
            history = client.wait_for_completion(session, prompt_id, timeout=300, poll_interval=3.0)
            
            if not history:
                print("[Runner] ComfyUI generation timed out after 5 minutes", flush=True)
                return False
            
            images = client.get_output_images(history)
            if not images:
                print("[Runner] No images returned from ComfyUI API", flush=True)
                return False
            
            first_image = str(images[0])
            self.result.generated_image_path = first_image
            
            # Extract dimensions if available
            try:
                im_size = subprocess.run(["identify", "-format", "%w %h", first_image],
                                        capture_output=True, text=True, timeout=15)
                w, h = im_size.stdout.split()[:2]
                self.result.visual_generation["image_dimensions"] = (int(w), int(h))
            except Exception:
                pass
            
            self.result.generated_image_path = first_image
            self.result.comfyui_output_path = first_image
            self.result.visual_generation = {
                "status": "complete",
                "reason": None,
                "flux_executed": True,
                "comfyui_executed": True,
                "production_valid": True,
                "workflow_path": str(self.result.workflow_path),
                "output_image": first_image,
            }
            
            print(f"[Runner] FLUX workflow executed. Output: {first_image}", flush=True)
            return True
            
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"[Runner] ComfyUI API error: {e}", flush=True)
            return False

    def _start_comfyui_briefly(self, timeout_sec: int = 120) -> bool:
        """Attempt to launch ComfyUI server for the duration of timeout_sec."""
        print("[Runner] Attempting to start ComfyUI server...", flush=True)
        try:
            env = os.environ.copy()
            env["HF_HUB_DISABLE_TELEMETRY"] = "1"
            env["DO_NOT_TRACK"] = "1"
            
            process = subprocess.Popen(
                ["/usr/bin/python3", str(COMFYUI_ROOT / "main.py")],
                cwd=str(COMFYUI_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            
            deadline = _time.time() + timeout_sec
            while _time.time() < deadline:
                try:
                    client = ComfyUIClient()
                    session = client.start_session()
                    if session.is_comfyui_available():
                        print("[Runner] ComfyUI server started and responding", flush=True)
                        self._comfyui_process = process
                        return True
                except Exception:
                    pass
                _time.sleep(2)
            
            print("[Runner] ComfyUI did not start within timeout", flush=True)
            process.terminate()
            process.wait(timeout=10)
            return False
        except Exception as e:
            print(f"[Runner] Failed to start ComfyUI: {e}", flush=True)
            return False

    def _synthesize_voiceover(self, scene_data: dict[str, Any]):
        """Synthesize dialogue voiceover via TTS."""
        logger.info("[Scene4] Synthesizing voiceover...")
        # Use EdgeTTS or local TTS — path determined by config
        from builder.tts_runner import TTSCreator
        
        tts = TTSCreator(output_dir=str(self.output_dir))
        result = tts.synthesize(scene_data)
        
        self.result.dialogue_audio_path = result.get("audio_path")
        self.result.tts_generation = {
            "backend": result.get("backend", "edge-tts"),
            "success": result.get("success", False),
            "duration_seconds": result.get("duration_seconds", 0),
        }
        
        if result.get("output_path"):
            self.result.file_sizes["dialogue_audio"] = os.path.getsize(result["output_path"])

    def _generate_music(self, scene_data: dict[str, Any]):
        """Generate background music via numpy procedural synthesis."""
        logger.info("[Scene4] Generating background music...")
        from builder.music_runner import DramaticStingGenerator
        
        mg = DramaticStingGenerator()
        beats = mg.generate(scene_data.get("beats", []))
        
        self.result.mixed_audio_path = beats.get("output_path")
        self.result.audio_generation["music_source"] = "numpy procedural"
        self.result.durations["music"] = beats.get("duration_seconds", 5.0)

    def _mix_audio(self, scene_data: dict[str, Any]):
        """Mix TTS voiceover + music via ffmpeg."""
        logger.info("[Scene4] Mixing audio layers...")
        # Use ffmpeg to combine dialogue + music tracks
        from builder.audio_mixer import AudioMixer
        
        mixer = AudioMixer(output_dir=str(self.output_dir))
        mixed = mixer.mix(
            dialogue_path=self.result.dialogue_audio_path or "",
            music_path=self.result.mixed_audio_path or "",
            output_prefix="scene4_mixed",
        )
        
        if mixed.get("output_path"):
            self.result.mixed_audio_path = mixed["output_path"]
            self.result.durations["mixed_audio"] = mixed.get("duration_seconds", 0)

    def _assemble_clip(self, scene_data: dict[str, Any]):
        """Assemble final scene video with Ken Burns effect."""
        logger.info("[Scene4] Assembling video clip...")
        
        from builder.ffmpeg_assembler import FFmpegAssembler
        
        assembler = FFmpegAssembler()
        assembly = assembler.assemble(
            image_path=self.result.generated_image_path or "",
            audio_path=self.result.mixed_audio_path or "",
            output_dir=str(self.output_dir),
        )
        
        self.result.final_scene_mp4_path = assembly.get("output_path")
        if assembly.get("output_size_bytes"):
            self.result.file_sizes["scene_4_preview_mp4"] = assembly["output_size_bytes"]
        if assembly.get("duration_seconds"):
            self.result.durations["scene_4_preview_mp4"] = assembly["duration_seconds"]

    def _validate_output(self):
        """Validate all generated assets meet production standards."""
        logger.info("[Scene4] Validating output...")
        
        checks = []
        
        if not self.result.generated_image_path:
            checks.append(("image", False, "No image generated"))
        elif not Path(self.result.generated_image_path).exists():
            checks.append(("image", False, "Image file not found"))
        else:
            size = os.path.getsize(self.result.generated_image_path)
            checks.append(("image", True, f"OK ({size} bytes)"))
        
        if not self.result.final_scene_mp4_path:
            checks.append(("video", False, "No video generated"))
        elif not Path(self.result.final_scene_mp4_path).exists():
            checks.append(("video", False, "Video file not found"))
        else:
            dur = self.result.durations.get("scene_4_preview_mp4", 0)
            size = os.path.getsize(self.result.final_scene_mp4_path)
            checks.append(("video", True, f"OK ({size} bytes, {dur:.1f}s)"))
        
        self.result.production_ready = all(c[1] for c in checks)
        self.result.builder_admission = "admitted" if self.result.production_ready else "conditional"

    def generate_report(self) -> str:
        """Generate a human-readable production report."""
        report_lines = [f"Scene 4 Production Report", "=" * 40]
        
        for key, value in [("status", self.result.status), ("production_ready", self.result.production_ready)]:
            report_lines.append(f"{key}: {value}")
        
        if self.result.generated_image_path:
            size = self.result.file_sizes.get("generated_image", os.path.getsize(self.result.generated_image_path))
            report_lines.append(f"  image ({size} bytes)")
        else:
            report_lines.append("  image: NOT GENERATED")
            
        if self.result.final_scene_mp4_path:
            size = self.result.file_sizes.get("scene_4_preview_mp4", os.path.getsize(self.result.final_scene_mp4_path))
            dur = self.result.durations.get("scene_4_preview_mp4", 0)
            report_lines.append(f"  video ({size} bytes, {dur:.1f}s)")
        else:
            report_lines.append("  video: NOT GENERATED")
        
        return "\n".join(report_lines)


if __name__ == "__main__":
    # Standalone test runner
    import sys
    logger.setLevel(logging.INFO)
    
    scene_data = {
        "prompt_text": "A cinematic wide shot of a character standing at the edge of a cliff",
        "visual_prompt": "cinematic wide shot, dramatic lighting",
        "negative_prompt": "blurry, low quality, text, watermark",
    }
    
    runner = Scene4PipelineRunner(output_dir="/tmp/scene4_test")
    result = runner.run(scene_data)
    print(result.generate_report())
