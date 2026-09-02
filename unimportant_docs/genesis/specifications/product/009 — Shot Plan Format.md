Genesis Specification (GSPEC)
GSPEC-009 — Shot Plan Format

Document ID: GSPEC-009
Title: Shot Plan Format Specification
Version: 1.0.0
Status: Specification
Authority: Derived from GO-109 Visual Expression Ontology

1. Purpose

This Specification defines the format for a Shot Plan — the complete specification of every camera setup in a production. The Shot Plan is produced by the Scene Planner Agent and consumed by the Prompt Builder Agent, Image Generator Agent, and Video Composer Agent. It is the authoritative source of truth for shot composition, camera movement, framing, and per-frame generation parameters.

The Shot Plan lives in the Production Knowledge Graph as a structured set of Shot nodes (GO-109) linked to their parent Scene node. It must be fully validated before any image generation begins.

2. Format

shot_plan:
  production_id: "uuid"
  scene_number: integer
  scene_title: "string"
  target_duration_seconds: number
  visual_style_ref: "string (Visual Style node id)"

  shots:
    - number: integer
      shot_id: "uuid"
      shot_size: "wide | medium | close-up | extreme_close-up | over-the-shoulder | two_shot | establishing"
      camera_movement: "static | pan | tilt | dolly | tracking | crane | handheld | steadicam | zoom_in | zoom_out"
      movement_direction: "string (optional, e.g. 'left-to-right', 'forward')"
      lens_mm: integer
      depth_of_field: "shallow | medium | deep"
      aperture: "string (optional, e.g. 'f/1.8')"
      duration_seconds: number
      visual_intent: "string (descriptive purpose of the shot)"
      emotional_intent: "string (optional, emotional purpose of the shot)"
      characters: ["string (character keys present in frame)"]
      environment: "string (environment key)"
      prompt_context:
        scene_description: "string"
        scene_description_alt: "string (optional, alternative framing for retry)"
        mood: "string"
        lighting_key: "string"
        time_of_day: "string (optional)"
        weather: "string (optional)"
      frames:
        - number: integer
          frame_id: "uuid"
          width: integer
          height: integer
          seed: integer (optional)
          reference_image_ids: ["uuid (optional)"]
          prompt: "string (optional, overrides shot prompt)"
          negative_prompt: "string (optional)"
          model: "sdxl | flux | flux_with_ipadapter (optional)"
          generation_params:
            steps: integer (optional)
            cfg_scale: number (optional)
            sampler: "string (optional)"

3. Field Definitions

- production_id: UUID of the parent production
- scene_number: Sequential scene identifier within the production
- scene_title: Human-readable scene title
- target_duration_seconds: Intended total duration of the scene; the sum of shot durations must equal this value
- visual_style_ref: Reference to the Visual Style node that governs the production's look
- shot.number: Sequential shot number within the scene (1-indexed)
- shot.shot_id: Stable UUID for cross-reference by the asset store and PKG
- shot.shot_size: Framing classification per GO-109
- shot.camera_movement: Camera motion classification per GO-109
- shot.lens_mm: Focal length in millimeters; must be a positive integer
- shot.depth_of_field: Depth of field classification
- shot.aperture: Optional human-readable aperture string
- shot.duration_seconds: Duration of the shot; must be positive
- shot.visual_intent: One-sentence description of what the shot must communicate
- shot.emotional_intent: Optional description of the emotional purpose
- shot.characters: List of character keys that appear in the shot
- shot.environment: Environment key from the Environment Subgraph
- shot.prompt_context: Structured context passed to the Prompt Builder Agent
- shot.frames: Ordered list of frames to generate for the shot
- frame.number: Sequential frame number within the shot (1-indexed)
- frame.width / frame.height: Pixel dimensions; must be multiples of 16
- frame.seed: Optional reproducibility seed
- frame.reference_image_ids: Optional references to existing assets in the asset store
- frame.prompt: Optional override prompt that replaces the builder-generated prompt
- frame.negative_prompt: Optional negative prompt for exclusion control
- frame.model: Generation model identifier
- frame.generation_params: Optional model-specific parameters

4. Validation Rules

- shot numbers must be sequential within each scene (1, 2, 3, ...)
- frame numbers must be sequential within each shot (1, 2, 3, ...)
- The sum of shot.duration_seconds must equal scene.target_duration_seconds (±0.5s tolerance)
- If shot_size is "close-up" or "extreme_close-up", at least one character must be present in shot.characters
- If shot_size is "establishing", shot.characters may be empty
- Frame width and height must be multiples of 16
- Frame width and height must be positive integers
- lens_mm must be a positive integer between 8 and 400
- duration_seconds must be greater than zero
- reference_image_ids must reference existing assets in the asset store
- visual_style_ref must reference an existing Visual Style node in the PKG
- environment must reference an existing Environment node in the PKG
- All character keys in shot.characters must exist in the Character Subgraph
- Every shot must have a non-empty visual_intent
- prompt_context.scene_description must be non-empty
- If camera_movement is "static", movement_direction must be omitted

5. Example

shot_plan:
  production_id: "a1b2c3d4-..."
  scene_number: 3
  scene_title: "Morning Kitchen"
  target_duration_seconds: 18.0
  visual_style_ref: "vs_morrison_001"
  shots:
    - number: 1
      shot_id: "shot-3-1-uuid"
      shot_size: "establishing"
      camera_movement: "static"
      lens_mm: 35
      depth_of_field: "deep"
      duration_seconds: 4.0
      visual_intent: "Establish the kitchen and morning light before Claire enters"
      characters: []
      environment: "kitchen_morrison"
      prompt_context:
        scene_description: "Modest kitchen, warm morning light through window, wooden table with two chairs"
        mood: "warm, quiet"
        lighting_key: "natural_daylight"
      frames:
        - number: 1
          frame_id: "frame-3-1-1-uuid"
          width: 1920
          height: 1080
          seed: 42117
          model: "sdxl"
    - number: 2
      shot_id: "shot-3-2-uuid"
      shot_size: "close-up"
      camera_movement: "static"
      lens_mm: 85
      depth_of_field: "shallow"
      aperture: "f/1.8"
      duration_seconds: 5.0
      visual_intent: "Show Claire's quiet emotion as she reads the note"
      emotional_intent: "longing, restrained grief"
      characters: ["claire"]
      environment: "kitchen_morrison"
      prompt_context:
        scene_description: "Claire in soft sweater, reading a handwritten note at the kitchen table"
        mood: "tender, melancholic"
        lighting_key: "natural_daylight"
      frames:
        - number: 1
          frame_id: "frame-3-2-1-uuid"
          width: 1920
          height: 1080
          seed: 88291
          model: "sdxl"

6. Usage

- Produced by: Scene Planner Agent (GAS-008)
- Consumed by: Prompt Builder Agent (GAS-011), Image Generator Agent (GAS-012), Video Composer Agent
- Stored in: Production Knowledge Graph as Shot nodes linked to the parent Scene node
- Validated by: Production Orchestrator Agent before dispatch to image generation
- Versioned: Each revision produces a new Shot Plan version; previous versions are retained in the PKG for auditability

7. Evolution Policy

This Specification may evolve through additive extensions governed by the Specification Governance Framework. New optional fields may be added without breaking existing Shot Plans. Removal or renaming of existing fields requires a major version bump and a migration plan.