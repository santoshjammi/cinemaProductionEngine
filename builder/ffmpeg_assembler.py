"""
ffmpeg_assembler — Assemble the final MP4 from image and mixed audio.

Operations:
  - Generate video frames from source image(s)
  - Sync with mixed audio duration
  - Encode to MP4 (H.264 video, AAC audio) using ffprobe-validated parameters
  - Final validation of output MP4 streams and metadata

No shell pipelines or grep — all subprocess calls use argument arrays.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class AssemblyResult:
    success: bool
    output_path: str | None = None
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


# ---------------------------------------------------------------------------
# FFmpeg subprocess helpers (no shell pipes)
# ---------------------------------------------------------------------------

def _run_ffmpeg(args: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    """Run ffmpeg with argument array. No shell=True."""
    return subprocess.run(
        ["ffmpeg", "-y"] + args,
        capture_output=True, text=False, timeout=timeout
    )


def _run_ffprobe(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Run ffprobe with argument array. No shell=True."""
    return subprocess.run(
        ["ffprobe", "-v", "error"] + args,
        capture_output=True, text=False, timeout=timeout
    )


# ---------------------------------------------------------------------------
# Video frame generation from image
# ---------------------------------------------------------------------------

class ImageToFrames:
    """Convert source images to a frame sequence for FFmpeg input."""

    @staticmethod
    def generate_from_image(
        source_image: str | Path,
        target_duration_seconds: float,
        fps: int = 30,
        output_dir: Path | str | None = None,
        image_dimensions: tuple[int, int] | None = None,
    ) -> list[str]:
        """Generate a frame sequence from a single source image.

        Returns list of temporary frame files for FFmpeg input.
        Uses ffmpeg's loop + filter_complex to create seamless frames.
        """
        img_path = Path(source_image)
        if not img_path.exists():
            raise FileNotFoundError(f"Source image not found: {source_image}")

        # Get image dimensions via ffprobe
        if image_dimensions is None:
            probe_cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                str(img_path),
            ]
            proc = _run_ffprobe(probe_cmd)
            if proc.returncode == 0:
                data = json.loads(proc.stdout)
                stream = data.get("streams", [{}])[0]
                image_dimensions = (stream.get("width", 1920), stream.get("height", 1080))
            else:
                image_dimensions = (1920, 1080)

        # Use ffmpeg to create a single continuous video file directly
        # rather than frame-by-frame output
        if output_dir is None:
            output_dir = Path("/tmp/video_frames")

        # Generate frame sequence as YUV or PNG frames
        odir = Path(output_dir)
        odir.mkdir(parents=True, exist_ok=True)
        temp_frames = []

        n_frames = int(fps * target_duration_seconds)

        for i in range(n_frames):
            frame_path = odir / f"frame_{i:04d}.png"
            # Copy source image with timestamp info for FFmpeg input
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-t", f"{target_duration_seconds}",
                 "-i", str(img_path),
                 "-vf", f"fps={fps},scale={image_dimensions[0]}:{image_dimensions[1]}",
                 "-frames:v", "1",
                 str(frame_path)],
                capture_output=True, timeout=30
            )
            if frame_path.exists():
                temp_frames.append(str(frame_path))

        return temp_frames


# ---------------------------------------------------------------------------
# Main FFmpeg Assembler
# ---------------------------------------------------------------------------

class FFmpegAssembler:
    """Assemble image frames + mixed audio into final MP4."""

    def __init__(self, fps: int = 30):
        self.fps = fps

    def assemble(
        self,
        source_image: str | Path,
        mixed_audio: str | Path,
        target_duration_seconds: float,
        output_path: str | Path,
        image_dimensions: tuple[int, int] | None = None,
        silence_specs: list[dict[str, Any]] | None = None,
    ) -> AssemblyResult:
        """Assemble the final scene MP4 from image and audio.

        FFmpeg command construction (argument arrays only):
          ffmpeg -y \
            -loop 1 -i SOURCE_IMAGE -i MIXED_AUDIO \
            -filter_complex "[0:v]scale=W:H,fps=F,format=yuv420p[v]; \
                             [1:a]volume=1.0[a]" \
            -map "[v]" -map "[a]" \
            -c:v libx264 -preset slow -crf 18 \
            -pix_fmt yuv420p \
            -t DURATION \
            OUTPUT.mp4
        """

        img_path = Path(source_image)
        audio_path = Path(mixed_audio)
        out_path = Path(output_path)

        # --- Pre-flight checks using ffprobe (JSON output) ---

        # Validate source image via ffprobe
        if not img_path.exists():
            return AssemblyResult(success=False, error=f"Source image missing: {source_image}")

        img_probe_cmd = [
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,pix_fmt,codec_name",
            "-of", "json",
            str(img_path),
        ]
        proc = _run_ffprobe(img_probe_cmd)
        if proc.returncode != 0:
            return AssemblyResult(success=False, error=f"Image probe failed: {proc.stderr.decode()[:200]}")

        img_data = json.loads(proc.stdout)
        img_stream = img_data.get("streams", [{}])[0]
        width = img_stream.get("width", 1920)
        height = img_stream.get("height", 1080)
        image_dimensions = (width, height)

        # Validate audio file via ffprobe
        if not audio_path.exists():
            return AssemblyResult(success=False, error=f"Audio file missing: {mixed_audio}")

        aud_probe_cmd = [
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name,sample_rate,channels,duration,format=format_name,duration,nb_streams",
            "-of", "json",
            str(audio_path),
        ]
        proc = _run_ffprobe(aud_probe_cmd)
        if proc.returncode != 0:
            return AssemblyResult(success=False, error=f"Audio probe failed: {proc.stderr.decode()[:200]}")

        aud_data = json.loads(proc.stdout)
        aud_stream = aud_data.get("streams", [{}])[0]
        audio_codec = aud_stream.get("codec_name", "")
        audio_sr = aud_stream.get("sample_rate", 44100)
        audio_channels = aud_stream.get("channels", 1)

        # --- FFmpeg assembly (argument arrays, no shell pipes) ---

        # Ensure output directory exists
        out_path.parent.mkdir(parents=True, exist_ok=True)

        filter_complex_parts = []

        # Video: scale + fps + pixel format
        vf_str = f"fps={self.fps},scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p"
        filter_complex_parts.append(f"[0:v]{vf_str}[v]")

        # Audio: ensure correct sample rate and channels for AAC encoding
        af_str = f"aresample={audio_sr},aformat=sample_fmts=s16:channel_layouts=stereo"
        filter_complex_parts.append(f"[1:a]{af_str}[a]")

        filter_complex = ";".join(filter_complex_parts)

        cmd = [
            "-loop", "1",
            "-t", str(target_duration_seconds),
            "-i", str(img_path),
            "-i", str(audio_path),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", str(audio_sr),
            "-ac", "2",  # Stereo output
            "-movflags", "+faststart",  # For web streaming
            str(out_path),
        ]

        proc = _run_ffmpeg(cmd, timeout=300)
        if proc.returncode != 0:
            return AssemblyResult(
                success=False,
                error=f"FFmpeg assembly failed (rc={proc.returncode}): {proc.stderr.decode()[:500]}",
                details={"command": " ".join(str(a) for a in cmd)},
            )

        # --- Post-assembly validation ---
        if not out_path.exists():
            return AssemblyResult(success=False, error="Output MP4 not created")

        size = out_path.stat().st_size
        if size == 0:
            return AssemblyResult(success=False, error="Output MP4 has zero size")

        # Validate output via ffprobe (JSON output)
        final_probe_cmd = [
            "-show_entries", "stream=index,codec_type,codec_name,width,height,sample_rate,channels,r_frame_rate",
            "-show_entries", "format=format_name,duration,nb_streams,size",
            "-of", "json",
            str(out_path),
        ]
        proc = _run_ffprobe(final_probe_cmd)
        if proc.returncode != 0:
            return AssemblyResult(
                success=False,
                error=f"Final validation probe failed: {proc.stderr.decode()[:200]}",
                details={"command": " ".join(str(a) for a in cmd)},
            )

        final_data = json.loads(proc.stdout)
        fmt_info = final_data.get("format", {})
        all_streams = final_data.get("streams", [])

        has_video = any(s.get("codec_type") == "video" for s in all_streams)
        has_audio = any(s.get("codec_type") == "audio" for s in all_streams)

        if not has_video:
            return AssemblyResult(
                success=False,
                error="Output MP4 missing video stream",
                details={"command": " ".join(str(a) for a in cmd)},
            )
        if not has_audio:
            return AssemblyResult(
                success=False,
                error="Output MP4 missing audio stream",
                details={"command": " ".join(str(a) for a in cmd)},
            )

        # Collect detailed stream info
        video_streams = []
        audio_streams_list = []
        for s in all_streams:
            if s.get("codec_type") == "video":
                video_streams.append({
                    "index": s.get("index"),
                    "codec": s.get("codec_name"),
                    "width": s.get("width"),
                    "height": s.get("height"),
                    "frame_rate": s.get("r_frame_rate"),
                })
            elif s.get("codec_type") == "audio":
                audio_streams_list.append({
                    "index": s.get("index"),
                    "codec": s.get("codec_name"),
                    "sample_rate": s.get("sample_rate"),
                    "channels": s.get("channels"),
                })

        result_duration = float(fmt_info.get("duration", 0))

        return AssemblyResult(
            success=True,
            output_path=str(out_path),
            details={
                "command_args": [str(a) for a in cmd],
                "output_size_bytes": size,
                "format": fmt_info.get("format_name"),
                "duration_seconds": result_duration,
                "nb_streams": fmt_info.get("nb_streams"),
                "video_streams": video_streams,
                "audio_streams": audio_streams_list,
                "image_dimensions": list(image_dimensions),
                "fps": self.fps,
                "video_codec": "libx264",
                "audio_codec": "aac",
            },
        )


# ---------------------------------------------------------------------------
# Final MP4 Validator (wraps media_validators.MP4Validator)
# ---------------------------------------------------------------------------

def validate_final_mp4(filepath: str | Path) -> AssemblyResult:
    """Validate the final assembled MP4 against all criteria."""
    from builder.media_validators import MP4Validator

    val = MP4Validator(filepath)
    result = val.validate()

    return AssemblyResult(
        success=result.valid,
        output_path=str(filepath),
        error=None if result.valid else "; ".join(result.errors),
        details=result.to_dict(),
    )
