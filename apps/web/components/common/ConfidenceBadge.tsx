import { cn } from '@/lib/utils/cn'
import { AlertTriangle } from 'lucide-react'

interface ConfidenceBadgeProps {
  score: number
  className?: string
}

export function ConfidenceBadge({ score, className }: ConfidenceBadgeProps) {
  const percentage = Math.round(score * 100)

  const variant =
    score >= 0.85
      ? 'high'
      : score >= 0.6
        ? 'medium'
        : 'low'

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium',
        variant === 'high' && 'bg-green-500/15 text-green-400',
        variant === 'medium' && 'bg-yellow-500/15 text-yellow-400',
        variant === 'low' && 'bg-red-500/15 text-red-400',
        className
      )}
    >
      {variant === 'low' && <AlertTriangle size={10} />}
      {percentage}%
    </span>
  )
}
