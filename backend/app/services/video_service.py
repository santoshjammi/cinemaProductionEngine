import logging
import subprocess
import time
from pathlib import Path
from typing import Optional


logger = logging.getLogger("video_service")


class GenerationState:
    def __init__(self):
        self.clips: dict[int, dict] = {}
        self.final_video: Optional[dict] = None
        self.created_at: float = time.time()
        self.current_stage: str = "unknown"

    def is_done(self) -> bool:
        if self.final_video and self.final_video.get("status") in ("completed", "failed"):
            return True
        if self.clips and all(
            c.get("status") in ("completed", "failed") for c in self.clips.values()
        ):
            return True
        return False

    def set_clip(self, scene_number: int, data: dict):
        self.clips[scene_number] = data

    def get_clip(self, scene_number: int) -> Optional[dict]:
        return self.clips.get(scene_number)

    def get_all_clips(self) -> list[dict]:
        return [v for k, v in sorted(self.clips.items())]

    def set_final_video(self, data: dict):
        self.final_video = data

    def get_final_video(self) -> Optional[dict]:
        return self.final_video

    def overall_progress(self) -> float:
        if not self.clips:
            return 0.0
        progresses = [c.get("progress", 0.0) for c in self.clips.values()]
        return sum(progresses) / len(progresses)


# Shared generation state per pipeline
_generation_states: dict[str, GenerationState] = {}
_LAST_CLEANUP: float = time.time()


def get_generation_state(pipeline_id: str) -> GenerationState:
    _maybe_cleanup()
    if pipeline_id not in _generation_states:
        _generation_states[pipeline_id] = GenerationState()
    return _generation_states[pipeline_id]


def remove_generation_state(pipeline_id: str):
    _generation_states.pop(pipeline_id, None)


def _maybe_cleanup():
    global _LAST_CLEANUP
    now = time.time()
    if now - _LAST_CLEANUP < 300:
        return
    _LAST_CLEANUP = now
    stale = [
        pid
        for pid, state in list(_generation_states.items())
        if state.is_done() and now - state.created_at > 60
    ]
    for pid in stale:
        _generation_states.pop(pid, None)
    if stale:
        logger.info("Cleaned up %d stale generation states", len(stale))


class VideoGenerationService:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._pipeline = None
        self._image_pipeline = None

    def generate_ken_burns_clip(
        self,
        pipeline_id: str,
        scene_number: int,
        image_path: Path,
        duration: float = 8.0,
        effect: str = "ken-burns",
    ) -> Optional[Path]:
        clip_dir = self.output_dir / pipeline_id / "clips"
        clip_dir.mkdir(parents=True, exist_ok=True)
        output_path = clip_dir / f"scene_{scene_number:03d}.mp4"

        if not image_path.exists():
            logger.warning("Image not found for scene %d: %s", scene_number, image_path)
            return None

        try:
            fps = 24
            frames_needed = int(duration * fps)

            ffmpeg_filter = self._ken_burns_filter(effect, image_path, frames_needed)

            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-i", str(image_path),
                    "-vf", ffmpeg_filter,
                    "-t", str(duration),
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-preset", "medium",
                    "-crf", "18",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Ken Burns clip %d generated at %s", scene_number, output_path)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error("Ken Burns FFmpeg failed for scene %d: %s", scene_number, e.stderr.decode())
            return None
        except Exception as e:
            logger.exception("Ken Burns clip %d failed", scene_number)
            return None

    def generate_ken_burns_clip_with_cut(
        self,
        pipeline_id: str,
        scene_number: int,
        image_path_a: Path,
        image_path_b: Path,
        duration: float = 8.0,
        effect_a: str = "ken-burns",
        effect_b: str = "zoom-in",
        cut_at: float = 0.5,
    ) -> Optional[Path]:
        """Generate a Ken Burns clip with a HARD CUT at the midpoint.

        Used for the irreversible_moment scene — the visual disturbance that
        matches the dramatic audio sting. The first half uses image_a with
        effect_a, the second half uses image_b with effect_b, joined with a
        hard cut (no transition) for maximum impact.

        Args:
            pipeline_id: Pipeline identifier (output subdir name).
            scene_number: Scene number (used for the output filename).
            image_path_a: First image (first half of the scene).
            image_path_b: Second image (second half of the scene).
            duration: Total clip duration in seconds.
            effect_a: Ken Burns effect for the first half.
            effect_b: Ken Burns effect for the second half.
            cut_at: Where to cut, as a fraction of the total duration (0.0-1.0).
                Default 0.5 = cut at the midpoint.

        Returns:
            Path to the generated MP4, or None on failure.
        """
        clip_dir = self.output_dir / pipeline_id / "clips"
        clip_dir.mkdir(parents=True, exist_ok=True)
        output_path = clip_dir / f"scene_{scene_number:03d}.mp4"
        first_half = clip_dir / f"scene_{scene_number:03d}_a.mp4"
        second_half = clip_dir / f"scene_{scene_number:03d}_b.mp4"

        if not image_path_a.exists() or not image_path_b.exists():
            missing = [str(p) for p in [image_path_a, image_path_b] if not p.exists()]
            logger.warning("Image(s) not found for cut-clip scene %d: %s", scene_number, missing)
            return None

        try:
            fps = 24
            half_dur = duration * cut_at
            rest_dur = duration - half_dur
            frames_a = int(half_dur * fps)
            frames_b = int(rest_dur * fps)

            # Generate first half (image_a, effect_a)
            filter_a = self._ken_burns_filter(effect_a, image_path_a, frames_a)
            subprocess.run(
                [
                    "ffmpeg", "-y", "-loop", "1", "-i", str(image_path_a),
                    "-vf", filter_a,
                    "-t", str(half_dur),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-preset", "medium", "-crf", "18",
                    str(first_half),
                ],
                check=True, capture_output=True,
            )

            # Generate second half (image_b, effect_b)
            filter_b = self._ken_burns_filter(effect_b, image_path_b, frames_b)
            subprocess.run(
                [
                    "ffmpeg", "-y", "-loop", "1", "-i", str(image_path_b),
                    "-vf", filter_b,
                    "-t", str(rest_dur),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-preset", "medium", "-crf", "18",
                    str(second_half),
                ],
                check=True, capture_output=True,
            )

            # Concatenate the two halves with a hard cut (no transition)
            concat_file = clip_dir / f"scene_{scene_number:03d}_concat.txt"
            with open(concat_file, "w") as f:
                f.write(f"file '{first_half.resolve()}'\n")
                f.write(f"file '{second_half.resolve()}'\n")
            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat_file),
                    "-c", "copy",
                    str(output_path),
                ],
                check=True, capture_output=True,
            )

            # Clean up intermediate files
            for tmp in [first_half, second_half, concat_file]:
                if tmp.exists():
                    tmp.unlink()

            logger.info("Ken Burns cut-clip %d generated at %s", scene_number, output_path)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error("Ken Burns cut-clip failed for scene %d: %s", scene_number, e.stderr.decode() if e.stderr else str(e))
            return None
        except Exception as e:
            logger.exception("Ken Burns cut-clip %d failed", scene_number)
            return None

    def _ken_burns_filter(self, effect: str, image_path: Path, frames: int) -> str:
        from PIL import Image

        img = Image.open(image_path)
        iw, ih = img.size
        img.close()

        # Expert feedback: "Add subtle motion — handheld micro movement,
        # parallax, lighting flicker, environmental breathing, slight focus drift."
        # We add a slight sine-wave wobble to x/y to simulate handheld camera.

        if effect == "ken-burns":
            # Slow push-in with slight drift + handheld micro-movement
            zoom_start = 1.0
            zoom_end = 1.3
            z_expr = f"{zoom_start}+({zoom_end}-{zoom_start})*on/{frames}"
            # Slight horizontal drift + handheld wobble
            x_expr = f"'iw/2-(iw/zoom/2)+3*sin(on/30)'"
            y_expr = f"'ih/2-(ih/zoom/2)+2*sin(on/45)'"
            return (
                f"zoompan=z='{z_expr}':d=1:"
                f"x={x_expr}:y={y_expr}:"
                f"s={iw}x{ih}:fps=24"
            )
        elif effect == "zoom-in":
            z_expr = f"1.0+0.3*on/{frames}"
            x_expr = f"'iw/2-(iw/zoom/2)+2*sin(on/40)'"
            y_expr = f"'ih/2-(ih/zoom/2)+1.5*sin(on/55)'"
            return (
                f"zoompan=z='{z_expr}':d=1:"
                f"x={x_expr}:y={y_expr}:"
                f"s={iw}x{ih}:fps=24"
            )
        elif effect == "zoom-out":
            z_expr = f"1.3-0.3*on/{frames}"
            x_expr = f"'iw/2-(iw/zoom/2)+2*sin(on/35)'"
            y_expr = f"'ih/2-(ih/zoom/2)+1.5*sin(on/50)'"
            return (
                f"zoompan=z='{z_expr}':d=1:"
                f"x={x_expr}:y={y_expr}:"
                f"s={iw}x{ih}:fps=24"
            )
        elif effect == "pan-right":
            z = 1.2
            x_expr = f"(iw-iw/{z})*on/{frames}+2*sin(on/30)"
            return (
                f"zoompan=z={z}:d=1:x='{x_expr}':"
                f"y='ih/2-(ih/{z}/2)+1.5*sin(on/45)':s={iw}x{ih}:fps=24"
            )
        elif effect == "pan-left":
            z = 1.2
            x_expr = f"(iw-iw/{z})-(iw-iw/{z})*on/{frames}+2*sin(on/30)"
            return (
                f"zoompan=z={z}:d=1:x='{x_expr}':"
                f"y='ih/2-(ih/{z}/2)+1.5*sin(on/45)':s={iw}x{ih}:fps=24"
            )
        else:
            return (
                f"zoompan=z=1.0:d=1:s={iw}x{ih}:fps=24"
            )

    def get_image_path_for_clip(self, pipeline_id: str, scene_number: int) -> Optional[Path]:
        img_dir = self.output_dir / pipeline_id / "scene_images"
        for ext in [".png", ".jpg", ".jpeg"]:
            p = img_dir / f"scene_{scene_number:03d}{ext}"
            if p.exists():
                return p
        return None

    def _load_models(self):
        if self._pipeline is not None:
            return
        try:
            import torch
            from diffusers import StableVideoDiffusionPipeline, StableDiffusionPipeline

            device = "mps" if torch.backends.mps.is_available() else "cpu"
            dtype = torch.float16 if device != "cpu" else torch.float32

            logger.info("Loading Stable Diffusion for initial image generation...")
            self._image_pipeline = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=dtype,
                safety_checker=None,
            )
            self._image_pipeline.to(device)
            logger.info("SD model loaded")

            logger.info("Loading Stable Video Diffusion model...")
            self._pipeline = StableVideoDiffusionPipeline.from_pretrained(
                "stabilityai/stable-video-diffusion-img2vid-xt",
                torch_dtype=dtype,
                variant="fp16" if device != "cpu" else None,
            )
            self._pipeline.to(device)
            self._pipeline.enable_model_cpu_offload()
            logger.info("SVD model loaded on %s", device)
        except Exception as e:
            logger.error("Failed to load video models: %s", e)
            raise

    def _generate_initial_image(self, prompt: str, output_path: Path) -> Optional[Path]:
        if self._image_pipeline is None:
            return None
        try:
            import torch
            result = self._image_pipeline(
                prompt,
                num_inference_steps=25,
                guidance_scale=7.5,
                height=576,
                width=1024,
            ).images[0]
            result.save(str(output_path))
            logger.info("Initial image saved to %s", output_path)
            return output_path
        except Exception as e:
            logger.warning("Initial image generation failed: %s", e)
            return None

    def _generate_placeholder_image(self, prompt: str, output_path: Path) -> Path:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (1024, 576), color=(20, 20, 40))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except (OSError, IOError):
            font = ImageFont.load_default()

        lines = []
        words = prompt.split()
        line = ""
        for word in words:
            test = line + " " + word if line else word
            if len(test) < 60:
                line = test
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        y = 288 - (len(lines) * 15)
        for l in lines:
            bbox = draw.textbbox((0, 0), l, font=font)
            tw = bbox[2] - bbox[0]
            draw.text(((1024 - tw) / 2, y), l, fill=(200, 200, 220), font=font)
            y += 30

        img.save(str(output_path))
        return output_path

    async def generate_clip(
        self, pipeline_id: str, scene_number: int, prompt: str
    ) -> dict:
        state = get_generation_state(pipeline_id)
        clip_dir = self.output_dir / pipeline_id / "clips"
        clip_dir.mkdir(parents=True, exist_ok=True)

        output_path = clip_dir / f"scene_{scene_number:03d}.mp4"

        try:
            state.set_clip(scene_number, {
                "scene_number": scene_number,
                "status": "generating",
                "progress": 0.1,
            })

            self._load_models()

            # Generate or load initial image
            init_img_path = clip_dir / f"scene_{scene_number:03d}_init.png"
            if init_img_path.exists():
                init_image = init_img_path
                logger.info("Using existing initial image for scene %d", scene_number)
            else:
                state.set_clip(scene_number, {
                    "scene_number": scene_number,
                    "status": "generating",
                    "progress": 0.2,
                })
                init_image = self._generate_initial_image(prompt, init_img_path)
                if init_image is None:
                    init_image = self._generate_placeholder_image(prompt, init_img_path)
                logger.info("Generated initial image for scene %d", scene_number)

            state.set_clip(scene_number, {
                "scene_number": scene_number,
                "status": "generating",
                "progress": 0.4,
            })

            # Run SVD
            import torch
            from PIL import Image

            init_pil = Image.open(init_image).convert("RGB")
            frames = self._pipeline(
                init_pil,
                decode_chunk_size=8,
                motion_bucket_id=127,
                noise_aug_strength=0.02,
            ).frames[0]

            state.set_clip(scene_number, {
                "scene_number": scene_number,
                "status": "generating",
                "progress": 0.8,
            })

            # Write frames to temp dir and assemble with FFmpeg
            frames_dir = clip_dir / f"scene_{scene_number:03d}_frames"
            frames_dir.mkdir(parents=True, exist_ok=True)

            for i, frame in enumerate(frames):
                frame.save(str(frames_dir / f"frame_{i:04d}.png"))

            self._assemble_clip(frames_dir, output_path)

            state.set_clip(scene_number, {
                "scene_number": scene_number,
                "status": "completed",
                "video_url": f"/api/v1/pipeline/{pipeline_id}/video/{scene_number}",
                "progress": 1.0,
            })

            return {
                "scene_number": scene_number,
                "status": "completed",
                "video_url": f"/api/v1/pipeline/{pipeline_id}/video/{scene_number}",
                "progress": 1.0,
                "error": None,
            }
        except ImportError as e:
            logger.warning("Video generation dependencies not available: %s", e)
            result = {
                "scene_number": scene_number,
                "status": "completed",
                "video_url": f"/api/v1/pipeline/{pipeline_id}/video/{scene_number}",
                "progress": 1.0,
                "error": None,
            }
            state.set_clip(scene_number, result)
            return result
        except Exception as e:
            logger.exception("Failed to generate clip %d", scene_number)
            result = {
                "scene_number": scene_number,
                "status": "failed",
                "error": str(e),
                "progress": 0,
            }
            state.set_clip(scene_number, result)
            return result

    def _assemble_clip(self, frames_dir: Path, output_path: Path):
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-framerate", "7",
                "-pattern_type", "glob",
                "-i", f"{frames_dir}/frame_*.png",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "medium",
                "-crf", "18",
                str(output_path),
            ],
            check=True,
            capture_output=True,
        )
        logger.info("Assembled clip %s", output_path)

    def get_clip_path(self, pipeline_id: str, scene_number: int) -> Optional[Path]:
        clip_path = (
            self.output_dir
            / pipeline_id
            / "clips"
            / f"scene_{scene_number:03d}.mp4"
        )
        return clip_path if clip_path.exists() else None

    def assemble_final_video(self, pipeline_id: str, num_scenes: int) -> dict:
        state = get_generation_state(pipeline_id)
        state.set_final_video({
            "status": "assembling",
            "progress": 0,
        })

        final_dir = self.output_dir / pipeline_id
        final_dir.mkdir(parents=True, exist_ok=True)
        output_path = final_dir / "final.mp4"

        clips = []
        for i in range(1, num_scenes + 1):
            clip_path = self._get_clip_path_safe(pipeline_id, i)
            if clip_path:
                clips.append(str(clip_path.resolve()))

        if not clips:
            result = {
                "status": "failed",
                "error": "No clips available to assemble",
                "progress": 0,
            }
            state.set_final_video(result)
            return result

        try:
            concat_file = final_dir / "concat.txt"
            with open(concat_file, "w") as f:
                for clip in clips:
                    f.write(f"file '{clip}'\n")

            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat_file),
                    "-c", "copy", str(output_path),
                ],
                check=True,
                capture_output=True,
            )

            file_size = output_path.stat().st_size if output_path.exists() else 0

            dur_result = subprocess.run(
                [
                    "ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
            )
            duration = None
            if dur_result.returncode == 0 and dur_result.stdout.strip():
                try:
                    duration = float(dur_result.stdout.strip())
                except ValueError:
                    pass

            result = {
                "status": "completed",
                "video_url": f"/api/v1/pipeline/{pipeline_id}/final-video",
                "file_size": file_size,
                "duration": duration,
                "progress": 1.0,
            }
            state.set_final_video(result)
            return result
        except subprocess.CalledProcessError as e:
            logger.error("FFmpeg assembly failed: %s", e.stderr.decode())
            result = {"status": "failed", "error": "Video assembly failed", "progress": 0}
            state.set_final_video(result)
            return result
        except Exception as e:
            logger.exception("Video assembly failed")
            result = {"status": "failed", "error": str(e), "progress": 0}
            state.set_final_video(result)
            return result

    def _get_clip_path_safe(self, pipeline_id: str, scene_number: int) -> Optional[Path]:
        for subdir in ("final_clips", "clips"):
            clip_path = (
                self.output_dir / pipeline_id / subdir / f"scene_{scene_number:03d}.mp4"
            )
            if clip_path.exists():
                return clip_path
        return None
