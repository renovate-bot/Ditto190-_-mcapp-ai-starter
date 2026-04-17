# Serena + GitHub Actions MCP Integration Plan

## Overview

This document outlines the configuration strategy for integrating Serena's symbolic code tools with GitHub Actions MCP for automated workflow management.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code Copilot                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Plan Agent   │    │ Ask Agent    │    │ Edit Agent   │ │
│  │              │    │              │    │              │ │
│  │ Uses:        │    │ Uses:        │    │ Uses:        │ │
│  │ - Serena     │    │ - GitHub     │    │ - Serena     │ │
│  │ - GitHub     │    │   Docs       │    │   (editing)  │ │
│  │   Actions    │    │ - Memory     │    │              │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                   │                    │         │
└─────────┼───────────────────┼────────────────────┼─────────┘
          │                   │                    │
          ▼                   ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      MCP Layer                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────┐      ┌──────────────────────────┐ │
│  │  Serena (oraios)   │      │  GitHub Actions MCP      │ │
│  │  ─────────────────  │      │  ──────────────────────  │ │
│  │  • find_symbol     │◄────►│  • actions_get           │ │
│  │  • get_symbols     │      │  • actions_list          │ │
│  │  • replace_symbol  │      │  • actions_run_trigger   │ │
│  │  • search_pattern  │      │  • get_file_contents     │ │
│  │  • read_memory     │      │  • create_branch         │ │
│  │  • write_memory    │      │  • create_pull_request   │ │
│  └────────────────────┘      └──────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
          │                               │
          ▼                               ▼
    Local Codebase                   GitHub API
```

## Use Cases

### 1. **Automated Code Analysis → Workflow Creation**

**Workflow:**

```
User: "Analyze Python modules and create a CI workflow"

Plan Agent:
  1. Uses Serena: find_symbol(pattern=".*\\.py", type="module")
  2. Uses Serena: get_symbols_overview(depth=2)
  3. Analyzes test files, identifies test patterns
  4. Uses GitHub Actions: actions_get() to fetch existing workflows
  5. Uses Serena: write_memory() to store analysis
  6. Uses GitHub Actions: create_or_update_file() to create .github/workflows/test.yml
```

### 2. **Symbol-Aware GitHub Actions**

**Workflow:**

```
User: "Create a workflow that runs tests for changed functions"

Plan Agent:
  1. Serena: find_referencing_symbols() to map dependencies
  2. Serena: search_for_pattern(pattern="def test_.*") to find tests
  3. GitHub Actions: actions_list() to see available runners
  4. Generate smart workflow that only runs affected tests
```

### 3. **Documentation Generation from Symbols**

**Workflow:**

```
User: "Generate AGENTS.md from codebase and trigger deployment"

Plan Agent:
  1. Serena: get_symbols_overview() for architecture
  2. GenerateAgents MCP: generate_agents()
  3. Serena: create_or_update_file() to save AGENTS.md
  4. GitHub Actions: create_branch() + create_pull_request()
  5. GitHub Actions: actions_run_trigger() to run docs deployment
```

## Configuration

### Agent Tool Assignments

#### Plan Agent (Architecture + Automation)

```json
"github.copilot.chat.planAgent.additionalTools": [
    "memory",
    "sequentialthinking",
    "context7",
    "github_support_docs_search",
    "n8n-docs",
    "github",  // Full GitHub MCP with Actions
    "mcp_oraios_serena_find_symbol",
    "mcp_oraios_serena_get_symbols_overview",
    "mcp_oraios_serena_find_referencing_symbols",
    "mcp_oraios_serena_search_for_pattern",
    "mcp_oraios_serena_read_memory",
    "mcp_oraios_serena_write_memory"
]
```

#### Ask Agent (Quick Lookups)

```json
"github.copilot.chat.askAgent.additionalTools": [
    "github_support_docs_search",
    "n8n-docs",
    "memory",
    "time",
    "mcp_oraios_serena_find_symbol",
    "mcp_oraios_serena_get_symbols_overview"
]
```

#### Edit Agent (Code Modifications)

```json
"github.copilot.chat.editAgent.additionalTools": [
    "mcp_oraios_serena_replace_symbol_body",
    "mcp_oraios_serena_insert_after_symbol",
    "mcp_oraios_serena_insert_before_symbol",
    "mcp_oraios_serena_rename_symbol",
    "mcp_github2_create_branch",
    "mcp_github2_create_pull_request"
]
```

## Workflow Templates

### Template 1: Symbol Analysis + CI/CD

```yaml
name: Symbol-Aware Testing
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  analyze-symbols:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Serena identifies changed symbols
      - name: Get changed symbols
        id: symbols
        run: |
          # Agent uses Serena to find changed functions
          # Outputs: changed_functions.json

      # Run only affected tests
      - name: Run targeted tests
        run: |
          pytest $(cat changed_functions.json | jq -r '.tests[]')
```

### Template 2: Auto-Documentation

```yaml
name: Generate AGENTS.md
on:
  push:
    branches: [main]
    paths:
      - "src/**/*.py"
      - "generateagents-mcp/**"

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Use GenerateAgents MCP
      - name: Generate AGENTS.md
        run: |
          npx generateagents-mcp generate \
            --repo ${{ github.workspace }} \
            --style comprehensive

      # Commit back
      - name: Commit docs
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "docs: Auto-update AGENTS.md [skip ci]"
          file_pattern: "AGENTS.md"
```

### Template 3: Workflow Health Monitor (Your Existing Pattern)

```yaml
name: Workflow Health Monitor
on:
  schedule:
    - cron: "0 */6 * * *" # Every 6 hours
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - name: Check workflow status
        run: |
          # Uses GitHub Actions MCP: actions_list()
          # Uses Serena: write_memory() to log issues

      - name: Analyze patterns
        run: |
          # Uses Serena: search_for_pattern() in .github/workflows/
          # Identifies anti-patterns

      - name: Create issue if failures
        if: failure()
        run: |
          # Uses GitHub MCP: issue_write()
```

## Memory Organization

Serena uses project-scoped memories. Create these in your workspace:

```
.serena/
├── memories/
│   ├── github-actions-patterns.md      # Common workflow patterns
│   ├── symbol-analysis-cache.md        # Cached symbol relationships
│   ├── test-coverage-map.md            # Symbol → test mapping
│   └── recent-changes.md               # Track modifications
```

## Implementation Steps

1. **Enable Serena Tools for Agents** (settings.json)
2. **Create Serena Memory Structure** (.serena/ directory)
3. **Test Integration** (run sample queries)
4. **Create Workflow Templates** (.github/workflows/)
5. **Document Patterns** (store in Serena memories)

## Expected Benefits

### Context Reduction

- **Before:** Load entire codebase (200k+ tokens)
- **After:** Symbolic navigation (~5k tokens per query)
- **Savings:** 97% reduction in read operations

### Workflow Precision

- **Before:** Run all tests on every change
- **After:** Run only tests for changed symbols
- **Savings:** 80% faster CI/CD

### Knowledge Retention

- **Before:** Re-analyze architecture every time
- **After:** Serena memories cache patterns
- **Savings:** 10x faster subsequent queries

## Example Commands

### For Plan Agent

```
@plan Use Serena to analyze the GenerateAgents.md Python codebase,
      identify all DSPy modules, and create a GitHub Actions workflow
      that runs tests only for changed modules
```

### For Ask Agent

```
@ask What are the main classes in generateagents-mcp/server.py?
     (Uses Serena: get_symbols_overview)
```

### For Edit Agent

```
@edit Refactor the CLI argument parser in GenerateAgents.md/cli.py
      (Uses Serena symbolic editing + creates PR via GitHub Actions MCP)
```

## Next Steps

1. ✅ Review this configuration plan
2. ⬜ Apply settings.json changes
3. ⬜ Create .serena/memories/ structure
4. ⬜ Test Serena tools with @plan agent
5. ⬜ Create first automated workflow
6. ⬜ Store learnings in Serena memories
