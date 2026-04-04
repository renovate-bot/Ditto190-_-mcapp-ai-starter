# Quick Start: Connect External Agent to Codespace

**Codespace Name**: `curly-space-spork-v9rg679gpqw3rj6`

## 🚀 30-Second Setup

### Step 1: Export Credentials
```bash
# On your local machine
export N8N_API_KEY="<N8N_API_KEY>"
export CODESPACE_NAME="curly-space-spork-v9rg679gpqw3rj6"
```

### Step 2: Copy the Python Helper
```bash
# Copy codespace_agent.py to your project
cp /workspaces/self-hosted-ai-starter-kit/codespace_agent.py ./
```

### Step 3: Use in Your Agent
```python
from codespace_agent import CodespaceAgent

# Initialize
agent = CodespaceAgent(
    codespace_name="curly-space-spork-v9rg679gpqw3rj6",
    n8n_api_key="<N8N_API_KEY>"
)

# Use services
workflows = agent.n8n.list_workflows()
response = agent.ollama.generate("llama3.2", "Hello!")
agent.qdrant.upsert("embeddings", points=[...])
```

---

## 📋 Service URLs (Copy-Paste)

### n8n
```
Base: https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev
API Key: <N8N_API_KEY>
Header: X-N8N-API-KEY
```

### Ollama
```
Base: https://curly-space-spork-v9rg679gpqw3rj6-11434.app.github.dev
Models: llama3.2, mistral, neural-chat
```

### Qdrant
```
Base: https://curly-space-spork-v9rg679gpqw3rj6-6333.app.github.dev
Default Collection: embeddings
```

---

## 🧪 Quick Test

```bash
# Test n8n
curl -H "X-N8N-API-KEY: DXx4zJ8kL2m9vQ5bR3tY7wNpH6sC1eF0oX2yZ9aB4d=" \
  https://curly-space-spork-v9rg679gpqw3rj6-5678.app.github.dev/api/v1/workflows | jq

# Test Ollama
curl https://curly-space-spork-v9rg679gpqw3rj6-11434.app.github.dev/api/tags | jq

# Test Qdrant
curl https://curly-space-spork-v9rg679gpqw3rj6-6333.app.github.dev/health | jq
```

---

## 📖 Full Documentation

See:
- **CONNECTION_GUIDE.md** - Detailed setup for all services
- **codespace.config** - Configuration template
- **codespace_agent.py** - Python SDK with examples

---

## 🔐 Security Notes

⚠️ **Never commit API keys to GitHub!**

Set credentials via environment variables:
```bash
export N8N_API_KEY="..."
export POSTGRES_PASSWORD="..."
```

In CI/CD, use GitHub Secrets:
```yaml
# .github/workflows/agent.yml
env:
  N8N_API_KEY: ${{ secrets.CODESPACE_N8N_API_KEY }}
```

---

## ❓ Common Questions

**Q: Can I access PostgreSQL remotely?**  
A: Yes, but requires SSH tunnel setup. See CONNECTION_GUIDE.md for details.

**Q: How do I integrate with my local LLM?**  
A: Use the Ollama client. Models are downloaded on-demand via `pull_model()`.

**Q: What if the Codespace shuts down?**  
A: Restart with `gh codespace resume --codespace curly-space-spork-v9rg679gpqw3rj6`

**Q: Can multiple agents connect simultaneously?**  
A: Yes! n8n, Ollama, and Qdrant support concurrent connections.

---

## 📞 Support

- **Codespace Status**: `gh codespace list`
- **View Logs**: `docker compose logs -f n8n` (in Codespace)
- **Stop Services**: `docker compose down` (in Codespace)
- **Restart Services**: `docker compose up` (in Codespace)

