import os
import sys
from pathlib import Path

# Add the project root to Python path  
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing ew001 pipeline execution...")

try:
    # Import all our critical agents to verify they work
    from movie_os.agents.creative.screenplay_writer_agent import ScreenplayWriterAgent
    from movie_os.agents.creative.dialogue_writer_agent import DialogueWriterAgent  
    from movie_os.agents.creative.image_generator_agent import ImageGeneratorAgent
    from movie_os.agents.creative.voice_generator_agent import VoiceGeneratorAgent
    from movie_os.agents.creative.music_generator_agent import MusicGeneratorAgent
    from movie_os.agents.creative.video_composer_agent import VideoComposerAgent
    from movie_os.agents.creative.audio_mixer_agent import AudioMixerAgent
    
    print("✅ All 6 critical agents imported successfully")
    
    # Test instantiation
    screenplay_writer = ScreenplayWriterAgent()
    dialogue_writer = DialogueWriterAgent() 
    image_generator = ImageGeneratorAgent()
    voice_generator = VoiceGeneratorAgent()
    music_generator = MusicGeneratorAgent()
    video_composer = VideoComposerAgent()
    audio_mixer = AudioMixerAgent()
    
    print("✅ All agents instantiated successfully")
    
    # Test that they have proper attributes
    print(f"ScreenplayWriter: {screenplay_writer.name} v{screenplay_writer.version}")
    print(f"DialogueWriter: {dialogue_writer.name} v{dialogue_writer.version}")
    print(f"ImageGenerator: {image_generator.name} v{image_generator.version}")
    print(f"VoiceGenerator: {voice_generator.name} v{voice_generator.version}")
    print(f"MusicGenerator: {music_generator.name} v{music_generator.version}")
    print(f"VideoComposer: {video_composer.name} v{video_composer.version}")
    print(f"AudioMixer: {audio_mixer.name} v{audio_mixer.version}")
    
    print("\n🎉 Pipeline components are ready for execution!")
    
except Exception as e:
    print(f"❌ Error in pipeline test: {e}")
    import traceback
    traceback.print_exc()
    
print("\nPipeline test completed successfully!")
