// 분석 결과 관련 타입

import type { AnalysisStatus } from './api'

// 디자인 토큰
export interface ColorToken {
  id: string
  name: string
  value: string
  rawValue: { r: number; g: number; b: number; a: number }
  usageCount: number
  cssVariable: string
  tailwindClass: string
  usageNodes: string[]
}

export interface TypographyToken {
  id: string
  name: string
  fontFamily: string
  fontSize: number
  fontWeight: number
  lineHeight: number
  letterSpacing?: number
  tailwindClasses: string
  usageNodes: string[]
}

export interface SpacingToken {
  id: string
  value: number
  tailwindClass: string
  usageContext: string
}

export interface RadiusToken {
  id: string
  value: number
  tailwindClass: string
  usageContext: string
}

export interface DesignTokens {
  colors: ColorToken[]
  typography: TypographyToken[]
  spacing: SpacingToken[]
  radius: RadiusToken[]
}

// 컴포넌트 후보
export interface ComponentCandidate {
  nodeId: string
  figmaName: string
  suggestedName: string
  componentType: 'section' | 'card' | 'ui' | 'layout' | 'unknown'
  filePath?: string
  isRepeating: boolean
  confidence: number
  reasoning: string
  children?: ComponentCandidate[]
  repeatCount?: number
}

export interface Warning {
  type: 'LOW_CONFIDENCE' | 'COMPLEX_LAYOUT' | 'ABSOLUTE_POSITION' | 'MISSING_AUTOLAYOUT'
  nodeId: string
  message: string
}

export interface AiInterpretation {
  componentCandidates: ComponentCandidate[]
  layoutPattern: string
  topLevelSections: string[]
  warnings: Warning[]
  modelUsed: string
  processedAt: string
}

// 코드 생성 결과
export interface GeneratedFile {
  path: string
  type: 'page' | 'section' | 'card' | 'ui' | 'tokens'
  content: string
}

export interface GeneratedCode {
  files: GeneratedFile[]
  generatedAt: string
}

// 분석 실행
export interface AnalysisRun {
  id: string
  projectId: string
  status: AnalysisStatus
  designTokens?: DesignTokens
  aiInterpretation?: AiInterpretation
  generatedCode?: GeneratedCode
  errorMessage?: string
  createdAt: string
  completedAt?: string
}

export interface AnalysisStatusResponse {
  id: string
  status: AnalysisStatus
  currentStep?: string
  progress?: number
}
