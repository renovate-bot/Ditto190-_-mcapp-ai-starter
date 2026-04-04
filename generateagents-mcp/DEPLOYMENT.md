# GenerateAgents MCP Deployment & Integration Guide

**Status**: Complete MCP server scaffold with 5 tools, client configs, and OpenAI spec  
**Last Updated**: 2025-03-04

## Quick Start

### 1. Verify Installation

```bash
cd /workspaces/self-hosted-ai-starter-kit
ls -la generateagents-mcp/
```

Expected files:
- `server.py` - MCP server implementation (5 tools exposed)
- `pyproject.toml` - Dependencies
- `README.md` - Full documentation
- Configuration files:
  - `vscode-copilot-mcp-config.json` - VS Code Copilot config
  - `claude-desktop-mcp-config.json` - Claude Desktop config
  - `openai-function-spec.json` - OpenAI Function Calling spec
- Setup helper: `setup.py`
- Integration examples: `integration-examples.py`

### 2. Test the Server (Local Development)

```bash
cd /workspaces/self-hosted-ai-starter-kit/GenerateAgents.md
uv run python ../generateagents-mcp/server.py
```

Expected output:
```
Starting GenerateAgents MCP Server
GenerateAgents repo: /workspaces/self-hosted-ai-starter-kit/GenerateAgents.md
Available tools:
  - list_models()
  - generate_agents(repo_path, style, model, api_base?, api_key?)
  - generate_agents_from_github(repo_url, style, model, analyze_git_history?, api_base?, api_key?)
  - validate_output(project_name)
  - run_tests(include_e2e?)

Starting stdio transport (for VS Code Copilot)...
```

> **Note**: Server runs indefinitely listening on stdio. Press Ctrl+C to stop.

### 3. Register with Clients

#### Option A: Automatic Setup (Recommended)

```bash
cd /workspaces/self-hosted-ai-starter-kit/generateagents-mcp
python setup.py all
```

This configures all detected clients:
- ✓ VS Code Copilot (`.vscode/settings.json`)
- ✓ Claude Desktop (`~/.claude/config.json` or equivalent)
- ✓ Cline extension (`~/.cline/mcp-servers.json`)

#### Option B: Manual Setup

**For VS Code Copilot:**
1. Open `.vscode/settings.json` in your workspace
2. Copy content from `vscode-copilot-mcp-config.json`
3. Save and reload VS Code

**For Claude Desktop:**
1. Locate Claude config:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add entry from `claude-desktop-mcp-config.json`
3. Restart Claude Desktop

### 4. Test the Tools

Once configured, test in your AI assistant:

**VS Code Copilot:**
```
@generateagents-mcp list_models
```

**Claude:**
```
I need to generate AGENTS.md for /tmp/my-repo. Can you use the generate_agents tool?
```

---

## Architecture Overview

### Tool Transport Flow

```
┌─────────────────────────────────────────────────────────────┐
│ AI Assistant (Copilot / Claude / OpenAI)                    │
│ - Sends: Tool list request                                  │
│ - Implements: Function calling protocol                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─► LIST_TOOLS()
                     │   Returns: [Tool schemas in JSON]
                     │
                     ├─► CALL_TOOL(name, params)
                     │   Returns: Structured JSON result
                     │
          ┌──────────┴─────────────────────────────┐
          │                                         │
          ▼                                         ▼
┌─────────────────────────┐          ┌──────────────────────┐
│ MCP Protocol Transport  │          │ Function Calling API │
│ - stdio (localhost)     │          │ - OpenAI             │
│ - HTTP (remote)         │          │ - Anthropic          │
│ - SSE streaming         │          │ - Mistral            │
└──────┬──────────────────┘          └──────────┬───────────┘
       │                                        │
       └────────────────┬───────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │ GenerateAgents MCP Server    │
         │                              │
         │  - server.py (FastMCP)       │
         │  - 5 tools                   │
         │  - Wraps GenerateAgents CLI  │
         │  - JSON schemas              │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │ GenerateAgents.md CLI        │
         │                              │
         │  - uv run autogenerateagentsmd
         │  - Supports 100+ LLM providers
         │  - Local/GitHub repo support │
         │  - RLM-powered analysis      │
         └──────────────────────────────┘
```

---

## Tool Specifications

### Tool 1: `list_models()`
**No parameters**

Returns available models across all providers.

```json
{
  "success": true,
  "provider_count": 10,
  "models": {
    "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-opus", "claude-3-sonnet"],
    "gemini": ["gemini-2.5-pro", "gemini-2.0-flash"],
    ...
  }
}
```

**Use case**: Display available models to end user; let them choose

---

### Tool 2: `generate_agents()`
**Required**: `repo_path` (str)  
**Optional**: `style` ("comprehensive" | "strict"), `model` (str), `api_base` (str), `api_key` (str)

Generates AGENTS.md from a local repository.

```json
{
  "success": true,
  "status": "completed",
  "output_path": "/path/to/projects/flask/AGENTS.md",
  "agents_md_content": "# Agents\n## Architecture\n...",
  "repo_name": "flask"
}
```

**Use case**: Local repos the user has access to; faster than GitHub cloning

---

### Tool 3: `generate_agents_from_github()`
**Required**: `repo_url` (str, HTTPS GitHub URL)  
**Optional**: `style`, `model`, `analyze_git_history` (int), `api_base`, `api_key`

Generates AGENTS.md from a public GitHub repository.

```json
{
  "success": true,
  "status": "completed",
  "output_path": "/path/to/projects/flask/AGENTS.md",
  "agents_md_content": "...",
  "repo_name": "flask",
  "analyzed_commits": 500
}
```

**Use case**: Analyze repos without local clone; extract lessons from git history

---

### Tool 4: `validate_output()`
**Required**: `project_name` (str, repo name)

Validates generated AGENTS.md file.

```json
{
  "project_name": "flask",
  "is_valid": true,
  "file_path": "...",
  "file_size_bytes": 5432,
  "has_agents_section": true,
  "has_architecture_section": true,
  "has_constraints_section": true,
  "issues": []
}
```

**Use case**: Verify generation succeeded; check for missing sections

---

### Tool 5: `run_tests()`
**Optional**: `include_e2e` (bool, default: false)

Runs GenerateAgents test suite.

```json
{
  "success": true,
  "total_tests": 22,
  "passed_tests": 22,
  "failed_tests": 0,
  "skipped_tests": 4,
  "summary": "22 passed, 4 skipped in 45.23s"
}
```

**Use case**: Validate tool functionality; health check before deploying

---

## Platform-Specific Integration

### VS Code Copilot

**Transport**: stdio (local process)  
**Config Location**: `.vscode/settings.json`  
**Status**: ✅ Ready

```json
{
  "[copilot].mcp": {
    "servers": [
      {
        "name": "generateagents-mcp",
        "command": "python",
        "args": ["/workspaces/self-hosted-ai-starter-kit/generateagents-mcp/server.py"],
        "env": {
          "PYTHONPATH": "/workspaces/self-hosted-ai-starter-kit"
        }
      }
    ]
  }
}
```

**How to use**:
```
@generateagents-mcp
Please generate AGENTS.md for https://github.com/pallets/flask
```

---

### Claude Desktop

**Transport**: stdio (local process)  
**Config Location**: `~/.claude/config.json` (varies by OS)  
**Status**: ✅ Ready

```json
{
  "mcpServers": {
    "generateagents-mcp": {
      "command": "python",
      "args": ["/workspaces/self-hosted-ai-starter-kit/generateagents-mcp/server.py"],
      "disabled": false
    }
  }
}
```

**How to use**:
```
Please use the generateagents tools to analyze https://github.com/dspy-modules/dspy
```

---

### OpenAI Function Calling API

**Transport**: REST API (HTTP, must deploy MCP as server)  
**Config Location**: See `openai-function-spec.json`  
**Status**: ⚠️ Requires HTTP deployment

Use the provided `openai-function-spec.json` in your OpenAI API calls:

```python
import json
from openai import OpenAI

# Load tool definitions
with open("openai-function-spec.json") as f:
    spec = json.load(f)

client = OpenAI(api_key="sk-...")
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "user", "content": "Generate AGENTS.md for /tmp/myrepo"}
    ],
    tools=spec["x-openai-functions"],  # <-- Use the spec
    tool_choice="auto"
)

# Check if OpenAI wants to use a tool
if response.stop_reason == "tool_calls":
    for call in response.choices[0].message.tool_calls:
        print(f"Tool: {call.function.name}")
        print(f"Args: {call.function.arguments}")
        # TODO: Dispatch to your MCP server
```

See `integration-examples.py` for complete examples.

---

### Anthropic Claude API

**Transport**: REST API (Claude 3.5+)  
**Status**: ⚠️ Requires API spec conversion

Claude uses a similar tool calling interface. Convert `openai-function-spec.json` to Anthropic format:

```python
from anthropic import Anthropic

# Adapt the OpenAI function spec to Anthropic format
tools = [
    {
        "name": "generateagents_generate_agents",
        "description": "Generate AGENTS.md from a repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string"},
                "style": {"type": "string", "enum": ["comprehensive", "strict"]},
                ...
            },
            "required": ["repo_path"]
        }
    }
]

client = Anthropic(api_key="sk-ant-...")
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Generate AGENTS.md..."}]
)

if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            print(f"Tool: {block.name}, Input: {block.input}")
```

---

### Mistral AI API

**Transport**: REST API (Mistral models support function calling)  
**Status**: ⚠️ Similar to OpenAI

```python
from mistralai.client import MistralClient

client = MistralClient(api_key="...")
response = client.chat(
    model="mistral-large-latest",
    tools=[...],  # Same format as OpenAI
    messages=[...]
)

if response.choices[0].message.tool_calls:
    for call in response.choices[0].message.tool_calls:
        print(f"Tool: {call.function.name}")
```

---

### Ollama (Local)

**Transport**: HTTP (local `localhost:11434`)  
**Status**: ⚠️ No native function calling; use prompt engineering

```python
import ollama

tools_prompt = """Available tools:
1. generateagents_generate_agents(repo_path, style, model)
2. generateagents_list_models()
...
"""

response = ollama.chat(
    model="llama3.2",
    messages=[
        {"role": "user", "content": f"Use these tools: {tools_prompt}..."}
    ]
)

# Parse response to extract tool calls (regex/structured prompt)
# Then dispatch to MCP server
```

---

## Production Deployment

### HTTP Transport Setup

Modify `server.py` to use HTTP instead of stdio:

```python
from mcp.server.httpserver import HTTPServer

if __name__ == "__main__":
    server = HTTPServer(host="0.0.0.0", port=8000)
    mcp.run(server)
```

Or use FastAPI/Uvicorn:

```bash
pip install uvicorn fastapi

# Add to server.py:
if __name__ == "__main__":
    import asyncio
    from fastapi import FastAPI
    from fastapi.responses import StreamingResponse
    
    app = FastAPI()
    
    @app.post("/mcp/tools/list")
    async def list_tools():
        # Return tool definitions
        pass
    
    @app.post("/mcp/tools/call/{tool_name}")
    async def call_tool(tool_name: str, params: dict):
        # Route to appropriate tool
        pass
    
    # Run with: uvicorn server:app --host 0.0.0.0 --port 8000
```

### Deployment Platforms

#### AWS Lambda + API Gateway
1. Package `server.py` as Lambda layer
2. Create Lambda handler that calls MCP tools
3. Expose via API Gateway HTTPS endpoint
4. Update client configs with Lambda URL

#### Google Cloud Run
```bash
docker build -t generateagents-mcp .
gcloud run deploy generateagents-mcp \
  --image generateagents-mcp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
az container create \
  --resource-group mygroup \
  --name generateagents-mcp \
  --image generateagents-mcp \
  --ports 8000 \
  --environment-variables PORT=8000
```

#### Self-hosted (Dokku, Heroku, Render, etc.)
Push repo to platform; Procfile configures HTTP server:
```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

---

## Security Checklist

- [ ] **Rotate API keys** immediately (see GenerateAgents.md `.env.sample`)
  - [ ] OpenAI API key
  - [ ] Anthropic API key
  - [ ] Gemini API key
  - [ ] GitHub token
  - [ ] Any other secrets
  
- [ ] **Never return secrets** from tool outputs (server.py filters this)

- [ ] **Validate inputs**:
  - [ ] `repo_path` must exist and be within allowed directory
  - [ ] `repo_url` must be valid GitHub URL
  - [ ] `model` must be in approved list

- [ ] **Rate limiting** (for production):
  - [ ] Limit calls per user/IP
  - [ ] Timeout long-running generations (already: 10 min local, 15 min GitHub)

- [ ] **Logging & monitoring**:
  - [ ] Log all tool invocations
  - [ ] Monitor error rates
  - [ ] Alert on failures

- [ ] **HTTPS only** in production

- [ ] **Authentication**:
  - [ ] Require API key for MCP server access (if remote)
  - [ ] Or restrict to private network (VPN, VPC)

---

## Troubleshooting

### Server won't start
```bash
# Check Python version (must be 3.12+)
python --version

# Check mcp library
pip show mcp

# Run with verbose logging
LOG_LEVEL=DEBUG python server.py
```

### Tools not appearing in Copilot
- Restart VS Code after updating config
- Verify `.vscode/settings.json` syntax (use VS Code JSON validator)
- Check MCP server logs: `grep "error\|warning" ~/.mcp.log`

### Timeouts
- Local Ollama models timeout on RLM reasoning
- Solution: Use cloud models (Gemini, OpenAI, Anthropic)
- Or increase timeout in `run_command()`: `timeout=600` → `timeout=1200`

### "GenerateAgents CLI not found"
```bash
cd GenerateAgents.md
uv sync
uv run autogenerateagentsmd --help
```

---

## Next Steps

1. **Rotate secrets** in GenerateAgents.md/.env
2. **Test tools locally** with setup.py
3. **Deploy MCP server** to production (HTTP transport)
4. **Register** with OpenAI/Anthropic/Mistral APIs
5. **Monitor usage** and performance
6. **Iterate** based on user feedback

---

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-a-bot#use-with-tools)
- [GenerateAgents.md](../GenerateAgents.md/README.md)

---

## Support

For issues, questions, or feature requests:
- Check [README.md](./README.md) for tool documentation
- Review [integration-examples.py](./integration-examples.py) for code examples
- See [CONTRIBUTING.md](../CONTRIBUTING.md) in parent repo
