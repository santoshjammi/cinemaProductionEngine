"""
Data models and validation logic for Text Cinema Engine
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

# --- Enums ---

class Platform(Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    OTHER = "other"

class EmotionalTone(Enum):
    JOYFUL = "joyful"
    SAD = "sad"
    TENSE = "tense"
    WONDER = "wonder"
    FEAR = "fear"
    ANGER = "anger"
    CALM = "calm"

# --- Input Models ---

@dataclass
class InputConfig:
    """Handles input validation and storage as per PRD"""
    # Required inputs
    topic: str
    emotional_tone: EmotionalTone
    story_length: str  # 'short', 'medium', 'long'
    platform: Platform
    
    # Optional inputs
    character_constraints: Optional[str] = None
    setting: Optional[str] = None
    pacing_style: Optional[str] = None
    target_audience: Optional[str] = None
    producer_brief: Optional[Dict[str, Any]] = None
    producer_brief: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts config to dictionary for pipeline processing"""
        return {
            'topic': self.topic,
            'emotional_tone': self.emotional_tone.value,
            'story_length': self.story_length,
            'platform': self.platform.value,
            # Add optional fields only if they exist
            **(self.character_constraints and {'character_constraints': self.character_constraints} or {}),
            **(self.setting and {'setting': self.setting} or {}),
            **(self.pacing_style and {'pacing_style': self.pacing_style} or {}),
            **(self.target_audience and {'target_audience': self.target_audience} or {}),
            **(self.producer_brief and {'producer_brief': self.producer_brief} or {}),
            **(self.producer_brief and {'producer_brief': self.producer_brief} or {}),
        }

class InputValidationError(Exception):
    pass

def validate_input(data: Dict[str, Any]) -> InputConfig:
    """Validates raw input dictionary against PRD requirements"""
    # Check required fields
    required = ['topic', 'emotional_tone', 'story_length', 'platform']
    for key in required:
        if key not in data or not data[key]:
            raise InputValidationError(f"Missing required input: {key}")
    
    # Parse enums with fallback or strict mode as needed
    try:
        tone = EmotionalTone(data['emotional_tone'])
    except ValueError:
        valid_tones = [e.value for e in EmotionalTone]
        raise InputValidationError(f"Invalid emotional_tone: '{data['emotional_tone']}'. Valid: {valid_tones}")
        
    try:
        platform = Platform(data['platform'])
    except ValueError:
        # Fallback to OTHER if not recognized, or could raise error depending on strictness
        platform = Platform.OTHER
    
    return InputConfig(
        topic=data['topic'],
        emotional_tone=tone,
        story_length=data['story_length'],
        platform=platform,
        character_constraints=data.get('character_constraints'),
        setting=data.get('setting'),
        pacing_style=data.get('pacing_style'),
        target_audience=data.get('target_audience')
    )

# --- Output Models ---

@dataclass
class Scene:
    id: int
    narration: str
    emotion: str
    camera: str
    lighting: str
    visual_prompt: str
    dialogue: Optional[str] = None # Populated in Dialogue Generation stage

@dataclass
class PipelineOutput:
    story_yaml_content: Dict[str, Any]
    scenes_yaml_content: List[Scene]
    dialogues_yaml_content: List[Dict[str, Any]]
    prompts_yaml_content: List[Dict[str, str]]
    research_context: Optional[Dict[str, Any]] = None


# --- Optional LLM/ML Models (lazy imports to avoid heavy deps) ---

def get_creative_writer(model_name: str = "gpt2"):
    """Lazy import CreativeWriter — only loads torch/transformers when called."""
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    
    class CreativeWriter:
        def __init__(self, model_name=model_name):
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
        def generate_story(self, prompt):
            full_prompt = f"Generate an emotional story about {prompt['topic']} with a {prompt['emotional_tone']} tone. " \
                          f"The story should be structured in scenes and include character development. " \
                          f"Length: {prompt.get('duration', '30 seconds')}."
            inputs = self.tokenizer.encode(full_prompt, return_tensors="pt")
            outputs = self.model.generate(
                inputs, max_length=200, num_return_sequences=1,
                temperature=0.8, do_sample=True, pad_token_id=self.tokenizer.eos_token_id
            )
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return {
                'title': f'Story about {prompt["topic"]}',
                'emotional_tone': prompt['emotional_tone'],
                'content': generated_text,
                'scenes': [{'id': 1, 'description': 'Initial scene setup', 'emotional_context': prompt['emotional_tone']}]
            }


def get_visual_prompt_generator(model_name: str = "stabilityai/stable-diffusion-2"):
    """Lazy import VisualPromptGenerator — only loads diffusers when called."""
    from diffusers import StableDiffusionPipeline
    import torch
    
    class VisualPromptGenerator:
        def __init__(self, model_name=model_name):
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_name, torch_dtype=torch.float16 if device == "cuda" else torch.float32
            ).to(device)
            
        def generate_prompt(self, scene_description):
            base_prompt = f"Cinematic shot of {scene_description['topic']} with {scene_description['emotional_tone']} tone. "
            final_prompt = base_prompt + "highly detailed, professional cinematography, dramatic lighting, 8k resolution"
            image = self.pipeline(final_prompt).images[0]
            return {
                'scene_id': scene_description.get('id', 1),
                'prompt': final_prompt,
                'image': image
            }
