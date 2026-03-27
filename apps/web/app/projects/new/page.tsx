'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { PageHeader } from '@/components/layout/PageHeader'
import { useCreateProject } from '@/hooks/useProject'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'

export default function NewProjectPage() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const { mutate: createProject, isPending, error } = useCreateProject()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return

    createProject(
      { name: name.trim(), description: description.trim() || undefined },
      {
        onSuccess: (project) => {
          router.push(`/projects/${project.id}`)
        },
      }
    )
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="새 프로젝트"
        description="프로젝트 정보를 입력하고 Figma 분석을 시작하세요"
      />

      <div className="flex-1 p-6">
        <div className="max-w-lg">
          <Link
            href="/projects"
            className="inline-flex items-center gap-1.5 mb-6 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft size={14} />
            프로젝트 목록
          </Link>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-foreground mb-1.5">
                프로젝트 이름 <span className="text-red-600">*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="랜딩 페이지 디자인"
                className="w-full px-3 py-2.5 rounded-lg bg-card border border-border text-sm text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:border-indigo-500 transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-foreground mb-1.5">
                설명 <span className="text-muted-foreground/40">(선택)</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="프로젝트에 대한 간단한 설명..."
                rows={3}
                className="w-full px-3 py-2.5 rounded-lg bg-card border border-border text-sm text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:border-indigo-500 transition-colors resize-none"
              />
            </div>

            {error && (
              <p className="text-xs text-red-600">{error.message}</p>
            )}

            <Button
              type="submit"
              disabled={!name.trim() || isPending}
              className="w-full bg-primary/100 hover:bg-indigo-600 text-white disabled:opacity-50"
            >
              {isPending ? (
                <span className="flex items-center gap-2">
                  <Loader2 size={14} className="animate-spin" />
                  생성 중...
                </span>
              ) : (
                '프로젝트 생성'
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
