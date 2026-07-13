#!/usr/bin/env python3
"""Fix EW001 video - add audio, better images, and proper duration."""
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
print("FIXING EW001 VIDEO")
print("=" * 60)

# STEP 1: Generate better placeholder images with text overlays
print("\nStep 1: Generating cinematic placeholder images...")
from PIL import Image, ImageDraw, ImageFont
import random

for i in range(1, 14):
    sid = f"scene_{i:02d}"
    img_path = out / "images" / f"{sid}.png"
    
    # Create cinematic gradient background
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Cinematic color palettes for each scene
    palettes = [
        [(30,40,60), (80,90,120)],  # Morning - cool blues
        [(50,50,50), (100,100,100)],  # Kitchen - gray
        [(40,50,70), (90,100,130)],  # Work - blue tones
        [(60,50,40), (120,100,80)],  # Phone call - warm
        [(40,40,40), (80,80,80)],  # Dinner - dark
        [(70,60,50), (130,110,90)],  # Irreversible moment - sepia
        [(20,30,50), (40,60,90)],  # Rain - deep blue
        [(80,70,50), (140,120,80)],  # Friend's apartment - warm gold
        [(50,40,60), (100,80,120)],  # Attempt - purple tones
        [(60,55,45), (110,100,80)],  # Architect's model - warm wood
        [(70,65,60), (120,110,100)],  # Letter - parchment
        [(90,85,80), (140,130,120)],  # Decision - neutral
        [(20,25,35), (60,70,90)],  # Threshold - dramatic contrast
    ]
    
    top_color = palettes[i-1][0]
    bottom_color = palettes[i-1][1]
    
    for y in range(height):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / height)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / height)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add vignette effect
    for y in range(height):
        for x in range(width):
            dx = abs(x - width/2) / (width/2)
            dy = abs(y - height/2) / (height/2)
            dist = (dx*dx + dy*dy) ** 0.5
            if dist > 0.4:
                darkness = int((dist - 0.4) * 80)
                r, g, b = img.getpixel((x, y))
                img.putpixel((x, y), (max(0, r-darkness), max(0, g-darkness), max(0, b-darkness)))
    
    # Add scene title overlay
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
    except:
        font = ImageFont.load_default()
    
    titles = [
        "Morning Routine", "The Kitchen Silence", "Work as Escape",
        "The Phone Call", "Dinner for Two", "The Irreversible Moment",
        "Walking in the Rain", "The Friend's Apartment", "The Attempt",
        "The Architect's Model", "The Letter", "The Decision", "The Threshold"
    ]
    
    # Draw semi-transparent overlay for text
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
    img_pil = img.convert('RGBA')
    blended = Image.alpha_composite(img_pil, overlay)
    img = blended.convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Add title text
    bbox = draw.textbbox((0, 0), titles[i-1], font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (width - tw) // 2
    y = height - 150
    
    # Text shadow
    draw.text((x+2, y+2), titles[i-1], fill=(0, 0, 0), font=font)
    draw.text((x, y), titles[i-1], fill=(255, 255, 255), font=font)
    
    # Add scene number
    try:
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except:
        small_font = font
    
    draw.text((x, y + th + 20), f"Scene {i} of 13", fill=(200, 200, 200), font=small_font)
    
    img.save(img_path)

print("  ✅ Generated 13 cinematic images with titles")

# STEP 2: Create scene videos WITH audio (voiceover + silence padding)
print("\nStep 2: Creating scene videos with proper audio...")

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
        
        # Create video with image + extended audio (NO -shortest!)
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', str(img_path),
            '-i', str(ext_audio),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,crop=1920:1080',
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
        
        # Verify audio exists
        has_audio = 'audio' in subprocess.run(
            ['ffprobe','-v','error','-show_streams','-select_streams','a','-of','default=noprint_wrappers=1:nokey=1',str(scene_vid)],
            capture_output=True, text=True).stdout
        
        scene_files.append(str(scene_vid))
        print(f"  [{i}/13] {sid}: {actual_dur:.1f}s {'✅ WITH AUDIO' if has_audio else '⚠️ NO AUDIO'}")
    else:
        print(f"  [{i}/13] {sid}: FAILED - {r.stderr[:100]}")

if not scene_files:
    print("No scenes created!")
    exit(1)

# STEP 3: Concatenate into final video
print(f"\nStep 3: Assembling final video ({len(scene_files)} scenes)...")

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
    streams = subprocess.run(
        ['ffprobe','-v','error','-show_streams','-of','json',str(final)],
        capture_output=True, text=True)
    stream_info = streams.json() if hasattr(streams, 'json') else {}
    
    print(f"\n{'='*60}")
    print("EW001 VIDEO FIXED AND REGENERATED!")
    print(f"{'='*60}")
    print(f"Output: {final}")
    print(f"Size: {size:.1f} MB")
    print(f"Duration: {dur:.1f}s ({dur/60:.1f} minutes)")
    print(f"Scenes: {len(scene_files)}")
    print(f"Video Resolution: 1920x1080")
    
    # Check if audio exists
    has_audio_stream = False
    try:
        probe = subprocess.run(
            ['ffprobe','-v','error','-show_streams','-of','default=noprint_wrappers=0',str(final)],
            capture_output=True, text=True)
        has_audio = 'codec_type=audio' in probe.stdout
        print(f"Audio Stream: {'✅ YES' if has_audio else '❌ NO'}")
    except:
        print("Audio Stream: ❌ Could not verify")
    
    print(f"{'='*60}")
else:
    print(f"\nFailed: {r.stderr[:500]}")
