# 08. AI 파이프라인

## 목적

이 문서는 DesignFlow AI Builder의 AI 해석 레이어 설계를 정의한다. Claude API를 통한 Figma 구조 해석 흐름, 프롬프트 전략, 출력 구조, 신뢰도 시스템을 포함한다.

---

## 핵심 결정 사항

### 1. AI는 해석 레이어 (Interpretation Layer)
AI는 디자인을 "변환"하는 것이 아니라 "해석"한다. 결과는 사용자가 검토하고 수정할 수 있어야 한다.

### 2. 구조화 JSON 출력 강제
Claude의 `response_format` 또는 JSON 모드를 활용하여 항상 파싱 가능한 구조화 JSON 반환. 자유 텍스트 응답 금지.

### 3. 신뢰도 점수 포함
모든 해석 결과에는 0.0~1.0 범위의 신뢰도 점수가 포함된다. 0.6 미만은 경고로 표시.

### 4. 프롬프트 버전 관리
프롬프트는 `/prompts` 디렉토리에 명시적으로 버전 관리되어 코드에 하드코딩되지 않는다.

---

## 선택 이유

| 결정 | 이유 |
|------|------|
| Claude Sonnet 4.6 | 구조화 JSON 출력 일관성, 빠른 응답 속도 |
| 3단계 분리 프롬프트 | 분석/명명/코드생성 각각 최적화 가능 |
| 신뢰도 점수 | 사용자가 결과 신뢰 여부를 판단할 수 있는 근거 제공 |

---

## 대안 비교

| 전략 | 장점 | 단점 | 선택 |
|------|------|------|------|
| 단일 프롬프트 (모두 처리) | 간단 | 복잡도 과다, 품질 낮음 | 미선택 |
| 3단계 분리 프롬프트 | 각 단계 최적화 | API 호출 3회 | **선택** |
| Few-shot 학습 포함 | 품질 향상 | 토큰 비용 증가 | 부분 적용 |

---

## 향후 영향

- 프롬프트 버전 관리로 모델 업그레이드 시 품질 비교 가능
- 신뢰도 로그 축적으로 프롬프트 개선 방향 파악 가능
- 3단계 구조로 향후 각 단계 독립적 모델 교체 가능

---

## AI 파이프라인 흐름

```
정규화된 노드 트리 (normalized_tree)
        │
        ▼
┌─────────────────────┐
│  Step 1: 분석       │  → system_prompt_analysis.md
│  구조 해석          │
│  토큰 확인          │
│  레이아웃 패턴 인식  │
└─────────┬───────────┘
          │ componentCandidates
          ▼
┌─────────────────────┐
│  Step 2: 명명       │  → system_prompt_naming.md
│  컴포넌트명 제안    │
│  파일 경로 제안     │
└─────────┬───────────┘
          │ namedComponents
          ▼
┌─────────────────────┐
│  Step 3: 코드 생성  │  → system_prompt_codegen.md
│  React 컴포넌트     │
│  Tailwind 클래스    │
│  토큰 적용          │
└─────────┬───────────┘
          │ generatedFiles
          ▼
     최종 결과 저장
```

---

## 입력 구조

### Step 1 (분석) 입력
```json
{
  "normalizedTree": {
    "id": "uuid",
    "figmaId": "1:2",
    "name": "Landing Page",
    "type": "FRAME",
    "children": [...],
    ...
  },
  "designTokens": {
    "colors": [...],
    "typography": [...]
  }
}
```

---

## 출력 구조

### Step 1 (분석) 출력
```json
{
  "componentCandidates": [
    {
      "nodeId": "1:23",
      "figmaName": "Hero Frame",
      "componentType": "section",
      "isRepeating": false,
      "confidence": 0.92,
      "reasoning": "루트 레벨 전체 너비 프레임. 헤딩과 CTA 버튼 포함. 랜딩 페이지 히어로 패턴.",
      "children": [...]
    }
  ],
  "layoutPattern": "landing-page",
  "topLevelSections": ["hero", "features", "cta"],
  "warnings": [
    {
      "type": "LOW_CONFIDENCE",
      "nodeId": "1:45",
      "message": "이 프레임의 역할이 명확하지 않습니다. 수동 확인 필요."
    }
  ]
}
```

### Step 2 (명명) 출력
```json
{
  "namedComponents": [
    {
      "nodeId": "1:23",
      "originalName": "Hero Frame",
      "suggestedName": "HeroSection",
      "filePath": "components/sections/HeroSection.tsx",
      "confidence": 0.95,
      "reason": "전형적인 히어로 섹션 패턴. PascalCase 컴포넌트명 적용."
    }
  ]
}
```

### Step 3 (코드 생성) 출력
```json
{
  "files": [
    {
      "path": "app/page.tsx",
      "content": "import HeroSection from '@/components/sections/HeroSection'\n\nexport default function Page() {\n  return (\n    <main>\n      <HeroSection />\n    </main>\n  )\n}",
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
  ]
}
```

---

## 신뢰도 시스템

| 점수 범위 | 표시 | 의미 |
|----------|------|------|
| 0.85 ~ 1.0 | 초록 배지 | 높은 신뢰도 |
| 0.60 ~ 0.84 | 노란 배지 | 보통 신뢰도, 확인 권장 |
| 0.0 ~ 0.59 | 빨간 배지 + 경고 | 낮은 신뢰도, 수동 확인 필수 |

---

## Claude API 호출 설정

```python
response = await client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    system=system_prompt,
    messages=[
        {
            "role": "user",
            "content": f"다음 Figma 노드 구조를 분석하세요:\n\n{json.dumps(input_data)}"
        }
    ]
)
```

---

## 에러 처리

| 상황 | 처리 |
|------|------|
| API 타임아웃 | 1회 재시도 후 실패 처리 |
| 잘못된 JSON 응답 | 구조화 실패로 표시, 부분 결과 반환 |
| 토큰 초과 | 트리 깊이 줄여서 재시도 |
| API 오류 | `AI_SERVICE_ERROR` 코드로 사용자에게 안내 |

---

_작성 에이전트: AI Agent_
_최종 수정: 2026-03-26_
