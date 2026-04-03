#!/bin/bash
set -euo pipefail

echo "🚀 AI Starter Kit - Codespace Setup"
echo "======================================"

# ── 1. Docker ─────────────────────────────────────────────────────────────────
echo "✅ Checking Docker..."
docker --version
docker compose --version

# ── 2. .env file ─────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  echo "📝 Creating .env file from template..."
  cp .env.example .env
  ENCRYPTION_KEY=$(openssl rand -base64 32)
  JWT_SECRET=$(openssl rand -base64 32)
  sed -i "s|N8N_ENCRYPTION_KEY=.*|N8N_ENCRYPTION_KEY=$ENCRYPTION_KEY|" .env
  sed -i "s|N8N_USER_MANAGEMENT_JWT_SECRET=.*|N8N_USER_MANAGEMENT_JWT_SECRET=$JWT_SECRET|" .env
  echo "✅ .env created with auto-generated secrets"
else
  echo "✅ .env already exists"
fi

# ── 3. Python toolchain (uv) ──────────────────────────────────────────────────
echo ""
echo "🐍 Setting up Python toolchain..."
if ! command -v uv &>/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi
echo "  uv: $(uv --version)"

# Install uv-managed python tools globally
uv tool install ruff 2>/dev/null || true
uv tool install black 2>/dev/null || true
echo "✅ Python toolchain ready"

# ── 4. Node / npm ─────────────────────────────────────────────────────────────
echo ""
echo "📦 Checking Node.js..."
node --version
npm --version
echo "✅ Node.js ready"

# ── 5. Git hooks ──────────────────────────────────────────────────────────────
echo ""
echo "🪝 Installing git hooks..."
if [ -f .git-hooks/pre-commit ]; then
  git config core.hooksPath .git-hooks
  chmod +x .git-hooks/pre-commit
  echo "✅ Git hooks installed"
fi

# ── 6. Shared directories ─────────────────────────────────────────────────────
mkdir -p shared logs
chmod 777 shared

# ── 7. Make helper scripts executable ─────────────────────────────────────────
echo ""
echo "🔧 Making scripts executable..."
chmod +x .devcontainer/scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true
echo "✅ Scripts ready"

# ── 8. Start memory guard daemon ─────────────────────────────────────────────
echo ""
echo "🧠 Starting memory guard..."
if [ -f .devcontainer/scripts/memory-guard.sh ]; then
  bash .devcontainer/scripts/memory-guard.sh &
  echo "✅ Memory guard started (PID $!)"
fi

# ── 9. Pre-pull Docker images in the background ───────────────────────────────
echo ""
echo "📡 Pre-pulling Docker images in background..."
(
  docker pull n8nio/n8n:latest &>/dev/null &
  docker pull postgres:16-alpine &>/dev/null &
  docker pull qdrant/qdrant &>/dev/null &
  wait
  echo "✅ Core Docker images ready"
) &
echo "  (images pulling in background — run 'docker images' to check progress)"

# ── 10. Final summary ─────────────────────────────────────────────────────────
echo ""
echo "✅ Codespace Setup Complete!"
echo "======================================"
echo ""
echo "📋 Quick-start commands:"
echo "  Start stack (CPU):   docker compose --profile cpu up -d"
echo "  Health check:        bash .devcontainer/scripts/health-check.sh"
echo "  Self-heal deps:      bash .devcontainer/scripts/self-heal-deps.sh"
echo "  Configure LLMs:      bash .devcontainer/scripts/setup-llm.sh"
echo "  Run tests:           bash scripts/test-runner.sh"
echo ""
echo "  n8n UI:              http://localhost:5678"
echo "  Ollama API:          http://localhost:11434"
echo "  Qdrant API:          http://localhost:6333"
echo "======================================"

