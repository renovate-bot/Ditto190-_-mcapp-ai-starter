#!/usr/bin/env python3
"""gitlab_report_to_github.py — GitLab CI → GitHub bridge.

Posts GitLab pipeline results back to the corresponding GitHub PR / commit.
Called from the `auxiliary` stage in `.gitlab-ci.yml` so that GitHub can
display GitLab CI outcomes as commit statuses and (on failure) as PR comments.

Modes
-----
  status  (default)  Post a GitHub commit status for the GitLab pipeline.
  review             Post a PR comment summarising the GitLab job results.
  both               Do both in one run.

Required GitLab CI variables (set in Project → Settings → CI/CD → Variables)
-----------------------------------------------------------------------------
  GITHUB_TOKEN_FOR_GITLAB  GitHub PAT with ``repo`` scope.
  GITHUB_REPO              GitHub repository in ``owner/repo`` form
                           (e.g. ``Ditto190/mcapp-ai-starter``).

Auto-set by GitLab CI (no action needed)
-----------------------------------------
  CI_COMMIT_SHA
  CI_COMMIT_REF_NAME
  CI_PIPELINE_URL
  CI_JOB_STATUS          last job status (success / failed / …)
  CI_PIPELINE_STATUS     overall pipeline status if set manually

Usage in .gitlab-ci.yml
-----------------------
  gl:github-status:
    stage: auxiliary
    image: python:3.12-slim
    when: always
    before_script:
      - pip install requests --quiet
    script:
      - python scripts/gitlab_report_to_github.py --mode both
    rules:
      - if: '$CI_PIPELINE_SOURCE == "merge_request_event" && $GITHUB_TOKEN_FOR_GITLAB && $GITHUB_REPO'
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

import requests

GITHUB_API = "https://api.github.com"

# ── Read GitLab CI environment ────────────────────────────────────────────────

GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN_FOR_GITLAB", "")
GITHUB_REPO: str = os.environ.get("GITHUB_REPO", "")  # owner/repo

CI_COMMIT_SHA: str = os.environ.get("CI_COMMIT_SHA", "")
CI_BRANCH: str = os.environ.get("CI_COMMIT_REF_NAME", "")
CI_PIPELINE_URL: str = os.environ.get("CI_PIPELINE_URL", "")
CI_PIPELINE_ID: str = os.environ.get("CI_PIPELINE_ID", "")
CI_PROJECT_NAME: str = os.environ.get("CI_PROJECT_NAME", "gitlab-ci")

# Prefer an explicit override, then fall back to CI_JOB_STATUS.
_raw_status: str = os.environ.get(
    "CI_PIPELINE_STATUS",
    os.environ.get("CI_JOB_STATUS", "success"),
)

# Normalize to GitHub commit-status states.
_GITLAB_TO_GITHUB_STATE: dict[str, str] = {
    "success": "success",
    "passed": "success",
    "failed": "failure",
    "canceled": "error",
    "running": "pending",
    "pending": "pending",
    "skipped": "success",
    "manual": "pending",
}
GITHUB_STATE: str = _GITLAB_TO_GITHUB_STATE.get(_raw_status, "error")


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _check_config() -> bool:
    ok = True
    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN_FOR_GITLAB is not set — cannot report to GitHub.", file=sys.stderr)
        ok = False
    if not GITHUB_REPO or "/" not in GITHUB_REPO:
        print("GITHUB_REPO is not set or invalid (expected owner/repo).", file=sys.stderr)
        ok = False
    return ok


# ── GitHub API calls ──────────────────────────────────────────────────────────

def post_commit_status(owner: str, repo: str) -> None:
    """Post a GitHub commit status for the current GitLab pipeline."""
    if not CI_COMMIT_SHA:
        print("CI_COMMIT_SHA not available — skipping commit status.", file=sys.stderr)
        return

    url = f"{GITHUB_API}/repos/{owner}/{repo}/statuses/{CI_COMMIT_SHA}"
    description = f"GitLab CI: {_raw_status}"
    payload = {
        "state": GITHUB_STATE,
        "description": description[:140],  # GitHub enforces 140-char limit
        "context": f"gitlab-ci / {CI_PROJECT_NAME}",
        "target_url": CI_PIPELINE_URL or None,
    }
    resp = requests.post(url, headers=_headers(), json=payload, timeout=30)
    resp.raise_for_status()
    print(
        f"✅ Posted commit status '{GITHUB_STATE}' to {owner}/{repo}@{CI_COMMIT_SHA[:8]}"
    )


def find_pr_for_branch(owner: str, repo: str, branch: str) -> Optional[dict]:
    """Find an open GitHub PR whose head branch matches `branch`."""
    if not branch:
        return None
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls"
    resp = requests.get(
        url,
        headers=_headers(),
        params={"head": f"{owner}:{branch}", "state": "open"},
        timeout=30,
    )
    resp.raise_for_status()
    prs = resp.json()
    return prs[0] if prs else None


def post_pr_review_comment(owner: str, repo: str, pr_number: int) -> None:
    """Post a GitLab pipeline summary comment on the corresponding GitHub PR."""
    status_emoji = "✅" if GITHUB_STATE == "success" else "❌"
    pipeline_link = f"[Pipeline #{CI_PIPELINE_ID}]({CI_PIPELINE_URL})" if CI_PIPELINE_URL else f"Pipeline #{CI_PIPELINE_ID}"

    body_lines = [
        f"## {status_emoji} GitLab CI Auxiliary Pipeline",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| **Status** | `{_raw_status}` |",
        f"| **Pipeline** | {pipeline_link} |",
        f"| **Branch** | `{CI_BRANCH}` |",
        f"| **Commit** | `{CI_COMMIT_SHA[:8]}` |",
        "",
        "_This report was posted automatically by the GitLab CI auxiliary stage._",
        "_See `.gitlab-ci.yml` and `scripts/gitlab_report_to_github.py` for details._",
    ]
    body = "\n".join(body_lines)

    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    resp = requests.post(url, headers=_headers(), json={"body": body}, timeout=30)
    resp.raise_for_status()
    print(f"✅ Posted review comment to GitHub PR #{pr_number}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["status", "review", "both"],
        default="status",
        help="What to post to GitHub (default: status).",
    )
    args = parser.parse_args()

    if not _check_config():
        # Exit 0 so a missing config doesn't block the overall pipeline.
        return 0

    owner, repo = GITHUB_REPO.split("/", 1)

    if args.mode in ("status", "both"):
        try:
            post_commit_status(owner, repo)
        except requests.HTTPError as exc:
            print(f"⚠️  Could not post commit status: {exc}", file=sys.stderr)

    if args.mode in ("review", "both"):
        if not CI_BRANCH:
            print("CI_COMMIT_REF_NAME not set — cannot find GitHub PR for review comment.")
        else:
            try:
                pr = find_pr_for_branch(owner, repo, CI_BRANCH)
                if pr:
                    post_pr_review_comment(owner, repo, pr["number"])
                else:
                    print(f"No open GitHub PR found for branch '{CI_BRANCH}' — skipping review comment.")
            except requests.HTTPError as exc:
                print(f"⚠️  Could not post PR comment: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
