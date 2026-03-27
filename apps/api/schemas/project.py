import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class AnalysisSummary(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: uuid.UUID
    status: str
    created_at: datetime


class ProjectResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: uuid.UUID
    name: str
    description: str | None = None
    analysis_count: int = 0
    created_at: datetime
    updated_at: datetime


class ProjectDetailResponse(ProjectResponse):
    analyses: list[AnalysisSummary] = []
