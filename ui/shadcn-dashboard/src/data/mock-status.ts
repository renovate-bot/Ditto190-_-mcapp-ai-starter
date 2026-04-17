/**
 * mock-status.ts — Static placeholder data for the Codespace dashboard.
 *
 * ⚠️  ALL VALUES HERE ARE HARDCODED MOCKS.
 *
 * TODO(future-agent): Replace this file with a real data-fetching module.
 * Proposed approach:
 *
 *   Option A — Thin HTTP API (recommended)
 *     Run a small Express / FastAPI process inside the Codespace that reads
 *     /proc/meminfo, runs `df -h`, and calls `docker stats --no-stream`.
 *     Expose as GET /api/status on port 3001.
 *     Then use fetch('/api/status') in a React hook (e.g. useQuery from
 *     @tanstack/react-query, version already used in shadcn-admin).
 *
 *   Option B — Shell-script polling
 *     Keep the existing .devcontainer/scripts/health-check.sh and have the
 *     API wrapper execute it with `child_process.exec` or Python subprocess.
 *
 *   Option C — codespace_agent.py extension
 *     Extend codespace_agent.py to expose a /metrics route using FastAPI, then
 *     call it from the React app.
 *
 * Assumption: metrics will be polled every 30 s, matching the CHECK_INTERVAL
 * in .devcontainer/scripts/memory-guard.sh.
 */

export type ServiceStatus = 'ok' | 'warn' | 'crit' | 'unknown'

export interface MemoryMetrics {
  totalGb: number
  usedGb: number
  freeGb: number
  freePct: number
  /** Threshold from memory-guard.sh */
  warnThresholdPct: number
  /** Threshold from memory-guard.sh */
  critThresholdPct: number
}

export interface DiskMetrics {
  totalGb: number
  usedGb: number
  freeGb: number
  usedPct: number
}

export interface DockerMetrics {
  runningContainers: number
  stoppedContainers: number
  imageCount: number
  volumeCount: number
}

export interface ServiceHealth {
  name: string
  port: number
  status: ServiceStatus
  /** URL used for the health check ping */
  healthUrl: string
  note?: string
}

export interface CodespaceStatusData {
  memory: MemoryMetrics
  disk: DiskMetrics
  docker: DockerMetrics
  services: ServiceHealth[]
  lastChecked: string
}

// ---------------------------------------------------------------------------
// MOCK DATA — replace with API call
// ---------------------------------------------------------------------------

/**
 * Returns hardcoded example data.
 *
 * TODO(future-agent): Replace with:
 *   const data = await fetch('/api/status').then(r => r.json())
 */
export function getMockStatus(): CodespaceStatusData {
  return {
    lastChecked: new Date().toISOString(),

    memory: {
      totalGb: 8,
      usedGb: 5.2,
      freeGb: 2.8,
      freePct: 35,
      // These match thresholds in .devcontainer/scripts/memory-guard.sh
      warnThresholdPct: 20,
      critThresholdPct: 10,
    },

    disk: {
      totalGb: 32,
      usedGb: 14.6,
      freeGb: 17.4,
      usedPct: 46,
    },

    docker: {
      runningContainers: 4,
      stoppedContainers: 1,
      imageCount: 12,
      volumeCount: 5,
    },

    services: [
      {
        name: 'n8n',
        port: 5678,
        status: 'ok',
        healthUrl: 'http://localhost:5678/healthz',
        note: 'Low-code workflow engine',
      },
      {
        name: 'Ollama',
        port: 11434,
        status: 'ok',
        healthUrl: 'http://localhost:11434/api/health',
        note: 'Local LLM inference',
      },
      {
        name: 'Qdrant',
        port: 6333,
        status: 'ok',
        healthUrl: 'http://localhost:6333/health',
        note: 'Vector database',
      },
      {
        name: 'PostgreSQL',
        port: 5432,
        status: 'ok',
        healthUrl: 'pg_isready',
        note: 'n8n persistent storage',
      },
      {
        name: 'Shadcn Dashboard',
        port: 5173,
        status: 'ok',
        healthUrl: 'http://localhost:5173',
        note: 'This UI (Vite dev server)',
      },
    ],
  }
}

/** Derive a status colour from a free-memory percentage. */
export function memoryStatusFromPct(
  freePct: number,
  warnThreshold: number,
  critThreshold: number,
): ServiceStatus {
  if (freePct <= critThreshold) return 'crit'
  if (freePct <= warnThreshold) return 'warn'
  return 'ok'
}
