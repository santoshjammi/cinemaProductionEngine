#!/usr/bin/env python3
"""Final EW001 video assembly with correct durations."""
import subprocess
from pathlib import Path

out = Path("output/ew001_production")
vids = out / "videos"
vids.mkdir(exist_ok=True)

# Scene durations in seconds
durations = {
    1:45, 2:60, 3:50, 4:55, 5:70, 6:90, 7:65,
    8:60, 9:75, 10:80, 11:85, 12:70, 13:90
}

print("Creating scene videos with correct durations...\n")

scene_files = []
for i in range(1, 14):
    sid = f"scene_{i:02d}"
    img = out / "images" / f"{sid}.png"
    vo = out / "voiceovers" / f"{sid}_voice.mp3"
    dur = durations[i]
    
    scene_vid = vids / f"{sid}.mp4"
    
    if vo.exists():
        # Create video with image + voiceover, NO -shortest
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', str(img),
            '-i', str(vo),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
            '-t', str(dur),
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
            '-shortest',  # This will use voiceover duration, then we extend
            str(scene_vid)
        ]
    else:
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', str(img),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
            '-t', str(dur),
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-an',
            str(scene_vid)
        ]
    
    r = subprocess.run(cmd, capture_output=True, text=True)
    
    # If voiceover exists but is short, we need to extend the video with silence
    if vo.exists() and scene_vid.exists():
        actual_dur = float(subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(scene_vid)],
            capture_output=True, text=True).stdout.strip())
        
        if actual_dur < dur:
            # Create silent audio to fill the gap
            silence_dur = dur - actual_dur
            silence_file = out / "music" / f"silence_{i}.wav"
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=stereo',
                '-t', str(silence_dur), '-c:a', 'pcm_s16le', str(silence_file)
            ], capture_output=True)
            
            # Concatenate original video with silent audio
            extended_vid = vids / f"{sid}_extended.mp4"
            concat_file = out / "music" / f"concat_{i}.txt"
            concat_file.write_text(f"file '{scene_vid}'\nfile '{silence_file}'\n")
            
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', str(concat_file), '-c', 'copy', str(extended_vid)
            ], capture_output=True)
            
            scene_files.append(str(extended_vid))
            print(f"  [{i}/13] {sid}: {dur}s (extended with silence)")
        else:
            scene_files.append(str(scene_vid))
            print(f"  [{i}/13] {sid}: {dur}s")
    elif scene_vid.exists():
        scene_files.append(str(scene_vid))
        print(f"  [{i}/13] {sid}: {dur}s (no audio)")
    else:
        print(f"  [{i}/13] {sid}: FAILED")

if not scene_files:
    print("No scenes created!")
    exit(1)

# Write concat list with absolute paths
clist = vids / "final_concat.txt"
with open(clist, 'w') as f:
    for sf in scene_files:
        f.write(f"file '{sf}'\n")

# Final assembly
final = out.parent / "ew001_emotional_withdrawal.mp4"
print(f"\nAssembling final video ({len(scene_files)} scenes)...")
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
    print("EW001 VIDEO GENERATED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"Output: {final}")
    print(f"Size: {size:.1f} MB")
    print(f"Duration: {dur:.1f}s ({dur/60:.1f} minutes)")
    print(f"Scenes: {len(scene_files)}")
    print(f"{'='*60}")
else:
    print(f"\nFailed: {r.stderr[:500]}")
