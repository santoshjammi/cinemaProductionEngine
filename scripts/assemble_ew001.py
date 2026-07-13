#!/usr/bin/env python3
"""Simple EW001 video assembly using FFmpeg."""
import subprocess, os
from pathlib import Path

out = Path("output/ew001_production")
vids = out / "videos"
vids.mkdir(exist_ok=True)

durations = {
    1:45, 2:60, 3:50, 4:55, 5:70, 6:90, 7:65,
    8:60, 9:75, 10:80, 11:85, 12:70, 13:90
}

print("Assembling EW001 video...\n")

# Build concat list
concat_lines = []
for i in range(1, 14):
    sid = f"scene_{i:02d}"
    img = out / "images" / f"{sid}.png"
    vo = out / "voiceovers" / f"{sid}_voice.mp3"
    dur = durations[i]
    
    scene_vid = vids / f"{sid}.mp4"
    
    if vo.exists():
        cmd = [
            'ffmpeg', '-y', '-loop','1','-i',str(img),
            '-i', str(vo),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
            '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
            '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-shortest',
            str(scene_vid)
        ]
    else:
        cmd = [
            'ffmpeg', '-y', '-loop','1','-i',str(img),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
            '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-an',
            str(scene_vid)
        ]
    
    r = subprocess.run(cmd, capture_output=True, text=True)
    if scene_vid.exists():
        concat_lines.append(f"file '{scene_vid}'")
        print(f"  [{i}/13] {sid}: OK ({dur}s)")
    else:
        print(f"  [{i}/13] {sid}: FAILED - {r.stderr[:100]}")

if not concat_lines:
    print("No scenes created!")
    exit(1)

# Write concat list
clist = vids / "concat.txt"
clist.write_text("\n".join(concat_lines))

# Final assembly
final = out / "ew001_emotional_withdrawal.mp4"
print(f"\nAssembling final video...")
cmd = [
    'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(clist),
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
    '-pix_fmt', 'yuv420p', '-r', '24',
    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
    '-movflags', '+faststart', str(final)
]
r = subprocess.run(cmd, capture_output=True, text=True)

if final.exists():
    size = final.stat().st_size / (1024*1024)
    dr = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(final)], capture_output=True, text=True)
    dur = float(dr.stdout.strip()) if dr.returncode==0 else 0
    print(f"\n{'='*60}")
    print("EW001 VIDEO GENERATED!")
    print(f"{'='*60}")
    print(f"Output: {final}")
    print(f"Size: {size:.1f} MB")
    print(f"Duration: {dur:.1f}s ({dur/60:.1f} min)")
    print(f"Scenes: 13")
    print(f"{'='*60}")
else:
    print(f"Failed: {r.stderr[:300]}")
