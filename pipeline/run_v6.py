"""
V6 Pipeline — runs the full videoGen pipeline with CC0 Zimmer-style music,
emotional dialogue arcs, multi-frame images, and staggered audio.

Usage:
    python -m pipeline.run_v6
"""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path

# Shared LLM config loader (single source of truth for model selection).
sys.path.insert(0, "/Users/santosh/.hermes/scripts")
from llm_config import get_model

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pipeline.v6")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_ROOT / "output" / "the_space_between_us_v6"
IMAGES = OUTPUT / "images"
AUDIO_DIR = OUTPUT / "audio"
VIDEO_DIR = OUTPUT / "video"


# ---- Step 1: Story + Scene + Dialogue + Prompts ----
def run_llm_pipeline():
    print(f"\n{'='*60}")
    print(f"  V6 — STEP 1: LLM PIPELINE")
    print(f"{'='*60}\n")

    from pipeline.orchestrator import Pipeline

    raw_input = {
        "topic": "A man slowly withdraws from his marriage after repeated small rejections, culminating in a quiet decision to leave",
        "emotional_tone": "sad",
        "story_length": "long",
        "platform": "youtube",
        "character_constraints": "MARK (husband, 30s, quiet, introspective, emotionally exhausted), SARAH (wife, 30s, distracted, work-focused, unaware of the growing distance)",
        "setting": "Urban home — kitchen, bathroom, dining room, bedroom, balcony.",
        "pacing_style": "slow",
        "target_audience": "adults",
    }

    config = {
        "llm": {"endpoint": "http://localhost:11434"},
        "models": {
            "orchestrator": {"model": get_model()},
            "creative_writer": {"model": get_model()},
        },
        "stage_settings": {
            "story_generation": {"temperature": 0.85, "max_tokens": 4000},
            "scene_decomposition": {"temperature": 0.7, "max_tokens": 3000},
            "dialogue_generation": {"temperature": 0.9, "max_tokens": 2500},
            "cinematic_prompt_generation": {"temperature": 0.8, "max_tokens": 2000},
        },
        "research": {"enabled": False},
    }

    pipeline = Pipeline(config=config)
    result = pipeline.run(raw_input)

    # Save
    out_dir = OUTPUT / "pipeline_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    json.dump(result.story_yaml_content, open(out_dir / "story.json","w"), indent=2, default=str)
    json.dump(result.scenes_yaml_content, open(out_dir / "scenes.json","w"), indent=2, default=str)
    json.dump(result.dialogues_yaml_content, open(out_dir / "dialogues.json","w"), indent=2, default=str)
    json.dump(result.prompts_yaml_content, open(out_dir / "prompts.json","w"), indent=2, default=str)

    print(f"  Story: {result.story_yaml_content.get('title', '?')}")
    print(f"  Scenes: {len(result.scenes_yaml_content)}")
    print(f"  Dialogues: {len(result.dialogues_yaml_content)}")

    return result


# ---- Step 2: Images ----
def generate_images(prompts, scenes):
    print(f"\n{'='*60}")
    print(f"  V6 — STEP 2: IMAGES (3 per scene)")
    print(f"{'='*60}\n")

    sys.path.insert(0, str(PROJECT_ROOT / "movie_os"))
    from movie_os.workflows.comfyui_client import ComfyUIClient
    from movie_os.workflows import load_workflow, fill_placeholders

    client = ComfyUIClient(base_url="http://localhost:8188", timeout=600.0)
    scene_images = {}

    for p in prompts:
        sid = p["scene_id"]
        base_prompt = p["prompt"]
        negative = p.get("negative_prompt", "")

        variants = [
            {"prompt": base_prompt, "seed": sid * 1000 + 1},
            {"prompt": base_prompt.replace("Wide", "Medium").replace("wide", "medium"), "seed": sid * 1000 + 2},
            {"prompt": f"Close-up detail: " + base_prompt[:200], "seed": sid * 1000 + 3},
        ]

        frames = []
        for i, v in enumerate(variants):
            path = IMAGES / f"scene_{sid:03d}_frame_{i+1}.png"
            if path.exists():
                frames.append(path); continue

            workflow = load_workflow("flux_txt2img")
            fill_placeholders(workflow, {"prompt": v["prompt"], "negative_prompt": negative or "blurry, low quality, deformed"})
            for nid, node in workflow.items():
                if node.get("class_type") == "UNETLoader":
                    node["inputs"]["unet_name"] = "flux1-schnell.safetensors"
                elif node.get("class_type") == "KSampler":
                    node["inputs"]["seed"] = v["seed"]; node["inputs"]["steps"] = 4; node["inputs"]["cfg"] = 1.0

            logger.info(f"[Scene {sid}] Frame {i+1}/3...")
            try:
                pid = client.submit(workflow)
                hist = client.wait_for_result(pid, timeout=600)
                outs = client.get_outputs(hist)
                if outs:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    client.save_image(outs[0]["filename"], path, outs[0].get("subfolder",""))
                    frames.append(path)
            except Exception as e:
                logger.error(f"  Failed: {e}")

        scene_images[sid] = frames
        logger.info(f"[Scene {sid}] {len(frames)}/3 frames")

    return scene_images


# ---- Step 3: Audio ----
async def generate_audio(scenes, dialogues):
    print(f"\n{'='*60}")
    print(f"  V6 — STEP 3: AUDIO (CC0 music + TTS)")
    print(f"{'='*60}\n")

    from movie_os.audio.music_selector import get_track_for_scene, get_track_duration
    voice_map = {"MARK": "en-US-GuyNeural", "SARAH": "en-US-JennyNeural"}
    dialogue_map = {}
    for d in dialogues:
        dialogue_map.setdefault(d.get("scene_id", 1), []).append(d)

    scene_audio = {}
    for s in scenes:
        sid = s["id"]
        dur_str = s.get("duration", "60s")
        duration_s = int(dur_str.replace("s", ""))
        scene_class = s.get("scene_class", "dialogue")

        # Pick CC0 track
        track = get_track_for_scene(sid, s.get("emotion","melancholic"), scene_class)
        music_path = AUDIO_DIR / f"scene_{sid:03d}.wav"
        if track and track.exists():
            tdur = get_track_duration(track) or 60
            opt = "-t" if tdur >= duration_s else "-stream_loop -1 -t"
            subprocess.run(f'ffmpeg -y {opt} -i "{track}" {duration_s} -ac 2 "{music_path}"', shell=True, capture_output=True, timeout=120)
        logger.info(f"[Scene {sid}] Music: {track.name if track else 'fallback'} ({duration_s}s)")

        # TTS
        tts_paths = []
        lines = dialogue_map.get(sid, [])
        for i, line in enumerate(lines):
            speaker = line.get("speaker", "MARK")
            text = line.get("dialogue_text", "")
            voice = voice_map.get(speaker, "en-US-GuyNeural")
            path = AUDIO_DIR / f"scene_{sid:03d}_line_{i+1}.mp3"
            proc = await asyncio.create_subprocess_shell(f'edge-tts --voice "{voice}" --rate "+0%" --text "{text}" --write-media "{path}"')
            try:
                await asyncio.wait_for(proc.communicate(), timeout=120)
            except asyncio.TimeoutError:
                proc.kill()
                logger.warning(f"TTS timed out for scene {sid} line {i+1}")
            tts_paths.append(path)

        # Mix (staggered)
        from pipeline.audio_pipeline import mix_audio
        mixed_path = AUDIO_DIR / f"scene_{sid:03d}_mixed.mp3"
        mix_audio(music_path, tts_paths, mixed_path, duration_s)
        scene_audio[sid] = mixed_path
        logger.info(f"[Scene {sid}] {len(tts_paths)} dialogue lines + music mixed")

    return scene_audio


# ---- Step 4: Assemble ----
async def assemble_video(scenes, scene_images, scene_audio):
    print(f"\n{'='*60}")
    print(f"  V6 — STEP 4: ASSEMBLE")
    print(f"{'='*60}\n")

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    concat_lines = []
    total_dur = 0

    for s in scenes:
        sid = s["id"]
        dur = int(s.get("duration", "60s").replace("s",""))
        total_dur += dur
        frames = scene_images.get(sid, [])
        mixed = scene_audio.get(sid)
        if not frames or not mixed or not mixed.exists():
            logger.warning(f"Scene {sid}: missing assets"); continue

        fdur = dur / max(len(frames), 1)
        flist = VIDEO_DIR / f"scene_{sid}_frames.txt"
        flines = [f"file '{f}'\nduration {fdur}" for f in frames]
        flines[-1] = f"file '{frames[-1]}'"
        flist.write_text("\n".join(flines))

        sv = VIDEO_DIR / f"scene_{sid:03d}.mp4"
        cmd = (f'ffmpeg -y -f concat -safe 0 -i "{flist}" -i "{mixed}" '
               f'-c:v libx264 -pix_fmt yuv420p '
               f'-vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1" '
               f'-c:a aac -b:a 192k -map 0:v -map 1:a -t {dur} "{sv}"')
        subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
        if sv.exists():
            concat_lines.append(f"file '{sv}'")
        logger.info(f"[Scene {sid}] {len(frames)} frames × {fdur:.0f}s + audio ({dur}s)")

    # Final concat
    concat_file = OUTPUT / "concat_v6.txt"
    concat_file.write_text("\n".join(concat_lines))
    final = VIDEO_DIR / "the_space_between_us_v6.mp4"

    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c copy "{final}"'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    if not final.exists():
        cmd2 = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c:v libx264 -c:a aac "{final}"'
        subprocess.run(cmd2, shell=True, timeout=120)

    if final.exists():
        r2 = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration,size",
                             "-of","default=noprint_wrappers=1:nokey=1",str(final)],
                            capture_output=True,text=True,timeout=30)
        d, sz = r2.stdout.strip().split("\n")
        mins = float(d)/60; mb = int(sz)/(1024*1024)
        logger.info(f"\n{'='*60}")
        logger.info(f"  ✅ V6 COMPLETE — {float(d):.0f}s ({mins:.1f} min), {mb:.1f} MB")
        logger.info(f"  {final}")
        logger.info(f"{'='*60}")
        return str(final)
    else:
        logger.error("Failed to create final video")
        return None


async def main():
    IMAGES.mkdir(parents=True, exist_ok=True); AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    result = run_llm_pipeline()
    images = generate_images(result.prompts_yaml_content, result.scenes_yaml_content)
    audio = await generate_audio(result.scenes_yaml_content, result.dialogues_yaml_content)
    video = await assemble_video(result.scenes_yaml_content, images, audio)

    if video:
        # Notify Discord
        import subprocess
        notify_cmd = f'echo "✅ V6 film is ready: {video}"'
        proc = await asyncio.create_subprocess_shell(notify_cmd)
        try:
            await asyncio.wait_for(proc.communicate(), timeout=30)
        except asyncio.TimeoutError:
            proc.kill()


if __name__ == "__main__":
    asyncio.run(main())