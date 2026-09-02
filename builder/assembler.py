"""
Builder Authority - Video Assembly
Combines images and audio into the final MP4 deliverable.
"""
import subprocess
from pathlib import Path

OUTPUT_DIR = Path("/Users/santosh/Desktop/projects/videoGen/output/builder_assets")

def assemble_video(output_path=OUTPUT_DIR / "final_video.mp4"):
    print(f"[Builder] Assembling video to {output_path}...")
    
    # 1. Generate image list for ffmpeg
    images_dir = OUTPUT_DIR / "images"
    scene_files = sorted([f for f in images_dir.glob("*.png")])
    
    if not scene_files:
        print("[Builder] No images found to assemble.")
        return

    # Create a file list for ffmpeg
    list_file = OUTPUT_DIR / "image_list.txt"
    with open(list_file, 'w') as f:
        for img in scene_files:
            f.write(f"file '{img}'\n")
            f.write("duration 5\n") # 5 seconds per scene

    # 2. Generate audio list for ffmpeg (simplified)
    audio_dir = OUTPUT_DIR / "audio"
    audio_files = sorted([f for f in audio_dir.glob("*.wav")])
    
    # Simple concat of all audio clips for the final mix
    if audio_files:
        audio_list_file = OUTPUT_DIR / "audio_list.txt"
        with open(audio_list_file, 'w') as f:
            for a in audio_files:
                f.write(f"file '{a}'\n")

    # 3. Run FFmpeg to assemble
    # -f concat is tricky with mixed inputs, so we'll use a simpler approach:
    # Filter_complex to overlay audio onto images
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-loop", "1", "-t", "5", "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p", 
        "-i", str(audio_files[0]) if audio_files else "/dev/null", # Use first audio as base
        "-c:v", "libx264", "-preset", "fast",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, check=True,
        timeout=300)
        print(f"[Builder] Video assembled successfully at {output_path}")
    except Exception as e:
        print(f"[Builder] Assembly failed (likely ffmpeg issue): {e}")
