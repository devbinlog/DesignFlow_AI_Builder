import Link from 'next/link'
import { Plus, ArrowRight, Cpu } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'

export default function DashboardPage() {
  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="대시보드"
        description="프로젝트를 생성하고 Figma 디자인을 분석하세요"
        actions={
          <Link
            href="/projects/new"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-md bg-primary/100 hover:bg-indigo-600 text-white transition-colors"
          >
            <Plus size={14} />
            새 프로젝트
          </Link>
        }
      />

      <div className="flex-1 p-6">
        <div className="flex flex-col items-center justify-center h-full max-w-md mx-auto text-center gap-6 py-20">
          <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 border border-primary/30">
            <Cpu size={28} className="text-indigo-600" />
          </div>

          <div>
            <h2 className="text-xl font-semibold text-foreground mb-2">
              첫 번째 프로젝트를 시작하세요
            </h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Figma 프레임의 JSON을 붙여넣으면 AI가 디자인 토큰을 추출하고
              React + Tailwind 코드를 생성합니다.
            </p>
          </div>

          <div className="flex flex-col gap-2 w-full">
            <Link
              href="/projects/new"
              className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-primary/100 hover:bg-indigo-600 text-white text-sm font-medium transition-colors"
            >
              <Plus size={16} />
              새 프로젝트 만들기
            </Link>
            <Link
              href="/projects"
              className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-border text-foreground hover:bg-accent hover:text-foreground text-sm font-medium transition-colors"
            >
              프로젝트 목록 보기
              <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
