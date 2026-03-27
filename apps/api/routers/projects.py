import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db
from core.exceptions import ProjectNotFoundException
from schemas.project import ProjectCreate, ProjectResponse, ProjectDetailResponse
from schemas.common import ErrorResponse
import services.project_service as project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=dict)
async def list_projects(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await project_service.list_projects(db, limit=limit, offset=offset)
    return {"items": [i.model_dump(by_alias=True) for i in items], "total": total, "limit": limit, "offset": offset}


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    return await project_service.create_project(db, data)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await project_service.get_project(db, project_id)
    except ProjectNotFoundException:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "프로젝트를 찾을 수 없습니다."}})


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        await project_service.delete_project(db, project_id)
    except ProjectNotFoundException:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "프로젝트를 찾을 수 없습니다."}})
