# Shadcn Dashboard Foundation — Agent & Developer Guide

> This document is the primary reference for agents or developers extending the
> Shadcn-based Codespace dashboard introduced in `ui/shadcn-dashboard/`.

---

## Overview

`ui/shadcn-dashboard/` is a minimal **Vite + React + Tailwind CSS + shadcn/ui**
skeleton that will become the Codespace Operations Dashboard for
`mcapp-ai-starter`.

**Current state:** All metrics are mocked. The UI renders fully but has no live
data or working action buttons.

**Goal:** Provide a visual control panel for the Codespace VM so operators can
monitor memory, disk, Docker containers, and service health without dropping to
the terminal.

---

## How It Relates to mcapp-ai-starter

The existing Codespace tooling (which this dashboard will visualise) lives at:

| Script/File | Purpose |
|-------------|---------|
| `.devcontainer/scripts/memory-guard.sh` | Background daemon watching RAM; prunes Docker when critically low |
| `.devcontainer/scripts/health-check.sh` | Comprehensive stack health check (Docker, ports, RAM, toolchain) |
| `.devcontainer/scripts/self-heal-deps.sh` | Repairs broken deps, missing `.env`, Docker images |
| `codespace_agent.py` | Python helper for connecting to n8n / Ollama / Qdrant |
| `docker-compose.yml` | Defines n8n, Ollama, Qdrant, PostgreSQL services |

The dashboard is intended to be a **UI layer on top of these scripts**, not a
replacement. It should:

1. Expose the same metrics the scripts already compute.
2. Allow running the scripts via UI buttons (with result display).
3. Not duplicate the logic — call the scripts via a thin API wrapper.

---

## Shadcn Resource Inventory

### Primary Repos (ordered by relevance)

#### 1. shadcn-admin — `https://github.com/Ditto190/shadcn-admin`
**Stack:** Vite + React 19 + TypeScript + Tailwind v4 + TanStack Router + Recharts

The closest match to this dashboard's tech stack. **Mine this first.**

Key files to copy/adapt:
```
src/components/layout/app-sidebar.tsx     → full collapsible sidebar with groups
src/components/layout/top-nav.tsx         → breadcrumb + search + theme toggle
src/components/theme-switch.tsx           → dark-mode toggle
src/components/profile-dropdown.tsx       → user menu
src/components/command-menu.tsx           → keyboard command palette
src/features/dashboard/                   → dashboard page with Recharts charts
src/features/settings/                    → settings pages pattern
src/hooks/use-mobile.tsx                  → responsive hook
src/components/ui/                        → complete shadcn/ui primitive set
```

**Recharts chart components** in `src/features/dashboard/` are exactly what
is needed for the memory trend chart (Priority 2 in the handover list).

#### 2. shadcn-ui-sidebar-modme — `https://github.com/Ditto190/shadcn-ui-sidebar-modme`
**Stack:** Next.js + Tailwind v3 + shadcn/ui sidebar component

Registry-based sidebar patterns. Useful for:
```
registry/                  → standalone sidebar component variants
src/app/                   → sidebar layout examples with collapsible/nested nav
```

The sidebar component variants here can replace or enhance the current basic
`Sidebar.tsx` in this dashboard.

#### 3. awesome-shadcn-ui-modme — `https://github.com/Ditto190/awesome-shadcn-ui-modme`
**Stack:** Next.js 14 + Tailwind + shadcn/ui showcase

A curated gallery/registry of advanced shadcn components not in the base library.

Useful components to find here:
- Timeline components (for activity log / event history)
- Multi-step forms (for configuration wizard)
- Enhanced data-grid / table patterns
- Chart card components

Check `src/` for component implementations.

#### 4. shadcn-vue-modme — `https://github.com/Ditto190/shadcn-vue-modme`
**Stack:** Vue 3 + Radix Vue

Reference only for non-React implementations. Not directly usable in this
React dashboard, but useful if a Vue version is ever needed (e.g., for a
different Codespace environment).

---

## Proposed API Contract

When a real backend is added, it should expose:

### `GET /api/status`

Returns a `CodespaceStatusData` object (see `src/data/mock-status.ts` for the
TypeScript type definition).

```json
{
  "lastChecked": "2026-04-03T17:40:00.000Z",
  "memory": {
    "totalGb": 8,
    "usedGb": 5.2,
    "freeGb": 2.8,
    "freePct": 35,
    "warnThresholdPct": 20,
    "critThresholdPct": 10
  },
  "disk": {
    "totalGb": 32,
    "usedGb": 14.6,
    "freeGb": 17.4,
    "usedPct": 46
  },
  "docker": {
    "runningContainers": 4,
    "stoppedContainers": 1,
    "imageCount": 12,
    "volumeCount": 5
  },
  "services": [
    {
      "name": "n8n",
      "port": 5678,
      "status": "ok",
      "healthUrl": "http://localhost:5678/healthz",
      "note": "Low-code workflow engine"
    }
  ]
}
```

Data sources for each field:

| Field | Shell command / file |
|-------|----------------------|
| `memory.totalGb` | `awk '/MemTotal/ {print $2}' /proc/meminfo` |
| `memory.freeGb` | `awk '/MemAvailable/ {print $2}' /proc/meminfo` |
| `disk.usedPct` | `df -h / | awk 'NR==2 {print $5}'` |
| `docker.runningContainers` | `docker ps -q | wc -l` |
| `docker.imageCount` | `docker image ls -q | wc -l` |
| `services[].status` | HTTP `fetch(healthUrl)` → ok if 200, else crit |

### `POST /api/action`

```json
{ "command": "health-check" }
```

Accepted commands:

| Command | Script |
|---------|--------|
| `health-check` | `bash .devcontainer/scripts/health-check.sh` |
| `docker-prune` | `docker system prune -f` |
| `stack-restart` | `docker compose restart` |
| `self-heal` | `bash .devcontainer/scripts/self-heal-deps.sh` |

Response: `{ "output": "<stdout>", "exitCode": 0 }`

---

## How Agents Should Interact With the Dashboard

### Querying status

```python
import requests

resp = requests.get("http://localhost:3001/api/status")
data = resp.json()

# Check memory
if data["memory"]["freePct"] < 20:
    print("⚠ Memory low — consider pruning Docker")
```

### Triggering an action

```python
resp = requests.post(
    "http://localhost:3001/api/action",
    json={"command": "docker-prune"}
)
print(resp.json()["output"])
```

### Checking service health

```python
services = data["services"]
unhealthy = [s for s in services if s["status"] != "ok"]
if unhealthy:
    print(f"Unhealthy services: {[s['name'] for s in unhealthy]}")
```

---

## Extending the Dashboard

### Adding a new page

1. Create `src/pages/MyPage.tsx` following the `Services.tsx` stub pattern.
2. Add the page to the `Page` union type in `App.tsx`.
3. Add a nav item in `Sidebar.tsx` `navItems` array.
4. Add a render clause in `App.tsx`.

### Adding a new metric card

1. Add the data field to `CodespaceStatusData` in `src/data/mock-status.ts`.
2. Add mock data in `getMockStatus()`.
3. Add a new `<SummaryCard />` or custom card in `CodespaceStatus.tsx`.
4. Wire real data via the API when ready.

### Adding a Recharts chart

```bash
npm install recharts
```

Then copy the chart pattern from
`shadcn-admin/src/features/dashboard/components/overview.tsx`.

### Installing additional shadcn/ui components

With `components.json` already configured:
```bash
npx shadcn@latest add table
npx shadcn@latest add chart
npx shadcn@latest add dialog
npx shadcn@latest add alert
```

---

## Known Limitations & Open Questions

1. **CORS**: If the metrics API runs on a different port than the Vite dev
   server (`:5173`), CORS headers must be set in the API. Add
   `cors: { origin: 'http://localhost:5173' }` to the Express server or
   equivalent.

2. **Codespace port forwarding**: GitHub Codespaces auto-forwards ports listed
   in `devcontainer.json`. To expose the dashboard publicly, add port `5173`
   (or whichever the API uses) to `.devcontainer/devcontainer.json`:
   ```json
   "forwardPorts": [5173, 5678, 11434, 6333]
   ```

3. **Tailwind v3 vs v4**: This package uses Tailwind v3. The `shadcn-admin`
   fork uses v4 (`@tailwindcss/vite`). Migration is mechanical but involves
   updating imports and config. Decision deferred until the foundation is
   validated.

4. **React version**: This package uses React 19 (matching `shadcn-admin` and
   `examples/basic-server-react`). Downgrading to React 18 should work without
   changes.

5. **No tests**: Unit/E2E tests have not been added. When adding real data
   fetching, add tests for the `getMockStatus()` → real API transition using
   `vitest` + `@testing-library/react`.

---

*Document created: 2026-04-03*
*Package: `ui/shadcn-dashboard/`*
*Author: Copilot Agent*
