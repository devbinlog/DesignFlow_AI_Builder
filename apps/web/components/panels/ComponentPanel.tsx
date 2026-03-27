'use client'

import { ScrollArea } from '@/components/ui/scroll-area'
import { ConfidenceBadge } from '@/components/common/ConfidenceBadge'
import { useAnalysisStore } from '@/store/analysisStore'
import { cn } from '@/lib/utils/cn'
import { ChevronRight, Layers, Square, LayoutGrid, Repeat2 } from 'lucide-react'
import type { ComponentCandidate } from '@/types/analysis'

interface ComponentPanelProps {
  candidates: ComponentCandidate[]
}

const typeIcon: Record<string, React.ElementType> = {
  section: Layers,
  card: Square,
  layout: LayoutGrid,
  ui: Square,
  unknown: Square,
}

function ComponentItem({
  candidate,
  depth,
}: {
  candidate: ComponentCandidate
  depth: number
}) {
  const { selectedNodeId, setSelectedNodeId } = useAnalysisStore()
  const isSelected = selectedNodeId === candidate.nodeId
  const Icon = typeIcon[candidate.componentType] ?? Square

  return (
    <div>
      <button
        onClick={() => setSelectedNodeId(candidate.nodeId)}
        className={cn(
          'w-full flex items-center gap-2 px-3 py-2 text-left transition-colors rounded-md text-sm',
          isSelected
            ? 'bg-primary/10 text-foreground border-l-2 border-primary'
            : 'text-muted-foreground hover:text-foreground hover:bg-accent',
        )}
        style={{ paddingLeft: `${(depth * 16) + 12}px` }}
      >
        <Icon size={13} className="flex-shrink-0" />
        <span className="flex-1 truncate text-xs">{candidate.suggestedName}</span>
        {candidate.isRepeating && (
          <Repeat2 size={11} className="text-primary flex-shrink-0" aria-label="반복 구조" />
        )}
        <ConfidenceBadge score={candidate.confidence} />
        <ChevronRight size={11} className="flex-shrink-0 text-muted-foreground/40" />
      </button>

      {candidate.children?.map((child) => (
        <ComponentItem key={child.nodeId} candidate={child} depth={depth + 1} />
      ))}
    </div>
  )
}

export function ComponentPanel({ candidates }: ComponentPanelProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="px-4 h-[45px] flex items-center border-b border-border">
        <p className="text-xs text-muted-foreground">{candidates.length}개의 컴포넌트 식별됨</p>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-0.5">
          {candidates.map((candidate) => (
            <ComponentItem key={candidate.nodeId} candidate={candidate} depth={0} />
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}
