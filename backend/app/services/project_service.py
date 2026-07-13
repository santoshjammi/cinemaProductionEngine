import uuid
import logging
from datetime import datetime, timezone
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
            now = datetime.now(timezone.utc).isoformat()
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
        now = datetime.now(timezone.utc).isoformat()
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
        proj["updated_at"] = datetime.now(timezone.utc).isoformat()
        return self._to_response(proj)

    def delete_project(self, project_id: str) -> bool:
        if project_id in self._projects:
            del self._projects[project_id]
            return True
        return False

    def add_story_to_project(self, project_id: str, story_id: str, topic: str, status: str) -> bool:
        proj = self._projects.get(project_id)
        if not proj:
            return False
        now = datetime.now(timezone.utc).isoformat()
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
        proj["updated_at"] = datetime.now(timezone.utc).isoformat()
        return len(proj["stories"]) < before

    def update_story_status(self, project_id: str, story_id: str, status: str):
        proj = self._projects.get(project_id)
        if not proj:
            return
        for s in proj["stories"]:
            if s["id"] == story_id:
                s["status"] = status
                s["updated_at"] = datetime.now(timezone.utc).isoformat()
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
