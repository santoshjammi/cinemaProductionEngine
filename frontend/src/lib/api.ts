import axios from 'axios';
import type {
  PipelineInput,
  PipelineResult,
  GenerationProgress,
  ImageGenerationResponse,
  Project,
  ProjectCreate,
  ProjectUpdate,
  ProductionProfile,
  SceneClassDef,
} from './types';
import { toCamelCase } from './utils';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
});

api.interceptors.response.use((res) => {
  if (res.data && typeof res.data === 'object') {
    res.data = toCamelCase(res.data);
  }
  return res;
});

// Separate instance for long-running Genesis2 pipeline (no timeout)
const genesisApi = axios.create({
  baseURL: '/api/v1',
  timeout: 0, // no pipeline can take hours
});

genesisApi.interceptors.response.use((res) => {
  if (res.data && typeof res.data === 'object') {
    res.data = toCamelCase(res.data);
  }
  return res;
});

// Separate instance for GENESIS3 (no timeout, large payloads)
const genesis3Api = axios.create({
  baseURL: '/api/v1',
  timeout: 0,
});

genesis3Api.interceptors.response.use((res) => {
  if (res.data && typeof res.data === 'object') {
    res.data = toCamelCase(res.data);
  }
  return res;
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

// Genesis API
export async function runGenesis(synopsis: string): Promise<any> {
  const { data } = await api.post('/genesis/run', { synopsis });
  return data;
}

export async function getGenesisResult(sessionId: string): Promise<any> {
  const { data } = await api.get(`/genesis/${sessionId}`);
  return data;
}

// Genesis2 API
export async function runGenesis2(synopsis: string): Promise<any> {
  const { data } = await genesisApi.post('/genesis2/run', { synopsis });
  return data;
}

// ============================================================================
// GENESIS3 API – Synopsis analysis workflow
// ============================================================================

export interface Genesis3Constraints {
  tone?: string;
  length?: string;
  targetAudience?: string;
  genre?: string;
  [key: string]: any;
}

export interface Genesis3AnalyzeResult {
  synopsisAnalysis: {
    theme: string;
    genre: string;
    coreElements: any[];
    narrativeStructure: string;
    emotionalArc: string;
  };
  characterDna: Record<string, any>;
  worldBuilding: Record<string, any>;
}

export interface Genesis3ReviewResult {
  reviewReport: {
    constitutionChecks: Array<{
      rule: string;
      status: 'pass' | 'fail' | 'warning';
      evidence: string;
      requirement: string;
      finding: string;
    }>;
    summary: Record<string, any>;
  };
  findings: Record<string, any>;
}

export interface Genesis3CertifyResult {
  certificate: {
    id?: string;
    title: string;
    synopsisSummary: string;
    productionReadiness: 'ready' | 'not-ready';
    issuedAt: string;
    compilersPass: Record<string, any>;
    qaResult: Genesis3ReviewResult;
  };
}

export interface Genesis3CertificateResponse {
  id: string;
  title: string;
  synopsisSummary: string;
  productionReadiness: 'ready' | 'not-ready';
  issuedAt: string;
  compilersPass: Record<string, any>;
  qaResult: Genesis3ReviewResult;
}

export async function analyzeSynopsis(
  synopsis: string,
  constraints?: Genesis3Constraints
): Promise<Genesis3AnalyzeResult> {
  const { data } = await genesis3Api.post<Genesis3AnalyzeResult>(
    '/genesis3/analyze',
    { synopsis, ...(constraints || {}) }
  );
  return data;
}

export async function reviewSynopsis(
  synopsis: string,
  constraints?: Genesis3Constraints
): Promise<Genesis3ReviewResult> {
  const { data } = await genesis3Api.post<Genesis3ReviewResult>(
    '/genesis3/review',
    { synopsis, ...(constraints || {}) }
  );
  return data;
}

export async function certifySynopsis(
  synopsis: string,
  constraints?: Genesis3Constraints
): Promise<Genesis3CertifyResult> {
  const { data } = await genesis3Api.post<Genesis3CertifyResult>(
    '/genesis3/certify',
    { synopsis, ...(constraints || {}) }
  );
  return data;
}

export async function getCertificate(
  id: string
): Promise<Genesis3CertificateResponse> {
  const { data } = await genesis3Api.get<Genesis3CertificateResponse>(
    `/genesis3/certificate/${id}`
  );
  return data;
}

// Production profiles API
export async function listProductionProfiles(): Promise<{ profiles: ProductionProfile[]; sceneClasses: Record<string, SceneClassDef> }> {
  const { data } = await api.get('/profiles');
  return data;
}

export async function getProductionProfile(profileId: string): Promise<any> {
  const { data } = await api.get(`/profiles/${profileId}`);
  return data;
}

// ============================================================================
// PRODUCTION API – canonical GENESIS2 → PROMETHEUS → final MP4 path
// ============================================================================

export interface ProductionJob {
  jobId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  stage: string;
  error?: string | null;
  runId?: string | null;
  outputPath?: string | null;
  createdAt: string;
  updatedAt: string;
  phases: Array<{
    phaseNumber: number;
    phaseName: string;
    status: string;
    detail?: string;
  }>;
  prometheusStages: Array<{
    name: string;
    status: string;
    artifacts: number;
  }>;
}

export interface ProductionStartRequest {
  synopsis: string;
  constraints?: Record<string, any>;
}

export async function startProduction(
  input: ProductionStartRequest
): Promise<ProductionJob> {
  const { data } = await genesisApi.post<ProductionJob>('/production/start', input);
  return data;
}

export async function getProductionJob(jobId: string): Promise<ProductionJob> {
  const { data } = await genesisApi.get<ProductionJob>(`/production/jobs/${jobId}`);
  return data;
}

export async function listProductionJobs(): Promise<ProductionJob[]> {
  const { data } = await genesisApi.get<ProductionJob[]>('/production/jobs');
  return data;
}

export function getProductionVideoUrl(jobId: string): string {
  return `/api/v1/production/jobs/${jobId}/video`;
}
