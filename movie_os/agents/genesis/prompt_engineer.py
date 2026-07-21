from movie_os.agents.genesis.schema import VisualPromptBundle, SceneBlueprint

class PromptEngineerAgent:
    """Translates semantic tokens into full cinematic prompts for ComfyUI/Flux."""
    
    def compile_prompts(self, beats: list[SceneBlueprint]) -> VisualPromptBundle:
        bundle = VisualPromptBundle()
        
        anchors = [
            "cinematic photorealism", 
            "35mm film grain", 
            "shallow depth of field",
            "cool blue undertones in every scene",
            "warm amber only from practical light sources"
        ]
        
        for beat in beats:
            # Handle both Enum and string states
            emotion = beat.emotional_state.value if hasattr(beat.emotional_state, 'value') else beat.emotional_state
            
            core_tokens = [
                f"{emotion} expression",
                beat.visual_symbolism,
                f"camera: {beat.camera_movement}"
            ]
            
            full_prompt = ", ".join(core_tokens) + ", " + ", ".join(anchors)
            bundle.prompts.append(full_prompt)

        return bundle
