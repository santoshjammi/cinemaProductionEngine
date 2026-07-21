from movie_os.agents.genesis.schema import AudioManifest, SceneBlueprint

class AudioDirectorAgent:
    """Assigns acoustic zones and prosody registers based on Story DNA."""
    
    def generate_manifest(self, dna, beats) -> AudioManifest:
        manifest = AudioManifest()
        
        # 1. Global Soundtrack Zones (3-Zone Architecture)
        manifest.soundtrack_zones = {
            "act_1": "ambient_piano", # Warmth + sub-drone
            "act_2": "dark_drone",    # Unease + dissonance
            "act_3": "near_silence"   # Devastating quiet
        }

        # 2. Per-Scene Prosody Overrides (Voice Modulation Engine)
        for beat in beats:
            state = beat.emotional_state
            # Default baseline
            manifest.prosody_override[beat.scene_number] = {
                "rate": "-15%", 
                "volume": "-10%", 
                "pitch": "-5Hz"
            }

            # Specific overrides based on emotional intensity
            if state in ["defensive", "grief"]:
                manifest.prosody_override[beat.scene_number]["rate"] = "-25%"
                manifest.prosody_override[beat.scene_number]["volume"] = "-18%"
            elif state in ["numb", "resigned"]:
                manifest.prosody_override[beat.scene_number]["rate"] = "-30%" # Heavier pauses
            
        # 3. SFX Layers (Layered Ambience)
        for beat in beats:
            cue = {
                "scene": beat.scene_number,
                "layers": [
                    "room_tone_low_pass",
                    f"{beat.visual_symbolism.split(',')[0].replace(' ', '_')}_sfx" # Dynamic layering
                ]
            }
            if beat.scene_number == 8: # Irreversible moment
                cue["layers"].append("breath_forward_ambient")
            manifest.scene_audio_cues.append(cue)

        return manifest
