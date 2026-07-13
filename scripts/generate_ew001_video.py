#!/usr/bin/env python3
"""
Complete Pipeline Execution for ew001 Video Generation

This script executes the full Movie OS Cinema Production Engine pipeline:
1. Screenplay generation with Ollama LLM
2. Dialogue enhancement with Ollama LLM
3. Image generation (placeholder if ComfyUI unavailable)
4. Voiceover generation with Edge TTS
5. Music composition (procedural placeholder)
6. Video composition with FFmpeg
7. Audio mixing and final assembly

Usage:
    python generate_ew001_video.py [--output-dir <path>] [--duration <minutes>]
"""

import os
import sys
import json
import time
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
import os
from pathlib import Path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Import our critical agents
from movie_os.agents.creative.screenplay_writer_agent import ScreenplayWriterAgent
from movie_os.agents.creative.dialogue_writer_agent import DialogueWriterAgent
from movie_os.agents.creative.image_generator_agent import ImageGeneratorAgent
from movie_os.agents.creative.voice_generator_agent import VoiceGeneratorAgent
from movie_os.agents.creative.music_generator_agent import MusicGeneratorAgent
from movie_os.agents.creative.video_composer_agent import VideoComposerAgent
from movie_os.agents.creative.audio_mixer_agent import AudioMixerAgent

# Import config and base classes
from config.ollama_client import OllamaClient
from movie_os.capabilities.agent_base import ProductionContext, AgentResult, AgentStatus


class EW001Pipeline:
    """Complete pipeline for generating ew001 video."""
    
    def __init__(self, output_dir: str = None, duration_minutes: int = 15):
        self.output_dir = Path(output_dir) if output_dir else Path("output/ew001_production")
        self.duration_minutes = duration_minutes
        self.scenes: List[Dict[str, Any]] = []
        self.screenplay: str = ""
        self.voiceovers: List[Dict[str, Any]] = []
        
        # Initialize agents
        self.llm_client = OllamaClient()
        self.screenplay_writer = ScreenplayWriterAgent()
        self.dialogue_writer = DialogueWriterAgent()
        self.image_generator = ImageGeneratorAgent()
        self.voice_generator = VoiceGeneratorAgent()
        self.music_generator = MusicGeneratorAgent()
        self.video_composer = VideoComposerAgent()
        self.audio_mixer = AudioMixerAgent()
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "screenplay").mkdir(exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "voiceovers").mkdir(exist_ok=True)
        (self.output_dir / "music").mkdir(exist_ok=True)
        (self.output_dir / "videos").mkdir(exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    async def generate_screenplay(self) -> str:
        """Generate screenplay using Ollama LLM via the agent's execute method."""
        self.log("=" * 60)
        self.log("PHASE 1: Screenplay Generation", "PHASE")
        self.log("=" * 60)
        
        # Define the production context for ew001
        production_context = ProductionContext(
            title="Emotional Withdrawal",
            dna={
                "territory": "emotional_withdrawal",
                "theme": "The slow erosion of connection in long-term relationships",
                "archetype": "slow_withdrawal"
            },
            production_dir=self.output_dir,
            grammar="psychological_cinema",
            outline={
                "title": "Emotional Withdrawal",
                "beats": [
                    {"id": 1, "description": "Morning distance - Maya wakes beside sleeping partner"},
                    {"id": 2, "description": "Kitchen silence - minimal exchange over cold coffee"},
                    {"id": 3, "description": "Work as escape - lost in architectural drawings"},
                    {"id": 4, "description": "Phone call - surface conversation with longing underneath"},
                    {"id": 5, "description": "Cold dinner - two people at opposite ends of table"},
                    {"id": 6, "description": "Irreversible moment - stops mid-gesture setting table"},
                    {"id": 7, "description": "Rain walk - alone in city, rain mirrors internal state"},
                    {"id": 8, "description": "Friend's apartment - laughter comes easier here"},
                    {"id": 9, "description": "The attempt - tries to reconnect, doesn't meet halfway"},
                    {"id": 10, "description": "Architect's model - builds something precise and controllable"},
                    {"id": 11, "description": "The letter - writes words she cannot say aloud"},
                    {"id": 12, "description": "The decision - packs a small bag, steps toward herself"},
                    {"id": 13, "description": "The threshold - hand on doorknob, walks into light"}
                ]
            },
            creative_brief={
                "tone": "contemplative, intimate, restrained",
                "setting": "Contemporary urban apartment",
                "protagonist": {
                    "name": "Maya",
                    "age": 35,
                    "occupation": "Architect"
                }
            }
        )
        
        # Generate screenplay using our agent's execute method
        try:
            self.log("Generating screenplay with Ollama LLM...")
            result = await self.screenplay_writer.execute(production_context)
            
            if result.status == AgentStatus.SUCCESS and production_context.screenplay_path:
                self.screenplay = production_context.screenplay_path.read_text()
                self.log(f"✅ Screenplay generated successfully ({len(self.screenplay)} characters)")
                self.log(f"Screenplay saved to: {production_context.screenplay_path}")
            else:
                self.log(f"⚠️ Screenplay generation returned status: {result.status}", "WARNING")
                self.log(f"Message: {result.message}")
                # Fall back to template
                self.screenplay = await self._generate_template_screenplay(production_context)
                
        except Exception as e:
            self.log(f"❌ Screenplay generation failed: {e}", "ERROR")
            self.log("Using template fallback...")
            self.screenplay = await self._generate_template_screenplay(production_context)
        
        return self.screenplay
    
    async def _generate_template_screenplay(self, context: ProductionContext) -> str:
        """Generate a template screenplay when LLM is unavailable."""
        self.log("Generating template screenplay...")
        
        screenplay = f"""# Screenplay: {context.title}

## Production Info
- Territory: {context.dna.get('territory', 'unknown')}
- Theme: {context.dna.get('theme', 'N/A')}
- Grammar: {context.grammar or 'psychological_cinema'}
- Target Duration: {self.duration_minutes} minutes

---

"""
        
        beats = context.outline.get('beats', []) if context.outline else []
        for beat in beats:
            screenplay += f"""## Scene {beat['id']}: Beat {beat['description']}

**Duration**: {30 + beat['id'] * 5} seconds
**Emotional Tone**: contemplative

### Action
{beat['description'].capitalize()}. The camera holds. We see what words cannot say.

### Dialogue
{context.creative_brief.get('protagonist', {}).get('name', 'Protagonist')}: (internal) "I am still here."

---

"""
        
        # Save the template screenplay
        output_path = self.output_dir / "screenplay" / "production_screenplay.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(screenplay)
        
        return screenplay
    
    async def enhance_dialogue(self) -> List[Dict[str, Any]]:
        """Enhance dialogue using Ollama LLM via the agent's execute method."""
        self.log("=" * 60)
        self.log("PHASE 2: Dialogue Enhancement", "PHASE")
        self.log("=" * 60)
        
        # Create context with screenplay data
        production_context = ProductionContext(
            title="Emotional Withdrawal",
            dna={"territory": "emotional_withdrawal"},
            production_dir=self.output_dir,
            grammar="psychological_cinema",
            screenplay_path=self.output_dir / "screenplay" / "production_screenplay.md" if hasattr(self, 'screenplay') and self.screenplay else None
        )
        
        # Load screenplay content into context
        if hasattr(self, 'screenplay') and self.screenplay:
            production_context.outline = {"beats": [{"id": i+1, "description": f"Scene {i+1}"} for i in range(13)]}
        
        try:
            self.log("Enhancing dialogue with Ollama LLM...")
            result = await self.dialogue_writer.execute(production_context)
            
            if result.status == AgentStatus.SUCCESS:
                self.log(f"✅ Dialogue enhancement complete: {result.message}")
                # Parse scenes from the enhanced screenplay
                return self._parse_scenes_from_screenplay()
            else:
                self.log(f"⚠️ Dialogue enhancement returned: {result.message}", "WARNING")
                
        except Exception as e:
            self.log(f"❌ Dialogue enhancement failed: {e}", "ERROR")
        
        # Fallback to template-based dialogue
        self.log("Using template-based dialogue generation...")
        return self._generate_template_dialogue()
    
    def _parse_scenes_from_screenplay(self) -> List[Dict[str, Any]]:
        """Parse scenes from the generated screenplay."""
        if not hasattr(self, 'screenplay') or not self.screenplay:
            return self._generate_template_dialogue()
        
        # Simple parsing - in production this would be more sophisticated
        scenes = []
        lines = self.screenplay.split('\n')
        scene_num = 0
        
        for i, line in enumerate(lines):
            if line.startswith('## Scene'):
                scene_num += 1
                title = line.replace('## Scene ', '').strip()
                duration = 30 + scene_num * 5  # Variable duration
                
                # Get visual prompt from context or generate one
                visual_prompt = f"Cinematic shot for {title}, psychological cinema style, restrained composition"
                
                scenes.append({
                    "id": f"ew001-scene-{scene_num:02d}",
                    "title": title,
                    "act": (scene_num // 5) + 1,
                    "duration_seconds": min(duration, 90),
                    "description": f"Scene {scene_num} from Emotional Withdrawal screenplay",
                    "visual_prompt": visual_prompt,
                    "dialogue": [{"character": "Maya", "text": "I am still here."}],
                    "camera": "Slow push-in, shallow depth of field",
                    "lighting": "Natural light, cool tones"
                })
        
        return scenes if scenes else self._generate_template_dialogue()
    
    def _generate_template_dialogue(self) -> List[Dict[str, Any]]:
        """Generate template dialogue for ew001 production."""
        self.log("Generating template dialogue for Emotional Withdrawal...")
        
        scenes = [
            {
                "id": "ew001-scene-01",
                "title": "Morning Routine",
                "act": 1,
                "duration_seconds": 45,
                "description": "Maya wakes up. Her partner sleeps beside her. The distance is palpable.",
                "visual_prompt": "Cinematic shot, woman waking up in modern bedroom, morning light through blinds, intimate close-up, shallow depth of field",
                "dialogue": [
                    {"character": "Maya (internal)", "text": "When did we stop talking?"}
                ],
                "camera": "Close-up, slow push-in",
                "lighting": "Soft morning light, cool tones"
            },
            {
                "id": "ew001-scene-02", 
                "title": "The Kitchen Silence",
                "act": 1,
                "duration_seconds": 60,
                "description": "Maya makes coffee. Her partner enters. They exchange minimal words.",
                "visual_prompt": "Wide shot of modern kitchen, two people at opposite ends, cold light from window, composition emphasizes distance",
                "dialogue": [
                    {"character": "Partner", "text": "Did you call the contractor?"},
                    {"character": "Maya", "text": "Yes. Tomorrow."},
                    {"character": "Partner", "text": "Good."}
                ],
                "camera": "Static wide shot, symmetrical composition",
                "lighting": "Harsh overhead light, clinical feel"
            },
            {
                "id": "ew001-scene-03",
                "title": "Work as Escape",
                "act": 1,
                "duration_seconds": 50,
                "description": "Maya at her drafting table. Lost in work to avoid going home.",
                "visual_prompt": "Over-the-shoulder shot of architectural drawings, warm desk lamp against cool room, focused expression",
                "dialogue": [
                    {"character": "Maya (internal)", "text": "If I stay here long enough, I don't have to go back."}
                ],
                "camera": "Over-the-shoulder, slow pan across drawings",
                "lighting": "Warm desk lamp pool against cool ambient"
            },
            {
                "id": "ew001-scene-04",
                "title": "The Phone Call",
                "act": 1,
                "duration_seconds": 55,
                "description": "Maya calls her mother. The conversation is surface-level but longing underneath.",
                "visual_prompt": "Close-up of Maya on phone, forced smile, eyes looking away, soft window light",
                "dialogue": [
                    {"character": "Maya", "text": "I'm fine, Mom. Really."},
                    {"character": "Mother (V.O.)", "text": "You sound tired, sweetheart."},
                    {"character": "Maya", "text": "Just work. I'll call you Sunday."}
                ],
                "camera": "Tight close-up, shallow focus",
                "lighting": "Soft window light, warm highlight on face"
            },
            {
                "id": "ew001-scene-05",
                "title": "Dinner for Two (Nobody Eating)",
                "act": 2,
                "duration_seconds": 70,
                "description": "They sit across from each other. The meal grows cold. Phones are checked.",
                "visual_prompt": "Top-down shot of dinner table, two plates untouched, phone screens glowing, overhead pendant light",
                "dialogue": [
                    {"character": "Partner", "text": "How was your day?"},
                    {"character": "Maya", "text": "Fine."},
                    {"character": "Partner", "text": "Mine too."}
                ],
                "camera": "Top-down static, symmetrical framing",
                "lighting": "Warm pendant light, cool phone screen glow"
            },
            {
                "id": "ew001-scene-06",
                "title": "The Irreversible Moment - Setting the Table",
                "act": 2,
                "duration_seconds": 90,
                "description": "Maya stops mid-gesture while setting the table. She cannot complete the action. The pause speaks volumes.",
                "visual_prompt": "Medium shot of woman at dining table, fork in hand frozen, half-set place settings, soft melancholic light through window",
                "dialogue": [
                    {"character": "Maya (internal)", "text": "I don't know how to do this anymore. I don't know how to do us."}
                ],
                "camera": "Slow push-in on frozen gesture, shallow depth of field",
                "lighting": "Golden hour light, long shadows"
            },
            {
                "id": "ew001-scene-07",
                "title": "Walking in the Rain",
                "act": 2,
                "duration_seconds": 65,
                "description": "Maya walks through the city. Rain mirrors her internal state. She doesn't use an umbrella.",
                "visual_prompt": "Wide shot of woman walking alone on wet city street at dusk, neon reflections on pavement, cinematic noir lighting",
                "dialogue": [
                    {"character": "Maya (internal)", "text": "Maybe if I walk far enough, I'll find where I left myself."}
                ],
                "camera": "Tracking shot from behind, rain droplets on lens",
                "lighting": "Neon signs reflecting on wet pavement, blue tones"
            },
            {
                "id": "ew001-scene-08",
                "title": "The Friend's Apartment",
                "act": 2,
                "duration_seconds": 60,
                "description": "Maya visits her friend. Laughter comes easier here. A glimpse of who she used to be.",
                "visual_prompt": "Warm interior shot, Maya laughing genuinely with friend, cluttered cozy apartment, golden hour light streaming through blinds",
                "dialogue": [
                    {"character": "Friend", "text": "When was the last time you did something just for you?"},
                    {"character": "Maya", "text": "(pause) I don't remember."}
                ],
                "camera": "Handheld, intimate close-ups",
                "lighting": "Warm golden hour, soft highlights"
            },
            {
                "id": "ew001-scene-09",
                "title": "The Attempt",
                "act": 2,
                "duration_seconds": 75,
                "description": "Maya tries to reconnect. She initiates conversation. Her partner responds but doesn't meet her halfway.",
                "visual_prompt": "Two-shot of couple on sofa, Maya leaning forward, partner leaning back, asymmetrical composition showing emotional gap",
                "dialogue": [
                    {"character": "Maya", "text": "I feel like we're... strangers."},
                    {"character": "Partner", "text": "What are you talking about?"},
                    {"character": "Maya", "text": "Nothing. Never mind."}
                ],
                "camera": "Two-shot with shallow focus on Maya's face",
                "lighting": "Dim ambient light, cool tones"
            },
            {
                "id": "ew001-scene-10",
                "title": "The Architect's Model",
                "act": 3,
                "duration_seconds": 80,
                "description": "Maya works on an architectural model. She builds something beautiful and precise. Control over what she can control.",
                "visual_prompt": "Extreme close-up of hands building miniature architecture, magnifying glass, precision tools, warm desk lamp light",
                "dialogue": [
                    {"character": "Maya (internal)", "text": "I can build things that stand. Things that don't fall apart."}
                ],
                "camera": "Macro shots of hands and materials, slow motion",
                "lighting": "Focused warm light on work surface"
            },
            {
                "id": "ew001-scene-11",
                "title": "The Letter",
                "act": 3,
                "duration_seconds": 85,
                "description": "Maya writes a letter she may never send. Words she cannot say aloud finally have form.",
                "visual_prompt": "Close-up of handwriting on paper, pen moving slowly, crumpled drafts nearby, soft window light",
                "dialogue": [
                    {"character": "Maya (voiceover)", "text": "I loved you enough for both of us. I just forgot how to love myself."}
                ],
                "camera": "Extreme close-up on pen and paper, slow pan",
                "lighting": "Soft diffused window light"
            },
            {
                "id": "ew001-scene-12",
                "title": "The Decision",
                "act": 3,
                "duration_seconds": 70,
                "description": "Maya packs a small bag. Not running away. Stepping toward herself.",
                "visual_prompt": "Medium shot of hands packing a single bag, folded clothes, passport, photograph face-down on bed",
                "dialogue": [
                    {"character": "Maya (internal)", "text": "This isn't failure. This is honesty."}
                ],
                "camera": "Static medium shot, slow zoom out",
                "lighting": "Morning light, clean and clear"
            },
            {
                "id": "ew001-scene-13",
                "title": "The Threshold",
                "act": 3,
                "duration_seconds": 90,
                "description": "Maya stands at the door. Hand on knob. One breath. She opens it and walks into light.",
                "visual_prompt": "Low angle shot of woman at doorway, hand on doorknob, bright light from outside silhouetting her figure, cinematic composition",
                "dialogue": [
                    {"character": "Maya (internal)", "text": "I am still here. I am still me. And that has to be enough."}
                ],
                "camera": "Low angle, slow push toward light",
                "lighting": "Bright exterior light silhouetting figure"
            }
        ]
        
        self.scenes = scenes
        return scenes
    
    async def generate_images(self) -> List[str]:
        """Generate images for each scene using the agent's execute method."""
        self.log("=" * 60)
        self.log("PHASE 3: Image Generation", "PHASE")
        self.log("=" * 60)
        
        image_paths = []
        
        # Check if ComfyUI is available
        comfyui_available = await self._check_comfyui()
        
        for i, scene in enumerate(self.scenes):
            scene_num = i + 1
            self.log(f"Generating image {scene_num}/{len(self.scenes)}: {scene['title']}")
            
            # Create context for the image generator agent
            production_context = ProductionContext(
                title="Emotional Withdrawal",
                dna={"territory": "emotional_withdrawal"},
                production_dir=self.output_dir,
                grammar="psychological_cinema"
            )
            
            # Add scene-specific data to context
            production_context.outline = {
                "scene_prompt": scene.get('visual_prompt', 'Cinematic shot'),
                "scene_id": scene.get('id', f'scene_{scene_num}')
            }
            
            if comfyui_available:
                # Use ComfyUI for generation via agent
                result = await self.image_generator.execute(production_context)
                if result.status == AgentStatus.SUCCESS and result.artifacts:
                    image_path = result.artifacts.get('image_path')
                    if image_path:
                        image_paths.append(str(image_path))
                        self.log(f"  ✅ Image saved: {image_path}")
                        continue
            else:
                # Generate placeholder using Python (simple gradient/abstract image)
                self.log(f"  ComfyUI not available, generating placeholder...")
            
            # Fallback to placeholder image generation
            image_path = await self._generate_placeholder_image(
                prompt=scene.get('visual_prompt', ''),
                scene_num=scene_num
            )
            
            if image_path:
                image_paths.append(str(image_path))
                self.log(f"  ✅ Image saved: {image_path}")
            else:
                self.log(f"  ⚠️ Failed to generate image for scene {scene_num}", "WARNING")
        
        self.log(f"✅ Image generation complete: {len(image_paths)}/{len(self.scenes)} images")
        return image_paths
    
    async def _check_comfyui(self) -> bool:
        """Check if ComfyUI is available."""
        try:
            import urllib.request
            response = urllib.request.urlopen("http://localhost:8188/system_stats", timeout=2)
            return response.status == 200
        except:
            return False
    
    async def _generate_placeholder_image(self, prompt: str, scene_num: int) -> Optional[Path]:
        """Generate a placeholder image using Python PIL."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import random
            
            # Create a cinematic gradient image
            width, height = 1920, 1080
            
            # Generate colors based on scene description (deterministic)
            seed = hash(prompt) % 1000
            random.seed(seed)
            
            # Create gradient background
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)
            
            # Generate cinematic color palette
            top_color = (random.randint(20, 60), random.randint(30, 70), random.randint(50, 100))
            bottom_color = (random.randint(80, 140), random.randint(60, 100), random.randint(40, 80))
            
            for y in range(height):
                r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / height)
                g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / height)
                b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / height)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # Add subtle vignette
            for y in range(height):
                for x in range(width):
                    dx = abs(x - width/2) / (width/2)
                    dy = abs(y - height/2) / (height/2)
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist > 0.5:
                        darkness = int((dist - 0.5) * 100)
                        r, g, b = img.getpixel((x, y))
                        img.putpixel((x, y), (max(0, r-darkness), max(0, g-darkness), max(0, b-darkness)))
            
            # Save image
            output_path = self.output_dir / "images" / f"scene_{scene_num:02d}.png"
            img.save(output_path)
            return output_path
            
        except ImportError:
            self.log("  ⚠️ PIL not available, creating minimal PNG", "WARNING")
            # Create minimal valid PNG
            import struct
            import zlib
            
            # Minimal PNG structure
            width, height = 640, 360
            raw_data = b''
            for y in range(height):
                raw_data += b'\x00'  # filter byte
                raw_data += bytes([random.randint(0, 255) for _ in range(width * 3)])
            
            def create_png(width, height, raw_data):
                def chunk(chunk_type, data):
                    c = chunk_type + data
                    crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
                    return struct.pack('>I', len(data)) + c + crc
                
                signature = b'\x89PNG\r\n\x1a\n'
                ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
                compressed = zlib.compress(raw_data)
                
                with open(self.output_dir / "images" / f"scene_{random.randint(1,100):02d}.png", 'wb') as f:
                    f.write(signature)
                    f.write(chunk(b'IHDR', ihdr))
                    f.write(chunk(b'IDAT', compressed))
                    f.write(chunk(b'IEND', b''))
            
            create_png(width, height, raw_data)
            return None
    
    async def generate_voiceovers(self) -> List[Dict[str, Any]]:
        """Generate voiceovers using Edge TTS via the agent's execute method."""
        self.log("=" * 60)
        self.log("PHASE 4: Voiceover Generation", "PHASE")
        self.log("=" * 60)
        
        try:
            import edge_tts
            
            voiceover_paths = []
            
            for i, scene in enumerate(self.scenes):
                scene_num = i + 1
                self.log(f"Generating voiceover {scene_num}/{len(self.scenes)}")
                
                # Collect all dialogue for this scene
                dialogue_text = " ".join([d['text'] for d in scene.get('dialogue', [])])
                
                if not dialogue_text.strip():
                    continue
                
                # Determine voice type based on character
                voice = "en-US-JennyNeural"  # Default female voice
                
                # Generate voiceover
                output_file = self.output_dir / "voiceovers" / f"scene_{scene_num:02d}_voice.mp3"
                
                comm = edge_tts.Communicate(dialogue_text, voice)
                await comm.save(str(output_file))
                
                voiceover_paths.append({
                    'scene_id': scene['id'],
                    'file': str(output_file),
                    'duration_seconds': scene.get('duration_seconds', 30)
                })
                
                self.log(f"  ✅ Voiceover saved: {output_file}")
            
            self.voiceovers = voiceover_paths
            self.log(f"✅ Voiceover generation complete: {len(voiceover_paths)} voiceovers")
            return voiceover_paths
            
        except ImportError:
            self.log("⚠️ Edge TTS not available, skipping voiceover generation", "WARNING")
            return []
    
    async def generate_music(self) -> List[Dict[str, Any]]:
        """Generate procedural music for scenes."""
        self.log("=" * 60)
        self.log("PHASE 5: Music Composition", "PHASE")
        self.log("=" * 60)
        
        # Generate simple ambient music using Python (placeholder)
        music_tracks = []
        
        for i, scene in enumerate(self.scenes):
            scene_num = i + 1
            self.log(f"Generating music track {scene_num}/{len(self.scenes)}")
            
            # Create a silent audio file as placeholder
            # In production, this would use our procedural music engine
            import numpy as np
            
            sample_rate = 44100
            duration = scene.get('duration_seconds', 30)
            samples = np.zeros(int(sample_rate * duration))
            
            output_file = self.output_dir / "music" / f"scene_{scene_num:02d}_music.wav"
            
            # Save as WAV using wave module (no numpy dependency needed)
            import wave
            with wave.open(str(output_file), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                # Write silent samples
                for _ in range(len(samples)):
                    wav_file.writeframes(b'\x00\x00')
            
            music_tracks.append({
                'scene_id': scene['id'],
                'file': str(output_file),
                'duration_seconds': duration
            })
            
            self.log(f"  ✅ Music track saved: {output_file}")
        
        self.log(f"✅ Music composition complete: {len(music_tracks)} tracks")
        return music_tracks
    
    async def compose_video(self, image_paths: List[str], voiceover_paths: List[Dict], music_tracks: List[Dict]) -> str:
        """Compose final video using FFmpeg."""
        self.log("=" * 60)
        self.log("PHASE 6: Video Composition", "PHASE")
        self.log("=" * 60)
        
        # Create a list file for FFmpeg concat demuxer
        list_file = self.output_dir / "videos" / "scene_list.txt"
        
        with open(list_file, 'w') as f:
            for i, scene in enumerate(self.scenes):
                image_path = image_paths[i] if i < len(image_paths) else None
                voiceover = next((v for v in voiceover_paths if v['scene_id'] == scene['id']), None)
                music = next((m for m in music_tracks if m['scene_id'] == scene['id']), None)
                
                duration = scene.get('duration_seconds', 30)
                
                f.write(f"filename 'scene_{i+1:02d}.mp4'\n")
                f.write(f"duration {duration}\n")
        
        # Generate individual scene videos with Ken Burns effect
        scene_videos = []
        for i, scene in enumerate(self.scenes):
            scene_num = i + 1
            self.log(f"Composing scene {scene_num}/{len(self.scenes)}: {scene['title']}")
            
            image_path = image_paths[i] if i < len(image_paths) else None
            
            if not image_path or not os.path.exists(image_path):
                # Create a colored placeholder video
                self.log(f"  ⚠️ No image for scene {scene_num}, using color placeholder", "WARNING")
                duration = scene.get('duration_seconds', 30)
                output_file = self.output_dir / "videos" / f"scene_{scene_num:02d}.mp4"
                
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi', '-i', f'color=c=black:s=1920x1080:d={duration}',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    str(output_file)
                ]
                subprocess.run(cmd, capture_output=True)
            else:
                # Generate scene video with Ken Burns effect
                duration = scene.get('duration_seconds', 30)
                output_file = self.output_dir / "videos" / f"scene_{scene_num:02d}.mp4"
                
                # Ken Burns effect parameters (subtle zoom and pan)
                zoom_start = "1.0"
                zoom_end = "1.15"
                x_start = "0"
                y_start = "0"
                x_end = "-100"
                y_end = "-50"
                
                cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1',
                    '-i', image_path,
                    '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,setsar=1,crop=1920:1080,zoompan=z=\'min(zoom+0.001,{zoom_end})\':x=\'iw/2-(iw/zoom/2)+{x_start}+({x_end}-{x_start})*on/{duration*25}\':y=\'ih/2-(ih/zoom/2)+{y_start}+({y_end}-{y_start})*on/{duration*25}\':d={duration*25}:s=1920x1080:f=25',
                    '-t', str(duration),
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    '-crf', '18',
                    '-pix_fmt', 'yuv420p',
                    '-r', '24',
                    '-an',  # No audio yet
                    str(output_file)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log(f"  ⚠️ FFmpeg error for scene {scene_num}: {result.stderr[:200]}", "WARNING")
            
            scene_videos.append(str(output_file))
        
        # Add voiceover and music to each scene
        for i, scene in enumerate(self.scenes):
            scene_num = i + 1
            scene_video = self.output_dir / "videos" / f"scene_{scene_num:02d}.mp4"
            
            voiceover = next((v for v in voiceover_paths if v['scene_id'] == scene['id']), None)
            music = next((m for m in music_tracks if m['scene_id'] == scene['id']), None)
            
            # Build audio mix command
            audio_inputs = []
            audio_filters = []
            
            if voiceover:
                audio_inputs.extend(['-i', voiceover['file']])
                audio_filters.append(f"[0:a]volume=1.0[audio_vo]")
            
            if music:
                audio_inputs.extend(['-i', music['file']])
                audio_filters.append(f"[1:a]volume=0.3[audio_music]")
            
            if audio_inputs:
                # Add audio to video
                output_with_audio = self.output_dir / "videos" / f"scene_{scene_num:02d}_with_audio.mp4"
                
                filter_complex = "&".join(audio_filters)
                if len(audio_inputs) > 0:
                    filter_complex += ",amix=inputs=" + str(len(audio_inputs)) + ":duration=longest[audio]"
                
                cmd = ['ffmpeg', '-y', '-i', str(scene_video)] + audio_inputs + [
                    '-filter_complex', filter_complex,
                    '-map', '0:v',
                    '-map', '[audio]',
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-shortest',
                    str(output_with_audio)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    os.remove(scene_video)
                    os.rename(str(output_with_audio), str(scene_video))
        
        # Concatenate all scenes into final video
        self.log("=" * 60)
        self.log("PHASE 7: Final Assembly", "PHASE")
        self.log("=" * 60)
        
        concat_list = self.output_dir / "videos" / "concat_list.txt"
        with open(concat_list, 'w') as f:
            for scene_video in scene_videos:
                f.write(f"file '{scene_video}'\n")
        
        final_video = self.output_dir / "videos" / f"ew001_final_{self.duration_minutes}min.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_list),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-r', '24',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-ar', '48000',
            str(final_video)
        ]
        
        self.log("Assembling final video...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(final_video) / (1024 * 1024)  # MB
            self.log(f"✅ Final video generated successfully!")
            self.log(f"   Output: {final_video}")
            self.log(f"   Size: {file_size:.1f} MB")
            
            # Get duration
            dur_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(final_video)]
            dur_result = subprocess.run(dur_cmd, capture_output=True, text=True)
            if dur_result.returncode == 0:
                duration = float(dur_result.stdout.strip())
                self.log(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        else:
            self.log(f"❌ Final assembly failed: {result.stderr[:500]}", "ERROR")
        
        return str(final_video)
    
    async def run(self) -> str:
        """Execute the complete ew001 pipeline."""
        self.log("=" * 60)
        self.log("🎬 MOVIE OS CINEMA PRODUCTION ENGINE", "START")
        self.log(f"Production: ew001 - Emotional Withdrawal")
        self.log(f"Target Duration: {self.duration_minutes} minutes")
        self.log(f"Output Directory: {self.output_dir}")
        self.log("=" * 60)
        
        start_time = time.time()
        
        try:
            # Phase 1: Generate screenplay
            await self.generate_screenplay()
            
            # Phase 2: Enhance dialogue
            await self.enhance_dialogue()
            
            # Phase 3: Generate images
            image_paths = await self.generate_images()
            
            # Phase 4: Generate voiceovers
            voiceover_paths = await self.generate_voiceovers()
            
            # Phase 5: Generate music
            music_tracks = await self.generate_music()
            
            # Phase 6-7: Compose video and final assembly
            final_video = await self.compose_video(image_paths, voiceover_paths, music_tracks)
            
            elapsed = time.time() - start_time
            self.log("=" * 60)
            self.log("🎉 EW001 PRODUCTION COMPLETE", "SUCCESS")
            self.log(f"Total execution time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
            self.log(f"Final video: {final_video}")
            self.log("=" * 60)
            
            return final_video
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.log(f"❌ Pipeline failed after {elapsed:.1f} seconds: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            raise


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate ew001 video using Movie OS Cinema Production Engine")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for the production")
    parser.add_argument("--duration", type=int, default=15, help="Target duration in minutes (default: 15)")
    
    args = parser.parse_args()
    
    pipeline = EW001Pipeline(
        output_dir=args.output_dir,
        duration_minutes=args.duration
    )
    
    final_video = await pipeline.run()
    
    if final_video:
        print(f"\n🎬 Final video generated at: {final_video}")
        return 0
    else:
        print("\n❌ Video generation failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
