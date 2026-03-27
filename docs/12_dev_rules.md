# 12. 개발 규칙

## 목적

이 문서는 DesignFlow AI Builder 개발 과정에서 모든 에이전트와 개발자가 준수해야 하는 코딩 규칙, 컨벤션, 워크플로우를 정의한다.

---

## 핵심 결정 사항

### 1. 문서 우선 원칙
코드 작성 전 반드시 해당 모듈의 문서가 작성되어야 한다.

### 2. 단일 책임 원칙
각 파일/모듈은 하나의 명확한 책임만 가진다.

### 3. 명시적 타입
TypeScript와 Pydantic을 통해 모든 데이터 구조를 명시적으로 타입화한다.

---

## 선택 이유

이 규칙들은 포트폴리오 품질의 코드베이스를 유지하고, 향후 확장 시 혼란을 방지하기 위해 설정되었다.

---

## 향후 영향

규칙이 문서화되어 있으므로 팀 확장 시 온보딩 비용 최소화 가능.

---

## 대안 비교

N/A — 개발 규칙은 선택이 아닌 표준화 문서.

---

## 공통 규칙

### 금지 사항
- [ ] 문서 없이 코드 작성
- [ ] `any` 타입 사용 (TypeScript)
- [ ] 비즈니스 로직을 UI 컴포넌트에 포함
- [ ] 시크릿을 코드에 하드코딩
- [ ] 플레이스홀더 구현 ("나중에 고치기")
- [ ] 과도한 주석 (코드가 자명해야 함)
- [ ] 단일 파일 1000줄 초과

### 의무 사항
- [ ] 모든 공개 함수에 타입 명시
- [ ] 에러는 명확한 메시지와 함께 처리
- [ ] 새 기능은 해당 문서 업데이트 후 구현
- [ ] 환경 변수는 `.env.example`에 즉시 추가

---

## 프론트엔드 규칙 (Next.js / TypeScript)

### 파일 네이밍
```
컴포넌트:  PascalCase.tsx          예) HeroSection.tsx
훅:        use + camelCase.ts      예) useAnalysis.ts
스토어:    camelCase + Store.ts    예) analysisStore.ts
유틸:      camelCase.ts            예) formatDate.ts
타입:      camelCase.ts            예) analysis.ts
```

### 컴포넌트 구조
```tsx
// 1. 임포트 (외부 → 내부)
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useAnalysis } from '@/hooks/useAnalysis'
import type { AnalysisResult } from '@/types/analysis'

// 2. 타입 정의
interface ComponentProps {
  analysisId: string
  onClose: () => void
}

// 3. 컴포넌트 (named export 권장)
export function ComponentName({ analysisId, onClose }: ComponentProps) {
  // 4. 훅 (순서: useState → useRef → 커스텀 훅)
  const [isOpen, setIsOpen] = useState(false)
  const { data } = useAnalysis(analysisId)

  // 5. 핸들러
  const handleClick = () => { ... }

  // 6. 렌더링
  return (
    <div>...</div>
  )
}
```

### 상태 관리 규칙
- 서버 데이터는 React Query만 사용 (로컬 useState 금지)
- UI 상태(열림/닫힘, 선택 등)는 Zustand
- URL에 반영되어야 하는 상태는 searchParams

---

## 백엔드 규칙 (FastAPI / Python)

### 파일 네이밍
```
라우터:    domain_name.py          예) projects.py
서비스:    domain_name_service.py  예) analysis_service.py
모델:      domain_name.py          예) project.py (SQLAlchemy)
스키마:    domain_name.py          예) project.py (Pydantic)
파서:      concept_parser.py       예) figma_parser.py
```

### 함수 규칙
```python
# 타입 힌트 필수
async def get_analysis_by_id(
    analysis_id: UUID,
    db: AsyncSession,
) -> AnalysisRun | None:
    ...

# 독스트링: 복잡한 로직에만 (자명한 함수 불필요)
async def run_pipeline(raw_json: dict) -> AnalysisResult:
    """
    Figma JSON 입력을 받아 전체 분석 파이프라인을 실행합니다.
    파싱 → 정규화 → 토큰 추출 → AI 해석 → 코드 생성
    """
    ...
```

### 에러 처리 규칙
```python
# HTTPException 직접 사용 대신 커스텀 예외 클래스 사용
raise AnalysisNotFoundException(analysis_id=analysis_id)

# 서비스 레이어에서는 도메인 예외 발생
# 라우터 레이어에서 HTTPException으로 변환
```

---

## Git 규칙

### 브랜치 전략
```
main        → 프로덕션 배포 가능 상태
develop     → 개발 통합 브랜치
feature/    → 기능 개발 (feature/ai-pipeline)
fix/        → 버그 수정 (fix/token-extraction)
docs/       → 문서 작업 (docs/api-spec)
```

### 커밋 메시지 컨벤션 (Conventional Commits)
```
feat:     새 기능 추가
fix:      버그 수정
docs:     문서 변경
refactor: 코드 리팩토링 (기능 변경 없음)
test:     테스트 추가/수정
chore:    빌드 설정, 의존성 변경

예시:
feat(api): add figma json parser endpoint
fix(frontend): resolve analysis status polling issue
docs(ai): update system prompt for naming step
```

---

## 코드 리뷰 체크리스트

- [ ] 타입 명시 여부
- [ ] 에러 처리 여부
- [ ] 비즈니스 로직 분리 여부
- [ ] 하드코딩된 값 없음
- [ ] 관련 문서 업데이트 여부
- [ ] 과도한 복잡도 없음

---

_작성 에이전트: Product Agent_
_최종 수정: 2026-03-26_
