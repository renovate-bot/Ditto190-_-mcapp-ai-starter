DEVELOPER QUICKSTART
===================

This file contains one-line commands and quick notes for common developer tasks across the repository. Use it as the quick reference when onboarding or scripting development steps.

Prerequisites
-------------
- Linux (Ubuntu 22.04+ recommended for Codespaces dev container)
- Docker & docker-compose
- Python 3.12+ (virtualenv recommended)
- Node.js (v18+ recommended) and npm

Quick commands — root / full stack
---------------------------------
Start the self-hosted stack (CPU):

```bash
docker compose up
```

Start with NVIDIA GPU support:

```bash
docker compose up --profile gpu-nvidia
```

Verify docker-compose configuration:

```bash
docker compose config -q
```

GenerateAgents.md (Python CLI)
-----------------------------
Install / dev setup:

```bash
cd GenerateAgents.md
uv sync --extra dev
```

Run the CLI against a repo (comprehensive):

```bash
uv run autogenerateagentsmd /path/to/repo --style comprehensive
```

Run non-e2e tests:

```bash
cd GenerateAgents.md
uv run pytest -m 'not e2e' -q
```

generateagents-mcp (MCP server)
--------------------------------
Setup / register clients:

```bash
cd generateagents-mcp
uv sync
python setup.py all
```

Run server (dev):

```bash
python server.py
# or: uv run server.py
```

Prompt Registry (VS Code extension)
----------------------------------
Install & build:

```bash
cd prompt-registry
npm install
npm run compile   # fast smoke test
# or: npm run build
```

Run tests (may trigger VS Code integration download):

```bash
npm test
```

Awesome Copilot (agents & skills)
--------------------------------
Install & build:

```bash
cd awesome-copilot
npm ci
npm run build
```

Validation & generation:

```bash
npm run skill:validate
npm run plugin:validate
```

n8n (workflows & demo data)
---------------------------
Dev notes:
- Templates and demo workflows live in `n8n/demo-data/workflows/` and `n8n/demo-data/credentials/`.

Start n8n locally (part of docker compose stack):

```bash
# With docker compose started above, n8n is available at http://localhost:5678
```

Secrets & environment variables
--------------------------------
- Copy `.env.example` to `.env` and fill required API keys and secrets before running the stack.
- Never commit `.env` or secrets to the repository.

Common gotchas
--------------
- `prompt-registry`'s full `npm test` may attempt to download VS Code integration during tests — prefer `npm run compile` for fast checks.
- `awesome-copilot` plugin validation can fail on manifest changes; use `npm run build` to generate marketplace files.
- Running LLM analysis (GenerateAgents.md) against private code will send source to APIs — obtain permission and sanitize secrets.

If you'd like, I can add smaller, component-specific quickstarts (e.g., `GenerateAgents-QUICK.md`) or commit hooks to enforce `.env` rules.