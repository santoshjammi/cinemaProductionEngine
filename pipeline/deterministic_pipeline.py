"""Deterministic pipeline — generates complete video assets WITHOUT requiring Ollama.

Uses real MARK/SARAH dialogue-driven content from scenes.yaml and prompts.yaml,
with character-consistent visual descriptions for every image prompt.

Usage:
    python -m pipeline.deterministic_pipeline [--no-images] [--no-audio] [--no-video]

This is the primary entry point when you want to generate a video without
depending on local LLM inference or ComfyUI availability.
"""

import asyncio
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pipeline.det")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUTPUT = ROOT / "output" / "the_space_between_us_det"
IMAGES = OUTPUT / "images"
AUDIO = OUTPUT / "audio"
VIDEO = OUTPUT / "video"

VOICES = {"MARK": "en-US-BrianNeural", "SARAH": "en-US-AriaNeural"}

import yaml


def load_scenes():
    """Load scenes from scenes.yaml — our source of truth for dialogue-driven content."""
    scenes_path = ROOT / "pipeline" / "scenes" / "scenes.yaml"
    if scenes_path.exists():
        with open(scenes_path) as f:
            return yaml.safe_load(f) or []
    # Fallback to deterministic fallback module
    from pipeline.deterministic_fallback import generate_scenes
    return generate_scenes()


def load_prompts():
    """Load prompts from prompts.yaml — character-consistent descriptions."""
    prompts_path = ROOT / "pipeline" / "prompts" / "prompts.yaml"
    if prompts_path.exists():
        with open(prompts_path) as f:
            return yaml.safe_load(f) or []

    # Fallback to deterministic fallback module
    from pipeline.deterministic_fallback import generate_scenes, CHARACTER_LOCK_IN
    scenes = generate_scenes()
    prompts = []
    for s in scenes:
        sid = s.get("id", 1)
        camera = s.get("camera", "wide shot")
        lighting = s.get("lighting", "natural light")
        emotion = s.get("emotion", "calm").replace(" ", "_")
        vp = s.get("visual_prompt", "")
        if "-- character references:" not in vp:
            vp += CHARACTER_LOCK_IN
        prompts.append({
            "scene_id": sid,
            "prompt": f"Cinematic {camera} of the scene described above. {lighting} with dramatic composition. {emotion} atmosphere. Professional cinematography, 8k resolution.{CHARACTER_LOCK_IN}",
            "negative_prompt": "blurry, low quality, deformed, extra fingers, cartoon",
            "visual_style": "cinematic",
        })
    return prompts


def load_dialogue_map(scenes):
    """Build dialogue_map {scene_id: [{speaker, text}]} from scene-level dialogue_lines."""
    dialogue_map = {}
    for s in scenes:
        sid = s.get("id")
        lines = s.get("dialogue_lines")
        if lines and isinstance(lines, list):
            dialogue_map[sid] = []
            for line in lines:
                speaker_raw = line.get("speaker", "MARK")
                speaker_name = speaker_raw.split("(")[0].strip()
                text = line.get("text", "") or line.get("dialogue_text", "")
                dialogue_map[sid].append({"speaker": speaker_name, "dialogue_text": text})
    return dialogue_map


def generate_placeholder_images(scenes):
    """Generate solid-color placeholder images when ComfyUI is unavailable."""
    from PIL import Image, ImageDraw, ImageFont
    print(f"\n{'='*60}")
    print(f"  DET — STEP: PLACEHOLDER IMAGES (no ComfyUI)")
    print(f"{'='*60}\n")

    placeholder_colors = [
        "#2c3e50", "#34495e", "#1a5276", "#1b4f72", "#0e3d5e",
    ]

    scene_images = {}
    for s in scenes:
        sid = s["id"]
        frames = []
        for i in range(3):
            path = IMAGES / f"scene_{sid:03d}_frame_{i+1}.png"
            if not path.exists():
                color = placeholder_colors[(sid - 1) % len(placeholder_colors)]
                img = Image.new("RGB", (1280, 720), color)
                draw = ImageDraw.Draw(img)

                # Try to use a nice font for the label
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 44)
                except:
                    font = ImageFont.load_default()

                text = f"Scene {sid}\nFrame {i+1}"
                bbox = draw.textbbox((0, 0), text, font=font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

                draw.text(((1280 - tw) // 2, (720 - th) // 2), text, fill="white", font=font)
                img.save(str(path), "PNG")

            frames.append(path)
        scene_images[sid] = frames

    return scene_images


async def generate_audio(scenes, dialogue_map):
    """Generate TTS for both MARK and SARAH's lines with CC0 music."""
    print(f"\n{'='*60}")
    print(f"  DET — STEP: AUDIO (dialogue + CC0 music)")
    print(f"{'='*60}\n")

    import edge_tts
    from movie_os.audio.music_selector import get_track_for_scene, get_track_duration
    import re

    # Emotion-aware prosody mapping
    _PROSODY_BY_EMOTION = {
        "guarded":   {"MARK": {"rate": "-8%", "pitch": "+2%"}, "SARAH": {"rate": "+3%", "volume": "-3dB"}},
        "withdrawn": {"MARK": {"rate": "-10%", "volume": "-4dB"}},
        "frustrated":{"MARK": {"pitch": "+3%"}, "SARAH": {"rate": "-5%", "volume": "-3dB"}},
        "emotional peak":  {"MARK": {"volume": "+2dB", "rate": "-8%"}, "SARAH": {"volume": "+2dB", "pitch": "+5%"}},
        "resolved":  {"MARK": {"rate": "+3%", "volume": "+1dB"}, "SARAH": {"rate": "-3%", "volume": "-4dB"}},
    }

    _DIRECTION_MAP = {
        "whisper":      {"volume": "-12dB", "rate": "-10%", "pitch": "-5%"},
        "quietly":      {"volume": "-6dB", "rate": "-5%"},
        "sigh":         {"volume": "-4dB", "rate": "-8%"},
        "tired":        {"volume": "-4dB", "rate": "-8%"},
        "distracted":   {"volume": "-3dB", "rate": "+5%"},
    }

    scene_audio = {}
    total_lines = 0

    for s in scenes:
        sid = s["id"]
        dur_str = s.get("duration", "15s")
        duration_s = int(re.sub(r'[^\d]', '', dur_str).strip())
        emotion = s.get("emotion", "calm")
        scene_class = s.get("scene_class", "dialogue")

        scene_dialogues = dialogue_map.get(sid, [])
        if not scene_dialogues:
            logger.warning(f"[Scene {sid}] No dialogue lines — skipping audio")
            continue

        # Music
        track = get_track_for_scene(sid, emotion, scene_class)
        music_path = AUDIO / f"scene_{sid:03d}.wav"
        if track and track.exists():
            tdur = get_track_duration(track) or 60
            opt = "" if tdur >= duration_s else "-stream_loop -1"
            import subprocess as sp
            sp.run(f'ffmpeg -y {opt} -i "{track}" -t {duration_s} -ac 2 "{music_path}"',
                   shell=True, capture_output=True, timeout=120)

        # TTS per line
        tts_paths = []
        for i, line in enumerate(scene_dialogues):
            speaker = line["speaker"]
            text = line["dialogue_text"]
            voice = VOICES.get(speaker, VOICES["MARK"])

            # Extract stage direction
            clean = text.strip()
            stage = ""
            m = re.match(r'^\(([^)]+)\)\s*(.*)', clean, re.DOTALL)
            if m:
                stage = m.group(1).strip().lower()
                clean = m.group(2).strip()
            elif re.search(r'\([^)]+\)$', clean):
                m = re.match(r'^(.*?)\s*\(([^)]+)\)\s*$', clean, re.DOTALL)
                if m:
                    stage = m.group(2).strip().lower()
                    clean = m.group(1).strip()
            clean = " ".join(clean.split())

            props = _DIRECTION_MAP.get(stage, {})
            if emotion in _PROSODY_BY_EMOTION:
                props.update(_PROSODY_BY_EMOTION[emotion].get(speaker, {}))
            # Build SSML
            ssml = (
                f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
                f'<voice name="{voice}"><prosody rate="{props.get("rate","0%")}" '
                f'volume="{props.get("volume","0dB")}" pitch="{props.get("pitch","0%")}">'
                f'{clean}</prosody></voice></speak>'
            )

            path = AUDIO / f"scene_{sid:03d}_line_{i+1}.mp3"
            try:
                communicate = edge_tts.Communicate(ssml)
                await communicate.save(str(path))
                tts_paths.append(path)
                total_lines += 1
                logger.info(f"  [Scene {sid}] {speaker}: {clean[:60]}...")
            except Exception as e:
                logger.error(f"  TTS failed for scene {sid} line {i+1} ({speaker}): {e}")

        # Mix with music
        from pipeline.audio_pipeline import mix_audio
        mixed_path = AUDIO / f"scene_{sid:03d}_mixed.mp3"
        if tts_paths and music_path.exists():
            mix_audio(music_path, tts_paths, mixed_path, duration_s)
            scene_audio[sid] = mixed_path
            logger.info(f"[Scene {sid}] Mixed {len(tts_paths)} dialogue lines + music")

    logger.info(f"\n[Audio] Total dialogue lines generated: {total_lines}")
    return scene_audio


async def assemble_video(scenes, scene_images, scene_audio):
    """Assemble final video with Ken Burns pan/zoom on each frame."""
    print(f"\n{'='*60}")
    print(f"  DET — STEP: ASSEMBLE (Ken Burns + synced audio)")
    print(f"{'='*60}\n")

    VIDEO.mkdir(parents=True, exist_ok=True)
    concat_lines = []

    for s in scenes:
        sid = s["id"]
        dur_str = s.get("duration", "15s")
        duration_s = int(re.sub(r'[^\d]', '', dur_str).strip())
        frames = scene_images.get(sid, [])
        mixed = scene_audio.get(sid)

        if not frames or not mixed or not mixed.exists():
            logger.warning(f"Scene {sid}: missing assets")
            continue

        num_frames = len(frames)
        fdur = duration_s / max(num_frames, 1)

        flist = VIDEO / f"scene_{sid}_frames.txt"
        flines = []
        for f_idx, frame_path in enumerate(frames):
            filter_str = (
                f'scale=1920:1080:force_original_aspect_ratio=decrease,'
                f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,'
                f"crop=min(iw,iph):min(ih,iph):(iw-ow)/2:(ih-oh)/2,"
                f'setpts={1.0 + (f_idx/max(num_frames,1))*0.05:.4f}*PTS'
            )
            flines.append(f'file \'{frame_path}\'\nduration {fdur}\nfilter_video \'{filter_str}\'')
        flist.write_text("\n".join(flines))

        sv = VIDEO / f"scene_{sid:03d}.mp4"
        cmd = (f'ffmpeg -y -f concat -safe 0 -i "{flist}" -i "{mixed}" '
               f'-c:v libx264 -pix_fmt yuv420p -preset slow -crf 18 -r 24 '
               f'-c:a aac -b:a 192k -ar 48000 -map 0:v -map 1:a -t {duration_s} "{sv}"')
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if sv.exists():
            concat_lines.append(f"file '{sv}'")
            logger.info(f"[Scene {sid}] {num_frames} frames × {fdur:.1f}s + audio ({duration_s}s)")

    # Final concat
    concat_file = OUTPUT / "concat_det.txt"
    concat_file.write_text("\n".join(concat_lines))
    final = VIDEO / "the_space_between_us_det.mp4"

    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c copy "{final}"'
    subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    if not final.exists() or final.stat().st_size < 1000:
        cmd2 = (f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" '
                f'-c:v libx264 -pix_fmt yuv420p -crf 18 -r 24 '
                f'-c:a aac -b:a 192k -ar 48000 "{final}"')
        subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=300)

    if final.exists() and final.stat().st_size > 1000:
        import subprocess
        r2 = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(final)],
                    capture_output=True, text=True, timeout=30)
        d, sz = r2.stdout.strip().split("\n")
        mins = float(d) / 60
        mb = int(sz) / (1024 * 1024)
        logger.info(f"\n{'='*60}")
        logger.info(f"  ✅ DET COMPLETE — {float(d):.0f}s ({mins:.1f} min), {mb:.1f} MB")
        logger.info(f"  {final}")
        logger.info(f"{'='*60}")
        return str(final)
    else:
        logger.error("Failed to create final video")
        return None


async def main():
    IMAGES.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    VIDEO.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  DET — DETERMINISTIC VIDEO PIPELINE")
    print(f"{'='*60}\n")

    # Load data from YAML files
    scenes = load_scenes()
    prompts = load_prompts()
    dialogue_map = load_dialogue_map(scenes)

    logger.info(f"Scenes: {len(scenes)}, Prompts: {len(prompts)}")
    total_dl = sum(len(v) for v in dialogue_map.values())
    logger.info(f"Dialogue lines: {total_dl}")

    # Check if ComfyUI is available for real images
    import socket
    comfyui_ok = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        r = s.connect_ex(("localhost", 8188))
        comfyui_ok = (r == 0)
        s.close()
    except:
        pass

    if not comfyui_ok:
        logger.info("ComfyUI not available — using placeholder images")
        images = generate_placeholder_images(scenes)
    else:
        import sys
        sys.path.insert(0, str(ROOT / "movie_os"))
        from movie_os.workflows.comfyui_client import ComfyUIClient
        from movie_os.workflows import load_workflow, fill_placeholders

        logger.info("ComfyUI found — generating real images")
        client = ComfyUIClient(base_url="http://localhost:8188", timeout=600.0)
        scene_images = {}

        for p in prompts:
            sid = p["scene_id"]
            base_prompt = p.get("prompt", "")
            negative = p.get("negative_prompt", "blurry, low quality, deformed")

            variants = [
                {"prompt": base_prompt, "seed": sid * 1000 + 1},
                {"prompt": base_prompt.replace("Wide", "Medium").replace("wide", "medium"), "seed": sid * 1000 + 2},
                {"prompt": "Close-up detail: " + base_prompt[:300], "seed": sid * 1000 + 3},
            ]

            frames = []
            for i, v in enumerate(variants):
                path = IMAGES / f"scene_{sid:03d}_frame_{i+1}.png"
                if path.exists() and path.stat().st_size > 1000:
                    frames.append(path)
                    continue

                workflow = load_workflow("flux_txt2img")
                fill_placeholders(workflow, {"prompt": v["prompt"], "negative_prompt": negative})
                for nid, node in workflow.items():
                    if node.get("class_type") == "UNETLoader":
                        node["inputs"]["unet_name"] = "flux1-schnell.safetensors"
                    elif node.get("class_type") == "KSampler":
                        node["inputs"]["seed"] = v["seed"]
                        node["inputs"]["steps"] = 4
                        node["inputs"]["cfg"] = 1.0

                try:
                    pid = client.submit(workflow)
                    hist = client.wait_for_result(pid, timeout=600)
                    outs = client.get_outputs(hist)
                    if outs:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        client.save_image(outs[0]["filename"], path, outs[0].get("subfolder", ""))
                        frames.append(path)
                except Exception as e:
                    logger.error(f"  Failed scene {sid} frame {i+1}: {e}")

            scene_images[sid] = frames

        images = scene_images

    # Audio (always generated — TTS doesn't depend on LLM)
    audio = await generate_audio(scenes, dialogue_map)

    # Video assembly
    video = await assemble_video(scenes, images, audio)

    if video:
        print(f"\n✅ Deterministic pipeline completed successfully. Video at: {video}")
    else:
        print("\n⚠️  Pipeline completed but final video could not be assembled.")


if __name__ == "__main__":
    asyncio.run(main())
