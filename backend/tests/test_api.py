"""Backend API tests for Text Cinema Engine."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import httpx
from backend.app.main import app
from backend.app.api.v1.pipeline import pipeline_service
from backend.app.models.schemas import (
    PipelineStartRequest,
    RetryStageRequest,
    PipelineResponse,
)


@pytest.fixture
def client():
    from backend.app.api.v1.projects import project_service as projects_project_service
    pipeline_service._pipelines = {}
    pipeline_service._skip_execution = True
    pipeline_service._project_service = projects_project_service
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.asyncio
class TestPipelineAPI:
    async def test_health_check(self, client):
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    async def test_start_pipeline_validates_input(self, client):
        response = await client.post(
            "/api/v1/pipeline/start",
            json={"topic": ""},
        )
        assert response.status_code == 422

    async def test_start_pipeline_accepts_valid_input(self, client):
        response = await client.post(
            "/api/v1/pipeline/start",
            json={
                "topic": "A lone astronaut on Mars",
                "tone": "wonder",
                "length": "short",
                "platform": "cinematic",
                "enableResearch": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "A lone astronaut on Mars"
        assert data["status"] == "completed"

    async def test_get_nonexistent_pipeline_returns_404(self, client):
        response = await client.get("/api/v1/pipeline/nonexistent-id")
        assert response.status_code == 404

    async def test_pipeline_stages_are_returned(self, client):
        response = await client.post(
            "/api/v1/pipeline/start",
            json={"topic": "Test story", "enableResearch": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["stages"]) == 6
        stage_names = [s["name"] for s in data["stages"]]
        assert stage_names == [
            "research", "story", "scenes", "dialogues", "prompts", "validation"
        ]

    async def test_retry_stage_validates_stage_name(self, client):
        response = await client.post(
            "/api/v1/pipeline/test-id/retry",
            json={"stage": "invalid-stage"},
        )
        assert response.status_code in (404, 422)

    async def test_generate_video_requires_completed_pipeline(self, client):
        response = await client.post(
            "/api/v1/pipeline/nonexistent-id/generate-video",
        )
        assert response.status_code == 404

    async def test_history_returns_list(self, client):
        response = await client.get("/api/v1/pipeline/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSchemas:
    def test_pipeline_start_request_validates_length(self):
        with pytest.raises(Exception):
            PipelineStartRequest(topic="test", length="invalid")

    def test_retry_stage_request_validates_stage(self):
        req = RetryStageRequest(stage="story")
        assert req.stage == "story"

    def test_pipeline_response_shape(self):
        data = {
            "id": "test-id",
            "topic": "test",
            "status": "running",
            "stages": [],
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
        }
        resp = PipelineResponse(**data)
        assert resp.id == "test-id"
        assert resp.status == "running"


@pytest.mark.asyncio
class TestProjectAPI:
    async def test_create_project(self, client):
        resp = await client.post("/api/v1/projects", json={"name": "Test Project"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Project"
        assert "id" in data

    async def test_list_projects(self, client):
        await client.post("/api/v1/projects", json={"name": "A"})
        await client.post("/api/v1/projects", json={"name": "B"})
        resp = await client.get("/api/v1/projects")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    async def test_get_project(self, client):
        created = (await client.post("/api/v1/projects", json={"name": "Get Test"})).json()
        resp = await client.get(f"/api/v1/projects/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Test"

    async def test_get_nonexistent_project_404(self, client):
        resp = await client.get("/api/v1/projects/nonexistent")
        assert resp.status_code == 404

    async def test_delete_project(self, client):
        created = (await client.post("/api/v1/projects", json={"name": "Delete Me"})).json()
        resp = await client.delete(f"/api/v1/projects/{created['id']}")
        assert resp.status_code == 200

    async def test_cannot_delete_default_project(self, client):
        projects = (await client.get("/api/v1/projects")).json()
        default = [p for p in projects if p["name"] == "Default Project"]
        if default:
            resp = await client.delete(f"/api/v1/projects/{default[0]['id']}")
            assert resp.status_code == 400

    async def test_get_project_stories(self, client):
        created = (await client.post("/api/v1/projects", json={"name": "Stories"})).json()
        resp = await client.get(f"/api/v1/projects/{created['id']}/stories")
        assert resp.status_code == 200
        assert "stories" in resp.json()

    @pytest.mark.asyncio
    async def test_project_to_story_flow(self, client):
        proj_resp = await client.post("/api/v1/projects", json={"name": "Integration Test"})
        assert proj_resp.status_code == 200
        proj = proj_resp.json()
        project_id = proj["id"]

        list_resp = await client.get("/api/v1/projects")
        assert any(p["id"] == project_id for p in list_resp.json())

        detail_resp = await client.get(f"/api/v1/projects/{project_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["story_count"] == 0

        pipeline_resp = await client.post(
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

        detail_resp = await client.get(f"/api/v1/projects/{project_id}")
        assert detail_resp.json()["story_count"] >= 1

        stories_resp = await client.get(f"/api/v1/projects/{project_id}/stories")
        assert stories_resp.status_code == 200
        assert len(stories_resp.json()["stories"]) >= 1

        pipeline_detail = await client.get(f"/api/v1/pipeline/{pipeline['id']}")
        assert pipeline_detail.status_code == 200
        assert pipeline_detail.json().get("project_id") == project_id
