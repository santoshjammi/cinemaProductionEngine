import { vi, describe, it, expect, beforeEach } from 'vitest';
import { usePipelineStore } from './store';

vi.mock('@/lib/api', () => ({
  startPipeline: vi.fn().mockResolvedValue({
    id: 'test-pipeline-1',
    topic: 'story in project',
    status: 'completed',
    stages: [{ name: 'research', status: 'completed' }],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }),
  createProject: vi.fn().mockImplementation(async (data) => ({
    id: 'proj-' + Date.now(),
    name: data.name,
    description: data.description || '',
    story_count: 0,
    stories: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  })),
  listProjects: vi.fn().mockResolvedValue([]),
  getProject: vi.fn().mockImplementation(async (id) => ({
    id,
    name: 'Test Project',
    description: '',
    story_count: 2,
    stories: [
      { id: 'pipe-1', topic: 'Story 1', status: 'completed', created_at: new Date().toISOString() },
      { id: 'pipe-2', topic: 'Story 2', status: 'running', created_at: new Date().toISOString() },
    ],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  })),
}));

describe('PipelineStore', () => {
  beforeEach(() => {
    usePipelineStore.getState().reset();
  });

  it('starts with empty state', () => {
    const state = usePipelineStore.getState();
    expect(state.currentPipeline).toBeNull();
    expect(state.generationProgress).toBeNull();
    expect(state.isRunning).toBe(false);
    expect(state.error).toBeNull();
  });

  it('sets running state on start', () => {
    usePipelineStore.getState().startPipeline({
      topic: 'test story',
      enableResearch: true,
    });
    const state = usePipelineStore.getState();
    expect(state.isRunning).toBe(true);
  });

  it('resets state correctly', () => {
    const store = usePipelineStore.getState();
    store.startPipeline({ topic: 'test' });
    store.reset();
    const state = usePipelineStore.getState();
    expect(state.currentPipeline).toBeNull();
    expect(state.error).toBeNull();
    expect(state.isRunning).toBe(false);
  });
});

describe('PipelineStore Projects', () => {
  beforeEach(() => {
    usePipelineStore.getState().reset();
    usePipelineStore.setState({
      projects: [],
      currentProject: null,
    });
  });

  it('initializes with no projects', () => {
    const state = usePipelineStore.getState();
    expect(state.projects).toEqual([]);
    expect(state.currentProject).toBeNull();
  });

  it('creates a project via store action', async () => {
    const { createProject } = usePipelineStore.getState();
    const project = await createProject({
      name: 'Test Project',
      description: 'A test project',
    });
    expect(project.name).toBe('Test Project');
    expect(project.id).toBeTruthy();
    const state = usePipelineStore.getState();
    expect(state.projects).toHaveLength(1);
  });

  it('sets current project', () => {
    const { setCurrentProject } = usePipelineStore.getState();
    const project = {
      id: 'proj-1',
      name: 'My Project',
      description: 'desc',
      story_count: 3,
      stories: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setCurrentProject(project);
    expect(usePipelineStore.getState().currentProject?.id).toBe('proj-1');
  });

  it('passes projectId to startPipeline', async () => {
    const { startPipeline } = usePipelineStore.getState();
    await startPipeline(
      { topic: 'story in project', enableResearch: false },
      'proj-1'
    );
    const state = usePipelineStore.getState();
    expect(state.isRunning).toBe(false);
    expect(state.currentPipeline?.id).toBe('test-pipeline-1');
  });

  it('loads projects into state', async () => {
    const { loadProjects } = usePipelineStore.getState();
    await loadProjects();
    const state = usePipelineStore.getState();
    expect(state.projects).toEqual([]);
  });

  it('loads a single project into currentProject', async () => {
    const { loadProject } = usePipelineStore.getState();
    await loadProject('proj-1');
    const state = usePipelineStore.getState();
    expect(state.currentProject?.id).toBe('proj-1');
    expect(state.currentProject?.name).toBe('Test Project');
    expect(state.currentProject?.story_count).toBe(2);
  });

  it('loadProject fails silently for unknown id', async () => {
    const api = await import('@/lib/api');
    (api.getProject as any).mockRejectedValueOnce(new Error('Not found'));

    const { loadProject } = usePipelineStore.getState();
    const prev = usePipelineStore.getState().currentProject;
    await loadProject('nonexistent');
    expect(usePipelineStore.getState().currentProject).toBe(prev);
  });
});
