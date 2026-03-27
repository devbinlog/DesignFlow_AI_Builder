'use client'

import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { DesignTokens } from '@/types/analysis'

interface TokenPanelProps {
  tokens: DesignTokens
}

export function TokenPanel({ tokens }: TokenPanelProps) {
  return (
    <div className="flex flex-col h-full">
      <Tabs defaultValue="colors" className="flex flex-col h-full">
        <TabsList className="mx-4 mt-4 grid grid-cols-4 bg-secondary border border-border">
          <TabsTrigger value="colors" className="text-xs">색상</TabsTrigger>
          <TabsTrigger value="typography" className="text-xs">타이포</TabsTrigger>
          <TabsTrigger value="spacing" className="text-xs">간격</TabsTrigger>
          <TabsTrigger value="radius" className="text-xs">반경</TabsTrigger>
        </TabsList>

        <ScrollArea className="flex-1">
          {/* 색상 탭 */}
          <TabsContent value="colors" className="mt-0 p-4 space-y-2">
            <p className="text-xs text-muted-foreground mb-3">{tokens.colors.length}개의 색상 발견</p>
            {tokens.colors.map((color) => (
              <div
                key={color.id}
                className="flex items-center gap-3 p-2.5 rounded-lg bg-card border border-border hover:border-border/60 transition-colors"
              >
                <div
                  className="w-8 h-8 rounded-md flex-shrink-0 border border-border"
                  style={{ backgroundColor: color.value }}
                />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-foreground truncate">{color.name}</p>
                  <p className="text-[11px] text-muted-foreground font-mono">{color.value}</p>
                </div>
                <span className="text-[10px] text-muted-foreground/50 flex-shrink-0">×{color.usageCount}</span>
              </div>
            ))}
          </TabsContent>

          {/* 타이포그래피 탭 */}
          <TabsContent value="typography" className="mt-0 p-4 space-y-2">
            <p className="text-xs text-muted-foreground mb-3">{tokens.typography.length}개의 스타일 발견</p>
            {tokens.typography.map((type) => (
              <div
                key={type.id}
                className="p-2.5 rounded-lg bg-card border border-border hover:border-border/60 transition-colors"
              >
                <p className="text-xs font-medium text-foreground mb-1">{type.name}</p>
                <p
                  className="text-foreground mb-1.5"
                  style={{ fontSize: Math.min(type.fontSize, 24), fontWeight: type.fontWeight, lineHeight: 1.3 }}
                >
                  Aa
                </p>
                <div className="flex gap-3">
                  <span className="text-[11px] text-muted-foreground">{type.fontSize}px</span>
                  <span className="text-[11px] text-muted-foreground">w{type.fontWeight}</span>
                  <span className="text-[11px] text-muted-foreground">{type.fontFamily}</span>
                </div>
              </div>
            ))}
          </TabsContent>

          {/* 간격 탭 */}
          <TabsContent value="spacing" className="mt-0 p-4 space-y-2">
            <p className="text-xs text-muted-foreground mb-3">{tokens.spacing.length}개의 간격 발견</p>
            {tokens.spacing.map((sp) => (
              <div
                key={sp.id}
                className="flex items-center gap-3 p-2.5 rounded-lg bg-card border border-border"
              >
                <div
                  className="bg-primary/10 rounded-sm flex-shrink-0"
                  style={{ width: Math.min(sp.value / 2, 80), height: 16 }}
                />
                <div>
                  <p className="text-xs font-medium text-foreground">{sp.value}px</p>
                  <p className="text-[11px] text-muted-foreground font-mono">{sp.tailwindClass}</p>
                </div>
                <p className="text-[11px] text-muted-foreground/50 ml-auto truncate max-w-24">{sp.usageContext}</p>
              </div>
            ))}
          </TabsContent>

          {/* 반경 탭 */}
          <TabsContent value="radius" className="mt-0 p-4 space-y-2">
            <p className="text-xs text-muted-foreground mb-3">{tokens.radius.length}개의 반경 발견</p>
            {tokens.radius.map((r) => (
              <div
                key={r.id}
                className="flex items-center gap-3 p-2.5 rounded-lg bg-card border border-border"
              >
                <div
                  className="w-8 h-8 bg-primary/10 border border-primary/20 flex-shrink-0"
                  style={{ borderRadius: Math.min(r.value, 16) }}
                />
                <div>
                  <p className="text-xs font-medium text-foreground">{r.value}px</p>
                  <p className="text-[11px] text-muted-foreground font-mono">{r.tailwindClass}</p>
                </div>
              </div>
            ))}
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </div>
  )
}
