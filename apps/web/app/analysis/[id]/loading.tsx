import { LoadingSpinner } from '@/components/common/LoadingSpinner'

export default function AnalysisLoading() {
  return (
    <div className="flex items-center justify-center h-full">
      <LoadingSpinner size={24} label="분석 결과 불러오는 중..." />
    </div>
  )
}
