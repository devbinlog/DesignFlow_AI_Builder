# 10. 디자인 시스템 및 UI

## 목적

이 문서는 DesignFlow AI Builder의 시각적 언어와 UI 컴포넌트 시스템을 정의한다. 색상, 타이포그래피, 간격, 컴포넌트 패턴, 인터랙션을 포함하여 전체 UI의 일관성을 보장한다.

---

## 핵심 결정 사항

### 1. 다크 모드 전용 UI
분석 도구라는 특성상 다크 UI가 더 적합하다. VS Code, Figma와 동일한 다크 테마 전략 채택.

### 2. shadcn/ui 기반 컴포넌트
커스터마이징 가능한 원자 컴포넌트 시스템. 의존성 없이 코드를 소유하는 방식.

### 3. 패널 기반 레이아웃
분석 도구에 특화된 3단 패널 레이아웃 (좌/중/우). 정보 계층을 유지하며 컨텍스트 전환 최소화.

---

## 선택 이유

| 결정 | 이유 |
|------|------|
| 다크 테마 | 코드/토큰 가독성 향상, 개발 도구 친화적 |
| shadcn/ui | 소유 가능한 컴포넌트, Radix 접근성 내장 |
| 패널 레이아웃 | 동시에 여러 정보 레이어 표시 가능 |
| Inter + JetBrains Mono | 가독성 최고, 개발 도구 표준 |

---

## 향후 영향

- 다크/라이트 모드 전환은 CSS 변수 기반으로 향후 추가 용이
- 컴포넌트 토큰 시스템으로 브랜드 색상 변경 시 일괄 적용 가능

---

## 색상 시스템

### 기본 팔레트

```css
/* Background */
--color-bg-base: #0F0F11;
--color-bg-surface: #1A1A1F;
--color-bg-elevated: #222228;
--color-bg-overlay: #2A2A35;

/* Border */
--color-border-default: #2A2A35;
--color-border-subtle: #1F1F25;
--color-border-strong: #3A3A45;

/* Text */
--color-text-primary: #F4F4F5;
--color-text-secondary: #A1A1AA;
--color-text-tertiary: #71717A;
--color-text-disabled: #52525B;

/* Brand */
--color-brand-primary: #6366F1;    /* Indigo 500 */
--color-brand-secondary: #8B5CF6;  /* Violet 500 */
--color-brand-hover: #4F46E5;      /* Indigo 600 */

/* Semantic */
--color-success: #22C55E;
--color-warning: #F59E0B;
--color-error: #EF4444;
--color-info: #3B82F6;

/* Confidence */
--color-confidence-high: #22C55E;
--color-confidence-medium: #F59E0B;
--color-confidence-low: #EF4444;
```

### Tailwind 설정 (tailwind.config.ts)

```ts
theme: {
  extend: {
    colors: {
      background: 'hsl(var(--background))',
      surface: 'hsl(var(--surface))',
      brand: {
        DEFAULT: '#6366F1',
        hover: '#4F46E5',
        secondary: '#8B5CF6',
      },
      confidence: {
        high: '#22C55E',
        medium: '#F59E0B',
        low: '#EF4444',
      }
    }
  }
}
```

---

## 타이포그래피 시스템

### 폰트 패밀리

| 용도 | 폰트 | 특징 |
|------|------|------|
| 일반 텍스트 | Inter | 가독성 최고, 웹 표준 |
| 코드 뷰어 | JetBrains Mono | 개발자 친화적 모노스페이스 |

### 타이포 스케일

| 토큰 | 크기 | 두께 | 용도 |
|------|------|------|------|
| `text-display` | 48px / 3rem | 800 | 히어로 제목 |
| `text-h1` | 32px / 2rem | 700 | 페이지 제목 |
| `text-h2` | 24px / 1.5rem | 600 | 섹션 제목 |
| `text-h3` | 18px / 1.125rem | 600 | 패널 제목 |
| `text-body-lg` | 16px / 1rem | 400 | 본문 대 |
| `text-body` | 14px / 0.875rem | 400 | 본문 기본 |
| `text-caption` | 12px / 0.75rem | 400 | 보조 정보 |
| `text-code` | 13px / 0.8125rem | 400 | 코드 (Mono) |

---

## 간격 시스템

| 토큰 | 값 | Tailwind |
|------|----|---------|
| xs | 4px | `p-1`, `m-1` |
| sm | 8px | `p-2`, `m-2` |
| md | 16px | `p-4`, `m-4` |
| lg | 24px | `p-6`, `m-6` |
| xl | 32px | `p-8`, `m-8` |
| 2xl | 48px | `p-12`, `m-12` |
| 3xl | 64px | `p-16`, `m-16` |

---

## 레이아웃 구조

### 앱 셸 (App Shell)

```
┌─────────────────────────────────────────────────────────┐
│  Header (높이: 56px)                                      │
│  앱 로고 | 브레드크럼              | 전역 액션 버튼       │
├──────┬──────────────────────────────────┬────────────────┤
│ Side │                                  │                │
│ bar  │     메인 콘텐츠 영역              │  (선택적)       │
│      │                                  │  우측 패널     │
│ 240px│     (flex-1)                     │  320px         │
│      │                                  │                │
└──────┴──────────────────────────────────┴────────────────┘
```

### 분석 뷰어 레이아웃

```
┌─────────────────────────────────────────────────────────┐
│  Header: 프로젝트명 | 분석 ID | 상태 | 액션 버튼          │
├──────────┬──────────────────────────────┬───────────────┤
│          │  탭 네비게이션                │               │
│ 노드     │  [토큰] [컴포넌트] [코드]     │  속성 패널    │
│ 트리     │                              │               │
│          │  메인 콘텐츠                  │  선택된 항목  │
│ 280px    │                              │  상세 정보    │
│ 스크롤   │  (flex-1, 스크롤)            │               │
│ 가능     │                              │  320px        │
└──────────┴──────────────────────────────┴───────────────┘
```

---

## 컴포넌트 명세

### ConfidenceBadge

```tsx
// 신뢰도 표시 배지
<ConfidenceBadge score={0.92} />
// → 초록 배지: "92%"

<ConfidenceBadge score={0.65} />
// → 노란 배지: "65%"

<ConfidenceBadge score={0.45} />
// → 빨간 배지: "45%" + 경고 아이콘
```

### StatusBadge

```tsx
<StatusBadge status="completed" />  // → "완료" 초록
<StatusBadge status="running" />    // → "분석 중" 파란 + 스피너
<StatusBadge status="failed" />     // → "실패" 빨간
<StatusBadge status="pending" />    // → "대기 중" 회색
```

### NodeTreeItem

```tsx
// 노드 트리 아이템
<NodeTreeItem
  name="HeroSection"
  type="FRAME"
  confidence={0.92}
  isSelected={true}
  hasChildren={true}
  depth={0}
/>
```

---

## 인터랙션 패턴

### 호버 상태
- 배경: `bg-white/5` (5% 흰색 오버레이)
- 전환: `transition-colors duration-150`

### 선택 상태
- 배경: `bg-brand/10` + 왼쪽 테두리: `border-l-2 border-brand`

### 포커스 상태
- 링: `ring-2 ring-brand ring-offset-2 ring-offset-background`

### 로딩 상태
- 스켈레톤: `animate-pulse bg-surface`
- 스피너: 브랜드 색상 원형 스피너

---

## 아이콘 시스템

- 라이브러리: Lucide Icons
- 크기: 16px (sm), 20px (md), 24px (lg)
- 색상: 텍스트 색상 상속 (`currentColor`)

---

_작성 에이전트: Design Agent_
_최종 수정: 2026-03-26_
