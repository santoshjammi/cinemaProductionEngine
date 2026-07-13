import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger("tts_service")


class TTSService:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Voice per playbook: "soft, conversational, tired, emotionally restrained, intimate"
        # AndrewMultilingualNeural: Warm, Authentic, Honest — not energetic
        self._voice = os.environ.get("TTS_VOICE", "en-US-AndrewMultilingualNeural")
        self._rate = os.environ.get("TTS_RATE", "-15%")    # slower = reflective
        self._volume = os.environ.get("TTS_VOLUME", "-10%")  # softer
        self._pitch = os.environ.get("TTS_PITCH", "-5Hz")    # lower = tired

    async def generate_speech(
        self,
        pipeline_id: str,
        scene_number: int,
        text: str,
        speaker_wav: Optional[str] = None,
        prosody_override: Optional[dict] = None,
        vocal_fracture: bool = False,
    ) -> dict:
        audio_dir = self.output_dir / pipeline_id / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        output_path = audio_dir / f"scene_{scene_number:03d}.mp3"
        wav_path = audio_dir / f"scene_{scene_number:03d}.wav"

        # v5.0 — per-scene prosody override
        if prosody_override:
            rate = prosody_override.get("rate", self._rate)
            volume = prosody_override.get("volume", self._volume)
            pitch = prosody_override.get("pitch", self._pitch)
            logger.info(
                "TTS prosody override for scene %d: rate=%s volume=%s pitch=%s",
                scene_number, rate, volume, pitch,
            )
        else:
            rate = self._rate
            volume = self._volume
            pitch = self._pitch

        try:
            import edge_tts

            # v1.1.2 BUGFIX: edge-tts does NOT process SSML. The old
            # _apply_vocal_fracture produced <speak><break> markup which
            # was TTS'd as literal text, making the audio unintelligible.
            #
            # New approach: split the text at loaded words, TTS each chunk
            # separately, then concatenate with 300ms silences between.
            # The first chunk gets a 400ms breath pre-pad.
            if vocal_fracture and text:
                marked_text = self._apply_vocal_fracture(text)
                chunks = self.split_vocal_fracture_chunks(marked_text)
                logger.info(
                    "TTS vocal_fracture applied for scene %d: %d chunks",
                    scene_number, len(chunks),
                )
                await self._synthesize_vocal_fracture(
                    chunks, output_path, rate, volume, pitch,
                )
            else:
                communicate = edge_tts.Communicate(
                    text,
                    self._voice,
                    rate=rate,
                    volume=volume,
                    pitch=pitch,
                )
                await communicate.save(str(output_path))

            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(output_path),
                    "-ar", "44100",
                    "-ac", "2",
                    str(wav_path),
                ],
                check=True, capture_output=True,
            )

            output_path.unlink(missing_ok=True)

            logger.info("TTS generated for scene %d (%s)", scene_number, self._voice)
            return {
                "scene_number": scene_number,
                "status": "completed",
                "audio_url": f"/api/v1/pipeline/{pipeline_id}/audio/{scene_number}",
                "error": None,
            }
        except Exception as e:
            logger.exception("TTS failed for scene %d", scene_number)
            return {
                "scene_number": scene_number,
                "status": "failed",
                "error": str(e),
            }

    # v1.1.2 — VOCAL FRACTURE HELPER (Rule 22)
    # v1.1.2 BUGFIX: edge-tts does NOT process SSML. The previous version
    # wrapped the text in <speak><break>...</speak> which was TTS'd as
    # literal text ("less than s-p-e-a-k, break time equals..."). That
    # made the irreversible moment unintelligible.
    #
    # New approach: instead of SSML, split the text at each loaded word
    # and generate a separate TTS for each chunk. The pipeline then
    # concatenates the chunks with ffmpeg silences between them, achieving
    # the same emotional-fracture effect.
    _VOCAL_FRACTURE_LOADED_WORDS = frozenset({
        "still", "almost", "dangerous", "tired", "grief", "afraid",
        "love", "lost", "alone", "home", "safe", "reaching", "remember",
        "quiet", "enough", "silence", "stayed", "stopped", "left",
    })

    async def _synthesize_vocal_fracture(
        self,
        chunks: list[str],
        output_path: Path,
        rate: str,
        volume: str,
        pitch: str,
    ) -> None:
        """v1.1.2 — Synthesize vocal_fracture audio by chunked TTS + silence.

        Each chunk is TTS'd separately, then concatenated with:
          - 400ms breath pre-pad before the first chunk
          - 300ms silence between chunks

        The viewer hears the voice "catch itself" between fragments.
        """
        import edge_tts
        import tempfile
        import shutil

        tmpdir = Path(tempfile.mkdtemp(prefix="vfracture_"))
        try:
            chunk_files: list[Path] = []
            for i, chunk_text in enumerate(chunks):
                chunk_path = tmpdir / f"chunk_{i:02d}.mp3"
                comm = edge_tts.Communicate(
                    chunk_text,
                    self._voice,
                    rate=rate, volume=volume, pitch=pitch,
                )
                await comm.save(str(chunk_path))
                chunk_files.append(chunk_path)

            # Build the ffmpeg concat command.
            # First chunk: 400ms breath pre-pad + chunk
            # Each subsequent chunk: 300ms silence + chunk
            inputs = []
            filter_parts = []

            # Convert all chunks to wav first (uniform format)
            wav_files: list[Path] = []
            for i, cf in enumerate(chunk_files):
                wf = tmpdir / f"chunk_{i:02d}.wav"
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(cf), "-ar", "44100", "-ac", "2", str(wf)],
                    check=True, capture_output=True,
                )
                wav_files.append(wf)

            # Build concat using ffmpeg concat filter
            # All inputs are wav files. Use a single concat filter.
            for wf in wav_files:
                inputs.extend(["-i", str(wf)])
            n = len(wav_files)
            concat_inputs = "".join(f"[{i}:a]" for i in range(n))
            # Pre-pad 400ms silence at the start (anullsrc) and concat
            # Use the atrim+asetpts approach to insert silence between chunks
            #
            # Simpler approach: use the ffmpeg `concat` demuxer with
            # silpad wav files inserted between chunks.
            concat_list_path = tmpdir / "concat.txt"
            with open(concat_list_path, "w") as f:
                # First chunk with breath pre-pad
                f.write(f"file 'silence_400ms.wav'\n")
                for i, wf in enumerate(wav_files):
                    f.write(f"file '{wf.name}'\n")
                    # 300ms silence between chunks (but not after the last)
                    if i < len(wav_files) - 1:
                        f.write(f"file 'silence_300ms.wav'\n")

            # Generate the silence wavs
            silence_400 = tmpdir / "silence_400ms.wav"
            silence_300 = tmpdir / "silence_300ms.wav"
            for sil_path, dur in [(silence_400, 0.4), (silence_300, 0.3)]:
                subprocess.run(
                    [
                        "ffmpeg", "-y",
                        "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
                        "-t", str(dur),
                        "-ar", "44100", "-ac", "2",
                        str(sil_path),
                    ],
                    check=True, capture_output=True,
                )

            # Concat everything
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", str(concat_list_path),
                    "-ar", "44100", "-ac", "2",
                    str(output_path),
                ],
                check=True, capture_output=True,
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _apply_vocal_fracture(self, text: str) -> str:
        """Mark loaded words in the text so the pipeline can insert silence.

        Returns the text with each loaded word surrounded by \u00ab/\u00bb markers
        that the pipeline can use to split the text into TTS chunks:

            "She \u00abstopped\u00bb. The second fork... she didn't know why."

        The pipeline's _synthesize_vocal_fracture_chunks() method then:
          1. Splits the text on these markers
          2. TTS each chunk
          3. Concatenates with silpad wavs between them
        """
        import re
        result = text
        for word in self._VOCAL_FRACTURE_LOADED_WORDS:
            # Insert \u00ab\u00bb around each loaded word (markers for split)
            pattern = re.compile(rf'\b({re.escape(word)})\b', re.IGNORECASE)
            result = pattern.sub(r'«\1»', result)
        return result

    def split_vocal_fracture_chunks(self, text: str) -> list[str]:
        """Split marked text into chunks for chunked TTS synthesis.

        Returns a list of plain text chunks. The pipeline will generate
        TTS for each chunk, then concatenate with 300ms silence between
        each chunk. The first chunk gets a 400ms breath pre-pad.
        """
        import re
        if "«" not in text:
            return [text]
        # Split on the markers, keeping the markers as separate items
        parts = re.split(r'(«[^»]+»)', text)
        chunks = []
        for p in parts:
            if p:
                # Strip the markers — the loaded word is now its own chunk
                cleaned = p.replace("«", "").replace("»", "").strip()
                if cleaned:
                    chunks.append(cleaned)
        return chunks

    def get_audio_path(self, pipeline_id: str, scene_number: int) -> Optional[Path]:
        for ext in [".wav", ".mp3"]:
            audio_path = (
                self.output_dir
                / pipeline_id
                / "audio"
                / f"scene_{scene_number:03d}{ext}"
            )
            if audio_path.exists():
                return audio_path
        return None

    def get_audio_duration(self, pipeline_id: str, scene_number: int) -> Optional[float]:
        audio_path = self.get_audio_path(pipeline_id, scene_number)
        if audio_path is None:
            return None
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path),
            ],
            capture_output=True, text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                return float(result.stdout.strip())
            except ValueError:
                return None
        return None

    def merge_audio_with_video(
        self,
        pipeline_id: str,
        scene_number: int,
    ) -> Optional[Path]:
        video_dir = self.output_dir / pipeline_id / "clips"
        audio_dir = self.output_dir / pipeline_id / "audio"
        output_dir = self.output_dir / pipeline_id / "final_clips"
        output_dir.mkdir(parents=True, exist_ok=True)

        video_path = video_dir / f"scene_{scene_number:03d}.mp4"
        audio_path = self.get_audio_path(pipeline_id, scene_number)
        output_path = output_dir / f"scene_{scene_number:03d}.mp4"

        if not video_path.exists() or audio_path is None:
            return None

        try:
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(video_path),
                    "-i", str(audio_path),
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-ar", "44100",
                    "-shortest",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
            )
            logger.info("Audio merged for scene %d", scene_number)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error("Audio merge failed for scene %d: %s", scene_number, e.stderr.decode())
            return None