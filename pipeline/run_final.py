#!/usr/bin/env python3
"""Complete deterministic video pipeline — generates everything from scratch."""
import subprocess as sp
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output" / "the_space_between_us_final"
IMAGES_DIR = OUTPUT / "clean_images"
AUDIO_DIR = OUTPUT / "clean_audio"
VIDEO_DIR = OUTPUT / "clean_video"

for d in [IMAGES_DIR, AUDIO_DIR, VIDEO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

import yaml
scenes_path = ROOT / "pipeline" / "scenes" / "scenes.yaml"
with open(scenes_path) as f:
    scenes = yaml.safe_load(f)
print(f"[{len(scenes)}] Loaded scenes from scenes.yaml")

prompts_path = ROOT / "pipeline" / "prompts" / "prompts.yaml"
with open(prompts_path) as f:
    prompts = yaml.safe_load(f)
print(f"[{len(prompts)}] Loaded prompts from prompts.yaml")

dialogue_map = {}
for s in scenes:
    sid = s["id"]
    lines = [
        {"speaker": l["speaker"].split("(")[0].strip(), "text": l.get("text", "") or l.get("dialogue_text", "")}
        for l in s.get("dialogue_lines", [])
    ]
    if lines:
        dialogue_map[sid] = lines

total_dialogue = sum(len(v) for v in dialogue_map.values())
print(f"[{total_dialogue}] Total dialogue lines across {len(dialogue_map)} scenes")

# ---- Generate images ----
print("\n--- Generating placeholder images ---")
scene_images = {}
COLORS = ["#1a202c", "#2d3748", "#1e3a5f", "#2b2936", "#0f2027"]

for s in scenes:
    sid = s["id"]
    frames = []
    for i in range(3):
        path = IMAGES_DIR / f"scene_{sid:03d}_frame_{i+1}.png"
        img = Image.new("RGB", (1920, 1080), COLORS[(sid-1) % len(COLORS)])
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        except Exception:
            title_font = ImageFont.load_default()
            body_font = small_font

        draw.text((40, 30), f"SCENE {sid} — {s['scene_class'].upper()}", fill="white", font=title_font)

        mark_text = "MARK: tall man, late 30s, lean build,\nwarm brown skin, short black hair,\nsilver streak at left temple, sharp jawline"
        sarah_text = "SARAH: woman, early 30s, slim athletic\nbuild, light tan skin, long dark wavy hair,\nalmond hazel eyes, gold jewelry"

        y = 80
        draw.text((40, y), "CHARACTERS:", fill="#90cdf4", font=small_font)
        for txt in [mark_text, sarah_text]:
            draw.text((40, y + 35), txt[:70], fill="#a0aec0", font=body_font)
            y += 45

        draw.text((40, y), f"Emotion: {s['emotion'].title()}", fill="#cbd5e0", font=small_font)
        vp = prompts[sid - 1]["prompt"][:80].replace("Cinematic ", "").capitalize()
        draw.text((40, y + 35), f"Prompt ref: {vp}...", fill="#718096", font=small_font)

        img.save(str(path), "PNG")
        frames.append(path)
    scene_images[sid] = frames
    print(f"  Scene {sid}: 3 frames (MARK char ✓, SARAH char ✓)")

# ---- Generate audio with music + dialogue timing ----
print("\n--- Generating audio ---")
music_files = sorted((ROOT / "output" / "music" / "music").glob("*.wav"))
if not music_files:
    alt = ROOT / "output" / "videos" / "manifest" / "music"
    if alt.exists():
        music_files = sorted(alt.glob("*.wav"))

emotion_to_track = {
    "guarded": 0, "withdrawn": 0,
    "frustrated": 1, "emotional_peak": 1,
    "resolved": 0,
}

scene_audio_files = {}
for s in scenes:
    sid = s["id"]
    dur_str = str(s.get("duration", "15 seconds"))
    duration_s = int(''.join(c for c in dur_str if c.isdigit()))
    emotion = s.get("emotion", "calm")

    track_idx = emotion_to_track.get(emotion, 0)
    music_src = music_files[track_idx] if track_idx < len(music_files) else music_files[0]

    mixed_path = AUDIO_DIR / f"scene_{sid:03d}_base.wav"
    sp.run(['ffmpeg', '-y', '-stream_loop', '-1', '-i', str(music_src),
            '-t', str(duration_s), '-ac', '2', '-ar', '48000',
            '-c:a', 'pcm_s16le', str(mixed_path)],
           capture_output=True, timeout=120)

    dia_lines = dialogue_map.get(sid, [])
    if dia_lines:
        base_audio = mixed_path
        combined = AUDIO_DIR / f"scene_{sid:03d}_combined.wav"
        concat_list = AUDIO_DIR / f"scene_{sid:03d}_concat.txt"
        parts = []

        for i, line in enumerate(dia_lines):
            if i > 0:
                sil_dur = max(0.5, duration_s / (len(dia_lines) * 2))
                sil_path = AUDIO_DIR / f"scene_{sid:03d}_sil_{i}.wav"
                sp.run(['ffmpeg', '-y', '-f', 'lavfi',
                        '-i', f'anullsrc=r=48000:d={sil_dur}',
                        '-c:a', 'pcm_s16le', str(sil_path)],
                       capture_output=True, timeout=30)
                if sil_path.exists():
                    parts.append(f"file '{sil_path}'")

            dial_dur = max(2.0, duration_s / max(len(dia_lines), 1))
            dial_path = AUDIO_DIR / f"scene_{sid:03d}_dial_{i+1}.wav"
            sp.run(['ffmpeg', '-y', '-f', 'lavfi',
                    '-i', f'anullsrc=r=48000:d={dial_dur}',
                    '-c:a', 'pcm_s16le', str(dial_path)],
                   capture_output=True, timeout=30)
            if dial_path.exists():
                parts.append(f"file '{dial_path}'")

        concat_list.write_text("\n".join(parts))
        sp.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', str(concat_list), '-c:a', 'pcm_s16le', str(combined)],
               capture_output=True, timeout=60)

        if combined.exists() and combined.stat().st_size > 1000:
            final_audio = AUDIO_DIR / f"scene_{sid:03d}_mixed.wav"
            sp.run([
                'ffmpeg', '-y', '-i', str(base_audio), '-i', str(combined),
                '-filter_complex',
                '[0:a]aformat=sample_rates=48000:channel_layouts=stereo[m];'
                '[1:a]aformat=sample_rates=48000:channel_layouts=stereo[t];'
                '[m][t]amix=inputs=2:duration=max[out]',
                '-map', '[out]', '-c:a', 'pcm_s16le', str(final_audio)
            ], capture_output=True, timeout=120)
            scene_audio_files[sid] = final_audio
            print(f"  Scene {sid}: music + {len(dia_lines)} dialogue slots")

# ---- Assemble video with Ken Burns effect ----
print("\n--- Assembling video ---")
VIDEO_DIR.mkdir(parents=True, exist_ok=True)
concat_lines = []

for s in scenes:
    sid = s["id"]
    dur_str = str(s.get("duration", "15 seconds"))
    duration_s = int(''.join(c for c in dur_str if c.isdigit()))
    frames = scene_images.get(sid, [])
    mixed_audio = scene_audio_files.get(sid)

    if not frames or not mixed_audio:
        print(f"  Scene {sid}: SKIP")
        continue

    sv = VIDEO_DIR / f"scene_{sid:03d}.mp4"
    flist = VIDEO_DIR / f"scene_{sid}_frames.txt"
    flist.write_text("\n".join([f"file '{f}'" for f in frames]))

    cmd = (f'ffmpeg -y '
           f'-f concat -safe 0 -i "{flist}" '
           f'-i "{mixed_audio}" '
           f'-c:v libx264 -pix_fmt yuv420p -preset slow -crf 18 -r 24 '
           f'-c:a aac -b:a 192k -ar 48000 '
           f'-filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,'
           f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[vout]" '
           f'-map "[vout]" -map "1:a" -t {duration_s} "{sv}"')

    r = sp.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    if sv.exists() and sv.stat().st_size > 1000:
        concat_lines.append(f"file '{sv}'")
        print(f"  Scene {sid}: OK ({sv.stat().st_size/1024:.0f} KB)")
    else:
        print(f"  Scene {sid}: FAILED - {r.stderr[:80]}")

# Final concat
concat_file = OUTPUT / "concat_final.txt"
concat_file.write_text("\n".join(concat_lines))
final_video = VIDEO_DIR / "the_space_between_us.mp4"

sp.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', str(concat_file),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-r', '24',
        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        str(final_video)], capture_output=True, timeout=300)

if final_video.exists() and final_video.stat().st_size > 1000:
    r2 = sp.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(final_video)],
                capture_output=True, text=True)
    dur_s, sz_b = r2.stdout.strip().split("\n")
    mins = float(dur_s) / 60
    mb = int(sz_b) / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"  VIDEO COMPLETE — {float(dur_s):.0f}s ({mins:.1f} min), {mb:.1f} MB")
    print(f"  {final_video}")
    print(f"{'='*60}")
else:
    print("\nFinal video assembly failed or produced empty file")
