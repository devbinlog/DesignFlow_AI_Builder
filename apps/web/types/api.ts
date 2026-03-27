// API 공통 응답 타입

export interface ApiError {
  error: {
    code: string
    message: string
    detail?: Record<string, unknown>
  }
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed'
