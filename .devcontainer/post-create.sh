#!/bin/bash
set -euo pipefail

echo "🚀 AI Starter Kit - Codespace Setup"
echo "======================================"

# ── 1. Docker ─────────────────────────────────────────────────────────────────
echo "✅ Checking Docker..."
if command -v docker &>/dev/null; then
  docker --version
  docker compose --version || true
else
  echo "⚠️ Docker not found; skipping Docker checks"
fi

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

# ── NEW: Install Python deps from requirements.txt ────────────────────────────
echo ""
echo "📦 Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt
echo "✅ Python deps installed"

# ── 4. Node / npm ─────────────────────────────────────────────────────────────
echo ""
echo "📦 Checking Node.js..."
node --version
npm --version
echo "✅ Node.js ready"

# ── 4.5 Nix (Determinate installer) ───────────────────────────────────────────
echo ""
echo "❄️ Setting up Nix..."
if ! command -v nix &>/dev/null; then
  curl -fsSL https://install.determinate.systems/nix | sh -s -- install --no-confirm
fi

# Ensure nix profile is loaded in current shell (installer can require this)
if [ -e "/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh" ]; then
  # shellcheck disable=SC1091
  . "/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh"
elif [ -e "$HOME/.nix-profile/etc/profile.d/nix.sh" ]; then
  # shellcheck disable=SC1090
  . "$HOME/.nix-profile/etc/profile.d/nix.sh"
fi

if command -v nix &>/dev/null; then
  echo "  nix: $(nix --version)"
  mkdir -p "$HOME/.config/nix"
  if [ ! -f "$HOME/.config/nix/nix.conf" ] || ! grep -q "^experimental-features = .*flakes" "$HOME/.config/nix/nix.conf"; then
    {
      echo "experimental-features = nix-command flakes"
    } >> "$HOME/.config/nix/nix.conf"
  fi
  echo "✅ Nix ready"
else
  echo "⚠️ Nix install did not complete in this shell; restart terminal after rebuild."
fi

# ── NEW: ContextStream MCP setup ──────────────────────────────────────────────
echo ""
echo "🧠 Setting up ContextStream MCP..."
# Use npx to run the setup and init commands to avoid relying on a global binary
npx @contextstream/mcp-server@latest setup || true
npx @contextstream/mcp-server@latest init --folder-path="$(pwd)" || true
echo "✅ ContextStream MCP ready"

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

# ── NEW: Lightweight CodeQL CLI setup ─────────────────────────────────────────
echo ""
echo "🔒 Setting up lightweight CodeQL CLI..."
if [ ! -d ~/codeql ]; then
  wget -q https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
  unzip -q codeql-linux64.zip
  rm codeql-linux64.zip
  mv codeql ~/codeql
  echo 'export PATH="$HOME/codeql:$PATH"' >> "$HOME/.bashrc"
  export PATH=\"$HOME/codeql:$PATH\"
fi
echo 'alias codeql-analyze=\"codeql database create --overwrite --source-root=. codeql-db && codeql database analyze codeql-db --format=sarif-latest --output=results.sarif security-and-quality\"' >> ~/.bashrc
echo "✅ CodeQL CLI ready (run 'codeql-analyze' or source ~/.bashrc)"

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
echo "✅ Codespace Setup Complete! (with pip deps, ContextStream MCP, CodeQL)"
echo "======================================"
echo ""
echo "📋 Quick-start commands:"
echo "  Start stack (CPU):   docker compose --profile cpu up -d"
echo "  Health check:        bash .devcontainer/scripts/health-check.sh"
echo "  Self-heal deps:      bash .devcontainer/scripts/self-heal-deps.sh"
echo "  Configure LLMs:      bash .devcontainer/scripts/setup-llm.sh"
echo "  Run tests:           bash scripts/test-runner.sh"
echo "  CodeQL analyze:      codeql-analyze"
echo "  ContextStream search: mcp_contextstream_search(query=\\\"your query\\\")"
echo ""
echo "  n8n UI:              http://localhost:5678"
echo "  Ollama API:          http://localhost:11434"
echo "  Qdrant API:          http://localhost:6333"
echo "======================================"
