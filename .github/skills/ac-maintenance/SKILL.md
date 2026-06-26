---
name: ac-maintenance
description: >
  Run dependency updates, lint fixes, and cleanup tasks for the awesome-copilot library.
  Use when asked to update dependencies, run npm audit, fix lint errors, clean up dead code,
  update package versions, run Renovate checks, or keep the project healthy and up-to-date.
  Triggers: 'update dependencies', 'npm audit', 'fix lint', 'cleanup', 'renovate',
  'dependency health', 'npm outdated', 'housekeeping', 'upgrade packages'.
---

# AC Maintenance Skill

Keep the awesome-copilot library healthy: dependency updates, lint fixes, and cleanup.

## When to Use This Skill

- Running `npm audit` to check for security vulnerabilities
- Updating outdated packages
- Fixing ESLint or TypeScript errors
- Removing dead code or stale files
- Running Renovate-triggered changes

## Step-by-Step Workflows

### Check dependency health

```bash
cd /workspaces/mcapp-ai-starter/awesome-copilot
npm audit
npm outdated
```

### Fix audit vulnerabilities

```bash
npm audit fix              # safe fixes only
npm audit fix --force      # ONLY with user confirmation (can break)
```

### Lint check

```bash
npm run lint 2>/dev/null || echo "No lint script available"
```

### Update a specific dependency

```bash
npm install <package>@latest --save-dev
npm ci  # reinstall from updated lock
```

### Python dependency audit (GenerateAgents.md)

```bash
cd /workspaces/mcapp-ai-starter/GenerateAgents.md
uv sync --extra dev
uv run pip-audit 2>/dev/null || pip install pip-audit && uv run pip-audit
```

## Key Rules

- ALWAYS use `npm ci` (not `npm install`) to install from the lock file
- Commit `package-lock.json` when updating dependencies
- After updates, run `npm run build` and `npm run skill:validate` to verify
- Python: always `uv run`, never `pip` direct
- NEVER use `npm audit fix --force` without explicit user approval
