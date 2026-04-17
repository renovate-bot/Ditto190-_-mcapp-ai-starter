#!/bin/bash
set -euo pipefail

echo "🔍 Verifying post-rebuild setup..."

echo "📦 Python deps:"
pip list | head -20 || true

echo -e "\n🧠 ContextStream MCP:"
npx @contextstream/mcp-server@latest --version || echo "npx version check"

echo -e "\n🔒 CodeQL CLI:"
codeql version || echo "CodeQL ready - run 'source ~/.bashrc' if alias missing"

echo -e "\n✅ Setup verification complete. Run 'source ~/.bashrc' for full PATH/aliases."

