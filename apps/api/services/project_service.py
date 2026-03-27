"""프로젝트 CRUD 서비스"""
from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.project import Project
from models.analysis_run import AnalysisRun
from schemas.project import ProjectCreate, ProjectResponse, ProjectDetailResponse, AnalysisSummary
from core.exceptions import ProjectNotFoundException


async def list_projects(db: AsyncSession, limit: int = 20, offset: int = 0) -> tuple[list[ProjectResponse], int]:
    count_result = await db.execute(select(func.count()).select_from(Project))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Project).order_by(Project.created_at.desc()).limit(limit).offset(offset)
    )
    projects = result.scalars().all()

    items = []
    for p in projects:
        count_res = await db.execute(
            select(func.count()).select_from(AnalysisRun).where(AnalysisRun.project_id == p.id)
        )
        analysis_count = count_res.scalar_one()
        item = ProjectResponse.model_validate(p)
        item.analysis_count = analysis_count
        items.append(item)

    return items, total


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> ProjectDetailResponse:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise ProjectNotFoundException(project_id)

    analyses_result = await db.execute(
        select(AnalysisRun)
        .where(AnalysisRun.project_id == project_id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(20)
    )
    analyses = analyses_result.scalars().all()

    count_res = await db.execute(
        select(func.count()).select_from(AnalysisRun).where(AnalysisRun.project_id == project_id)
    )
    analysis_count = count_res.scalar_one()

    detail = ProjectDetailResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        analysis_count=analysis_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
        analyses=[AnalysisSummary(id=a.id, status=a.status.value, created_at=a.created_at) for a in analyses],
    )
    return detail


async def create_project(db: AsyncSession, data: ProjectCreate) -> ProjectResponse:
    project = Project(name=data.name, description=data.description)
    db.add(project)
    await db.flush()
    await db.refresh(project)
    response = ProjectResponse.model_validate(project)
    response.analysis_count = 0
    return response


async def delete_project(db: AsyncSession, project_id: uuid.UUID) -> None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise ProjectNotFoundException(project_id)
    await db.delete(project)
