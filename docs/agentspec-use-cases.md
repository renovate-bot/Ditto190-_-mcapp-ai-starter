# AgentSpec Use Cases & Examples

## Overview

This document demonstrates concrete, real-world use cases for AgentSpec and shows how they solve actual problems in the current system.

---

## Use Case 1: Auto-Generated n8n Workflows

### Problem (Today)

When building AI-powered n8n workflows, you must:
1. Manually define agent nodes in n8n UI
2. Manually wire connections between agents
3. Manually add constraints as function nodes
4. Manually configure MCP server connections
5. Keep AGENTS.md synchronized with n8n workflow definition
6. If architecture changes, manually update both documents

**Result**: Duplication, inconsistency, high maintenance burden.

### Solution (With AgentSpec)

Define agent architecture once in AgentSpec, auto-generate n8n workflow:

**Input**: `cloud-orchestration.agentspec.json`

```json
{
  "version": "1.0.0",
  "name": "cloud-infrastructure-team",
  "domain": "azure",
  "agents": {
    "CloudArchitect": {
      "type": "specialist",
      "description": "Designs cloud infrastructure",
      "model": "claude-opus",
      "capabilities": [
        {
          "name": "terraform-module-design",
          "description": "Design reusable Terraform modules",
          "inputs": ["requirements", "constraints"],
          "outputs": ["module-spec"]
        },
        {
          "name": "bicep-compilation",
          "description": "Compile Bicep to ARM templates",
          "inputs": ["bicep-file"],
          "outputs": ["arm-template"]
        }
      ],
      "constraints": [
        "Must validate against Azure security policies",
        "Must support both Terraform AND Bicep"
      ],
      "tools": ["terraform-parser", "bicep-compiler"],
      "mcpServers": [
        {"name": "azure-validator", "type": "stdio", "uri": "docker://azure-mcp"}
      ]
    },
    "ComplianceValidator": {
      "type": "specialist",
      "description": "Validates against compliance policies",
      "model": "claude-haiku",
      "capabilities": [
        {
          "name": "policy-check",
          "description": "Verify resources comply with org policies",
          "inputs": ["infrastructure-spec"],
          "outputs": ["compliance-report"]
        }
      ],
      "constraints": ["Must be stateless and idempotent"],
      "tools": ["policy-engine"]
    }
  },
  "workflows": [
    {
      "name": "DeploymentPipeline",
      "steps": [
        {"agent": "CloudArchitect", "outputs": ["module-spec"]},
        {"agent": "ComplianceValidator", "inputs": ["module-spec"], "outputs": ["compliance-report"]}
      ]
    }
  ]
}
```

**Process**:

```bash
# Generate n8n workflow from AgentSpec
uv run autogenerateagentsmd --agentspec-file cloud-orchestration.agentspec.json --emit n8n-workflow

# Output: cloud-orchestration-workflow.json (ready to import into n8n)
```

**Output**: `cloud-orchestration-workflow.json`

```json
{
  "name": "cloud-infrastructure-team",
  "nodes": [
    {
      "id": "0",
      "name": "CloudArchitect",
      "type": "agentNode",
      "position": [0, 0],
      "parameters": {
        "model": "claude-opus",
        "capabilities": [
          {
            "name": "terraform-module-design",
            "description": "Design reusable Terraform modules",
            "inputs": ["requirements", "constraints"],
            "outputs": ["module-spec"]
          },
          {
            "name": "bicep-compilation",
            "description": "Compile Bicep to ARM templates",
            "inputs": ["bicep-file"],
            "outputs": ["arm-template"]
          }
        ],
        "constraints": ["Must validate against Azure security policies", "Must support both Terraform AND Bicep"],
        "tools": ["terraform-parser", "bicep-compiler"],
        "systemPrompt": "You are CloudArchitect. Designs cloud infrastructure.\n\nYour capabilities:\n- terraform-module-design: Design reusable Terraform modules\n- bicep-compilation: Compile Bicep to ARM templates\n\nConstraints:\n- Must validate against Azure security policies\n- Must support both Terraform AND Bicep",
        "mcpServers": [
          {"name": "azure-validator", "type": "stdio", "uri": "docker://azure-mcp"}
        ]
      }
    },
    {
      "id": "1",
      "name": "ComplianceValidator",
      "type": "agentNode",
      "position": [300, 0],
      "parameters": {
        "model": "claude-haiku",
        "capabilities": [
          {
            "name": "policy-check",
            "description": "Verify resources comply with org policies",
            "inputs": ["infrastructure-spec"],
            "outputs": ["compliance-report"]
          }
        ],
        "constraints": ["Must be stateless and idempotent"],
        "tools": ["policy-engine"]
      }
    }
  ],
  "connections": {
    "CloudArchitect": [
      [{"node": "ComplianceValidator", "type": "main", "index": 0}]
    ]
  },
  "settings": {}
}
```

**Benefit**: Import directly into n8n, fully functional workflow. Zero manual step configuration.

---

## Use Case 2: Enterprise Agent Standardization

### Problem (Today)

Large organizations have 50+ agents across different teams. Each agent:
- Has different naming conventions
- Specifies tools inconsistently
- Violates security constraints
- Uses incompatible models
- Has no formal versioning

**Result**: Chaos, inconsistent agent behavior, hard to reason about system.

### Solution (With AgentSpec)

Define org-wide agent standards in AgentSpec, enforce via linting:

**Step 1: Define Org Standard**

```yaml
# awesome-copilot/agent-specs/acme-corp-standard/1.0.0/agents.agentspec.json
{
  "version": "1.0.0",
  "name": "acme-corp-standard",
  "description": "ACME Corp standard agent definitions",
  "metadata": {
    "owner": "ai-platform-team",
    "approval_date": "2024-03-04",
    "sla": "99.9% uptime"
  },
  "patterns": {
    "DataProcessorPattern": {
      "description": "Standard for all data processing agents",
      "decorators": ["@idempotent", "@audit-logged", "@versioned"],
      "constraints": [
        "Must handle 1M+ records efficiently",
        "Must validate data before processing",
        "Must log all transformations",
        "Must never modify source data"
      ]
    },
    "CloudArchitectPattern": {
      "description": "Standard for all cloud infrastructure agents",
      "constraints": [
        "Must support Azure ARM, Terraform, AND Bicep",
        "Must validate against security policies",
        "Must check cost optimization rules",
        "Must ensure disaster recovery plan exists"
      ]
    }
  },
  "rules": {
    "all_agents_require_description": {
      "severity": "error",
      "message": "Every agent MUST have a description field"
    },
    "cloud_agents_must_support_multiple_iac": {
      "severity": "error",
      "domain": "azure",
      "rule": "agents_must_have_terraform_and_bicep_capabilities"
    },
    "data_processors_must_be_idempotent": {
      "severity": "error",
      "agent_type": "data-processor",
      "rule": "must_have_@idempotent_trait"
    }
  }
}
```

**Step 2: Create Team AgentSpec**

```yaml
# awesome-copilot/agent-specs/data-engineering-team/1.0.0/agents.agentspec.json
{
  "version": "1.0.0",
  "dependencies": {
    "@acme/corp-standard": "^1.0.0"
  },
  "agents": {
    "DataEngineer": {
      "type": "specialist",
      "extends": "DataProcessorPattern",
      "description": "Designs and maintains data pipelines",
      "model": "claude-opus",
      "traits": ["@idempotent", "@audit-logged"],
      "capabilities": [...]
    }
  }
}
```

**Step 3: Validate Team Compliance**

```bash
# Lint against org standards
uv run autogenerateagentsmd --agentspec-file data-engineering-team.agentspec.json \
  --lint \
  --inherit-rules @acme/corp-standard

# Output:
# ✗ DataEngineer: Missing 'versioned' trait (required by DataProcessorPattern)
# ✓ All other constraints satisfied
```

**Benefit**: Organizations enforce standards without manual review; violations caught automatically.

---

## Use Case 3: Multi-Cloud Agent Composition

### Problem (Today)

A company supports Azure AND AWS. Currently:
- Maintain separate AGENTS.md for Azure agents
- Maintain separate AGENTS.md for AWS agents
- Manual reconciliation of common patterns
- No way to express "this workflow needs both Azure AND AWS agents"
- Risk of inconsistency between cloud implementations

### Solution (With AgentSpec)

Compose cloud-specific AgentSpecs into unified library:

**Input 1**: `azure-patterns.agentspec.json`

```json
{
  "version": "1.0.0",
  "name": "azure-patterns",
  "domain": "azure",
  "agents": {
    "AzureArchitect": {
      "type": "specialist",
      "capabilities": [
        {"name": "bicep-design", "outputs": ["bicep-template"]},
        {"name": "arm-validation", "outputs": ["validation-report"]}
      ]
    }
  }
}
```

**Input 2**: `aws-patterns.agentspec.json`

```json
{
  "version": "1.0.0",
  "name": "aws-patterns",
  "domain": "aws",
  "agents": {
    "AWSArchitect": {
      "type": "specialist",
      "capabilities": [
        {"name": "cloudformation-design", "outputs": ["cf-template"]},
        {"name": "sam-validation", "outputs": ["validation-report"]}
      ]
    }
  }
}
```

**Input 3**: `multi-cloud-orchestration.agentspec.json`

```json
{
  "version": "1.0.0",
  "name": "multi-cloud-orchestration",
  "domain": "infrastructure",
  "dependencies": {
    "@awesome/azure-patterns": "^1.0.0",
    "@awesome/aws-patterns": "^1.0.0"
  },
  "agents": {
    "MultiCloudOrchestrator": {
      "type": "orchestrator",
      "description": "Orchestrates multi-cloud deployments",
      "model": "claude-opus",
      "capabilities": [
        {
          "name": "cloud-selection",
          "description": "Select optimal cloud for workload",
          "outputs": ["target-cloud"]
        }
      ]
    }
  },
  "workflows": [
    {
      "name": "MultiCloudDeployment",
      "steps": [
        {
          "agent": "MultiCloudOrchestrator",
          "outputs": ["target-cloud"]
        },
        {
          "agent": "AzureArchitect",
          "condition": "target-cloud == 'azure'",
          "outputs": ["bicep-template"]
        },
        {
          "agent": "AWSArchitect",
          "condition": "target-cloud == 'aws'",
          "outputs": ["cf-template"]
        }
      ],
      "contracts": [
        "If target-cloud=azure, AzureArchitect must output bicep-template",
        "If target-cloud=aws, AWSArchitect must output cf-template"
      ]
    }
  ]
}
```

**Process**:

```bash
# Compose all cloud patterns + orchestration
uv run autogenerateagentsmd --agentspec-file multi-cloud-orchestration.agentspec.json \
  --resolve-dependencies

# Generate unified documentation
uv run autogenerateagentsmd --agentspec-file multi-cloud-orchestration.agentspec.json \
  --emit agents-md > MULTI_CLOUD_AGENTS.md

# Generate n8n workflow
uv run autogenerateagentsmd --agentspec-file multi-cloud-orchestration.agentspec.json \
  --emit n8n-workflow > multi-cloud-workflow.json
```

**Benefit**: Single source of truth for multi-cloud architecture; automatic consistency checking.

---

## Use Case 4: Agent Anti-Pattern Detection

### Problem (Today)

Developer creates new agent in Awesome Copilot but violates performance constraints:
- Agent is NOT idempotent (can't handle retries)
- Agent doesn't validate inputs (crashes on bad data)
- Agent doesn't handle rate limits

Discovered only in production.

### Solution (With AgentSpec)

Linting catches patterns BEFORE deployment:

**Define Anti-Pattern Rules**:

```javascript
// awesome-copilot/linter-rules/data-processing.rule.js

const lintRules = {
  "data-processor-must-be-idempotent": {
    severity: "error",
    applies_to: { agent_type: "data-processor" },
    check: (agent) => {
      return agent.traits?.includes("@idempotent")
        ? { ok: true }
        : {
            ok: false,
            message: `Data processor '${agent.id}' MUST have @idempotent trait`,
            fix: `Add "traits": ["@idempotent"] to agent definition`
          };
    }
  },

  "data-processor-must-validate-inputs": {
    severity: "error",
    applies_to: { agent_type: "data-processor" },
    check: (agent) => {
      const hasValidation = agent.capabilities?.some(c =>
        c.name.includes("validate") || c.name.includes("check")
      );
      return hasValidation
        ? { ok: true }
        : {
            ok: false,
            message: `Data processor '${agent.id}' must have an input validation capability`,
            fix: `Add a capability like "name": "validate-inputs" that validates data before processing`
          };
    }
  },

  "data-processor-must-handle-rate-limits": {
    severity: "warning",
    applies_to: { agent_type: "data-processor" },
    applies_when: { tools: { includes: ["api-client", "http-request"] } },
    check: (agent) => {
      const hasRateLimitHandling = agent.constraints?.some(c =>
        c.toLowerCase().includes("rate") ||
        c.toLowerCase().includes("throttle") ||
        c.toLowerCase().includes("backoff")
      );
      return hasRateLimitHandling
        ? { ok: true }
        : {
            ok: false,
            message: `'${agent.id}' uses external APIs but doesn't specify rate limiting strategy`,
            fix: `Add constraint like "Must implement exponential backoff for rate limit handling"`
          };
    }
  }
};
```

**Usage**:

```bash
# Validate agent spec against data processing rules
uv run autogenerateagentsmd --agentspec-file agents.agentspec.json \
  --lint \
  --rules data-processing

# Output:
# ✗ CSVProcessor: Data processor must have @idempotent trait
#   Fix: Add "traits": ["@idempotent"] to agent definition
#
# ✗ CSVProcessor: Data processor must have input validation capability
#   Fix: Add a capability like validate-inputs
#
# ✓ APIDataExtractor: All checks passed
```

**Benefit**: Catch anti-patterns during development, before they cause production issues.

---

## Use Case 5: Agent Library Marketplace Discovery

### Problem (Today)

Developers browse GitHub Awesome Copilot repo to find agents. Process:
1. Search through markdown files
2. Copy-paste agent definition
3. Modify for their specific needs
4. No versioning, no composition

### Solution (With AgentSpec)

Publish versioned agent libraries, auto-discovered via OpenAPI:

**Step 1: Publish Library**

```bash
# GitHub Awesome Copilot as an "agent library marketplace"
awesome-copilot/agent-specs/github-automation/2.3.1/agents.agentspec.json

# Automatic discovery through OpenAPI
awesome-copilot/emitted/openapi-specs/github-automation-2.3.1.json
```

**Step 2: Query Available Agents**

```bash
# List all agents and their capabilities
curl -X GET http://localhost:3000/api/agents

# Response:
# [
#   {
#     "id": "CodeReviewAgent",
#     "type": "specialist",
#     "domain": "github",
#     "capabilities": [
#       {"name": "analyze-pr-quality", "inputs": ["pr-diff"], "outputs": ["quality-report"]},
#       {"name": "suggest-improvements", "inputs": ["code-analysis"], "outputs": ["suggestions"]}
#     ],
#     "version": "2.3.1",
#     "library": "@awesome/github-automation"
#   }
# ]
```

**Step 3: Auto-Generate Integration**

```bash
# Copilot: "Find agents that analyze PRs and generate reports"
copilot suggest-agents --capability "pr-analysis" --model claude-opus

# Output:
# Found 3 agents matching criteria:
# 1. CodeReviewAgent@2.3.1 - "Analyzes code quality, suggests improvements"
# 2. SecurityAuditAgent@1.5.0 - "Analyzes security vulnerabilities"
# 3. PerformanceAnalyzerAgent@3.0.0 - "Analyzes performance issues"

# Auto-generate composition:
copilot compose --agents CodeReviewAgent,SecurityAuditAgent,PerformanceAnalyzerAgent --output pr-analysis-suite.agentspec.json

# Output: pr-analysis-suite.agentspec.json
# (Fully composed AgentSpec ready to deploy)
```

**Benefit**: Library discovery becomes programmatic; agents become LEGO bricks for composition.

---

## Use Case 6: CI/CD Agent Synchronization

### Problem (Today)

When AGENTS.md changes, n8n workflows aren't automatically updated. Manual steps:
1. Edit AGENTS.md in repo
2. Manually update n8n workflow definition
3. Test workflow
4. Remember to update Prompt Registry

Easy to forget steps, causing inconsistency.

### Solution (With AgentSpec)

CI/CD pipeline auto-updates all artifacts:

**GitHub Actions Pipeline** (`.github/workflows/update-agents.yml`)

```yaml
name: Sync AgentSpec to all formats

on:
  push:
    paths:
      - "agent-specs/**/*.agentspec.json"
  pull_request:
    paths:
      - "agent-specs/**/*.agentspec.json"

jobs:
  validate-and-emit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate AgentSpecs
        run: |
          uv run autogenerateagentsmd --agentspec-dir ./agent-specs \
            --lint \
            --fail-on-errors

      - name: Generate AGENTS.md
        run: |
          uv run autogenerateagentsmd --agentspec-dir ./agent-specs \
            --emit agents-md \
            --output-dir ./emitted/agents-md

      - name: Generate n8n workflows
        run: |
          uv run autogenerateagentsmd --agentspec-dir ./agent-specs \
            --emit n8n-workflow \
            --output-dir ./emitted/n8n-workflows

      - name: Generate VS Code configs
        run: |
          uv run autogenerateagentsmd --agentspec-dir ./agent-specs \
            --emit vscode-config \
            --output-dir ./emitted/vscode-configs

      - name: Generate OpenAPI specs
        run: |
          uv run autogenerateagentsmd --agentspec-dir ./agent-specs \
            --emit openapi \
            --output-dir ./emitted/openapi-specs

      - name: Push generated artifacts
        run: |
          git config user.name "Agent Bot"
          git config user.email "agent-bot@acme.com"
          git add emitted/
          git commit -m "chore: auto-generated agent artifacts from AgentSpec"
          git push

      - name: Update n8n workflows
        run: |
          # Use n8n API to import updated workflows
          for workflow_file in emitted/n8n-workflows/*.json; do
            curl -X POST https://n8n.example.com/api/v1/workflows \
              -H "Authorization: Bearer ${{ secrets.N8N_API_KEY }}" \
              -d @$workflow_file
          done

      - name: Notify Prompt Registry
        run: |
          # Trigger Prompt Registry rebuild
          curl -X POST https://prompt-registry.example.com/api/rebuild \
            -H "Authorization: Bearer ${{ secrets.PROMPT_REGISTRY_API_KEY }}"

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const agents = JSON.parse(fs.readFileSync('./emitted/agents-md/summary.json'));
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Generated Artifacts\n\n- ${agents.count} agents defined\n- AGENTS.md generated\n- n8n workflows ready to import\n- All validations passed ✓`
            });
```

**Benefit**: Automatic synchronization; no manual steps; consistency guaranteed by automation.

---

## Summary Table

| Use Case | Problem | Solution | Benefit |
|----------|---------|----------|---------|
| **n8n Automation** | Manual workflow setup | Auto-emit from AgentSpec | Instant, correct workflows |
| **Enterprise Standards** | Inconsistent agents | Org-wide AgentSpec + linting | Enforced standards |
| **Multi-Cloud** | Separate specs per cloud | Unified composition | Single source of truth |
| **Anti-Pattern Prevention** | Bugs caught in production | Linting rules | Catch early |
| **Agent Marketplace** | Manual search & copy | Programmatic discovery | Composable libraries |
| **CI/CD Automation** | Manual synchronization | Automated gen & deploy | Consistency guaranteed |

All these use cases are enabled by treating agent definitions as **formal, composable, versioned specifications** rather than documentation.

