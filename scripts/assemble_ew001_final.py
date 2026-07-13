#!/usr/bin/env python3
"""Complete the ew001 video assembly using FFmpeg."""

import os
import subprocess
from pathlib import Path

output_dir = Path("output/ew001_production")
images_dir = output_dir / "images"
voiceovers_dir = output_dir / "voiceovers"
music_dir = output_dir / "music"
videos_dir = output_dir / "videos"

# Scene durations (from the pipeline)
scene_durations = {
    "scene_01": 45,
    "scene_02": 60,
    "scene_03": 50,
    "scene_04": 55,
    "scene_05": 70,
    "scene_06": 90,
    "scene_07": 65,
    "scene_08": 60,
    "scene_09": 75,
    "scene_10": 80,
    "scene_11": 85,
    "scene_12": 70,
    "scene_13": 90,
}

print("=" * 60)
print("🎬 EW001 Video Assembly - Final Phase")
print("=" * 60)

# Step 1: Create individual scene videos with Ken Burns effect
print("\nStep 1: Creating scene videos with Ken Burns effect...")
scene_videos = []

for scene_num in range(1, 14):
    scene_id = f"scene_{scene_num:02d}"
    image_path = images_dir / f"{scene_id}.png"
    duration = scene_durations.get(scene_id, 30)
    
    if not image_path.exists():
        print(f"  ⚠️ {scene_id}: No image found, skipping")
        continue
    
    output_file = videos_dir / f"{scene_id}_video.mp4"
    
    # Simple zoom effect (Ken Burns style)
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', str(image_path),
        '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080,zoompan=z=\'min(zoom+0.0015):x=\'iw/2-(iw/zoom/2)+50*on\'':y=\'ih/2-(ih/zoom/2)+30*on\'':d={duration*25}:s=1920x1080:f=24',
        '-t', str(duration),
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '20',
        '-pix_fmt', 'yuv420p',
        '-r', '24',
        '-an',
        str(output_file)
    ]
    
    print(f"  Processing {scene_id} ({duration}s)...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and output_file.exists():
        scene_videos.append(str(output_file))
        print(f"    ✅ Created: {output_file}")
    else:
        print(f"    ⚠️ Failed: {result.stderr[:200] if result.stderr else 'Unknown error'}")

print(f"\n✅ Created {len(scene_videos)} scene videos")

# Step 2: Create video with audio (voiceover + music)
print("\nStep 2: Adding audio to scenes...")
scene_videos_with_audio = []

for i, scene_num in enumerate(range(1, 14)):
    scene_id = f"scene_{scene_num:02d}"
    scene_video = videos_dir / f"{scene_id}_video.mp4"
    
    if not scene_video.exists():
        continue
    
    voiceover = voiceovers_dir / f"{scene_id}_voice.mp3"
    music = music_dir / f"{scene_id}_music.wav"
    
    output_file = videos_dir / f"{scene_id}_final.mp4"
    
    if voiceover.exists() and music.exists():
        # Both voiceover and music
        cmd = [
            'ffmpeg', '-y',
            '-i', str(scene_video),
            '-i', str(voiceover),
            '-i', str(music),
            '-filter_complex', '[1:a]volume=1.0[vo];[2:a]volume=0.3[music];[vo][music]amix=inputs=2:duration=first[a]',
            '-map', '0:v',
            '-map', '[a]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '20',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-ar', '48000',
            '-shortest',
            str(output_file)
        ]
    elif voiceover.exists():
        # Only voiceover
        cmd = [
            'ffmpeg', '-y',
            '-i', str(scene_video),
            '-i', str(voiceover),
            '-map', '0:v',
            '-map', '1:a',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '20',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-ar', '48000',
            '-shortest',
            str(output_file)
        ]
    else:
        # No audio, just copy video
        cmd = [
            'ffmpeg', '-y',
            '-i', str(scene_video),
            '-c', 'copy',
            str(output_file)
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and output_file.exists():
        scene_videos_with_audio.append(str(output_file))
        print(f"  ✅ {scene_id} with audio")
    else:
        # Try without music (just voiceover or video only)
        print(f"  ⚠️ {scene_id}: Retrying without music...")
        if voiceover.exists():
            cmd = [
                'ffmpeg', '-y',
                '-i', str(scene_video),
                '-i', str(voiceover),
                '-map', '0:v',
                '-map', '1:a',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '20',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-ar', '48000',
                '-shortest',
                str(output_file)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and output_file.exists():
            scene_videos_with_audio.append(str(output_file))
            print(f"    ✅ {scene_id} with voiceover only")
        else:
            # Fallback to video only
            cmd = [
                'ffmpeg', '-y',
                '-i', str(scene_video),
                '-c', 'copy',
                str(output_file)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and output_file.exists():
                scene_videos_with_audio.append(str(output_file))
                print(f"    ✅ {scene_id} video only (fallback)")

print(f"\n✅ Created {len(scene_videos_with_audio)} scenes with audio")

# Step 3: Concatenate all scenes into final video
print("\nStep 3: Assembling final video...")

concat_file = videos_dir / "final_concat.txt"
with open(concat_file, 'w') as f:
    for video in scene_videos_with_audio:
        f.write(f"file '{video}'\n")

final_video = output_dir / "videos" / "ew001_emotional_withdrawal.mp4"

cmd = [
    'ffmpeg', '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', str(concat_file),
    '-c:v', 'libx264',
    '-preset', 'medium',
    '-crf', '18',
    '-pix_fmt', 'yuv420p',
    '-r', '24',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-ar', '48000',
    '-movflags', '+faststart',
    str(final_video)
]

print("  Assembling final video...")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0 and final_video.exists():
    file_size = final_video.stat().st_size / (1024 * 1024)  # MB
    
    # Get duration
    dur_cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',
        str(final_video)
    ]
    dur_result = subprocess.run(dur_cmd, capture_output=True, text=True)
    duration = float(dur_result.stdout.strip()) if dur_result.returncode == 0 else 0
    
    print("\n" + "=" * 60)
    print("🎉 EW001 VIDEO GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Output: {final_video}")
    print(f"Size: {file_size:.1f} MB")
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"Scenes: {len(scene_videos_with_audio)}")
    print("=" * 60)
else:
    print(f"\n❌ Final assembly failed!")
    print(f"Error: {result.stderr[:500] if result.stderr else 'Unknown error'}")
