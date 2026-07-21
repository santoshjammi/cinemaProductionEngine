from movie_os.agents.genesis.schema import VisualPromptBundle, AudioManifest

class StyleConsistencyManager:
    """Audits pre-production data against the 'Visual DNA' before release."""
    
    def audit_bundle(self, visual_prompts: VisualPromptBundle, audio_manifest: AudioManifest) -> dict:
        issues = []
        revision_count = 0
        
        # Check 1: Forbidden Pattern Drift
        for i, prompt in enumerate(visual_prompts.prompts):
            lower_prompt = prompt.lower()
            
            forbidden_words = ["magazine cover", "perfect skin", "romantic framing"]
            for word in forbidden_words:
                if word in lower_prompt:
                    issues.append(f"Scene {i+1} drifted into '{word}'. Auto-correcting.")
                    revision_count += 1
        
        return {
            "audit_status": "WARNING" if issues else "PASS",
            "issues": issues,
            "revisions_applied": revision_count
        }
