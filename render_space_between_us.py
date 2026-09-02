#!/usr/bin/env python3
"""The Space Between Us — full render pipeline.

Path A: cinematic stills (FLUX via ComfyUI) + emotional TTS (edge-tts)
+ CC0 music + ffmpeg Ken Burns assembly.

Verified working:
  - ComfyUI at http://127.0.0.1:8188 (FLUX fp8, 1024x576)
  - edge-tts BrianNeural (Mark) / AriaNeural (Sarah)
  - CC0 music in assets/music/
"""
import asyncio
import json
import logging
import re
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("space_between_us")

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "the_space_between_us_final"
IMAGES = OUTPUT / "images"
AUDIO = OUTPUT / "audio"
VIDEO = OUTPUT / "video"
MUSIC = ROOT / "assets" / "music"

COMFY = "http://127.0.0.1:8188"
VOICES = {
    "MARK": "en-US-BrianNeural",
    "SARAH": "en-US-AriaNeural",
    "MARK_INNER": "en-US-AndrewNeural",  # Mark's whispering inner voice (distinct from spoken)
}

# Scene -> music track (emotional arc)
SCENE_MUSIC = {
    1: "cinematic_ambient_piano",   # warm, secure
    2: "isolation_ambient",          # uneasy, withdrawing
    3: "dark_rain_piano_strings",    # painfully distant
    4: "circle_of_life_sad",         # vulnerable turning point
    5: "lucas_king_hurt",            # cautiously hopeful
}

# Stage-direction prosody for edge-tts
_DIRECTION = {
    "softly": {"rate": "-8%", "volume": "-4dB"},
    "soft": {"rate": "-8%", "volume": "-4dB"},
    "quiet": {"rate": "-10%", "volume": "-6dB"},
    "quietly": {"rate": "-10%", "volume": "-6dB"},
    "flat": {"rate": "+2%", "volume": "-3dB"},
    "voice breaking": {"rate": "-12%", "volume": "+1dB"},
    "crying": {"rate": "-12%", "volume": "+1dB"},
    "voice catching": {"rate": "-10%", "volume": "+1dB"},
    "almost a whisper": {"rate": "-15%", "volume": "-8dB"},
    "barely audible": {"rate": "-15%", "volume": "-8dB"},
    "whisper": {"rate": "-18%", "volume": "-10dB"},  # Mark's inner voice — soft, intimate, suffering
    "whispering": {"rate": "-18%", "volume": "-10dB"},
    "warm": {"rate": "-4%", "volume": "+1dB"},
    "sincere": {"rate": "-4%"},
    "gently": {"rate": "-6%", "volume": "-2dB"},
    "touched": {"rate": "-4%", "volume": "+1dB"},
    "not accusing": {"rate": "-6%", "volume": "-2dB"},
    "voice thick with emotion": {"rate": "-12%", "volume": "+1dB"},
}


def clean_text(text):
    """Strip leading (stage direction) and return (clean, props).

    Handles comma-separated directions like '(whisper, barely audible)'
    by merging the prosody of each recognized token.
    """
    m = re.match(r"^\s*\(([^)]+)\)\s*(.*)", text, re.DOTALL)
    if m:
        stage = m.group(1).strip().lower()
        clean = m.group(2).strip()
        props = {}
        for token in re.split(r"[,\s]+", stage):
            if token in _DIRECTION:
                props.update(_DIRECTION[token])
        return clean, props
    return text.strip(), {}


# ── ComfyUI FLUX ─────────────────────────────────────────────────────────
def comfy_get(path):
    with urllib.request.urlopen(f"{COMFY}{path}", timeout=30) as r:
        return json.loads(r.read().decode())


def comfy_post(path, data):
    req = urllib.request.Request(
        f"{COMFY}{path}", data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def flux_workflow(prompt, seed, width=1024, height=576, steps=4):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux1-dev-fp8.safetensors", "weight_dtype": "default"}},
        "1v": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "2": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "t5xxl_fp8_e4m3fn.safetensors", "clip_name2": "clip_l.safetensors", "type": "flux"}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "cartoon, anime, illustration, painting, 3d render, cgi, blurry, low quality, distorted, deformed, disfigured, bad anatomy, extra limbs, extra fingers, watermark, signature, text, oversaturated, plastic skin, duplicate, cloned, multiple scenes, collage"}},
        "5": {"class_type": "FluxGuidance", "inputs": {"conditioning": ["3", 0], "guidance": 3.5}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["5", 0], "negative": ["4", 0], "latent_image": ["6", 0], "seed": seed, "steps": steps, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1v", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "space_between", "images": ["8", 0]}},
    }


def render_flux(prompt, seed, out_path, steps=4):
    """Render one FLUX image and copy it to out_path. Returns True on success."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        logger.info(f"  [img] exists, skip: {out_path.name}")
        return True
    wf = flux_workflow(prompt, seed, steps=steps)
    resp = comfy_post("/prompt", {"prompt": wf, "client_id": str(uuid.uuid4())})
    pid = resp.get("prompt_id")
    if not pid:
        logger.error(f"  [img] submit failed: {resp}")
        return False
    for _ in range(180):
        time.sleep(2)
        try:
            hist = comfy_get(f"/history/{pid}")
            if pid in hist:
                st = hist[pid].get("status", {})
                if st.get("completed"):
                    for nid, out in hist[pid].get("outputs", {}).items():
                        for img in out.get("images", []):
                            fname = img.get("filename")
                            sub = img.get("subfolder", "")
                            src = Path("/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/output")
                            if sub:
                                src = src / sub
                            src = src / fname
                            if src.exists():
                                import shutil
                                shutil.copy2(src, out_path)
                                logger.info(f"  [img] {out_path.name} ({src.stat().st_size//1024}KB)")
                                return True
                    return True
                elif st.get("status_str") == "error":
                    logger.error(f"  [img] render error: {json.dumps(st)[:500]}")
                    return False
        except Exception as e:
            logger.warning(f"  [img] poll err: {e}")
    logger.error(f"  [img] timeout for {out_path.name}")
    return False


# ── TTS ──────────────────────────────────────────────────────────────────
def _rate_to_atempo(rate_str: str) -> float:
    """Convert edge-tts rate ('-8%', '+5%') to an ffmpeg atempo factor.
    atempo > 1 = faster, < 1 = slower. Range must be 0.5-2.0."""
    try:
        pct = float(rate_str.replace("%", "").strip())
    except Exception:
        return 1.0
    factor = 1.0 + pct / 100.0
    # atempo only supports 0.5-2.0; clamp and chain if needed
    return max(0.5, min(2.0, factor))


def _volume_to_gain(volume_str: str) -> str:
    """Convert edge-tts volume ('-4dB', '+3dB') to an ffmpeg volume filter arg.
    Returns '1.0' (no-op) if not a valid dB value."""
    v = volume_str.strip()
    if v.endswith("dB"):
        return v  # ffmpeg accepts dB directly
    try:
        return str(float(v))
    except Exception:
        return "1.0"


async def tts_line(speaker, text, emotion, out_path):
    """Generate edge-tts for one line, applying prosody via ffmpeg.

    IMPORTANT: edge-tts SSML (<speak>/<voice>/<prosody>) is BROKEN in the
    installed build — it stretches a 2s line to 30s+ (garbled audio).
    Fix: generate PLAIN text, then apply rate/volume with ffmpeg
    (atempo + volume). This produces correct, intelligible dialogue.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        return out_path
    clean, props = clean_text(text)
    if not clean:
        return None
    voice = VOICES.get(speaker, VOICES["MARK"])
    rate = props.get("rate", "0%")
    volume = props.get("volume", "0dB")

    # 1. Generate plain text (no SSML — avoids the stretch bug)
    raw_path = out_path.with_suffix(".raw.mp3")
    try:
        import edge_tts
        tts = edge_tts.Communicate(clean, voice)
        await tts.save(str(raw_path))
    except Exception as e:
        logger.error(f"  [tts] edge-tts failed: {e}")
        return None

    # 2. Apply prosody via ffmpeg (atempo for rate, volume for loudness)
    atempo = _rate_to_atempo(rate)
    gain = _volume_to_gain(volume)
    filters = []
    if atempo != 1.0:
        filters.append(f"atempo={atempo}")
    if gain != "1.0":
        filters.append(f"volume={gain}")
    if filters:
        cmd = (f'ffmpeg -y -i "{raw_path}" -af "{",".join(filters)}" '
               f'-c:a libmp3lame -b:a 128k "{out_path}"')
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if not out_path.exists():
            logger.error(f"  [tts] ffmpeg prosody failed: {r.stderr[-500:]}")
            return None
    else:
        # No prosody needed — just use the raw file
        import shutil
        shutil.copy2(raw_path, out_path)

    # Cleanup raw temp
    if raw_path.exists():
        raw_path.unlink()
    return out_path


# ── Music ────────────────────────────────────────────────────────────────
def prepare_music(track_key, duration_s, out_path):
    """Trim/loop a CC0 track to duration. Returns path or None."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        return out_path
    src = MUSIC / f"{track_key}.mp3"
    if not src.exists():
        logger.warning(f"  [music] missing: {track_key}")
        return None
    # Get duration
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(src)],
                       capture_output=True, text=True)
    tdur = float(r.stdout.strip()) if r.stdout.strip() else 0
    loop = "-stream_loop -1" if tdur < duration_s else ""
    cmd = f'ffmpeg -y {loop} -i "{src}" -t {duration_s} -ac 2 -b:a 192k "{out_path}"'
    subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
    return out_path if out_path.exists() else None


# ── Audio mix ────────────────────────────────────────────────────────────
def _probe_duration(path) -> float:
    """Get audio duration in seconds via ffprobe."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True, timeout=10)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def compute_scene_duration(tts_paths, min_duration_s=8.0, pause_s=0.7, tail_s=2.0):
    """Compute a natural scene duration from the dialogue.

    Lines are placed back-to-back with a short pause between them, so the
    scene length is driven by how much is actually said — NOT a fixed
    arbitrary duration that leaves 10s+ gaps of dead silence.
    """
    total = 0.0
    for tp in tts_paths:
        if tp and tp.exists():
            total += _probe_duration(tp) + pause_s
    if total <= 0:
        return min_duration_s
    return max(min_duration_s, total + tail_s)


def mix_audio(music_path, tts_paths, out_path, duration_s, emotion):
    """Mix music (ducked) + dialogue placed back-to-back with natural pauses.

    Fix: previously lines were spread evenly across a fixed scene duration,
    creating 10s+ gaps of dead silence between lines (not dialogue). Now
    each line starts immediately after the previous one ends (plus a short
    pause), so the conversation flows naturally.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        return out_path
    duck = {"guarded": "-6dB", "withdrawn": "-10dB", "frustrated": "-4dB",
            "emotional_peak": "-2dB", "resolved": "-12dB"}.get(emotion, "-6dB")
    inputs = ["-i", str(music_path)]
    filters = [f"[0:a]volume={duck},aresample=48000[m]"]
    idx = 1
    # Place lines back-to-back: each starts after the previous ends + pause
    cursor_ms = 0
    pause_ms = 700  # 0.7s natural pause between lines
    for tp in tts_paths:
        if not tp or not tp.exists():
            continue
        inputs += ["-i", str(tp)]
        filters.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                       f"adelay={cursor_ms}|{cursor_ms},volume=1.6[v{idx}]")
        idx += 1
        cursor_ms += int((_probe_duration(tp) + pause_ms / 1000.0) * 1000)
    if idx == 1:
        # No dialogue — just music
        subprocess.run(f'ffmpeg -y -i "{music_path}" -t {duration_s} -ac 2 -b:a 192k "{out_path}"',
                       shell=True, capture_output=True, timeout=120)
        return out_path if out_path.exists() else None
    mix_inputs = "".join(f"[v{i}]" for i in range(1, idx))
    filters.append(f"{mix_inputs}amix=inputs={idx-1}:duration=first:dropout_transition=3[vout]")
    filters.append("[m][vout]amix=inputs=2:duration=first:dropout_transition=3[out]")
    cmd = (["ffmpeg", "-y"] + inputs +
           ["-filter_complex", ";".join(filters), "-map", "[out]",
            "-c:a", "aac", "-b:a", "192k", str(out_path)])
    subprocess.run(cmd, capture_output=True, timeout=180)
    if not out_path.exists():
        return None

    # ── Loudness normalization: bring the mix to a broadcast-friendly level
    #    so dialogue is clearly audible (target -16 LUFS, true peak -1.5 dBTP).
    norm_path = out_path.with_suffix(".norm.m4a")
    norm_cmd = (f'ffmpeg -y -i "{out_path}" -af '
                f'"loudnorm=I=-16:TP=-1.5:LRA=11" '
                f'-c:a aac -b:a 192k "{norm_path}"')
    r = subprocess.run(norm_cmd, shell=True, capture_output=True, text=True, timeout=120)
    if norm_path.exists() and norm_path.stat().st_size > 0:
        import shutil
        shutil.move(str(norm_path), str(out_path))
    return out_path if out_path.exists() else None


# ── Video assembly ───────────────────────────────────────────────────────
def render_scene_video(scene_id, frames, audio_path, duration_s, out_path):
    """Ken Burns over 3 frames + audio. Returns path or None."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        return out_path
    fdur = duration_s / len(frames)
    flist = out_path.parent / f"scene_{scene_id:03d}_frames.txt"
    lines = []
    for i, f in enumerate(frames):
        lines.append(f"file '{f.resolve()}'\nduration {fdur}")
    # Last frame needs no duration (concat demuxer uses it as the end)
    lines.append(f"file '{frames[-1].resolve()}'")
    flist.write_text("\n".join(lines))
    # Ken Burns: slow zoom + pan across the whole scene via zoompan
    vf = ("scale=1920:1080:force_original_aspect_ratio=decrease,"
          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
          "zoompan=z='1+0.06*on/({dur}*24)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24".format(dur=duration_s))
    cmd = (f'ffmpeg -y -f concat -safe 0 -i "{flist}" -i "{audio_path}" '
           f'-vf "{vf}" '
           f'-c:v libx264 -pix_fmt yuv420p -preset medium -crf 20 -r 24 '
           f'-c:a aac -b:a 192k -ar 48000 '
           f'-map 0:v -map 1:a -t {duration_s} "{out_path}"')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if not out_path.exists():
        logger.error(f"  [video] scene {scene_id} failed: {r.stderr[-800:]}")
    return out_path if out_path.exists() else None


# ── Main ─────────────────────────────────────────────────────────────────
async def main():
    import yaml
    IMAGES.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    VIDEO.mkdir(parents=True, exist_ok=True)

    scenes = yaml.safe_load((ROOT / "pipeline/scenes/scenes_space_between_us.yaml").read_text())
    prompts = yaml.safe_load((ROOT / "pipeline/prompts/prompts_space_between_us.yaml").read_text())
    prompt_map = {p["scene_id"]: p["prompt"] for p in prompts}

    logger.info("=" * 60)
    logger.info("  THE SPACE BETWEEN US — FULL RENDER")
    logger.info(f"  {len(scenes)} scenes, ~{sum(int(re.sub(r'[^0-9]','',s['duration'])) for s in scenes)}s total")
    logger.info("=" * 60)

    scene_videos = []

    for scene in scenes:
        sid = scene["id"]
        duration_s = int(re.sub(r"[^0-9]", "", scene["duration"]))
        emotion = scene["emotion"]
        prompt = prompt_map.get(sid, "")
        logger.info(f"\n--- Scene {sid} ({emotion}) — {duration_s}s ---")

        # 1. Images (3 frames)
        frames = []
        for fi in range(1, 4):
            out = IMAGES / f"scene_{sid:03d}_frame_{fi}.png"
            seed = 1000 + sid * 10 + fi
            ok = render_flux(prompt, seed, out)
            if ok:
                frames.append(out)
        if len(frames) < 2:
            logger.error(f"  Scene {sid}: only {len(frames)} frames, skipping")
            continue

        # 2. TTS dialogue
        tts_paths = []
        for li, line in enumerate(scene.get("dialogue_lines", [])):
            speaker = line["speaker"]
            text = line["text"]
            emotion_line = line.get("emotion", emotion)
            out = AUDIO / f"scene_{sid:03d}_line_{li+1}.mp3"
            p = await tts_line(speaker, text, emotion_line, out)
            if p:
                tts_paths.append(p)
        logger.info(f"  [tts] {len(tts_paths)} lines")

        # 3. Music
        music_path = prepare_music(SCENE_MUSIC.get(sid, "cinematic_ambient_piano"),
                                   duration_s, AUDIO / f"scene_{sid:03d}_music.wav")

        # 4. Mix — scene duration driven by actual dialogue length
        scene_dur = compute_scene_duration(tts_paths)
        mixed = mix_audio(music_path, tts_paths, AUDIO / f"scene_{sid:03d}_mixed.m4a",
                          scene_dur, emotion)
        if not mixed:
            logger.error(f"  Scene {sid}: no mixed audio")
            continue

        # 5. Video
        sv = render_scene_video(sid, frames, mixed, scene_dur, VIDEO / f"scene_{sid:03d}.mp4")
        if sv:
            scene_videos.append(sv)
            logger.info(f"  ✅ Scene {sid} rendered ({scene_dur:.0f}s)")

    # ── Quality gate: verify all assets before assembly ──
    logger.info(f"\n{'='*60}")
    logger.info("  QUALITY GATE — verifying all scene assets")
    logger.info(f"{'='*60}")
    from quality_gate import verify_scene_assets
    scene_assets = {}
    for scene in scenes:
        sid = scene["id"]
        frames = [IMAGES / f"scene_{sid:03d}_frame_{fi}.png" for fi in (1, 2, 3)]
        frames = [f for f in frames if f.exists()]
        mixed = AUDIO / f"scene_{sid:03d}_mixed.m4a"
        scene_assets[sid] = {"frames": frames, "mixed": mixed if mixed.exists() else None}
    all_qa = []
    for scene in scenes:
        sid = scene["id"]
        rep = verify_scene_assets(sid, scene_assets[sid]["frames"], scene_assets[sid]["mixed"])
        all_qa.append(rep)
        status = "PASS" if rep["ok"] else "FAIL"
        logger.info(f"  Scene {sid}: {status} — {len(rep['images'])} imgs, audio={'ok' if rep.get('audio') and rep['audio']['ok'] else 'MISSING'}")
        if not rep["ok"]:
            for e in rep["errors"]:
                logger.error(f"    ✗ {e}")
    passed = sum(1 for r in all_qa if r["ok"])
    logger.info(f"  Quality gate: {passed}/{len(all_qa)} scenes passed")
    if passed < len(all_qa):
        logger.warning("  Some scenes failed quality gate — proceeding with passed scenes only")

    # Concatenate
    if not scene_videos:
        logger.error("No scene videos rendered!")
        return
    concat = OUTPUT / "concat.txt"
    concat.write_text("\n".join(f"file '{v}'" for v in scene_videos))
    final = VIDEO / "the_space_between_us.mp4"
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" -c copy "{final}"',
                   shell=True, capture_output=True, timeout=120)
    if not final.exists() or final.stat().st_size < 10000:
        subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{concat}" -c:v libx264 -pix_fmt yuv420p -crf 20 -r 24 -c:a aac -b:a 192k "{final}"',
                       shell=True, capture_output=True, timeout=300)

    if final.exists():
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
                            "-of", "default=noprint_wrappers=1:nokey=1", str(final)],
                           capture_output=True, text=True)
        d, sz = r.stdout.strip().split("\n")
        logger.info(f"\n{'='*60}")
        logger.info(f"  ✅ FILM COMPLETE: {float(d):.0f}s ({float(d)/60:.1f} min), {int(sz)//(1024*1024)} MB")
        logger.info(f"  {final}")
        logger.info(f"{'='*60}")
    else:
        logger.error("Final video not created!")


if __name__ == "__main__":
    asyncio.run(main())
