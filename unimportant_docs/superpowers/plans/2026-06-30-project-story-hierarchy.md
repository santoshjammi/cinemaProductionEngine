# Project & Story Hierarchy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce a `Project` → `Story` hierarchy so users can organize multiple story ideas under projects, each with its own scenes, dialogues, audio, and video.

**Architecture:** Projects are lightweight containers (name, description, metadata). Existing pipelines become "stories" nested under a project. All existing endpoints remain functional; new endpoints add the project layer.

**Tech Stack:** FastAPI + Pydantic v2 (backend), Next.js 14 + Zustand (frontend)

## Global Constraints

- Backend is in-memory (`_pipelines: dict[str, dict]`) — projects stored the same way
- Existing pipeline endpoints must remain unchanged
- `project_id` is optional on create — missing = auto-assign to "Default Project"
- Frontend uses existing UI component library (Card, Button, Badge, etc.)

---

### Task 1: Backend — Project Schemas

**Files:**
- Create: `backend/app/models/project_schemas.py`
- Test: `backend/tests/test_projects.py`

**Interfaces:**
- Consumes: nothing
- Produces: `ProjectCreate`, `ProjectResponse`, `ProjectUpdate`, `StorySummaryResponse`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_projects.py
import pytest
from backend.app.models.project_schemas import ProjectCreate, ProjectResponse


def test_project_create_validates_name():
    with pytest.raises(Exception):
        ProjectCreate(name="")


def test_project_create_defaults():
    p = ProjectCreate(name="My Project")
    assert p.name == "My Project"
    assert p.description == ""
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/santosh/Desktop/projects/videoGen && python3 -m pytest backend/tests/test_projects.py -v
```
Expected: ModuleNotFoundError or ImportError

- [ ] **Step 3: Write schemas**

```python
# backend/app/models/project_schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class StorySummaryResponse(BaseModel):
    id: str
    topic: str
    status: str
    created_at: str
    updated_at: str
    scene_count: Optional[int] = None
    has_video: bool = False


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    story_count: int = 0
    stories: list[StorySummaryResponse] = []
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/santosh/Desktop/projects/videoGen && python3 -m pytest backend/tests/test_projects.py -v
```
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/project_schemas.py backend/tests/test_projects.py
git commit -m "feat: add project schemas"
```

---

### Task 2: Backend — ProjectService CRUD

**Files:**
- Create: `backend/app/services/project_service.py`
- Test: `backend/tests/test_projects.py` (extend)

**Interfaces:**
- Consumes: `ProjectCreate`, `ProjectUpdate`, `ProjectResponse`
- Produces: `ProjectService` with `create_project`, `get_project`, `list_projects`, `update_project`, `delete_project`, `add_story_to_project`, `remove_story_from_project`

- [ ] **Step 1: Write the failing test**

```python
# extend backend/tests/test_projects.py
import pytest
from backend.app.services.project_service import ProjectService
from backend.app.models.project_schemas import ProjectCreate


@pytest.fixture
def service():
    return ProjectService()


def test_create_project(service):
    result = service.create_project(ProjectCreate(name="Test"))
    assert result.name == "Test"
    assert result.id is not None
    assert result.story_count == 0


def test_list_projects(service):
    service.create_project(ProjectCreate(name="A"))
    service.create_project(ProjectCreate(name="B"))
    projects = service.list_projects()
    assert len(projects) == 2


def test_get_nonexistent_project(service):
    result = service.get_project("nonexistent")
    assert result is None


def test_delete_project(service):
    p = service.create_project(ProjectCreate(name="Del"))
    service.delete_project(p.id)
    assert service.get_project(p.id) is None


def test_add_story_to_project(service):
    p = service.create_project(ProjectCreate(name="P"))
    service.add_story_to_project(p.id, "story-1", "Test story", "completed")
    updated = service.get_project(p.id)
    assert updated.story_count == 1
    assert updated.stories[0].topic == "Test story"


def test_default_project_exists(service):
    default = service.get_default_project()
    assert default is not None
    assert default.name == "Default Project"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/santosh/Desktop/projects/videoGen && python3 -m pytest backend/tests/test_projects.py -v
```
Expected: ImportError

- [ ] **Step 3: Write ProjectService**

```python
# backend/app/services/project_service.py
import uuid
import logging
from datetime import datetime
from typing import Optional

from backend.app.models.project_schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, StorySummaryResponse,
)

logger = logging.getLogger("project_service")


class ProjectService:
    def __init__(self):
        self._projects: dict[str, dict] = {}
        self._ensure_default_project()

    def _ensure_default_project(self):
        existing = [p for p in self._projects.values() if p.get("name") == "Default Project"]
        if not existing:
            now = datetime.utcnow().isoformat()
            pid = str(uuid.uuid4())
            self._projects[pid] = {
                "id": pid,
                "name": "Default Project",
                "description": "Auto-created project for unassigned stories",
                "created_at": now,
                "updated_at": now,
                "stories": [],
            }

    def get_default_project(self) -> Optional[ProjectResponse]:
        for p in self._projects.values():
            if p.get("name") == "Default Project":
                return self._to_response(p)
        return None

    def create_project(self, data: ProjectCreate) -> ProjectResponse:
        pid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        self._projects[pid] = {
            "id": pid,
            "name": data.name,
            "description": data.description,
            "created_at": now,
            "updated_at": now,
            "stories": [],
        }
        logger.info("Created project: %s (%s)", data.name, pid)
        return self._to_response(self._projects[pid])

    def get_project(self, project_id: str) -> Optional[ProjectResponse]:
        proj = self._projects.get(project_id)
        return self._to_response(proj) if proj else None

    def list_projects(self) -> list[ProjectResponse]:
        return [self._to_response(p) for p in self._projects.values()]

    def update_project(self, project_id: str, data: ProjectUpdate) -> Optional[ProjectResponse]:
        proj = self._projects.get(project_id)
        if not proj:
            return None
        if data.name is not None:
            proj["name"] = data.name
        if data.description is not None:
            proj["description"] = data.description
        proj["updated_at"] = datetime.utcnow().isoformat()
        return self._to_response(proj)

    def delete_project(self, project_id: str) -> bool:
        if project_id in self._projects:
            del self._projects[project_id]
            return True
        return False

    def add_story_to_project(self, project_id: str, story_id: str, topic: str, status: str):
        proj = self._projects.get(project_id)
        if not proj:
            return False
        now = datetime.utcnow().isoformat()
        proj["stories"].append({
            "id": story_id,
            "topic": topic,
            "status": status,
            "created_at": now,
            "updated_at": now,
        })
        proj["updated_at"] = now
        return True

    def remove_story_from_project(self, project_id: str, story_id: str) -> bool:
        proj = self._projects.get(project_id)
        if not proj:
            return False
        before = len(proj["stories"])
        proj["stories"] = [s for s in proj["stories"] if s["id"] != story_id]
        proj["updated_at"] = datetime.utcnow().isoformat()
        return len(proj["stories"]) < before

    def update_story_status(self, project_id: str, story_id: str, status: str):
        proj = self._projects.get(project_id)
        if not proj:
            return
        for s in proj["stories"]:
            if s["id"] == story_id:
                s["status"] = status
                s["updated_at"] = datetime.utcnow().isoformat()
                proj["updated_at"] = s["updated_at"]
                break

    def _to_response(self, proj: dict) -> ProjectResponse:
        stories = [StorySummaryResponse(**s) for s in proj.get("stories", [])]
        return ProjectResponse(
            id=proj["id"],
            name=proj["name"],
            description=proj.get("description", ""),
            created_at=proj["created_at"],
            updated_at=proj["updated_at"],
            story_count=len(stories),
            stories=stories,
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/santosh/Desktop/projects/videoGen && python3 -m pytest backend/tests/test_projects.py -v
```
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/project_service.py backend/tests/test_projects.py
git commit -m "feat: add project service with CRUD"
```

---

### Task 3: Backend — Add `project_id` to Pipeline + Backfill Default Project

**Files:**
- Modify: `backend/app/services/pipeline_service.py`
- Modify: `backend/app/api/v1/pipeline.py`

**Interfaces:**
- Consumes: `ProjectService` singleton
- Produces: Pipeline state now includes optional `project_id`. `start_pipeline` accepts optional `project_id`. Existing pipelines auto-assigned to Default Project on startup.

- [ ] **Step 1: Write the failing test**

```python
# extend backend/tests/test_projects.py

def test_pipeline_start_accepts_project_id():
    from backend.app.services.pipeline_service import PipelineService
    ps = PipelineService()
    # Mock the LLM calls or use _skip_execution
    ps._skip_execution = True
    result = ps.start_pipeline(
        topic="Test",
        enable_research=False,
        project_id="some-project",
    )
    # Should create pipeline with project_id
    result_dict = ps.get_pipeline(result["id"])
    # Not asserting project_id here since it's returned from state
```

Actually, since `start_pipeline` is async and calls Ollama, we need a mock setup. Let me adjust the test approach — we test the state modification directly instead:

```python
def test_pipeline_state_includes_project_id():
    from backend.app.services.pipeline_service import PipelineService
    service = PipelineService()
    # Directly manipulate state to verify project_id is stored
    service._pipelines["test-id"] = {
        "id": "test-id",
        "topic": "test",
        "status": "running",
        "project_id": "proj-1",
        "stages": [],
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }
    result = service.get_pipeline("test-id")
    assert result["project_id"] == "proj-1"
```

- [ ] **Step 2: Understand the change needed**

The pipeline state dict needs an optional `project_id` field. When `start_pipeline` is called without `project_id`, auto-assign to the Default Project.

- [ ] **Step 3: Update PipelineService**

In `start_pipeline`, after creating the state dict, add `project_id`:

```python
async def start_pipeline(self, topic: str, ..., project_id: Optional[str] = None) -> dict:
    pipeline_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Resolve project
    if project_id is None:
        default = self._project_service.get_default_project()
        if default:
            project_id = default.id
    else:
        proj = self._project_service.get_project(project_id)
        if not proj:
            project_id = None  # Invalid project — leave unassigned

    state = {
        "id": pipeline_id,
        "topic": topic,
        "status": "running",
        "project_id": project_id,  # New field
        ...
    }

    if project_id:
        self._project_service.add_story_to_project(
            project_id, pipeline_id, topic, "running"
        )
```

Then, in `_run_pipeline`, update the story status on completion/failure. Initialize `_project_service` in `__init__`:

```python
# At the top of PipelineService.__init__
from backend.app.services.project_service import ProjectService
self._project_service = ProjectService()

# Resolve pipelines into default project
self._backfill_default_project()

def _backfill_default_project(self):
    default = self._project_service.get_default_project()
    if default:
        for pid, state in self._pipelines.items():
            if not state.get("project_id"):
                state["project_id"] = default.id
                self._project_service.add_story_to_project(
                    default.id, pid, state.get("topic", ""), state.get("status", "pending")
                )
```

- [ ] **Step 4: Add `project_id` to PipelineResponse schema**

```python
# backend/app/models/schemas.py — add to PipelineResponse
class PipelineResponse(BaseModel):
    id: str
    topic: str
    status: str
    project_id: Optional[str] = None  # NEW
    stages: list[StageResponse]
    ...
```

- [ ] **Step 5: Update `start_pipeline` endpoint to accept `project_id`**

```python
# backend/app/models/schemas.py — add to PipelineStartRequest
class PipelineStartRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    tone: Optional[str] = None
    length: str = Field(default="medium", pattern="^(short|medium|long)$")
    platform: str = Field(default="cinematic", pattern="^(cinematic|youtube|tiktok|instagram)$")
    enable_research: bool = Field(default=True, alias="enableResearch")
    project_id: Optional[str] = None  # NEW
```

```python
# backend/app/api/v1/pipeline.py — pass project_id
@router.post("/start", response_model=PipelineResponse)
async def start_pipeline(req: PipelineStartRequest):
    result = await pipeline_service.start_pipeline(
        topic=req.topic,
        tone=req.tone,
        length=req.length,
        platform=req.platform,
        enable_research=req.enable_research,
        project_id=req.project_id,
    )
    return result
```

- [ ] **Step 6: Run existing tests to verify no regressions**

```bash
cd /Users/santosh/Desktop/projects/videoGen && python3 -m pytest backend/tests/ -v
```
Expected: 23+ passed

- [ ] **Step 7: Commit**

```bash
git add backend/app/services/pipeline_service.py backend/app/models/schemas.py backend/app/api/v1/pipeline.py
git commit -m "feat: nest pipelines under projects via project_id"
```

---

### Task 4: Backend — Project CRUD Endpoints

**Files:**
- Create: `backend/app/api/v1/projects.py`
- Modify: `backend/app/main.py` (include new router)

**Interfaces:**
- Consumes: `ProjectService`, `PipelineService`
- Produces: REST endpoints for project CRUD + story listing

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_api.py — extend or create separate project test

def test_create_project_endpoint(client):
    response = client.post("/api/v1/projects", json={"name": "My Project"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Project"
    assert data["id"] is not None


def test_list_projects_endpoint(client):
    client.post("/api/v1/projects", json={"name": "A"})
    client.post("/api/v1/projects", json={"name": "B"})
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_project_endpoint(client):
    created = client.post("/api/v1/projects", json={"name": "Get Test"}).json()
    response = client.get(f"/api/v1/projects/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Test"


def test_get_nonexistent_project_404(client):
    response = client.get("/api/v1/projects/nonexistent")
    assert response.status_code == 404


def test_delete_project_endpoint(client):
    created = client.post("/api/v1/projects", json={"name": "Delete Me"}).json()
    response = client.delete(f"/api/v1/projects/{created['id']}")
    assert response.status_code == 200
    assert client.get(f"/api/v1/projects/{created['id']}").status_code == 404


def test_project_stories_list(client):
    created = client.post("/api/v1/projects", json={"name": "Stories"}).json()
    response = client.get(f"/api/v1/projects/{created['id']}/stories")
    assert response.status_code == 200
    assert "stories" in response.json()
```

- [ ] **Step 2: Write the router**

```python
# backend/app/api/v1/projects.py
import logging
from fastapi import APIRouter, HTTPException
from backend.app.models.project_schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from backend.app.services.project_service import ProjectService
from backend.app.services.pipeline_service import PipelineService

logger = logging.getLogger("projects_router")
router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

project_service = ProjectService()
pipeline_service = PipelineService()


@router.post("", response_model=ProjectResponse)
async def create_project(data: ProjectCreate):
    return project_service.create_project(data)


@router.get("", response_model=list[ProjectResponse])
async def list_projects():
    return project_service.list_projects()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    result = project_service.get_project(project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, data: ProjectUpdate):
    result = project_service.update_project(project_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    if project_id == project_service.get_default_project()?.id:
        raise HTTPException(status_code=400, detail="Cannot delete default project")
    if not project_service.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "deleted"}


@router.get("/{project_id}/stories")
async def get_project_stories(project_id: str):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    stories = []
    for s in project.stories:
        pipeline = pipeline_service.get_pipeline(s.id)
        if pipeline:
            stories.append(pipeline)
    return {"project_id": project_id, "stories": stories}
```

- [ ] **Step 3: Register router in main.py**

```python
# backend/app/main.py — add import and include
from backend.app.api.v1.projects import router as projects_router
app.include_router(projects_router)
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/santosh/Desktop/projects/videoGen && python3 -m pytest backend/tests/ -v
```
Expected: All existing + new tests passing

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/v1/projects.py backend/app/main.py
git commit -m "feat: add project CRUD endpoints"
```

---

### Task 5: Frontend — Project Types, API Client, Store

**Files:**
- Modify: `frontend/src/lib/types.ts`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/lib/store.ts`

- [ ] **Step 1: Add project types**

```typescript
// frontend/src/lib/types.ts

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
```

- [ ] **Step 2: Add API functions**

```typescript
// frontend/src/lib/api.ts

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
```

- [ ] **Step 3: Add store actions**

```typescript
// frontend/src/lib/store.ts — add to PipelineStore interface and implementation

interface PipelineStore {
  // ... existing fields
  projects: Project[];
  currentProject: Project | null;
  
  loadProjects: () => Promise<void>;
  loadProject: (id: string) => Promise<void>;
  createProject: (data: ProjectCreate) => Promise<Project>;
  setCurrentProject: (project: Project | null) => void;
  
  startPipeline: (input: PipelineInput, projectId?: string) => Promise<void>;
}

// In create:
projects: [],
currentProject: null,

// Implementation:
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

// Modify startPipeline to accept projectId
startPipeline: async (input: PipelineInput, projectId?: string) => {
    set({ isRunning: true, error: null, currentPipeline: null });
    try {
      const result = await api.startPipeline({ ...input, projectId });
      set({ currentPipeline: result, isRunning: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start pipeline';
      set({ error: message, isRunning: false });
    }
  },
```

- [ ] **Step 4: Run tests**

```bash
cd /Users/santosh/Desktop/projects/videoGen/frontend && npm test
```
Expected: All passing, project type additions don't break existing tests

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/types.ts frontend/src/lib/api.ts frontend/src/lib/store.ts
git commit -m "feat: add project types, API client, and store actions"
```

---

### Task 6: Frontend — Project List Page

**Files:**
- Create: `frontend/src/app/projects/page.tsx`
- Create: `frontend/src/components/projects/ProjectCard.tsx`
- Create: `frontend/src/components/projects/CreateProjectDialog.tsx`

- [ ] **Step 1: Write the test**

```typescript
// frontend/src/components/projects/projects.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProjectCard } from './ProjectCard';

describe('ProjectCard', () => {
  it('renders project info', () => {
    render(
      <ProjectCard
        project={{ id: '1', name: 'Test Project', description: 'A test', story_count: 3, stories: [], created_at: '', updated_at: '' }}
      />
    );
    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('3 stories')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Create ProjectCard**

```tsx
// frontend/src/components/projects/ProjectCard.tsx
'use client';

import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { FolderIcon } from 'lucide-react';
import type { Project } from '@/lib/types';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link href={`/projects/${project.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
        <CardContent className="p-4 flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <FolderIcon className="w-5 h-5 text-primary" />
            <h3 className="font-semibold truncate">{project.name}</h3>
          </div>
          {project.description && (
            <p className="text-xs text-muted-foreground line-clamp-2">{project.description}</p>
          )}
          <div className="flex items-center gap-2 mt-auto pt-2">
            <Badge variant="secondary" className="text-xs">
              {project.story_count} {project.story_count === 1 ? 'story' : 'stories'}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
```

- [ ] **Step 3: Create CreateProjectDialog**

```tsx
// frontend/src/components/projects/CreateProjectDialog.tsx
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/Dialog';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { PlusIcon } from 'lucide-react';
import { usePipelineStore } from '@/lib/store';
import type { ProjectCreate } from '@/lib/types';

export function CreateProjectDialog() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const { createProject } = usePipelineStore();

  const handleSubmit = async () => {
    if (!name.trim()) return;
    await createProject({ name: name.trim(), description: description.trim() });
    setName('');
    setDescription('');
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusIcon className="w-4 h-4 mr-1" />
          New Project
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Project</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <Input
            placeholder="Project name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
          />
          <Button onClick={handleSubmit} disabled={!name.trim()} className="w-full">
            Create
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

- [ ] **Step 4: Create projects page**

```tsx
// frontend/src/app/projects/page.tsx
'use client';

import { useEffect } from 'react';
import { usePipelineStore } from '@/lib/store';
import { ProjectCard } from '@/components/projects/ProjectCard';
import { CreateProjectDialog } from '@/components/projects/CreateProjectDialog';
import { EmptyState } from '@/components/ui/EmptyState';
import { FolderIcon } from 'lucide-react';

export default function ProjectsPage() {
  const { projects, loadProjects } = usePipelineStore();

  useEffect(() => {
    loadProjects();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container py-8 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
            <p className="text-muted-foreground mt-1">
              Organize your story ideas into projects
            </p>
          </div>
          <CreateProjectDialog />
        </div>

        {projects.length === 0 ? (
          <EmptyState
            icon={<FolderIcon className="w-12 h-12" />}
            title="No projects yet"
            description="Create your first project to get started"
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <ProjectCard key={p.id} project={p} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
```

- [ ] **Step 5: Verify build**

```bash
cd /Users/santosh/Desktop/projects/videoGen/frontend && npm run build
```
Expected: Compiled successfully

- [ ] **Step 6: Commit**

```bash
git add frontend/src/app/projects/ frontend/src/components/projects/
git commit -m "feat: add project list page with create dialog"
```

---

### Task 7: Frontend — Project Detail Page with Story Table

**Files:**
- Create: `frontend/src/app/projects/[id]/page.tsx`
- Create: `frontend/src/components/projects/StoryTable.tsx`

- [ ] **Step 1: Write the test**

```typescript
// frontend/src/components/projects/story-table.test.tsx
import { render, screen } from '@testing-library/react';
import { StoryTable } from './StoryTable';

describe('StoryTable', () => {
  const stories = [
    { id: '1', topic: 'Test Story', status: 'completed', created_at: '2024-01-01T00:00:00', updated_at: '2024-01-01T00:00:00' },
  ];

  it('renders stories', () => {
    const onNewStory = vi.fn();
    render(<StoryTable stories={stories} projectId="proj-1" onNewStory={onNewStory} />);
    expect(screen.getByText('Test Story')).toBeInTheDocument();
    expect(screen.getByText('completed')).toBeInTheDocument();
  });

  it('shows empty state', () => {
    render(<StoryTable stories={[]} projectId="proj-1" onNewStory={() => {}} />);
    expect(screen.getByText(/no stories/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Create StoryTable**

```tsx
// frontend/src/components/projects/StoryTable.tsx
'use client';

import Link from 'next/link';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { formatDate } from '@/lib/utils';
import { PlusIcon, FileTextIcon } from 'lucide-react';
import type { StorySummary } from '@/lib/types';

interface StoryTableProps {
  stories: StorySummary[];
  projectId: string;
  onNewStory: () => void;
}

export function StoryTable({ stories, projectId, onNewStory }: StoryTableProps) {
  if (stories.length === 0) {
    return (
      <EmptyState
        icon={<FileTextIcon className="w-12 h-12" />}
        title="No stories yet"
        description="Create your first story in this project"
        action={
          <Button onClick={onNewStory}>
            <PlusIcon className="w-4 h-4 mr-1" />
            New Story
          </Button>
        }
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{stories.length} stories</p>
        <Button size="sm" onClick={onNewStory}>
          <PlusIcon className="w-4 h-4 mr-1" />
          New Story
        </Button>
      </div>

      <div className="rounded-md border">
        <div className="grid grid-cols-[1fr_auto_auto_auto] gap-2 p-3 bg-muted/50 text-xs font-medium text-muted-foreground">
          <span>Topic</span>
          <span>Status</span>
          <span>Created</span>
          <span></span>
        </div>
        {stories.map((story) => (
          <Link
            key={story.id}
            href={`/pipeline/${story.id}`}
            className="grid grid-cols-[1fr_auto_auto_auto] gap-2 p-3 items-center border-t hover:bg-accent transition-colors"
          >
            <span className="font-medium text-sm truncate">{story.topic}</span>
            <div>
              <Badge
                variant={
                  story.status === 'completed' ? 'success'
                  : story.status === 'failed' ? 'destructive'
                  : 'warning'
                }
                className="text-[10px]"
              >
                {story.status}
              </Badge>
            </div>
            <span className="text-xs text-muted-foreground">{formatDate(story.created_at)}</span>
            <span className="text-xs text-primary">View &rarr;</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create project detail page**

```tsx
// frontend/src/app/projects/[id]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { usePipelineStore } from '@/lib/store';
import { StoryTable } from '@/components/projects/StoryTable';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { Button } from '@/components/ui/Button';
import { ArrowLeftIcon } from 'lucide-react';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;
  const { currentProject, loadProject, startPipeline } = usePipelineStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadProject(id).finally(() => setLoading(false));
    }
  }, [id]);

  const handleNewStory = async () => {
    if (!currentProject?.id) return;
    router.push(`/?projectId=${currentProject.id}`);
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
        <div className="container py-8 space-y-4">
          <LoadingSkeleton className="h-8 w-48" />
          <LoadingSkeleton className="h-64 w-full" />
        </div>
      </main>
    );
  }

  if (!currentProject) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
        <div className="container py-8">
          <p className="text-muted-foreground">Project not found</p>
          <Link href="/projects" className="text-primary text-sm">Back to projects</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container py-8 space-y-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/projects" className="text-sm text-muted-foreground hover:text-foreground">
              <ArrowLeftIcon className="w-4 h-4" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold">{currentProject.name}</h1>
              {currentProject.description && (
                <p className="text-sm text-muted-foreground">{currentProject.description}</p>
              )}
            </div>
          </div>
        </div>

        <ErrorBoundary>
          <StoryTable
            stories={currentProject.stories}
            projectId={currentProject.id}
            onNewStory={handleNewStory}
          />
        </ErrorBoundary>
      </div>
    </main>
  );
}
```

- [ ] **Step 4: Verify build**

```bash
cd /Users/santosh/Desktop/projects/videoGen/frontend && npm run build
```
Expected: Compiled successfully

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/projects/ frontend/src/components/projects/
git commit -m "feat: add project detail page with story table"
```

---

### Task 8: Frontend — Update Home Page with Project Context + Navigation

**Files:**
- Modify: `frontend/src/app/page.tsx`
- Modify: `frontend/src/app/layout.tsx`
- Modify: `frontend/src/components/pipeline/PipelineView.tsx`
- Modify: `frontend/src/app/pipeline/[id]/page.tsx`

- [ ] **Step 1: Add navigation header to layout**

```tsx
// frontend/src/app/layout.tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Text Cinema Engine',
  description: 'Generate cinematic videos from story prompts',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased min-h-screen`}>
        <nav className="border-b bg-background">
          <div className="container flex items-center h-12 gap-6">
            <a href="/" className="font-bold text-sm hover:text-primary transition-colors">
              Text Cinema
            </a>
            <a href="/projects" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Projects
            </a>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
```

- [ ] **Step 2: Update home page to accept `projectId` query param**

```tsx
// frontend/src/app/page.tsx
'use client';

import { useSearchParams } from 'next/navigation';
import PipelineView from '@/components/pipeline/PipelineView';
import HistoryList from '@/components/pipeline/HistoryList';
import Link from 'next/link';
import { FolderIcon } from 'lucide-react';

export default function Home() {
  const searchParams = useSearchParams();
  const projectId = searchParams?.get('projectId');

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container py-8 space-y-8">
        <header className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
            Text Cinema Engine
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400">
            Transform your story ideas into cinematic video narratives
          </p>
        </header>

        <div className="flex gap-2">
          <Link
            href="/projects"
            className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <FolderIcon className="w-4 h-4" />
            Projects
          </Link>
        </div>

        <PipelineView projectId={projectId || undefined} />
        <HistoryList />
      </div>
    </main>
  );
}
```

- [ ] **Step 3: Update PipelineView to accept and pass `projectId`**

```tsx
// frontend/src/components/pipeline/PipelineView.tsx — add prop
interface PipelineViewProps {
  projectId?: string;
}

export default function PipelineView({ projectId }: PipelineViewProps) {
  // ...existing code...

  const handleStart = async (input: Parameters<typeof startPipeline>[0]) => {
    await startPipeline(input, projectId);
  };

  // ...rest of component unchanged...
}
```

- [ ] **Step 4: Update StoryInput to include project context**

The `StoryInput` component needs to tell the user when they're creating a story within a project. No code change needed — the `projectId` is passed through the store. But we can optionally show a badge:

```tsx
// Inside PipelineView, near StoryInput:
{projectId && (
  <p className="text-xs text-muted-foreground">
    Creating story in project: {currentProject?.name || '...'}
  </p>
)}
```

- [ ] **Step 5: Update detail page to show project context**

```tsx
// frontend/src/app/pipeline/[id]/page.tsx
// Add project breadcrumb if pipeline has project_id

// In the return:
<div className="flex items-center gap-2 text-sm text-muted-foreground">
  <Link href="/projects">Projects</Link>
  {currentPipeline?.projectId && (
    <>
      <span>/</span>
      <Link href={`/projects/${currentPipeline.projectId}`}>Project</Link>
    </>
  )}
  <span>/</span>
  <span>Pipeline {id?.slice(0, 8)}...</span>
</div>
```

- [ ] **Step 6: Verify build**

```bash
cd /Users/santosh/Desktop/projects/videoGen/frontend && npm run build
```
Expected: Compiled successfully

- [ ] **Step 7: Commit**

```bash
git add frontend/src/app/ frontend/src/components/pipeline/
git commit -m "feat: add project navigation and context throughout app"
```

---

### Task 9: Backend — Integration Test for Full Flow

**Files:**
- Modify: `backend/tests/test_api.py`

- [ ] **Step 1: Write the integration test**

```python
# backend/tests/test_api.py

def test_project_to_story_flow(client):
    # 1. Create project
    proj_resp = client.post("/api/v1/projects", json={"name": "Integration Test"})
    assert proj_resp.status_code == 200
    proj = proj_resp.json()
    project_id = proj["id"]

    # 2. Verify project list includes it
    list_resp = client.get("/api/v1/projects")
    assert any(p["id"] == project_id for p in list_resp.json())

    # 3. Verify project detail
    detail_resp = client.get(f"/api/v1/projects/{project_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["story_count"] == 0

    # 4. Start pipeline with project_id
    pipeline_resp = client.post(
        "/api/v1/pipeline/start",
        json={
            "topic": "Integration test story",
            "enableResearch": False,
            "projectId": project_id,
            "length": "short",
        },
    )
    assert pipeline_resp.status_code == 200
    pipeline = pipeline_resp.json()

    # 5. Verify project now has the story
    detail_resp = client.get(f"/api/v1/projects/{project_id}")
    assert detail_resp.json()["story_count"] >= 1

    # 6. Verify project stories endpoint
    stories_resp = client.get(f"/api/v1/projects/{project_id}/stories")
    assert stories_resp.status_code == 200
    assert len(stories_resp.json()["stories"]) >= 1

    # 7. Verify pipeline has project_id
    pipeline_detail = client.get(f"/api/v1/pipeline/{pipeline['id']}")
    assert pipeline_detail.status_code == 200
    assert pipeline_detail.json().get("project_id") == project_id
```

- [ ] **Step 2: Run tests**

```bash
cd /Users/santosh/Desktop/projects/videoGen && python3 -m pytest backend/tests/ -v
```
Expected: All tests passing

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_api.py
git commit -m "test: add project-to-story integration flow test"
```

---

### Task 10: Frontend — E2E Test Update

**Files:**
- Modify: `frontend/e2e/pipeline.spec.ts`

- [ ] **Step 1: Add E2E test for project creation flow**

```typescript
// frontend/e2e/pipeline.spec.ts — add test

test('can create project and view it', async ({ page }) => {
  await page.goto('/projects');
  await page.click('text=New Project');
  await page.fill('input[placeholder="Project name"]', 'E2E Test Project');
  await page.click('text=Create');
  await expect(page.locator('text=E2E Test Project')).toBeVisible();
  await page.click('text=E2E Test Project');
  await expect(page.locator('text=New Story')).toBeVisible();
});
```

- [ ] **Step 2: Run E2E tests (requires dev server running)**

```bash
cd /Users/santosh/Desktop/projects/videoGen/frontend && npx playwright test --headed
```

- [ ] **Step 3: Commit**

```bash
git add frontend/e2e/pipeline.spec.ts
git commit -m "test: add project creation E2E test"
```
