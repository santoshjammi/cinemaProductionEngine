#!/usr/bin/env python3
"""EW001 Production Pipeline - Complete Movie OS v1 with ComfyUI/FLUX.1 integration.

Runs the full 26-agent pipeline for the Emotional Withdrawal production (ew001).

Usage:
    python scripts/run_ew001_production.py [--duration 15] [--comfyui http://localhost:8188]
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from movie_os.capabilities.agent_base import ProductionContext, AgentStatus
from movie_os.agents.creative.screenplay_writer_agent import ScreenplayWriterAgent
from movie_os.agents.creative.dialogue_writer_agent import DialogueWriterAgent
from movie_os.agents.creative.image_generator_agent import ImageGeneratorAgent
from movie_os.agents.creative.voice_generator_agent import VoiceGeneratorAgent
from movie_os.agents.creative.music_generator_agent import MusicGeneratorAgent
from movie_os.agents.creative.video_composer_agent import VideoComposerAgent
from movie_os.agents.creative.audio_mixer_agent import AudioMixerAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger("ew001_production")


class EW001ProductionPipeline:
    """Complete production pipeline for Emotional Withdrawal video."""
    
    def __init__(self, duration_minutes: int = 15, comfyui_url: str = "http://localhost:8188"):
        self.duration_minutes = duration_minutes
        self.comfyui_url = comfyui_url
        
        # Production directories
        self.base_dir = Path("output/ew001_production")
        self.screenshots_dir = self.base_dir / "screenshots"
        self.images_dir = self.base_dir / "images"
        self.voiceovers_dir = self.base_dir / "voiceovers"
        self.music_dir = self.base_dir / "music"
        self.videos_dir = self.base_dir / "videos"
        self.output_dir = self.base_dir / "output"
        
        # Scene durations (in seconds) - optimized for 15-20 min video
        self.scene_durations = {
            1: 60,   # Opening: Warm memories
            2: 75,   # First tension
            3: 65,   # Growing distance
            4: 70,   # Misunderstanding
            5: 90,   # Irreversible moment (climax)
            6: 85,   # Aftermath
            7: 70,   # Emotional withdrawal
            8: 65,   # Isolation deepens
            9: 80,   # Moment of clarity
            10: 75,  # Failed connection
            11: 85,  # Acceptance of distance
            12: 70,  # New normal
            13: 90,  # Final scene: Hope
        }
        
    async def run(self) -> Dict[str, Any]:
        """Run the complete production pipeline."""
        logger.info("=" * 80)
        logger.info("EW001 PRODUCTION PIPELINE - MOVIE OS v1")
        logger.info("=" * 80)
        
        # Create production context
        context = ProductionContext(
            title="Emotional Withdrawal",
            dna={"theme": "emotional_withdrawal", "genre": "drama"},
            creative_brief={
                "logline": "A couple's gradual emotional distance leads to quiet devastation.",
                "tone": "naturalistic, intimate, restrained",
                "visual_style": "warm tones fading to cool, close-ups, shallow depth of field",
            },
            production_dir=self.base_dir,
        )
        
        # Set phase as attribute (not constructor param)
        context.phase = "initializing"
        
        # Ensure directories exist
        for d in [self.screenshots_dir, self.images_dir, self.voiceovers_dir, 
                  self.music_dir, self.videos_dir, self.output_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        # Phase 1: Screenplay Generation
        logger.info("\n[Phase 1/8] Generating screenplay...")
        context.phase = "screenplay"
        screenplay_agent = ScreenplayWriterAgent()
        screenplay_result = await screenplay_agent.execute(context)
        results["screenplay"] = screenplay_result
        if screenplay_result.updated_context:
            context = screenplay_result.updated_context
        
        # Phase 2: Dialogue Refinement
        logger.info("\n[Phase 2/8] Refining dialogue...")
        context.phase = "dialogue"
        dialogue_agent = DialogueWriterAgent()
        dialogue_result = await dialogue_agent.execute(context)
        results["dialogue"] = dialogue_result
        if dialogue_result.updated_context:
            context = dialogue_result.updated_context
        
        # Phase 3: Image Generation via ComfyUI/FLUX.1
        logger.info("\n[Phase 3/8] Generating images via ComfyUI/FLUX.1...")
        context.phase = "images"
        
        # Check ComfyUI availability
        from movie_os.llm.comfyui_client import ComfyUIClient, ComfyUIConfig
        config = ComfyUIConfig(
            base_url=self.comfyui_url,
            workspace_root=str(Path(__file__).parent.parent),
        )
        client = ComfyUIClient(config)
        comfyui_available = await client.health_check()
        
        logger.info(f"ComfyUI available: {comfyui_available}")
        if not comfyui_available:
            logger.warning("ComfyUI not running - will use placeholder images")
        
        image_agent = ImageGeneratorAgent(comfyui_url=self.comfyui_url)
        image_result = await image_agent.execute(context)
        results["images"] = image_result
        if image_result.updated_context:
            context = image_result.updated_context
        
        # Phase 4: Voice Generation via Edge TTS
        logger.info("\n[Phase 4/8] Generating voiceovers via Edge TTS...")
        context.phase = "voice"
        voice_agent = VoiceGeneratorAgent()
        voice_result = await voice_agent.execute(context)
        results["voice"] = voice_result
        if voice_result.updated_context:
            context = voice_result.updated_context
        
        # Phase 5: Music Generation via Procedural Composition
        logger.info("\n[Phase 5/8] Generating music via procedural composition...")
        context.phase = "music"
        music_agent = MusicGeneratorAgent()
        music_result = await music_agent.execute(context)
        results["music"] = music_result
        if music_result.updated_context:
            context = music_result.updated_context
        
        # Phase 6: Video Composition via FFmpeg
        logger.info("\n[Phase 6/8] Composing videos via FFmpeg...")
        context.phase = "video"
        video_agent = VideoComposerAgent()
        video_result = await video_agent.execute(context)
        results["video"] = video_result
        if video_result.updated_context:
            context = video_result.updated_context
        
        # Phase 7: Audio Mixing
        logger.info("\n[Phase 7/8] Mixing audio...")
        context.phase = "audio_mix"
        audio_agent = AudioMixerAgent()
        audio_result = await audio_agent.execute(context)
        results["audio_mix"] = audio_result
        if audio_result.updated_context:
            context = audio_result.updated_context
        
        # Phase 8: Evaluation (all 7 agents)
        logger.info("\n[Phase 8/8] Running evaluations...")
        context.phase = "evaluation"
        
        from movie_os.agents.evaluation.story_quality_agent import StoryQualityAgent
        from movie_os.agents.evaluation.dialogue_quality_agent import DialogueQualityAgent
        from movie_os.agents.evaluation.visual_consistency_agent import VisualConsistencyAgent
        from movie_os.agents.evaluation.audio_mix_agent import AudioMixAgent
        from movie_os.agents.evaluation.emotion_score_agent import EmotionScoreAgent
        from movie_os.agents.evaluation.character_consistency_agent import CharacterConsistencyAgent
        from movie_os.agents.evaluation.youtube_readiness_agent import YouTubeReadinessAgent
        
        eval_results = {}
        
        for name, agent_class in [
            ("story_quality", StoryQualityAgent),
            ("dialogue_quality", DialogueQualityAgent),
            ("visual_consistency", VisualConsistencyAgent),
            ("audio_mix", AudioMixAgent),
            ("emotion_score", EmotionScoreAgent),
            ("character_consistency", CharacterConsistencyAgent),
        ]:
            agent = agent_class()
            result = await agent.execute(context)
            eval_results[name] = result
            logger.info(f"  {name}: {result.status.value}")
        
        # YouTube readiness
        youtube_agent = YouTubeReadinessAgent()
        youtube_result = await youtube_agent.execute(context)
        eval_results["youtube_readiness"] = youtube_result
        logger.info(f"  youtube_readiness: {youtube_result.status.value}")
        
        # Final summary
        all_passed = all(
            r.status in [AgentStatus.SUCCESS, AgentStatus.REVISED]
            for r in eval_results.values()
        )
        
        logger.info("\n" + "=" * 80)
        logger.info("PRODUCTION PIPELINE COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Final Status: {'PASSED' if all_passed else 'NEEDS REVISION'}")
        logger.info(f"Images: {image_result.artifacts.get('image_count', 0)} generated")
        logger.info(f"Voiceovers: {len(voice_result.artifacts.get('voice_paths', []))} generated")
        logger.info(f"Music tracks: {len(music_result.artifacts.get('music_paths', []))} generated")
        logger.info(f"Video: {video_result.artifacts.get('video_path', 'N/A')}")
        
        return {
            "status": "passed" if all_passed else "needs_revision",
            "results": {k: v.status.value for k, v in results.items()},
            "evaluations": {k: v.status.value for k, v in eval_results.items()},
        }


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EW001 Production Pipeline")
    parser.add_argument("--duration", type=int, default=15, help="Target duration in minutes")
    parser.add_argument("--comfyui", type=str, default="http://localhost:8188", help="ComfyUI URL")
    args = parser.parse_args()
    
    pipeline = EW001ProductionPipeline(duration_minutes=args.duration, comfyui_url=args.comfyui)
    result = await pipeline.run()
    
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
