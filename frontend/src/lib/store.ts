import { create } from 'zustand';
import type {
  PipelineResult,
  PipelineInput,
  GenerationProgress,
  SceneImageResult,
  Project,
  ProjectCreate,
} from '@/lib/types';
import * as api from '@/lib/api';

interface PipelineStore {
  currentPipeline: PipelineResult | null;
  generationProgress: GenerationProgress | null;
  sceneImages: SceneImageResult[];
  history: PipelineResult[];
  isRunning: boolean;
  isImageGenRunning: boolean;
  error: string | null;
  projects: Project[];
  currentProject: Project | null;

  startPipeline: (input: PipelineInput, projectId?: string) => Promise<void>;
  pollStatus: (id: string) => Promise<void>;
  retryStage: (stage: string) => Promise<void>;
  loadHistory: () => Promise<void>;
  startVideoGen: () => Promise<void>;
  pollVideoGen: (id: string) => Promise<void>;
  startImageGen: () => Promise<void>;
  pollImageGen: (id: string) => Promise<void>;
  startKenBurnsGen: () => Promise<void>;
  reset: () => void;
  loadProjects: () => Promise<void>;
  loadProject: (id: string) => Promise<void>;
  createProject: (data: ProjectCreate) => Promise<Project>;
  setCurrentProject: (project: Project | null) => void;
}

export const usePipelineStore = create<PipelineStore>((set, get) => ({
  currentPipeline: null,
  generationProgress: null,
  sceneImages: [],
  history: [],
  isRunning: false,
  isImageGenRunning: false,
  error: null,
  projects: [],
  currentProject: null,

  startPipeline: async (input: PipelineInput, projectId?: string) => {
    set({ isRunning: true, error: null, currentPipeline: null });
    try {
      const result = await api.startPipeline({ ...input, project_id: projectId });
      set({ currentPipeline: result, isRunning: false });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to start pipeline';
      set({ error: message, isRunning: false });
    }
  },

  pollStatus: async (id: string) => {
    const { currentPipeline } = get();
    if (currentPipeline && currentPipeline.id === id && currentPipeline.status === 'completed') return;

    try {
      const result = await api.getPipelineStatus(id);
      const updated: PipelineResult = {
        ...(currentPipeline || result),
        ...result,
        stages: result.stages,
        updatedAt: result.updatedAt,
      };

      const isCompleted =
        result.stages.every(
          (s) => s.status === 'completed' || s.status === 'skipped'
        ) || result.status === 'completed';

      set({
        currentPipeline: { ...updated, status: isCompleted ? 'completed' : 'running' },
      });

      if (!isCompleted) {
        setTimeout(() => get().pollStatus(id), 2000);
      }
    } catch (err) {
      const is404 = err && typeof err === 'object' && 'response' in err &&
        (err as any).response?.status === 404;
      if (is404) {
        set({ error: `Pipeline not found` });
        return;
      }
      setTimeout(() => get().pollStatus(id), 5000);
    }
  },

  retryStage: async (stage: string) => {
    const { currentPipeline } = get();
    if (!currentPipeline) return;

    set({ isRunning: true, error: null });
    try {
      const result = await api.retryPipelineStage(currentPipeline.id, stage);
      set({ currentPipeline: result, isRunning: false });
      get().pollStatus(result.id);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to retry stage';
      set({ error: message, isRunning: false });
    }
  },

  loadHistory: async () => {
    try {
      const history = await api.getPipelineHistory();
      set({ history });
    } catch {
      // silently fail
    }
  },

  startVideoGen: async () => {
    const { currentPipeline } = get();
    if (!currentPipeline) return;

    try {
      await api.startVideoGeneration(currentPipeline.id);
      set({
        generationProgress: {
          pipeline: currentPipeline,
          clips: [],
          finalVideo: null,
          overallProgress: 0,
          currentStage: 'video-generation',
        },
      });
      get().pollVideoGen(currentPipeline.id);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to start video generation';
      set({ error: message });
    }
  },

  pollVideoGen: async (id: string) => {
    try {
      const progress = await api.getGenerationProgress(id);
      set({ generationProgress: progress });

      if (
        progress.finalVideo?.status !== 'completed' &&
        progress.finalVideo?.status !== 'failed'
      ) {
        setTimeout(() => get().pollVideoGen(id), 3000);
      }
    } catch (err) {
      const is404 = err && typeof err === 'object' && 'response' in err &&
        (err as any).response?.status === 404;
      if (is404) {
        set({ error: `Generation progress not found` });
        return;
      }
      setTimeout(() => get().pollVideoGen(id), 5000);
    }
  },

  startImageGen: async () => {
    const { currentPipeline } = get();
    if (!currentPipeline) return;

    set({ isImageGenRunning: true, sceneImages: [] });
    try {
      await api.startImageGeneration(currentPipeline.id);
      get().pollImageGen(currentPipeline.id);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to start image generation';
      set({ error: message, isImageGenRunning: false });
    }
  },

  pollImageGen: async (id: string) => {
    try {
      const result = await api.getImageGenerationStatus(id);
      set({ sceneImages: result.images, isImageGenRunning: false });

      const anyGenerating = result.images.some(
        (img) => img.status === 'generating'
      );
      if (anyGenerating) {
        set({ isImageGenRunning: true });
        setTimeout(() => get().pollImageGen(id), 2000);
      }
    } catch (err) {
      const is404 = err && typeof err === 'object' && 'response' in err &&
        (err as any).response?.status === 404;
      if (is404) return;
      setTimeout(() => get().pollImageGen(id), 5000);
    }
  },

  startKenBurnsGen: async () => {
    const { currentPipeline } = get();
    if (!currentPipeline) return;

    try {
      await api.startKenBurnsVideo(currentPipeline.id);
      set({
        generationProgress: {
          pipeline: currentPipeline,
          clips: [],
          finalVideo: null,
          overallProgress: 0,
          currentStage: 'video-generation',
        },
      });
      get().pollVideoGen(currentPipeline.id);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to start video generation';
      set({ error: message });
    }
  },

  loadProjects: async () => {
    try {
      const projects = await api.listProjects();
      set({ projects });
    } catch { /* silent */ }
  },

  loadProject: async (id: string) => {
    try {
      const project = await api.getProject(id);
      set({ currentProject: project });
    } catch { /* silent */ }
  },

  createProject: async (data: ProjectCreate) => {
    const project = await api.createProject(data);
    set((state) => ({ projects: [...state.projects, project] }));
    return project;
  },

  setCurrentProject: (project) => set({ currentProject: project }),

  reset: () => {
    set({
      currentPipeline: null,
      generationProgress: null,
      sceneImages: [],
      error: null,
      isRunning: false,
      isImageGenRunning: false,
    });
  },
}));
