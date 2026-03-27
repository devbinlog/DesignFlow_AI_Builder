"""분석 서비스 — 파이프라인 오케스트레이션"""
from __future__ import annotations
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.analysis_run import AnalysisRun, AnalysisStatus
from schemas.analysis import AnalysisRunCreated, AnalysisRunResponse, AnalysisStatusResponse
from core.exceptions import AnalysisNotFoundException, ProjectNotFoundException, InvalidFigmaJsonException
from parsers.figma_parser import parse_figma_json
from parsers.normalizer import normalize_tree
from parsers.token_extractor import extract_tokens
from services.ai_service import analyze_structure, name_components, generate_code

logger = logging.getLogger(__name__)


async def create_analysis(
    db: AsyncSession,
    project_id: uuid.UUID,
    figma_json: dict,
) -> AnalysisRunCreated:
    from models.project import Project
    proj_result = await db.execute(select(Project).where(Project.id == project_id))
    if not proj_result.scalar_one_or_none():
        raise ProjectNotFoundException(project_id)

    run = AnalysisRun(project_id=project_id, status=AnalysisStatus.pending, raw_input=figma_json)
    db.add(run)
    await db.flush()
    await db.refresh(run)
    return AnalysisRunCreated(id=run.id, status=run.status.value, created_at=run.created_at)


async def run_pipeline(db: AsyncSession, analysis_id: uuid.UUID) -> None:
    """파이프라인 실행 (백그라운드 태스크로 호출)"""
    result = await db.execute(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
    run = result.scalar_one_or_none()
    if not run:
        return

    run.status = AnalysisStatus.running
    run.started_at = datetime.now(timezone.utc)
    await db.flush()

    try:
        raw_json = run.raw_input or {}

        # Step 1: 파싱
        parsed = parse_figma_json(raw_json)

        # Step 2: 정규화
        normalized = normalize_tree(parsed)
        run.normalized_tree = normalized

        # Step 3: 토큰 추출
        tokens = extract_tokens(normalized)
        run.design_tokens = tokens

        # Step 4: AI 분석
        analysis_result = await analyze_structure(normalized, tokens)
        candidates = analysis_result.get("componentCandidates", [])

        # Step 5: AI 명명
        named_result = await name_components(candidates)
        named_candidates = named_result.get("componentCandidates", candidates)
        run.ai_interpretation = {
            **analysis_result,
            "componentCandidates": named_candidates,
        }

        # Step 6: 코드 생성
        code_result = await generate_code(named_candidates, tokens)
        run.generated_code = code_result

        run.status = AnalysisStatus.completed
        run.completed_at = datetime.now(timezone.utc)
        run.ai_model_used = "claude-sonnet-4-6"

    except InvalidFigmaJsonException as e:
        run.status = AnalysisStatus.failed
        run.error_message = str(e)
    except Exception as e:
        logger.error("파이프라인 실패: %s", e, exc_info=True)
        run.status = AnalysisStatus.failed
        run.error_message = f"내부 오류: {str(e)}"

    run.completed_at = datetime.now(timezone.utc)
    await db.flush()


async def get_analysis(db: AsyncSession, analysis_id: uuid.UUID) -> AnalysisRunResponse:
    result = await db.execute(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
    run = result.scalar_one_or_none()
    if not run:
        raise AnalysisNotFoundException(analysis_id)
    return AnalysisRunResponse(
        id=run.id,
        project_id=run.project_id,
        status=run.status.value,
        design_tokens=run.design_tokens,
        ai_interpretation=run.ai_interpretation,
        generated_code=run.generated_code,
        error_message=run.error_message,
        created_at=run.created_at,
        completed_at=run.completed_at,
    )


async def get_analysis_status(db: AsyncSession, analysis_id: uuid.UUID) -> AnalysisStatusResponse:
    result = await db.execute(
        select(AnalysisRun.id, AnalysisRun.status).where(AnalysisRun.id == analysis_id)
    )
    row = result.first()
    if not row:
        raise AnalysisNotFoundException(analysis_id)
    return AnalysisStatusResponse(id=row.id, status=row.status.value)
