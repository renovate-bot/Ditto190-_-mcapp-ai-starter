#!/bin/bash
set -euo pipefail

run_snapshot=1
run_format=1
run_analyze=1
do_commit=1
do_push=1
label="checkpoint-$(date -u +%Y%m%dT%H%M%SZ)"
output_root=".session-state/checkpoints"
commit_message="checkpoint: automated savepoint"
base_branch="main"
open_pr=0

usage() {
  cat <<'EOF'
Usage: bash scripts/session-checkpoint.sh [options]

Options:
  --label <name>         Snapshot label override.
  --output-root <path>   Snapshot output root override.
  --message <text>       Commit message override.
  --base <branch>        PR base branch when using --open-pr (default: main).
  --no-snapshot          Skip session snapshot capture.
  --no-format            Skip formatter commands.
  --no-analyze           Skip analysis commands.
  --no-commit            Skip git commit.
  --no-push              Skip git push.
  --open-pr              Create a draft PR with gh if none exists.
  --help                 Show this help text.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label)
      label="${2:?missing value for --label}"
      shift 2
      ;;
    --output-root)
      output_root="${2:?missing value for --output-root}"
      shift 2
      ;;
    --message)
      commit_message="${2:?missing value for --message}"
      shift 2
      ;;
    --base)
      base_branch="${2:?missing value for --base}"
      shift 2
      ;;
    --no-snapshot)
      run_snapshot=0
      shift
      ;;
    --no-format)
      run_format=0
      shift
      ;;
    --no-analyze)
      run_analyze=0
      shift
      ;;
    --no-commit)
      do_commit=0
      shift
      ;;
    --no-push)
      do_push=0
      shift
      ;;
    --open-pr)
      open_pr=1
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

has_npm_script() {
  local script_name="$1"
  if ! command -v node >/dev/null 2>&1; then
    return 1
  fi
  node -e "const fs=require('fs'); const pkg=JSON.parse(fs.readFileSync('package.json','utf8')); process.exit(pkg.scripts&&pkg.scripts['$script_name']?0:1);" 2>/dev/null
}

run_first_available() {
  local label_name="$1"
  shift
  local script_name
  for script_name in "$@"; do
    if has_npm_script "$script_name"; then
      echo "Running ${label_name}: npm run ${script_name}"
      npm run "$script_name"
      return 0
    fi
  done
  echo "Skipping ${label_name}: no matching npm script found (${*})"
}

if [[ "$run_snapshot" -eq 1 ]]; then
  bash scripts/session-pre-end.sh --label "$label" --output-root "$output_root" --skip-code --skip-docker
fi

if [[ "$run_format" -eq 1 ]]; then
  run_first_available "formatter" format:write format prettier:fix prettier
fi

if [[ "$run_analyze" -eq 1 ]]; then
  run_first_available "analysis" lint typecheck check
  if [[ -f scripts/test-runner.sh ]]; then
    echo "Running fast suite: scripts/test-runner.sh --fast --suite npm"
    bash scripts/test-runner.sh --fast --suite npm || true
  fi
fi

current_branch="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$do_commit" -eq 1 ]]; then
  git add -A
  if ! git diff --cached --quiet; then
    git commit -m "$commit_message"
  else
    echo "No staged changes to commit."
  fi
fi

if [[ "$do_push" -eq 1 ]]; then
  if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    git push
  else
    git push -u origin "$current_branch"
  fi
fi

if [[ "$open_pr" -eq 1 ]]; then
  if command -v gh >/dev/null 2>&1; then
    if ! gh pr view --json number >/dev/null 2>&1; then
      gh pr create --draft --base "$base_branch" --head "$current_branch" --title "checkpoint: ${current_branch}" --body "Automated checkpoint PR for asynchronous review."
    else
      echo "PR already exists for branch ${current_branch}."
    fi
  else
    echo "Skipping --open-pr: gh CLI is not installed."
  fi
fi

cat <<EOF
Checkpoint completed.

Branch: ${current_branch}
Commit message: ${commit_message}
Snapshot root: ${output_root}

Your push-triggered checkpoint pipeline can run while you continue coding.
EOF