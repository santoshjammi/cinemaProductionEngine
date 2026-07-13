import axios from 'axios';
import type {
  PipelineInput,
  PipelineResult,
  GenerationProgress,
  ImageGenerationResponse,
  Project,
  ProjectCreate,
  ProjectUpdate,
} from './types';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
});

export async function startPipeline(
  input: PipelineInput
): Promise<PipelineResult> {
  const { data } = await api.post<PipelineResult>('/pipeline/start', input);
  return data;
}

export async function getPipelineStatus(
  id: string
): Promise<PipelineResult> {
  const { data } = await api.get<PipelineResult>(`/pipeline/${id}`);
  return data;
}

export async function getGenerationProgress(
  id: string
): Promise<GenerationProgress> {
  const { data } = await api.get<GenerationProgress>(
    `/pipeline/${id}/generation`
  );
  return data;
}

export async function getPipelineHistory(): Promise<PipelineResult[]> {
  const { data } = await api.get<PipelineResult[]>('/pipeline/history');
  return data;
}

export async function retryPipelineStage(
  id: string,
  stage: string
): Promise<PipelineResult> {
  const { data } = await api.post<PipelineResult>(
    `/pipeline/${id}/retry`,
    { stage }
  );
  return data;
}

export async function startVideoGeneration(
  id: string
): Promise<{ clips: string[] }> {
  const { data } = await api.post(`/pipeline/${id}/generate-video`);
  return data;
}

export function getVideoUrl(
  pipelineId: string,
  sceneNumber: number
): string {
  return `/api/v1/pipeline/${pipelineId}/video/${sceneNumber}`;
}

export function getAudioUrl(
  pipelineId: string,
  sceneNumber: number
): string {
  return `/api/v1/pipeline/${pipelineId}/audio/${sceneNumber}`;
}

export function getFinalVideoUrl(pipelineId: string): string {
  return `/api/v1/pipeline/${pipelineId}/final-video`;
}

export async function startImageGeneration(
  id: string
): Promise<{ status: string; totalScenes: number }> {
  const { data } = await api.post(`/pipeline/${id}/generate-images`);
  return data;
}

export async function getImageGenerationStatus(
  id: string
): Promise<ImageGenerationResponse> {
  const { data } = await api.get<ImageGenerationResponse>(
    `/pipeline/${id}/images`
  );
  return data;
}

export function getImageUrl(pipelineId: string, sceneNumber: number): string {
  return `/api/v1/pipeline/${pipelineId}/image/${sceneNumber}`;
}

export async function startKenBurnsVideo(
  id: string
): Promise<{ status: string }> {
  const { data } = await api.post(`/pipeline/${id}/generate-ken-burns-video`);
  return data;
}

export async function createProject(data: ProjectCreate): Promise<Project> {
  const { data: result } = await api.post('/projects', data);
  return result;
}

export async function listProjects(): Promise<Project[]> {
  const { data } = await api.get('/projects');
  return data;
}

export async function getProject(id: string): Promise<Project> {
  const { data } = await api.get(`/projects/${id}`);
  return data;
}

export async function updateProject(id: string, data: ProjectUpdate): Promise<Project> {
  const { data: result } = await api.put(`/projects/${id}`, data);
  return result;
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/projects/${id}`);
}

export async function getProjectStories(id: string): Promise<{ project_id: string; stories: PipelineResult[] }> {
  const { data } = await api.get(`/projects/${id}/stories`);
  return data;
}