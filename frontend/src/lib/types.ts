export type PipelineStageName =
  | 'research'
  | 'story'
  | 'scenes'
  | 'dialogues'
  | 'prompts'
  | 'validation';

export type PipelineStageStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'skipped';

export interface PipelineStage {
  name: PipelineStageName;
  status: PipelineStageStatus;
  progress?: number;
  error?: string;
  startedAt?: string;
  completedAt?: string;
}

export interface ResearchResult {
  topic: string;
  summary: string;
  sources: ResearchSource[];
  keyFindings: string[];
}

export interface ResearchSource {
  title: string;
  url: string;
  snippet: string;
}

export interface StoryResult {
  title: string;
  logline: string;
  synopsis: string;
  emotionalTone: string;
  themes: string[];
  targetAudience: string;
  researchContext?: string;
}

export interface SceneResult {
  sceneNumber: number;
  title: string;
  description: string;
  location: string;
  characters: string[];
  emotionalBeat: string;
  duration: string;
  sceneClass?: string;
}

export interface DialogueResult {
  sceneNumber: number;
  dialogues: DialogueLine[];
}

export interface DialogueLine {
  character: string;
  dialogue: string;
  emotion: string;
  delivery: string;
}

export interface PromptResult {
  sceneNumber: number;
  cinematicPrompt: string;
  visualStyle: string;
  cameraAngle: string;
  lighting: string;
  colorPalette: string[];
}

export interface PipelineMetrics {
  yamlValidationPassRate: number;
  sceneCompletionRate: number;
  emotionalArcScore: number;
  visualPromptQualityScore: number;
  totalDuration?: string;
  totalScenes?: number;
}

export interface PipelineResult {
  id: string;
  topic: string;
  status: 'running' | 'completed' | 'failed';
  stages: PipelineStage[];
  research?: ResearchResult;
  story?: StoryResult;
  scenes?: SceneResult[];
  dialogues?: DialogueResult[];
  prompts?: PromptResult[];
  metrics?: PipelineMetrics;
  error?: string;
  project_id?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProducerBrief {
  title: string;
  logline: string;
  targetAudience: string;
  callToAction: string;
  totalDuration: string;
  aspectRatio: '9:16' | '16:9' | '1:1';
  pacingStyle: 'fast' | 'medium' | 'slow' | 'relaxed';
  visualStyleGuide: string[];
  musicMood: string;
  voiceOverStyle: string;
  multiProductGoals: string[];
}

export interface PipelineInput {
  topic: string;
  tone?: string;
  length?: 'short' | 'medium' | 'long' | 'conversational';
  platform?: 'cinematic' | 'youtube' | 'tiktok' | 'instagram';
  enableResearch?: boolean;
  project_id?: string;
  profileId?: string;
  // Extended Genesis inputs
  producerBrief?: ProducerBrief;
}

export interface VideoClipResult {
  sceneNumber: number;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  videoUrl?: string;
  audioUrl?: string;
  progress?: number;
  error?: string;
}

export interface FinalVideoResult {
  status: 'pending' | 'assembling' | 'completed' | 'failed';
  videoUrl?: string;
  duration?: number;
  fileSize?: number;
  error?: string;
  progress?: number;
}

export interface SceneImageResult {
  sceneNumber: number;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  imageUrl?: string;
  progress?: number;
  error?: string;
}

export interface ImageGenerationResponse {
  pipelineId: string;
  images: SceneImageResult[];
  totalScenes: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
}

export interface StorySummary {
  id: string;
  topic: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  story_count: number;
  stories: StorySummary[];
}

export interface GenerationProgress {
  pipeline: PipelineResult | null;
  clips: VideoClipResult[];
  finalVideo: FinalVideoResult | null;
  overallProgress: number;
  currentStage: string;
}

export interface AudioResult {
  sceneNumber: number;
  sfx: string;
  musicCue: string;
  voiceoverScript: string;
}

// Genesis types
export interface GenesisSpecField {
  key: string;
  label: string;
  value: any;
  type: 'text' | 'textarea' | 'array' | 'object' | 'select';
  options?: string[];
  description?: string;
}

export interface GenesisSpecGroup {
  specId: string;
  specName: string;
  phase: string;
  fields: GenesisSpecField[];
  validationStatus: string;
  confidence: string;
}

export interface GenesisResult {
  sessionId: string;
  completeness: number;
  gatePassed: boolean;
  specs: GenesisSpecGroup[];
  discovery: Record<string, any>;
  reviews: Record<string, any>;
  raw: any;
}

// Genesis2 types
export interface Genesis2PhaseResult {
  phaseNumber: number;
  phaseName: string;
  status: string;
  draftCount: number;
  validationIssues: number;
  critiqueFindings: number;
}

export interface Genesis2Summary {
  synopsis: string;
  version: string;
  created_at: string;
  phases: Genesis2PhaseResult[];
  totalPhases: number;
  completedPhases: number;
  failedPhases: number;
}

export interface Genesis2Package {
  synopsis: string;
  version: string;
  created_at: string;
  phase_results: Genesis2PhaseResult[];
  [key: string]: any;
}

// Production profiles
export interface ProductionProfileRuntime {
  target_minutes: number;
  minimum_minutes: number;
  maximum_minutes: number;
  variance_percent?: number;
}

export interface ProductionProfileScenePolicy {
  preferred_scene_duration_seconds: [number, number];
  hard_minimum_seconds: number;
  hard_maximum_seconds: number;
  preferred_scene_count: [number, number];
  minimum_scene_count: number;
  maximum_scene_count: number;
}

export interface ProductionProfile {
  id: string;
  label: string;
  default?: boolean;
  runtime: ProductionProfileRuntime;
  scene_policy: ProductionProfileScenePolicy;
}

export interface SceneClassDef {
  duration_seconds: [number, number];
  purpose: string;
}
