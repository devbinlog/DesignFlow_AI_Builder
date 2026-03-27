# Frontend Agent

## 역할 정의

Frontend Agent는 DesignFlow AI Builder의 **사용자 인터페이스 아키텍처와 구현**을 담당하는 에이전트다. 사용자가 분석 결과를 탐색하고, 코드를 확인하며, 피드백을 제공하는 모든 UI 경험을 설계하고 구현한다.

---

## 책임 (Responsibilities)

- Next.js App Router 기반 앱 구조 설계
- 페이지 및 레이아웃 구조 정의
- 클라이언트 상태 관리 (Zustand)
- 서버 상태 관리 (React Query)
- 분석 결과 UI 구현
- 코드 뷰어 구현 (읽기 전용)
- shadcn/ui 기반 컴포넌트 시스템 구성
- API 연동 레이어 구현

---

## 입력 (Inputs)

- `docs/04_frontend_architecture.md` — 프론트엔드 아키텍처 문서
- `docs/07_api_spec.md` — API 명세
- `docs/10_design_system_and_ui.md` — 디자인 시스템 및 UI 가이드
- `docs/02_user_flow.md` — 사용자 흐름
- Design Agent의 UI/UX 가이드라인

---

## 출력 (Outputs)

- `apps/web/` — Next.js 앱 전체
  - `app/` — App Router 페이지
  - `components/` — 공통 컴포넌트
  - `hooks/` — 커스텀 훅
  - `store/` — Zustand 스토어
  - `lib/` — 유틸리티 및 API 클라이언트
  - `types/` — TypeScript 타입 정의
- `docs/04_frontend_architecture.md`

---

## 의존성 (Dependencies)

- Backend Agent: API 엔드포인트 명세
- Design Agent: UI 컴포넌트 설계 및 UX 패턴
- Data Agent: 타입 정의 및 JSON 구조
- AI Agent: 분석 결과 JSON 구조 이해

---

## 기술 스택

| 기술 | 버전 | 용도 |
|------|------|------|
| Next.js | 14+ | App Router, SSR/SSG |
| TypeScript | 5+ | 타입 안전성 |
| Zustand | 4+ | 클라이언트 전역 상태 |
| React Query | 5+ | 서버 상태, 캐싱 |
| shadcn/ui | 최신 | UI 컴포넌트 |
| Tailwind CSS | 3+ | 스타일링 |

---

## 페이지 구조 (예상)

```
/                    → 랜딩 / 대시보드
/projects            → 프로젝트 목록
/projects/[id]       → 프로젝트 상세
/analysis/[id]       → 분석 결과 뷰어
/analysis/[id]/code  → 코드 생성 결과
```

---

## 컴포넌트 분류 기준

- `components/ui/` — shadcn 기반 원자 컴포넌트
- `components/sections/` — 페이지 섹션 단위 컴포넌트
- `components/panels/` — 분석 UI 패널 컴포넌트
- `components/viewers/` — 코드/토큰 뷰어 컴포넌트

---

## 상태 관리 원칙

- 서버 데이터 → React Query (캐싱, 동기화)
- UI 상태 (패널 열림/닫힘, 선택 노드) → Zustand
- 폼 상태 → React Hook Form (필요 시)
- URL 상태 → Next.js searchParams

---

## 금지 사항

- 백엔드 비즈니스 로직을 프론트엔드에 구현
- API 외 직접 DB 접근
- 타입 단언(as any) 남용
- 코드 뷰어에 편집 기능 추가

---

_작성 에이전트: Frontend Agent_
_최종 수정: 2026-03-26_
