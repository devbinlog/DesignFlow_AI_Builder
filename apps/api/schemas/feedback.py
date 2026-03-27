import uuid
from datetime import datetime
from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    analysis_run_id: uuid.UUID
    target_type: str
    target_id: str
    original_value: dict
    user_value: dict


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
