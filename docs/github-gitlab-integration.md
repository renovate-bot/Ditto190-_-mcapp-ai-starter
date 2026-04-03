# GitHub + GitLab Integration Guide

## Architecture overview

```
┌──────────────────────────────────────────────────────────────┐
│  GitHub (source of truth / auto-merge authority)            │
│                                                              │
│  .github/workflows/auto-merge.yml                           │
│    ├── check-override     (scan comments for block phrase)  │
│    ├── rule-checks        (draft?, up-to-date?, secrets?)   │
│    ├── ai-review          (GitHub Models → PASS/FAIL/SKIP)  │
│    ├── enable-auto-merge  (GraphQL enablePullRequestAuto…)  │
│    └── disable-auto-merge (when "don't auto-merge" found)   │
└───────────────────┬──────────────────────────────────────────┘
                    │  mirror (pull every 5 min)
                    ▼
┌──────────────────────────────────────────────────────────────┐
│  GitLab (auxiliary / augmenting)                            │
│                                                              │
│  .gitlab-ci.yml                                             │
│    ├── validate   (configs, shell scripts)                  │
│    ├── test       (Python / npm unit tests)                 │
│    ├── audit      (npm audit, pip-audit)                    │
│    ├── build      (awesome-copilot marketplace)             │
│    ├── auxiliary  ← NEW                                     │
│    │     ├── gl:github-commit-status                        │
│    │     │     Calls GitHub Commit Status API               │
│    │     │     → appears as "gitlab-ci / <project>" badge  │
│    │     └── gl:github-pr-comment-on-failure                │
│    │           Posts summary comment to GitHub PR on fail   │
│    └── notify     (pipeline summary)                        │
└──────────────────────────────────────────────────────────────┘
```

**Decision flow for a typical PR:**

1. Developer opens a PR on GitHub.
2. GitHub Actions (`auto-merge.yml`) runs:
   - Checks for "don't auto-merge" in comments → no block found.
   - Rule-based checks pass (not draft, up-to-date, no secrets).
   - AI review returns PASS (cheap `gpt-4o-mini` call via GitHub Models).
   - GitHub's native auto-merge is enabled on the PR.
3. GitLab CI runs in parallel (mirrored code):
   - Full test matrix, security audits.
   - `gl:github-commit-status` posts `success` to the GitHub commit.
4. GitHub sees all required status checks green → auto-merges the PR.

If the developer comments **"don't auto-merge"** on the PR:
- `auto-merge.yml` detects the phrase, disables auto-merge immediately.
- Re-enables on the next commit push if the comment is gone.

---

## One-time setup (repository administrator)

### GitHub side

**1. Enable auto-merge in repository settings**

```
Repo → Settings → General → Pull Requests → ☑ Allow auto-merge
```

**2. Set up branch protection for `main`**

```
Repo → Settings → Branches → Add branch protection rule
  Branch name pattern: main
  ☑ Require status checks to pass before merging
     Add status checks:
       • "Rule-based checks"          (from auto-merge.yml)
       • "AI review (low-cost)"       (from auto-merge.yml)
       • "gitlab-ci / <project>"      (optional, from GitLab)
  ☑ Require branches to be up to date before merging
  ☑ Do not allow bypassing the above settings
```

**3. (Optional) Repository variable to disable AI review**

If you want to temporarily skip the AI review step:

```
Repo → Settings → Secrets and variables → Actions → Variables
  AI_REVIEW_SKIP = true
```

**4. (Optional) GitLab trigger secret**

If you want GitHub Actions to trigger GitLab pipelines directly:

```
Repo → Settings → Secrets and variables → Actions → Secrets
  GITLAB_TOKEN = <GitLab PAT with api scope>
  GITLAB_PROJECT_ID = <your GitLab project ID>
```

---

### GitLab side

**1. Mirror from GitHub**

```
GitLab project → Settings → Repository → Mirroring repositories
  Mirror direction: Pull
  URL: https://github.com/OWNER/REPO.git   ← replace with your GitHub repo URL
  Authentication: GitHub PAT (repo scope)
  ☑ Only mirror protected branches
```

**2. CI/CD variables**

```
GitLab project → Settings → CI/CD → Variables
```

| Variable | Value | Protected | Masked |
|---|---|---|---|
| `GITHUB_TOKEN_FOR_GITLAB` | GitHub PAT (`repo` scope) | ✅ | ✅ |
| `GITHUB_REPO` | `OWNER/REPO` (e.g. `Ditto190/mcapp-ai-starter`) | | |

With these set, the `gl:github-commit-status` and `gl:github-pr-comment-on-failure` jobs
in the `auxiliary` stage will automatically post results to GitHub.

**3. (Optional) Bot user for GitLab approvals**

If you want GitLab to also enforce approvals via a bot:

1. Create a separate GitLab account (e.g. `auto-merge-bot`).
2. Give it **Developer** access to the project.
3. Generate a **Personal Access Token** with `api` scope.
4. Store as CI variable `BOT_TOKEN` (Protected + Masked).
5. Add bot as a required approver under **Settings → Merge requests → Approvals**.

---

## Auto-merge override

The workflow watches all PR comments (including edits and deletions) for
these case-insensitive phrases:

| Phrase | Effect |
|---|---|
| `don't auto-merge` | Disables auto-merge |
| `dont auto-merge` | Disables auto-merge |
| `do not auto-merge` | Disables auto-merge |
| `no auto-merge` | Disables auto-merge |

**To re-enable auto-merge** after adding an override comment:
- Push a new commit to the PR branch (re-triggers the workflow).
- Or close and re-open the PR.

The workflow scans the **current state** of all comments on each run, so
deleting the override comment and pushing a new commit will re-enable it.

---

## AI review configuration

The AI review step uses the **GitHub Models API** — no extra billing beyond
your GitHub plan (free for public repos; pay-per-token for private repos on
GitHub Enterprise).

| Setting | Default | How to override |
|---|---|---|
| Model | `gpt-4o-mini` | Set `AI_REVIEW_MODEL` secret/variable |
| Max diff | 4 000 chars | Edit `DIFF_MAX_CHARS` in `scripts/ai_review.py` |
| Skip entirely | `false` | Set `AI_REVIEW_SKIP=true` repo variable |

The AI review only **FAILs** on:
- Hardcoded secrets / credentials
- Critical security vulnerabilities (SQLi, XSS, SSRF, …)
- Syntax errors preventing execution
- Breaking public API changes without version bump

Everything else (style, minor bugs, performance) returns **PASS** so the
auto-merge gate is not blocked by subjective feedback.

---

## Scripts reference

| Script | Purpose |
|---|---|
| `scripts/auto_merge.py` | Standalone Python helper — checks conditions and enables/merges a PR via GitHub API. Can be run locally or from any CI. |
| `scripts/ai_review.py` | Low-cost AI review (GitHub Models). Called by `auto-merge.yml`. |
| `scripts/gitlab_report_to_github.py` | GitLab → GitHub bridge. Posts commit status and PR comments from GitLab CI. |

### Running `auto_merge.py` locally

```bash
# Dry run (check conditions, don't merge)
GITHUB_TOKEN=ghp_... python scripts/auto_merge.py \
  --repo Ditto190/mcapp-ai-starter \
  --pr 42 \
  --dry-run

# Actually enable auto-merge
GITHUB_TOKEN=ghp_... python scripts/auto_merge.py \
  --repo Ditto190/mcapp-ai-starter \
  --pr 42
```

### Running `ai_review.py` locally

```bash
GITHUB_TOKEN=ghp_... \
GITHUB_REPOSITORY=Ditto190/mcapp-ai-starter \
PR_NUMBER=42 \
  python scripts/ai_review.py
```

---

## Language stack compatibility

The integration is language-agnostic — it works at the PR/commit level,
not at the language level. The existing CI jobs already handle:

| Language | Tool | Where |
|---|---|---|
| TypeScript / JavaScript | `npm test`, `npm run lint` | `ci.yml`, `repo-ci.yml` |
| Python | `pytest`, `pip-audit` | `gitlab-ci.yml`, `repo-ci.yml` |
| C# / .NET | Add `dotnet test` step as needed | `repo-ci.yml` |
| YAML / Shell | `shellcheck`, `docker compose config` | `gitlab-ci.yml` |

The rule-based check in `auto-merge.yml` scans `.ts`, `.js`, `.py`, `.cs`,
`.json`, `.yml`, `.yaml` files for potential secrets.

---

## Troubleshooting

**Auto-merge not enabling**
- Check that "Allow auto-merge" is turned on in Repo Settings.
- Verify the `GITHUB_TOKEN` has `contents: write` and `pull-requests: write` permissions.
- Check the `enable-auto-merge` job logs for GraphQL errors.

**AI review skipped every time**
- Make sure the `rule-checks` job passes first (AI review depends on it).
- Check if `AI_REVIEW_SKIP` is set to `true` in repository variables.
- Verify the GitHub Models API is accessible from the runner (`curl https://models.inference.ai.azure.com`).

**GitLab status not appearing on GitHub commits**
- Confirm `GITHUB_TOKEN_FOR_GITLAB` and `GITHUB_REPO` are set in GitLab CI variables.
- The pipeline must be a merge request pipeline (`CI_PIPELINE_SOURCE = merge_request_event`).
- Check the `gl:github-commit-status` job logs in GitLab.

**"don't auto-merge" not being detected**
- Comments are scanned case-insensitively; any of the four phrases will trigger it.
- Verify the `check-override` job ran (it only runs on `pull_request` and `issue_comment` events).
- The PR body is also scanned — check it doesn't accidentally contain a block phrase.

---

## Security notes

- `GITHUB_TOKEN_FOR_GITLAB` should be a **fine-grained PAT** scoped to this
  repository only, with `Contents: read` + `Issues: write` + `Commit statuses: write`.
- Never put tokens in workflow files or committed configuration — always use
  GitHub Secrets or GitLab CI Variables.
- The AI review prompt never includes file paths or repository metadata beyond
  the diff itself, limiting exposure of sensitive project structure.
