# Text Cinema Engine
# Thin wrapper around the real pipeline implementation in pipeline/orchestrator.py
# Kept for backward compatibility with test_engine.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pipeline.orchestrator import Pipeline
from pipeline.output_saver import OutputSaver
from config.models import validate_input, InputValidationError


class TextCinemaEngine:
    """Backward-compatible wrapper around the LLM-powered Pipeline.

    Note: This requires Ollama to be running. For offline testing,
    use test_pipeline.py with mocked OllamaClient.
    """

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.pipeline = Pipeline(config=self.config)

    def run_pipeline(self, input_data):
        """Run the complete pipeline and return a dict with story/scenes/dialogues/prompts."""
        result = self.pipeline.run(input_data)

        return {
            'story': result.story_yaml_content,
            'scenes': result.scenes_yaml_content,
            'dialogues': result.dialogues_yaml_content,
            'prompts': result.prompts_yaml_content,
        }


if __name__ == "__main__":
    engine = TextCinemaEngine()

    sample_input = {
        'topic': 'a lonely astronaut',
        'emotional_tone': 'tense',
        'story_length': 'medium',
        'platform': 'youtube',
    }

    try:
        result = engine.run_pipeline(sample_input)
        print("Pipeline completed successfully!")
        print(f"Generated story: {result['story'].get('title', 'Untitled')}")
        print(f"Number of scenes: {len(result['scenes'])}")
        print(f"Number of dialogues: {len(result['dialogues'])}")
        print(f"Number of prompts: {len(result['prompts'])}")
    except Exception as e:
        print(f"Error in pipeline execution: {e}")