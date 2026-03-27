'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { analysisApi } from '@/lib/api/analysis'

export function useAnalysis(analysisId: string) {
  return useQuery({
    queryKey: ['analysis', analysisId],
    queryFn: () => analysisApi.get(analysisId),
    staleTime: 5 * 60 * 1000, // 5분 캐시
    enabled: !!analysisId,
  })
}

export function useAnalysisStatus(analysisId: string, enabled: boolean) {
  return useQuery({
    queryKey: ['analysis-status', analysisId],
    queryFn: () => analysisApi.getStatus(analysisId),
    refetchInterval: (query) => {
      const status = query.state.data?.status
      // 완료되거나 실패하면 폴링 중단
      if (status === 'completed' || status === 'failed') return false
      return 2000 // 2초마다 폴링
    },
    enabled: enabled && !!analysisId,
  })
}

export function useRunAnalysis() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: analysisApi.run,
    onSuccess: (data) => {
      // 분석 목록 캐시 무효화
      queryClient.invalidateQueries({ queryKey: ['analyses'] })
      return data
    },
  })
}
