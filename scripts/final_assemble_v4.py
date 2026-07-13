#!/usr/bin/env python3
"""Final EW001 video - proper duration handling without -shortest."""
import subprocess
from pathlib import Path

out = Path("output/ew001_production")
vids = out / "videos"
vids.mkdir(exist_ok=True)

durations = {
    1:45, 2:60, 3:50, 4:55, 5:70, 6:90, 7:65,
    8:60, 9:75, 10:80, 11:85, 12:70, 13:90
}

print("Creating scene videos with CORRECT durations...\n")

scene_files = []
for i in range(1, 14):
    sid = f"scene_{i:02d}"
    img = out / "images" / f"{sid}.png"
    vo = out / "voiceovers" / f"{sid}_voice.mp3"
    dur = durations[i]
    
    scene_vid = vids / f"{sid}.mp4"
    
    if vo.exists():
        # Get voiceover duration
        vo_dur = float(subprocess.run(
            ['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(vo)],
            capture_output=True, text=True).stdout.strip())
        
        silence_dur = dur - vo_dur
        
        # Create extended audio with silence padding
        ext_audio = out / "music" / f"{sid}_ext.wav"
        if silence_dur > 0:
            silence_file = out / "music" / f"{sid}_silence.wav"
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi', 
                '-i', 'anullsrc=r=48000:cl=stereo',
                '-t', str(silence_dur), '-c:a', 'pcm_s16le', str(silence_file)
            ], capture_output=True)
            
            # Concatenate audio files
            concat_audio = out / "music" / f"{sid}_concat.txt"
            concat_audio.write_text(f"file '{vo}'\nfile '{silence_file}'\n")
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', str(concat_audio), '-c:a', 'pcm_s16le', str(ext_audio)
            ], capture_output=True)
        else:
            subprocess.run(['cp', str(vo), str(ext_audio)], capture_output=True)
        
        # Create video with looping image + extended audio (NO -shortest!)
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', str(img),
            '-i', str(ext_audio),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
            '-t', str(dur),  # Use -t to control duration, NOT -shortest
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
            str(scene_vid)
        ]
    else:
        cmd = [
            'ffmpeg', '-y', '-loop','1','-i',str(img),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
            '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-pix_fmt', 'yuv420p', '-an', str(scene_vid)
        ]
    
    r = subprocess.run(cmd, capture_output=True, text=True)
    
    if scene_vid.exists():
        actual_dur = float(subprocess.run(
            ['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(scene_vid)],
            capture_output=True, text=True).stdout.strip())
        scene_files.append(str(scene_vid))
        print(f"  [{i}/13] {sid}: {actual_dur:.1f}s")
    else:
        print(f"  [{i}/13] {sid}: FAILED - {r.stderr[:100]}")

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
