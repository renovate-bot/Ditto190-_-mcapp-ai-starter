import { AlertTriangle, CheckCircle2, XCircle, HelpCircle, Play, Trash2, Activity } from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import {
  getMockStatus,
  memoryStatusFromPct,
  type ServiceStatus,
} from '@/data/mock-status'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function StatusIcon({ status }: { status: ServiceStatus }) {
  switch (status) {
    case 'ok':
      return <CheckCircle2 className="h-4 w-4 text-green-500" />
    case 'warn':
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />
    case 'crit':
      return <XCircle className="h-4 w-4 text-red-500" />
    default:
      return <HelpCircle className="h-4 w-4 text-slate-400" />
  }
}

function statusVariant(
  status: ServiceStatus,
): 'ok' | 'warn' | 'crit' | 'unknown' {
  return status
}

/** Colour the progress bar based on severity. */
function progressIndicatorClass(status: ServiceStatus) {
  switch (status) {
    case 'ok':
      return 'bg-green-500'
    case 'warn':
      return 'bg-yellow-500'
    case 'crit':
      return 'bg-red-500'
    default:
      return 'bg-slate-400'
  }
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

/**
 * CodespaceStatus — main dashboard page.
 *
 * Shows RAM, disk, Docker, and service-health metrics for the mcapp-ai-starter
 * Codespace environment.
 *
 * ⚠️  All metrics on this page are MOCKED. See src/data/mock-status.ts for
 *     the TODO items and proposed real-data wiring.
 *
 * TODO(future-agent): Add a real-time chart for memory trend using Recharts.
 * The shadcn-admin fork already ships Recharts:
 *   https://github.com/Ditto190/shadcn-admin/blob/main/src/features/dashboard/
 *
 * TODO(future-agent): Wire the action buttons to the Codespace scripts:
 *   - "Run Health Check" → exec .devcontainer/scripts/health-check.sh via API
 *   - "Prune Docker"     → exec `docker system prune -f` via API
 *   - "Restart Stack"    → exec `docker compose restart` via API
 */
export function CodespaceStatus() {
  const data = getMockStatus()
  const { memory, disk, docker, services } = data

  const memStatus = memoryStatusFromPct(
    memory.freePct,
    memory.warnThresholdPct,
    memory.critThresholdPct,
  )
  const usedMemPct = Math.round((memory.usedGb / memory.totalGb) * 100)
  const diskStatus: ServiceStatus = disk.usedPct > 85 ? 'crit' : disk.usedPct > 70 ? 'warn' : 'ok'

  return (
    <div className="space-y-6">
      {/* Page heading */}
      <div>
        <h1 className="text-xl font-semibold">Codespace Status</h1>
        <p className="text-sm text-muted-foreground">
          Resource overview for the mcapp-ai-starter Codespace environment.{' '}
          <span className="text-yellow-600 font-medium">All values are mocked.</span>
        </p>
      </div>

      {/* ── Top summary row ──────────────────────────────────────────────── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard
          title="RAM Free"
          value={`${memory.freeGb} GB`}
          sub={`of ${memory.totalGb} GB total`}
          status={memStatus}
        />
        <SummaryCard
          title="Disk Used"
          value={`${disk.usedPct}%`}
          sub={`${disk.usedGb} GB of ${disk.totalGb} GB`}
          status={diskStatus}
        />
        <SummaryCard
          title="Containers"
          value={String(docker.runningContainers)}
          sub={`${docker.stoppedContainers} stopped`}
          status={docker.runningContainers > 0 ? 'ok' : 'unknown'}
        />
        <SummaryCard
          title="Services"
          value={String(services.filter((s) => s.status === 'ok').length)}
          sub={`of ${services.length} healthy`}
          status={
            services.every((s) => s.status === 'ok')
              ? 'ok'
              : services.some((s) => s.status === 'crit')
              ? 'crit'
              : 'warn'
          }
        />
      </div>

      {/* ── Memory & Disk ─────────────────────────────────────────────────── */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Memory */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <StatusIcon status={memStatus} />
              Memory (RAM)
            </CardTitle>
            <CardDescription>
              Thresholds: warn &lt; {memory.warnThresholdPct}% free / crit &lt;{' '}
              {memory.critThresholdPct}% free
              <br />
              <span className="text-xs text-muted-foreground/70">
                Source: .devcontainer/scripts/memory-guard.sh
              </span>
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Used: {memory.usedGb} GB</span>
              <span className="font-medium">{usedMemPct}%</span>
            </div>
            <Progress
              value={usedMemPct}
              indicatorClassName={progressIndicatorClass(memStatus)}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Free: {memory.freeGb} GB ({memory.freePct}%)</span>
              <Badge variant={statusVariant(memStatus)} className="capitalize">
                {memStatus}
              </Badge>
            </div>
            {/* TODO(future-agent): Add Recharts AreaChart for memory trend over time */}
            <p className="text-xs text-muted-foreground border-t pt-2">
              📈 TODO: Memory trend chart (Recharts AreaChart) — see{' '}
              <code className="text-xs bg-muted px-1 rounded">shadcn-admin/src/features/dashboard/</code>
            </p>
          </CardContent>
        </Card>

        {/* Disk */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <StatusIcon status={diskStatus} />
              Disk Usage
            </CardTitle>
            <CardDescription>
              Codespace filesystem (container layer)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Used: {disk.usedGb} GB</span>
              <span className="font-medium">{disk.usedPct}%</span>
            </div>
            <Progress
              value={disk.usedPct}
              indicatorClassName={progressIndicatorClass(diskStatus)}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Free: {disk.freeGb} GB</span>
              <Badge variant={statusVariant(diskStatus)} className="capitalize">
                {diskStatus}
              </Badge>
            </div>
            {/* TODO(future-agent): Add Docker image list breakdown */}
            <p className="text-xs text-muted-foreground border-t pt-2">
              🐳 TODO: Docker image size breakdown — run{' '}
              <code className="text-xs bg-muted px-1 rounded">docker image ls --format json</code>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* ── Docker summary ────────────────────────────────────────────────── */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Docker Summary</CardTitle>
          <CardDescription>
            Container and image counts — pruning frees disk.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 text-sm">
            <Metric label="Running" value={docker.runningContainers} />
            <Metric label="Stopped" value={docker.stoppedContainers} />
            <Metric label="Images" value={docker.imageCount} />
            <Metric label="Volumes" value={docker.volumeCount} />
          </div>
        </CardContent>
      </Card>

      {/* ── Services health table ────────────────────────────────────────── */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Service Health</CardTitle>
          <CardDescription>
            Stack services defined in docker-compose.yml.{' '}
            {/* TODO(future-agent): Replace mock status with real HTTP health pings.
                Use codespace_agent.py health_check() or a dedicated API endpoint. */}
            <span className="text-yellow-600">Status is mocked.</span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="divide-y">
            {services.map((svc) => (
              <div
                key={svc.name}
                className="flex items-center justify-between py-3"
              >
                <div className="flex items-center gap-3">
                  <StatusIcon status={svc.status} />
                  <div>
                    <p className="text-sm font-medium">{svc.name}</p>
                    <p className="text-xs text-muted-foreground">
                      port {svc.port} · {svc.note}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <code className="hidden sm:block text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">
                    {svc.healthUrl}
                  </code>
                  <Badge variant={statusVariant(svc.status)} className="capitalize">
                    {svc.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ── Action panel ──────────────────────────────────────────────────── */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Actions</CardTitle>
          <CardDescription>
            Trigger Codespace management scripts.{' '}
            <span className="text-yellow-600">
              Buttons are disabled — backend wiring not yet implemented.
            </span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* TODO(future-agent): Wire each button to POST /api/action with a
              { command: 'health-check' | 'docker-prune' | 'stack-restart' }
              body. The API should exec the corresponding shell script and
              stream the output back. */}
          <div className="flex flex-wrap gap-3">
            <Button variant="outline" size="sm" disabled>
              <Activity className="h-4 w-4" />
              Run Health Check
            </Button>
            <Button variant="outline" size="sm" disabled>
              <Trash2 className="h-4 w-4" />
              Prune Docker
            </Button>
            <Button variant="outline" size="sm" disabled>
              <Play className="h-4 w-4" />
              Restart Stack
            </Button>
          </div>
          <Separator className="my-4" />
          <p className="text-xs text-muted-foreground">
            These actions map to existing scripts:
            <br />· <code className="bg-muted px-1 rounded">.devcontainer/scripts/health-check.sh</code>
            <br />· <code className="bg-muted px-1 rounded">docker system prune -f</code>
            <br />· <code className="bg-muted px-1 rounded">docker compose restart</code>
            <br />
            See <code className="bg-muted px-1 rounded">docs/shadcn-dashboard-foundation.md</code> for
            the proposed API contract.
          </p>
        </CardContent>
      </Card>

      <p className="text-xs text-muted-foreground text-center pb-2">
        Last checked (mock): {new Date(data.lastChecked).toLocaleTimeString()}
      </p>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function SummaryCard({
  title,
  value,
  sub,
  status,
}: {
  title: string
  value: string
  sub: string
  status: ServiceStatus
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="flex items-center justify-between">
          <span>{title}</span>
          <StatusIcon status={status} />
        </CardDescription>
        <CardTitle className="text-2xl font-bold">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground">{sub}</p>
      </CardContent>
    </Card>
  )
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="text-center rounded-lg bg-muted/50 p-3">
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}
