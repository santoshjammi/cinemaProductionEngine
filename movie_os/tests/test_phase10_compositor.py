"""Tests for the ffmpeg compositor (Phase 10+)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _has_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


pytestmark = pytest.mark.skipif(
    not _has_ffmpeg(), reason="ffmpeg not installed"
)


@pytest.fixture
def sample_image(tmp_path):
    from PIL import Image
    img = Image.new("RGB", (256, 256), color=(40, 80, 160))
    p = tmp_path / "scene.png"
    img.save(p)
    return p


@pytest.fixture
def sample_wav(tmp_path):
    """Generate a 1-second test wav with simple sine wave."""
    import wave
    import struct
    import math
    p = tmp_path / "tone.wav"
    sample_rate = 44100
    duration = 1.0
    frequency = 440
    n_samples = int(sample_rate * duration)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        for i in range(n_samples):
            sample = int(16384 * math.sin(2 * math.pi * frequency * i / sample_rate))
            w.writeframes(struct.pack("<h", sample))
    return p


class TestProbe:
    def test_probe_duration(self, sample_wav):
        from movie_os.agents.compositor import probe_duration
        d = probe_duration(sample_wav)
        assert 0.9 < d < 1.1

    def test_probe_missing_returns_zero(self, tmp_path):
        from movie_os.agents.compositor import probe_duration
        assert probe_duration(tmp_path / "nope.wav") == 0.0


class TestRenderSceneClip:
    def test_static_render(self, sample_image, tmp_path):
        from movie_os.agents.compositor import render_scene_clip, probe_duration
        out = tmp_path / "static.mp4"
        result = render_scene_clip(
            sample_image, 2.0, out, ken_burns="static",
        )
        assert result.exists()
        assert result.stat().st_size > 1000
        d = probe_duration(result)
        assert 1.8 < d < 2.2

    def test_ken_burns_render(self, sample_image, tmp_path):
        from movie_os.agents.compositor import render_scene_clip, probe_duration
        out = tmp_path / "kb.mp4"
        result = render_scene_clip(
            sample_image, 2.0, out, ken_burns="ken-burns",
        )
        assert result.exists()
        d = probe_duration(result)
        assert 1.8 < d < 2.2

    def test_render_with_voice(self, sample_image, sample_wav, tmp_path):
        from movie_os.agents.compositor import render_scene_clip
        out = tmp_path / "with_voice.mp4"
        result = render_scene_clip(
            sample_image, 2.0, out, voice_path=sample_wav, ken_burns="static",
        )
        assert result.exists()

    def test_render_with_music(self, sample_image, sample_wav, tmp_path):
        from movie_os.agents.compositor import render_scene_clip
        out = tmp_path / "with_music.mp4"
        result = render_scene_clip(
            sample_image, 2.0, out,
            music_path=sample_wav, music_volume=0.2,
            ken_burns="static",
        )
        assert result.exists()

    def test_render_with_both_audio(self, sample_image, sample_wav, tmp_path):
        from movie_os.agents.compositor import render_scene_clip
        out = tmp_path / "full.mp4"
        result = render_scene_clip(
            sample_image, 2.0, out,
            voice_path=sample_wav,
            music_path=sample_wav,
            music_volume=0.2,
            ken_burns="ken-burns",
        )
        assert result.exists()


class TestConcat:
    def test_concat_two_clips(self, sample_image, tmp_path):
        from movie_os.agents.compositor import render_scene_clip, concat_clips, probe_duration
        c1 = render_scene_clip(sample_image, 1.0, tmp_path / "c1.mp4", ken_burns="static")
        c2 = render_scene_clip(sample_image, 1.0, tmp_path / "c2.mp4", ken_burns="static")
        out = tmp_path / "concat.mp4"
        result = concat_clips([c1, c2], out)
        assert result.exists()
        d = probe_duration(result)
        assert 1.8 < d < 2.5

    def test_concat_many_clips(self, sample_image, tmp_path):
        from movie_os.agents.compositor import render_scene_clip, concat_clips, probe_duration
        clips = []
        for i in range(5):
            c = render_scene_clip(sample_image, 0.5, tmp_path / f"c{i}.mp4", ken_burns="static")
            clips.append(c)
        out = tmp_path / "many.mp4"
        result = concat_clips(clips, out)
        assert result.exists()
        d = probe_duration(result)
        assert 2.0 < d < 3.0
