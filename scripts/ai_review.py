#!/usr/bin/env python3
"""ai_review.py — Low-cost AI code review using GitHub Models API.

Fetches the PR diff, sends a focused prompt to a cheap LLM, and writes
a PASS / FAIL / SKIP verdict to ``$GITHUB_OUTPUT`` (GitHub Actions format).

On FAIL the script also posts a review comment to the PR explaining the issue.
On SKIP (API unavailable, empty diff, etc.) the auto-merge gate continues.

Cost controls
-------------
• Only the first 4 000 characters of the diff are sent (~1 000 tokens).
• The model is fixed to ``gpt-4o-mini`` by default (cheapest GitHub model).
• ``max_tokens`` is capped at 200 so responses are always concise.
• Set ``AI_REVIEW_SKIP=true`` (repo variable) to disable entirely.

Environment variables
---------------------
  GITHUB_TOKEN          Actions token or PAT (required).
  GITHUB_REPOSITORY     owner/repo (required).
  PR_NUMBER             Pull request number (required).
  AI_REVIEW_MODEL       Override model name (default: gpt-4o-mini).
  AI_REVIEW_SKIP        Set to "true" to skip AI review (default: false).
  GITHUB_OUTPUT         Path to GitHub Actions output file (auto-set).
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import requests

# ── Configuration ─────────────────────────────────────────────────────────────

GITHUB_API = "https://api.github.com"
GITHUB_MODELS_API = "https://models.inference.ai.azure.com"

GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
REPO: str = os.environ.get("GITHUB_REPOSITORY", "")
PR_NUMBER_STR: str = os.environ.get("PR_NUMBER", "")
MODEL: str = os.environ.get("AI_REVIEW_MODEL", "gpt-4o-mini")
SKIP: bool = os.environ.get("AI_REVIEW_SKIP", "false").lower() == "true"
GITHUB_OUTPUT: str = os.environ.get("GITHUB_OUTPUT", "")

# Only send the first N characters of the diff to keep token usage low.
DIFF_MAX_CHARS = 4_000

REVIEW_PROMPT = """\
You are a senior code reviewer. Analyse the diff below and respond ONLY with \
valid JSON in this exact format:

  {{"verdict": "PASS" | "FAIL", "reason": "<one concise sentence>"}}

Rules — respond FAIL only for:
  1. Hardcoded secrets, passwords, or API keys.
  2. Obvious critical security vulnerabilities (SQL injection, XSS, SSRF, etc.).
  3. Syntax errors that would prevent the code from running.
  4. Breaking API changes (public interfaces removed or changed without a version bump).

Respond PASS for everything else (style, minor bugs, performance, etc. are NOT a reason to FAIL).

Diff:
{diff}
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _gh_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def set_output(key: str, value: str) -> None:
    """Write a key=value pair to the GitHub Actions output file."""
    if GITHUB_OUTPUT:
        with open(GITHUB_OUTPUT, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")
    # Also echo for log visibility.
    print(f"[output] {key}={value}")


def get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """Fetch the unified diff for a PR."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
    resp = requests.get(
        url,
        headers={**_gh_headers(), "Accept": "application/vnd.github.v3.diff"},
        timeout=30,
    )
    resp.raise_for_status()
    diff = resp.text
    if len(diff) > DIFF_MAX_CHARS:
        diff = diff[:DIFF_MAX_CHARS] + "\n\n... [diff truncated — only first 4 000 chars sent]"
    return diff


def call_github_models(diff: str) -> dict[str, Any]:
    """Call the GitHub Models (Azure inference) endpoint and return parsed JSON."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": REVIEW_PROMPT.format(diff=diff)}],
        "max_tokens": 200,
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(
        f"{GITHUB_MODELS_API}/chat/completions",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    content: str = resp.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def post_pr_comment(owner: str, repo: str, pr_number: int, body: str) -> None:
    """Post a comment on the given PR. Logs a warning on failure but does not raise."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    try:
        resp = requests.post(url, headers=_gh_headers(), json={"body": body}, timeout=30)
        resp.raise_for_status()
    except requests.HTTPError as exc:
        print(f"::warning::Could not post PR comment ({exc}). The verdict is still recorded.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    # Bail out early on missing configuration.
    if not GITHUB_TOKEN:
        print("::warning::GITHUB_TOKEN not set — skipping AI review.")
        set_output("verdict", "SKIP")
        return 0

    if SKIP:
        print("AI_REVIEW_SKIP=true — AI review disabled.")
        set_output("verdict", "SKIP")
        return 0

    if not REPO or not PR_NUMBER_STR:
        print("::warning::GITHUB_REPOSITORY or PR_NUMBER not set — skipping AI review.")
        set_output("verdict", "SKIP")
        return 0

    owner, repo = REPO.split("/", 1)
    pr_number = int(PR_NUMBER_STR)

    print(f"🤖 AI review: {owner}/{repo} PR #{pr_number} using model={MODEL}")

    # Fetch diff.
    try:
        diff = get_pr_diff(owner, repo, pr_number)
    except requests.HTTPError as exc:
        print(f"::warning::Could not fetch PR diff ({exc}) — skipping AI review.")
        set_output("verdict", "SKIP")
        return 0

    if not diff.strip():
        print("Empty diff — nothing to review.")
        set_output("verdict", "PASS")
        return 0

    # Call LLM.
    try:
        result = call_github_models(diff)
        verdict: str = result.get("verdict", "PASS").upper()
        reason: str = result.get("reason", "")
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        print(f"::warning::GitHub Models API returned {status} — skipping AI review.")
        set_output("verdict", "SKIP")
        return 0
    except (json.JSONDecodeError, KeyError, Exception) as exc:
        print(f"::warning::AI review parsing error ({exc}) — skipping.")
        set_output("verdict", "SKIP")
        return 0

    print(f"Verdict: {verdict} — {reason}")
    set_output("verdict", verdict)

    if verdict == "FAIL":
        comment = (
            "## 🤖 AI Review — Auto-Merge Gate\n\n"
            f"❌ **FAIL**: {reason}\n\n"
            "Please address the issue above, or ask a human reviewer to override "
            "with an approval. The auto-merge gate will re-run on the next push.\n\n"
            f"_Model: `{MODEL}` · Diff size: {len(diff):,} chars_"
        )
        post_pr_comment(owner, repo, pr_number, comment)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
