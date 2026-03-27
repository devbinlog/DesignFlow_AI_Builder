# 15. 변경 이력 (Changelog)

## 목적

이 문서는 DesignFlow AI Builder의 변경 이력을 기록한다. 주요 결정 변경, 아키텍처 수정, 기능 추가/제거를 시간 순으로 추적한다.

---

## 형식

```
## [버전] - YYYY-MM-DD
### 추가 (Added)
### 변경 (Changed)
### 제거 (Removed)
### 수정 (Fixed)
### 결정 변경 (Decision Changed)
```

---

## [0.1.0] - 2026-03-26

### 추가 (Added)

#### 프로젝트 기반 구조
- `/agents` 디렉토리 생성
  - `claude.md` — 전역 에이전트 규칙
  - `product_agent.md` — 제품 에이전트 정의
  - `frontend_agent.md` — 프론트엔드 에이전트 정의
  - `backend_agent.md` — 백엔드 에이전트 정의
  - `ai_agent.md` — AI 에이전트 정의
  - `data_agent.md` — 데이터 에이전트 정의
  - `infra_agent.md` — 인프라 에이전트 정의
  - `design_agent.md` — 디자인 에이전트 정의

#### 문서 시스템
- `/docs` 디렉토리 생성
  - `00_project_overview.md` — 프로젝트 개요
  - `01_scope_and_goals.md` — 범위 및 목표
  - `02_user_flow.md` — 사용자 흐름
  - `03_information_architecture.md` — 정보 구조
  - `04_frontend_architecture.md` — 프론트엔드 아키텍처
  - `05_backend_architecture.md` — 백엔드 아키텍처
  - `06_data_model.md` — 데이터 모델
  - `07_api_spec.md` — API 명세
  - `08_ai_pipeline.md` — AI 파이프라인
  - `09_codegen_rules.md` — 코드 생성 규칙
  - `10_design_system_and_ui.md` — 디자인 시스템 및 UI
  - `11_infra_and_deployment.md` — 인프라 및 배포
  - `12_dev_rules.md` — 개발 규칙
  - `13_milestones.md` — 마일스톤
  - `14_portfolio_story.md` — 포트폴리오 스토리
  - `15_changelog.md` — 변경 이력 (이 파일)

#### 레포지토리 구조
- `/apps/web` — Next.js 앱 디렉토리 (초기화 대기)
- `/apps/api` — FastAPI 앱 디렉토리 (초기화 대기)
- `/packages/shared` — 공유 패키지 (초기화 대기)
- `/prompts` — AI 프롬프트 파일 (작성 예정)
- `/samples` — 샘플 데이터 (작성 예정)
- `/infra/docker` — Docker 설정 (작성 예정)
- `/infra/env` — 환경 변수 템플릿 (작성 예정)
- `/infra/deployment` — 배포 스크립트 (작성 예정)

### 핵심 아키텍처 결정 (Initial ADR)

| 결정 | 내용 |
|------|------|
| AI 모델 | Claude Sonnet 4.6 선택 |
| 프론트엔드 | Next.js App Router + Zustand + React Query |
| 백엔드 | FastAPI + Pydantic v2 + SQLAlchemy 2 |
| DB | PostgreSQL 16 + JSONB |
| UI | shadcn/ui + Tailwind CSS (다크 테마) |
| 배포 | Docker Compose |

---

## 향후 변경 기록 방법

새 기능을 추가하거나 결정을 변경할 때마다 이 파일 상단에 새 버전을 추가한다.

버전 번호 규칙 (SemVer 변형):
- `0.x.0` — 마일스톤 단위 증가
- `0.0.x` — 세부 기능/문서 변경

---

_작성 에이전트: Product Agent_
_최종 수정: 2026-03-26_
