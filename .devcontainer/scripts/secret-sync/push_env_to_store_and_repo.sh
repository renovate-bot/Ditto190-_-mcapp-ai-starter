#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   export EXTERNAL_STORE_URL="https://example-store/api/save"
#   export EXTERNAL_STORE_TOKEN="secret-token"
#   export GITHUB_REPO="Ditto190/mcapp-ai-starter"
#   ./push_env_to_store_and_repo.sh

if [[ ! -f .env ]]; then
  echo ".env not found in $(pwd)"
  exit 1
fi

# Read .env content (preserve newlines)
ENV_CONTENT="$(cat .env)"

# 1) Push full .env to external store (replace with your provider endpoint)
# Example: POST with JSON { "key": "repo:env", "value": "<base64>" }
BODY_JSON=$(jq -nc --arg v "$(printf '%s' "$ENV_CONTENT" | base64 -w0)" '{key: $key, value: $v}' --arg key "env:repo:$(basename $PWD)")
curl -sS -X POST \
  -H "Authorization: Bearer ${EXTERNAL_STORE_TOKEN}" \
  -H "Content-Type: application/json" \
  --data "$BODY_JSON" \
  "${EXTERNAL_STORE_URL}" | jq .

# 2) Export individual keys to GitHub repo secrets (requires gh CLI and you logged in)
# For each KEY=VALUE in .env (skip comments/empty)
while IFS= read -r line; do
  [[ "$line" =~ ^# ]] && continue
  [[ -z "$line" ]] && continue
  if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
    KEY="${BASH_REMATCH[1]}"
    VAL="${BASH_REMATCH[2]}"
    # Remove surrounding quotes if present
    VAL="${VAL%\"}"
    VAL="${VAL#\"}"
    echo "Setting GitHub secret: $KEY (repo: ${GITHUB_REPO})"
    printf "%s" "$VAL" | gh secret set "$KEY" --repo "${GITHUB_REPO}" --body -
  fi
done < <(sed -n 's/\r$//p' .env)