from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db
from schemas.feedback import FeedbackCreate, FeedbackResponse
from models.feedback_log import FeedbackLog

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    data: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    log = FeedbackLog(
        analysis_run_id=data.analysis_run_id,
        target_type=data.target_type,
        target_id=data.target_id,
        original_value=data.original_value,
        user_value=data.user_value,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return FeedbackResponse(id=log.id, created_at=log.created_at)
