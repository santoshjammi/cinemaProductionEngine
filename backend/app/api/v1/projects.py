import logging
from fastapi import APIRouter, HTTPException
from backend.app.models.project_schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from backend.app.services.project_service import ProjectService
from backend.app.api.v1.pipeline import pipeline_service

logger = logging.getLogger("projects_router")
router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

project_service = ProjectService()


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
    default = project_service.get_default_project()
    if default and project_id == default.id:
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
