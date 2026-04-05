---
name: ac-devops
description: >
  Manage Docker, environment configuration, and infrastructure for the awesome-copilot dev stack.
  Use when asked to start the docker stack, configure environment variables, manage .env settings,
  fix docker-compose issues, set up Ollama, Qdrant, n8n, Postgres, or manage devcontainer setup.
  Triggers: 'docker compose', 'start stack', 'environment variables', '.env config',
  'docker stack', 'devcontainer', 'ollama setup', 'n8n config', 'infrastructure'.
---

# AC DevOps Skill

Manage Docker Compose stack, environment configuration, and devcontainer infrastructure.

## When to Use This Skill

- Starting or stopping the Docker stack (`docker compose up`)
- Configuring `.env` variables for the stack
- Setting up or troubleshooting n8n, Qdrant, Postgres, or Ollama
- Updating devcontainer configuration
- Generating secure secrets

## Prerequisites

- Docker and docker-compose available
- `.env` file configured (from `.env.example`)

## Step-by-Step Workflows

### Start the stack (CPU mode)

```bash
cd /workspaces/mcapp-ai-starter
cp .env.example .env  # first time only — edit with your secrets
docker compose up -d
sleep 30
docker compose ps
```

### Generate secrets

```bash
openssl rand -base64 32  # N8N_ENCRYPTION_KEY
openssl rand -base64 32  # N8N_USER_MANAGEMENT_JWT_SECRET
```

### Health check

```bash
bash .devcontainer/scripts/health-check.sh
```

### Validate docker-compose config

```bash
docker compose config -q && echo "OK"
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `POSTGRES_PASSWORD` | Yes | PostgreSQL password |
| `N8N_ENCRYPTION_KEY` | Yes | n8n encryption (32+ chars) |
| `N8N_USER_MANAGEMENT_JWT_SECRET` | Yes | JWT secret (32+ chars) |
| `OPENAI_API_KEY` | Optional | LLM provider |
| `ANTHROPIC_API_KEY` | Optional | LLM provider |
| `GEMINI_API_KEY` | Optional | LLM provider |

## Important Notes

- NEVER commit `.env` to git
- n8n API uses `X-N8N-API-KEY` header, NOT `Authorization: Bearer`
- Default n8n URL: `http://localhost:5678`
