'use client'

import Link from 'next/link'
import { Plus, FolderOpen, ArrowRight } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { StatusBadge } from '@/components/common/StatusBadge'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'
import { useProjects } from '@/hooks/useProject'

export default function ProjectsPage() {
  const { data, isLoading, error } = useProjects()

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="프로젝트"
        description="Figma 분석 프로젝트 목록"
        actions={
          <Link
            href="/projects/new"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-primary/100 hover:bg-indigo-600 text-white text-sm font-medium transition-colors"
          >
            <Plus size={14} />
            새 프로젝트
          </Link>
        }
      />

      <div className="flex-1 p-6">
        {isLoading && (
          <div className="flex justify-center py-20">
            <LoadingSpinner label="프로젝트 불러오는 중..." />
          </div>
        )}

        {error && (
          <div className="flex flex-col items-center py-20 gap-2">
            <p className="text-sm text-red-600">프로젝트를 불러오지 못했습니다.</p>
            <p className="text-xs text-muted-foreground">백엔드 서버가 실행 중인지 확인하세요.</p>
          </div>
        )}

        {data && data.items.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <FolderOpen size={40} className="text-muted-foreground/40" />
            <div className="text-center">
              <p className="text-sm font-medium text-foreground">프로젝트가 없습니다</p>
              <p className="text-xs text-muted-foreground mt-1">새 프로젝트를 만들어 시작하세요.</p>
            </div>
            <Link
              href="/projects/new"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-primary/100 hover:bg-indigo-600 text-white text-sm font-medium transition-colors"
            >
              <Plus size={14} />
              새 프로젝트
            </Link>
          </div>
        )}

        {data && data.items.length > 0 && (
          <div className="grid grid-cols-3 gap-4">
            {data.items.map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                className="group flex flex-col gap-3 p-4 rounded-xl bg-card border border-border hover:border-border transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-primary/10 border border-primary/30">
                    <FolderOpen size={16} className="text-indigo-600" />
                  </div>
                  <ArrowRight size={14} className="text-muted-foreground/40 group-hover:text-muted-foreground transition-colors mt-1" />
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-foreground mb-0.5">{project.name}</h3>
                  {project.description && (
                    <p className="text-xs text-muted-foreground line-clamp-2">{project.description}</p>
                  )}
                </div>

                <div className="flex items-center justify-between mt-auto pt-2 border-t border-border">
                  <span className="text-[11px] text-muted-foreground">
                    분석 {project.analysisCount}회
                  </span>
                  <span className="text-[11px] text-muted-foreground/40">
                    {new Date(project.createdAt).toLocaleDateString('ko-KR')}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
