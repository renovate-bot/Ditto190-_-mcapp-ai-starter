import { RefreshCw, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'

/**
 * Top application header.
 *
 * TODO(future-agent): Add:
 * - Dark-mode toggle (see shadcn-admin `src/components/theme-switch.tsx`)
 * - Last-refreshed timestamp driven by real poll interval
 * - User profile dropdown (see shadcn-admin `src/components/profile-dropdown.tsx`)
 */
export function Header() {
  return (
    <header className="flex h-14 items-center justify-between border-b px-6">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Codespace Operations</span>
        <span className="rounded bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
          ⚠ Mocked data
        </span>
      </div>

      <div className="flex items-center gap-2">
        {/* TODO(future-agent): Wire this button to re-fetch metrics from the
            /api/status endpoint. See docs/shadcn-dashboard-foundation.md for
            the proposed API shape. */}
        <Button
          variant="outline"
          size="sm"
          disabled
          title="Auto-refresh not yet implemented"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh
        </Button>

        <a
          href="https://github.com/Ditto190/mcapp-ai-starter"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
        >
          <ExternalLink className="h-3.5 w-3.5" />
          Repo
        </a>
      </div>
    </header>
  )
}
