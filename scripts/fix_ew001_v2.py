#!/usr/bin/env python3
"""Fix EW001 - proper audio+video merge."""
import subprocess
from pathlib import Path

out = Path("output/ew001_production")
vids = out / "videos"
vids.mkdir(exist_ok=True)

durations = {
    1:45, 2:60, 3:50, 4:55, 5:70, 6:90, 7:65,
    8:60, 9:75, 10:80, 11:85, 12:70, 13:90
}

print("Creating scene videos with CORRECT audio...\n")

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
        
        # Create extended audio with silence padding
        ext_audio = out / "music" / f"{sid}_ext.wav"
        if silence_dur > 0:
            silence_file = out / "music" / f"{sid}_silence.wav"
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi', 
                '-i', 'anullsrc=r=48000:cl=stereo',
                '-t', str(silence_dur), '-c:a', 'pcm_s16le', str(silence_file)
            ], capture_output=True)
            
            concat_audio = out / "music" / f"{sid}_aconcat.txt"
            concat_audio.write_text(f"file '{vo_path}'\nfile '{silence_file}'\n")
            subprocess.run([
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', str(concat_audio), '-c:a', 'pcm_s16le', str(ext_audio)
            ], capture_output=True)
        else:
            subprocess.run(['cp', str(vo_path), str(ext_audio)], capture_output=True)
        
        # Step 1: Create video-only with looping image for FULL duration
        temp_vid = vids / f"{sid}_temp.mp4"
        subprocess.run([
            'ffmpeg', '-y', '-loop','1','-i',str(img_path),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
            '-t', str(dur), '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-pix_fmt', 'yuv420p', '-an', str(temp_vid)
        ], capture_output=True)
        
        # Step 2: Combine video + audio using -map explicitly (NO -shortest!)
        cmd = [
            'ffmpeg', '-y',
            '-i', str(temp_vid),
            '-i', str(ext_audio),
            '-map', '0:v:0',  # Video from first input
            '-map', '1:a:0',  # Audio from second input
            '-c:v', 'copy',   # Copy video (no re-encode)
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
            '-t', str(dur),   # Use -t to control final duration
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
        print(f"  [{i}/13] {sid}: FAILED - {r.stderr[:100]}")

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
        print(f"Audio Codec: {audio_probe.stdout[:100]}")
    
    print(f"{'='*60}")
else:
    print(f"\nFailed: {r.stderr[:500]}")
