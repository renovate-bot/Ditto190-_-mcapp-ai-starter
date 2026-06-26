# Implementation Plan

## Overview

Enhance the memory-guard.sh script for better code quality, maintainability, and resource management effectiveness in Codespaces, focusing on safe handling of idle Docker containers and resource surges without disrupting critical services.

This plan improves the existing lightweight RAM monitor by adding configurable thresholds, graceful shutdown, tiered responses (warn/cache drop/prune/idle stop/compose scale-down), swap/CPU monitoring, and selective Docker actions. It integrates with docker-compose.yml (ollama/n8n heavy services) and session scripts. Changes are backward-compatible, opt-in where risky (e.g., compose management), with dry-run modes and whitelists to prevent breakage. Needed to prevent OOM in multi-service setups (n8n, ollama CPU-intensive).

High-level approach: Modularize into functions, env-var config, signal handling; add idle detection via docker stats/ps; graduated actions preserve postgres/qdrant essentials.

## Types

No type system changes (Bash script).

## Files

Modify one existing file with precise, reversible changes.

- **Existing file to modify**: `/workspaces/mcapp-ai-starter/.devcontainer/scripts/memory-guard.sh`
  - Add config section (env vars with defaults).
  - Enhance functions (log, get_free_pct, drop_caches, compact_docker → selective).
  - Add new functions (below).
  - Wrap main loop with trap/PID file.
  - Preserve all existing logic/behavior.
- **New file**: `/workspaces/mcapp-ai-starter/.devcontainer/scripts/memory-guard.pid` (runtime PID only, auto-clean).
- No deletions/moves/config updates.

## Functions

Add/enhance 8 functions for modularity, safety.

**New functions**:

- `get_free_pct_swap()` (/workspaces/mcapp-ai-starter/.devcontainer/scripts/memory-guard.sh): Returns swap used % from /proc/meminfo; purpose: detect swap pressure.
- `get_cpu_avg()`: Averages top CPU % via `top -bn1`; purpose: high CPU + low mem → surge.
- `is_container_idle()` (name: string → bool): `docker stats --no-stream $1 | awk` checks CPU<1%, no recent logs; purpose: safe stop.
- `prune_idle_containers()`: Lists idle running containers (uptime>1h), stops if !whitelisted; logs dry-run.
- `manage_compose_services()`: If docker-compose.yml & services up, `docker compose --profile cpu scale ollama-cpu=0 n8n=0`; opt-in.
- `notify_low_resources()`: `echo` to VSCode output or `gh codespace status` if available.
- `rotate_log()`: Truncate if >1MB.
- `perform_action(level)`: Switch on 'warn'/'crit'/'panic'; calls appropriate.

**Modified functions**:

- `log()`: Add level prefix (INFO/WARN/CRIT); optional JSON.
- `drop_caches()`: Unchanged but called from perform_action.
- `compact_docker()` → `compact_docker_selective()`: Add image/container filters (no <latest>, label !memory-critical).

**No removed functions**.

## Classes

No class modifications (Bash script).

## Dependencies

No new dependencies (pure Bash/Docker; assumes docker/compose present as per post-create.sh).

Version pins unnecessary.

## Testing

Manual validation in Codespace; no dedicated test file.

- Run `bash .devcontainer/scripts/memory-guard.sh &`; check PID/logs.
- Simulate low mem: stress test or edit thresholds.
- Docker tests: `docker run busybox sleep 3600`; verify idle prune.
- Compose: `docker compose --profile cpu up -d ollama-cpu`; trigger scale-down.
- Edge: No docker → skip; rootless → safe fallbacks.
- Verify: post-create.sh still starts; session-end.sh unaffected.

## Implementation Order

1. Create backup: `cp .devcontainer/scripts/memory-guard.sh .devcontainer/scripts/memory-guard.sh.bak`.
2. Edit memory-guard.sh: Insert config/trap at top; add new functions after existing; refactor main loop.
3. Use edit_file with exact diffs for precision (multiple if needed).
4. Test: Kill old processes (`pkill -f memory-guard`), restart via post-create or manual.
5. Validate logs/PID; attempt_completion with run command.
