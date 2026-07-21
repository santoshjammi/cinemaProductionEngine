"""
Genesis Orchestration: Coordinates the entire creative pipeline from synopsis to production assets.
"""
import sys, os

sys.path.insert(0, '/Users/santosh/Desktop/projects/videoGen/movie_os/agents/genesis')

from storyteller import StorytellerAgent
from audio_director import AudioDirectorAgent
from prompt_engineer import PromptEngineerAgent
from style_consistency_manager import StyleConsistencyManager
from schema import GenesisOutput, ScreenplayOutput

class GenesisOrchestrator:
    """Runs the full pre-production pipeline."""
    
    def __init__(self):
        self.storyteller = StorytellerAgent()
        self.audio_director = AudioDirectorAgent()
        self.prompt_engineer = PromptEngineerAgent()
        self.style_guard = StyleConsistencyManager()

    def run(self, synopsis: str) -> GenesisOutput:
        print(f"[Genesis] Processing input: {synopsis}")
        
        # 1. Narrative DNA & Screenplay Generation (The Creative Layer)
        dna = self.storyteller.extract_dna(synopsis)
        screenplay = self.storyteller.generate_screenplay(dna, synopsis)
        
        # 2. Audio Director (Sonic & Vocal Architecture)
        audio_manifest = self.audio_director.generate_manifest(dna, screenplay)
        
        # 3. Prompt Engineer (Visual Compilation)
        visual_prompts = self.prompt_engineer.compile_prompts(screenplay)
        
        # 4. Style Consistency Manager (The Gatekeeper)
        audit_result = self.style_guard.audit_bundle(visual_prompts, audio_manifest)
        print(f"[Genesis] Audit Status: {audit_result['audit_status']} ({audit_result['revisions_applied']} revisions applied)\n")
        
        return GenesisOutput(
            dna=dna,
            screenplay=screenplay,
            audio_manifest=audio_manifest,
            visual_prompts=visual_prompts,
            audit_status=audit_result['audit_status']
        )

    def run_solo(self, synopsis: str) -> ScreenplayOutput:
        """Quick-run method for just getting the screenplay without full pipeline overhead."""
        dna = self.storyteller.extract_dna(synopsis)
        return self.storyteller.generate_screenplay(dna, synopsis)
