#!/bin/bash
# health-check.sh — Comprehensive stack health check.
# Checks Docker services, ports, Python/Node toolchains, and key files.
#
# Usage: bash .devcontainer/scripts/health-check.sh

set -euo pipefail

PASS=0
FAIL=0

ok()   { echo "  ✅ $*"; PASS=$((PASS+1)); }
warn() { echo "  ⚠️  $*"; }
fail() { echo "  ❌ $*"; FAIL=$((FAIL+1)); }

section() { echo ""; echo "── $* ──────────────────────────────────"; }

# ── Docker ────────────────────────────────────────────────────────────────────
section "Docker"
if docker info &>/dev/null; then
  ok "Docker daemon running"
else
  fail "Docker daemon not available"
fi

if docker compose version &>/dev/null; then
  ok "Docker Compose available"
else
  fail "Docker Compose not available"
fi

# ── Running services ──────────────────────────────────────────────────────────
section "Running containers"
for svc in n8n postgres qdrant; do
  if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${svc}$"; then
    ok "Container '$svc' is running"
  else
    warn "Container '$svc' not running (start with: docker compose --profile cpu up -d)"
  fi
done

# ── Port connectivity ─────────────────────────────────────────────────────────
section "Port connectivity"
check_port() {
  local label=$1 port=$2
  if curl -sf --connect-timeout 3 "http://localhost:${port}" &>/dev/null || \
     curl -sf --connect-timeout 3 "http://localhost:${port}/health" &>/dev/null; then
    ok "${label} (port ${port})"
  else
    warn "${label} not responding on port ${port} (may not be started)"
  fi
}
check_port "n8n"    5678
check_port "Ollama" 11434
check_port "Qdrant" 6333

# ── Toolchain ─────────────────────────────────────────────────────────────────
section "Toolchain"
check_cmd() {
  local cmd=$1 label=${2:-$1}
  if command -v "$cmd" &>/dev/null; then
    ok "${label}: $($cmd --version 2>&1 | head -1)"
  else
    fail "${label} not found in PATH"
  fi
}
check_cmd docker    "Docker"
check_cmd node      "Node.js"
check_cmd npm       "npm"
check_cmd python3   "Python"
check_cmd uv        "uv (Python package manager)"
check_cmd git       "Git"

# ── Key files ─────────────────────────────────────────────────────────────────
section "Key files"
check_file() {
  local path=$1
  if [ -f "$path" ]; then
    ok "$path"
  else
    fail "$path missing"
  fi
}
check_file ".env"
check_file "docker-compose.yml"
check_file "llm.config.json"

# ── Memory ────────────────────────────────────────────────────────────────────
section "Memory"
TOTAL=$(awk '/MemTotal/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)
FREE=$(awk '/MemAvailable/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)
FREE_PCT=$(awk '/MemTotal/{t=$2} /MemAvailable/{a=$2} END{printf "%.0f", a*100/t}' /proc/meminfo)

if [ "$FREE_PCT" -gt 20 ]; then
  ok "RAM: ${FREE}GB free of ${TOTAL}GB (${FREE_PCT}% available)"
elif [ "$FREE_PCT" -gt 10 ]; then
  warn "RAM: ${FREE}GB free of ${TOTAL}GB (${FREE_PCT}% — low, consider stopping unused services)"
else
  fail "RAM: ${FREE}GB free of ${TOTAL}GB (${FREE_PCT}% — critically low!)"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
echo "  Health Check: ${PASS} passed, ${FAIL} failed"
echo "══════════════════════════════════════════"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
