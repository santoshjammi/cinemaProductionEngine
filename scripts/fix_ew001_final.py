#!/usr/bin/env python3
"""Final fix for EW001 - single-step ffmpeg with aevalsrc for silence."""
import subprocess
from pathlib import Path

out = Path("output/ew001_production")
vids = out / "videos"
vids.mkdir(exist_ok=True)

durations = {
    1:45, 2:60, 3:50, 4:55, 5:70, 6:90, 7:65,
    8:60, 9:75, 10:80, 11:85, 12:70, 13:90
}

print("=" * 60)
print("FINAL FIX FOR EW001 VIDEO")
print("=" * 60)

scene_files = []
for i in range(1, 14):
    sid = f"scene_{i:02d}"
    img_path = out / "images" / f"{sid}.png"
    vo_path = out / "voiceovers" / f"{sid}_voice.mp3"
    dur = durations[i]
    
    scene_vid = vids / f"{sid}.mp4"
    
    if vo_path.exists():
        # Get voiceover duration
        vo_dur = float(subprocess.run(
            ['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(vo_path)],
            capture_output=True, text=True).stdout.strip())
        
        silence_dur = dur - vo_dur
        
        # Use aevalsrc to generate silence directly (no file needed!)
        # Combine voiceover + silence using amovie filter
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', str(img_path),
            '-i', str(vo_path),
            '-f', 'lavfi', '-i', f'aevalsrc=0:d={silence_dur}:s=48000:c=stereo',
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
            '-filter_complex', 
                f'[1:a][2:a]concat=n=2:v=0:a=1[outa];'
                f'[outa]apad=whole_dur={dur}[audio]',
            '-map', '0:v', '-map', '[audio]',
            '-t', str(dur),
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
            str(scene_vid)
        ]
    else:
        cmd = [
            'ffmpeg', '-y', '-loop','1','-i',str(img_path),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
            '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-pix_fmt', 'yuv420p', '-an', str(scene_vid)
        ]
    
    r = subprocess.run(cmd, capture_output=True, text=True)
    
    if scene_vid.exists():
        actual_dur = float(subprocess.run(
            ['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(scene_vid)],
            capture_output=True, text=True).stdout.strip())
        
        # Check for audio stream
        probe = subprocess.run(
            ['ffprobe','-v','error','-show_streams','-select_streams','a','-of','default=noprint_wrappers=1',str(scene_vid)],
            capture_output=True, text=True)
        has_audio = 'codec_type=audio' in probe.stdout
        
        scene_files.append(str(scene_vid))
        status = '✅ WITH AUDIO' if has_audio else '⚠️ NO AUDIO'
        print(f"  [{i}/13] {sid}: {actual_dur:.1f}s {status}")
    else:
        print(f"  [{i}/13] {sid}: FAILED")
        print(f"     stderr: {r.stderr[:200]}")

if not scene_files:
    print("No scenes created!")
    exit(1)

# Concatenate into final video
print(f"\nAssembling final video ({len(scene_files)} scenes)...")

clist = vids / "final_concat.txt"
with open(clist, 'w') as f:
    for sf in scene_files:
        f.write(f"file '{sf}'\n")

final = out.parent / "ew001_emotional_withdrawal.mp4"
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
    
    # Check streams
    probe = subprocess.run(
        ['ffprobe','-v','error','-show_streams','-of','default=noprint_wrappers=0',str(final)],
        capture_output=True, text=True)
    has_audio = 'codec_type=audio' in probe.stdout
    
    print(f"\n{'='*60}")
    print("EW001 VIDEO FIXED AND REGENERATED!")
    print(f"{'='*60}")
    print(f"Output: {final}")
    print(f"Size: {size:.1f} MB")
    print(f"Duration: {dur:.1f}s ({dur/60:.1f} minutes)")
    print(f"Scenes: {len(scene_files)}")
    print(f"Video Resolution: 1920x1080")
    print(f"Audio Stream: {'✅ YES' if has_audio else '❌ NO'}")
    
    if has_audio:
        audio_probe = subprocess.run(
            ['ffprobe','-v','error','-show_streams','-select_streams','a','-of','default=noprint_wrappers=0',str(final)],
            capture_output=True, text=True)
        print(f"Audio Codec: {audio_probe.stdout[:150]}")
    
    print(f"{'='*60}")
else:
    print(f"\nFailed: {r.stderr[:500]}")
