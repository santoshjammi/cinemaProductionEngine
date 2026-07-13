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

export interface PipelineInput {
  topic: string;
  tone?: string;
  length?: 'short' | 'medium' | 'long';
  platform?: 'cinematic' | 'youtube' | 'tiktok' | 'instagram';
  enableResearch?: boolean;
  project_id?: string;
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