# 04. 프론트엔드 아키텍처

## 목적

이 문서는 DesignFlow AI Builder의 프론트엔드 구조를 정의한다. Next.js App Router 기반의 앱 구조, 상태 관리 전략, 컴포넌트 설계 원칙, API 통신 레이어를 포함한다.

---

## 핵심 결정 사항

### 1. Next.js App Router 채택
- Pages Router 대비 레이아웃 공유, 서버 컴포넌트 활용 용이
- Route Groups를 통한 레이아웃 분리

### 2. 상태 관리 이중화
- 서버 상태: React Query (TanStack Query v5)
- 클라이언트 UI 상태: Zustand

### 3. shadcn/ui 기반 컴포넌트
- 커스터마이징 가능한 컴포넌트 세트
- Radix UI 프리미티브 기반 → 접근성 보장
- Tailwind CSS와 완벽 통합

---

## 선택 이유

| 결정 | 이유 |
|------|------|
| Next.js App Router | 서버 컴포넌트, 스트리밍, 중첩 레이아웃 지원 |
| React Query | 자동 캐싱, 리페치, 낙관적 업데이트 지원 |
| Zustand | 보일러플레이트 없는 간결한 전역 상태 관리 |
| shadcn/ui | 소유권 있는 컴포넌트 (복사-붙여넣기 방식) |

---

## 대안 비교

### 상태 관리
| 라이브러리 | 장점 | 단점 | 선택 |
|-----------|------|------|------|
| Zustand | 간결, 작은 번들 | - | **선택** |
| Redux Toolkit | 강력한 도구 | 보일러플레이트 과다 | 미선택 |
| Jotai | 원자 기반 | 팀 학습 비용 | 미선택 |

### UI 라이브러리
| 라이브러리 | 장점 | 단점 | 선택 |
|-----------|------|------|------|
| shadcn/ui | 커스터마이징, 접근성 | 초기 설정 | **선택** |
| MUI | 완성도 높음 | 디자인 제약 | 미선택 |
| Mantine | 풍부한 컴포넌트 | 의존성 무거움 | 미선택 |

---

## 향후 영향

- App Router 기반으로 향후 서버 액션 활용 용이
- React Query 캐시 전략으로 분석 결과 로컬 캐싱 가능
- shadcn/ui 컴포넌트는 프로젝트 소유 코드이므로 자유롭게 수정 가능

---

## 디렉토리 구조

```
apps/web/
├── app/
│   ├── layout.tsx              # 루트 레이아웃
│   ├── page.tsx                # 대시보드 (/)
│   ├── projects/
│   │   ├── page.tsx            # 프로젝트 목록
│   │   ├── new/
│   │   │   └── page.tsx        # 새 프로젝트 생성
│   │   └── [id]/
│   │       └── page.tsx        # 프로젝트 상세
│   └── analysis/
│       └── [id]/
│           ├── page.tsx        # 분석 결과 뷰어
│           └── loading.tsx     # 로딩 UI
│
├── components/
│   ├── ui/                     # shadcn 원자 컴포넌트
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── tabs.tsx
│   │   └── ...
│   ├── layout/                 # 레이아웃 컴포넌트
│   │   ├── AppShell.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── PanelLayout.tsx
│   ├── panels/                 # 분석 UI 패널
│   │   ├── NodeTreePanel.tsx
│   │   ├── TokenPanel.tsx
│   │   ├── ComponentPanel.tsx
│   │   └── PropertyPanel.tsx
│   ├── viewers/                # 뷰어 컴포넌트
│   │   ├── CodeViewer.tsx
│   │   ├── TokenViewer.tsx
│   │   └── ComponentTreeViewer.tsx
│   └── common/                 # 공통 컴포넌트
│       ├── ConfidenceBadge.tsx
│       ├── StatusBadge.tsx
│       └── LoadingSpinner.tsx
│
├── hooks/
│   ├── useAnalysis.ts          # 분석 관련 훅
│   ├── useProject.ts           # 프로젝트 관련 훅
│   └── useCodeViewer.ts        # 코드 뷰어 훅
│
├── store/
│   ├── analysisStore.ts        # 분석 UI 상태
│   ├── projectStore.ts         # 프로젝트 UI 상태
│   └── uiStore.ts              # 전역 UI 상태
│
├── lib/
│   ├── api/                    # API 클라이언트
│   │   ├── client.ts           # axios/fetch 기반 클라이언트
│   │   ├── projects.ts         # 프로젝트 API
│   │   ├── analysis.ts         # 분석 API
│   │   └── codegen.ts          # 코드 생성 API
│   └── utils/
│       ├── cn.ts               # clsx + tailwind-merge
│       └── format.ts           # 데이터 포맷 유틸
│
└── types/
    ├── api.ts                  # API 응답 타입
    ├── analysis.ts             # 분석 결과 타입
    └── figma.ts                # Figma 노드 타입
```

---

## 상태 관리 전략

### React Query (서버 상태)
```typescript
// 분석 결과 조회
const { data: analysis, isLoading } = useQuery({
  queryKey: ['analysis', analysisId],
  queryFn: () => api.analysis.getById(analysisId),
  staleTime: 5 * 60 * 1000, // 5분 캐시
})

// 분석 실행 (뮤테이션)
const { mutate: runAnalysis } = useMutation({
  mutationFn: api.analysis.run,
  onSuccess: () => queryClient.invalidateQueries(['analysis']),
})
```

### Zustand (클라이언트 UI 상태)
```typescript
// 분석 뷰어 상태
interface AnalysisStore {
  selectedNodeId: string | null
  activeTab: 'tokens' | 'components' | 'code'
  selectedFile: string | null
  setSelectedNodeId: (id: string | null) => void
  setActiveTab: (tab: string) => void
}
```

---

## 라우팅 구조

| 경로 | 컴포넌트 | 설명 |
|------|---------|------|
| `/` | `app/page.tsx` | 대시보드 |
| `/projects` | `app/projects/page.tsx` | 프로젝트 목록 |
| `/projects/new` | `app/projects/new/page.tsx` | 새 프로젝트 |
| `/projects/[id]` | `app/projects/[id]/page.tsx` | 프로젝트 상세 |
| `/analysis/[id]` | `app/analysis/[id]/page.tsx` | 분석 결과 뷰어 |

---

## TypeScript 설정

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

_작성 에이전트: Frontend Agent_
_최종 수정: 2026-03-26_
