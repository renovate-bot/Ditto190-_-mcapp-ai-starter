#!/bin/bash
set -euo pipefail

echo "🔧 Pre-install setup"
echo "===================="

echo "✅ Checking GitHub CLI..."
if ! command -v gh >/dev/null 2>&1; then
  echo "❌ gh not found (devcontainer github-cli feature may have failed)"
  exit 1
fi

echo "  gh: $(gh --version | head -n 1)"

echo "🔐 Configuring GitHub CLI auth (non-interactive when token is available)..."
if gh auth status >/dev/null 2>&1; then
  echo "✅ gh already authenticated"
else
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    printf '%s' "$GITHUB_TOKEN" | gh auth login --hostname github.com --with-token || true
  elif [ -n "${GH_TOKEN:-}" ]; then
    printf '%s' "$GH_TOKEN" | gh auth login --hostname github.com --with-token || true
  else
    echo "ℹ️ No GH token found in env; skipping non-interactive auth"
  fi
fi

gh auth setup-git >/dev/null 2>&1 || true

echo "✅ Pre-install complete"
