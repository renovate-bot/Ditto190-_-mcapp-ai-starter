# n8n — AGENTS.md (folder guidance)

Purpose
-------
Folder-scoped guidance for working with the `n8n/` demo workflows and integration with the self-hosted stack.

What to read first
------------------
- `n8n/demo-data/workflows/` — template workflows that are loaded by the stack
- `n8n/demo-data/credentials/` — demo credentials (encrypted when imported)
- Root `.env.example` — required environment variables for n8n (N8N_HOST, N8N_API_KEY, encryption keys)

Quick commands
--------------
Start the full stack (includes n8n):

```bash
docker compose up
```

If running n8n locally for development, ensure `N8N_HOST` and `N8N_API_KEY` are set in `.env`.

How agents interact
--------------------
- Agents create or execute workflows using the n8n HTTP API:
  - List workflows: `GET /api/v1/workflows` (Authorization: Bearer {N8N_API_KEY})
  - Create workflow: `POST /api/v1/workflows` with workflow JSON
  - Execute workflow: `POST /api/v1/workflows/{id}/execute`

Conventions
-----------
- Keep demo workflows small and well-documented in `n8n/demo-data/workflows/`.
- Credentials stored in `n8n/demo-data/credentials/` must be encrypted using the repository's `N8N_ENCRYPTION_KEY`.

Tips & pitfalls
--------------
- Codespace or container URLs may change — update `N8N_HOST` in `.env` when that happens.
- Do not commit production credentials into `n8n/demo-data/credentials/` (the demo directory is for templates only).
