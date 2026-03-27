'use client'

import { use, useEffect, useState } from 'react'
import Link from 'next/link'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { PageHeader } from '@/components/layout/PageHeader'
import { StatusBadge } from '@/components/common/StatusBadge'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { TokenPanel } from '@/components/panels/TokenPanel'
import { ComponentPanel } from '@/components/panels/ComponentPanel'
import { CodeViewer } from '@/components/viewers/CodeViewer'
import { useAnalysis, useAnalysisStatus } from '@/hooks/useAnalysis'
import { useAnalysisStore } from '@/store/analysisStore'
import { ArrowLeft, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'

interface PageProps {
  params: Promise<{ id: string }>
}

export default function AnalysisViewerPage({ params }: PageProps) {
  const { id } = use(params)
  const queryClient = useQueryClient()
  const { activeTab, setActiveTab } = useAnalysisStore()
  const [warningsOpen, setWarningsOpen] = useState(true)
  const { data: analysis, isLoading } = useAnalysis(id)

  const isPolling = analysis?.status === 'pending' || analysis?.status === 'running'
  const { data: statusData } = useAnalysisStatus(id, isPolling)

  useEffect(() => {
    if (statusData?.status === 'completed') {
      queryClient.invalidateQueries({ queryKey: ['analysis', id] })
    }
  }, [statusData?.status, id, queryClient])

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <LoadingSpinner label="분석 결과 불러오는 중..." />
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-2">
        <p className="text-sm text-muted-foreground">분석 결과를 찾을 수 없습니다.</p>
        <Link href="/projects" className="text-sm text-indigo-600 hover:text-indigo-500">
          목록으로
        </Link>
      </div>
    )
  }

  // 분석 진행 중 화면
  if (analysis.status === 'pending' || analysis.status === 'running') {
    const stepLabels: Record<string, string> = {
      parsing: '노드 파싱 중',
      normalizing: '정규화 중',
      extracting: '토큰 추출 중',
      ai_interpretation: 'AI 해석 중',
      code_generation: '코드 생성 중',
    }
    const currentLabel =
      statusData?.currentStep
        ? (stepLabels[statusData.currentStep] ?? statusData.currentStep)
        : '분석 준비 중'

    return (
      <div className="flex flex-col items-center justify-center h-full gap-6">
        <LoadingSpinner size={32} />
        <div className="text-center">
          <p className="text-sm font-medium text-foreground mb-1">{currentLabel}...</p>
          {statusData?.progress !== undefined && (
            <div className="w-48 h-1 bg-primary/10 rounded-full mx-auto mt-3">
              <div
                className="h-1 bg-primary/100 rounded-full transition-all duration-500"
                style={{ width: `${statusData.progress}%` }}
              />
            </div>
          )}
        </div>
      </div>
    )
  }

  // 분석 실패 화면
  if (analysis.status === 'failed') {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <AlertTriangle size={32} className="text-red-600" />
        <div className="text-center">
          <p className="text-sm font-medium text-foreground mb-1">분석에 실패했습니다</p>
          <p className="text-xs text-muted-foreground">{analysis.errorMessage ?? '알 수 없는 오류'}</p>
        </div>
        <Link
          href={`/projects/${analysis.projectId}`}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-border text-foreground hover:bg-accent text-sm transition-colors"
        >
          <ArrowLeft size={14} />
          프로젝트로 돌아가기
        </Link>
      </div>
    )
  }

  // 분석 완료 — 결과 뷰어
  return (
    <div className="flex flex-col h-screen">
      <PageHeader
        title="분석 결과"
        description={`분석 ID: ${id.slice(0, 8)}...`}
        actions={
          <div className="flex items-center gap-3">
            <StatusBadge status={analysis.status} />
            <Link
              href={`/projects/${analysis.projectId}`}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              <ArrowLeft size={14} />
              프로젝트
            </Link>
          </div>
        }
      />

      <div className="flex flex-1 overflow-hidden">
        {/* 탭 기반 메인 콘텐츠 */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <Tabs
            value={activeTab}
            onValueChange={(v) => setActiveTab(v as typeof activeTab)}
            className="flex flex-col h-full"
          >
            <div className="px-4 h-[45px] flex items-end border-b border-border">
              <TabsList className="bg-transparent gap-0 p-0 h-auto">
                {[
                  { value: 'tokens', label: '디자인 토큰' },
                  { value: 'components', label: '컴포넌트' },
                  { value: 'code', label: '생성된 코드' },
                ].map((tab) => (
                  <TabsTrigger
                    key={tab.value}
                    value={tab.value}
                    className="px-4 py-2 text-sm rounded-none border-b-2 border-transparent data-[state=active]:border-indigo-500 data-[state=active]:text-foreground text-muted-foreground bg-transparent hover:text-foreground transition-colors"
                  >
                    {tab.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </div>

            <TabsContent value="tokens" className="flex-1 overflow-hidden mt-0">
              {analysis.designTokens ? (
                <TokenPanel tokens={analysis.designTokens} />
              ) : (
                <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
                  토큰 데이터가 없습니다
                </div>
              )}
            </TabsContent>

            <TabsContent value="components" className="flex-1 overflow-hidden mt-0">
              {analysis.aiInterpretation ? (
                <ComponentPanel candidates={analysis.aiInterpretation.componentCandidates} />
              ) : (
                <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
                  컴포넌트 데이터가 없습니다
                </div>
              )}
            </TabsContent>

            <TabsContent value="code" className="flex-1 overflow-hidden mt-0">
              {analysis.generatedCode ? (
                <CodeViewer generatedCode={analysis.generatedCode} />
              ) : (
                <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
                  생성된 코드가 없습니다
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>

        {/* 우측 패널: 경고 */}
        {analysis.aiInterpretation?.warnings &&
          analysis.aiInterpretation.warnings.length > 0 && (
          <div className="w-72 border-l border-border flex flex-col">
            <button
              onClick={() => setWarningsOpen(o => !o)}
              className="px-4 h-[45px] flex items-center justify-between border-b border-border hover:bg-accent transition-colors w-full"
            >
              <div className="flex items-center gap-2">
                <AlertTriangle size={13} className="text-amber-500" />
                <p className="text-xs font-medium text-foreground">
                  경고 {analysis.aiInterpretation.warnings.length}개
                </p>
              </div>
              {warningsOpen ? <ChevronUp size={13} className="text-muted-foreground" /> : <ChevronDown size={13} className="text-muted-foreground" />}
            </button>
            {warningsOpen && (
              <div className="p-3 space-y-2 overflow-y-auto">
                {analysis.aiInterpretation.warnings.map((warning, i) => (
                  <div
                    key={i}
                    className="p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800"
                  >
                    <div className="flex items-center gap-1.5 mb-1">
                      <AlertTriangle size={11} className="text-amber-600" />
                      <span className="text-[11px] font-medium text-amber-600">
                        {warning.type.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <p className="text-[11px] text-muted-foreground">{warning.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
