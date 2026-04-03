#!/bin/bash
# memory-guard.sh — Lightweight memory monitor daemon for Codespaces.
# Runs in the background and takes action when free memory drops dangerously low,
# preventing OOM crashes that can corrupt the codespace environment.
#
# Usage: bash .devcontainer/scripts/memory-guard.sh &
# Logs:  ~/logs/memory-guard.log

set -euo pipefail

LOG_DIR="${HOME}/logs"
LOG_FILE="${LOG_DIR}/memory-guard.log"
mkdir -p "$LOG_DIR"

# Thresholds (percentage of total RAM that must remain FREE)
WARN_THRESHOLD=20   # warn when free < 20%
CRIT_THRESHOLD=10   # act  when free < 10%
CHECK_INTERVAL=30   # seconds between checks

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

get_free_pct() {
  local total free
  total=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
  free=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
  echo $(( free * 100 / total ))
}

drop_caches() {
  # Drop page cache (safe; kernel reclaims on demand).
  # Opt-in: set MEMORY_GUARD_DROP_CACHES=1 to enable (requires root and a non-restricted kernel).
  if [ "${MEMORY_GUARD_DROP_CACHES:-0}" != "1" ]; then
    log "ℹ️  Cache drop skipped (set MEMORY_GUARD_DROP_CACHES=1 to enable)"
    return
  fi
  if sync && echo 1 > /proc/sys/vm/drop_caches 2>/dev/null; then
    log "🧹 Dropped page cache"
  else
    log "⚠️  Could not drop page cache (may lack kernel privileges)"
  fi
}

compact_docker() {
  # Remove stopped containers and dangling images without touching named volumes.
  docker container prune -f 2>/dev/null | tail -1 | xargs -I{} log "🐳 Docker container prune: {}" || true
  docker image prune -f 2>/dev/null | tail -1 | xargs -I{} log "🐳 Docker image prune: {}" || true
}

log "🛡️  Memory guard started (PID $$) — thresholds: warn=${WARN_THRESHOLD}%, crit=${CRIT_THRESHOLD}%"

while true; do
  FREE_PCT=$(get_free_pct)

  if [ "$FREE_PCT" -lt "$CRIT_THRESHOLD" ]; then
    log "🚨 CRITICAL: only ${FREE_PCT}% RAM free — clearing caches + Docker pruning"
    drop_caches
    compact_docker
  elif [ "$FREE_PCT" -lt "$WARN_THRESHOLD" ]; then
    log "⚠️  WARNING: only ${FREE_PCT}% RAM free — dropping page cache"
    drop_caches
  fi

  sleep "$CHECK_INTERVAL"
done
