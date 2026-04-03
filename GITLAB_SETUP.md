# GitLab Setup Guide

> **New to GitLab?** This guide walks you through getting your GitHub repository
> running on GitLab CI/CD, step by step — no prior GitLab experience needed.

## What is GitLab and why use it?

GitLab is a code hosting + CI/CD platform similar to GitHub, but with a more
powerful built-in pipeline system. You can:

- Run automated tests, builds, and security scans on every commit
- Mirror your GitHub repo so both platforms stay in sync automatically
- Use GitLab's free CI runners (Linux, Windows, macOS) without any extra cost
- Schedule weekly dependency audits, deploy pipelines, and more

---

## Option A — Mirror GitHub → GitLab (recommended for beginners)

This is the easiest path. Your code lives on GitHub; GitLab just runs the
pipelines whenever you push.

### Step 1 — Create a GitLab account

1. Go to [gitlab.com](https://gitlab.com) and sign up with your GitHub account.
2. Verify your email.

### Step 2 — Create a new GitLab project from GitHub

1. In GitLab, click **New project** → **Import project** → **GitHub**.
2. Authorize GitLab to access your GitHub account.
3. Find `Ditto190/mcapp-ai-starter` in the list and click **Import**.
4. GitLab will create a copy at `gitlab.com/your-username/mcapp-ai-starter`.

### Step 3 — Enable automatic mirroring (keep repos in sync)

1. In your GitLab project, go to **Settings → Repository → Mirroring repositories**.
2. Click **Add new mirror**.
3. Set **Mirror direction** to **Pull** (GitLab pulls from GitHub).
4. Enter the GitHub URL: `https://github.com/Ditto190/mcapp-ai-starter.git`
5. For authentication, create a **GitHub Personal Access Token** (PAT):
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Scopes needed: `repo` (full repo access)
   - Copy the token
6. Paste the token into GitLab's **Password** field.
7. Click **Mirror repository**.

Every 5 minutes GitLab will pull the latest commits from GitHub and
automatically trigger pipelines. ✅

---

## Option B — Push directly to GitLab

If you want GitLab to be your primary remote:

```bash
# Add GitLab as a second remote in your local clone
git remote add gitlab https://gitlab.com/YOUR_USERNAME/mcapp-ai-starter.git

# Push your branch to both GitHub and GitLab
git push origin  copilot/setup-ai-starter-in-codespace
git push gitlab  copilot/setup-ai-starter-in-codespace
```

---

## Step 4 — Set CI/CD variables (secrets)

GitLab needs the same secrets that are in your `.env` file. Never put real
secrets in `.gitlab-ci.yml` — add them as **CI/CD Variables** instead:

1. GitLab project → **Settings → CI/CD → Variables** → **Add variable**
2. Add these variables (mark as **Protected** + **Masked** where indicated):

| Variable name                    | Where to find the value         | Protect? | Mask? |
|----------------------------------|---------------------------------|----------|-------|
| `N8N_ENCRYPTION_KEY`             | Your `.env` file                | ✅       | ✅    |
| `N8N_USER_MANAGEMENT_JWT_SECRET` | Your `.env` file                | ✅       | ✅    |
| `POSTGRES_PASSWORD`              | Your `.env` file                | ✅       | ✅    |
| `OPENAI_API_KEY`                 | [platform.openai.com](https://platform.openai.com) | ✅ | ✅ |
| `ANTHROPIC_API_KEY`              | [console.anthropic.com](https://console.anthropic.com) | ✅ | ✅ |
| `GEMINI_API_KEY`                 | [aistudio.google.com](https://aistudio.google.com) | ✅ | ✅ |

Variables marked **Masked** are hidden in log output so they never appear in
pipeline logs by accident.

---

## Step 5 — Understanding the pipeline stages

The `.gitlab-ci.yml` file in this repo defines these stages:

```
validate → test → audit → build → notify
```

| Stage      | What it does                                                    | Runs when                        |
|------------|-----------------------------------------------------------------|----------------------------------|
| `validate` | Checks JSON configs, `.env.example`, docker-compose, shellcheck | On every push to any branch      |
| `test`     | Runs Python pytest (non-e2e) and npm tests                      | When matching files change       |
| `audit`    | `npm audit` + `pip-audit` security scan                         | On main branch + scheduled       |
| `build`    | Builds awesome-copilot marketplace artifacts                    | On main branch when files change |
| `notify`   | Prints a summary with links                                     | Always, after everything else    |

### Setting up a weekly schedule (dependency audit)

1. GitLab project → **CI/CD → Schedules** → **New schedule**
2. Description: `Weekly dependency audit`
3. Interval: `0 9 * * 1` (Mondays at 9am)
4. Target branch: `main`
5. Click **Save pipeline schedule**

---

## Step 6 — View your pipeline results

- Go to **CI/CD → Pipelines** to see all pipeline runs
- Click any pipeline to see the individual jobs and their logs
- Green ✅ = passed, Red ❌ = failed, Yellow ⚠️ = warning/allowed failure
- Download **artifacts** (like audit JSON files) from the job detail page

---

## Troubleshooting common GitLab CI issues

| Problem | Solution |
|---------|----------|
| `docker-compose: not found` | The docker-compose stage needs the `docker:24-dind` service — check that Docker-in-Docker is enabled for your runner |
| `shellcheck: not found` | Use the `koalaman/shellcheck-alpine:stable` image (already set in the job) |
| `pip-audit: not found` | Make sure the `audit:python` job runs `pip install pip-audit uv` in `before_script` |
| Pipeline never triggers | Check that the mirroring step (Option A, Step 3) is set up correctly |
| Variables not available | Variables set as **Protected** only inject into protected branches — add `main` as a protected branch |

---

## Next level: GitLab → n8n webhook integration

Once your pipeline is running you can connect it to n8n:

1. In n8n, create a new workflow with a **Webhook** trigger node.
2. Copy the webhook URL.
3. In GitLab: **Settings → Webhooks** → paste the URL, tick **Pipeline events**.
4. Now every pipeline completion fires an n8n workflow — you can use this to
   send Slack/Discord notifications, update a database, or trigger further
   automation.
