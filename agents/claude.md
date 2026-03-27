# DesignFlow AI Builder — Global Agent Rules (claude.md)

## 프로젝트 정체성

**DesignFlow AI Builder**는 Figma 디자인 구조를 분석하여 React + Tailwind 코드를 생성하는 AI 기반 설계-개발 해석 시스템이다. 단순 변환기(converter)가 아니라, 디자인 의도를 이해하고 개발 관점으로 재해석하는 **해석 레이어(interpretation layer)**다.

---

## 전역 규칙

### 언어 규칙
- 모든 내부 추론 및 시스템 사고는 영어로 수행
- 모든 출력, 문서, 설명, 생성 콘텐츠는 **한국어**로 작성
- 코드 파일 내 변수명/함수명/클래스명은 영어 (camelCase / PascalCase / snake_case)
- 코드 주석은 한국어 허용

### 문서 우선 원칙
- 코드 작성 전 반드시 문서가 먼저 작성되어야 함
- 모든 결정 사항은 문서에 명시
- 문서와 코드는 항상 동기화 상태 유지

### 에이전트 분리 원칙
- 각 에이전트는 명확히 구분된 책임 영역을 가짐
- 에이전트 간 책임 중복 금지
- 에이전트 정의를 이탈한 작업 수행 금지

### 품질 기준
- 이 프로젝트는 프로토타입이 아닌 **포트폴리오 수준**의 품질을 요구함
- 얕은 구현, 플레이스홀더 코드 금지
- 모든 구성 요소는 실제 동작 가능한 수준으로 구현

---

## 에이전트 목록

| 에이전트 | 파일 | 핵심 책임 |
|---------|------|----------|
| Product Agent | product_agent.md | 문제 정의, 범위, 사용자 흐름, 기능 우선순위 |
| Frontend Agent | frontend_agent.md | UI 아키텍처, Next.js 앱, 상태 관리 |
| Backend Agent | backend_agent.md | API 설계, FastAPI, 파이프라인 |
| AI Agent | ai_agent.md | 프롬프트 설계, 해석 로직, 구조화 출력 |
| Data Agent | data_agent.md | DB 스키마, JSON 구조, 토큰 저장 |
| Infra Agent | infra_agent.md | 배포 아키텍처, Docker, 환경 변수 |
| Design Agent | design_agent.md | UI/UX 시스템, 레이아웃, 인터랙션 패턴 |

---

## 실행 순서 (STRICT)

```
STEP 0  → 전체 폴더 구조 생성
STEP 1  → 에이전트 파일 정의
STEP 2  → Product Agent: 문제/범위/사용자흐름 정의
STEP 3  → 전체 에이전트 협업: 문서 생성
STEP 4  → 문서 일관성 검토
STEP 5  → apps/web, apps/api 구조 정의
STEP 6  → 백엔드 기반 구현
STEP 7  → 프론트엔드 기반 구현
STEP 8  → 파이프라인 구현 (parser → analyzer → AI → codegen)
STEP 9  → UI 구현
STEP 10 → 시스템 통합
STEP 11 → 포트폴리오 문서 완성
```

---

## 출력 포맷 (모든 단계 공통)

각 단계 완료 시 반드시 아래 형식으로 보고:

1. 현재 단계 목표
2. 생성/수정한 파일 목록
3. 핵심 결정 사항
4. 파일 전체 내용
5. 검토 체크리스트
6. 다음 단계

---

## 기술 스택 요약

| 영역 | 기술 |
|------|------|
| Frontend | Next.js (App Router), TypeScript, Zustand, React Query, shadcn/ui |
| Backend | FastAPI, Python, Pydantic |
| DB | PostgreSQL, JSONB |
| AI | Claude API (claude-sonnet-4-6) |
| Infra | Docker, Docker Compose |

---

## 금지 사항

- 문서 없이 코드 작성
- 에이전트 책임 혼합
- 스코프 임의 확장
- 플레이스홀더 문서 생성
- 한 번에 과도한 코드 생성

---

_Last updated: 2026-03-26_
