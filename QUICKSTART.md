# Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide gets you up and running with the Self-Hosted AI Starter Kit, whether you're in GitHub Codespaces, a dev container, or running locally.

## Prerequisites

- **Git** (any recent version)
- **Docker** and **Docker Compose** (for the AI stack)
- **Node.js 20+** (for Prompt Registry and Awesome Copilot)
- **Python 3.12+** (for GenerateAgents.md)
- **uv** package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## One-Command Setup

### GitHub Codespaces (Recommended)

```bash
# The dev container auto-installs everything!
# Just wait for post-create commands to complete (~2-3 minutes)

# Verify setup
docker compose config -q && echo "✓ Docker ready"
node -v && echo "✓ Node $(node -v)"
python --version && echo "✓ Python ready"
```

### Local Machine

```bash
# Clone repository
git clone https://github.com/n8n-io/self-hosted-ai-starter-kit
cd self-hosted-ai-starter-kit

# Setup each component
# Follow component-specific instructions below
```

## Component Setup

### 1. Docker Stack (Start First!)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your secrets
nano .env  # Change POSTGRES_PASSWORD, N8N_ENCRYPTION_KEY, etc.

# Start services (CPU mode)
docker compose up -d

# OR with GPU support
docker compose --profile gpu-nvidia up -d

# Verify services
docker compose ps

# Access n8n UI
echo "n8n: http://localhost:5678"
```

### 2. GenerateAgents.md (Core CLI)

```bash
cd GenerateAgents.md

# Install dependencies
uv sync --extra dev

# Set up API key
export GEMINI_API_KEY="your-key-here"

# Test on a sample repository
uv run autogenerateagentsmd . --style comprehensive

# Run tests
uv run pytest -m 'not e2e' -q
```

### 3. generateagents-mcp (MCP Server)

```bash
cd generateagents-mcp

# Install dependencies
uv sync

# Auto-register with AI clients
python setup.py all

# Verify
uv run python verify.py
```

### 4. Prompt Registry (VS Code Extension)

```bash
cd prompt-registry

# Use correct Node version
nvm install
nvm use

# Install dependencies
npm install

# Compile and test
npm run compile
npm run test:unit  # Should see 2536 passing
```

### 5. Awesome Copilot (Agent Library)

```bash
cd awesome-copilot

# Install and build
npm ci
npm run build

# Validate
npm run skill:validate
npm run plugin:validate
```

## Verification Checklist

Run this to confirm everything works:

```bash
# 1. Docker Stack
docker compose ps | grep "healthy"

# 2. GenerateAgents.md
cd GenerateAgents.md && uv run pytest -m 'not e2e' -q

# 3. generateagents-mcp
cd ../generateagents-mcp && uv run python verify.py

# 4. Prompt Registry
cd ../prompt-registry && npm run test:unit

# 5. Awesome Copilot
cd ../awesome-copilot && npm run build
```

## Common Issues

### Docker: Port Already in Use

```bash
# Find and kill process
lsof -ti:5678 | xargs kill -9
```

### Python: Module Not Found

```bash
# Activate virtual environment
source .venv/bin/activate
# Or use uv prefix
uv run python ...
```

### Node: Wrong Version

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Use project version
nvm install && nvm use
```

## Next Steps

### For Developers
1. Read [TECHNICAL-REFERENCE.md](./TECHNICAL-REFERENCE.md)
2. Check [KNOWLEDGE-INDEX.md](./KNOWLEDGE-INDEX.md)
3. Press F5 in prompt-registry to run extension

### For AI Agents
1. Generate AGENTS.md: `uv run autogenerateagentsmd /path/to/project`
2. Use MCP tools in VS Code Copilot
3. Create n8n workflows at http://localhost:5678

### For Contributors
1. Create agents in awesome-copilot/agents/
2. Validate: `npm run skill:validate`
3. Submit PR following [CONTRIBUTING.md](./CONTRIBUTING.md)

## Environment Variables

Create `.env` in project root:

```bash
# PostgreSQL
POSTGRES_USER=root
POSTGRES_PASSWORD=CHANGE_THIS
POSTGRES_DB=n8n

# n8n Security
N8N_ENCRYPTION_KEY=minimum-32-characters
N8N_USER_MANAGEMENT_JWT_SECRET=another-32-chars

# n8n API
N8N_API_KEY=your-api-key-here
N8N_HOST=https://your-host:5678

# LLM Providers
GEMINI_API_KEY=your-key
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
```

Generate strong secrets:
```bash
openssl rand -base64 32
```

## Getting Help

- **Technical Reference**: [TECHNICAL-REFERENCE.md](./TECHNICAL-REFERENCE.md)
- **Knowledge Index**: [KNOWLEDGE-INDEX.md](./KNOWLEDGE-INDEX.md)
- **GitHub Issues**: Report bugs and request features
- **Contributing**: [CONTRIBUTING.md](./CONTRIBUTING.md)

---

_Last updated: March 4, 2026_
