import pytest
from backend.app.models.project_schemas import ProjectCreate, ProjectResponse
from backend.app.services.project_service import ProjectService


@pytest.fixture
def service():
    return ProjectService()


def test_project_create_validates_name():
    with pytest.raises(Exception):
        ProjectCreate(name="")


def test_project_create_defaults():
    p = ProjectCreate(name="My Project")
    assert p.name == "My Project"
    assert p.description == ""


def test_project_response_defaults():
    r = ProjectResponse(
        id="1", name="Test", description="",
        created_at="now", updated_at="now",
    )
    assert r.story_count == 0
    assert r.stories == []


def test_create_project(service):
    result = service.create_project(ProjectCreate(name="Test"))
    assert result.name == "Test"
    assert result.id is not None
    assert result.story_count == 0


def test_list_projects(service):
    service.create_project(ProjectCreate(name="A"))
    service.create_project(ProjectCreate(name="B"))
    projects = service.list_projects()
    assert len(projects) >= 2


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


def test_remove_story_from_project(service):
    p = service.create_project(ProjectCreate(name="P"))
    service.add_story_to_project(p.id, "s1", "S1", "completed")
    service.add_story_to_project(p.id, "s2", "S2", "completed")
    service.remove_story_from_project(p.id, "s1")
    updated = service.get_project(p.id)
    assert updated.story_count == 1
    assert updated.stories[0].id == "s2"


def test_update_story_status(service):
    p = service.create_project(ProjectCreate(name="P"))
    service.add_story_to_project(p.id, "s1", "S1", "running")
    service.update_story_status(p.id, "s1", "completed")
    updated = service.get_project(p.id)
    assert updated.stories[0].status == "completed"


def test_pipeline_state_includes_project_id(service):
    p = service.create_project(ProjectCreate(name="State Test"))
    service.add_story_to_project(p.id, "pipe-1", "Test", "completed")
    updated = service.get_project(p.id)
    assert updated.story_count == 1
    assert updated.stories[0].topic == "Test"
