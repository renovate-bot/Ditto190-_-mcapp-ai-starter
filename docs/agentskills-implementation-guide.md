# AgentSkills Integration Complete Implementation Guide

## Overview

This guide provides complete implementation instructions for integrating AgentSkills (universal agent capability format by Anthropic) into the self-hosted-ai-starter-kit project with n8n workflow automation and Context7 memory integration.

## Table of Contents

1. [Quick Start](#quick-start)
2. [AgentSkills Templates](#agentskills-templates)
3. [n8n Validation Workflow](#n8n-validation-workflow)
4. [Context7 Memory Integration](#context7-memory-integration)
5. [MCP Server Integration](#mcp-server-integration)
6. [CI/CD Automation](#cicd-automation)
7. [Testing & Validation](#testing--validation)

## Quick Start

### Prerequisites

```bash
# Install skills-ref library
cd /workspaces/self-hosted-ai-starter-kit/agentskills/skills-ref
uv sync
source .venv/bin/activate

# Verify installation
skills-ref --help

# Install Context7 CLI (optional)
# Follow instructions at https://context7.io/docs/cli
```

### Validate Existing Skills

```bash
# Validate all skills
cd /workspaces/self-hosted-ai-starter-kit/awesome-copilot/skills
for skill in */; do
    echo "Validating: $skill"
    skills-ref validate "$skill"
done

# Generate validation report
for skill in */; do
    skills-ref validate "$skill" 2>&1 | tee "validation-report-$(basename "$skill").txt"
done

# Count valid/invalid skills
grep -r "is valid" validation-report-*.txt | wc -l  # Count valid
grep -r "Error" validation-report-*.txt | wc -l     # Count errors
```

## AgentSkills Templates

### Template 1: Minimal Skill

Created at: `awesome-copilot/skills/example-minimal-skill/`

**Structure:**
```
example-minimal-skill/
└── SKILL.md  (frontmatter + instructions only)
```

**Use when:** Simple, instruction-only skills without scripts or resources.

**Frontmatter:**
```yaml
---
name: example-minimal-skill
description: A minimal AgentSkill example showing only required fields...
license: Apache-2.0
---
```

### Template 2: Full Skill

Created at: `awesome-copilot/skills/example-full-skill/`

**Structure:**
```
example-full-skill/
├── SKILL.md                          # Main instructions
├── scripts/
│   ├── validate.py                   # Python validation (PEP 723 inline deps)
│   ├── process.sh                    # Bash processing
│   └── extract.ts                    # Deno extraction (npm: imports)
└── references/
    ├── schema.json                   # JSON schema
    ├── examples.md                   # Usage examples
    └── troubleshooting.md            # Common errors & solutions
```

**Use when:** Complex skills requiring scripts, validation, multiple resources.

**Frontmatter:**
```yaml
---
name: example-full-skill
description: A comprehensive AgentSkill example demonstrating all available fields...
license: Apache-2.0
compatibility: Works best with models that support tool calling...
allowed-tools: ['read_file', 'write_file', 'run_command']
metadata:
  version: '1.0.0'
  author: 'n8n Community'
  category: 'example'
  tags: ['template', 'reference', 'comprehensive']
  requires_python: '>=3.11'
  requires_node: '>=18.0.0'
---
```

### Key Script Design Principles

All scripts follow AgentSkills best practices:

1. **Non-Interactive**: All input via CLI flags (no TTY prompts)
2. **Self-Contained**: Inline dependencies (PEP 723, npm:, jsr:)
3. **Clear Interface**: `--help` with usage examples
4. **Structured Output**: JSON/CSV to stdout, diagnostics to stderr
5. **Error Handling**: Meaningful exit codes and messages
6. **Idempotent**: Safe to retry (agents may retry on failure)
7. **Bounded Output**: Default to summaries, support pagination

## n8n Validation Workflow

### Workflow Overview

**Purpose:** Automated AgentSkills validation integrated with n8n, Context7 memory, and error handling.

**Workflow Name:** AgentSkills Validation Workflow  
**Trigger:** Webhook POST to `/agentskills-validate`  
**Error Workflow:** AgentSkills Error Handler

### Workflow Nodes

#### 1. Webhook Trigger
- **Type:** Webhook  
- **Method:** POST  
- **Path:** `/agentskills-validate`  
- **Payload:**
  ```json
  {
    "skillPath": "/path/to/skill/directory",
    "validateAll": false
  }
  ```

#### 2. Parse Request (Code Node)
Extracts and validates request parameters:
- `skillPath`: Path to single skill directory
- `validateAll`: Boolean to validate all skills in awesome-copilot/skills/

#### 3. Validate All? (IF Node)
Routes to either "Validate All Skills" or "Validate Single Skill" based on `validateAll` flag.

#### 4. Validate All Skills (Execute Command)
```bash
cd /workspaces/self-hosted-ai-starter-kit/agentskills/skills-ref
source .venv/bin/activate
cd /workspaces/self-hosted-ai-starter-kit/awesome-copilot/skills
for skill in */; do
    echo "Validating: $skill"
    skills-ref validate "$skill" 2>&1
done
```

#### 5. Validate Single Skill (Execute Command)
```bash
cd /workspaces/self-hosted-ai-starter-kit/agentskills/skills-ref
source .venv/bin/activate
skills-ref validate {{ $json.skillPath }}
```

#### 6. Parse Validation Output (Code Node)
Parses validation output and structures report:
```javascript
{
  requestId: "val-1234567890",
  timestamp: "2026-03-05T10:30:00Z",
  skillPath: "/path/to/skill",
  status: "valid" | "invalid",
  valid: true | false,
  exitCode: 0,
  errors: [],
  agentskillsCompliant: true,
  recommendations: []
}
```

#### 7. Validation Passed? (IF Node)
Routes to success or failure response based on validation result.

#### 8. Respond Success/Failure (Respond to Webhook)
Returns structured JSON response with appropriate HTTP status:
- **200 OK:** Validation passed
- **422 Unprocessable Entity:** Validation failed

#### 9. Log to Context7 (HTTP Request)
Logs validation results to Context7 memory system for tracking and analysis.

### Setup Instructions

#### Create Workflow in n8n UI

1. **Access n8n:** Navigate to `http://localhost:5678` (or your Codespace URL)

2. **Create New Workflow:**
   - Click "New Workflow"
   - Name it "AgentSkills Validation Workflow"

3. **Add Nodes:**
   - Add Webhook Trigger (configure path: `/agentskills-validate`)
   - Add Code nodes for request parsing and output parsing
   - Add IF nodes for conditional routing
   - Add Execute Command nodes for validation
   - Add Respond to Webhook nodes for responses
   - Add HTTP Request node for Context7 logging

4. **Configure Error Workflow:**
   - Create separate workflow: "AgentSkills Error Handler"
   - Add Error Trigger node
   - Add notification nodes (Slack, Email)
   - Link to main workflow in Workflow Settings → Error Workflow

5. **Test Workflow:**
   ```bash
   # Test validation of single skill
   curl -X POST http://localhost:5678/webhook/agentskills-validate \\
     -H "Content-Type: application/json" \\
     -d '{
       "skillPath": "/workspaces/self-hosted-ai-starter-kit/awesome-copilot/skills/example-minimal-skill"
     }'
   
   # Test validation of all skills
   curl -X POST http://localhost:5678/webhook/agentskills-validate \\
     -H "Content-Type: application/json" \\
     -d '{"validateAll": true}'
   ```

### Error Handling Workflow

**Name:** AgentSkills Error Handler  
**Trigger:** Error Trigger (linked to main workflow)

**Nodes:**
1. **Error Trigger** - Receives error data from main workflow
2. **Parse Error** - Extracts error details, recommendations
3. **Log to Context7** - Stores error in memory system
4. **Notify Slack** - Sends alert to #agentskills-alerts channel
5. **Send Email** - Emails admin with error details
6. **Create Incident** - Logs incident for tracking

## Context7 Memory Integration

### Purpose
Store and retrieve AgentSkills validation history, errors, and recommendations using Context7 semantic memory system.

### Integration Points

#### 1. Validation Logs
```bash
# Store validation result in Context7
curl -X POST https://api.context7.io/docs \\
  -H "Authorization: Bearer $CONTEXT7_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "doc_type": "agentskills_validation",
    "title": "example-full-skill - valid",
    "content": {
      "timestamp": "2026-03-05T10:30:00Z",
      "skillPath": "/path/to/skill",
      "status": "valid",
      "errors": []
    },
    "tags": ["validation", "agentskills", "success"]
  }'
```

#### 2. Error Tracking
```bash
# Store error in Context7
curl -X POST https://api.context7.io/docs \\
  -H "Authorization: Bearer $CONTEXT7_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "doc_type": "agentskills_error",
    "title": "Workflow execution error",
    "content": {
      "workflowName": "AgentSkills Validation",
      "errorMessage": "skills-ref: command not found",
      "recommendations": ["Install skills-ref library"]
    },
    "tags": ["error", "agentskills", "high-severity"]
  }'
```

#### 3. Query Validation History
```bash
# Retrieve validation history
curl -X GET "https://api.context7.io/docs?doc_type=agentskills_validation&limit=50" \\
  -H "Authorization: Bearer $CONTEXT7_API_KEY"

# Query specific skill
curl -X GET "https://api.context7.io/search?q=example-full-skill&doc_type=agentskills_validation" \\
  -H "Authorization: Bearer $CONTEXT7_API_KEY"
```

### Context7 MCP Integration

Use Context7 MCP tools within workflows:

```javascript
// In n8n Code node
const context7 = {
  action: 'create_doc',
  doc_type: 'agentskills_validation',
  title: `${skillName} - ${status}`,
  content: JSON.stringify(validationResult),
  tags: ['validation', 'agentskills', status]
};
return { json: context7 };
```

## MCP Server Integration

### Add AgentSkills Tools to GenerateAgents MCP Server

**File:** `generateagents-mcp/server.py`

**Add Three New Tools:**

#### 1. `validate_agentskills`
```python
@mcp.tool()
async def validate_agentskills(
    repo_path: str,
    skills_subdir: str = "awesome-copilot/skills"
) -> dict:
    """
    Validate all AgentSkills in a repository.
    
    Args:
        repo_path: Path to repository root
        skills_subdir: Subdirectory containing skills (default: awesome-copilot/skills)
    
    Returns:
        Validation report with status and errors
    """
    # Implementation calls skills-ref validate
    pass
```

#### 2. `generate_agentskills_prompt`
```python
@mcp.tool()
async def generate_agentskills_prompt(
    repo_path: str,
    skills_subdir: str = "awesome-copilot/skills",
    format: str = "xml"
) -> dict:
    """
    Generate agent prompt with available skills metadata.
    
    Args:
        repo_path: Path to repository root
        skills_subdir: Subdirectory containing skills
        format: Output format (xml, json, markdown)
    
    Returns:
        Formatted prompt with skill metadata
    """
    # Implementation calls skills-ref to-prompt
    pass
```

#### 3. `read_skill_properties`
```python
@mcp.tool()
async def read_skill_properties(
    skill_path: str
) -> dict:
    """
    Read AgentSkill metadata from SKILL.md frontmatter.
    
    Args:
        skill_path: Path to skill directory
    
    Returns:
        Skill properties (name, description, license, compatibility, metadata)
    """
    # Implementation calls skills-ref read-properties
    pass
```

### MCP Tool Usage Examples

```python
# From VS Code Copilot or Claude Desktop

# Validate all skills in a repository
result = await validate_agentskills(
    repo_path="/workspaces/self-hosted-ai-starter-kit",
    skills_subdir="awesome-copilot/skills"
)

# Generate XML prompt for Claude
prompt = await generate_agentskills_prompt(
    repo_path="/workspaces/self-hosted-ai-starter-kit",
    format="xml"
)

# Read individual skill metadata
props = await read_skill_properties(
    skill_path="/workspaces/self-hosted-ai-starter-kit/awesome-copilot/skills/example-full-skill"
)
```

## CI/CD Automation

### GitHub Actions Workflow

**File:** `.github/workflows/validate-agentskills.yml`

```yaml
name: Validate AgentSkills

on:
  pull_request:
    paths:
      - 'awesome-copilot/skills/**'
  push:
    branches: [main]
    paths:
      - 'awesome-copilot/skills/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH
      
      - name: Install skills-ref
        run: |
          cd agentskills/skills-ref
          uv sync
      
      - name: Validate all skills
        run: |
          source agentskills/skills-ref/.venv/bin/activate
          cd awesome-copilot/skills
          
          FAILED=0
          for skill in */; do
            echo "Validating: $skill"
            if ! skills-ref validate "$skill"; then
              echo "❌ Failed: $skill"
              FAILED=$((FAILED + 1))
            else
              echo "✅ Passed: $skill"
            fi
          done
          
          if [ $FAILED -gt 0 ]; then
            echo "❌ $FAILED skill(s) failed validation"
            exit 1
          fi
          
          echo "✅ All skills passed validation"
      
      - name: Generate validation report
        if: always()
        run: |
          source agentskills/skills-ref/.venv/bin/activate
          cd awesome-copilot/skills
          
          echo "# AgentSkills Validation Report" > validation-report.md
          echo "" >> validation-report.md
          echo "Generated: $(date)" >> validation-report.md
          echo "" >> validation-report.md
          
          for skill in */; do
            echo "## $(basename "$skill")" >> validation-report.md
            skills-ref validate "$skill" &>> validation-report.md || true
            echo "" >> validation-report.md
          done
      
      - name: Upload validation report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: validation-report
          path: awesome-copilot/skills/validation-report.md
      
      - name: Comment on PR
        if: github.event_name == 'pull_request' && failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('awesome-copilot/skills/validation-report.md', 'utf8');
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## ❌ AgentSkills Validation Failed\\n\\n${report}`
            });
```

### Pre-commit Hook

**File:** `.git/hooks/pre-commit`

```bash
#!/bin/bash

# Validate AgentSkills before commit
echo "Validating AgentSkills..."

cd agentskills/skills-ref
if [ ! -d ".venv" ]; then
    echo "Installing skills-ref..."
    uv sync
fi

source .venv/bin/activate
cd ../../awesome-copilot/skills

FAILED=0
for skill in $(git diff --cached --name-only --diff-filter=ACM | grep 'skills/' | cut -d'/' -f1-2 | sort -u); do
    if [ -d "$skill" ]; then
        echo "Validating: $skill"
        if ! skills-ref validate "$skill"; then
            echo "❌ Failed: $skill"
            FAILED=$((FAILED + 1))
        fi
    fi
done

if [ $FAILED -gt 0 ]; then
    echo "❌ $FAILED skill(s) failed validation"
    echo "Fix errors before committing or use --no-verify to skip"
    exit 1
fi

echo "✅ All skills passed validation"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Testing & Validation

### Manual Testing

```bash
# Test minimal skill
skills-ref validate awesome-copilot/skills/example-minimal-skill

# Test full skill
skills-ref validate awesome-copilot/skills/example-full-skill

# Test script execution
cd awesome-copilot/skills/example-full-skill

# Create test input
cat > test-input.json << 'EOF'
{
  "items": [
    {
      "id": "test-1",
      "name": "Test User",
      "email": "test@example.com",
      "status": "active"
    }
  ]
}
EOF

# Run validation script
uv run scripts/validate.py --input test-input.json --schema references/schema.json --verbose

# Run processing script
bash scripts/process.sh test-input.json test-output.json --verbose

# Run extraction script
deno run --allow-read scripts/extract.ts --file test-output.json --fields id,email --pretty
```

### Automated Testing

```bash
# Run all tests
cd awesome-copilot/skills
./test-all-skills.sh

# Test specific skill
./test-skill.sh example-full-skill

# Generate test report
./generate-test-report.sh > test-results.md
```

### Integration Testing with n8n

```bash
# Test validation workflow
curl -X POST http://localhost:5678/webhook/agentskills-validate \\
  -H "Content-Type: application/json" \\
  -d '{
    "skillPath": "/workspaces/self-hosted-ai-starter-kit/awesome-copilot/skills/example-full-skill"
  }'

# Expected response (200 OK):
{
  "requestId": "val-1234567890",
  "timestamp": "2026-03-05T10:30:00Z",
  "skillPath": "/workspaces/self-hosted-ai-starter-kit/awesome-copilot/skills/example-full-skill",
  "status": "valid",
  "valid": true,
  "exitCode": 0,
  "errors": [],
  "agentskillsCompliant": true,
  "recommendations": []
}
```

## Success Criteria

- ✅ All 205+ skills pass AgentSkills validation
- ✅ CI/CD validates skills on every PR
- ✅ n8n workflow automates validation and logging
- ✅ Context7 stores validation history and errors
- ✅ MCP server exposes 3 new AgentSkills tools
- ✅ Example templates available for contributors
- ✅ Zero breaking changes to existing workflows

## Resources

- **AgentSkills Specification:** https://agentskills.io/specification
- **skills-ref Library:** https://github.com/agentskills/agentskills/tree/main/skills-ref
- **Example Skills:** `awesome-copilot/skills/example-minimal-skill`, `example-full-skill`
- **Integration Strategy:** `docs/agentskills-integration-strategy.md`
- **Context7 MCP Docs:** https://context7.io/docs/mcp
- **n8n Error Handling:** https://docs.n8n.io/flow-logic/error-handling/

## Next Steps

1. **Phase 1 (Week 1):** Validate all existing skills, fix compliance issues
2. **Phase 2 (Week 2):** Implement MCP server tools, add CLI flags to agentspec_mvp
3. **Phase 3 (Week 3):** Deploy n8n validation workflow, configure error handling
4. **Phase 4 (Week 4):** Update documentation, create contributor guide

---

**Implementation Status:** ✅ Templates Created | ⏳ n8n Workflow Design Complete | ⏳ CI/CD Pending | ⏳ MCP Tools Pending
