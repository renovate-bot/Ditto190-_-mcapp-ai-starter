#!/usr/bin/env python3
"""Set GitHub repository secrets from .env.

Usage:
- Ensure Python deps installed: requests, python-dotenv, pynacl
- Optionally set GITHUB_TOKEN in env. Otherwise the script will use
  GITHUB_PERSONAL_ACCESS_TOKEN or GITHUB_PAT_ALT from .env.

This script reads .env in the repo root, fetches the repo Actions public
key, encrypts each secret and uploads it via the GitHub REST API.

WARNING: This will call GitHub's API and create/update repository secrets.
Make sure you trust the .env contents before running.
"""

import os
import sys
import json
import base64
from pathlib import Path

try:
    import requests
    from dotenv import dotenv_values
    from nacl import public, encoding
except Exception as e:
    print(
        "Missing Python dependencies. Install with: python3 -m pip install requests python-dotenv pynacl",
        file=sys.stderr,
    )
    raise

OWNER = "Ditto190"
REPO = "mcapp-ai-starter"
API_BASE = "https://api.github.com"


def get_env_values(env_path: Path):
    if not env_path.exists():
        print(f"Error: {env_path} not found", file=sys.stderr)
        sys.exit(1)
    vals = dotenv_values(env_path)
    # dotenv_values returns keys for commented lines as None, filter them
    clean = {
        k: v
        for k, v in vals.items()
        if k and v is not None and str(k).strip() and not str(k).strip().startswith("#")
    }
    return clean


def get_token_from_env_or_file(env_vars):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
    if token:
        return token
    # Fallback to values present in .env
    for candidate in (
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "GITHUB_PAT_ALT",
        "GITHUB_PAT",
        "GITHUB_TOKEN",
    ):
        if candidate in env_vars and env_vars[candidate]:
            return env_vars[candidate]
    return None


def get_public_key(headers):
    url = f"{API_BASE}/repos/{OWNER}/{REPO}/actions/secrets/public-key"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()


def encrypt_secret(public_key: str, secret_value: str) -> str:
    # public_key is base64 encoded
    pk = base64.b64decode(public_key)
    public_key_obj = public.PublicKey(pk)
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def set_repo_secret(name: str, encrypted_value: str, key_id: str, headers):
    url = f"{API_BASE}/repos/{OWNER}/{REPO}/actions/secrets/{name}"
    payload = {"encrypted_value": encrypted_value, "key_id": key_id}
    r = requests.put(url, headers=headers, data=json.dumps(payload))
    if r.status_code in (201, 204):
        return True
    else:
        print(f"Failed to set {name}: {r.status_code} {r.text}", file=sys.stderr)
        return False


def main():
    repo_root = Path(__file__).resolve().parent
    env_path = repo_root / ".env"
    env_vars = get_env_values(env_path)

    token = get_token_from_env_or_file(env_vars)
    if not token:
        print(
            "No GitHub token found. Set GITHUB_TOKEN in environment or add GITHUB_PERSONAL_ACCESS_TOKEN to .env",
            file=sys.stderr,
        )
        sys.exit(1)

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    print("Fetching repository public key...")
    public_key_resp = get_public_key(headers)
    key_id = public_key_resp.get("key_id")
    public_key = public_key_resp.get("key")
    if not key_id or not public_key:
        print("Could not retrieve public key from GitHub API", file=sys.stderr)
        sys.exit(1)

    # Upload each secret; skip obvious non-secret keys or placeholders
    skip_keys = set(["#", ""])
    success_count = 0
    total = 0
    for k, v in env_vars.items():
        total += 1
        name = k.strip()
        if not name or name.startswith("#"):
            continue
        # Skip some keys that are not meant to be secrets/no-op, but user may want them
        # We upload everything by default; if you want to skip keys, modify skip_list
        try:
            encrypted = encrypt_secret(public_key, str(v))
            ok = set_repo_secret(name, encrypted, key_id, headers)
            if ok:
                print(f"{name}: set")
                success_count += 1
        except Exception as e:
            print(f"{name}: error: {e}", file=sys.stderr)

    print(f"Done. {success_count}/{total} secrets set (attempted {total}).")


if __name__ == "__main__":
    main()
