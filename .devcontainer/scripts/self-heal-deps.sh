#!/bin/bash
# self-heal-deps.sh — Detect and repair broken or missing dependencies.
# Covers: npm, Python/uv, Docker images, and .env secrets.
#
# Usage: bash .devcontainer/scripts/self-heal-deps.sh

set -euo pipefail

HEALED=0
FAILED=0

ok()   { echo "  ✅ $*"; }
fix()  { echo "  🔧 $*"; HEALED=$((HEALED+1)); }
fail() { echo "  ❌ $*"; FAILED=$((FAILED+1)); }

section() { echo ""; echo "── $* ──────────────────────────────────"; }

# ── .env secrets ─────────────────────────────────────────────────────────────
section "Environment / .env"
if [ ! -f .env ]; then
  fix "Creating .env from .env.example"
  cp .env.example .env
fi

for key in N8N_ENCRYPTION_KEY N8N_USER_MANAGEMENT_JWT_SECRET; do
  val=$(grep -m1 "^${key}=" .env | cut -d= -f2- | tr -d '"' || true)
  if echo "$val" | grep -qE "^(super-secret|even-more-secret|generate_with|your_|CHANGE_ME|)$|^$"; then
    NEW=$(openssl rand -base64 32)
    # Use Python to safely substitute (avoids sed special-character issues with base64 values)
    python3 -c "
import re, sys
key, new_val = sys.argv[1], sys.argv[2]
with open('.env', 'r') as f:
    content = f.read()
content = re.sub(r'^' + re.escape(key) + r'=.*$', key + '=' + new_val, content, flags=re.MULTILINE)
with open('.env', 'w') as f:
    f.write(content)
" "$key" "$NEW"
    fix "Regenerated secure value for ${key}"
  else
    ok "${key} already set"
  fi
done

# ── npm root ─────────────────────────────────────────────────────────────────
section "npm (root)"
if [ -f package.json ]; then
  if [ ! -d node_modules ] || [ package.json -nt node_modules ]; then
    fix "Running npm install (root)"
    npm install --prefer-offline 2>&1 | tail -3
  else
    ok "node_modules up-to-date"
  fi
fi

# ── npm sub-packages ─────────────────────────────────────────────────────────
section "npm sub-packages"
for pkg_dir in prompt-registry awesome-copilot n8n-dev; do
  if [ -f "${pkg_dir}/package.json" ]; then
    if [ ! -d "${pkg_dir}/node_modules" ] || [ "${pkg_dir}/package.json" -nt "${pkg_dir}/node_modules" ]; then
      fix "Running npm install in ${pkg_dir}/"
      (cd "$pkg_dir" && npm install --prefer-offline 2>&1 | tail -3)
    else
      ok "${pkg_dir}/node_modules up-to-date"
    fi
  fi
done

# ── Python / uv ──────────────────────────────────────────────────────────────
section "Python / uv"
if ! command -v uv &>/dev/null; then
  fix "Installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
ok "uv: $(uv --version)"

for py_dir in GenerateAgents.md generateagents-mcp agentskills/skills-ref; do
  if [ -f "${py_dir}/pyproject.toml" ] || [ -f "${py_dir}/uv.lock" ]; then
    if [ ! -d "${py_dir}/.venv" ]; then
      fix "Creating venv in ${py_dir}/"
      (cd "$py_dir" && uv sync 2>&1 | tail -3)
    else
      ok "${py_dir}/.venv exists"
    fi
  fi
done

# ── Docker images ─────────────────────────────────────────────────────────────
section "Docker images"
for img in n8nio/n8n:latest postgres:16-alpine qdrant/qdrant ollama/ollama:latest; do
  if docker image inspect "$img" &>/dev/null; then
    ok "$img cached"
  else
    fix "Pulling missing image: $img"
    docker pull "$img" 2>&1 | tail -1
  fi
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
echo "  Self-heal: ${HEALED} fixed, ${FAILED} errors"
echo "══════════════════════════════════════════"
[ "$FAILED" -eq 0 ] && exit 0 || exit 1
