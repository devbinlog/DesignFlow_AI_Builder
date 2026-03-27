// 프로젝트 관련 타입

import type { AnalysisStatus } from './api'

export interface Project {
  id: string
  name: string
  description?: string
  analysisCount: number
  createdAt: string
  updatedAt: string
}

export interface ProjectDetail extends Project {
  analyses: {
    id: string
    status: AnalysisStatus
    createdAt: string
  }[]
}

export interface CreateProjectInput {
  name: string
  description?: string
}
