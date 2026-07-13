# Local LLM Implementation Context Document

## Overview
This document outlines the implementation of Text Cinema Engine using local LLMs instead of cloud-based GPT-4 API. This provides:
- Complete offline functionality
- No API costs or rate limits
- Full data privacy
- Customizable model parameters
- Support for open-source models (Llama 3, Mistral, etc.)

## Technical Stack

### LLM Integration Options
1. **Ollama** - Primary interface for running local LLMs
   - Supports multiple models: Llama 3, Mistral, Gemma, etc.
   - Simple HTTP API interface
   - Docker support available
   - Model pull/push capabilities

2. **LocalAI** - Alternative GPT-compatible API endpoint
   - Compatible with OpenAI API format (easy switch if needed)
   - Supports multiple backends (llama.cpp, textgen.cpp, etc.)

3. **Hugging Face Transformers** - Direct library integration
   - No server required
   - More control over inference process
   - Higher system resource requirements

### Recommended Architecture
```
app.py -> Pipeline Orchestrator -> LLM Wrapper -> Local LLM Service (Ollama)
                                      |
                                  config/models.py
```

## Model Recommendations for VideoGen Task

### Primary Models
1. **Llama 3 (8B or 70B)** - Best overall balance of quality and performance
2. **Mistral 7B** - Good alternative with efficient memory usage
3. **Gemma 7B** - Google's lightweight model, good for text generation

### System Prompts by Stage
Each pipeline stage will use specialized system prompts to guide the local LLM:

1. **Story Generation Prompt**: "You are an expert storyteller specializing in creating cinematic narratives..."
2. **Scene Decomposition Prompt**: "You are a film director tasked with breaking down stories into scenes..."
3. **Dialogue Generation Prompt**: "You are a professional dialogue writer specializing in short-form video content..."
4. **Cinematic Prompt Prompt**: "You are an expert prompt engineer for text-to-video models..."

## Implementation Plan

### Phase 1: Core Infrastructure (Current)
- [x] Basic project structure
- [x] Data models and validation
- [x] Pipeline orchestrator framework
- [ ] LLM Wrapper with Ollama integration
- [ ] Specialized prompts for each stage
- [ ] Model configuration options

### Phase 2: Enhanced Features
- [ ] Multi-model support (ability to switch between models)
- [ ] Streaming responses for long outputs
- [ ] Caching mechanism for repeated requests
- [ ] Temperature and parameter customization per stage
- [ ] Prompt templating with context injection

### Phase 3: Advanced Functionality
- [ ] Local embedding model for content analysis
- [ ] Automatic model selection based on task complexity
- [ ] Distributed inference (across multiple GPUs if available)
- [ ] Batch processing capabilities
- [ ] Performance metrics and logging

## Configuration Requirements

### Ollama Setup
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull recommended model
ollama pull llama3:8b-instruct-q4_K_M
```

### Application Config
```yaml
# config/llm_config.yaml (to be created)
llm_settings:
  endpoint: "http://localhost:11434"
  model: "llama3:8b-instruct-q4_K_M"
  temperature: 0.7
  max_tokens: 2000
  top_p: 0.9
  
stage_settings:
  story_generation:
    temperature: 0.8
    max_tokens: 3000
    top_p: 0.95
    
  scene_decomposition:
    temperature: 0.7
    max_tokens: 2000
    
  dialogue_generation:
    temperature: 0.9
    max_tokens: 1500
    
  cinematic_prompt:
    temperature: 0.8
    max_tokens: 2000
```

## Hardware Requirements
- **Minimum**: 16GB RAM, capable GPU (optional)
- **Recommended**: 32GB+ RAM, NVIDIA RTX 3090/4090 or Apple M-series chip
- **For 7B models**: ~8GB VRAM/RAM when quantized
- **For 70B models**: ~40GB RAM with CPU execution

## Advantages of Local LLM Approach
1. **Privacy**: All content stays on your machine
2. **Customization**: Fine-tune models for specific video styles
3. **Cost**: No per-token costs after model download
4. **Control**: Full control over generation parameters
5. **Reliability**: Works without internet connection

## Potential Challenges
1. **Performance**: Local inference is slower than API calls
2. **Memory**: Large models require significant RAM/VRAM
3. **Quality Variance**: Model quality depends on base model choice
4. **Consistency**: May need multiple attempts for consistent output

## Next Steps
1. Implement LLM Wrapper with Ollama integration
2. Create specialized system prompts for each stage
3. Add configuration file support
4. Test with different models and parameters
5. Optimize prompt engineering for best results

## Open Questions
1. What specific model would you prefer to use?
2. Should we implement fallback to cloud API if local fails?
3. Do you have any specific style requirements for the generated content?
4. What hardware are you running this on? (helps with model recommendations)
5. Any preference for output format (just YAML files, or also actual video/image generation)?
