# A.D.A.M. — Agentic Development and Agent Management

An MCP App playground for building, managing, and evolving AI agents, ETL pipelines, and a knowledge management platform. Grounded in the **Dynamic Capabilities Framework**.

## Dynamic Capabilities Framework

| Capability               | Description                                 | A.D.A.M. Feature                         |
| ------------------------ | ------------------------------------------- | ---------------------------------------- |
| **Sensing**              | Identify opportunities and threats          | Agent monitoring, anomaly detection      |
| **Seizing**              | Mobilize resources to capture opportunities | Workflow orchestration, agent spawning   |
| **Transforming**         | Reconfigure resources to adapt              | Code-to-tool pipelines, schema evolution |
| **Integrative Learning** | Absorb and apply knowledge                  | Knowledge base ingestion + search        |

## Features

### 🤖 Agent Factory

- Register agents with capabilities and model preferences
- List and filter agents by status
- Execute agents with task descriptions
- Track execution traces

### 🛠️ Skills Catalog

- Browse all available MCP tools and skills
- Organized by category (factory, catalog, learning, transforming)

### 🔄 ETL Pipelines

- Define data pipelines with source → transform → destination
- Built-in transforms: `extract-code-patterns`, `mdx-to-zod-schema`, `to-composable-tools`, `summarize-and-embed`, `code-to-mcp-tool`
- Monitor pipeline status and records processed

### 📚 Knowledge Base

- Ingest knowledge items (code, docs, schemas, workflows)
- Full-text search across title, content, and tags
- Type-based filtering

## MCP Tools

| Tool               | Description                                      |
| ------------------ | ------------------------------------------------ |
| `list-agents`      | List all agents, optionally filtered by status   |
| `register-agent`   | Register a new agent with capabilities and model |
| `run-agent`        | Execute an agent with a task description         |
| `list-skills`      | Browse the skills/tool catalog                   |
| `ingest-knowledge` | Add knowledge items to the knowledge base        |
| `search-knowledge` | Search the knowledge base                        |
| `create-pipeline`  | Define a new ETL pipeline                        |
| `pipeline-status`  | Get the status of all or a specific pipeline     |

## Development

```bash
# Install dependencies (from repo root)
npm install

# Build
npm run --workspace examples/adam-server build

# Dev mode (watch + serve)
npm run --workspace examples/adam-server dev
```

## Running with an MCP Client

```json
{
  "mcpServers": {
    "adam": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-adam", "--stdio"]
    }
  }
}
```

Or with a local build:

```json
{
  "mcpServers": {
    "adam": {
      "command": "bash",
      "args": [
        "-c",
        "cd ~/code/mcapp-ai-starter/examples/adam-server && npm run build >&2 && node dist/index.js --stdio"
      ]
    }
  }
}
```

## Extending A.D.A.M.

To add new capabilities:

1. **Add a new tool** in `server.ts` using `registerAppTool()`
2. **Add the UI** in `src/mcp-app.tsx` (new tab or new card in an existing tab)
3. **Add to the skills catalog** in the `list-skills` handler
4. **Write a pipeline transform** to automate ingestion into the knowledge base

Use the scaffold helper script for boilerplate:

```bash
node scripts/scaffold-agent.mjs --name "MyNewAgent" --capabilities "sensing,api-monitoring"
```
