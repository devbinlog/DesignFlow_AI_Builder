# 05. 백엔드 아키텍처

## 목적

이 문서는 FastAPI 기반 백엔드 서비스의 구조와 설계 원칙을 정의한다. 도메인 분리, 서비스 레이어 패턴, 비동기 처리 전략, 파이프라인 구조를 포함한다.

---

## 핵심 결정 사항

### 1. 도메인 기반 라우터 분리
각 비즈니스 도메인은 독립적인 라우터 모듈로 분리된다. 의존성 역전 원칙(DIP)을 적용하여 서비스 레이어는 라우터에 의존하지 않는다.

### 2. 서비스 레이어 패턴
- 라우터: 요청/응답 변환, 인증, 에러 처리
- 서비스: 비즈니스 로직 (파서, 추출기, AI 호출, 코드 생성)
- 리포지토리: DB 쿼리 (SQLAlchemy)

### 3. 비동기 우선 (Async-first)
- 모든 I/O 작업은 async/await 사용
- AI API 호출은 httpx 비동기 클라이언트 사용
- DB 쿼리는 asyncpg + SQLAlchemy async session

---

## 선택 이유

| 결정 | 이유 |
|------|------|
| FastAPI | 자동 OpenAPI 문서, Pydantic 통합, 비동기 지원 |
| Pydantic v2 | 파싱 속도 개선, 더 엄격한 타입 검증 |
| SQLAlchemy 2 | 비동기 세션 지원, ORM 표준화 |
| asyncpg | PostgreSQL 전용 비동기 드라이버, 성능 우수 |

---

## 대안 비교

| 프레임워크 | 장점 | 단점 | 선택 |
|-----------|------|------|------|
| FastAPI | 빠름, 자동 문서화 | - | **선택** |
| Django REST | 배터리 포함 | 비동기 지원 제한 | 미선택 |
| Flask | 간단 | 비동기 생태계 약함 | 미선택 |

---

## 향후 영향

- 비동기 구조로 향후 WebSocket 기반 실시간 분석 상태 지원 가능
- 서비스 레이어 분리로 파서/분석기 교체 시 라우터 변경 불필요
- Pydantic 스키마가 자동으로 OpenAPI 문서를 생성하므로 프론트엔드와 타입 공유 가능

---

## 디렉토리 구조

```
apps/api/
├── main.py                     # FastAPI 앱 진입점
├── core/
│   ├── config.py               # 환경 변수 및 설정
│   ├── database.py             # DB 연결 및 세션
│   ├── dependencies.py         # FastAPI 의존성
│   └── exceptions.py           # 공통 예외 클래스
│
├── routers/
│   ├── __init__.py
│   ├── projects.py             # /api/v1/projects
│   ├── analysis.py             # /api/v1/analysis
│   ├── tokens.py               # /api/v1/tokens
│   ├── codegen.py              # /api/v1/codegen
│   └── feedback.py             # /api/v1/feedback
│
├── services/
│   ├── __init__.py
│   ├── project_service.py      # 프로젝트 CRUD
│   ├── analysis_service.py     # 분석 오케스트레이션
│   ├── ai_service.py           # Claude API 호출
│   └── codegen_service.py      # 코드 생성
│
├── parsers/
│   ├── __init__.py
│   ├── figma_parser.py         # Figma JSON → 내부 노드 구조
│   ├── normalizer.py           # 노드 정규화
│   └── token_extractor.py      # 디자인 토큰 추출
│
├── pipeline/
│   ├── __init__.py
│   ├── runner.py               # 파이프라인 오케스트레이터
│   └── steps/
│       ├── parse_step.py
│       ├── normalize_step.py
│       ├── extract_step.py
│       ├── ai_step.py
│       └── codegen_step.py
│
├── models/
│   ├── __init__.py
│   ├── project.py              # SQLAlchemy 모델
│   ├── analysis_run.py
│   └── feedback_log.py
│
├── schemas/
│   ├── __init__.py
│   ├── project.py              # Pydantic 입출력 스키마
│   ├── analysis.py
│   ├── tokens.py
│   ├── codegen.py
│   └── feedback.py
│
├── repositories/
│   ├── __init__.py
│   ├── project_repo.py
│   └── analysis_repo.py
│
├── clients/
│   ├── __init__.py
│   └── claude_client.py        # Anthropic API 클라이언트
│
├── migrations/                 # Alembic 마이그레이션
│   └── versions/
│
├── tests/
│   ├── test_parsers/
│   ├── test_services/
│   └── test_routers/
│
├── requirements.txt
└── pyproject.toml
```

---

## API 엔드포인트 구조

```
GET    /api/v1/health                    # 헬스 체크
GET    /api/v1/projects                  # 프로젝트 목록
POST   /api/v1/projects                  # 프로젝트 생성
GET    /api/v1/projects/{id}             # 프로젝트 상세
DELETE /api/v1/projects/{id}             # 프로젝트 삭제

POST   /api/v1/analysis                  # 분석 실행 (파이프라인 시작)
GET    /api/v1/analysis/{id}             # 분석 결과 조회
GET    /api/v1/analysis/{id}/status      # 분석 상태 조회
GET    /api/v1/analysis/project/{pid}    # 프로젝트별 분석 목록

GET    /api/v1/analysis/{id}/tokens      # 디자인 토큰
PATCH  /api/v1/analysis/{id}/tokens      # 토큰 수정 (피드백)

GET    /api/v1/analysis/{id}/codegen     # 생성된 코드
POST   /api/v1/analysis/{id}/codegen/run # 코드 재생성

POST   /api/v1/feedback                  # 피드백 제출
```

---

## 파이프라인 설계

```python
# pipeline/runner.py (의사 코드)
async def run_pipeline(raw_figma_json: dict) -> AnalysisResult:
    # Step 1: 파싱
    raw_nodes = await parse_step.run(raw_figma_json)

    # Step 2: 정규화
    normalized_tree = await normalize_step.run(raw_nodes)

    # Step 3: 토큰 추출
    design_tokens = await extract_step.run(normalized_tree)

    # Step 4: AI 해석
    ai_result = await ai_step.run(normalized_tree, design_tokens)

    # Step 5: 코드 생성
    generated_code = await codegen_step.run(ai_result, design_tokens)

    return AnalysisResult(
        normalized_tree=normalized_tree,
        design_tokens=design_tokens,
        ai_interpretation=ai_result,
        generated_code=generated_code,
    )
```

---

## 에러 처리 전략

| 에러 유형 | HTTP 상태 | 처리 방법 |
|----------|----------|----------|
| 유효하지 않은 Figma JSON | 422 | Pydantic 검증 실패 반환 |
| AI API 응답 실패 | 503 | 재시도 후 부분 결과 반환 |
| DB 연결 실패 | 503 | 헬스 체크 실패 알림 |
| 분석 타임아웃 | 408 | 상태를 'failed'로 저장 |

---

_작성 에이전트: Backend Agent_
_최종 수정: 2026-03-26_
