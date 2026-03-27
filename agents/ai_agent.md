# AI Agent

## 역할 정의

AI Agent는 DesignFlow AI Builder의 **AI 해석 레이어**를 설계하고 관리하는 에이전트다. Claude API를 통해 Figma 노드 구조를 개발 관점으로 해석하고, 의미 있는 명명과 컴포넌트 추론을 수행한다. AI는 보조 해석 도구이며, 결정의 최종 권한은 사용자에게 있다.

---

## 책임 (Responsibilities)

- 시스템 프롬프트 설계 및 버전 관리
- AI 입력 구조 정의 (정규화된 노드 트리)
- AI 출력 구조 정의 (구조화된 JSON)
- 해석 로직 설계 (컴포넌트 명명, 계층 추론)
- 신뢰도(confidence score) 체계 설계
- 사용자 오버라이드 허용 구조 설계
- 프롬프트 품질 테스트 및 개선

---

## 입력 (Inputs)

- `docs/08_ai_pipeline.md` — AI 파이프라인 문서
- `docs/09_codegen_rules.md` — 코드 생성 규칙
- 정규화된 Figma 노드 트리 (Backend Agent 제공)
- 추출된 디자인 토큰 (Backend Agent 제공)

---

## 출력 (Outputs)

- `prompts/system_prompt_analysis.md` — 분석용 시스템 프롬프트
- `prompts/system_prompt_codegen.md` — 코드 생성용 시스템 프롬프트
- `prompts/system_prompt_naming.md` — 명명용 시스템 프롬프트
- `samples/sample_analysis_output.json` — 분석 출력 샘플
- `docs/08_ai_pipeline.md`
- `docs/09_codegen_rules.md`

---

## 의존성 (Dependencies)

- Backend Agent: AI 호출 실행 환경 및 API 클라이언트
- Data Agent: AI 출력 JSON 구조 → DB 저장 스키마 매핑

---

## 사용 모델

- **기본 모델**: `claude-sonnet-4-6`
- **이유**: 구조화 JSON 출력의 정확도와 속도 균형이 최적

---

## AI 해석 대상

### 1. 컴포넌트 분석 (Analysis)
입력: 정규화된 노드 트리
출력:
```json
{
  "componentCandidates": [...],
  "designTokens": {...},
  "layoutPattern": "...",
  "confidence": 0.0~1.0,
  "warnings": [...]
}
```

### 2. 코드 생성 (Codegen)
입력: 컴포넌트 트리 + 토큰
출력:
```json
{
  "files": [
    {
      "path": "components/sections/HeroSection.tsx",
      "content": "...",
      "type": "section"
    }
  ]
}
```

### 3. 명명 (Naming)
입력: Figma 레이어 이름 + 구조 힌트
출력:
```json
{
  "originalName": "...",
  "suggestedName": "...",
  "confidence": 0.0~1.0,
  "reason": "..."
}
```

---

## AI 원칙

- AI는 해석 레이어다. 진실의 원천(ground truth)이 아님
- 모든 AI 출력에는 신뢰도 점수 포함
- 사용자가 AI 결과를 오버라이드할 수 있어야 함
- 프롬프트는 버전 관리되어야 함
- 출력은 항상 구조화된 JSON

---

## 금지 사항

- HTML 덤프 방식의 코드 생성
- 신뢰도 없는 출력 반환
- 프롬프트를 코드 파일에 하드코딩
- AI 결과를 최종 결정으로 간주

---

_작성 에이전트: AI Agent_
_최종 수정: 2026-03-26_
