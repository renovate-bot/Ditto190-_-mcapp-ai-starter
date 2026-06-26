# Codespace Shadcn Dashboard — Foundation

> **Status: Foundation / Skeleton** — All metric values are mocked.
> This package lays the UI groundwork for a future, fully-wired Codespace
> Operations Dashboard for `mcapp-ai-starter`.

---

## Table of Contents

1. [Purpose & Scope](#purpose--scope)
2. [Architecture](#architecture)
3. [Shadcn Source Repos](#shadcn-source-repos)
4. [Running Inside a Codespace](#running-inside-a-codespace)
5. [Component Map](#component-map)
6. [What Is NOT Implemented](#what-is-not-implemented)
7. [Assumptions Made](#assumptions-made)
8. [Handover / Next Steps for Agents](#handover--next-steps-for-agents)

---

## Purpose & Scope

This package is a **minimal Vite + React + Tailwind CSS + shadcn/ui skeleton**
designed to be extended into a full Codespace VM status dashboard for the
`mcapp-ai-starter` AI starter kit.

**What it does right now:**

- Displays a multi-card dashboard with RAM, disk, Docker, and service-health
  sections, all driven by **hardcoded mock data**.
- Provides a sidebar navigation shell (Status / Services pages).
- Documents exactly **where** real data should be wired in via inline `TODO`
  comments and this README.

**What it does NOT do:**

- Make any real system calls or API calls.
- Execute or interact with `memory-guard.sh`, `health-check.sh`, or Docker.
- Provide authentication or access control.

---

## Architecture

```
ui/shadcn-dashboard/
├── index.html
├── package.json
├── vite.config.ts          # Vite + @vitejs/plugin-react, port 5173
├── tailwind.config.ts      # Tailwind v3 + shadcn CSS variable tokens
├── components.json         # shadcn/ui CLI config (new-york style, slate base)
├── tsconfig*.json
└── src/
    ├── index.css           # Tailwind directives + shadcn CSS variable @layer
    ├── main.tsx            # React DOM entry
    ├── App.tsx             # Top-level layout (Sidebar + Header + pages)
    ├── lib/
    │   └── utils.ts        # cn() helper (clsx + tailwind-merge)
    ├── data/
    │   └── mock-status.ts  # ⚠ MOCKED data + TypeScript types + TODO comments
    ├── components/
    │   ├── layout/
    │   │   ├── Sidebar.tsx # Nav sidebar
    │   │   └── Header.tsx  # Top bar
    │   └── ui/             # shadcn/ui primitive components
    │       ├── badge.tsx
    │       ├── button.tsx
    │       ├── card.tsx
    │       ├── progress.tsx
    │       └── separator.tsx
    └── pages/
        ├── CodespaceStatus.tsx  # Main dashboard page (mocked metrics)
        └── Services.tsx         # Services page (stub)
```

### How it fits into `mcapp-ai-starter`

```
.devcontainer/scripts/memory-guard.sh  ─┐
.devcontainer/scripts/health-check.sh  ─┤  Future API layer
codespace_agent.py                     ─┘  (POST /api/status, POST /api/action)
                                                │
                                      ui/shadcn-dashboard  ◄── this package
                                         (React + shadcn)
```

---

## Shadcn Source Repos

These four repos (all forks/curations by [@Ditto190](https://github.com/Ditto190))
are the primary upstream sources for components and patterns:

| Repo | Tech | Key Assets |
|------|------|------------|
| [shadcn-admin](https://github.com/Ditto190/shadcn-admin) | Vite + React + TanStack Router | Full admin layout, data tables, dashboard page with Recharts, auth flow, settings, command-menu |
| [shadcn-vue-modme](https://github.com/Ditto190/shadcn-vue-modme) | Vue 3 + Radix Vue | Vue equivalent components — useful as a reference for non-React implementations |
| [awesome-shadcn-ui-modme](https://github.com/Ditto190/awesome-shadcn-ui-modme) | Next.js | Curated shadcn component showcase and registry — good source for advanced component examples |
| [shadcn-ui-sidebar-modme](https://github.com/Ditto190/shadcn-ui-sidebar-modme) | Next.js | Sidebar patterns — collapsible, nested nav, icon-only mode |

### What to mine from each repo

**shadcn-admin** (closest to this package's stack — same Vite + React):
- `src/components/layout/app-sidebar.tsx` → collapsible sidebar with groups
- `src/components/layout/top-nav.tsx` → breadcrumb + search + theme toggle header
- `src/features/dashboard/` → Recharts bar/line/area charts already wired
- `src/components/ui/` → full set of shadcn primitives (dialog, dropdown, table, tooltip …)
- `src/components/theme-switch.tsx` → dark-mode toggle with local-storage persistence
- `src/hooks/use-mobile.tsx` → responsive breakpoint hook

**shadcn-ui-sidebar-modme**:
- `registry/` → standalone sidebar component variants (icon-only, nested)
- `src/` → sidebar with collapsible sections — directly usable for nav expansion

**awesome-shadcn-ui-modme**:
- `src/` → showcases many advanced components not in the base shadcn library
  (timeline, multi-step form, chart cards, data-grid)

**shadcn-vue-modme**:
- Reference only (different framework) — useful if a Vue version of this
  dashboard is ever needed.

---

## Running Inside a Codespace

```bash
# 1. Open the terminal inside your Codespace

# 2. Navigate to this package
cd ui/shadcn-dashboard

# 3. Install dependencies (requires Node ≥18)
npm install

# 4. Start the dev server
npm run dev
# → Listening on http://localhost:5173

# 5. Open the port-forwarded URL in your browser
#    GitHub Codespaces automatically forwards port 5173.
#    Look in the "Ports" tab of VS Code for the forwarded URL.
```

### Production build (optional)

```bash
npm run build
# → dist/ directory with static files

# Serve locally to verify
npm run preview
```

### From the repo root (convenience)

```bash
# Add this alias to your shell or .devcontainer/post-create.sh:
alias start-dashboard="cd ui/shadcn-dashboard && npm install && npm run dev"
```

---

## Component Map

| Component | File | shadcn/ui Reference |
|-----------|------|---------------------|
| `Card` | `src/components/ui/card.tsx` | [ui.shadcn.com/docs/components/card](https://ui.shadcn.com/docs/components/card) |
| `Badge` (+ status variants) | `src/components/ui/badge.tsx` | [ui.shadcn.com/docs/components/badge](https://ui.shadcn.com/docs/components/badge) |
| `Progress` | `src/components/ui/progress.tsx` | [ui.shadcn.com/docs/components/progress](https://ui.shadcn.com/docs/components/progress) |
| `Button` | `src/components/ui/button.tsx` | [ui.shadcn.com/docs/components/button](https://ui.shadcn.com/docs/components/button) |
| `Separator` | `src/components/ui/separator.tsx` | [ui.shadcn.com/docs/components/separator](https://ui.shadcn.com/docs/components/separator) |

To add more shadcn components from the CLI (once `components.json` is present):
```bash
npx shadcn@latest add table
npx shadcn@latest add chart
npx shadcn@latest add dialog
```

---

## What Is NOT Implemented

The following features are **intentionally deferred** to avoid over-building
on unvalidated assumptions:

| Feature | Why Deferred |
|---------|--------------|
| Real RAM/disk metrics | Requires a backend API — see next section |
| Real service health pings | Requires CORS-enabled endpoints or a proxy |
| Docker prune / restart actions | Requires shell execution via API |
| Memory trend chart | Needs real time-series data before adding Recharts |
| Dark-mode toggle | UI affordance exists in shadcn-admin; add when design is validated |
| Auth / access control | Not needed for single-user Codespace; add if multi-user |
| Log streaming | Needs SSE or WebSocket backend |
| Settings / Activity log pages | Sidebar items exist but are disabled stubs |

---

## Assumptions Made

1. **Framework choice: Vite + React + TypeScript**
   Chosen to match `shadcn-admin` (the primary upstream fork) and the existing
   examples in `mcapp-ai-starter/examples/basic-server-react/`.

2. **Tailwind v3 (not v4)**
   `shadcn-admin` uses Tailwind v4 (`@tailwindcss/vite`), but v3 is used here
   for broader stability and simpler `tailwind.config.ts` config. Upgrading
   to v4 is straightforward — update `package.json` deps and switch the Vite
   plugin.

3. **Metric polling interval: 30 seconds**
   Matches `CHECK_INTERVAL=30` in `.devcontainer/scripts/memory-guard.sh`.

4. **API base URL: `http://localhost:3001`**
   Assumed for future backend. Adjust via `VITE_API_BASE` env var.

5. **Single-page app (no router)**
   Simple `useState`-based navigation used instead of TanStack Router (which
   `shadcn-admin` uses) to keep the skeleton minimal and dependency-light.

---

## Handover / Next Steps for Agents

> This section is written for automated agents or human developers picking up
> this work.

### Priority 1 — Wire real metrics

1. Create a thin metrics API. Two options:
   - **Node/Express** in `ui/shadcn-dashboard/server/`:
     ```bash
     # Reads /proc/meminfo, runs `df -h`, runs `docker stats --no-stream`
     node server/index.js  # serves GET /api/status on :3001
     ```
   - **Python/FastAPI** by extending `codespace_agent.py`:
     ```python
     @app.get("/metrics")
     def metrics():
         # read /proc/meminfo, subprocess df, docker stats
     ```

2. Replace `getMockStatus()` in `src/data/mock-status.ts` with a `fetch` call:
   ```ts
   const data = await fetch(import.meta.env.VITE_API_BASE + '/api/status')
                       .then(r => r.json())
   ```

3. Add `@tanstack/react-query` for polling (already in `shadcn-admin`'s deps):
   ```bash
   npm install @tanstack/react-query
   ```

### Priority 2 — Add memory trend chart

Recharts is already in `shadcn-admin`. Copy the dashboard chart pattern:
- `shadcn-admin/src/features/dashboard/components/overview.tsx`
- Use `<AreaChart>` from Recharts with a 5-minute rolling window of RAM samples.
- Store samples in a `useRef` or Zustand store (also already in `shadcn-admin`).

### Priority 3 — Enable action buttons

Wire the "Run Health Check", "Prune Docker", and "Restart Stack" buttons to
`POST /api/action` with `{ command: 'health-check' | 'docker-prune' | 'stack-restart' }`.

Backend executes the corresponding script and streams stdout via SSE or returns
a single JSON result.

### Priority 4 — Expand sidebar pages

Add the disabled sidebar items (Activity Log, Settings) as real pages.
Pattern from `shadcn-admin/src/features/settings/` can be used as a starting
template.

### Priority 5 — Dark-mode toggle

Copy `shadcn-admin/src/components/theme-switch.tsx` and add a
`ThemeProvider` context. Wire the toggle in `Header.tsx`.

---

*Last updated: 2026-04-03 by Copilot Agent*
*Upstream Shadcn repos: see [Shadcn Source Repos](#shadcn-source-repos)*
