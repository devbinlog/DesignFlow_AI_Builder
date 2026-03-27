# 07. API 명세

## 목적

이 문서는 DesignFlow AI Builder의 REST API 엔드포인트를 명세한다. 각 엔드포인트의 요청/응답 구조, 상태 코드, 에러 처리를 포함한다.

---

## 핵심 결정 사항

### 1. REST 기반 API
- GraphQL 대비 단순하고 캐싱 용이
- Next.js + React Query와의 통합 자연스러움

### 2. 버전 접두사 `/api/v1`
- 향후 호환성 없는 변경 시 `/api/v2` 분리 가능

### 3. 표준 에러 응답 구조
모든 에러는 동일한 형식으로 반환:
```json
{ "error": { "code": "string", "message": "string", "detail": {} } }
```

---

## 선택 이유

| 결정 | 이유 |
|------|------|
| REST | 간단, HTTP 캐싱, 클라이언트 친화적 |
| 버전 접두사 | 향후 API 변경 시 기존 클라이언트 영향 최소화 |
| 표준 에러 형식 | 프론트엔드에서 에러 처리 일관성 확보 |

---

## 향후 영향

- 분석 상태 실시간 조회는 현재 폴링(polling)으로 구현. 향후 SSE/WebSocket으로 전환 가능
- OpenAPI 스키마 자동 생성으로 프론트엔드 타입 자동 동기화 가능

---

## Base URL

```
개발: http://localhost:8000
프로덕션: https://api.designflow.example.com
```

---

## 공통 헤더

```
Content-Type: application/json
Accept: application/json
```

---

## 엔드포인트 목록

### 헬스 체크

#### `GET /api/v1/health`

**응답 200**
```json
{ "status": "ok", "version": "1.0.0" }
```

---

### 프로젝트

#### `GET /api/v1/projects`

프로젝트 목록 조회

**쿼리 파라미터**
| 파라미터 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| limit | int | 20 | 페이지 크기 |
| offset | int | 0 | 오프셋 |

**응답 200**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "My Landing Page",
      "description": "...",
      "analysisCount": 3,
      "createdAt": "2026-03-26T00:00:00Z",
      "updatedAt": "2026-03-26T00:00:00Z"
    }
  ],
  "total": 10,
  "limit": 20,
  "offset": 0
}
```

---

#### `POST /api/v1/projects`

프로젝트 생성

**요청 Body**
```json
{
  "name": "My Landing Page",
  "description": "Optional description"
}
```

**응답 201**
```json
{
  "id": "uuid",
  "name": "My Landing Page",
  "description": "...",
  "createdAt": "2026-03-26T00:00:00Z"
}
```

**에러**
- 422: 이름 누락

---

#### `GET /api/v1/projects/{id}`

프로젝트 상세 조회

**응답 200**
```json
{
  "id": "uuid",
  "name": "My Landing Page",
  "description": "...",
  "analyses": [
    {
      "id": "uuid",
      "status": "completed",
      "createdAt": "2026-03-26T00:00:00Z"
    }
  ],
  "createdAt": "...",
  "updatedAt": "..."
}
```

**에러**
- 404: 프로젝트 없음

---

### 분석

#### `POST /api/v1/analysis`

분석 실행 (파이프라인 시작)

**요청 Body**
```json
{
  "projectId": "uuid",
  "figmaJson": { ... }
}
```

**응답 202 (Accepted)**
```json
{
  "id": "uuid",
  "status": "pending",
  "createdAt": "2026-03-26T00:00:00Z"
}
```

**에러**
- 422: 유효하지 않은 Figma JSON
- 404: 프로젝트 없음

---

#### `GET /api/v1/analysis/{id}`

분석 결과 전체 조회

**응답 200**
```json
{
  "id": "uuid",
  "projectId": "uuid",
  "status": "completed",
  "designTokens": {
    "colors": [...],
    "typography": [...],
    "spacing": [...],
    "radius": [...]
  },
  "aiInterpretation": {
    "componentCandidates": [...],
    "layoutPattern": "landing-page",
    "warnings": [...]
  },
  "generatedCode": {
    "files": [...]
  },
  "createdAt": "...",
  "completedAt": "..."
}
```

**에러**
- 404: 분석 없음

---

#### `GET /api/v1/analysis/{id}/status`

분석 상태 폴링용 경량 엔드포인트

**응답 200**
```json
{
  "id": "uuid",
  "status": "running",
  "currentStep": "ai_interpretation",
  "progress": 75
}
```

---

#### `GET /api/v1/analysis/project/{projectId}`

프로젝트의 분석 이력

**응답 200**
```json
{
  "items": [...],
  "total": 5
}
```

---

### 피드백

#### `POST /api/v1/feedback`

사용자 피드백 제출 (AI 결과 수정)

**요청 Body**
```json
{
  "analysisRunId": "uuid",
  "targetType": "component_name",
  "targetId": "node-1:23",
  "originalValue": { "name": "Frame 1" },
  "userValue": { "name": "HeroSection" }
}
```

**응답 201**
```json
{ "id": "uuid", "createdAt": "..." }
```

---

## 에러 코드 목록

| 코드 | HTTP | 설명 |
|------|------|------|
| `NOT_FOUND` | 404 | 리소스 없음 |
| `VALIDATION_ERROR` | 422 | 요청 검증 실패 |
| `INVALID_FIGMA_JSON` | 422 | Figma JSON 형식 오류 |
| `ANALYSIS_FAILED` | 500 | 파이프라인 실패 |
| `AI_SERVICE_ERROR` | 503 | AI API 호출 실패 |
| `DB_ERROR` | 503 | DB 연결 실패 |

---

_작성 에이전트: Backend Agent_
_최종 수정: 2026-03-26_
