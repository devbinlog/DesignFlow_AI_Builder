from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str
    version: str
