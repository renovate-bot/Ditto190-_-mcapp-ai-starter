#!/bin/bash
set -euo pipefail

label="$(date -u +%Y%m%dT%H%M%SZ)"
output_root=".session-state/snapshots"
archive_snapshot=0
skip_code=0
skip_docker=0
skip_python=0
skip_node=0
skip_apt=0

usage() {
  cat <<'EOF'
Usage: bash scripts/session-pre-end.sh [options]

Options:
  --label <name>        Override the snapshot label.
  --output-root <path>  Override the output root relative to the repo root.
  --archive             Create a tar.gz archive alongside the snapshot directory.
  --skip-code           Skip VS Code extension export.
  --skip-docker         Skip Docker inventory export.
  --skip-python         Skip uv and pip inventory export.
  --skip-node           Skip npm global package inventory export.
  --skip-apt            Skip apt manual package inventory export.
  --help                Show this help text.
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
snapshot_root="${repo_root}/${output_root}"
snapshot_dir="${snapshot_root}/${label}"
raw_dir="${snapshot_dir}/raw"
safe_dir="${snapshot_dir}/safe"
inventory_dir="${snapshot_dir}/inventories"
restore_dir="${snapshot_dir}/restore"

mkdir -p "$raw_dir" "$safe_dir" "$inventory_dir" "$restore_dir"

latest_previous=""
if [[ -d "$snapshot_root" ]]; then
  latest_previous="$(find "$snapshot_root" -mindepth 1 -maxdepth 1 -type d ! -name "$label" | LC_ALL=C sort | tail -n 1)"
fi

note_unavailable() {
  local target="$1"
  local message="$2"
  printf '%s\n' "$message" > "$target"
}

sanitize_copy() {
  local src="$1"
  local dest="$2"
  python3 - "$src" "$dest" <<'PY'
from pathlib import Path
import json
import re
import sys

src = Path(sys.argv[1])
dest = Path(sys.argv[2])
secret_pattern = re.compile(r"(token|secret|password|passwd|api[_-]?key|authorization)", re.IGNORECASE)
text = src.read_text(encoding="utf-8", errors="ignore")

def redact_json(value):
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            if secret_pattern.search(key):
                result[key] = "[REDACTED]"
            else:
                result[key] = redact_json(child)
        return result
    if isinstance(value, list):
        return [redact_json(item) for item in value]
    return value

try:
    parsed = json.loads(text)
except Exception:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            if secret_pattern.search(key):
                lines.append(f"{key}=[REDACTED]")
            else:
                lines.append(line)
        elif ":" in line and not stripped.startswith("//"):
            key, value = line.split(":", 1)
            if secret_pattern.search(key):
                quote = '"' if '"' in value else ''
                suffix = ',' if value.rstrip().endswith(',') else ''
                lines.append(f"{key}: {quote}[REDACTED]{quote}{suffix}")
            else:
                lines.append(line)
        else:
            lines.append(line)
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
else:
    dest.write_text(json.dumps(redact_json(parsed), indent=2) + "\n", encoding="utf-8")
PY
}

write_inventory() {
  local target="$1"
  shift
  if "$@" > "$target" 2>/dev/null; then
    :
  else
    note_unavailable "$target" "UNAVAILABLE"
  fi
}

inventory_new_items() {
  local current_file="$1"
  local previous_file="$2"
  local label_name="$3"

  if [[ ! -s "$current_file" ]] || grep -qx 'UNAVAILABLE' "$current_file"; then
    printf '%s\n' "- ${label_name}: unavailable in this environment"
    return
  fi

  if [[ -n "$previous_file" && -f "$previous_file" ]] && ! grep -qx 'UNAVAILABLE' "$previous_file"; then
    local diff_output
    diff_output="$(comm -13 "$previous_file" "$current_file" || true)"
    if [[ -n "$diff_output" ]]; then
      while IFS= read -r item; do
        [[ -n "$item" ]] && printf '%s\n' "- NEW ${label_name}: ${item}"
      done <<< "$diff_output"
    else
      printf '%s\n' "- ${label_name}: no new items since previous snapshot"
    fi
  else
    printf '%s\n' "- ${label_name}: baseline captured"
  fi
}

write_restore_script() {
  local target="$1"
  local body="$2"
  cat > "$target" <<EOF
#!/bin/bash
set -euo pipefail

${body}
EOF
  chmod +x "$target"
}

cd "$repo_root"

git status --short --branch > "$raw_dir/git-status.txt"
git diff --binary > "$raw_dir/git-working-tree.patch"
git diff --binary --staged > "$raw_dir/git-staged.patch"
git ls-files --others --exclude-standard > "$raw_dir/git-untracked.txt"
git stash list > "$raw_dir/git-stashes.txt"
git rev-parse --abbrev-ref HEAD > "$raw_dir/git-branch.txt"
git rev-parse HEAD > "$raw_dir/git-head.txt"

config_files=(
  ".env"
  ".env.example"
  ".mcp.json"
  ".vscode/settings.json"
  ".vscode/extensions.json"
  ".vscode/mcp.json"
  ".devcontainer/devcontainer.json"
  ".devcontainer/post-create.sh"
  "codespace.config"
  "llm.config.json"
  "package.json"
  "package-lock.json"
)

for file in "${config_files[@]}"; do
  if [[ -f "$file" ]]; then
    mkdir -p "$safe_dir/$(dirname "$file")"
    sanitize_copy "$file" "$safe_dir/$file"
  fi
done

if [[ "$skip_code" -eq 0 ]] && command -v code >/dev/null 2>&1; then
  write_inventory "$inventory_dir/vscode-extensions.txt" bash -lc 'code --list-extensions --show-versions | LC_ALL=C sort'
else
  note_unavailable "$inventory_dir/vscode-extensions.txt" "UNAVAILABLE"
fi

if [[ "$skip_node" -eq 0 ]] && command -v npm >/dev/null 2>&1; then
  write_inventory "$inventory_dir/npm-global.txt" bash -lc 'npm ls -g --depth=0 --parseable | tail -n +2 | xargs -r -n1 basename | LC_ALL=C sort -u'
else
  note_unavailable "$inventory_dir/npm-global.txt" "UNAVAILABLE"
fi

if [[ "$skip_python" -eq 0 ]] && command -v uv >/dev/null 2>&1; then
  write_inventory "$inventory_dir/uv-tools.txt" bash -lc 'uv tool list | awk "NR > 2 && NF {print \$1}" | LC_ALL=C sort -u'
else
  note_unavailable "$inventory_dir/uv-tools.txt" "UNAVAILABLE"
fi

if [[ "$skip_python" -eq 0 ]] && command -v python3 >/dev/null 2>&1; then
  write_inventory "$inventory_dir/pip-global.txt" bash -lc 'python3 -m pip list --format=freeze | LC_ALL=C sort -u'
else
  note_unavailable "$inventory_dir/pip-global.txt" "UNAVAILABLE"
fi

if [[ "$skip_apt" -eq 0 ]] && command -v apt-mark >/dev/null 2>&1; then
  write_inventory "$inventory_dir/apt-manual.txt" bash -lc 'apt-mark showmanual | LC_ALL=C sort -u'
else
  note_unavailable "$inventory_dir/apt-manual.txt" "UNAVAILABLE"
fi

if [[ "$skip_docker" -eq 0 ]] && command -v docker >/dev/null 2>&1; then
  write_inventory "$inventory_dir/docker-images.txt" bash -lc 'docker images --format "{{.Repository}}:{{.Tag}}" | LC_ALL=C sort -u'
  write_inventory "$inventory_dir/docker-containers.txt" bash -lc 'docker ps -a --format "{{.Names}}\t{{.Image}}\t{{.Status}}" | LC_ALL=C sort -u'
else
  note_unavailable "$inventory_dir/docker-images.txt" "UNAVAILABLE"
  note_unavailable "$inventory_dir/docker-containers.txt" "UNAVAILABLE"
fi

write_restore_script "$restore_dir/restore-vscode-extensions.sh" '
if [[ ! -f "${1:-inventories/vscode-extensions.txt}" ]]; then
  echo "Pass the path to vscode-extensions.txt as the first argument if running outside the snapshot directory."
  exit 1
fi
inventory_file="${1:-inventories/vscode-extensions.txt}"
if ! command -v code >/dev/null 2>&1; then
  echo "VS Code CLI is not available."
  exit 1
fi
while IFS= read -r entry; do
  [[ -z "$entry" || "$entry" == "UNAVAILABLE" ]] && continue
  extension="${entry%@*}"
  code --install-extension "$extension" --force
done < "$inventory_file"
'

write_restore_script "$restore_dir/restore-global-node-tools.sh" '
inventory_file="${1:-inventories/npm-global.txt}"
if [[ ! -f "$inventory_file" ]]; then
  echo "Missing inventory file: $inventory_file"
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not available."
  exit 1
fi
packages=()
while IFS= read -r entry; do
  [[ -z "$entry" || "$entry" == "UNAVAILABLE" ]] && continue
  packages+=("$entry")
done < "$inventory_file"
if [[ ${#packages[@]} -gt 0 ]]; then
  npm install -g "${packages[@]}"
fi
'

write_restore_script "$restore_dir/restore-uv-tools.sh" '
inventory_file="${1:-inventories/uv-tools.txt}"
if [[ ! -f "$inventory_file" ]]; then
  echo "Missing inventory file: $inventory_file"
  exit 1
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not available."
  exit 1
fi
while IFS= read -r entry; do
  [[ -z "$entry" || "$entry" == "UNAVAILABLE" ]] && continue
  uv tool install "$entry" || true
done < "$inventory_file"
'

branch_name="$(cat "$raw_dir/git-branch.txt")"
head_sha="$(cat "$raw_dir/git-head.txt")"

cat > "$snapshot_dir/changelog.md" <<EOF
# Codespace Session Changelog

- Snapshot label: ${label}
- Generated at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Branch: ${branch_name}
- HEAD: ${head_sha}

## Working Tree Changes
EOF

if [[ -s "$raw_dir/git-status.txt" ]]; then
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    if [[ "$line" == '## '* ]]; then
      printf '%s\n' "- Branch tracking: ${line#\#\# }" >> "$snapshot_dir/changelog.md"
    elif [[ "$line" == '?? '* ]]; then
      printf '%s\n' "- NEW file: ${line#\?\? }" >> "$snapshot_dir/changelog.md"
    else
      printf '%s\n' "- ${line}" >> "$snapshot_dir/changelog.md"
    fi
  done < "$raw_dir/git-status.txt"
else
  echo "- Clean working tree" >> "$snapshot_dir/changelog.md"
fi

cat >> "$snapshot_dir/changelog.md" <<EOF

## Optional Environment Additions
EOF

inventory_new_items "$inventory_dir/vscode-extensions.txt" "${latest_previous:+$latest_previous/inventories/vscode-extensions.txt}" "VS Code extension" >> "$snapshot_dir/changelog.md"
inventory_new_items "$inventory_dir/npm-global.txt" "${latest_previous:+$latest_previous/inventories/npm-global.txt}" "npm global package" >> "$snapshot_dir/changelog.md"
inventory_new_items "$inventory_dir/uv-tools.txt" "${latest_previous:+$latest_previous/inventories/uv-tools.txt}" "uv tool" >> "$snapshot_dir/changelog.md"
inventory_new_items "$inventory_dir/pip-global.txt" "${latest_previous:+$latest_previous/inventories/pip-global.txt}" "Python package" >> "$snapshot_dir/changelog.md"
inventory_new_items "$inventory_dir/apt-manual.txt" "${latest_previous:+$latest_previous/inventories/apt-manual.txt}" "apt package" >> "$snapshot_dir/changelog.md"
inventory_new_items "$inventory_dir/docker-images.txt" "${latest_previous:+$latest_previous/inventories/docker-images.txt}" "Docker image" >> "$snapshot_dir/changelog.md"

cat > "$snapshot_dir/summary.md" <<EOF
# Codespace Session Snapshot

This snapshot is a local, gitignored backup of the current Codespace state.

## What was captured

- Git branch, status, untracked files, and raw patches in raw/
- Sanitized workspace and devcontainer configs in safe/
- Optional tool inventories in inventories/
- Convenience restore helpers in restore/

## What this does not replace

- A real Git commit and push
- Settings Sync or dotfiles for personal preferences across every Codespace
- Secret management outside the repository

## Suggested next steps

1. Review changelog.md for NEW optional additions.
2. Review raw/git-working-tree.patch before any broad commit.
3. If the work matters beyond this Codespace, commit and push it.
EOF

if [[ "$archive_snapshot" -eq 1 ]]; then
  tar -czf "${snapshot_root}/${label}.tar.gz" -C "$snapshot_root" "$label"
fi

echo "Snapshot created at: $snapshot_dir"
echo "SNAPSHOT_DIR=$snapshot_dir"