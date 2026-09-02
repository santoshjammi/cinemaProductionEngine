"""Stage 6: Film — final export with real audio mixing AND video assembly.

Takes edited timeline artifacts and produces the final film video file,
combining all images, audio clips, and music tracks into a single output.

PROMETHEUS audio fixes (persistent):
  1. Dialogue-driven scene durations — scene length is driven by how much is
     actually said (lines placed back-to-back + short pause), NOT a fixed
     arbitrary duration that leaves 10s+ gaps of dead silence.
  2. Loudness normalization (loudnorm I=-16 TP=-1.5) so dialogue is clearly
     audible and not buried under music.

PROMETHEUS video fixes (persistent):
  3. Real video assembly — each scene image gets a Ken Burns (slow zoom/pan)
     over the mixed audio, then all scene clips are concatenated into the
     final film. Previously the stage only mixed audio and never produced a
     playable video file.
  4. Idempotency trap fixed — stale 0-byte mixed files are regenerated, not
     silently reused.
"""
from __future__ import annotations

import asyncio
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional

from movie_os.runtime_paths import build_run_path
from movie_os.providers.video.svd_local import render_with_svd

logger = logging.getLogger("movie_os.prometheus.stages.film")


def _probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=10)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def compute_scene_duration(voice_paths: list[Path], min_duration_s: float = 8.0,
                           pause_s: float = 0.7, tail_s: float = 2.0) -> float:
    """Compute a natural scene duration from the dialogue.

    Lines are placed back-to-back with a short pause between them, so the
    scene length is driven by how much is actually said — NOT a fixed
    arbitrary duration that leaves 10s+ gaps of dead silence.
    """
    total = 0.0
    for p in voice_paths:
        if p and p.exists():
            total += _probe_duration(p) + pause_s
    if total <= 0:
        return min_duration_s
    return max(min_duration_s, total + tail_s)


def mix_scene_audio(music_path: Path | None, voice_paths: list[Path],
                    out_path: Path, duration_s: float, emotion: str = "neutral") -> Path | None:
    """Mix music (ducked) + dialogue placed back-to-back with natural pauses.

    Fix: previously lines were spread evenly across a fixed scene duration,
    creating 10s+ gaps of dead silence between lines (not dialogue). Now each
    line starts immediately after the previous one ends (plus a short pause),
    so the conversation flows naturally. Then loudnorm normalizes the mix.

    Idempotency fix: a stale 0-byte (or tiny) out_path is regenerated rather
    than silently reused.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Idempotency: reuse the mix ONLY if it exists, is non-trivial, AND is
    # newer than every source voice file. Otherwise a stale mix (e.g. from a
    # previous run with quieter/older voice files) is silently reused and the
    # dialogue is lost/truncated.
    if out_path.exists() and out_path.stat().st_size > 1000:
        out_mtime = out_path.stat().st_mtime
        stale = any(
            vp.exists() and vp.stat().st_mtime > out_mtime
            for vp in voice_paths
        )
        if not stale:
            return out_path

    duck = {"guarded": "-6dB", "withdrawn": "-10dB", "frustrated": "-4dB",
            "emotional_peak": "-2dB", "resolved": "-12dB"}.get(emotion, "-6dB")

    inputs: list[str] = []
    filters: list[str] = []
    idx = 0

    if music_path and music_path.exists():
        inputs += ["-i", str(music_path)]
        filters.append(f"[{idx}:a]volume={duck},aresample=48000[m]")
        idx += 1

    # Place lines back-to-back: each starts after the previous ends + pause
    cursor_ms = 0
    pause_ms = 700
    for vp in voice_paths:
        if not vp or not vp.exists():
            continue
        inputs += ["-i", str(vp)]
        filters.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                       f"adelay={cursor_ms}|{cursor_ms},volume=2.2[v{idx}]")
        idx += 1
        cursor_ms += int((_probe_duration(vp) + pause_ms / 1000.0) * 1000)

    if idx == 0:
        return None

    # Build the mix graph
    # FIX (scene-1 dialogue loss): amix `duration=first` truncated the dialogue
    # mix to the length of the FIRST line, silently dropping every later line.
    # Use `duration=longest` so all back-to-back dialogue lines survive.
    # FIX (music continuation): the music amix must ALSO use `duration=longest`
    # so the music bed plays through the whole scene instead of being cut off
    # at the dialogue length (which left the scene tail silent).
    if music_path and music_path.exists():
        # music [m] + dialogue voices [v1..vN] -> amix
        mix_inputs = "".join(f"[v{i}]" for i in range(1, idx))
        filters.append(f"{mix_inputs}amix=inputs={idx-1}:duration=longest:dropout_transition=3[vout]")
        filters.append("[vout][m]amix=inputs=2:duration=longest:dropout_transition=3[out]")
    else:
        mix_inputs = "".join(f"[v{i}]" for i in range(1, idx))
        filters.append(f"{mix_inputs}amix=inputs={idx-1}:duration=longest:dropout_transition=3[out]")

    cmd = (["ffmpeg", "-y"] + inputs +
           ["-filter_complex", ";".join(filters), "-map", "[out]",
            "-c:a", "aac", "-b:a", "192k", str(out_path)])
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    if not out_path.exists() or out_path.stat().st_size < 1000:
        return None

    # Loudness normalization so dialogue is clearly audible
    norm_path = out_path.with_suffix(".norm.m4a")
    norm_cmd = (f'ffmpeg -y -i "{out_path}" -af '
                f'"loudnorm=I=-16:TP=-1.5:LRA=11" '
                f'-c:a aac -b:a 192k "{norm_path}"')
    subprocess.run(norm_cmd, shell=True, capture_output=True, text=True, timeout=120)
    if norm_path.exists() and norm_path.stat().st_size > 0:
        shutil.move(str(norm_path), str(out_path))
    return out_path if out_path.exists() else None


def render_lipsync_scene_video(image_path: Path, audio_path: Path, duration_s: float,
                               out_path: Path, motion_prompt: str = "") -> Path | None:
    """Render a readable-speaking scene with SVD motion, then mux audio."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            motion_path = ex.submit(
                lambda: asyncio.run(
                    render_with_svd(
                        image_path=image_path,
                        output_dir=out_path.parent,
                        width=576,
                        height=1024,
                        fps=24,
                    )
                )
            ).result(timeout=1800)
        if not motion_path or not Path(motion_path).exists():
            return None
        subprocess.run([
            "ffmpeg", "-y", "-i", str(motion_path), "-i", str(audio_path),
            "-c:v", "copy", "-c:a", "aac", "-shortest", str(out_path)
        ], check=True, capture_output=True, timeout=300)
        return out_path if out_path.exists() and out_path.stat().st_size > 10000 else None
    except Exception as e:
        logger.warning("  [video] lip-sync render fallback engaged: %s", e)
        return None


def render_scene_video(image_path: Path, audio_path: Path, duration_s: float,
                       out_path: Path, motion: str = "zoom_in") -> Path | None:
    """Ken Burns over a single image + audio. Returns path or None.

    `motion` selects a distinct camera move so consecutive scenes do not all
    feel like the same static close-up (P0 video-review fix: the 30-shot plan
    collapses to a few scene images, so varying the Ken Burns motion per scene
    keeps the finished video from feeling monotonous).
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
    # Ken Burns: slow zoom + pan across the whole scene via zoompan.
    # Different motion profiles per scene reduce visual monotony.
    dur = max(duration_s, 1.0)
    fps = 24
    frames = int(dur * fps)
    if motion == "zoom_in":
        z = f"1+0.08*on/{frames}"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)"
    elif motion == "zoom_out":
        z = f"1.08-0.08*on/{frames}"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)"
    elif motion == "pan_left":
        z = "1.15"
        x = f"(iw-iw/zoom)*(1-on/{frames})"
        y = "ih/2-(ih/zoom/2)"
    elif motion == "pan_right":
        z = "1.15"
        x = f"(iw-iw/zoom)*(on/{frames})"
        y = "ih/2-(ih/zoom/2)"
    elif motion == "pan_up":
        z = "1.15"
        x = "iw/2-(iw/zoom/2)"
        y = f"(ih-ih/zoom)*(1-on/{frames})"
    else:  # pan_down
        z = "1.15"
        x = "iw/2-(iw/zoom/2)"
        y = f"(ih-ih/zoom)*(on/{frames})"
    vf = (f"scale=1920:1080:force_original_aspect_ratio=decrease,"
          f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps={fps}")
    cmd = (f'ffmpeg -y -loop 1 -i "{image_path}" -i "{audio_path}" '
           f'-vf "{vf}" '
           f'-c:v libx264 -pix_fmt yuv420p -preset medium -crf 20 -r {fps} '
           f'-c:a aac -b:a 192k -ar 48000 '
           f'-map 0:v -map 1:a -t {duration_s} "{out_path}"')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if not out_path.exists() or out_path.stat().st_size < 10000:
        logger.error(f"  [video] scene render failed: {r.stderr[-800:]}")
        return None
    return out_path


class FilmStage:
    """Film stage: final export with audio mixing and rendering."""

    def __init__(
        self,
        certificate: Any | None = None,
        brief: dict[str, Any] | None = None,
    ):
        self.certificate = certificate
        self.brief = brief or {}

    def run(self) -> dict[str, Any]:
        """Execute the film (final export) stage."""
        editing_data = self.brief.get("editing_timeline", {})
        timeline_entries = editing_data.get("timeline", [])
        scene_count = int(editing_data.get("total_scenes", len(timeline_entries))) or 1

        project_name = getattr(self.certificate, "project_name", "film") if self.certificate else "film"
        clean_name = "".join(c for c in project_name if c.isalnum() or c in "_- ")[:40].strip(" -_")
        output_path = str(build_run_path(self.brief, "render", f"{clean_name}_final.mp4"))

        all_images = self.brief.get("image_artifacts", [])
        all_audio = self.brief.get("voice_artifacts", [])
        all_music = self.brief.get("music_artifacts", [])

        # ── Real audio mixing: group voice clips by scene, mix with music ──
        mixed_audio: list[dict[str, Any]] = []
        voice_by_scene: dict[int, list[Path]] = {}
        for art in all_audio:
            meta = art.get("metadata", {}) if isinstance(art, dict) else {}
            sid = meta.get("scene_id", 0)
            p = Path(art.get("path", "")) if isinstance(art, dict) else None
            if p and p.exists():
                voice_by_scene.setdefault(sid, []).append(p)

        music_by_scene: dict[int, Path] = {}
        for art in all_music:
            meta = art.get("metadata", {}) if isinstance(art, dict) else {}
            sid = meta.get("scene_id", 0)
            p = Path(art.get("path", "")) if isinstance(art, dict) else None
            if p and p.exists():
                music_by_scene[sid] = p

        image_by_scene: dict[int, Path] = {}
        for art in all_images:
            meta = art.get("metadata", {}) if isinstance(art, dict) else {}
            sid = meta.get("scene_id", 0)
            p = Path(art.get("path", "")) if isinstance(art, dict) else None
            if p and p.exists():
                image_by_scene[sid] = p

        # ── Assemble each scene: mix audio, then Ken Burns video ──
        scene_videos: list[Path] = []
        # Distinct Ken Burns motion per scene so the finished video does not
        # feel like one static close-up held for the whole runtime (P0 review).
        _motions = ["zoom_in", "pan_right", "zoom_out", "pan_left", "pan_up", "pan_down"]
        for sid, voice_paths in voice_by_scene.items():
            scene_dur = compute_scene_duration(voice_paths)
            music = music_by_scene.get(sid)
            mixed = mix_scene_audio(music, voice_paths,
                                    build_run_path(self.brief, "render", f"scene_{sid:03d}_mixed.m4a"),
                                    scene_dur)
            if mixed:
                mixed_audio.append({
                    "type": "audio",
                    "path": str(mixed),
                    "url": None,
                    "metadata": {"scene_id": sid, "duration_seconds": scene_dur},
                })
            # Render the scene video: lipsync for readable speakers, Ken Burns otherwise.
            image = image_by_scene.get(sid)
            if image and mixed:
                scene_obj = next((s for s in self.brief.get("scenes", []) or [] if (s.get("number") or s.get("scene_number") or s.get("id")) == sid), {})
                shot = scene_obj.get("shot", {}) if isinstance(scene_obj.get("shot"), dict) else {}
                out_mp4 = build_run_path(self.brief, "render", f"scene_{sid:03d}.mp4")
                motion = _motions[(sid - 1) % len(_motions)]
                if shot.get("lip_sync_required") and shot.get("speaker"):
                    # SVD lip-sync render is heavy (5-6GB model, slow inference)
                    # and can fail/timing-out locally. NEVER drop a scene because
                    # the motion backend is unavailable — fall back to the
                    # reliable Ken Burns render so a playable film still assembles.
                    sv = render_lipsync_scene_video(
                        image, mixed, scene_dur, out_mp4,
                        motion_prompt=str(shot.get("visual_intent") or shot.get("performance_intent") or "acting camera and facial performance synchronized to dialogue"),
                    )
                    if sv is None:
                        logger.warning(
                            f"  [film] SVD lip-sync unavailable for scene {sid} "
                            f"— falling back to Ken Burns so the film still assembles."
                        )
                        sv = render_scene_video(image, mixed, scene_dur, out_mp4, motion=motion)
                else:
                    sv = render_scene_video(image, mixed, scene_dur, out_mp4, motion=motion)
                if sv:
                    scene_videos.append(sv)
                    logger.info(f"  [film] scene {sid} rendered ({scene_dur:.0f}s, {motion})")

        if not voice_by_scene:
            logger.error("[film] No dialogue/voice clips — cannot assemble a film. "
                         "The GENESIS dialogue phase under-produced (likely an LLM error).")
            raise RuntimeError(
                "FilmStage: no voice clips generated — GENESIS dialogue phase "
                "under-produced. Cannot assemble a film without audio."
            )

        # ── Concatenate all scene videos into the final film ──
        final_path = Path(output_path)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        if scene_videos:
            concat = final_path.parent / "concat.txt"
            concat.write_text("\n".join(f"file '{v.resolve()}'" for v in scene_videos))
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" -c copy "{final_path}"',
                           shell=True, capture_output=True, timeout=120)
            if not final_path.exists() or final_path.stat().st_size < 10000:
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" '
                               f'-c:v libx264 -pix_fmt yuv420p -crf 20 -r 24 '
                               f'-c:a aac -b:a 192k "{final_path}"',
                               shell=True, capture_output=True, timeout=300)

        # ── Vibrant color grade (reference-matching) ──
        # The reference is BRIGHT, VIBRANT, HIGH-SATURATION (SATAVG ~28).
        # Our photorealistic source is muted (~13.6). Boost saturation hard
        # (1.9x), plus contrast/brightness, so the final film pops toward the
        # reference's energy instead of looking like muted film stock.
        if final_path.exists() and final_path.stat().st_size > 10000:
            graded = final_path.with_suffix(".graded.mp4")
            grade_vf = ("eq=contrast=1.18:brightness=0.05:saturation=1.9,"
                        "unsharp=5:5:0.8:5:5:0.0")
            subprocess.run(
                f'ffmpeg -y -i "{final_path}" -vf "{grade_vf}" '
                f'-c:v libx264 -pix_fmt yuv420p -preset medium -crf 20 '
                f'-c:a copy "{graded}"',
                shell=True, capture_output=True, timeout=300)
            if graded.exists() and graded.stat().st_size > 10000:
                shutil.move(str(graded), str(final_path))
                logger.info(f"  [film] vibrant color grade applied to {final_path}")

        film_ok = final_path.exists() and final_path.stat().st_size > 10000
        if film_ok:
            logger.info(f"  [film] FINAL FILM: {final_path} ({final_path.stat().st_size//1024}KB)")

        artifacts_list = [{
            "type": "film",
            "path": output_path,
            "url": None,
            "metadata": {
                "project_name": getattr(self.certificate, "project_name", "") if self.certificate else "",
                "certificate_id": getattr(self.certificate, "certificate_id", "") if self.certificate else "",
                "scene_count": scene_count,
                "duration_seconds": editing_data.get("duration_seconds", scene_count * 5.0),
                "total_artifacts": len(all_images) + len(all_audio) + len(all_music),
                "mixed_audio_clips": len(mixed_audio),
                "scene_videos_rendered": len(scene_videos),
                "film_ok": film_ok,
            },
        }]

        return {
            "artifacts": artifacts_list,
            "stage_name": "Film",
            "film_exported": output_path,
            "film_ok": film_ok,
            "manifest": {
                "timeline_entries": timeline_entries,
                "audio_tracks": all_audio,
                "music_tracks": all_music,
                "mixed_audio": mixed_audio,
                "scene_videos": [str(v) for v in scene_videos],
                "output": output_path,
            },
        }

    def create_initial_state(self, name: str = "Film") -> dict[str, Any]:
        return {
            "name": name,
            "class_name": "FilmStage",
            "stage": {
                "name": name,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "artifacts": [],
                "error": None,
            },
        }
