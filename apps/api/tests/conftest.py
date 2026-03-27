"""pytest 공통 픽스처 — 인메모리 SQLite 기반 테스트 DB + TestClient"""
from __future__ import annotations

import asyncio
import uuid
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.database import Base
from core.dependencies import get_db
from models.project import Project
from models.analysis_run import AnalysisRun, AnalysisStatus
from main import app


# ─── 인메모리 SQLite 엔진 (테스트 전용) ───────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """세션 범위 이벤트 루프."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """테스트 세션 시작 전 테이블 생성."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """각 테스트에 격리된 DB 세션 (트랜잭션 롤백 방식)."""
    async with TestingSessionLocal() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """FastAPI 테스트 클라이언트 (DB 세션 오버라이드)."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ─── 공통 픽스처: 샘플 데이터 ────────────────────────────────────────────────

@pytest_asyncio.fixture
async def sample_project(db_session: AsyncSession) -> Project:
    """테스트용 샘플 프로젝트."""
    project = Project(name="테스트 프로젝트", description="pytest 자동화 테스트용")
    db_session.add(project)
    await db_session.flush()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def sample_analysis(db_session: AsyncSession, sample_project: Project) -> AnalysisRun:
    """테스트용 샘플 분석 실행 (completed 상태)."""
    run = AnalysisRun(
        project_id=sample_project.id,
        status=AnalysisStatus.COMPLETED,
        design_tokens={
            "colors": [{"id": "color-1", "name": "Primary", "value": "#6366F1"}],
            "typography": [],
            "spacing": [],
            "radius": [],
        },
        ai_interpretation={
            "componentCandidates": [
                {
                    "nodeId": "1:1",
                    "suggestedName": "HeroSection",
                    "componentType": "section",
                    "confidence": 0.92,
                    "isRepeating": False,
                    "children": [],
                }
            ],
            "warnings": [],
        },
        generated_code={
            "files": [
                {
                    "path": "components/HeroSection.tsx",
                    "language": "tsx",
                    "content": "export function HeroSection() { return <section>Hero</section> }",
                }
            ]
        },
    )
    db_session.add(run)
    await db_session.flush()
    await db_session.refresh(run)
    return run


# ─── 공통 픽스처: Figma JSON 샘플 ────────────────────────────────────────────

@pytest.fixture
def minimal_figma_json() -> dict:
    """최소한의 유효한 Figma JSON."""
    return {
        "document": {
            "id": "0:0",
            "name": "Document",
            "type": "DOCUMENT",
            "children": [
                {
                    "id": "0:1",
                    "name": "Page 1",
                    "type": "CANVAS",
                    "children": [
                        {
                            "id": "1:1",
                            "name": "Landing Page",
                            "type": "FRAME",
                            "absoluteBoundingBox": {"x": 0, "y": 0, "width": 1440, "height": 900},
                            "layoutMode": "VERTICAL",
                            "paddingTop": 80,
                            "paddingBottom": 80,
                            "paddingLeft": 120,
                            "paddingRight": 120,
                            "itemSpacing": 48,
                            "fills": [
                                {"type": "SOLID", "color": {"r": 0.05, "g": 0.05, "b": 0.07, "a": 1.0}}
                            ],
                            "children": [
                                {
                                    "id": "2:1",
                                    "name": "HeroSection",
                                    "type": "FRAME",
                                    "absoluteBoundingBox": {"x": 120, "y": 80, "width": 1200, "height": 600},
                                    "layoutMode": "VERTICAL",
                                    "itemSpacing": 24,
                                    "cornerRadius": 12,
                                    "children": [
                                        {
                                            "id": "3:1",
                                            "name": "Title",
                                            "type": "TEXT",
                                            "characters": "AI로 디자인을 코드로",
                                            "style": {
                                                "fontFamily": "Inter",
                                                "fontSize": 64,
                                                "fontWeight": 700,
                                                "lineHeightPx": 76.8,
                                                "letterSpacing": -1.5,
                                            },
                                            "fills": [
                                                {"type": "SOLID", "color": {"r": 0.95, "g": 0.95, "b": 0.97, "a": 1.0}}
                                            ],
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    }


@pytest.fixture
def figma_json_without_document() -> dict:
    return {"version": "1.0", "name": "Invalid"}


@pytest.fixture
def figma_json_empty_canvas() -> dict:
    return {
        "document": {
            "id": "0:0",
            "type": "DOCUMENT",
            "children": [
                {"id": "0:1", "type": "CANVAS", "children": []}
            ],
        }
    }
