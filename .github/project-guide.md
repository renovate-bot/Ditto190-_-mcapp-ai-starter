# Copilot Instructions — mcapp-ai-starter

Purpose: provide an on-first-contact summary for Copilot/AI assistants to work efficiently in this repository.

Build / Test / Lint (canonical commands)
- Root SDK (TypeScript):
  - Install: npm install
  - Build SDK: npm run build
  - Build all: npm run build:all
  - Unit tests: npm test
  - Run e2e: npm run test:e2e
  - Build a single example: npm run --workspace examples/<example-name> build
- prompt-registry (TS workspace):
  - Compile: npm run compile (inside prompt-registry)
  - Lint: npm run lint (inside prompt-registry)
- awesome-copilot: npm run build (inside awesome-copilot)
- GenerateAgents / Python tooling:
  - Use 'uv' runtime: uv sync and uv run python verify.py
  - If missing, install project Python deps (see GenerateAgents.md)
- Docker stack:
  - Copy env: cp .env.example .env (do NOT commit .env)
  - Validate compose: docker compose config -q
  - Start stack: docker compose up -d

Running a single test
- Most JS tests use npm test; to run a single jest test: npm test -- -t "<name>" (or run the test script in the relevant workspace).
- For workspace-scoped tests: npm run --workspace <workspace> test -- -t "<name>".
- For GenerateAgents checks: uv run python verify.py (see its output for single-check guidance).

High-level architecture (big-picture)
- Multi-component AI toolkit:
  - src/: MCP Apps TypeScript SDK (App, AppBridge, transports)
  - generateagents-mcp/: Python FastMCP server exposing GenerateAgents tools
  - GenerateAgents.md/: generator CLI and content
  - prompt-registry/: VS Code prompt bundle manager (TypeScript)
  - awesome-copilot/: agent/skill/plugin library (large collection of skills)
  - examples/: example servers and workspace-specific package.json files
  - n8n/: demo workflows and demo-data used in the Docker stack
- Protocols: MCP Apps uses PostMessage transport; host (AppBridge) mediates between View and MCP server tools.
- CI: .github/workflows contains multi-stage CI (build, lint, tests, playright e2e). PRs must pass primary CI and component CI.

Key repo conventions (non-obvious)
- Agent/skill files:
  - SKILL.md files follow lowercase-hyphen naming and live in various 'skills' directories (consolidated_sources/awesome-copilot holds bulk of them).
  - Frontmatter: YAML fields such as name and description are single-quoted when containing colons.
- Worktree multi-agent workflow:
  - Agents use git worktrees for isolated work (see Multi-Agent Development docs in repo).
- Scripts & tools:
  - Prefer uv for Python task runner (uv run ...) rather than plain python in CI and scripts.
- Secrets:
  - Copy .env.example -> .env locally; never commit .env. N8N uses X-N8N-API-KEY header.
- Generation and indexing:
  - A generator script exists at scripts/generate_skills_index.js. Generated outputs: .github/skills-index.json, .github/skills-index.md and .github/skills-tree.md.
  - The index intentionally excludes common vendor paths (.venv, node_modules, migration dumps).

Files to read first when onboarding
- README.md — project overview and quickstart
- DEVELOPER-QUICKSTART.md — per-component commands
- GenerateAgents.md/README.md — generator CLI and Python requirements
- AGENTS.md / CLAUDE.md — agent/instruction guidance for repo-specific agents

Other AI-assistant configs to incorporate
- CLAUDE.md (present)
- AGENTS.md (present)
- .github/agents and .agents/ for agent definitions — treat these as authoritative for agent behavior and permissions

MCP Servers
- This repo runs a Docker stack (n8n, Qdrant, Ollama, Postgres). Ask if Playwright or a headless browser MCP server should be added; otherwise no change.

Short workflow for Copilot agent on first run
1. Read README.md and DEVELOPER-QUICKSTART.md for which components are relevant to the user's question.
2. Run quick validation: npm ci (or npm install) && docker compose config -q.
3. Use .github/skills-index.json to find existing SKILL.md files rather than searching the entire repo.
4. Respect .env handling and do not surface secrets.

What was added
- A concise reference for build/test/lint commands, architecture summary, and repository conventions tailored to Copilot.

If you'd like adjustments, mention areas to expand (e.g., more command examples per workspace, single-test examples per testing framework, or adding CI auto-regeneration of skills index).
