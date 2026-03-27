import { apiClient } from './client'
import type { AnalysisRun, AnalysisStatusResponse } from '@/types/analysis'
import type { PaginatedResponse } from '@/types/api'

export const analysisApi = {
  run: (data: { projectId: string; figmaJson: Record<string, unknown> }) =>
    apiClient.post<{ id: string; status: string; createdAt: string }>('/analysis', data).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<AnalysisRun>(`/analysis/${id}`).then((r) => r.data),

  getStatus: (id: string) =>
    apiClient.get<AnalysisStatusResponse>(`/analysis/${id}/status`).then((r) => r.data),

  listByProject: (projectId: string) =>
    apiClient
      .get<PaginatedResponse<AnalysisRun>>(`/analysis/project/${projectId}`)
      .then((r) => r.data),
}
