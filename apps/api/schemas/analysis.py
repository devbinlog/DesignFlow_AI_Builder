import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class AnalysisRunRequest(BaseModel):
    """클라이언트 → 서버: camelCase 입력 허용"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    project_id: uuid.UUID
    figma_json: dict


class AnalysisRunCreated(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: uuid.UUID
    status: str
    created_at: datetime


class AnalysisStatusResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: uuid.UUID
    status: str
    current_step: str | None = None
    progress: int | None = None


class AnalysisRunResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    design_tokens: dict | None = None
    ai_interpretation: dict | None = None
    generated_code: dict | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
