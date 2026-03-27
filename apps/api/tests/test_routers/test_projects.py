"""프로젝트 라우터 통합 테스트"""
import pytest
from httpx import AsyncClient


class TestGetProjects:
    @pytest.mark.asyncio
    async def test_empty_list(self, client: AsyncClient):
        response = await client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_list_with_project(self, client: AsyncClient, sample_project):
        response = await client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "테스트 프로젝트"

    @pytest.mark.asyncio
    async def test_list_pagination_params(self, client: AsyncClient, sample_project):
        response = await client.get("/api/v1/projects?limit=10&offset=0")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_project_response_fields(self, client: AsyncClient, sample_project):
        response = await client.get("/api/v1/projects")
        item = response.json()["items"][0]
        assert "id" in item
        assert "name" in item
        assert "analysisCount" in item
        assert "createdAt" in item


class TestCreateProject:
    @pytest.mark.asyncio
    async def test_create_valid_project(self, client: AsyncClient):
        payload = {"name": "새 프로젝트"}
        response = await client.post("/api/v1/projects", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "새 프로젝트"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_with_description(self, client: AsyncClient):
        payload = {"name": "설명 포함", "description": "자세한 설명"}
        response = await client.post("/api/v1/projects", json=payload)
        assert response.status_code == 201
        assert response.json()["description"] == "자세한 설명"

    @pytest.mark.asyncio
    async def test_create_missing_name_returns_422(self, client: AsyncClient):
        response = await client.post("/api/v1/projects", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_empty_name_returns_422(self, client: AsyncClient):
        response = await client.post("/api/v1/projects", json={"name": ""})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_created_project_appears_in_list(self, client: AsyncClient):
        await client.post("/api/v1/projects", json={"name": "목록 확인용"})
        response = await client.get("/api/v1/projects")
        names = [item["name"] for item in response.json()["items"]]
        assert "목록 확인용" in names


class TestGetProjectDetail:
    @pytest.mark.asyncio
    async def test_get_existing_project(self, client: AsyncClient, sample_project):
        response = await client.get(f"/api/v1/projects/{sample_project.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "테스트 프로젝트"
        assert "analyses" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_project_returns_404(self, client: AsyncClient):
        import uuid
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/v1/projects/{fake_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_project_detail_includes_analysis_list(self, client: AsyncClient, sample_analysis):
        project_id = sample_analysis.project_id
        response = await client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["analyses"]) == 1
        assert data["analyses"][0]["status"] == "completed"


class TestDeleteProject:
    @pytest.mark.asyncio
    async def test_delete_existing_project(self, client: AsyncClient, sample_project):
        response = await client.delete(f"/api/v1/projects/{sample_project.id}")
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_deleted_project_not_retrievable(self, client: AsyncClient, sample_project):
        await client.delete(f"/api/v1/projects/{sample_project.id}")
        response = await client.get(f"/api/v1/projects/{sample_project.id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_project_returns_404(self, client: AsyncClient):
        import uuid
        fake_id = uuid.uuid4()
        response = await client.delete(f"/api/v1/projects/{fake_id}")
        assert response.status_code == 404
