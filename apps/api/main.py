"""DesignFlow AI Builder — FastAPI 진입점"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import settings
from core.database import engine, Base
from routers import projects, analysis, feedback

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시: 테이블 생성 (개발 환경용; 프로덕션은 Alembic 사용)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DesignFlow AI Builder API 시작됨")
    yield
    await engine.dispose()
    logger.info("DesignFlow AI Builder API 종료됨")


app = FastAPI(
    title="DesignFlow AI Builder API",
    description="Figma 디자인 분석 및 React + Tailwind 코드 생성 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(projects.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("처리되지 않은 예외: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "서버 내부 오류가 발생했습니다."}},
    )
