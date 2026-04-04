# Connection Guide: Codespace Infrastructure & External Agent Integration

## Quick Overview

This Codespace provides a **self-hosted AI toolkit** accessible to both local and remote agents. All services are containerized and exposed via GitHub Codespace URLs.

**Codespace Name**: `curly-space-spork-v9rg679gpqw3rj6`

---

## 🌐 Service URLs & Connectivity

### From THIS Codespace (Internal)

Use localhost addresses for local CLI/tool invocation:

| Service                | Internal URL             | Port  | Protocol |
| ---------------------- | ------------------------ | ----- | -------- |
| **n8n**                | `http://localhost:5678`  | 5678  | HTTP     |
| **PostgreSQL**         | `localhost:5432`         | 5432  | TCP      |
| **Ollama**             | `http://localhost:11434` | 11434 | HTTP     |
| **Qdrant**             | `http://localhost:6333`  | 6333  | HTTP     |
| **GenerateAgents MCP** | stdio (local invocation) | N/A   | stdio    |

### From EXTERNAL Environments (Your Local Machine)

Use Codespace-provided HTTPS URLs:

| Service                | External URL                                                     | API Key / Auth                                               |
| ---------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------ |
| **n8n**                | `https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev`  | `X-N8N-API-KEY: DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d=` |
| **PostgreSQL**         | SSH tunnel required (see below)                                  | user: `root` / pwd: `password`                               |
| **Ollama**             | `https://curly-space-spork-v9rg679gpqw3rj6-11434.app.github.dev` | No auth                                                      |
| **Qdrant**             | `https://curly-space-spork-v9rg679gpqw3rj6-6333.app.github.dev`  | No auth                                                      |
| **GenerateAgents MCP** | Via HTTP bridge (see below)                                      | Codespace token                                              |

---

## 🔧 Connection Patterns by Service

### 1️⃣ **n8n Workflow Automation**

#### **From External Agent (Your Local Machine)**

```bash
# List workflows
curl -X GET "https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev/api/v1/workflows" \
  -H "X-N8N-API-KEY: DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d="

# Create a workflow
curl -X POST "https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev/api/v1/workflows" \
  -H "X-N8N-API-KEY: DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d=" \
  -H "Content-Type: application/json" \
  -d @workflow.json

# Execute a workflow
curl -X POST "https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev/api/v1/workflows/{id}/execute" \
  -H "X-N8N-API-KEY: DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d=" \
  -H "Content-Type: application/json" \
  -d '{"params": {}}'

# Get workflow status
curl -X GET "https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev/api/v1/workflows/{id}" \
  -H "X-N8N-API-KEY: DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d="
```

#### **Python SDK for n8n (External Agent)**

```python
import requests
import json

class N8nClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {'X-N8N-API-KEY': api_key, 'Content-Type': 'application/json'}

    def list_workflows(self, limit: int = 100):
        """List all workflows."""
        response = requests.get(
            f"{self.base_url}/api/v1/workflows",
            params={'limit': limit},
            headers=self.headers
        )
        return response.json()

    def create_workflow(self, name: str, nodes: list, connections: dict):
        """Create a new workflow."""
        response = requests.post(
            f"{self.base_url}/api/v1/workflows",
            json={'name': name, 'nodes': nodes, 'connections': connections},
            headers=self.headers
        )
        return response.json()

    def execute_workflow(self, workflow_id: str, params: dict = None):
        """Execute a workflow."""
        response = requests.post(
            f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
            json={'params': params or {}},
            headers=self.headers
        )
        return response.json()

# Usage from external environment
client = N8nClient(
    api_key='DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d=',
    base_url='https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev'
)

workflows = client.list_workflows()
print(f"Found {len(workflows.get('data', []))} workflows")
```

---

### 2️⃣ **GenerateAgents MCP Server**

#### **From THIS Codespace (Direct Invocation)**

```bash
# List available models
cd /workspaces/self-hosted-ai-starter-kit/generateagents-mcp
uv run python -c "
import asyncio
from server import mcp

async def test():
    result = await mcp.call_tool('list_models', {})
    print(f'Models available: {result}')

asyncio.run(test())
"

# Generate AGENTS.md for a repo
uv run autogenerateagentsmd /path/to/repo --style comprehensive --model gemini/gemini-2.5-pro
```

#### **From External Environment (HTTP Bridge)**

Set up an HTTP bridge to forward requests to the Codespace's MCP server:

```python
# On the Codespace: Start HTTP-enabled MCP server
# In generateagents-mcp/server.py, add:
# mcp.run_http_async(host="127.0.0.1", port=8765)

# Then expose via Codespace port forwarding:
# gh codespace ports visibility 8765:public --codespace curly-space-spork-v9rg679gpqw3rj6

# From external environment:
import requests

class GenerateAgentsMCP:
    def __init__(self, http_url: str):
        self.http_url = http_url.rstrip('/')

    def list_models(self):
        response = requests.post(
            f"{self.http_url}/mcp/tools/list_models",
            json={}
        )
        return response.json()

    def generate_agents(self, repo_path: str, style: str = "comprehensive",
                       model: str = "gemini/gemini-2.5-pro"):
        response = requests.post(
            f"{self.http_url}/mcp/tools/generate_agents",
            json={
                "repo_path": repo_path,
                "style": style,
                "model": model
            }
        )
        return response.json()

# Usage
client = GenerateAgentsMCP("https://curly-space-spork-v9rg679gpqw3rj6-8765.app.github.dev")
models = client.list_models()
```

_Note: HTTP bridge requires additional setup. For now, use the local Codespace invocation directly._

---

### 3️⃣ **PostgreSQL Database**

#### **From Within Codespace**

```bash
# Connect via psql
psql -h localhost -U root -d n8n

# Or via docker
docker exec -it $(docker ps -q -f ancestor=postgres:16-alpine) psql -U root
```

#### **From External Environment (SSH Tunnel)**

```bash
# Step 1: SSH into Codespace
gh codespace ssh --codespace curly-space-spork-v9rg679gpqw3rj6

# Step 2: Forward PostgreSQL port
ssh -L 5432:localhost:5432 user@codespace-host

# Step 3: Connect from your local psql
psql -h localhost -U root -d n8n
```

Or use a single-line tunnel command:

```bash
# Maintain tunnel in background
gh codespace ports forward \
  --codespace curly-space-spork-v9rg679gpqw3rj6 \
  5432:5432

# Then connect
psql -h localhost -U root -d n8n  # password: "password"
```

**Python Connection (External)**:

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",          # After SSH tunnel setup
    user="root",
    password="password",
    database="n8n",
    port=5432
)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM workflows")
print(f"Workflows: {cursor.fetchone()[0]}")
```

---

### 4️⃣ **Ollama (Local LLM Inference)**

#### **From Within Codespace**

```bash
# List available models
curl http://localhost:11434/api/tags

# Generate text
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2", "prompt": "Hello world"}'

# Pull a new model
curl -X POST http://localhost:11434/api/pull \
  -d '{"name": "mistral"}'
```

#### **From External Environment**

```bash
# Pull from Codespace Ollama
curl -X POST https://curly-space-spork-v9rg679gpqw3rj6-11434.app.github.dev/api/pull \
  -H "Content-Type: application/json" \
  -d '{"name": "llama3.2"}'

# Generate using remote Ollama
curl -X POST https://curly-space-spork-v9rg679gpqw3rj6-11434.app.github.dev/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2", "prompt": "What is AI?"}'
```

**Python Client (External)**:

```python
import requests
import json

class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def list_models(self):
        response = requests.get(f"{self.base_url}/api/tags")
        return response.json()['models']

    def generate(self, model: str, prompt: str, stream: bool = False):
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": stream},
            stream=stream
        )
        if stream:
            for line in response.iter_lines():
                if line:
                    yield json.loads(line)
        else:
            return response.json()

# Usage
client = OllamaClient("https://curly-space-spork-v9rg679gpqw3rj6-11434.app.github.dev")
models = client.list_models()
print(f"Available models: {[m['name'] for m in models]}")

# Generate
for chunk in client.generate("llama3.2", "Explain machine learning in 2 sentences"):
    print(chunk['response'], end='', flush=True)
```

---

### 5️⃣ **Qdrant Vector Database**

#### **From Within Codespace**

```bash
# Health check
curl http://localhost:6333/health

# List collections
curl http://localhost:6333/collections

# Create a collection
curl -X PUT http://localhost:6333/collections/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    }
  }'
```

#### **From External Environment**

```python
from qdrant_client import QdrantClient

# Connect to Codespace Qdrant
client = QdrantClient(
    url="https://curly-space-spork-v9rg679gpqw3rj6-6333.app.github.dev"
)

# List collections
collections = client.get_collections()
print(f"Collections: {[c.name for c in collections.collections]}")

# Upsert vectors
client.upsert(
    collection_name="embeddings",
    points=[
        {
            "id": 1,
            "vector": [0.05, 0.61, 0.76, ...],  # 1536 dims for OpenAI embeddings
            "payload": {"title": "Document 1"}
        }
    ]
)

# Search
results = client.search(
    collection_name="embeddings",
    query_vector=[0.05, 0.61, 0.76, ...],
    limit=5
)
```

Install client:

```bash
pip install qdrant-client
```

---

## 🔐 Security & Credential Management

### ⚠️ Important Notes

**API Keys** (NEVER commit to GitHub):

- `N8N_API_KEY`: `DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d=`
- PostgreSQL: `root` / `password`
- All keys in `.env` file (not in repo)

**For Production**:

1. Change default PostgreSQL password immediately
2. Regenerate N8N_ENCRYPTION_KEY and N8N_USER_MANAGEMENT_JWT_SECRET
3. Use environment-specific `.env` files
4. Implement credential rotation policy

### Configure External Agent Credentials

**In your local agent's config**:

```yaml
# config.yaml
codespace:
  name: "curly-space-spork-v9rg679gpqw3rj6"
  domain: "app.github.dev"

services:
  n8n:
    base_url: "https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev"
    api_key: "${N8N_API_KEY}" # Set via environment variable

  ollama:
    base_url: "https://curly-space-spork-v9rg679gpqw3rj6-11434.app.github.dev"
    models:
      - "llama3.2"
      - "mistral"

  qdrant:
    url: "https://curly-space-spork-v9rg679gpqw3rj6-6333.app.github.dev"

  postgres:
    host: "localhost" # After SSH tunnel setup
    port: 5432
    user: "root"
    password: "${POSTGRES_PASSWORD}"
    database: "n8n"

generateagents:
  repo_path: "/workspaces/self-hosted-ai-starter-kit/GenerateAgents.md"
  # Requires direct Codespace CLI access or HTTP bridge
```

**Set environment variables**:

```bash
# In your local shell before running agent
export N8N_API_KEY="DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d="
export POSTGRES_PASSWORD="password"
export CODESPACE_NAME="curly-space-spork-v9rg679gpqw3rj6"
export OLLAMA_BASE_URL="https://curly-space-spork-v9rg679gpqw3rj6-11434.app.github.dev"

# Run your agent
python my_agent.py
```

---

## 🧪 Quick Test Commands (Use in Your Local Terminal)

```bash
# 1. Test n8n access
curl -I -H "X-N8N-API-KEY: DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d=" \
  https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev/health

# 2. Test Ollama access
curl -I https://curly-space-spork-v9rg679gpqw3rj6-11434.app.github.dev/api/tags

# 3. Test Qdrant access
curl -I https://curly-space-spork-v9rg679gpqw3rj6-6333.app.github.dev/health

# 4. List n8n workflows
curl -H "X-N8N-API-KEY: DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d=" \
  https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev/api/v1/workflows | jq
```

---

## 📡 Port Forwarding & Connectivity Matrix

| Scenario                       | Method                     | Latency | Setup Complexity  |
| ------------------------------ | -------------------------- | ------- | ----------------- |
| **Local CLI in Codespace**     | Direct (localhost)         | <1ms    | None              |
| **Local CLI to Codespace**     | GitHub URLs (public HTTPS) | ~100ms  | None              |
| **Local Agent → n8n**          | HTTPS via Codespace URL    | ~100ms  | ✅ (this guide)   |
| **Local Agent → Ollama**       | HTTPS via Codespace URL    | ~100ms  | ✅ (this guide)   |
| **Local Agent → PostgreSQL**   | SSH tunnel + local forward | ~100ms  | 🔧 (SSH required) |
| **External CI/CD → Codespace** | Codespace token auth       | ~200ms  | 🔧 (GitHub token) |

---

## 🚀 Example: Complete Local Agent Integration

```python
# my_ai_agent.py
import os
import requests
import json
from typing import Dict, Any

class CodespaceAgent:
    """Agent that coordinates with Codespace infrastructure."""

    def __init__(self):
        self.codespace_name = os.getenv("CODESPACE_NAME", "curly-space-spork-v9rg679gpqw3rj6")
        self.domain = "app.github.dev"
        self.n8n_api_key = os.getenv("N8N_API_KEY")

        # Build base URLs
        self.n8n_url = f"https://{self.codespace_name}-5678.{self.domain}"
        self.ollama_url = f"https://{self.codespace_name}-11434.{self.domain}"
        self.qdrant_url = f"https://{self.codespace_name}-6333.{self.domain}"

    def create_n8n_workflow(self, name: str, nodes: list, connections: dict) -> Dict[str, Any]:
        """Create a workflow in the Codespace n8n."""
        headers = {
            'X-N8N-API-KEY': self.n8n_api_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f"{self.n8n_url}/api/v1/workflows",
            json={'name': name, 'nodes': nodes, 'connections': connections},
            headers=headers
        )
        return response.json()

    def execute_n8n_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow."""
        headers = {'X-N8N-API-KEY': self.n8n_api_key}

        response = requests.post(
            f"{self.n8n_url}/api/v1/workflows/{workflow_id}/execute",
            json={},
            headers=headers
        )
        return response.json()

    def query_ollama(self, model: str, prompt: str) -> str:
        """Query Ollama for completions."""
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        return response.json()['response']

    def store_embeddings(self, collection: str, vectors: list):
        """Store embeddings in Qdrant."""
        response = requests.post(
            f"{self.qdrant_url}/collections/{collection}/points",
            json={"points": vectors}
        )
        return response.status_code == 200

# Usage
if __name__ == "__main__":
    agent = CodespaceAgent()

    # Test connectivity
    print("🚀 Testing Codespace connectivity...")

    # Create a workflow
    workflow = agent.create_n8n_workflow(
        name="Test Workflow",
        nodes=[
            {
                "id": "1",
                "name": "Start",
                "type": "n8n-nodes-base.start",
                "typeVersion": 1,
                "position": [50, 50],
                "parameters": {}
            },
            {
                "id": "2",
                "name": "Set",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3.4,
                "position": [250, 50],
                "parameters": {
                    "assignments": {
                        "assignments": [
                            {"name": "message", "value": "Hello from remote agent!"}
                        ]
                    }
                }
            }
        ],
        connections={
            "Start": {
                "main": [[{"index": 0, "node": "Set", "type": "main"}]]
            }
        }
    )

    if "data" in workflow:
        print(f"✅ Created workflow: {workflow['data']['id']}")

        # Execute it
        execution = agent.execute_n8n_workflow(workflow['data']['id'])
        print(f"✅ Executed workflow: {execution}")
    else:
        print(f"❌ Failed to create workflow: {workflow}")
```

Run it:

```bash
export N8N_API_KEY="DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d="
python my_ai_agent.py
```

---

## 📚 Additional Resources

- **Codespace Docs**: https://docs.github.com/en/codespaces
- **n8n API**: https://docs.n8n.io/api/
- **Ollama API**: https://ollama.ai/docs
- **Qdrant Python Client**: https://qdrant.tech/documentation/sdk-python/
- **GenerateAgents README**: [./GenerateAgents.md/README.md](./GenerateAgents.md/README.md)

---

## 🆘 Troubleshooting

### Connection Timeout from Local Machine

**Problem**: `curl: (7) Failed to connect to curly-space-spork... port 5678`

**Solution**:

1. Verify Codespace is still running: `gh codespace list`
2. Check firewall: Codespace URLs may be blocked by corporate firewalls
3. Try from VPN: Some networks block external HTTPS access
4. Verify URL format: `https://{codespace-name}-{port}.app.github.dev`

### PostgreSQL Connection Refused

**Problem**: `psql: could not resolve host "localhost"`

**Solution**:

1. Set up SSH tunnel first: `gh codespace ports forward 5432:5432`
2. Or use inline tunnel: `gh codespace ports forward --codespace {name} 5432:5432`
3. Test tunnel: `telnet localhost 5432`

### n8n Returns 401/403

**Problem**: `{"message":"unauthorized"}`

**Solution**:

1. Check API key in `.env`: `grep N8N_API_KEY /workspaces/self-hosted-ai-starter-kit/.env`
2. Ensure header format: `X-N8N-API-KEY: {key}` (not Authorization header)
3. Verify not expired: n8n keys don't expire unless explicitly rotated

### Ollama Model Not Found

**Problem**: `{"error": "model 'llama3.2' not found"}`

**Solution**:

1. Pull the model: `curl -X POST https://.../api/pull -d '{"name": "llama3.2"}'`
2. Wait for download (can take 5-10 minutes for large models)
3. Verify available: `curl https://.../api/tags | jq .models`

---

## Version Info

| Component       | Version            | Last Updated |
| --------------- | ------------------ | ------------ |
| n8n             | v2.10.3            | 2026-03-04   |
| PostgreSQL      | 16-alpine          | 2026-03-04   |
| Ollama          | latest             | 2026-03-04   |
| Qdrant          | latest             | 2026-03-04   |
| GenerateAgents  | 0.1.0              | 2026-03-04   |
| Codespace Image | Ubuntu 22.04.5 LTS | 2026-03-04   |
