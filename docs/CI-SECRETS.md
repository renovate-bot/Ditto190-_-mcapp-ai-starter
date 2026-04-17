CI & Secrets Guide for Copilot MCP Integration

Purpose
- Instruct how to store and use CONTEXTSTREAM_API_KEY in CI (GitHub Actions) without committing secrets.

Recommendations
- Use GitHub repository secrets (Settings → Secrets → Actions) to store keys securely. Name the secret: CONTEXTSTREAM_API_KEY
- In GitHub Actions workflows, reference the secret as `${{ secrets.CONTEXTSTREAM_API_KEY }}` and export it to the environment before running tools that need it.

Example workflow snippet

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up env for Copilot MCP
        run: |
          echo "CONTEXTSTREAM_API_KEY=${{ secrets.CONTEXTSTREAM_API_KEY }}" >> $GITHUB_ENV
      - name: Start/Use Copilot CLI with MCP config
        run: |
          # Copilot CLI will read .copilot/mcp-config.json in the repo root
          copilot --version

Local dev
- Keep local `.env` with your keys for convenience. Ensure `.gitignore` contains `.env` (this repo already does).
- Load local env: `set -o allexport && source .env && set +o allexport`

Secret rotation
- If a secret is exposed, rotate it immediately in the provider (ContextStream dashboard) and update the secret in GitHub.
- Remove old secrets from git history if previously committed: use `git filter-repo` or `BFG Repo Cleaner`.

Validation
- To validate access from CI, add a step that runs a curl -I to the contextstream MCP URL or runs a lightweight Copilot CLI `/mcp list` command if available.

Contact
- Document owner: repo admin
