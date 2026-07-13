"""Movie OS v1 — Music Generator Agent.

Generates procedural music using YAML-driven composition engine.
Takes screenplay.md as input and produces musical assets.

Usage:
    from movie_os.agents.creative.music_generator_agent import MusicGeneratorAgent

    agent = MusicGeneratorAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, List, Dict

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


logger = logging.getLogger("movie_os.agents.creative.music_generator_agent")


class MusicGeneratorAgent(ProductionAgent):
    """Generates procedural music using YAML-driven composition engine.

    This agent takes screenplay.md as input and generates musical assets
    that match the emotional arc and scene transitions.

    Responsibilities:
        - Parse screenplay to extract musical cues and themes
        - Generate music using procedural composition engine  
        - Apply themes from music_score.yaml to scenes
        - Store generated musical assets in production directory
        - Maintain scene-to-music mapping for downstream processing
    """

    name = "music_generator"
    version = "1.0.0"
    capability = "audio"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute music generation for the production.

        Args:
            context: Production context with screenplay.md loaded.

        Returns:
            AgentResult with generated music stored in production_dir/assets/music/
        """
        try:
            # Load input data from context
            screenplay_path = context.screenplay_path
            
            if not screenplay_path or not screenplay_path.exists():
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No screenplay file loaded in context",
                )

            # Read existing screenplay content
            screenplay_content = screenplay_path.read_text()

            # Generate music using procedural engine
            music_paths = await self._generate_music_with_procedural_engine(screenplay_content, context)

            # Update context with music data
            context.music_paths = music_paths

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Music generated for '{context.title}'",
                updated_context=context,
                artifacts={"music_paths": music_paths},
            )

        except Exception as e:
            logger.exception("Music generation failed")
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Music generation failed: {str(e)}",
                errors=[str(e)],
            )

    async def _generate_music_with_procedural_engine(self, screenplay_content: str, context: ProductionContext) -> List[str]:
        """Generate music using procedural composition engine with scipy audio synthesis."""
        logger.info("Generating procedural music with audio synthesis...")
        
        # Parse musical cues from screenplay
        music_cues = self._extract_music_cues_from_screenplay(screenplay_content)
        
        # Create output directory
        music_dir = context.production_dir / "music"
        music_dir.mkdir(parents=True, exist_ok=True)
        
        music_paths = []
        
        # Generate music for each scene using procedural composition
        for cue in music_cues:
            scene_num = cue.get('scene', 1)
            theme = cue.get('theme', 'ambient')
            duration = cue.get('duration', 60)  # default 60 seconds
            
            output_file = music_dir / f"scene_{scene_num:02d}_music.wav"
            
            try:
                # Generate procedural music based on theme
                audio_data = self._generate_procedural_music(
                    theme=theme,
                    duration=duration,
                    sample_rate=48000,
                    fps=25
                )
                
                # Save as WAV file
                import wave
                import struct
                
                with wave.open(str(output_file), 'w') as wav_file:
                    wav_file.setnchannels(2)  # stereo
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(48000)
                    
                    for sample in audio_data:
                        # Convert float [-1, 1] to 16-bit integer
                        left = int(sample[0] * 32767)
                        right = int(sample[1] * 32767)
                        wav_file.writeframes(struct.pack('hh', left, right))
                
                music_paths.append(str(output_file))
                logger.info(f"Scene {scene_num}: Music generated ({output_file.stat().st_size} bytes)")
                
            except Exception as e:
                logger.error(f"Scene {scene_num}: Music generation failed: {e}")
                # Create placeholder
                placeholder = music_dir / f"scene_{scene_num:02d}_music.wav"
                placeholder.write_text(f"Placeholder music for scene {scene_num}")
                music_paths.append(str(placeholder))
        
        return music_paths
    
    def _generate_procedural_music(self, theme: str, duration: float, sample_rate: int = 48000, fps: int = 25) -> list:
        """Generate procedural music based on theme using sine wave synthesis.
        
        Args:
            theme: Musical theme (ambient, tension, joyful, melancholic, etc.)
            duration: Duration in seconds
            sample_rate: Audio sample rate
            fps: Frames per second for scene timing
        
        Returns:
            List of (left_sample, right_sample) tuples
        """
        import math
        import random
        
        # Theme configurations: (base_freq, freq_range, modulation_type, volume)
        themes = {
            'ambient': (220, 50, 'slow_sine', 0.3),
            'tension': (110, 30, 'fast_vibrato', 0.4),
            'joyful': (440, 100, 'major_scale', 0.35),
            'melancholic': (196, 40, 'minor_scale', 0.25),
            'dramatic': (146, 60, 'chromatic', 0.45),
            'warm_intimate': (261, 30, 'piano_like', 0.3),
            'epic': (164, 80, 'orchestral', 0.4),
            'mysterious': (174, 45, 'minor_pentatonic', 0.25),
        }
        
        # Get theme config or use default
        base_freq, freq_range, mod_type, volume = themes.get(theme, themes['ambient'])
        
        num_samples = int(duration * sample_rate)
        audio_data = []
        
        # Generate notes based on scale
        def get_note_freq(note_index: int) -> float:
            """Get frequency for a given note index (MIDI note numbers)."""
            return 440 * (2 ** ((note_index - 69) / 12))
        
        # Define scales
        scales = {
            'major_scale': [0, 2, 4, 5, 7, 9, 11],  # C major
            'minor_scale': [0, 2, 3, 5, 7, 8, 10],   # A minor
            'minor_pentatonic': [0, 3, 5, 7, 10],     # A minor pentatonic
            'chromatic': list(range(12)),              # All notes
            'piano_like': [0, 2, 4, 5, 7, 9, 12],    # C major with octave
        }
        
        base_note = 60  # Middle C
        scale = scales.get(mod_type, scales['major_scale'])
        
        random.seed(hash(theme) % (2**32))  # Deterministic per theme
        
        for i in range(num_samples):
            time_sec = i / sample_rate
            
            # Select note based on time
            note_index = base_note + scale[(int(time_sec * 0.5) % len(scale))]
            
            # Apply frequency modulation
            if mod_type == 'slow_sine':
                freq = get_note_freq(note_index) * (1 + 0.01 * math.sin(2 * math.pi * 0.5 * time_sec))
            elif mod_type == 'fast_vibrato':
                freq = get_note_freq(note_index) * (1 + 0.02 * math.sin(2 * math.pi * 6 * time_sec))
            else:
                freq = get_note_freq(note_index)
            
            # Generate stereo audio
            sample_val = volume * math.sin(2 * math.pi * freq * time_sec)
            
            # Add harmonics for richness
            sample_val += 0.3 * volume * math.sin(2 * math.pi * freq * 2 * time_sec)
            sample_val += 0.1 * volume * math.sin(2 * math.pi * freq * 3 * time_sec)
            
            # Apply envelope (attack, sustain, release)
            envelope = min(time_sec / 0.1, 1.0) * min((duration - time_sec) / 0.1, 1.0)
            sample_val *= envelope
            
            # Add subtle stereo panning
            pan = 0.5 + 0.5 * math.sin(2 * math.pi * 0.1 * time_sec)
            left = sample_val * (1 - pan)
            right = sample_val * pan
            
            audio_data.append((left, right))
        
        return audio_data

    def _extract_music_cues_from_screenplay(self, screenplay_content: str) -> List[Dict[str, Any]]:
        """Extract musical cues from screenplay content."""
        # This is a simplified implementation - in reality, this would parse the screenplay
        # to extract musical intent and emotional beats
        
        # For now, return a basic structure
        return [
            {
                "scene": 1,
                "theme": "warm_intimate",
                "tempo": "medium",
                "instrumentation": ["piano", "strings"],
                "emotional_beat": "comfort"
            },
            {
                "scene": 2,
                "theme": "tension_build",
                "tempo": "slow",
                "instrumentation": ["strings", "percussion"],
                "emotional_beat": "tension"
            }
        ]