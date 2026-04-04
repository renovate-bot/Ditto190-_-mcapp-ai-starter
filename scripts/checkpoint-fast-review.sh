#!/bin/bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

echo "[checkpoint-fast-review] branch=$(git rev-parse --abbrev-ref HEAD)"

has_npm_script() {
  local script_name="$1"
  if ! command -v node >/dev/null 2>&1; then
    return 1
  fi
  node -e "const fs=require('fs'); const pkg=JSON.parse(fs.readFileSync('package.json','utf8')); process.exit(pkg.scripts&&pkg.scripts['$script_name']?0:1);" 2>/dev/null
}

run_if_script() {
  local script_name="$1"
  if has_npm_script "$script_name"; then
    echo "[checkpoint-fast-review] npm run ${script_name}"
    npm run "$script_name"
  else
    echo "[checkpoint-fast-review] skip ${script_name} (not defined)"
  fi
}

if command -v bash >/dev/null 2>&1; then
  for file in scripts/*.sh .devcontainer/scripts/*.sh; do
    [[ -f "$file" ]] || continue
    bash -n "$file"
  done
fi

run_if_script "lint"
run_if_script "typecheck"
run_if_script "build"

if [[ -f scripts/test-runner.sh ]]; then
  echo "[checkpoint-fast-review] scripts/test-runner.sh --fast --suite npm"
  bash scripts/test-runner.sh --fast --suite npm || true
fi

if [[ -f scripts/session-pre-end.sh ]]; then
  echo "[checkpoint-fast-review] validating snapshot script"
  bash scripts/session-pre-end.sh --label ci-checkpoint --output-root .session-state/ci --skip-code --skip-docker
fi

echo "[checkpoint-fast-review] complete"