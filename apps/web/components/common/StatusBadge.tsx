import { cn } from '@/lib/utils/cn'
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react'
import type { AnalysisStatus } from '@/types/api'

interface StatusBadgeProps {
  status: AnalysisStatus
  className?: string
}

const statusConfig: Record<
  AnalysisStatus,
  { label: string; icon: React.ElementType; className: string }
> = {
  pending: { label: '대기 중', icon: Clock, className: 'bg-zinc-500/15 text-muted-foreground' },
  running: { label: '분석 중', icon: Loader2, className: 'bg-blue-500/15 text-blue-400' },
  completed: { label: '완료', icon: CheckCircle2, className: 'bg-green-500/15 text-green-400' },
  failed: { label: '실패', icon: XCircle, className: 'bg-red-500/15 text-red-400' },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium',
        config.className,
        className
      )}
    >
      <Icon
        size={12}
        className={status === 'running' ? 'animate-spin' : undefined}
      />
      {config.label}
    </span>
  )
}
