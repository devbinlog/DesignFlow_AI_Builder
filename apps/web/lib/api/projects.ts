import { apiClient } from './client'
import type { Project, ProjectDetail, CreateProjectInput } from '@/types/project'
import type { PaginatedResponse } from '@/types/api'

export const projectsApi = {
  list: (params?: { limit?: number; offset?: number }) =>
    apiClient
      .get<PaginatedResponse<Project>>('/projects', { params })
      .then((r) => r.data),

  get: (id: string) =>
    apiClient.get<ProjectDetail>(`/projects/${id}`).then((r) => r.data),

  create: (data: CreateProjectInput) =>
    apiClient.post<Project>('/projects', data).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/projects/${id}`),
}
