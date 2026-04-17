#!/bin/bash
set -euo pipefail

label=""
output_root=".session-state/snapshots"
archive_snapshot=0
skip_code=0
skip_docker=0
skip_python=0
skip_node=0
skip_apt=0
stop_services=0
do_commit=0
do_push=0
commit_message="chore: save codespace session state"

usage() {
  cat <<'EOF'
Usage: bash scripts/session-end.sh [options]

Options:
  --label <name>         Override the snapshot label.
  --output-root <path>   Override the output root relative to the repo root.
  --archive              Create a tar.gz archive alongside the snapshot directory.
  --stop-services        Run docker compose down after the snapshot completes.
  --commit               Commit repository changes after the snapshot completes.
  --push                 Push after a successful commit.
  --message <text>       Commit message to use with --commit.
  --skip-code            Skip VS Code extension export.
  --skip-docker          Skip Docker inventory export.
  --skip-python          Skip uv and pip inventory export.
  --skip-node            Skip npm global package inventory export.
  --skip-apt             Skip apt manual package inventory export.
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
    --archive)
      archive_snapshot=1
      shift
      ;;
    --stop-services)
      stop_services=1
      shift
      ;;
    --commit)
      do_commit=1
      shift
      ;;
    --push)
      do_push=1
      shift
      ;;
    --message)
      commit_message="${2:?missing value for --message}"
      shift 2
      ;;
    --skip-code)
      skip_code=1
      shift
      ;;
    --skip-docker)
      skip_docker=1
      shift
      ;;
    --skip-python)
      skip_python=1
      shift
      ;;
    --skip-node)
      skip_node=1
      shift
      ;;
    --skip-apt)
      skip_apt=1
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

pre_end_args=("--output-root" "$output_root")
[[ -n "$label" ]] && pre_end_args+=("--label" "$label")
[[ "$archive_snapshot" -eq 1 ]] && pre_end_args+=("--archive")
[[ "$skip_code" -eq 1 ]] && pre_end_args+=("--skip-code")
[[ "$skip_docker" -eq 1 ]] && pre_end_args+=("--skip-docker")
[[ "$skip_python" -eq 1 ]] && pre_end_args+=("--skip-python")
[[ "$skip_node" -eq 1 ]] && pre_end_args+=("--skip-node")
[[ "$skip_apt" -eq 1 ]] && pre_end_args+=("--skip-apt")

snapshot_output="$(bash scripts/session-pre-end.sh "${pre_end_args[@]}")"
printf '%s\n' "$snapshot_output"

snapshot_dir="$(printf '%s\n' "$snapshot_output" | awk -F= '/^SNAPSHOT_DIR=/{print $2}' | tail -n 1)"

if [[ "$stop_services" -eq 1 ]] && [[ -f docker-compose.yml ]] && command -v docker >/dev/null 2>&1; then
  docker compose down || true
fi

if [[ "$do_commit" -eq 1 ]]; then
  git add -A
  if ! git diff --cached --quiet; then
    git commit -m "$commit_message"
  fi

  if [[ "$do_push" -eq 1 ]]; then
    git push
  fi
fi

cat <<EOF
End-session workflow complete.

Snapshot directory: ${snapshot_dir}

Recommended follow-up:
1. Review ${snapshot_dir}/changelog.md
2. Review ${snapshot_dir}/raw/git-working-tree.patch before any broad commit
3. Use Settings Sync or dotfiles for personal editor preferences that should survive all future Codespaces
EOF