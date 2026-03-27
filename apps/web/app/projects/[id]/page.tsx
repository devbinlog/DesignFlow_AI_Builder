'use client'

import { useState, use } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/PageHeader'
import { StatusBadge } from '@/components/common/StatusBadge'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { useProject } from '@/hooks/useProject'
import { useRunAnalysis } from '@/hooks/useAnalysis'
import { ArrowLeft, Play, Upload, Loader2, ChevronRight } from 'lucide-react'

interface PageProps {
  params: Promise<{ id: string }>
}

export default function ProjectDetailPage({ params }: PageProps) {
  const { id } = use(params)
  const router = useRouter()
  const { data: project, isLoading } = useProject(id)
  const { mutate: runAnalysis, isPending: isAnalyzing } = useRunAnalysis()

  const [figmaJson, setFigmaJson] = useState('')
  const [jsonError, setJsonError] = useState<string | null>(null)

  const handleAnalyze = () => {
    setJsonError(null)

    let parsed: Record<string, unknown>
    try {
      parsed = JSON.parse(figmaJson)
    } catch {
      setJsonError('유효한 JSON이 아닙니다. Figma에서 JSON을 다시 복사해주세요.')
      return
    }

    runAnalysis(
      { projectId: id, figmaJson: parsed },
      {
        onSuccess: (data) => {
          router.push(`/analysis/${data.id}`)
        },
        onError: (err) => {
          setJsonError(err.message)
        },
      }
    )
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <LoadingSpinner label="프로젝트 불러오는 중..." />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-2">
        <p className="text-sm text-muted-foreground">프로젝트를 찾을 수 없습니다.</p>
        <Link href="/projects" className="text-sm text-indigo-600 hover:text-indigo-500">
          목록으로
        </Link>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title={project.name}
        description={project.description ?? '분석을 시작하려면 Figma JSON을 붙여넣으세요'}
      />

      <div className="flex-1 p-6 overflow-y-auto">
        <Link
          href="/projects"
          className="inline-flex items-center gap-1.5 mb-6 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft size={14} />
          프로젝트 목록
        </Link>

        <div className="grid grid-cols-3 gap-6">
          {/* JSON 업로드 영역 */}
          <div className="col-span-2 space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Upload size={14} className="text-muted-foreground" />
                <h3 className="text-sm font-medium text-foreground">Figma JSON 붙여넣기</h3>
              </div>
              <p className="text-xs text-muted-foreground mb-3">
                Figma에서 프레임을 우클릭 → &quot;Copy/Paste as&quot; → &quot;Copy as JSON&quot;을 선택하세요
              </p>
              <textarea
                value={figmaJson}
                onChange={(e) => {
                  setFigmaJson(e.target.value)
                  setJsonError(null)
                }}
                placeholder='{"document": {"id": "0:0", "name": "Document", ...}}'
                rows={12}
                className="w-full px-3 py-3 rounded-lg bg-card border border-border text-xs text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:border-indigo-500 transition-colors resize-none font-mono"
              />
              {jsonError && (
                <p className="mt-1.5 text-xs text-red-600">{jsonError}</p>
              )}
            </div>

            <Button
              onClick={handleAnalyze}
              disabled={!figmaJson.trim() || isAnalyzing}
              className="bg-primary/100 hover:bg-indigo-600 text-white disabled:opacity-50 inline-flex items-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  분석 중...
                </>
              ) : (
                <>
                  <Play size={14} />
                  AI 분석 시작
                </>
              )}
            </Button>
          </div>

          {/* 분석 이력 */}
          <div>
            <h3 className="text-sm font-medium text-foreground mb-3">분석 이력</h3>
            {project.analyses.length === 0 ? (
              <div className="flex flex-col items-center py-8 gap-2 border border-dashed border-border rounded-xl">
                <p className="text-xs text-muted-foreground">분석 이력이 없습니다</p>
              </div>
            ) : (
              <div className="space-y-2">
                {project.analyses.map((analysis) => (
                  <Link
                    key={analysis.id}
                    href={`/analysis/${analysis.id}`}
                    className="flex items-center justify-between p-3 rounded-lg bg-card border border-border hover:border-border transition-colors group"
                  >
                    <div className="flex items-center gap-2">
                      <StatusBadge status={analysis.status as 'pending' | 'running' | 'completed' | 'failed'} />
                      <span className="text-xs text-muted-foreground">
                        {new Date(analysis.createdAt).toLocaleDateString('ko-KR')}
                      </span>
                    </div>
                    <ChevronRight size={14} className="text-muted-foreground/40 group-hover:text-muted-foreground transition-colors" />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
