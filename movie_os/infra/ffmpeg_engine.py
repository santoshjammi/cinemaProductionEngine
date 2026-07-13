"""Movie OS v1 — FFmpeg wrapper for video/audio processing.

Provides high-level operations for:
- Ken Burns effects on still images
- Scene composition (images + audio sync)
- Transitions between scenes
- Color grading per grammar rules
- Final video assembly from scenes
- Subtitle burning

All operations use FFmpeg as the backend engine.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


logger = logging.getLogger("movie_os.infra.ffmpeg")


class ColorGrade(Enum):
    """Color grading presets for psychological cinema grammar."""
    DESATURATED_WARM = "desaturated_warm"
    COOL_BLUE = "cool_blue"
    NEUTRAL = "neutral"
    WARM_GOLD = "warm_gold"
    HIGH_CONTRAST = "high_contrast"


class TransitionType(Enum):
    """Transition types between scenes."""
    CROSS_DISSOLVE = "cross_dissolve"  # smooth, natural
    HARD_CUT = "hard_cut"              # impact, silence
    FADE_BLACK = "fade_black"          # dramatic pause
    FADE_WHITE = "fade_white"          # dreamy, memory


class KenBurnsEffect(Enum):
    """Ken Burns camera effects for still images."""
    PAN_LEFT = "pan-left"
    PAN_RIGHT = "pan-right"
    ZOOM_IN = "zoom-in"
    ZOOM_OUT = "zoom-out"
    STATIC = "static"  # hold on face, weight


@dataclass
class AudioLayer:
    """Represents an audio layer (voice, music, SFX)."""
    file_path: str
    volume: float = 1.0  # 0.0 to 1.0
    fade_in: float = 0.0  # seconds
    fade_out: float = 0.0  # seconds
    start_offset: float = 0.0  # seconds


@dataclass
class SceneComposition:
    """Represents a single scene's composition."""
    scene_number: int
    image_path: str
    duration_seconds: float
    audio_layers: list[AudioLayer] = field(default_factory=list)
    ken_burns: KenBurnsEffect = KenBurnsEffect.PAN_LEFT
    transition_in: TransitionType = TransitionType.CROSS_DISSOLVE
    transition_out: TransitionType = TransitionType.CROSS_DISSOLVE
    color_grade: ColorGrade = ColorGrade.DESATURATED_WARM
    subtitle_path: Optional[str] = None


@dataclass
class VideoCompositionResult:
    """Result of video composition."""
    output_path: str
    total_duration_seconds: float
    scene_count: int
    success: bool
    errors: list[str] = field(default_factory=list)


class FFmpegError(Exception):
    """Raised when FFmpeg operations fail."""
    pass


class FFmpegEngine:
    """High-level FFmpeg engine for video/audio processing.

    This class provides a clean API over FFmpeg for:
    - Image-to-video with Ken Burns effects
    - Multi-layer audio mixing (voice + music + SFX)
    - Scene transitions
    - Color grading
    - Final assembly
    """

    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg = ffmpeg_path
        self.ffprobe = ffprobe_path
        self._validate()

    def _validate(self):
        """Check that FFmpeg is available."""
        try:
            result = subprocess.run(
                [self.ffmpeg, "-version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                raise FFmpegError("FFmpeg not found or not executable")
            logger.info(f"FFmpeg validated: {result.stdout.split(chr(10))[0]}")
        except FileNotFoundError:
            raise FFmpegError("FFmpeg binary not found. Install ffmpeg: brew install ffmpeg")
        except subprocess.TimeoutExpired:
            raise FFmpegError("FFmpeg version check timed out")

    @staticmethod
    def get_duration(file_path: str) -> float:
        """Get duration of an audio/video file in seconds using ffprobe."""
        try:
            result = subprocess.run(
                [
                    self.ffprobe,
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "json",
                    file_path
                ],
                capture_output=True, text=True, timeout=10
            )
            data = json.loads(result.stdout)
            return float(data["format"]["duration"])
        except Exception as e:
            logger.warning(f"Could not get duration for {file_path}: {e}")
            return 0.0

    @staticmethod
    def get_image_dimensions(image_path: str) -> tuple[int, int]:
        """Get image dimensions (width, height)."""
        try:
            result = subprocess.run(
                [
                    self.ffprobe,
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "json",
                    image_path
                ],
                capture_output=True, text=True, timeout=10
            )
            data = json.loads(result.stdout)
            stream = data["streams"][0]
            return int(stream["width"]), int(stream["height"])
        except Exception as e:
            logger.warning(f"Could not get dimensions for {image_path}: {e}")
            return 1920, 1080

    async def compose_scene(
        self,
        scene: SceneComposition,
        output_path: str,
        target_resolution: tuple[int, int] = (1920, 1080)
    ) -> bool:
        """Compose a single scene: image + audio layers with Ken Burns and color grading.

        Args:
            scene: Scene composition parameters
            output_path: Output video file path for this scene
            target_resolution: (width, height) of final video

        Returns:
            True if composition succeeded
        """
        width, height = target_resolution

        # Calculate Ken Burns zoom factor based on effect type
        zoom_factor = 1.05  # Slight zoom for all effects
        pan_x, pan_y = 0, 0  # Default center

        if scene.ken_burns == KenBurnsEffect.PAN_LEFT:
            pan_x = -0.1
        elif scene.ken_burns == KenBurnsEffect.PAN_RIGHT:
            pan_x = 0.1
        elif scene.ken_burns == KenBurnsEffect.ZOOM_IN:
            zoom_factor = 1.15
        elif scene.ken_burns == KenBurnsEffect.ZOOM_OUT:
            zoom_factor = 0.95

        # Build FFmpeg filter complex for this scene
        filters = []

        # 1. Scale image to target resolution
        filters.append(f"scale={width}:{height}:force_original_aspect_ratio=decrease")
        filters.append(f"crop={width}:{height}:-1:-1")

        # 2. Apply Ken Burns (zoom + pan) over duration
        zoom_expr = f"if(lt(t,{scene.duration_seconds/2}),{zoom_factor},1)"
        pan_x_expr = f"{pan_x}*t/{scene.duration_seconds}"
        filters.append(f"zoompan=z='{zoom_expr}':x='{pan_x_expr}':y=0:d={int(scene.duration_seconds*25)}:s={width}x{height}:fps=25")

        # 3. Apply color grading
        grade_filter = self._get_color_grade_filter(scene.color_grade)
        if grade_filter:
            filters.append(grade_filter)

        # 4. Add transition effects
        if scene.transition_in == TransitionType.FADE_BLACK:
            filters.append(f"fade=t=in:st=0:d=1")
        if scene.transition_out == TransitionType.FADE_BLACK:
            filters.append(f"fade=t=out:st={scene.duration_seconds-1}:d=1")

        filter_complex = ",".join(filters)

        # Build input arguments
        cmd = [self.ffmpeg, "-y"]

        # Input image (loop it for duration)
        cmd.extend(["-loop", "1", "-i", scene.image_path])

        # Input audio layers
        audio_inputs = []
        for i, layer in enumerate(scene.audio_layers):
            cmd.extend(["-i", layer.file_path])
            audio_inputs.append(i + 1)  # Audio inputs start after image input

        # Build audio filter chain
        audio_filters = []

        # Apply per-layer processing
        for idx, (layer, input_idx) in enumerate(zip(scene.audio_layers, audio_inputs)):
            layer_filters = []

            # Volume adjustment
            if layer.volume != 1.0:
                layer_filters.append(f"volume={layer.volume}")

            # Fade in
            if layer.fade_in > 0:
                layer_filters.append(f"afade=t=in:st=0:d={layer.fade_in}")

            # Fade out
            if layer.fade_out > 0:
                fade_start = max(0, scene.duration_seconds - layer.fade_out)
                layer_filters.append(f"afade=t=out:st={fade_start}:d={layer.fade_out}")

            if layer_filters:
                audio_filters.append(f"[{input_idx}:a]{''.join(layer_filters)}[a{idx}]")

        # Mix all audio layers
        if len(audio_filters) > 1:
            inputs_str = "".join(f"[a{i}]" for i in range(len(audio_filters)))
            audio_filters.append(f"{inputs_str}amix=inputs={len(audio_filters)}:duration=longest[aout]")

        # Add silence if no audio layers
        if not scene.audio_layers:
            audio_filters.append(f"anullsrc=r=48000:cl=stereo[dummy]")
            audio_filters.append("[dummy]adelay=all={delay}|{delay}[aout]").format(
                delay=int(scene.duration_seconds * 1000)
            )

        # Build full command
        cmd.extend([
            "-t", str(scene.duration_seconds),
            "-filter_complex", ";".join(audio_filters + [f"[0:v]fps=25,{filter_complex}[vout]"]),
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",  # High quality
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-shortest",
            output_path
        ])

        try:
            logger.info(f"Composing scene {scene.scene_number}: {output_path} ({scene.duration_seconds}s)")
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                error_msg = stderr.decode()[:500] if stderr else "Unknown FFmpeg error"
                logger.error(f"Scene {scene.scene_number} composition failed: {error_msg}")
                return False

            logger.info(f"Scene {scene.scene_number} composed successfully")
            return True

        except Exception as e:
            logger.error(f"Exception composing scene {scene.scene_number}: {e}")
            return False

    def _get_color_grade_filter(self, grade: ColorGrade) -> Optional[str]:
        """Get FFmpeg color filter for a grading preset."""
        filters = {
            ColorGrade.DESATURATED_WARM: (
                "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:"
                "curves=all='0/0 0.5/0.5 1/1'@saturation=0.8"
            ),
            ColorGrade.COOL_BLUE: "colorbalance=ps=balance=-0.1:cs=balance=0.05",
            ColorGrade.NEUTRAL: None,
            ColorGrade.WARM_GOLD: "curves=all='0/0 0.3/0.28 0.6/0.58 1/1'@saturation=1.2",
            ColorGrade.HIGH_CONTRAST: "curves=all='0/0 0.2/0.15 0.5/0.5 0.8/0.85 1/1'",
        }
        return filters.get(grade)

    async def assemble_final_video(
        self,
        scenes: list[SceneComposition],
        output_path: str,
        target_resolution: tuple[int, int] = (1920, 1080),
        fps: int = 25
    ) -> VideoCompositionResult:
        """Assemble all scenes into a final video with transitions.

        Args:
            scenes: List of scene compositions in order
            output_path: Final output video path
            target_resolution: (width, height)
            fps: Frames per second

        Returns:
            VideoCompositionResult with success status and metadata
        """
        errors = []
        total_duration = 0.0

        # Step 1: Compose each scene individually
        logger.info(f"Composing {len(scenes)} scenes...")
        scene_files = []

        for i, scene in enumerate(scenes):
            scene_file = f"/tmp/movie_os_scene_{i:04d}.mp4"
            success = await self.compose_scene(scene, scene_file, target_resolution)

            if success:
                scene_files.append(scene_file)
                total_duration += scene.duration_seconds
            else:
                errors.append(f"Scene {scene.scene_number} composition failed")
                logger.error(f"Skipping scene {scene.scene_number}")

        if not scene_files:
            return VideoCompositionResult(
                output_path=output_path,
                total_duration=0,
                scene_count=len(scenes),
                success=False,
                errors=["No scenes composed successfully"]
            )

        # Step 2: Create concat list for final assembly
        concat_file = "/tmp/movie_os_concat.txt"
        with open(concat_file, "w") as f:
            for scene_file in scene_files:
                f.write(f"file '{scene_file}'\n")

        # Step 3: Concatenate all scenes
        concat_cmd = [
            self.ffmpeg, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            output_path
        ]

        try:
            logger.info(f"Assembling final video: {output_path} ({total_duration:.1f}s)")
            result = await asyncio.create_subprocess_exec(
                *concat_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                error_msg = stderr.decode()[:500] if stderr else "Unknown FFmpeg error"
                errors.append(f"Final assembly failed: {error_msg}")
                logger.error(f"Final assembly failed: {error_msg}")
                return VideoCompositionResult(
                    output_path=output_path,
                    total_duration=total_duration,
                    scene_count=len(scenes),
                    success=False,
                    errors=errors
                )

            # Clean up temp files
            for scene_file in scene_files:
                try:
                    os.unlink(scene_file)
                except OSError:
                    pass
            try:
                os.unlink(concat_file)
            except OSError:
                pass

            logger.info(f"Final video assembled: {output_path} ({total_duration:.1f}s)")
            return VideoCompositionResult(
                output_path=output_path,
                total_duration=total_duration,
                scene_count=len(scenes),
                success=True,
                errors=[]
            )

        except Exception as e:
            errors.append(f"Exception during assembly: {e}")
            logger.error(f"Assembly exception: {e}")
            return VideoCompositionResult(
                output_path=output_path,
                total_duration=total_duration,
                scene_count=len(scenes),
                success=False,
                errors=errors
            )

    async def burn_subtitles(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
        style: dict[str, Any] | None = None
    ) -> bool:
        """Burn subtitles into video using FFmpeg's assvideo filter.

        Args:
            video_path: Input video file
            subtitle_path: SRT or ASS subtitle file
            output_path: Output video with burned subtitles
            style: Subtitle styling options (font, size, color, position)

        Returns:
            True if successful
        """
        if style is None:
            style = {
                "font": "Arial",
                "font_size": 24,
                "color": "&Hffffff",  # White text
                "outline_color": "&H000000",  # Black outline
                "outline": 2,
                "position": "bottom"  # bottom, center, top
            }

        # Calculate position offset
        positions = {
            "bottom": "Y:H-text_h-30",
            "center": "Y:H/2",
            "top": "Y:30"
        }
        pos = positions.get(style.get("position", "bottom"), "Y:H-text_h-30")

        cmd = [
            self.ffmpeg, "-y",
            "-i", video_path,
            "-vf", f"subtitles={subtitle_path}:force_style='Fontname={style['font']},FontSize={style['font_size']},PrimaryColour={style['color']},OutlineColour={style['outline_color']},Outline={style['outline']},Alignment=2,MarginV=10'",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            output_path
        ]

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                logger.error(f"Subtitle burning failed: {stderr.decode()[:500] if stderr else 'Unknown error'}")
                return False

            logger.info(f"Subtitles burned into {output_path}")
            return True

        except Exception as e:
            logger.error(f"Exception burning subtitles: {e}")
            return False


__all__ = [
    "FFmpegEngine",
    "FFmpegError",
    "ColorGrade",
    "TransitionType",
    "KenBurnsEffect",
    "AudioLayer",
    "SceneComposition",
    "VideoCompositionResult",
]
