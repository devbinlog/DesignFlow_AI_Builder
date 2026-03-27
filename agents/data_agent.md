# Data Agent

## 역할 정의

Data Agent는 DesignFlow AI Builder의 **데이터 구조, DB 스키마, JSON 포맷**을 설계하고 관리하는 에이전트다. 시스템 내 모든 데이터의 형태와 흐름을 정의하며, 원시 데이터부터 최종 결과까지의 변환 구조를 명확히 한다.

---

## 책임 (Responsibilities)

- PostgreSQL DB 스키마 설계
- JSONB 필드 구조 정의
- 정규화된 노드 트리 JSON 구조 정의
- 디자인 토큰 저장 구조 정의
- 분석 결과 버전 관리 구조 설계
- 피드백 로그 구조 정의
- 샘플 데이터 작성

---

## 입력 (Inputs)

- `docs/06_data_model.md` — 데이터 모델 문서
- AI Agent의 출력 JSON 구조
- Backend Agent의 파이프라인 흐름

---

## 출력 (Outputs)

- `docs/06_data_model.md`
- `samples/sample_figma_nodes.json` — Figma 노드 샘플
- `samples/sample_analysis_output.json` — 분석 결과 샘플
- `samples/sample_codegen_output.json` — 코드 생성 결과 샘플
- DB 마이그레이션 파일 (apps/api/migrations/)

---

## 의존성 (Dependencies)

- Backend Agent: 스키마를 실제 ORM 모델로 변환
- AI Agent: AI 출력 구조 → JSONB 저장 형태 일치 확인

---

## 핵심 엔티티

### Projects (프로젝트)
```sql
id            UUID PRIMARY KEY
name          VARCHAR(255)
description   TEXT
created_at    TIMESTAMP
updated_at    TIMESTAMP
```

### AnalysisRuns (분석 실행)
```sql
id              UUID PRIMARY KEY
project_id      UUID FK → Projects
status          ENUM('pending', 'running', 'completed', 'failed')
raw_input       JSONB    -- 원시 Figma JSON
normalized_tree JSONB    -- 정규화된 노드 트리
design_tokens   JSONB    -- 추출된 토큰
ai_interpretation JSONB  -- AI 해석 결과
generated_code  JSONB    -- 생성된 코드 파일들
created_at      TIMESTAMP
completed_at    TIMESTAMP
```

### FeedbackLogs (피드백)
```sql
id              UUID PRIMARY KEY
analysis_run_id UUID FK → AnalysisRuns
target_type     ENUM('token', 'component', 'code')
target_id       VARCHAR(255)
original_value  JSONB
user_value      JSONB
created_at      TIMESTAMP
```

---

## JSONB 구조 원칙

- 원시(raw)와 정규화(normalized) 데이터 분리 저장
- 분석 결과는 버전 이력 추적 가능한 구조
- JSONB 인덱싱으로 자주 조회되는 필드 최적화
- null 허용 여부 명시

---

## 데이터 흐름

```
Figma JSON (raw_input)
  → 정규화 (normalized_tree)
  → 토큰 추출 (design_tokens)
  → AI 해석 (ai_interpretation)
  → 코드 생성 (generated_code)
  ← 사용자 피드백 (FeedbackLogs)
```

---

## 금지 사항

- 단일 JSONB 필드에 모든 데이터 혼재
- 버전 관리 없는 덮어쓰기
- 타입 명세 없는 JSONB 사용

---

_작성 에이전트: Data Agent_
_최종 수정: 2026-03-26_
