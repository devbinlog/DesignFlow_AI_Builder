"""헬스체크 라우터 테스트"""
import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_response_structure(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_version_format(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        version = response.json()["version"]
        parts = version.split(".")
        assert len(parts) == 3
