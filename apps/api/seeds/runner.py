"""
데모용 시드 데이터 삽입 스크립트

사용법:
    cd apps/api
    python -m seeds.runner

효과:
    - 데모 프로젝트 1개 생성
    - 완료된 분석 결과 2개 삽입 (샘플 데이터 기반)
    - 피드백 로그 1개 삽입
"""
from __future__ import annotations

import asyncio
import json
import sys
import uuid
from pathlib import Path

# apps/api를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from core.config import settings
from core.database import Base
from models.project import Project
from models.analysis_run import AnalysisRun, AnalysisStatus
from models.feedback_log import FeedbackLog

# 샘플 파일 경로
SAMPLES_DIR = Path(__file__).parent.parent.parent.parent / "samples"


def _load_sample(filename: str) -> dict:
    """samples/ 디렉토리에서 JSON 파일 로드."""
    path = SAMPLES_DIR / filename
    if not path.exists():
        print(f"  [경고] 샘플 파일 없음: {path}")
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


# ─── 시드 데이터 정의 ──────────────────────────────────────────────────────────

DEMO_DESIGN_TOKENS = {
    "colors": [
        {
            "id": "color-1",
            "name": "Brand Indigo",
            "value": "#6366F1",
            "opacity": 1.0,
            "usageCount": 18,
            "cssVariable": "--color-brand-indigo",
            "tailwindClass": "bg-indigo-500",
            "usageNodes": ["1:2", "2:3", "5:1"],
        },
        {
            "id": "color-2",
            "name": "Background Dark",
            "value": "#0D0D12",
            "opacity": 1.0,
            "usageCount": 1,
            "cssVariable": "--color-background-dark",
            "tailwindClass": "bg-[#0D0D12]",
            "usageNodes": ["1:2"],
        },
        {
            "id": "color-3",
            "name": "Surface Dark",
            "value": "#1A1A24",
            "opacity": 1.0,
            "usageCount": 6,
            "cssVariable": "--color-surface-dark",
            "tailwindClass": "bg-[#1A1A24]",
            "usageNodes": ["3:1", "3:2", "3:3"],
        },
        {
            "id": "color-4",
            "name": "Text Primary",
            "value": "#F2F2F7",
            "opacity": 1.0,
            "usageCount": 12,
            "cssVariable": "--color-text-primary",
            "tailwindClass": "text-[#F2F2F7]",
            "usageNodes": ["2:2", "2:4", "4:1"],
        },
        {
            "id": "color-5",
            "name": "Text Secondary",
            "value": "#8E8EA0",
            "opacity": 1.0,
            "usageCount": 8,
            "cssVariable": "--color-text-secondary",
            "tailwindClass": "text-[#8E8EA0]",
            "usageNodes": ["2:3", "3:5", "4:2"],
        },
    ],
    "typography": [
        {
            "id": "type-1",
            "name": "Display / Extra Bold",
            "fontFamily": "Inter",
            "fontSize": 64,
            "fontWeight": 800,
            "lineHeight": 76.8,
            "letterSpacing": -2.0,
            "tailwindClasses": "text-6xl font-extrabold",
            "usageNodes": ["2:2"],
        },
        {
            "id": "type-2",
            "name": "Heading 1 / Bold",
            "fontFamily": "Inter",
            "fontSize": 36,
            "fontWeight": 700,
            "lineHeight": 43.2,
            "letterSpacing": -1.0,
            "tailwindClasses": "text-4xl font-bold",
            "usageNodes": ["3:1", "4:1"],
        },
        {
            "id": "type-3",
            "name": "Body Large / Regular",
            "fontFamily": "Inter",
            "fontSize": 18,
            "fontWeight": 400,
            "lineHeight": 27.0,
            "letterSpacing": 0,
            "tailwindClasses": "text-lg font-normal",
            "usageNodes": ["2:3", "3:2", "3:3"],
        },
        {
            "id": "type-4",
            "name": "Body / Medium",
            "fontFamily": "Inter",
            "fontSize": 14,
            "fontWeight": 500,
            "lineHeight": 21.0,
            "letterSpacing": 0,
            "tailwindClasses": "text-sm font-medium",
            "usageNodes": ["5:1", "5:2"],
        },
    ],
    "spacing": [
        {"id": "sp-1", "value": 8, "tailwindClass": "2", "usageContext": "padding/gap"},
        {"id": "sp-2", "value": 16, "tailwindClass": "4", "usageContext": "padding/gap"},
        {"id": "sp-3", "value": 24, "tailwindClass": "6", "usageContext": "padding/gap"},
        {"id": "sp-4", "value": 32, "tailwindClass": "8", "usageContext": "padding/gap"},
        {"id": "sp-5", "value": 48, "tailwindClass": "12", "usageContext": "padding/gap"},
        {"id": "sp-6", "value": 80, "tailwindClass": "20", "usageContext": "padding/gap"},
        {"id": "sp-7", "value": 120, "tailwindClass": "30", "usageContext": "padding/gap"},
    ],
    "radius": [
        {"id": "r-1", "value": 6, "tailwindClass": "rounded-md"},
        {"id": "r-2", "value": 12, "tailwindClass": "rounded-xl"},
        {"id": "r-3", "value": 16, "tailwindClass": "rounded-2xl"},
    ],
}

DEMO_AI_INTERPRETATION = {
    "componentCandidates": [
        {
            "nodeId": "1:2",
            "suggestedName": "LandingPage",
            "componentType": "layout",
            "confidence": 0.98,
            "isRepeating": False,
            "children": [
                {
                    "nodeId": "2:1",
                    "suggestedName": "HeroSection",
                    "componentType": "section",
                    "confidence": 0.95,
                    "isRepeating": False,
                    "children": [
                        {
                            "nodeId": "2:2",
                            "suggestedName": "HeroHeadline",
                            "componentType": "ui",
                            "confidence": 0.88,
                            "isRepeating": False,
                            "children": [],
                        },
                        {
                            "nodeId": "2:3",
                            "suggestedName": "HeroSubtitle",
                            "componentType": "ui",
                            "confidence": 0.85,
                            "isRepeating": False,
                            "children": [],
                        },
                        {
                            "nodeId": "2:4",
                            "suggestedName": "HeroCTAGroup",
                            "componentType": "ui",
                            "confidence": 0.90,
                            "isRepeating": False,
                            "children": [],
                        },
                    ],
                },
                {
                    "nodeId": "3:0",
                    "suggestedName": "FeatureSection",
                    "componentType": "section",
                    "confidence": 0.92,
                    "isRepeating": False,
                    "children": [
                        {
                            "nodeId": "3:1",
                            "suggestedName": "FeatureCard",
                            "componentType": "card",
                            "confidence": 0.94,
                            "isRepeating": True,
                            "children": [],
                        },
                    ],
                },
            ],
        }
    ],
    "warnings": [
        {
            "type": "missing_alt_text",
            "message": "이미지 노드에 대체 텍스트(alt)가 없습니다. 접근성을 위해 추가를 권장합니다.",
        }
    ],
}

DEMO_GENERATED_CODE = {
    "files": [
        {
            "path": "components/LandingPage.tsx",
            "language": "tsx",
            "content": """\
import { HeroSection } from './HeroSection'
import { FeatureSection } from './FeatureSection'

export function LandingPage() {
  return (
    <main className="flex flex-col min-h-screen bg-[#0D0D12]">
      <HeroSection />
      <FeatureSection />
    </main>
  )
}
""",
        },
        {
            "path": "components/HeroSection.tsx",
            "language": "tsx",
            "content": """\
export function HeroSection() {
  return (
    <section className="flex flex-col items-center justify-center gap-6 px-30 py-20 text-center">
      <h1 className="text-6xl font-extrabold tracking-tight text-[#F2F2F7]">
        AI로 디자인을<br />
        <span className="text-indigo-500">React 코드로</span>
      </h1>
      <p className="text-lg text-[#8E8EA0] max-w-2xl">
        Figma 디자인을 붙여넣으면 AI가 컴포넌트 구조를 분석하고
        Tailwind CSS 기반 React 코드를 자동으로 생성합니다.
      </p>
      <div className="flex items-center gap-4 mt-4">
        <button className="px-6 py-3 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white font-medium transition-colors">
          무료로 시작하기
        </button>
        <button className="px-6 py-3 rounded-xl border border-[#2A2A35] text-[#8E8EA0] hover:text-[#F2F2F7] hover:border-[#3A3A45] font-medium transition-colors">
          데모 보기
        </button>
      </div>
    </section>
  )
}
""",
        },
        {
            "path": "components/FeatureSection.tsx",
            "language": "tsx",
            "content": """\
import { FeatureCard } from './FeatureCard'

const FEATURES = [
  {
    title: '구조 자동 분석',
    description: 'Figma 노드 트리를 파싱해 컴포넌트 경계를 자동으로 식별합니다.',
    icon: '🔍',
  },
  {
    title: '디자인 토큰 추출',
    description: '색상, 타이포그래피, 간격, 반경 값을 Tailwind 클래스로 매핑합니다.',
    icon: '🎨',
  },
  {
    title: 'AI 코드 생성',
    description: 'Claude AI가 의미론적 컴포넌트 이름과 최적화된 JSX를 생성합니다.',
    icon: '⚡',
  },
]

export function FeatureSection() {
  return (
    <section className="px-30 py-20">
      <h2 className="text-4xl font-bold text-[#F2F2F7] text-center mb-12">
        주요 기능
      </h2>
      <div className="grid grid-cols-3 gap-6">
        {FEATURES.map((feature) => (
          <FeatureCard key={feature.title} {...feature} />
        ))}
      </div>
    </section>
  )
}
""",
        },
        {
            "path": "components/FeatureCard.tsx",
            "language": "tsx",
            "content": """\
interface FeatureCardProps {
  title: string
  description: string
  icon: string
}

export function FeatureCard({ title, description, icon }: FeatureCardProps) {
  return (
    <div className="flex flex-col gap-4 p-8 rounded-2xl bg-[#1A1A24] border border-[#2A2A35]">
      <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-500/10 text-2xl">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-[#F2F2F7]">{title}</h3>
      <p className="text-sm text-[#8E8EA0] leading-relaxed">{description}</p>
    </div>
  )
}
""",
        },
    ]
}


# ─── 시드 실행 함수 ────────────────────────────────────────────────────────────

async def seed(session: AsyncSession) -> None:
    print("  [1/4] 데모 프로젝트 생성 중...")
    project = Project(
        name="DesignFlow 데모 프로젝트",
        description="AI 기반 Figma → React 코드 변환 데모. 랜딩 페이지 디자인 분석 결과 포함.",
    )
    session.add(project)
    await session.flush()
    await session.refresh(project)
    print(f"         → 프로젝트 ID: {project.id}")

    print("  [2/4] 완료된 분석 결과 삽입 중 (샘플 데이터)...")
    raw_input = _load_sample("sample_figma_nodes.json")
    run1 = AnalysisRun(
        project_id=project.id,
        status=AnalysisStatus.COMPLETED,
        ai_model_used="claude-sonnet-4-6",
        raw_input=raw_input if raw_input else {"note": "sample_figma_nodes.json 없음"},
        normalized_tree={"id": str(uuid.uuid4()), "name": "Landing Page", "type": "FRAME"},
        design_tokens=DEMO_DESIGN_TOKENS,
        ai_interpretation=DEMO_AI_INTERPRETATION,
        generated_code=DEMO_GENERATED_CODE,
    )
    session.add(run1)
    await session.flush()
    await session.refresh(run1)
    print(f"         → 분석 ID: {run1.id} (completed)")

    print("  [3/4] 실패 분석 이력 삽입 중 (에러 케이스 데모)...")
    run2 = AnalysisRun(
        project_id=project.id,
        status=AnalysisStatus.FAILED,
        raw_input={"document": {"id": "0:0", "type": "DOCUMENT", "children": []}},
        error_message="캔버스에 파싱 가능한 FRAME이 없습니다.",
    )
    session.add(run2)
    await session.flush()
    print(f"         → 분석 ID: {run2.id} (failed)")

    print("  [4/4] 피드백 로그 삽입 중...")
    feedback = FeedbackLog(
        analysis_run_id=run1.id,
        target_type="component_name",
        target_id="1:2",
        original_value={"name": "LandingPage"},
        user_value={"name": "MainLayout"},
    )
    session.add(feedback)
    await session.flush()

    print()
    print("  ✓ 시드 완료")
    print(f"    - 프로젝트: {project.name}")
    print(f"    - 완료된 분석: 1개 (토큰 {len(DEMO_DESIGN_TOKENS['colors'])}색상, {len(DEMO_DESIGN_TOKENS['typography'])}서체)")
    print(f"    - 실패 분석: 1개")
    print(f"    - 피드백: 1개")


async def main() -> None:
    print("=" * 50)
    print("DesignFlow AI Builder — 시드 데이터 삽입")
    print("=" * 50)
    print(f"  DB: {settings.database_url}")
    print()

    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    print("  테이블 생성 중 (미존재 시)...")
    from core.database import Base as AppBase
    async with engine.begin() as conn:
        await conn.run_sync(AppBase.metadata.create_all)

    async with session_factory() as session:
        async with session.begin():
            await seed(session)

    await engine.dispose()
    print()
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
