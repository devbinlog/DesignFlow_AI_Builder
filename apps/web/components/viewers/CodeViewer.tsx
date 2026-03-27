'use client'

import { useState } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useAnalysisStore } from '@/store/analysisStore'
import { cn } from '@/lib/utils/cn'
import { Copy, Check, FileCode2 } from 'lucide-react'
import type { GeneratedCode } from '@/types/analysis'

interface CodeViewerProps {
  generatedCode: GeneratedCode
}

export function CodeViewer({ generatedCode }: CodeViewerProps) {
  const { selectedFile, setSelectedFile } = useAnalysisStore()
  const [copiedPath, setCopiedPath] = useState<string | null>(null)

  const currentFile =
    generatedCode.files.find((f) => f.path === selectedFile) ??
    generatedCode.files[0]

  const handleCopy = async (content: string, path: string) => {
    await navigator.clipboard.writeText(content)
    setCopiedPath(path)
    setTimeout(() => setCopiedPath(null), 2000)
  }

  return (
    <div className="flex h-full">
      {/* 파일 목록 */}
      <div className="w-56 border-r border-border flex flex-col">
        <div className="px-3 h-[45px] flex items-center border-b border-border">
          <p className="text-[11px] text-muted-foreground uppercase tracking-wider">파일 목록</p>
        </div>
        <ScrollArea className="flex-1">
          <div className="p-1.5 space-y-0.5">
            {generatedCode.files.map((file) => (
              <button
                key={file.path}
                onClick={() => setSelectedFile(file.path)}
                className={cn(
                  'w-full flex items-center gap-2 px-2.5 py-2 rounded-md text-left text-xs transition-colors',
                  (selectedFile ?? generatedCode.files[0]?.path) === file.path
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                )}
              >
                <FileCode2 size={12} className="flex-shrink-0" />
                <span className="truncate">{file.path.split('/').pop()}</span>
              </button>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* 코드 뷰어 */}
      {currentFile && (
        <div className="flex-1 flex flex-col min-w-0">
          {/* 파일 경로 헤더 */}
          <div className="flex items-center justify-between px-4 h-[45px] border-b border-border">
            <p className="text-xs text-muted-foreground font-mono">{currentFile.path}</p>
            <button
              onClick={() => handleCopy(currentFile.content, currentFile.path)}
              className="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              {copiedPath === currentFile.path ? (
                <>
                  <Check size={12} className="text-green-500" />
                  <span className="text-green-500">복사됨</span>
                </>
              ) : (
                <>
                  <Copy size={12} />
                  복사
                </>
              )}
            </button>
          </div>

          {/* 코드 본문 */}
          <ScrollArea className="flex-1">
            <pre className="p-4 text-[13px] leading-relaxed font-mono text-foreground whitespace-pre">
              <code>{currentFile.content}</code>
            </pre>
          </ScrollArea>
        </div>
      )}
    </div>
  )
}
