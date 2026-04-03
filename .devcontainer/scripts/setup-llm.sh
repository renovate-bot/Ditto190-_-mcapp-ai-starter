#!/bin/bash
# setup-llm.sh — Interactive LLM provider configuration wizard.
# Reads llm.config.json and helps the user set API keys in .env.
#
# Usage: bash .devcontainer/scripts/setup-llm.sh

set -euo pipefail

ENV_FILE=".env"
CONFIG_FILE="llm.config.json"

echo ""
echo "🤖 LLM Provider Setup"
echo "══════════════════════════════════════════"
echo ""
echo "This wizard helps you configure LLM providers."
echo "API keys are stored only in your local .env file."
echo ""

if [ ! -f "$ENV_FILE" ]; then
  cp .env.example "$ENV_FILE"
  echo "📝 Created .env from template"
fi

# Helper: set or update a key in .env, safely escaping special characters
set_env_key() {
  local key=$1 value=$2
  # Escape value for use as sed replacement (handles &, /, \, | and newlines)
  local escaped_value
  escaped_value=$(printf '%s\n' "$value" | sed 's:[\\&|/]:\\&:g; s/$/\\/' | head -c -1)
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s|^${key}=.*|${key}=${escaped_value}|" "$ENV_FILE"
  else
    printf '%s=%s\n' "$key" "$value" >> "$ENV_FILE"
  fi
}

configure_provider() {
  local name=$1 key_name=$2
  echo ""
  echo "── ${name} ──"
  local current
  current=$(grep "^${key_name}=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"' || true)
  if [ -n "$current" ] && ! echo "$current" | grep -qE "^(your_|CHANGE_ME|sk-YOUR)"; then
    echo "  Already configured ✅"
    return
  fi
  read -rp "  Enter ${key_name} (leave blank to skip): " api_key
  if [ -n "$api_key" ]; then
    set_env_key "$key_name" "$api_key"
    echo "  Saved ${key_name} to .env ✅"
  else
    echo "  Skipped"
  fi
}

# Ollama is always enabled — just show status
echo "── Ollama (local, no API key needed) ──"
echo "  Always enabled ✅  (runs as Docker service 'ollama')"

configure_provider "OpenAI"     "OPENAI_API_KEY"
configure_provider "Anthropic"  "ANTHROPIC_API_KEY"
configure_provider "Google Gemini" "GEMINI_API_KEY"
configure_provider "OpenRouter" "OPENROUTER_API_KEY"

echo ""
echo "══════════════════════════════════════════"
echo "✅ LLM setup complete. Keys saved to .env"
echo ""
echo "Next steps:"
echo "  • Restart Docker stack:  docker compose --profile cpu down && docker compose --profile cpu up -d"
echo "  • Generate AGENTS.md:    cd GenerateAgents.md && uv run autogenerateagentsmd . --style comprehensive"
echo "══════════════════════════════════════════"
