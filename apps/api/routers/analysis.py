import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db
from core.exceptions import ProjectNotFoundException, AnalysisNotFoundException, InvalidFigmaJsonException
from schemas.analysis import AnalysisRunRequest, AnalysisRunCreated, AnalysisRunResponse, AnalysisStatusResponse
import services.analysis_service as analysis_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisRunCreated, status_code=202)
async def run_analysis(
    data: AnalysisRunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    try:
        created = await analysis_service.create_analysis(db, data.project_id, data.figma_json)
        await db.commit()
        # 파이프라인을 백그라운드에서 실행
        background_tasks.add_task(_run_pipeline_bg, created.id)
        return created
    except ProjectNotFoundException:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "프로젝트를 찾을 수 없습니다."}})
    except InvalidFigmaJsonException as e:
        raise HTTPException(status_code=422, detail={"error": {"code": "INVALID_FIGMA_JSON", "message": str(e)}})


async def _run_pipeline_bg(analysis_id: uuid.UUID) -> None:
    from core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await analysis_service.run_pipeline(db, analysis_id)
        await db.commit()


@router.get("/project/{project_id}", response_model=dict)
async def list_by_project(
    project_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from models.analysis_run import AnalysisRun
    result = await db.execute(
        select(AnalysisRun)
        .where(AnalysisRun.project_id == project_id)
        .order_by(AnalysisRun.created_at.desc())
        .limit(limit)
    )
    runs = result.scalars().all()
    items = [{"id": str(r.id), "status": r.status.value, "createdAt": r.created_at.isoformat() if r.created_at else None} for r in runs]
    return {"items": items, "total": len(items)}


@router.get("/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_status(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await analysis_service.get_analysis_status(db, analysis_id)
    except AnalysisNotFoundException:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "분석을 찾을 수 없습니다."}})


@router.get("/{analysis_id}", response_model=AnalysisRunResponse)
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await analysis_service.get_analysis(db, analysis_id)
    except AnalysisNotFoundException:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "분석을 찾을 수 없습니다."}})
