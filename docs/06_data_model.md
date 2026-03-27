# 06. 데이터 모델

## 목적

이 문서는 DesignFlow AI Builder에서 사용되는 모든 데이터 구조를 정의한다. PostgreSQL 스키마, JSONB 필드 구조, 엔티티 간 관계, 데이터 흐름의 각 단계별 구조를 명확히 한다.

---

## 핵심 결정 사항

### 1. JSONB 기반 유연한 저장
- Figma JSON, 정규화 트리, AI 결과, 코드 생성 결과는 모두 JSONB로 저장
- 스키마 변경에 유연하게 대응 가능
- 단, JSONB 내부 구조는 반드시 문서화하여 명시적으로 관리

### 2. 분석 실행 단위로 버전 관리
- 분석을 실행할 때마다 새로운 `AnalysisRun` 레코드 생성
- 동일 프로젝트에 대해 여러 번 분석 가능 → 이력 추적
- 기존 결과를 덮어쓰지 않음

### 3. 원시 데이터와 처리 데이터 분리
- `raw_input`: 원본 Figma JSON (변경 불가)
- `normalized_tree`: 파싱 후 정규화된 내부 구조
- `ai_interpretation`: AI 해석 결과
- `generated_code`: 최종 코드 파일들

---

## 선택 이유

| 결정 | 이유 |
|------|------|
| JSONB 사용 | Figma JSON 구조가 동적이고 깊음. 컬럼 수백 개보다 JSONB가 현실적 |
| UUID 기본 키 | 분산 환경 확장성, URL 추측 방지 |
| 분석 이력 보존 | 이전 분석과 현재 분석 비교 가능, 피드백 추적 가능 |

---

## 대안 비교

| 접근 방식 | 장점 | 단점 | 선택 |
|----------|------|------|------|
| JSONB 저장 | 유연성, 빠른 개발 | 쿼리 복잡성 | **선택** |
| 완전 정규화 테이블 | 쿼리 용이 | 스키마 유지 비용 높음 | 미선택 |
| MongoDB | 문서 기반 | 트랜잭션 약함 | 미선택 |

---

## 향후 영향

- JSONB GIN 인덱스 추가로 내부 필드 검색 성능 개선 가능
- 분석 이력 보존으로 향후 AI 성능 개선 실험 데이터 활용 가능
- 피드백 로그로 사용자 패턴 분석 가능

---

## 엔티티 관계도 (ERD)

```
Projects
  │ 1
  │ N
  AnalysisRuns ──── (has many) ──── FeedbackLogs
       │
       └── JSONB 필드들:
           raw_input
           normalized_tree
           design_tokens
           ai_interpretation
           generated_code
```

---

## 테이블 스키마

### projects

```sql
CREATE TABLE projects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### analysis_runs

```sql
CREATE TABLE analysis_runs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- 상태값: 'pending' | 'running' | 'completed' | 'failed'

    raw_input           JSONB,          -- 원본 Figma JSON
    normalized_tree     JSONB,          -- 정규화된 노드 트리
    design_tokens       JSONB,          -- 추출된 디자인 토큰
    ai_interpretation   JSONB,          -- AI 해석 결과
    generated_code      JSONB,          -- 생성된 코드 파일들

    error_message       TEXT,           -- 실패 시 에러 메시지
    ai_model_used       VARCHAR(100),   -- 사용된 AI 모델명

    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at          TIMESTAMP WITH TIME ZONE,
    completed_at        TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_analysis_runs_project_id ON analysis_runs(project_id);
CREATE INDEX idx_analysis_runs_status ON analysis_runs(status);
```

### feedback_logs

```sql
CREATE TABLE feedback_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_run_id UUID NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
    target_type     VARCHAR(50) NOT NULL,
    -- 'token_color' | 'token_typography' | 'component_name' | 'code_file'
    target_id       VARCHAR(255) NOT NULL,
    original_value  JSONB NOT NULL,
    user_value      JSONB NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## JSONB 내부 구조 명세

### normalized_tree
```json
{
  "id": "uuid",
  "figmaId": "1:23",
  "name": "Hero Section",
  "type": "FRAME",
  "layoutMode": "VERTICAL",
  "width": 1440,
  "height": 800,
  "fills": [{ "type": "SOLID", "color": { "r": 0.06, "g": 0.06, "b": 0.07 } }],
  "paddingLeft": 80,
  "paddingRight": 80,
  "paddingTop": 120,
  "paddingBottom": 120,
  "itemSpacing": 32,
  "children": [...]
}
```

### design_tokens
```json
{
  "colors": [
    {
      "id": "color-1",
      "name": "Primary Background",
      "value": "#0F0F11",
      "usageCount": 5,
      "cssVariable": "--color-primary-bg"
    }
  ],
  "typography": [
    {
      "id": "type-1",
      "name": "Heading 1",
      "fontFamily": "Inter",
      "fontSize": 48,
      "fontWeight": 700,
      "lineHeight": 1.2,
      "cssClass": "text-5xl font-bold"
    }
  ],
  "spacing": [
    { "id": "sp-1", "value": 80, "tailwindClass": "p-20", "usageContext": "frame padding" }
  ],
  "radius": [
    { "id": "r-1", "value": 12, "tailwindClass": "rounded-xl" }
  ]
}
```

### ai_interpretation
```json
{
  "componentCandidates": [
    {
      "nodeId": "1:23",
      "suggestedName": "HeroSection",
      "componentType": "section",
      "confidence": 0.92,
      "reasoning": "Full-width frame at root level with heading and CTA button. Matches landing page hero pattern.",
      "children": [...]
    }
  ],
  "layoutPattern": "landing-page",
  "warnings": [
    { "type": "LOW_CONFIDENCE", "nodeId": "1:45", "message": "..." }
  ],
  "modelUsed": "claude-sonnet-4-6",
  "processedAt": "2026-03-26T12:00:00Z"
}
```

### generated_code
```json
{
  "files": [
    {
      "path": "app/page.tsx",
      "content": "...",
      "type": "page"
    },
    {
      "path": "components/sections/HeroSection.tsx",
      "content": "...",
      "type": "section"
    },
    {
      "path": "tokens.json",
      "content": "...",
      "type": "tokens"
    }
  ],
  "generatedAt": "2026-03-26T12:00:05Z"
}
```

---

_작성 에이전트: Data Agent_
_최종 수정: 2026-03-26_
