#!/usr/bin/env python3
"""Final EW001 video - two-step process."""
import subprocess
from pathlib import Path

out = Path("output/ew001_production")
vids = out / "videos"
vids.mkdir(exist_ok=True)

durations = {
    1:45, 2:60, 3:50, 4:55, 5:70, 6:90, 7:65,
    8:60, 9:75, 10:80, 11:85, 12:70, 13:90
}

print("Step 1: Creating video-only scenes with looping images...\n")

video_files = []
for i in range(1, 14):
    sid = f"scene_{i:02d}"
    img = out / "images" / f"{sid}.png"
    dur = durations[i]
    
    video_only = vids / f"{sid}_video.mp4"
    
    cmd = [
        'ffmpeg', '-y', '-loop','1','-i',str(img),
        '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
        '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p', '-an', str(video_only)
    ]
    
    r = subprocess.run(cmd, capture_output=True, text=True)
    
    if video_only.exists():
        actual_dur = float(subprocess.run(
            ['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(video_only)],
            capture_output=True, text=True).stdout.strip())
        video_files.append(str(video_only))
        print(f"  [{i}/13] {sid}: {actual_dur:.1f}s (video only)")
    else:
        print(f"  [{i}/13] {sid}: FAILED")

print("\nStep 2: Adding voiceover with silence padding...\n")

scene_files = []
for i in range(1, 14):
    sid = f"scene_{i:02d}"
    vo = out / "voiceovers" / f"{sid}_voice.mp3"
    dur = durations[i]
    
    final_scene = vids / f"{sid}.mp4"
    
    if vo.exists() and i < len(video_files):
        # Get voiceover duration
        vo_dur = float(subprocess.run(
            ['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(vo)],
            capture_output=True, text=True).stdout.strip())
        
        silence_dur = dur - vo_dur
        
        if silence_dur > 0:
            # Create silent audio
            silence_file = out / "music" / f"{sid}_silence.wav"
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi', 
                '-i', 'anullsrc=r=48000:cl=stereo',
                '-t', str(silence_dur), '-c:a', 'pcm_s16le', str(silence_file)
            ], capture_output=True)
            
            # Concatenate voiceover + silence into extended audio
            ext_audio = out / "music" / f"{sid}_ext.wav"
            concat_audio = out / "music" / f"{sid}_aconcat.txt"
            concat_audio.write_text(f"file '{vo}'\nfile '{silence_file}'\n")
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', str(concat_audio), '-c:a', 'pcm_s16le', str(ext_audio)
            ], capture_output=True)
            
            # Combine video + extended audio using filter_complex
            cmd = [
                'ffmpeg', '-y',
                '-i', video_files[i-1],
                '-i', str(ext_audio),
                '-filter_complex', '[0:v][1:a]nullsrc=s=1920x1080:r=24,format=yuv420p[v];[v][1:a]amerge=inputs=2[a]',
                '-map', '[v]', '-map', '[a]',
                '-t', str(dur),
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                str(final_scene)
            ]
        else:
            # Voiceover is longer than scene - just trim it
            cmd = [
                'ffmpeg', '-y',
                '-i', video_files[i-1],
                '-i', str(vo),
                '-filter_complex', '[0:v][1:a]amerge=inputs=2[a]',
                '-map', '[v]', '-map', '[a]',
                '-t', str(dur),
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                str(final_scene)
            ]
    else:
        # No voiceover - just copy video
        subprocess.run(['cp', video_files[i-1], final_scene], capture_output=True)
    
    if final_scene.exists():
        actual_dur = float(subprocess.run(
            ['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(final_scene)],
            capture_output=True, text=True).stdout.strip())
        scene_files.append(str(final_scene))
        print(f"  [{i}/13] {sid}: {actual_dur:.1f}s (with audio)")
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
print(f"\nStep 3: Assembling final video ({len(scene_files)} scenes)...")
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
