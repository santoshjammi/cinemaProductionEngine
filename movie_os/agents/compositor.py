"""ffmpeg composition utilities — Ken Burns + concat for the publishing agent.

Each scene is composed as:
  1. (Optional) Ken Burns pan/zoom over the scene's first shot image
  2. Voiceover mixed with music (if available)
  3. Concatenated into the final video

We use ffmpeg's `panzoom` filter for Ken Burns, `amix` for audio
mixing, and the `concat` demuxer for joining scenes.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any


logger = logging.getLogger("movie_os.agents.compositor")


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess, log stderr on failure."""
    logger.debug(f"ffmpeg: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, check=check,
            capture_output=True, text=True,
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg failed: {e.stderr[-1000:] if e.stderr else str(e)}")
        if check:
            raise
        return e


def probe_duration(path: str | Path) -> float:
    """Get the duration of a media file in seconds (0.0 if not found)."""
    path = Path(path)
    if not path.exists():
        return 0.0
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def render_scene_clip(
    image_path: str | Path,
    duration_seconds: float,
    output_path: str | Path,
    *,
    width: int = 1024,
    height: int = 576,
    fps: int = 24,
    voice_path: str | Path | None = None,
    music_path: str | Path | None = None,
    music_volume: float = 0.3,
    ken_burns: str = "ken-burns",  # "ken-burns" | "zoom-in" | "zoom-out" | "pan-left" | "pan-right" | "static"
    sharpen: bool = True,
) -> Path:
    """Render a single scene clip (image + audio) as a video segment.

    Args:
        image_path: Source image (PNG/JPG).
        duration_seconds: Target duration.
        output_path: Where to write the segment.
        width, height: Output dimensions (must be even). Default 1024x576.
        fps: Frames per second.
        voice_path: Optional voiceover wav to mix in.
        music_path: Optional music bed wav to mix in.
        music_volume: Music volume (0.0 to 1.0). Default 0.3.
        ken_burns: Pan/zoom effect — see v5.1 fade engine.
        sharpen: Apply unsharp filter for crispness. Default True.

    Returns:
        Path to the output segment.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    width = (width // 2) * 2
    height = (height // 2) * 2

    # Build the video filter — start with a Ken Burns pan/zoom
    if ken_burns in ("ken-burns", "zoom-in", None, ""):
        vf = (
            f"scale=2*iw:2*ih,"
            f"zoompan=z='min(zoom+0.0015,1.5)':d={int(duration_seconds * fps)}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s={width}x{height}:fps={fps},"
            f"format=yuv420p"
        )
    elif ken_burns == "zoom-out":
        vf = (
            f"scale=2*iw:2*ih,"
            f"zoompan=z='if(eq(on,0),1.5,max(1.0,zoom-0.0015))':"
            f"d={int(duration_seconds * fps)}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s={width}x{height}:fps={fps},"
            f"format=yuv420p"
        )
    elif ken_burns == "pan-left":
        vf = (
            f"scale=2*iw:2*ih,"
            f"zoompan=z=1.2:x='if(eq(on,0),iw,min(iw,x-2))':"
            f"d={int(duration_seconds * fps)}:"
            f"y='ih/2-(ih/zoom/2)':"
            f"s={width}x{height}:fps={fps},"
            f"format=yuv420p"
        )
    elif ken_burns == "pan-right":
        vf = (
            f"scale=2*iw:2*ih,"
            f"zoompan=z=1.2:x='if(eq(on,0),0,min(iw,x+2))':"
            f"d={int(duration_seconds * fps)}:"
            f"y='ih/2-(ih/zoom/2)':"
            f"s={width}x{height}:fps={fps},"
            f"format=yuv420p"
        )
    else:  # static
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,"
            f"format=yuv420p"
        )
    if sharpen:
        vf = vf + ",unsharp=5:5:1.0:5:5:0.0"

    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
           "-t", f"{duration_seconds:.3f}",
           "-vf", vf,
           "-r", str(fps),
           "-an",  # no audio in this pass
           "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
           str(output_path)]

    try:
        _run(cmd)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ken Burns render failed: {e.stderr[:300] if e.stderr else e}")
        # Fallback to static render
        if ken_burns != "static":
            return render_scene_clip(
                image_path, duration_seconds, output_path,
                width=width, height=height, fps=fps,
                voice_path=voice_path, music_path=music_path,
                music_volume=music_volume, ken_burns="static",
            )
        raise

    # Now add audio if we have any, otherwise mix silent audio so stream counts match
    if voice_path or music_path:
        _mix_audio_into_clip(
            output_path, duration_seconds,
            voice_path=voice_path,
            music_path=music_path,
            music_volume=music_volume,
            output_path=output_path,  # in-place
        )
    else:
        _mix_silent_audio(output_path, duration_seconds)
    return output_path


def _mix_silent_audio(video_path: str | Path, duration_seconds: float) -> None:
    """Mix a silent audio track of duration_seconds into the video in-place."""
    target = Path(str(video_path) + ".tmp.mp4")
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-map", "0:v", "-map", "1:a",
        "-t", f"{duration_seconds:.3f}",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(target)
    ]
    try:
        _run(cmd)
        shutil.move(target, video_path)
    except subprocess.CalledProcessError as e:
        logger.warning(f"Silent audio mix failed: {e.stderr[-1000:] if e.stderr else str(e)}")


def _mix_audio_into_clip(
    video_path: str | Path,
    duration_seconds: float,
    *,
    voice_path: str | Path | None,
    music_path: str | Path | None,
    music_volume: float,
    output_path: str | Path,
) -> None:
    """Mix voice + music into the existing video clip (in place via temp file)."""
    inputs = ["ffmpeg", "-y", "-i", str(video_path)]
    filter_parts = []
    if voice_path and Path(voice_path).exists():
        inputs.extend(["-i", str(voice_path)])
        voice_idx = 1
    if music_path and Path(music_path).exists():
        inputs.extend(["-i", str(music_path)])
        music_idx = 2 if voice_path else 1

    # Build the amix filter
    mix_inputs = []
    if voice_path and Path(voice_path).exists():
        # Pad voice to scene duration, then trim
        filter_parts.append(
            f"[{voice_idx}:a]aresample=44100,apad,atrim=0:{duration_seconds:.3f},"
            f"asetpts=PTS-STARTPTS[voice]"
        )
        mix_inputs.append("[voice]")
    if music_path and Path(music_path).exists():
        # Loop music, lower volume, trim to scene duration
        filter_parts.append(
            f"[{music_idx}:a]aresample=44100,aloop=loop=-1:size=2e9,"
            f"volume={music_volume},atrim=0:{duration_seconds:.3f},"
            f"asetpts=PTS-STARTPTS[music]"
        )
        mix_inputs.append("[music]")

    if not mix_inputs:
        return  # nothing to mix

    if len(mix_inputs) == 1:
        # Just one track — use it directly
        filter_complex = ";".join(filter_parts)
        cmd = inputs + [
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", mix_inputs[0],
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(output_path) + ".tmp.mp4",
        ]
        target = Path(str(output_path) + ".tmp.mp4")
    else:
        # Mix voice and music
        filter_complex = (
            ";".join(filter_parts)
            + ";"
            + "".join(mix_inputs) + f"amix=inputs={len(mix_inputs)}:"
            f"duration=longest:normalize=0[mixed]"
        )
        cmd = inputs + [
            "-filter_complex", filter_complex,
            "-map", "0:v", "-map", "[mixed]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            str(output_path) + ".tmp.mp4",
        ]
        target = Path(str(output_path) + ".tmp.mp4")

    try:
        _run(cmd)
        shutil.move(target, output_path)
    except subprocess.CalledProcessError as e:
        logger.warning(f"Audio mix failed: {e.stderr[:200] if e.stderr else e}")


def concat_clips(clip_paths: list[str | Path], output_path: str | Path) -> Path:
    """Concatenate multiple video clips into a single video.

    Uses ffmpeg's concat demuxer. All clips must have the same
    resolution and codec — which they do, since we just rendered
    them with the same settings.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Write a concat list
    list_file = output_path.parent / f".{output_path.stem}_concat.txt"
    with open(list_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{Path(p).absolute()}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path),
    ]
    try:
        _run(cmd)
    except subprocess.CalledProcessError as e:
        # Fallback: re-encode
        logger.warning("Concat copy failed, re-encoding")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            str(output_path),
        ]
        _run(cmd)
    finally:
        list_file.unlink(missing_ok=True)
    return output_path
