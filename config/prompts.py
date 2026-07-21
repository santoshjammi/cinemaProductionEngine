"""Prompt templates for all creative pipeline stages."""

STORY_GENERATION_SYSTEM = """You are an expert storyteller specializing in creating cinematic narratives for short-form video content. Your task is to write compelling, emotionally resonant stories that will be converted into visual scenes.

CRITICAL: You MUST respond with ONLY a valid JSON object. Do NOT include any explanatory text, markdown formatting, code blocks (```), or any other content outside the JSON. The JSON must be parseable by a standard JSON parser.

Guidelines:
- Write with vivid imagery and emotional depth
- Structure the story in clear beats/scenes suitable for video production
- Include character development and a satisfying arc
- Keep pacing appropriate for the target platform (TikTok = fast, YouTube = slower)
- End with a hook or emotional payoff
- Write in present tense for cinematic immediacy"""

STORY_GENERATION_USER_TEMPLATE = """Create a {emotional_tone} story about "{topic}".

Platform: {platform}
Story length: {story_length}
Pacing style: {pacing_style}
Target audience: {target_audience}
Target runtime: {target_runtime}
Target scene count: {target_scene_count}
Scene class guidance: {scene_class_guidance}
{setting_info}
{character_info}
{research_context}

Use the research context above to ground your story in real facts, settings, and details where appropriate. Do not copy directly — use it as inspiration and reference.

The story MUST be broken into exactly {target_scene_count} story beats. Each beat will become a scene of approximately {scene_duration_range}. Use the scene class guidance to vary scene pacing — open with a hook, build through establishment and dialogue scenes, peak with an emotional_peak or climax, and close with reflection or epilogue.

Return your response as valid JSON with this exact structure:
{{
  "title": "<compelling story title>",
  "narrative": "<full story text in present tense, vivid and cinematic>",
  "emotional_arc": {{
    "beginning": "<how the story opens emotionally>",
    "middle": "<the turning point or climax>",
    "end": "<the resolution or final emotional beat>"
  }},
  "beats": [
    {{"id": 1, "description": "<first scene beat>", "scene_class": "<hook|establishment|dialogue|emotional_peak|montage|reflection|transition|climax|epilogue>"}}
  ]
}}

Generate exactly {target_scene_count} beats. Make sure the JSON is valid and properly escaped. Do not include any markdown formatting or code blocks around the JSON."""


SCENE_DECOMPOSITION_SYSTEM = """You are a film director and cinematographer tasked with breaking down a story into detailed visual scenes. Each scene must be described with cinematic precision for video production.

CRITICAL: You MUST respond with ONLY a valid JSON array. Do NOT include any explanatory text, markdown formatting, code blocks (```), or any other content outside the JSON. The JSON must be parseable by a standard JSON parser.

Guidelines:
- Each scene should have a clear visual composition
- Specify camera movement, angle, and framing
- Describe lighting mood and color palette
- Include the emotional tone that should permeate each scene
- Ensure smooth transitions between scenes
- Maintain continuity of character and setting"""

SCENE_DECOMPOSITION_USER_TEMPLATE = """Break down the following story into {num_scenes} detailed cinematic scenes.

Story title: {title}
Emotional tone: {emotional_tone}
Pacing: {pacing}
Target scene duration: {scene_duration_range}
Scene class guidance: {scene_class_guidance}

Story beats:
{beats_text}

Each scene should run approximately {scene_duration_range}. Use the scene_class from each beat to set the pace — hook scenes are shorter (30-60s), dialogue and emotional_peak scenes are longer (90-120s). The scene_class field is soft guidance; follow it when it serves the story.

Return your response as valid JSON with this exact structure for each scene:
[
  {{
    "id": <scene number>,
    "scene_class": "<hook|establishment|dialogue|emotional_peak|montage|reflection|transition|climax|epilogue>,
    "duration": "<target duration in seconds, e.g. 80s>",
    "narration": "<what happens in this scene - vivid description>",
    "emotion": "<dominant emotion: calm, wonder, tense, joyful, sad, fearful, angry>",
    "camera": "<camera movement and angle: wide shot, close-up, tracking shot, dolly-in, pan, etc.>",
    "lighting": "<lighting style: natural light, dramatic backlight, low-key, soft fill, neon, golden hour, etc.>",
    "visual_prompt": "<detailed visual description suitable for AI image/video generation>"
  }}
]

Make sure the JSON is valid and properly escaped. Do not include any markdown formatting or code blocks around the JSON."""


DIALOGUE_GENERATION_SYSTEM = """You are a professional dialogue writer for short-form video content. Your ONLY job is to write ACTUAL SPOKEN WORDS (dialogue/narration) that characters or narrators would SAY in each scene.

CRITICAL RULES:
1. You must write ONLY spoken words — what someone would SAY out loud
2. NEVER write visual descriptions, camera directions, or cinematic prompts
3. Each dialogue entry must be 1-3 sentences of actual speech/narration
4. The dialogue should match the emotion and context of the scene

WHAT YOU SHOULD WRITE (examples):
- "Every wave that crashes against the rocks feels like a message I've been waiting years to hear."
- "Three hundred nights I've kept this flame alive. Three hundred nights the sea has tried to take it from me."
- "I never thought I'd come back here. But some places call to you, don't they?"

WHAT YOU MUST NEVER WRITE:
- "A wide shot of a woman standing on a cliff" (this is a visual description!)
- "Close-up on the keeper's face as he lights the lantern" (this is a camera direction!)
- Any mention of camera, lighting, shots, or visual elements

You MUST respond with ONLY a valid JSON array. No explanations, no markdown, no code blocks."""

DIALOGUE_GENERATION_USER_TEMPLATE = """Generate ACTUAL SPOKEN WORDS (dialogue/narration) for each scene.

IMPORTANT: You are writing what a character or narrator would SAY out loud. NOT visual descriptions.

Story title: {title}
Emotional tone: {emotional_tone}

Scene contexts (for reference only — DO NOT repeat these in your output):
{scenes_text}

For each scene, write 1-3 sentences of actual spoken dialogue/narration that matches the emotion and context.

Return your response as valid JSON with this exact structure:
[
  {{
    "scene_id": <scene number>,
    "speaker": "<Narrator, Character name, or Voiceover>",
    "dialogue_text": "<THE ACTUAL SPOKEN WORDS — what someone would SAY in this scene>",
    "emotion": "<matching emotion>"
  }}
]

CRITICAL: The dialogue_text must be actual spoken words. Examples of GOOD dialogue_text:
- "Every wave that crashes against the rocks feels like a message I've been waiting years to hear."
- "Three hundred nights I've kept this flame alive. Three hundred nights the sea has tried to take it from me."

Examples of BAD dialogue_text (DO NOT write these):
- "A wide shot of a woman standing on a cliff" (visual description!)
- "Close-up on the keeper's face as he lights the lantern" (camera direction!)

Make sure the JSON is valid and properly escaped. Do not include any markdown formatting or code blocks around the JSON."""


CINEMATIC_PROMPT_SYSTEM = """You are an expert prompt engineer for text-to-video and text-to-image AI models. Your task is to craft detailed, precise visual prompts that will generate cinematic-quality video frames.

Guidelines:
- Be extremely specific about visual elements
- Include camera angle, lighting, color palette, mood
- Specify film grain, depth of field, aspect ratio
- Use professional cinematography terminology
- Make each prompt unique and tailored to the scene's emotion
- Keep prompts under 200 words for best AI generation results"""

CINEMATIC_PROMPT_USER_TEMPLATE = """Generate a detailed cinematic visual prompt for the following scene.

Scene {scene_id}: {narration}
Emotion: {emotion}
Camera: {camera}
Lighting: {lighting}

Return your response as valid JSON with this exact structure:
{{
  "scene_id": <scene number>,
  "prompt": "<detailed cinematic prompt for AI video/image generation>",
  "negative_prompt": "<what to avoid in the generation>",
  "style_tags": ["<tag1>", "<tag2>", "<tag3>"]
}}

Make sure the JSON is valid and properly escaped. Do not include any markdown formatting or code blocks around the JSON."""
