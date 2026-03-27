'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils/cn'
import { LayoutGrid, FolderOpen, Settings, Cpu } from 'lucide-react'
import { ThemeToggle } from '@/components/common/ThemeToggle'

const navItems = [
  { href: '/', icon: LayoutGrid, label: '대시보드' },
  { href: '/projects', icon: FolderOpen, label: '프로젝트' },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex flex-col w-[240px] min-h-screen border-r border-border bg-secondary">
      {/* 로고 */}
      <div className="flex items-center gap-2.5 h-14 px-4 border-b border-border">
        <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-primary/10">
          <Cpu size={15} className="text-primary" />
        </div>
        <span className="text-sm font-semibold text-foreground">DesignFlow</span>
      </div>

      {/* 네비게이션 */}
      <nav className="flex flex-col gap-0.5 p-2 flex-1">
        {navItems.map((item) => {
          const isActive =
            item.href === '/'
              ? pathname === '/'
              : pathname.startsWith(item.href)

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary border-l-2 border-primary'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              )}
            >
              <item.icon size={16} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* 하단 */}
      <div className="p-2 border-t border-border space-y-0.5">
        <ThemeToggle />
        <button className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-accent transition-colors w-full">
          <Settings size={16} />
          설정
        </button>
      </div>
    </aside>
  )
}
