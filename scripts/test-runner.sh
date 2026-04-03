#!/bin/bash
# test-runner.sh — Automated test discovery and runner for the AI Starter Kit.
# Discovers and runs all available test suites across npm and Python sub-projects.
#
# Usage: bash scripts/test-runner.sh [--fast] [--suite npm|python|all]

set -euo pipefail

usage() {
  echo "Usage: bash scripts/test-runner.sh [--fast] [--suite npm|python|all]" >&2
}

SUITE="all"
FAST=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --fast)
      FAST=true
      shift
      ;;
    --suite)
      if [ "$#" -lt 2 ]; then
        echo "Error: --suite requires a value." >&2
        usage
        exit 1
      fi
      case "$2" in
        npm|python|all)
          SUITE="$2"
          shift 2
          ;;
        *)
          echo "Error: invalid suite '$2'. Expected one of: npm, python, all." >&2
          usage
          exit 1
          ;;
      esac
      ;;
    *)
      echo "Error: unknown argument '$1'." >&2
      usage
      exit 1
      ;;
  esac
done
PASS=0
FAIL=0
SKIP=0

section() { echo ""; echo "══ $* ══════════════════════════════════"; }
ok()   { echo "  ✅ $*"; PASS=$((PASS+1)); }
fail() { echo "  ❌ $*"; FAIL=$((FAIL+1)); }
skip() { echo "  ⏭️  $*"; SKIP=$((SKIP+1)); }

run_suite() {
  local name="$1" dir="$2" cmd="$3"
  if [ ! -d "$dir" ]; then skip "$name: directory '$dir' not found"; return; fi
  echo ""
  echo "  Running: $name"
  if (cd "$dir" && eval "$cmd" 2>&1); then
    ok "$name passed"
  else
    fail "$name failed"
  fi
}

# ── npm tests ─────────────────────────────────────────────────────────────────
if [[ "$SUITE" == "all" || "$SUITE" == "npm" ]]; then
  section "npm test suites"

  # Root package tests
  if [ -f package.json ] && node -e "require('./package.json').scripts?.test" &>/dev/null 2>&1; then
    run_suite "Root npm tests" "." "npm test 2>&1"
  else
    skip "Root: no test script in package.json"
  fi

  # prompt-registry
  run_suite "prompt-registry" "prompt-registry" "npm ci --quiet && npm test 2>&1"

  # awesome-copilot build check
  if [ -f awesome-copilot/package.json ]; then
    run_suite "awesome-copilot build" "awesome-copilot" "npm ci --quiet && npm run build 2>&1"
  fi
fi

# ── Python tests ──────────────────────────────────────────────────────────────
if [[ "$SUITE" == "all" || "$SUITE" == "python" ]]; then
  section "Python test suites"

  if ! command -v uv &>/dev/null; then
    skip "Python tests: uv not installed"
  else
    # GenerateAgents.md — skip e2e (requires API keys)
    if [ -f GenerateAgents.md/pyproject.toml ]; then
      if $FAST; then
        run_suite "GenerateAgents.md (fast)" "GenerateAgents.md" "uv sync --extra dev --quiet && uv run pytest -m 'not e2e' -q 2>&1"
      else
        run_suite "GenerateAgents.md" "GenerateAgents.md" "uv sync --extra dev --quiet && uv run pytest -m 'not e2e' -q 2>&1"
      fi
    fi

    # generateagents-mcp
    if [ -f generateagents-mcp/pyproject.toml ]; then
      run_suite "generateagents-mcp" "generateagents-mcp" "uv sync --quiet && uv run pytest -q 2>&1"
    fi
  fi
fi

# ── Summary ────────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
printf "  Tests: %d passed, %d failed, %d skipped\n" "$PASS" "$FAIL" "$SKIP"
echo "══════════════════════════════════════════"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
