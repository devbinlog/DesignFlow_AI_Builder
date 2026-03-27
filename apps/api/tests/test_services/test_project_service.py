"""project_service 통합 테스트 (인메모리 DB)"""
import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from services import project_service
from schemas.project import ProjectCreate
from core.exceptions import ProjectNotFoundException


class TestListProjects:
    @pytest.mark.asyncio
    async def test_empty_returns_zero(self, db_session: AsyncSession):
        items, total = await project_service.list_projects(db_session)
        assert total == 0
        assert items == []

    @pytest.mark.asyncio
    async def test_single_project_listed(self, db_session: AsyncSession, sample_project):
        items, total = await project_service.list_projects(db_session)
        assert total == 1
        assert items[0].name == "테스트 프로젝트"

    @pytest.mark.asyncio
    async def test_analysis_count_zero_for_new_project(self, db_session: AsyncSession, sample_project):
        items, _ = await project_service.list_projects(db_session)
        assert items[0].analysis_count == 0

    @pytest.mark.asyncio
    async def test_analysis_count_reflects_runs(self, db_session: AsyncSession, sample_analysis):
        items, _ = await project_service.list_projects(db_session)
        assert items[0].analysis_count == 1

    @pytest.mark.asyncio
    async def test_pagination_limit(self, db_session: AsyncSession):
        for i in range(5):
            await project_service.create_project(db_session, ProjectCreate(name=f"Project {i}"))
        items, total = await project_service.list_projects(db_session, limit=3, offset=0)
        assert total == 5
        assert len(items) == 3

    @pytest.mark.asyncio
    async def test_pagination_offset(self, db_session: AsyncSession):
        for i in range(5):
            await project_service.create_project(db_session, ProjectCreate(name=f"Project {i}"))
        items_page1, _ = await project_service.list_projects(db_session, limit=3, offset=0)
        items_page2, _ = await project_service.list_projects(db_session, limit=3, offset=3)
        ids_page1 = {p.id for p in items_page1}
        ids_page2 = {p.id for p in items_page2}
        assert ids_page1.isdisjoint(ids_page2)


class TestGetProject:
    @pytest.mark.asyncio
    async def test_get_existing_project(self, db_session: AsyncSession, sample_project):
        result = await project_service.get_project(db_session, sample_project.id)
        assert result.id == sample_project.id
        assert result.name == "테스트 프로젝트"
        assert result.description == "pytest 자동화 테스트용"

    @pytest.mark.asyncio
    async def test_get_nonexistent_raises(self, db_session: AsyncSession):
        fake_id = uuid.uuid4()
        with pytest.raises(ProjectNotFoundException):
            await project_service.get_project(db_session, fake_id)

    @pytest.mark.asyncio
    async def test_get_project_includes_analyses(self, db_session: AsyncSession, sample_analysis):
        project_id = sample_analysis.project_id
        result = await project_service.get_project(db_session, project_id)
        assert result.analysis_count == 1
        assert len(result.analyses) == 1
        assert result.analyses[0].id == sample_analysis.id

    @pytest.mark.asyncio
    async def test_get_project_empty_analyses(self, db_session: AsyncSession, sample_project):
        result = await project_service.get_project(db_session, sample_project.id)
        assert result.analyses == []


class TestCreateProject:
    @pytest.mark.asyncio
    async def test_create_with_name_only(self, db_session: AsyncSession):
        data = ProjectCreate(name="새 프로젝트")
        result = await project_service.create_project(db_session, data)
        assert result.name == "새 프로젝트"
        assert result.description is None
        assert result.analysis_count == 0
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_create_with_description(self, db_session: AsyncSession):
        data = ProjectCreate(name="설명 있는 프로젝트", description="상세 설명")
        result = await project_service.create_project(db_session, data)
        assert result.description == "상세 설명"

    @pytest.mark.asyncio
    async def test_created_project_is_retrievable(self, db_session: AsyncSession):
        data = ProjectCreate(name="조회 테스트")
        created = await project_service.create_project(db_session, data)
        fetched = await project_service.get_project(db_session, created.id)
        assert fetched.name == "조회 테스트"

    @pytest.mark.asyncio
    async def test_multiple_projects_have_unique_ids(self, db_session: AsyncSession):
        result1 = await project_service.create_project(db_session, ProjectCreate(name="A"))
        result2 = await project_service.create_project(db_session, ProjectCreate(name="B"))
        assert result1.id != result2.id


class TestDeleteProject:
    @pytest.mark.asyncio
    async def test_delete_existing_project(self, db_session: AsyncSession, sample_project):
        await project_service.delete_project(db_session, sample_project.id)
        with pytest.raises(ProjectNotFoundException):
            await project_service.get_project(db_session, sample_project.id)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_raises(self, db_session: AsyncSession):
        fake_id = uuid.uuid4()
        with pytest.raises(ProjectNotFoundException):
            await project_service.delete_project(db_session, fake_id)

    @pytest.mark.asyncio
    async def test_delete_decreases_count(self, db_session: AsyncSession):
        p1 = await project_service.create_project(db_session, ProjectCreate(name="Delete Me"))
        _, total_before = await project_service.list_projects(db_session)
        await project_service.delete_project(db_session, p1.id)
        _, total_after = await project_service.list_projects(db_session)
        assert total_after == total_before - 1
