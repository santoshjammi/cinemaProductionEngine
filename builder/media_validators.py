"""
media_validators — ffprobe-driven validators for image, audio, and MP4 streams.

All checks use subprocessed ffprobe with JSON output arrays (no grep, no shell pipes).
Each validator returns a result dict: {"valid": bool, "details": {}} or raises ValidatorError.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class ValidatorResult:
    valid: bool
    details: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.valid = False
        self.errors.append(msg)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ValidatorError(Exception):
    message: str
    context: dict = field(default_factory=dict)

    def __str__(self):
        ctx = ", ".join(f"{k}={v}" for k, v in self.context.items())
        base = f"ValidatorError: {self.message}"
        return f"{base} [{ctx}]" if ctx else base


class ImageValidator:
    """Validate image files using ffprobe with JSON output."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def validate(self) -> ValidatorResult:
        result = ValidatorResult(valid=True)
        details: dict[str, Any] = {}

        # 1. File exists
        if not self.filepath.exists():
            result.add_error(f"File does not exist: {self.filepath}")
            return result

        # 2. Regular file with non-zero size
        if not self.filepath.is_file():
            result.add_error(f"Not a regular file: {self.filepath}")
            return result

        size = self.filepath.stat().st_size
        details["size_bytes"] = size
        if size == 0:
            result.add_error("File has zero size")
            return result

        # 3. Probe via ffprobe JSON
        try:
            probe_cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,pix_fmt,codec_name,r_frame_rate,nb_read_frames",
                "-show_entries", "format=format_name,duration",
                "-of", "json",
                str(self.filepath),
            ]
            proc = subprocess.run(
                probe_cmd,
                capture_output=True,
                text=False,
                timeout=30,
            )
            if proc.returncode != 0:
                result.add_error(f"ffprobe failed: {proc.stderr.decode()[:500]}")
                return result

            data = json.loads(proc.stdout)
            streams = data.get("streams", [])
            formats = data.get("format", {})

        except subprocess.TimeoutExpired:
            result.add_error(f"ffprobe timed out after 30s for {self.filepath}")
            return result
        except (json.JSONDecodeError, KeyError) as e:
            result.add_error(f"Failed to parse ffprobe JSON: {e}")
            return result

        # 4. Format check
        fmt_name = formats.get("format_name", "")
        details["format"] = fmt_name
        if not fmt_name:
            result.add_error("No format detected by ffprobe")
            return result

        recognized_formats = ("png", "jpeg", "mjpeg", "bmp", "gif")
        is_image_format = any(fmt in fmt_name for fmt in recognized_formats) or "image" in fmt_name.lower()
        details["is_image_format"] = is_image_format
        if not is_image_format:
            result.add_error(f"Unrecognized image format: {fmt_name}")
            return result

        # 5. Stream check
        if not streams:
            result.add_error("No video stream found")
            return result

        stream = streams[0]

        # 6. Valid stream with codec
        codec = stream.get("codec_name", "")
        details["codec"] = codec
        if not codec:
            result.add_error("Stream has no codec_name")
            return result

        valid_codecs = ("png", "jpeg", "mjpeg", "bmp", "gif", "webp")
        if codec not in valid_codecs:
            result.add_error(f"Unrecognized image codec: {codec}")
            return result

        # 7. Valid dimensions
        width = stream.get("width", 0)
        height = stream.get("height", 0)
        details["dimensions"] = f"{width}x{height}"
        if not isinstance(width, int) or not isinstance(height, int):
            result.add_error("Width or height is not an integer")
            return result
        if width == 0 or height == 0:
            result.add_error(f"Invalid dimensions: {width}x{height}")
            return result

        result.details = details
        return result


class AudioValidator:
    """Validate audio files using ffprobe with JSON output arrays."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def validate(self) -> ValidatorResult:
        result = ValidatorResult(valid=True)
        details: dict[str, Any] = {}

        # 1. File exists
        if not self.filepath.exists():
            result.add_error(f"File does not exist: {self.filepath}")
            return result

        # 2. Regular file, non-zero size
        if not self.filepath.is_file():
            result.add_error(f"Not a regular file: {self.filepath}")
            return result

        size = self.filepath.stat().st_size
        details["size_bytes"] = size
        if size == 0:
            result.add_error("File has zero size")
            return result

        # 3. Probe format and streams via ffprobe JSON
        try:
            probe_cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=codec_name,sample_rate,channels,bit_rate,channel_layout",
                "-show_entries", "format=format_name,duration,nb_streams",
                "-of", "json",
                str(self.filepath),
            ]
            proc = subprocess.run(
                probe_cmd,
                capture_output=True,
                text=False,
                timeout=30,
            )
            if proc.returncode != 0:
                result.add_error(f"ffprobe failed: {proc.stderr.decode()[:500]}")
                return result

            data = json.loads(proc.stdout)
            streams = data.get("streams", [])
            formats = data.get("format", {})

        except subprocess.TimeoutExpired:
            result.add_error(f"ffprobe timed out after 30s for {self.filepath}")
            return result
        except (json.JSONDecodeError, KeyError) as e:
            result.add_error(f"Failed to parse ffprobe JSON: {e}")
            return result

        # 4. Format check
        fmt_name = formats.get("format_name", "")
        details["format"] = fmt_name
        if not fmt_name:
            result.add_error("No format detected by ffprobe")
            return result

        recognized_audio_formats = ("wav", "mp3", "m4a", "flac", "ogg", "aac", "webm")
        is_audio_format = any(fmt in fmt_name for fmt in recognized_audio_formats) or "audio" in fmt_name.lower()
        details["is_audio_format"] = is_audio_format
        if not is_audio_format:
            result.add_error(f"Unrecognized audio format: {fmt_name}")
            return result

        # 5. Duration check
        duration_str = formats.get("duration", "0")
        try:
            duration = float(duration_str)
        except (ValueError, TypeError):
            duration = 0.0
        details["duration_seconds"] = duration
        if duration <= 0:
            result.add_error(f"Duration is zero or negative: {duration}")
            return result

        # 6. Stream check
        if not streams:
            result.add_error("No audio stream found")
            return result

        stream = streams[0]

        # 7. Codec validation
        codec = stream.get("codec_name", "")
        details["codec"] = codec
        valid_audio_codecs = (
            "pcm_s16le", "pcm_s24le", "pcm_f32le",
            "mp3", "aac", "flac", "opus", "vorbis",
            "eac3", "ac3",
        )
        if codec not in valid_audio_codecs:
            result.add_error(f"Unrecognized audio codec: {codec}")
            return result

        # 8. Channels and sample rate
        channels = stream.get("channels", 0)
        sr_str = stream.get("sample_rate", "0")
        try:
            sample_rate = int(sr_str)
        except (ValueError, TypeError):
            sample_rate = 0
        details["channels"] = channels
        details["sample_rate"] = sample_rate

        # 9. Silence check — decode and inspect audio amplitude
        is_silent = self._check_silence(self.filepath)
        details["is_silent"] = is_silent
        if is_silent:
            result.add_error("Audio stream is silent (no audible signal)")
            return result

        result.details = details
        return result

    @staticmethod
    def _check_silence(filepath: Path, threshold_db: float = -60.0) -> bool:
        """Check if audio is effectively silent using ffprobe volumedetect."""
        try:
            probe_cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "stream=channels,sample_rate",
                "-of", "json",
                str(filepath),
            ]
            proc = subprocess.run(probe_cmd, capture_output=True, text=False, timeout=30)
            if proc.returncode != 0:
                return False

            data = json.loads(proc.stdout)
            streams = data.get("streams", [])
            stream = streams[0] if streams else {}

            channels = stream.get("channels", 1) or 1
            sr = stream.get("sample_rate", "44100")

            # Use volumedetect to measure audio level
            vol_cmd = [
                "ffmpeg",
                "-v", "error",
                "-i", str(filepath),
                "-af", f"volumedetect=max_volume={threshold_db}",
                "-f", "null", "-",
            ]
            proc2 = subprocess.run(vol_cmd, capture_output=True, text=True, timeout=60)
            output = proc2.stderr or ""

            # Parse max_volume from volumedetect output
            for line in output.splitlines():
                if "max_volume" in line:
                    try:
                        # Format: "[Parsed_volumedetect_0 @ ...] max_volume:-XX.X dB"
                        parts = line.split(":")
                        val_str = parts[-1].strip().replace(" dB", "")
                        val = float(val_str)
                        return val <= threshold_db
                    except (ValueError, IndexError):
                        continue

            # If no volumedetect data found, assume not silent
            return False

        except (subprocess.TimeoutExpired, Exception):
            return False


class MP4Validator:
    """Validate final MP4 output using ffprobe JSON output arrays."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def validate(self) -> ValidatorResult:
        result = ValidatorResult(valid=True)
        details: dict[str, Any] = {}

        # 1. File exists
        if not self.filepath.exists():
            result.add_error(f"File does not exist: {self.filepath}")
            return result

        # 2. Regular file, non-zero size
        if not self.filepath.is_file():
            result.add_error(f"Not a regular file: {self.filepath}")
            return result

        size = self.filepath.stat().st_size
        details["size_bytes"] = size
        if size == 0:
            result.add_error("File has zero size")
            return result

        # 3. Full format probe — JSON output
        try:
            fmt_cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=format_name,duration,nb_streams,size",
                "-of", "json",
                str(self.filepath),
            ]
            proc_fmt = subprocess.run(fmt_cmd, capture_output=True, text=False, timeout=30)
            if proc_fmt.returncode != 0:
                result.add_error(f"ffprobe format probe failed: {proc_fmt.stderr.decode()[:500]}")
                return result

            fmt_data = json.loads(proc_fmt.stdout)
            fmt_info = fmt_data.get("format", {})
            fmt_name = fmt_info.get("format_name", "")
            details["format"] = fmt_name
            details["nb_streams"] = int(fmt_info.get("nb_streams", 0))

        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as e:
            result.add_error(f"Format probe failed: {e}")
            return result

        # 4. Format check — must be mp4 or mov
        recognized_mp4_formats = ("mp4", "mov", "matroska", "mpegts")
        is_mp4_format = any(fmt in fmt_name for fmt in recognized_mp4_formats)
        details["is_mp4_format"] = is_mp4_format
        if not is_mp4_format:
            result.add_error(f"Output format '{fmt_name}' does not appear to be MP4/MOV")
            return result

        # 5. Duration check
        dur_str = fmt_info.get("duration", "0")
        try:
            duration = float(dur_str)
        except (ValueError, TypeError):
            duration = 0.0
        details["duration_seconds"] = duration
        if duration <= 0:
            result.add_error(f"MP4 duration is zero or negative: {duration}")
            return result

        # 6. Full stream probe — JSON output array per stream
        try:
            stream_cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "stream=index,codec_type,codec_name,width,height,sample_rate,channels,r_frame_rate,bit_rate",
                "-show_entries", "stream_disposition=default,detached",
                "-of", "json",
                str(self.filepath),
            ]
            proc_streams = subprocess.run(stream_cmd, capture_output=True, text=False, timeout=30)
            if proc_streams.returncode != 0:
                result.add_error(f"ffprobe stream probe failed: {proc_streams.stderr.decode()[:500]}")
                return result

            streams_data = json.loads(proc_streams.stdout)
            all_streams = streams_data.get("streams", [])

        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as e:
            result.add_error(f"Stream probe failed: {e}")
            return result

        # 7. Check for video and audio streams
        has_video = False
        has_audio = False
        video_streams: list[dict] = []
        audio_streams: list[dict] = []

        for s in all_streams:
            codec_type = s.get("codec_type", "")
            if codec_type == "video":
                has_video = True
                video_streams.append(s)
                details[f"video_stream_{s.get('index', '?')}"] = {
                    "codec": s.get("codec_name"),
                    "width": s.get("width"),
                    "height": s.get("height"),
                    "frame_rate": s.get("r_frame_rate"),
                }
            elif codec_type == "audio":
                has_audio = True
                audio_streams.append(s)
                details[f"audio_stream_{s.get('index', '?')}"] = {
                    "codec": s.get("codec_name"),
                    "sample_rate": s.get("sample_rate"),
                    "channels": s.get("channels"),
                }

        if not has_video:
            result.add_error("MP4 does not contain a video stream")
            return result
        if not has_audio:
            result.add_error("MP4 does not contain an audio stream")
            return result

        details["has_video"] = True
        details["has_audio"] = True

        # 8. Validate video dimensions are reasonable (> 0)
        for vs in video_streams:
            w = vs.get("width", 0)
            h = vs.get("height", 0)
            if isinstance(w, int) and isinstance(h, int) and (w == 0 or h == 0):
                result.add_error(f"Invalid video dimensions: {w}x{h}")
                return result

        # 9. Audio silence check for MP4 streams using ffmpeg decode + volumedetect
        if audio_streams:
            silent_flag = False
            for as_ in audio_streams:
                try:
                    vol_cmd = [
                        "ffmpeg",
                        "-v", "error",
                        "-i", str(self.filepath),
                        "-map", f"a:{as_.get('index', 0)}",
                        "-af", "volumedetect=max_volume=-60",
                        "-f", "null", "-",
                    ]
                    proc_vol = subprocess.run(vol_cmd, capture_output=True, text=True, timeout=60)
                    output = proc_vol.stderr or ""
                    is_stream_silent = False
                    for line in output.splitlines():
                        if "max_volume" in line:
                            parts = line.split(":")
                            val_str = parts[-1].strip().replace(" dB", "")
                            try:
                                val = float(val_str)
                                is_stream_silent = val <= -60.0
                            except ValueError:
                                pass
                            break
                    if is_stream_silent:
                        silent_flag = True
                except (subprocess.TimeoutExpired, Exception):
                    continue

            details["is_silent"] = silent_flag
            if silent_flag:
                result.add_error("Audio stream in MP4 is silent")
                return result

        # 10. Decoding check — brief decode pass to confirm media is decodable
        try:
            decode_cmd = [
                "ffmpeg",
                "-v", "error",
                "-i", str(self.filepath),
                "-f", "null", "-",
            ]
            proc_decode = subprocess.run(decode_cmd, capture_output=True, text=True, timeout=120)
            if proc_decode.returncode != 0:
                result.add_error(f"MP4 failed decode test: {proc_decode.stderr[:500]}")
                return result
        except subprocess.TimeoutExpired:
            pass  # Large files may timeout — that's okay

        result.details = details
        return result


class ComfyUIWorkflowValidator:
    """Validate ComfyUI API workflow JSON files."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def validate(self) -> ValidatorResult:
        result = ValidatorResult(valid=True)
        details: dict[str, Any] = {}

        # 1. File exists and is JSON
        if not self.filepath.exists():
            result.add_error(f"File does not exist: {self.filepath}")
            return result

        if not self.filepath.is_file():
            result.add_error(f"Not a regular file: {self.filepath}")
            return result

        try:
            with open(self.filepath, "r") as f:
                workflow = json.load(f)
        except json.JSONDecodeError as e:
            result.add_error(f"Invalid JSON: {e}")
            return result
        except Exception as e:
            result.add_error(f"Cannot read file: {e}")
            return result

        if not isinstance(workflow, dict):
            result.add_error("Workflow root is not a dictionary")
            return result

        details["node_count"] = len(workflow)
        if len(workflow) == 0:
            result.add_error("Workflow has zero nodes")
            return result

        # 2. Required node classes check
        required_classes = set()
        prompt_class = None
        output_node = None
        model_refs: list[str] = []

        class_types_found: dict[str, int] = {}

        for node_id, node_data in workflow.items():
            if not isinstance(node_data, dict):
                result.add_error(f"Node '{node_id}' is not a dictionary")
                return result

            class_type = node_data.get("class_type", "")
            if not class_type:
                result.add_error(f"Node '{node_id}' missing 'class_type'")
                return result

            class_types_found[class_type] = class_types_found.get(class_type, 0) + 1

        # 3. Check for prompt-related nodes (text input with prompt data)
        has_prompt = False
        for node_id, node_data in workflow.items():
            inputs = node_data.get("inputs", {})
            if "text" in inputs and isinstance(inputs["text"], str) and len(inputs["text"]) > 0:
                has_prompt = True
                break

        details["has_positive_prompt"] = has_prompt
        if not has_prompt:
            result.add_error("Workflow contains no positive prompt text")
            return result

        # 4. Check for output node (SaveImage or PreviewImage)
        output_classes = {"SaveImage", "PreviewImage", "SaveAnimatedGIF"}
        found_output = False
        for ct in class_types_found:
            if ct in output_classes:
                found_output = True
                break

        details["has_output_node"] = found_output
        if not found_output:
            result.add_error("Workflow has no output node (SaveImage/PreviewImage)")
            return result

        # 5. Model file references check
        for node_id, node_data in workflow.items():
            inputs = node_data.get("inputs", {})
            for key, val in inputs.items():
                if isinstance(val, str) and val.endswith(".safetensors"):
                    model_refs.append(val)

        # If the workflow uses named model references (like "FLUX_BF16"), those are looked up by ComfyUI's folder_paths.
        # We check for .safetensors filenames as explicit references.
        details["model_references"] = model_refs

        # 6. Check for sampler node (KSampler or similar)
        has_sampler = False
        for ct in class_types_found:
            if "sampler" in ct.lower() or "k_sample" in ct.lower():
                has_sampler = True
                break

        details["has_sampler"] = has_sampler
        if not has_sampler:
            result.add_error("Workflow has no sampler node")
            return result

        # 7. Check for VAE decode step (required before SaveImage)
        has_vae_decode = False
        has_text_encoder = False
        for ct in class_types_found:
            if "VAEDecode" in ct:
                has_vae_decode = True
            if "CLIP" in ct or "text_encoder" in ct.lower():
                has_text_encoder = True

        details["has_vae_decode"] = has_vae_decode
        details["has_text_encoder"] = has_text_encoder

        result.details = {**details, "class_types": class_types_found}
        return result


def validate_scene_package(package_dir: str | Path) -> ValidatorResult:
    """Validate that a sealed scene package contains all required artifacts."""
    result = ValidatorResult(valid=True)
    details: dict[str, Any] = {}

    pkg = Path(package_dir)

    required_specs = {
        "scene_specification": pkg / "scene.json",
        "dialogue_specification": pkg / "dialogue.json",
        "shot_specification": None,  # May be absent — we'll note it
        "image_prompt": pkg / "image_prompt.json",
        "video_prompt": None,  # Optional for image-to-video scenes
        "audio_prompt": pkg / "audio_prompt.json",
        "timing_plan": None,  # May be absent
    }

    for label, path in required_specs.items():
        if path is None:
            details[f"{label}_status"] = "not_required"
            continue

        exists = path.exists() and path.is_file()
        size = path.stat().st_size if exists else 0
        details[f"{label}_exists"] = exists
        details[f"{label}_size_bytes"] = size

        if not exists:
            result.add_error(f"Missing required spec: {path.name}")
        elif size == 0:
            result.add_error(f"Empty spec file: {path.name}")

    # Validate each JSON spec can be parsed
    for label, path in [l for l in required_specs.items() if l[1] and l[1].exists()]:
        try:
            with open(path) as f:
                json.load(f)
            details[f"{label}_valid_json"] = True
        except json.JSONDecodeError:
            result.add_error(f"Invalid JSON in {label}")
            details[f"{label}_valid_json"] = False

    # Check for absent but useful specs
    timing_path = pkg / "timing_plan.json"
    shot_path = pkg / "shot_specification.json"

    if not timing_path.exists():
        result.add_error("Missing optional but important: timing_plan.json")
    if not shot_path.exists():
        result.add_error("Missing optional but important: shot_specification.json")

    result.details = details
    return result


def validate_manifest(package_dir: str | Path) -> ValidatorResult:
    """Validate the scene manifest requires validation_status: passed, package_sealed: true, builder_admission: approved."""
    result = ValidatorResult(valid=True)
    details: dict[str, Any] = {}

    manifest_path = Path(package_dir) / "manifest.json"

    if not manifest_path.exists():
        # Try .yaml extension
        manifest_path = Path(package_dir) / "manifest.yaml"

    if not manifest_path.exists():
        result.add_error("No manifest.json or manifest.yaml found")
        return result

    try:
        with open(manifest_path, "r") as f:
            raw = json.load(f)
        details["source"] = str(manifest_path)
    except json.JSONDecodeError:
        # Try YAML (simple key-value extraction)
        try:
            with open(manifest_path, "r") as f:
                raw = {}
                for line in f:
                    line = line.strip()
                    if ":" in line and not line.startswith("#"):
                        k, v = line.split(":", 1)
                        k = k.strip().strip('"')
                        v = v.strip().strip('"').strip("'")
                        raw[k] = v
            details["source"] = str(manifest_path)
        except Exception as e:
            result.add_error(f"Cannot parse manifest: {e}")
            return result

    validation_status = raw.get("validation_status", "").lower()
    package_sealed = raw.get("package_sealed", False)
    builder_admission = raw.get("builder_admission", "").lower()

    details["validation_status"] = validation_status
    details["package_sealed"] = bool(package_sealed)
    details["builder_admission"] = builder_admission

    # Enforce strict admission criteria
    if validation_status != "passed":
        result.add_error(f"manifest.validation_status must be 'passed', got '{validation_status}'")

    if not bool(package_sealed):
        result.add_error("manifest.package_sealed must be true")

    if builder_admission != "approved":
        result.add_error(f"manifest.builder_admission must be 'approved', got '{builder_admission}'")

    result.details = details
    return result
