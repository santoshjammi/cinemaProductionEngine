"""Audio Pipeline -- local-only FFmpeg-based mixing with emotion-aware volume ducking."""
from __future__ import annotations

import logging
import subprocess as sp
from pathlib import Path

logger = logging.getLogger("pipeline.audio")

def _shell_quote(s: str) -> str:
    s = str(s)
    if all(c not in s for c in ' \t\n\'"()[]{};&|'):
        return s
    return "'" + s.replace("'", "'\\''") + "'"

def _probe(path: Path | str) -> float | None:
    path = str(Path(path).resolve())
    try:
        r = sp.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1",
             path],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            return float(r.stdout.strip())
    except Exception:
        pass
    return None

def _call(*args, **kw) -> sp.CompletedProcess:
    logger.debug(f"FFmpeg cmd: {args}")
    return sp.run(
        ["ffmpeg", "-y"] + list(args),
        capture_output=True, timeout=300, text=True, **kw,
    )

# Emotion-based audio ducking profiles (relative to dialogue)
Ducking_PROFILES = {
    "guarded":     {"music_volume_db": "-6dB", "description": "Warm, sparse piano — hope is still there."},
    "withdrawn":   {"music_volume_db": "-10dB", "description": "Very quiet, minimalist tones — the silence is loud."},
    "frustrated":  {"music_volume_db": "-4dB", "description": "Tense strings that feel like they are 'holding back' a release."},
    "emotional_peak": {"music_volume_db": "-2dB", "description": "A sudden swell of strings that abruptly cuts to silence on the flinch."},
    "resolved":    {"music_volume_db": "-12dB", "description": "Fading into pure ambient noise — the 'afterlife' of the relationship."}
}

def mix_audio(
    music_path: str | Path,
    tts_paths: list[str | Path],
    mixed_path: str | Path,
    duration_s: int = 60,
    emotion: str = "calm",
) -> Path:
    """Mix CC0 background music with staggered foreground TTS dialogue.

    Refactored to avoid zero-byte files by combining TTS into one track first,
    then layering music with emotion-aware volume ducking.
    """
    music = Path(music_path).resolve()
    tts = [Path(p).resolve() for p in tts_paths]
    out = Path(mixed_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    # If no dialogue lines, just output the trimmed music
    if not tts:
        _call("-i", str(music), "-t", str(duration_s), "-ac", "2", "-b:a", "192k", str(out))
        return out

    tmp_dir = out.parent / "_am_tmp"
    tmp_dir.mkdir(exist_ok=True)
    
    # Step 1: Normalize all TTS clips to mono/48kHz wav for reliable concat
    normed: list[Path] = []
    for i, t in enumerate(tts):
        if not t.exists():
            logger.warning(f"TTS file missing: {t}")
            continue
        nf = tmp_dir / f"s{i}.wav"
        _call("-i", str(t), "-ac", "1", "-ar", "48000", str(nf))
        normed.append(nf)

    # Step 2: Concatenate all TTS clips with silence gaps using FFmpeg concat demuxer
    if len(normed) > 1:
        concat_txt = tmp_dir / "tts_concat.txt"
        lines = []
        for i, nf in enumerate(normed):
            if i > 0:
                sil_f = tmp_dir / f"sil_{i}.wav"
                _call("-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono:d=1.5", "-ac", "2", str(sil_f))
                if sil_f.exists():
                    lines.append(f"file \\'{sil_f}\\'")
            lines.append(f"file \\'{nf}\\'")
        concat_txt.write_text("\\n".join(lines))
        
        combined_voice = tmp_dir / "combined_voice.wav"
        r = _call("-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c:a", "pcm_s16le", str(combined_voice))
        if r.returncode != 0 or not combined_voice.exists():
            logger.error("Failed to concat TTS tracks")
            return out # Return empty/failed file to be handled by caller
    else:
        combined_voice = normed[0] if normed else tmp_dir / "silence.wav"
        _call("-f", "lavfi", "-i", "anullsrc=r=48000:d=10", "-ac", "2", str(combined_voice))

    # Step 3: Apply emotion-aware volume ducking to the music track
    profile = Ducking_PROFILES.get(emotion, {"music_volume_db": "-6dB"})
    music_vol_db = profile["music_volume_db"]
    
    # Ensure voice is normalized to 0dB (foreground) and music is ducked (background)
    final_filter = (
        f"[1:a]volume={music_vol_db},aresample=48000,apad=pts_start=0[m];" # Music track ducked
        f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v];"       # Voice track normal
        f"[m][v]amix=inputs=2:duration=max:dropout_transition=3[out]"
    )

    r = _call(
        "-i", str(music), "-i", str(combined_voice),
        "-filter_complex", final_filter,
        "-map", "[out]",
        "-c:a", "aac", "-b:a", "192k", str(out)
    )

    # Cleanup temp files
    import shutil
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
        
    logger.info(f"Audio mix completed for {out.name} (Emotion: {emotion})")
    return out
