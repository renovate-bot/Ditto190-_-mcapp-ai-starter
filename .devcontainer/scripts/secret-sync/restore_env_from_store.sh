#!/usr/bin/env bash
set -euo pipefail

# Restore an environment file from a stored file.
# Usage: restore_env_from_store.sh [STORE_FILE] [TARGET_FILE]
# Defaults: STORE_FILE=.env.store  TARGET_FILE=.env

STORE_FILE="${1:-.env.store}"
TARGET_FILE="${2:-.env}"

if [ ! -f "$STORE_FILE" ]; then
	echo "Store file not found: $STORE_FILE" >&2
	exit 1
fi

cp -- "$STORE_FILE" "$TARGET_FILE"
echo "Restored env from $STORE_FILE to $TARGET_FILE"

#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   export EXTERNAL_STORE_URL="https://example-store/api/get?key=env:repo:myrepo"
#   export EXTERNAL_STORE_TOKEN="secret-token"
#   ./restore_env_from_store.sh

# 1) Fetch stored .env blob (example expects JSON { "value": "<base64>" })
RESP=$(curl -sS -H "Authorization: Bearer ${EXTERNAL_STORE_TOKEN}" "${EXTERNAL_STORE_URL}")
# Extract base64 value (adjust per your store's schema)
B64=$(echo "$RESP" | jq -r '.value // empty')
if [[ -z "$B64" || "$B64" == "null" ]]; then
  echo "No env stored at external store"
  exit 1
fi

# 2) Decode and write to .env (backup old .env)
if [[ -f .env ]]; then
  cp .env ".env.bak.$(date +%s)"
fi

printf '%s' "$B64" | base64 -d > .env
chmod 600 .env
echo ".env restored (local)."
# NOTE: cannot read GitHub repo secrets back — so we created .env from the external store.