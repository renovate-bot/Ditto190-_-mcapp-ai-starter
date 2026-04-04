#!/usr/bin/env python3
"""
set_repo_secrets_local.py

Safely upload key/value pairs from a .env file to a GitHub repository's Actions secrets.
Designed to be run locally with your personal access token (PAT) provided via the
`GITHUB_TOKEN` environment variable or prompted interactively.

Usage examples:

# dry-run (no changes):
export GITHUB_TOKEN="ghp_..."
python3 set_repo_secrets_local.py --env-file .env --repo Ditto190/mcapp-ai-starter --dry-run

# actually upload:
export GITHUB_TOKEN="ghp_..."
python3 set_repo_secrets_local.py --env-file .env --repo Ditto190/mcapp-ai-starter

Requirements (install locally):
python3 -m pip install requests python-dotenv pynacl

Security notes:
- Do NOT paste or print your PAT to shared logs. Provide it in your local environment only.
- This script never prints secret values; it only shows masked previews when requested.

"""
import argparse
import base64
import json
import os
import sys
import getpass
import subprocess
from typing import Dict, Tuple

try:
    import requests
    from dotenv import dotenv_values
    from nacl.public import SealedBox, PublicKey
except Exception as e:
    print(
        "Missing dependencies. Install: pip install requests python-dotenv pynacl",
        file=sys.stderr,
    )
    raise

GITHUB_API = "https://api.github.com"


def parse_args():
    p = argparse.ArgumentParser(
        description="Upload .env entries to GitHub Actions secrets (local run)."
    )
    p.add_argument("--env-file", default=".env", help="Path to .env file")
    p.add_argument(
        "--repo",
        help="Repository in form owner/repo. If omitted, try to infer from git remote.",
    )
    p.add_argument(
        "--token-env",
        default="GITHUB_TOKEN",
        help="Environment variable name that contains the PAT",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without making changes",
    )
    p.add_argument(
        "--skip-prefix",
        action="append",
        default=[],
        help="Skip secrets with this prefix (can be given multiple times)",
    )
    p.add_argument(
        "--only",
        action="append",
        default=[],
        help="Only upload these keys (can be given multiple times)",
    )
    p.add_argument(
        "--mask-preview",
        action="store_true",
        help="Show masked preview of values (safe) in dry-run",
    )
    return p.parse_args()


def infer_repo_from_git() -> str:
    try:
        out = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"], stderr=subprocess.DEVNULL
        )
        url = out.decode().strip()
        if url.startswith("git@github.com:"):
            path = url.split(":", 1)[1]
        else:
            # https://github.com/owner/repo.git
            path = url.split("github.com/", 1)[1]
        if path.endswith(".git"):
            path = path[:-4]
        return path
    except Exception:
        return None


def read_env_file(path: str) -> Dict[str, str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Env file not found: {path}")
    # dotenv_values preserves sensible parsing and doesn't execute anything
    data = dotenv_values(path)
    # dotenv_values returns None values for lines that cannot be parsed; filter those out
    return {k: v for k, v in data.items() if k and v is not None}


def get_github_token(env_name: str) -> str:
    token = os.environ.get(env_name)
    if token:
        return token
    # Prompt user securely (local run)
    print(
        f"Environment variable '{env_name}' not set. Please enter a GitHub PAT with repo+secrets permissions."
    )
    token = getpass.getpass("GitHub PAT: ")
    return token.strip()


def get_repo_public_key(owner: str, repo: str, token: str) -> Tuple[str, str]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code == 200:
        j = r.json()
        return j["key"], j["key_id"]
    elif r.status_code == 403:
        raise PermissionError(
            "403 Forbidden: token lacks permission to read repository public key (needs repo access)."
        )
    elif r.status_code == 404:
        raise FileNotFoundError(
            f"Repository not found or access denied: {owner}/{repo}"
        )
    else:
        raise RuntimeError(f"Failed to get public key: {r.status_code} {r.text}")


def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    public_key = base64.b64decode(public_key_b64)
    pk = PublicKey(public_key)
    sealed_box = SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_value.encode())
    return base64.b64encode(encrypted).decode()


def put_secret(
    owner: str, repo: str, token: str, key: str, encrypted_value_b64: str, key_id: str
) -> bool:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/actions/secrets/{key}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    body = {"encrypted_value": encrypted_value_b64, "key_id": key_id}
    r = requests.put(url, headers=headers, json=body, timeout=20)
    if r.status_code in (201, 204):
        return True
    else:
        print(f"Failed to set secret {key}: {r.status_code} {r.text}")
        return False


def mask_value(v: str) -> str:
    if v is None:
        return "(none)"
    v = str(v)
    if len(v) <= 8:
        return "*" * len(v)
    return v[:4] + "*" * (len(v) - 8) + v[-4:]


def main():
    args = parse_args()
    try:
        repo = args.repo or infer_repo_from_git()
        if not repo:
            print(
                "Repository not provided and could not be inferred from git. Use --repo owner/repo."
            )
            sys.exit(2)
        owner, repo_name = repo.split("/", 1)
    except Exception as e:
        print("Invalid repo format. Use owner/repo.")
        sys.exit(2)

    token = get_github_token(args.token_env)
    if not token:
        print("No GitHub token provided; aborting.")
        sys.exit(1)

    print(f"Reading env file: {args.env_file}")
    kv = read_env_file(args.env_file)
    if not kv:
        print(
            "No variables found in env file (or all values are blank). Nothing to do."
        )
        sys.exit(0)

    # Filter keys
    keys = sorted(kv.keys())
    if args.only:
        keys = [k for k in keys if k in args.only]
    if args.skip_prefix:
        keys = [
            k for k in keys if not any(k.startswith(pref) for pref in args.skip_prefix)
        ]

    if not keys:
        print("No keys to upload after filtering.")
        sys.exit(0)

    # Fetch public key
    try:
        public_key_b64, key_id = get_repo_public_key(owner, repo_name, token)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(
        f"Preparing to {'simulate upload' if args.dry_run else 'upload'} {len(keys)} secrets to {owner}/{repo_name}"
    )

    success = 0
    for k in keys:
        v = kv.get(k)
        if v is None or str(v).strip() == "":
            print(f"Skipping empty value: {k}")
            continue
        if args.dry_run:
            if args.mask_preview:
                print(f"[DRY] {k} => {mask_value(v)}")
            else:
                print(
                    f"[DRY] {k} => (hidden, use --mask-preview to show masked preview)"
                )
            success += 1
            continue
        try:
            enc = encrypt_secret(public_key_b64, str(v))
            ok = put_secret(owner, repo_name, token, k, enc, key_id)
            if ok:
                print(f"Uploaded: {k}")
                success += 1
        except Exception as e:
            print(f"Error uploading {k}: {e}")

    print(f"Done. {success} secrets processed (dry_run={args.dry_run}).")


if __name__ == "__main__":
    main()
