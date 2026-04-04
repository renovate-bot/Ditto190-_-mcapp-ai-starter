# GenerateAgents MCP Server

A Model Context Protocol (MCP) server that exposes the GenerateAgents.md CLI as first-class LLM-callable tools for VS Code Copilot, Claude Desktop, and other MCP-compatible AI assistants.

## Overview

The GenerateAgents MCP server bridges the gap between the GenerateAgents.md CLI tool and AI assistants by:
- Exposing 5 core GenerateAgents functions as MCP tools with JSON schemas
- Handling tool execution, error handling, and output structuring
- Supporting both local and remote deployment via stdio/HTTP transports
- Integrating with VS Code Copilot, Claude Desktop, and OpenAI Function Calling

## Installation

### Prerequisites
- Python 3.12+
- GenerateAgents.md repository cloned to `../GenerateAgents.md`
- `uv` package manager installed

### Setup

```bash
cd /workspaces/self-hosted-ai-starter-kit/generateagents-mcp
pip install -e .
# or with uv:
uv sync
```

## Tool Reference

### 1. `list_models()`
Lists all available language models across 100+ providers (OpenAI, Anthropic, Gemini, Ollama, etc.).

**Returns:**
```json
{
  "success": true,
  "provider_count": 10,
  "models": {
    "openai": ["gpt-4", "gpt-4-turbo", ...],
    "anthropic": ["claude-3-opus", ...],
    ...
  }
}
```

---

### 2. `generate_agents(repo_path, style, model, api_base?, api_key?)`
Generates AGENTS.md from a local repository.

**Parameters:**
- `repo_path` (str): Absolute path to local repository
- `style` (str): "comprehensive" or "strict" (default: "comprehensive")
- `model` (str): Model identifier like "gemini/gemini-2.5-pro" (default: "gemini/gemini-2.5-pro")
- `api_base` (str, optional): Custom API base URL
- `api_key` (str, optional): API key (never returned in output)

**Returns:**
```json
{
  "success": true,
  "status": "completed",
  "output_path": "/path/to/projects/repo_name/AGENTS.md",
  "agents_md_content": "# Agents\n...(first 1000 chars)...",
  "repo_name": "repo_name"
}
```

---

### 3. `generate_agents_from_github(repo_url, style, model, analyze_git_history?, api_base?, api_key?)`
Generates AGENTS.md from a public GitHub repository (clones it automatically).

**Parameters:**
- `repo_url` (str): Full GitHub URL (e.g., "https://github.com/owner/repo")
- `style` (str): "comprehensive" or "strict"
- `model` (str): Model identifier
- `analyze_git_history` (int, optional): Number of recent commits to analyze for anti-patterns (e.g., 500)
- `api_base` (str, optional): Custom API base URL
- `api_key` (str, optional): API key

**Returns:**
```json
{
  "success": true,
  "status": "completed",
  "output_path": "...",
  "agents_md_content": "...",
  "repo_name": "repo",
  "analyzed_commits": 500
}
```

---

### 4. `validate_output(project_name)`
Validates that AGENTS.md was generated correctly for a project.

**Parameters:**
- `project_name` (str): Project name (repository name)

**Returns:**
```json
{
  "project_name": "flask",
  "is_valid": true,
  "file_path": "/path/to/projects/flask/AGENTS.md",
  "file_size_bytes": 5432,
  "has_agents_section": true,
  "has_architecture_section": true,
  "has_constraints_section": true,
  "issues": []
}
```

---

### 5. `run_tests(include_e2e?)`
Runs the GenerateAgents test suite to validate tool functionality.

**Parameters:**
- `include_e2e` (bool): Include end-to-end tests requiring API keys (default: false)

**Returns:**
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

---

### 6. `generate_agentspec(awesome_copilot_path?, output_name?)` — **MVP**

**✅ STATUS: Working with real data (175 agents, 205 skills from awesome-copilot)**

Generates AgentSpec JSON schema by parsing real `.agent.md` and `SKILL.md` files from awesome-copilot.

**Parameters:**
- `awesome_copilot_path` (str, optional): Path to awesome-copilot directory (default: `../awesome-copilot`)
- `output_name` (str, optional): Output filename (default: `awesome-copilot.agentspec.json`)

**Returns:**
```json
{
  "success": true,
  "agent_count": 175,
  "skill_count": 205,
  "output_path": "/path/to/agentspec/generated/awesome-copilot.agentspec.json",
  "agentspec": { ... }
}
```

**Example AgentSpec Output (Real Data):**
```json
{
  "version": "1.0.0",
  "name": "awesome-copilot-agentspec",
  "description": "AgentSpec generated from awesome-copilot agents and skills",
  "source": "/path/to/awesome-copilot",
  "agents": {
    "api-architect": {
      "name": "API Architect",
      "description": "Your role is that of an API architect...",
      "type": "agent",
      "source_file": "/path/to/awesome-copilot/agents/api-architect.agent.md"
    }
  },
  "tools": {
    "terraform-azurerm-set-diff-analyzer": {
      "name": "terraform-azurerm-set-diff-analyzer",
      "description": "Analyze Terraform plan JSON output for AzureRM Provider...",
      "type": "skill",
      "source_file": "/path/to/awesome-copilot/skills/terraform-azurerm-set-diff-analyzer/SKILL.md"
    }
  }
}
```

---

### 7. `validate_agentspec(agentspec_path)` — **MVP**

Validates AgentSpec JSON file against required schema fields.

**Validation Rules:**
- Required top-level: `version`, `name`, `agents`, `tools`
- Required agent fields: `name`, `description`, `type`, `source_file`
- Required tool fields: `name`, `description`, `type`, `source_file`

**Parameters:**
- `agentspec_path` (str): Path to AgentSpec JSON file

**Returns:**
```json
{
  "success": true,
  "agentspec_path": "/path/to/spec.agentspec.json",
  "is_valid": true,
  "errors": [],
  "error_count": 0
}
```

**Example (invalid spec):**
```json
{
  "success": true,
  "is_valid": false,
  "errors": [
    "Missing required field: version",
    "Missing required field: agents",
    "Agent 'my-agent' missing field: description"
  ],
  "error_count": 3
}
```

---

## Usage

### Local Development (VS Code Copilot)

1. **Start the MCP server:**
   ```bash
   python /workspaces/self-hosted-ai-starter-kit/generateagents-mcp/server.py
   ```
   Or with uv:
   ```bash
   cd /workspaces/self-hosted-ai-starter-kit/generateagents-mcp && uv run server.py
   ```

2. **Register in VS Code Copilot** (see Configuration section below)

3. **Test the tools:**
   ```bash
   # In VS Code Copilot chat, try:
   @generateagents-mcp list_models
   @generateagents-mcp generate_agents /path/to/repo comprehensive gemini/gemini-2.5-pro
   @generateagents-mcp generate_agentspec  # Uses default awesome-copilot path
   @generateagents-mcp validate_agentspec /path/to/agentspec/generated/awesome-copilot.agentspec.json
   ```
   @generateagents-mcp emit_agents /path/to/repo.agentspec.json agents-md,n8n-workflow
   ```

### AgentSpec Workflow (TypeSpec-Inspired Agent Definitions)

AgentSpec enables formal, composable agent architecture definitions that compile to multiple output formats:

```bash
# 1. Generate a starter AgentSpec from your codebase
@generateagents-mcp generate_agentspec /path/to/myrepo
# Output: /path/to/generateagents-mcp/agentspec/generated/myrepo.agentspec.json

# 2. Validate the AgentSpec
@generateagents-mcp validate_agentspec /path/to/mcp/agentspec/generated/myrepo.agentspec.json
# Output: {"success": true, "is_valid": true, "issues": []}

# 3. Emit artifacts (AGENTS.md + n8n workflow)
@generateagents-mcp emit_agents /path/to/mcp/agentspec/generated/myrepo.agentspec.json
# Output: {
#   "emitted": {
#     "agents-md": "/path/.../myrepo.agentspec.AGENTS.md",
#     "n8n-workflow": "/path/.../myrepo.agentspec.n8n.workflow.json"
#   }
# }

# 4. Import the generated n8n workflow into your n8n instance
# Or use the AGENTS.md for documentation
```

For more details on AgentSpec design and patterns, see `/docs/agentspec-*.md`.

### Production Deployment (HTTP Transport)

For remote deployment, use HTTP transport:

```python
from mcp.server.httpserver import HTTPServer
mcp.run(HTTPServer(host="0.0.0.0", port=8000))
```

Then register the server with its HTTPS endpoint in client configs.

---

## Configuration

### VS Code Copilot (Local Stdio)

Create or update `.vscode/settings.json` in your workspace:

```json
{
  "copilot.advanced": {
    "debug.testingEnabled": true
  },
  "[copilot].mcp": {
    "servers": [
      {
        "name": "generateagents-mcp",
        "description": "GenerateAgents.md as MCP tools",
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

Or for `uv`-based invocation:

```json
{
  "[copilot].mcp": {
    "servers": [
      {
        "name": "generateagents-mcp",
        "command": "bash",
        "args": ["-c", "cd /workspaces/self-hosted-ai-starter-kit/generateagents-mcp && uv run server.py"],
        "env": {
          "PATH": "/home/codespace/.local/bin:/home/codespace/.deno/bin:$PATH"
        }
      }
    ]
  }
}
```

### Claude Desktop (Local Stdio)

Update `~/.claude_config.json` or equivalent:

```json
{
  "mcp": {
    "servers": [
      {
        "name": "generateagents-mcp",
        "description": "GenerateAgents.md tools",
        "command": "python",
        "args": ["/workspaces/self-hosted-ai-starter-kit/generateagents-mcp/server.py"],
        "disabled": false
      }
    ]
  }
}
```

### OpenAI Function Calling (REST API)

See `openai-function-spec.json` in this directory for integration with OpenAI's Function Calling API.

Example:
```python
import json
from openai import OpenAI

spec = json.load(open("/workspaces/self-hosted-ai-starter-kit/generateagents-mcp/openai-function-spec.json"))

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "user", "content": "Generate AGENTS.md for my repo at /tmp/my-repo"}
    ],
  tools=spec["x-openai-functions"],
    tool_choice="auto"
)
```

---

## AgentSpec Tools (Phase 1: Validation Cascade)

The generateagents-mcp server includes **AgentSpec** tools for agent specification generation, validation, and emission. This section documents the validation cascade pattern inspired by SmallAgents POC.

### `generate_agentspec(repo_path, output_name?)`

Generate a starter AgentSpec from a local repository.

**Parameters:**
- `repo_path` (str): Absolute path to repository
- `output_name` (str, optional): Output filename (default: `{repo_name}.agentspec.json`)

**Returns:**
```json
{
  "success": true,
  "status": "completed",
  "output_path": "/path/to/generated/typespec.agentspec.json",
  "repo_name": "typespec",
  "agent_count": 1,
  "workflow_count": 1,
  "preview": "{...first 1000 chars of spec...}"
}
```

**Example:**
```json
POST /tool/generate_agentspec
{
  "repo_path": "/workspaces/self-hosted-ai-starter-kit/typespec",
  "output_name": "typespec.agentspec.json"
}
```

---

### `validate_agentspec(agentspec_path)`

Validate an AgentSpec against multi-layer validation cascade:

1. **Schema Validation**: Required fields and types (version, agents, workflows)
2. **Naming Conventions**: Agent names must match `lowercase_with_underscores` pattern
3. **Reserved Names Check**: Prevents conflicts with system names (all, default, system, core, builtin)
4. **Tool References**: Tools referenced by agents must be defined in spec
5. **Circular Dependency Detection**: Prevents infinite loops in agent/tool relationships

**Parameters:**
- `agentspec_path` (str): Path to AgentSpec JSON file

**Returns:**
```json
{
  "success": true,
  "status": "completed",
  "agentspec_path": "/path/to/spec.json",
  "is_valid": true,
  "errors": [],
  "error_count_by_type": {}
}
```

**Returns (on validation errors):**
```json
{
  "success": true,
  "status": "completed",
  "agentspec_path": "/path/to/spec.json",
  "is_valid": false,
  "errors": [
    {
      "type": "naming",
      "path": "agents.InvalidAgent",
      "message": "Invalid agent name format. Must be lowercase_with_underscores",
      "params": {
        "pattern": "^[a-z][a-z0-9_]*$",
        "example": "valid_agent_name"
      }
    },
    {
      "type": "reference",
      "path": "agents.valid_agent.tools.undefined_tool",
      "message": "Referenced tool not found in spec: undefined_tool",
      "params": {
        "defined_tools": ["other_tool"]
      }
    }
  ],
  "error_count_by_type": {
    "naming": 1,
    "reference": 1
  }
}
```

**Validation Error Types:**
- `schema`: Missing required fields or incorrect types
- `naming`: Agent/tool names don't match naming conventions
- `reserved`: Agent/tool names use reserved words
- `reference`: Referenced tool doesn't exist in spec
- `circular`: Circular dependency detected in agent/tool relationships

**Example:**
```json
POST /tool/validate_agentspec
{
  "agentspec_path": "/path/to/typespec.agentspec.json"
}
```

---

### `emit_agents(agentspec_path, targets?)`

Emit artifacts from a valid AgentSpec in multiple formats (AGENTS.md, n8n workflows, etc.).

**Parameters:**
- `agentspec_path` (str): Path to AgentSpec JSON file
- `targets` (list[str], optional): Output formats to emit
  - `agents-md`: Emit AGENTS.md documentation
  - `n8n-workflow`: Emit n8n workflow JSON
  - Default: `["agents-md", "n8n-workflow"]`

**Returns:**
```json
{
  "success": true,
  "status": "completed",
  "agentspec_path": "/path/to/spec.json",
  "emitted": {
    "agents-md": "/path/to/spec.AGENTS.md",
    "n8n-workflow": "/path/to/spec.n8n.workflow.json"
  },
  "unsupported_targets": []
}
```

**Returns (on invalid AgentSpec):**
```json
{
  "success": false,
  "status": "error",
  "error_message": "AgentSpec is invalid; cannot emit artifacts",
  "issues": [...validation errors from validate_agentspec...],
  "error_count_by_type": {...}
}
```

**Example:**
```json
POST /tool/emit_agents
{
  "agentspec_path": "/path/to/typespec.agentspec.json",
  "targets": ["agents-md", "n8n-workflow"]
}
```

---

## AgentSpec Complete Workflow

**End-to-end example: generate → validate → emit**

```
1. Generate starter AgentSpec from repository:
   generate_agentspec(
     repo_path="/workspaces/self-hosted-ai-starter-kit/typespec",
     output_name="typespec.agentspec.json"
   )
   → Output: typespec.agentspec.json

2. Validate the generated spec (multi-layer cascade):
   validate_agentspec(
     agentspec_path="/generated/typespec.agentspec.json"
   )
   → Checks: schema, naming, reserved, references, circular deps
   → If is_valid=false, returns detailed error_count_by_type

3. If valid, emit artifacts:
   emit_agents(
     agentspec_path="/generated/typespec.agentspec.json",
     targets=["agents-md", "n8n-workflow"]
   )
   → Output: 
     - typespec.agentspec.AGENTS.md (documentation)
     - typespec.agentspec.n8n.workflow.json (executable workflow)
```

---

## Validation Patterns from SmallAgents POC

The AgentSpec validation system implements patterns from the SmallAgents POC:

**Multi-Layer Cascade:**
```
User Input
    ↓
[1] Schema Validation (types, required fields)
    ↓ (FAIL → return structured error)
[2] Naming Convention Check (lowercase_with_underscores)
    ↓ (FAIL → return structured error)
[3] Reserved Names Check (system words)
    ↓ (FAIL → return structured error)
[4] Tool References Validation (defined tools)
    ↓ (FAIL → return structured error)
[5] Circular Dependency Detection
    ↓ (FAIL → return structured error)
All Pass → is_valid=true
```

**Error Reporting:**
- Structured errors with: `type`, `path`, `message`, `params`
- `error_count_by_type` dict for quick assessment
- Full error list for detailed debugging

See [AGENTSPEC_PATTERNS_FROM_SMALLAGENTS_POC.md](./AGENTSPEC_PATTERNS_FROM_SMALLAGENTS_POC.md) for comprehensive pattern documentation.

---

## Security Considerations

⚠️ **Important Security Notes:**

1. **API Keys**: Never pass API keys via the MCP tool parameters in production. Instead:
   - Use environment variables (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)
   - Use credential files in user home directory
   - Use secure key management systems (AWS Secrets Manager, HashiCorp Vault)

2. **Path Sandboxing**: The server validates paths exist but does not currently sandbox directory traversal. For production:
   - Restrict `repo_path` to specific directories
   - Validate paths don't escape allowed regions

3. **Output Filtering**: The server filters out sensitive keys from subprocess environment. However:
   - Review command output for accidental secret leaks
   - Consider logging policies for production deployments

4. **Resource Limits**: Set timeouts appropriately:
   - Local repos: 600 seconds (10 minutes)
   - GitHub clones: 900 seconds (15 minutes)
   - Tests: 600 seconds

---

## Troubleshooting

### "GenerateAgents CLI not found"
Ensure GenerateAgents.md is installed:
```bash
cd ../GenerateAgents.md
uv sync
```

### MCP Server won't start
- Check Python version: `python --version` (must be 3.12+)
- Check mcp package: `pip show mcp`
- Check permissions: `ls -la /workspaces/self-hosted-ai-starter-kit/generateagents-mcp/server.py`

### Tools not appearing in Copilot
- Verify MCP config syntax in `.vscode/settings.json` (JSON validation)
- Restart VS Code or Claude Desktop after config changes
- Check MCP server logs: `grep -i "error\|warning" ~/.mcp.log`

### Generation timeouts
- Local Ollama models may timeout; use cloud providers (Gemini, OpenAI, Anthropic)
- Increase `timeout` parameter in `run_command()` if needed
- Check model availability: `uv run autogenerateagentsmd --list-models`

---

## Development

### Running Tests
```bash
cd generateagents-mcp
uv run pytest tests/ -v
```

### Testing Server Startup with AgentSpec Integration
```bash
uv run pytest tests/test_mcp_server_integration.py -v
```

This integration test validates that the server starts correctly, all tools (including AgentSpec) are discoverable, and the AgentSpec tool chain works end-to-end.

### Testing MCP compliance
Use the MCP Inspector tool (bundled with mcp package):
```bash
mcp dev server.py
```

This opens an interactive inspector where you can test each tool directly.

---

## API Reference

See [openai-function-spec.json](./openai-function-spec.json) for the complete OpenAPI specification of all tools.

---

## License

MIT – See [LICENSE](../LICENSE) in parent directory.

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
