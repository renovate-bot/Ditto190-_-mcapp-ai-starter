#!/usr/bin/env python3
"""auto_merge.py — GitHub PR auto-merge decision helper.

Evaluates whether a pull request should be auto-merged based on:
  1. PR is open and not a draft.
  2. No "don't auto-merge" directive in comments or PR body.
  3. All configured required status checks have passed.
  4. Optionally: invokes the AI review script and checks its verdict.

Can be run:
  • From GitHub Actions (GITHUB_TOKEN is automatically available).
  • Locally using a Personal Access Token (PAT) with ``repo`` scope.
  • From any CI that can set the required environment variables.

Usage
-----
  python scripts/auto_merge.py [--pr PR_NUMBER] [--repo OWNER/REPO]
                               [--dry-run] [--merge-method METHOD]

Environment variables (all optional if CLI flags are provided):
  GITHUB_TOKEN         GitHub PAT or Actions token (required).
  GITHUB_REPOSITORY    owner/repo string.
  PR_NUMBER            Pull request number.
  DRY_RUN              Set to "true" to check without merging.
  MERGE_METHOD         squash | merge | rebase (default: squash).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from typing import Any

import requests

GITHUB_API = "https://api.github.com"

# ── Configurable block phrases (case-insensitive) ────────────────────────────
BLOCK_PHRASES: list[str] = [
    "don't auto-merge",
    "dont auto-merge",
    "do not auto-merge",
    "no auto-merge",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get(token: str, url: str, **params: Any) -> Any:
    resp = requests.get(url, headers=_headers(token), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _paginate(token: str, url: str, **params: Any) -> list[dict]:
    results: list[dict] = []
    page = 1
    while True:
        batch = _get(token, url, page=page, per_page=100, **params)
        if not batch:
            break
        results.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return results


# ── Core logic ───────────────────────────────────────────────────────────────

def get_pr(token: str, owner: str, repo: str, pr_number: int) -> dict:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
    return _get(token, url)


def get_comments(token: str, owner: str, repo: str, pr_number: int) -> list[dict]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    return _paginate(token, url)


def has_block_directive(pr: dict, comments: list[dict]) -> bool:
    """Return True if any comment or the PR body contains a block phrase."""
    texts = [pr.get("body") or ""] + [c.get("body") or "" for c in comments]
    combined = "\n".join(texts).lower()
    return any(phrase in combined for phrase in BLOCK_PHRASES)


def get_check_runs(token: str, owner: str, repo: str, ref: str) -> list[dict]:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{ref}/check-runs"
    data = _get(token, url)
    return data.get("check_runs", [])


def all_checks_passed(check_runs: list[dict]) -> tuple[bool, list[str]]:
    """Return (all_passed, list_of_failed_names)."""
    failed = [
        cr["name"]
        for cr in check_runs
        if cr.get("status") == "completed" and cr.get("conclusion") not in ("success", "skipped", "neutral")
    ]
    pending = [cr["name"] for cr in check_runs if cr.get("status") != "completed"]
    if pending:
        return False, [f"(pending) {n}" for n in pending]
    return len(failed) == 0, failed


def enable_auto_merge_graphql(token: str, node_id: str, method: str) -> bool:
    """Enable GitHub auto-merge via GraphQL. Returns True on success."""
    query = """
    mutation EnableAutoMerge($pullRequestId: ID!, $mergeMethod: PullRequestMergeMethod!) {
      enablePullRequestAutoMerge(input: {
        pullRequestId: $pullRequestId,
        mergeMethod: $mergeMethod
      }) {
        pullRequest { number autoMergeRequest { mergeMethod } }
      }
    }
    """
    resp = requests.post(
        "https://api.github.com/graphql",
        headers=_headers(token),
        json={"query": query, "variables": {"pullRequestId": node_id, "mergeMethod": method.upper()}},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("errors"):
        print(f"GraphQL errors: {json.dumps(data['errors'], indent=2)}", file=sys.stderr)
        return False
    return True


def merge_pr(token: str, owner: str, repo: str, pr_number: int, method: str) -> bool:
    """Directly merge the PR. Returns True on success."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/merge"
    resp = requests.put(
        url,
        headers=_headers(token),
        json={"merge_method": method},
        timeout=30,
    )
    if resp.status_code == 200:
        return True
    print(f"Merge API returned {resp.status_code}: {resp.text}", file=sys.stderr)
    return False


# ── Entry point ──────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=textwrap.dedent(__doc__ or ""),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--pr", type=int, default=int(os.environ.get("PR_NUMBER") or 0))
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=os.environ.get("DRY_RUN", "false").lower() == "true",
        help="Check conditions without actually merging.",
    )
    p.add_argument(
        "--merge-method",
        choices=["squash", "merge", "rebase"],
        default=os.environ.get("MERGE_METHOD", "squash"),
    )
    p.add_argument(
        "--skip-check-runs",
        action="store_true",
        help="Skip checking whether all CI checks have passed.",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("❌ GITHUB_TOKEN is not set.", file=sys.stderr)
        return 1

    if not args.repo:
        print("❌ Repository not specified. Use --repo or set GITHUB_REPOSITORY.", file=sys.stderr)
        return 1

    if not args.pr:
        print("❌ PR number not specified. Use --pr or set PR_NUMBER.", file=sys.stderr)
        return 1

    owner, repo = args.repo.split("/", 1)
    pr_number = args.pr

    print(f"🔍 Evaluating PR #{pr_number} in {owner}/{repo} …")

    # 1. Fetch PR
    try:
        pr = get_pr(token, owner, repo, pr_number)
    except requests.HTTPError as exc:
        print(f"❌ Could not fetch PR: {exc}", file=sys.stderr)
        return 1

    if pr.get("state") != "open":
        print(f"ℹ️  PR #{pr_number} is not open (state={pr.get('state')}). Nothing to do.")
        return 0

    if pr.get("draft"):
        print("⏸  PR is a draft. Auto-merge deferred until marked ready.")
        return 0

    # 2. Check for block directive
    try:
        comments = get_comments(token, owner, repo, pr_number)
    except requests.HTTPError as exc:
        print(f"❌ Could not fetch comments: {exc}", file=sys.stderr)
        return 1

    if has_block_directive(pr, comments):
        print("⛔ Auto-merge blocked: 'don't auto-merge' directive found in PR comments or body.")
        return 0  # Not an error — intentional override.

    # 3. Check CI status (optional)
    if not args.skip_check_runs:
        head_sha = pr.get("head", {}).get("sha", "")
        if head_sha:
            try:
                check_runs = get_check_runs(token, owner, repo, head_sha)
                passed, issues = all_checks_passed(check_runs)
                if not passed:
                    print(f"⏳ Not all checks have passed yet:")
                    for issue in issues:
                        print(f"   • {issue}")
                    print("Auto-merge deferred — will retry on next push or status update.")
                    return 0
                print(f"✅ All {len(check_runs)} check run(s) passed.")
            except requests.HTTPError as exc:
                print(f"⚠️  Could not fetch check runs: {exc}. Proceeding anyway.", file=sys.stderr)

    # 4. Attempt auto-merge
    node_id: str = pr.get("node_id", "")
    method = args.merge_method

    if args.dry_run:
        print(f"🔆 Dry run: would enable auto-merge ({method}) for PR #{pr_number}.")
        return 0

    # Try GitHub's native auto-merge first (respects branch protection).
    print(f"🔀 Enabling auto-merge ({method}) for PR #{pr_number} …")
    if node_id and enable_auto_merge_graphql(token, node_id, method):
        print(f"✅ Auto-merge enabled. GitHub will merge PR #{pr_number} when all required checks pass.")
        return 0

    # Fall back to direct merge if auto-merge feature is not available.
    print("⚠️  GraphQL auto-merge unavailable. Attempting direct merge …")
    if merge_pr(token, owner, repo, pr_number, method):
        print(f"✅ PR #{pr_number} merged directly ({method}).")
        return 0

    print(
        f"❌ Could not merge PR #{pr_number}.\n"
        "Possible reasons:\n"
        "  • Branch protection checks are still pending.\n"
        "  • 'Allow auto-merge' is not enabled in repo settings.\n"
        "  • Insufficient token permissions (needs 'contents: write').",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
