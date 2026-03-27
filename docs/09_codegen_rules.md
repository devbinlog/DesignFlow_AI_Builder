# 09. 코드 생성 규칙

## 목적

이 문서는 DesignFlow AI Builder가 생성하는 React + Tailwind CSS 코드의 품질 기준과 생성 규칙을 정의한다. 생성된 코드가 실제 사용 가능한 수준이 되도록 제약 조건과 패턴을 명확히 한다.

---

## 핵심 결정 사항

### 1. HTML 덤프 방식 금지
단순히 Figma 노드를 div로 변환하는 방식은 사용하지 않는다. 반복 구조는 `.map()`, 재사용 가능한 단위는 컴포넌트로 분리한다.

### 2. 컴포넌트 파일 분류
- `components/sections/` — 페이지 섹션 (HeroSection, FeatureSection)
- `components/cards/` — 카드 단위 (FeatureCard, TestimonialCard)
- `components/ui/` — 원자 단위 (Button, Badge, Icon)

### 3. Tailwind 클래스 직접 사용
CSS 파일 생성 없이 Tailwind 유틸리티 클래스를 직접 사용한다. 토큰은 `tailwind.config.ts`의 `theme.extend`에 정의한다.

### 4. TypeScript 엄격 모드
생성되는 모든 코드는 TypeScript strict 모드에서 컴파일 에러가 없어야 한다.

---

## 선택 이유

| 결정 | 이유 |
|------|------|
| 컴포넌트 분리 | 실제 코드베이스에서 사용 가능한 수준의 구조 |
| Tailwind 직접 사용 | 스타일 시트 없이 즉시 실행 가능 |
| map() 강제 | 반복 구조를 인식하여 의미 있는 코드 생성 |
| TypeScript strict | 생성 코드 품질 보증 |

---

## 대안 비교

| 방식 | 장점 | 단점 | 선택 |
|------|------|------|------|
| HTML 덤프 | 빠름 | 품질 낮음, 실사용 불가 | 미선택 |
| 컴포넌트 분리 | 실사용 가능 | 복잡도 높음 | **선택** |
| Styled Components | 동적 스타일 용이 | 생성 복잡도 높음 | 미선택 |

---

## 향후 영향

- 컴포넌트 파일 분류 체계가 확립되면 미리보기 시스템 추가 용이
- `tokens.json` 생성으로 향후 다른 도구와 통합 가능
- TypeScript strict 보장으로 생성 코드를 즉시 프로젝트에 통합 가능

---

## 파일 생성 목록

분석 결과에서 생성되는 파일:

```
app/page.tsx                                # 최상위 페이지
components/
  sections/
    HeroSection.tsx
    FeatureSection.tsx
    CTASection.tsx
    FooterSection.tsx
  cards/
    FeatureCard.tsx
    TestimonialCard.tsx
  ui/
    Button.tsx                              # 공통 버튼 (필요 시)
tokens.json                                 # 디자인 토큰
tailwind.config.ts                          # Tailwind 커스텀 토큰 포함
```

---

## 코드 생성 규칙 상세

### 규칙 1: 반복 구조 감지

Figma 노드에서 동일한 구조가 3개 이상 반복되면 `.map()` 패턴 적용:

```tsx
// ❌ 금지
<FeatureCard icon="..." title="빠른 분석" description="..." />
<FeatureCard icon="..." title="AI 해석" description="..." />
<FeatureCard icon="..." title="코드 생성" description="..." />

// ✅ 권장
const features = [
  { icon: "...", title: "빠른 분석", description: "..." },
  { icon: "...", title: "AI 해석", description: "..." },
  { icon: "...", title: "코드 생성", description: "..." },
]

{features.map((feature) => (
  <FeatureCard key={feature.title} {...feature} />
))}
```

### 규칙 2: Props 타입 명시

```tsx
// ✅ 권장
interface FeatureCardProps {
  icon: string
  title: string
  description: string
}

export function FeatureCard({ icon, title, description }: FeatureCardProps) {
  ...
}
```

### 규칙 3: 레이아웃 경고

다음 패턴은 경고와 함께 생성:
- 절대 위치(`position: absolute`)가 많은 경우
- 고정 픽셀 값이 과도한 경우
- Auto Layout이 없는 중첩 구조

```tsx
// 경고 주석 포함
{/* ⚠️ WARNING: 이 컴포넌트는 절대 위치를 사용합니다. 반응형 대응 필요. */}
```

### 규칙 4: 색상 토큰 참조

하드코딩된 색상 대신 CSS 변수 또는 Tailwind 커스텀 색상 사용:

```tsx
// ❌ 금지
<div className="bg-[#6366F1]">

// ✅ 권장 (tailwind.config.ts에 토큰 정의 후)
<div className="bg-primary">
```

### 규칙 5: 컴포넌트 이름 규칙

| 분류 | 패턴 | 예시 |
|------|------|------|
| 섹션 | `[Name]Section` | `HeroSection`, `FeatureSection` |
| 카드 | `[Name]Card` | `FeatureCard`, `PricingCard` |
| 공통 UI | 단일 명사 | `Button`, `Badge`, `Tag` |

---

## Tailwind 클래스 매핑 기준

| Figma 속성 | Tailwind 클래스 |
|-----------|----------------|
| paddingLeft: 80 | `pl-20` |
| paddingTop: 120 | `pt-30` |
| gap/itemSpacing: 32 | `gap-8` |
| borderRadius: 12 | `rounded-xl` |
| fontWeight: 700 | `font-bold` |
| fontSize: 48 | `text-5xl` |
| opacity: 0.5 | `opacity-50` |

---

## 생성 불가 패턴 (경고 처리)

| 패턴 | 처리 |
|------|------|
| 복잡한 gradient 배경 | 주석으로 표시, 수동 구현 안내 |
| 복잡한 마스크/클립 | 주석으로 표시 |
| 벡터 SVG 요소 | `{/* SVG 직접 삽입 필요 */}` 플레이스홀더 |
| 이미지 fill | `<img src="placeholder" />` 생성 |

---

_작성 에이전트: AI Agent_
_최종 수정: 2026-03-26_
