#!/usr/bin/env bash
set -euo pipefail

paths_csv="migration,tools/external/system-manager"
out_dir="reports/recycle"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --paths)
      paths_csv="${2:?missing value for --paths}"
      shift 2
      ;;
    --out-dir)
      out_dir="${2:?missing value for --out-dir}"
      shift 2
      ;;
    --help)
      echo "Usage: bash scripts/recycle-imports.sh [--paths 'a,b,c'] [--out-dir reports/recycle]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

mkdir -p "$out_dir"

inventory_file="$out_dir/inventory.tsv"
priority_file="$out_dir/priority-files.txt"
exclude_file="$out_dir/exclude-suggestions.txt"
summary_file="$out_dir/summary.md"

printf "path\tsize_bytes\n" > "$inventory_file"
: > "$priority_file"

IFS=',' read -r -a input_paths <<< "$paths_csv"

for p in "${input_paths[@]}"; do
  p_trimmed="$(echo "$p" | xargs)"
  [[ -z "$p_trimmed" ]] && continue
  [[ ! -e "$p_trimmed" ]] && continue

  find "$p_trimmed" -type f \
    -not -path '*/.git/*' \
    -not -path '*/node_modules/*' \
    -not -path '*/.venv/*' \
    -not -path '*/__pycache__/*' \
    -not -path '*/.pytest_cache/*' \
    -not -path '*/dist/*' \
    -not -path '*/build/*' \
    -not -path '*/target/*' \
    -not -path '*/.session-state/*' \
    -print0 | while IFS= read -r -d '' f; do
      size="$(wc -c < "$f" | tr -d ' ')"
      printf "%s\t%s\n" "$f" "$size" >> "$inventory_file"

      case "$f" in
        */AGENTS.md|*/AGENTS_old.md|*/CLAUDE.md|*/README.md|*/CONTRIBUTING.md|*/CHANGELOG.md|*/\.github/workflows/*.yml|*/\.github/instructions/*.instructions.md|*/\.github/agents/*.agent.md|*/scripts/*.sh|*/nix/*.nix|*/flake.nix|*/docker-compose.yml)
          echo "$f" >> "$priority_file"
          ;;
      esac
    done
done

sort -k2 -nr "$inventory_file" -o "$inventory_file"
sort -u "$priority_file" -o "$priority_file"

cat > "$exclude_file" <<'EOF_EXCLUDE'
Suggested excludes for recycle PRs:
- migration/**/node_modules/**
- migration/**/.venv/**
- migration/**/.pytest_cache/**
- migration/**/__pycache__/**
- migration/**/Data/**
- migration/**/Documents/**
- migration/**/workspace/**
- migration/**/repodumps/**/.env
- migration/**/repodumps/**/.env.*
- tools/external/**/target/**
- tools/external/**/.git/**
EOF_EXCLUDE

file_count=$(($(wc -l < "$inventory_file") - 1))
priority_count=$(wc -l < "$priority_file" | tr -d ' ')

cat > "$summary_file" <<EOF_SUM
# Recycle Inventory Summary

Scanned paths: $paths_csv

- Files inventoried: $file_count
- Priority candidates: $priority_count

Top 25 largest files:

EOF_SUM

awk 'NR==1{next} NR<=26{print "- " $1 " (" $2 " bytes)"}' "$inventory_file" >> "$summary_file"

echo "Wrote $summary_file"
echo "Wrote $inventory_file"
echo "Wrote $priority_file"
echo "Wrote $exclude_file"
