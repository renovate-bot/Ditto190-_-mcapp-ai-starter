import {
  LayoutDashboard,
  Server,
  Activity,
  Settings,
  HardDrive,
} from 'lucide-react'
import { cn } from '@/lib/utils'

type Page = 'status' | 'services'

interface SidebarProps {
  currentPage: Page
  onNavigate: (page: Page) => void
}

interface NavItem {
  id: Page
  label: string
  icon: React.ComponentType<{ className?: string }>
}

const navItems: NavItem[] = [
  { id: 'status', label: 'Codespace Status', icon: LayoutDashboard },
  { id: 'services', label: 'Services', icon: Server },
]

/**
 * Application sidebar.
 *
 * Pattern sourced from:
 * - shadcn-admin layout:   https://github.com/Ditto190/shadcn-admin/tree/main/src/components/layout
 * - shadcn-ui-sidebar-modme: https://github.com/Ditto190/shadcn-ui-sidebar-modme
 *
 * TODO(future-agent): Replace static nav with a dynamic sidebar that reads
 * available pages from a route config, similar to shadcn-admin's
 * `src/components/layout/app-sidebar.tsx`.
 */
export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  return (
    <aside className="flex h-full w-60 flex-col border-r bg-card">
      {/* Brand */}
      <div className="flex items-center gap-2 px-4 py-5">
        <HardDrive className="h-5 w-5 text-primary" />
        <span className="font-semibold text-sm leading-tight">
          mcapp-ai-starter
          <br />
          <span className="text-xs font-normal text-muted-foreground">
            Codespace Dashboard
          </span>
        </span>
      </div>

      <nav className="flex-1 space-y-1 px-2">
        <p className="px-2 py-1.5 text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Navigation
        </p>
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={cn(
                'flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                currentPage === item.id
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </button>
          )
        })}
      </nav>

      {/* Footer links — stubs for future pages */}
      <div className="border-t px-2 py-3 space-y-1">
        {[
          { label: 'Activity Log', icon: Activity },
          { label: 'Settings', icon: Settings },
        ].map(({ label, icon: Icon }) => (
          <button
            key={label}
            disabled
            title="Not implemented yet"
            className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground opacity-50 cursor-not-allowed"
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>
    </aside>
  )
}
