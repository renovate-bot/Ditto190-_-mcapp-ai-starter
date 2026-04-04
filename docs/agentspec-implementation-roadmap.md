# AgentSpec Implementation Roadmap

## Overview

This document provides a concrete, phased implementation plan for bringing TypeSpec-inspired patterns to the composable agent library system. The goal is to transform agent definition from documentation-focused to specification-driven, enabling multi-format compilation, composition, and enterprise-scale reusability.

---

## Phase 1: Foundation (Weeks 1-2)

### 1.1 Define AgentSpec JSON Schema

**Deliverable**: `agentspec/schema/agentspec-1.0.0.json`

Create a formal JSON schema that codifies agent structure. This becomes the contract for validation and tooling.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "AgentSpec",
  "description": "Formal specification for composable AI agents",
  "required": ["version", "agents"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version (e.g., 1.0.0)"
    },
    "name": {
      "type": "string",
      "description": "Library name (e.g., 'github-patterns')"
    },
    "description": {
      "type": "string",
      "description": "Library purpose and domain"
    },
    "domain": {
      "type": "string",
      "enum": ["generic", "github", "azure", "aws", "gcp", "infrastructure", "security", "data"],
      "description": "Agent domain for linting context"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "author": { "type": "string" },
        "license": { "type": "string" },
        "repository": { "type": "string" },
        "tags": { "type": "array", "items": { "type": "string" } }
      }
    },
    "dependencies": {
      "type": "object",
      "additionalProperties": { "type": "string" },
      "description": "AgentSpec library dependencies with semver (e.g., {'@awesome/github-patterns': '^2.0.0'})"
    },
    "agents": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["type", "capabilities"],
        "properties": {
          "id": { "type": "string", "description": "Unique agent identifier" },
          "type": {
            "type": "string",
            "enum": ["specialist", "generalist", "data-processor", "orchestrator"],
            "description": "Agent archetype"
          },
          "description": { "type": "string" },
          "roles": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Roles this agent assumes (e.g., ['architect', 'reviewer', 'implementer'])"
          },
          "model": {
            "type": "string",
            "description": "LLM model (e.g., 'claude-opus', 'gpt-4', 'gemini-2.5-pro')"
          },
          "capabilities": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name"],
              "properties": {
                "name": { "type": "string", "description": "Capability name" },
                "description": { "type": "string" },
                "inputs": { "type": "array", "items": { "type": "string" } },
                "outputs": { "type": "array", "items": { "type": "string" } }
              }
            }
          },
          "constraints": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Hard constraints this agent must satisfy"
          },
          "tools": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Available tools/MCP servers this agent can access"
          },
          "mcpServers": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "name": { "type": "string" },
                "type": { "enum": ["stdio", "http"] },
                "uri": { "type": "string" }
              }
            }
          },
          "systemPrompt": {
            "type": "string",
            "description": "Custom system prompt template (can reference {{capability}} variables)"
          },
          "extends": {
            "type": ["string", "array"],
            "description": "Base agents or patterns this agent extends"
          },
          "traits": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Applied traits (e.g., ['@idempotent', '@audit-logged'])"
          }
        }
      }
    },
    "patterns": {
      "type": "object",
      "description": "Reusable trait definitions",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "description": { "type": "string" },
          "decorators": { "type": "array", "items": { "type": "string" } },
          "capabilities": { "type": "array", "items": { "type": "string" } },
          "constraints": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "workflows": {
      "type": "array",
      "description": "Defined agent composition workflows",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "description": { "type": "string" },
          "steps": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "agent": { "type": "string", "description": "Agent ID" },
                "outputs": { "type": "array", "items": { "type": "string" } }
              }
            }
          },
          "contracts": {
            "type": "array",
            "items": {
              "type": "string",
              "description": "Data contract between agent steps"
            }
          }
        }
      }
    }
  }
}
```

**Rationale**: JSON schema is toolable (VS Code validation, linting, docs generation), composable (can import $ref from other schemas), and language-agnostic.

### 1.2 Create AgentSpec TypeScript Interfaces

**Deliverable**: `agentspec/src/types.ts`

```typescript
export interface AgentSpec {
  version: string;
  name?: string;
  description?: string;
  domain?: "generic" | "github" | "azure" | "aws" | "gcp" | "infrastructure" | "security" | "data";
  metadata?: {
    author?: string;
    license?: string;
    repository?: string;
    tags?: string[];
  };
  dependencies?: Record<string, string>;
  agents: Record<string, AgentDefinition>;
  patterns?: Record<string, PatternDefinition>;
  workflows?: WorkflowDefinition[];
}

export interface AgentDefinition {
  id?: string;
  type: "specialist" | "generalist" | "data-processor" | "orchestrator";
  description: string;
  roles?: string[];
  model: string;
  capabilities: Capability[];
  constraints?: string[];
  tools?: string[];
  mcpServers?: MCPServer[];
  systemPrompt?: string;
  extends?: string | string[];
  traits?: string[];
}

export interface Capability {
  name: string;
  description?: string;
  inputs?: string[];
  outputs?: string[];
}

export interface PatternDefinition {
  description?: string;
  decorators?: string[];
  capabilities?: string[];
  constraints?: string[];
}

export interface MCPServer {
  name: string;
  type: "stdio" | "http";
  uri: string;
}

export interface WorkflowDefinition {
  name: string;
  description?: string;
  steps: WorkflowStep[];
  contracts?: string[];
}

export interface WorkflowStep {
  agent: string;
  outputs?: string[];
}
```

### 1.3 Sample AgentSpecs (Examples)

**Deliverable**: `agentspec/examples/`

Create 2-3 example AgentSpecs demonstrating different use cases:

1. **`github-automation.agentspec.json`** - GitHub PR/issue agents
2. **`azure-infrastructure.agentspec.json`** - Azure Terraform/Bicep agents
3. **`data-pipeline.agentspec.json`** - ETL and data processing agents

Each example includes:
- Multiple agents with different archetypes
- Capability definitions with inputs/outputs
- Constraints and tools
- Workflow definitions showing composition
- Data contracts

---

## Phase 2: Tooling & Validation (Weeks 2-3)

### 2.1 AgentSpec Compiler

**Deliverable**: `agentspec/src/compiler.ts`

```typescript
import * as fs from "fs";
import Ajv from "ajv";

export class AgentSpecCompiler {
  private ajv: Ajv;
  private schema: any;

  constructor(schemaPath: string) {
    this.ajv = new Ajv();
    this.schema = JSON.parse(fs.readFileSync(schemaPath, "utf-8"));
    this.ajv.addSchema(this.schema);
  }

  parse(filePath: string): AgentSpec {
    const content = fs.readFileSync(filePath, "utf-8");
    const spec = JSON.parse(content);
    
    if (!this.validate(spec)) {
      throw new Error(
        `AgentSpec validation failed:\n${JSON.stringify(this.ajv.errorsText())}`
      );
    }
    
    return spec;
  }

  validate(spec: AgentSpec): boolean {
    const valid = this.ajv.validateSchema(spec);
    if (!valid) {
      console.error("Schema errors:", this.ajv.errorsText());
    }
    return valid;
  }

  // Resolve dependencies (like npm package resolution)
  async resolveDependencies(
    spec: AgentSpec,
    registry: AgentSpecRegistry
  ): Promise<Map<string, AgentSpec>> {
    const resolved = new Map<string, AgentSpec>();
    const queue = [spec];
    
    while (queue.length > 0) {
      const current = queue.shift()!;
      
      if (current.dependencies) {
        for (const [libName, version] of Object.entries(current.dependencies)) {
          const dep = await registry.resolve(libName, version);
          if (!resolved.has(libName)) {
            resolved.set(libName, dep);
            queue.push(dep);
          }
        }
      }
    }
    
    return resolved;
  }

  // Merge multiple AgentSpecs into unified one
  merge(...specs: AgentSpec[]): AgentSpec {
    const merged: AgentSpec = {
      version: "1.0.0",
      agents: {},
      patterns: {},
      workflows: []
    };

    for (const spec of specs) {
      // Merge agents (detect conflicts)
      for (const [id, agent] of Object.entries(spec.agents)) {
        if (merged.agents[id]) {
          throw new Error(
            `Agent conflict: ${id} defined in multiple specs`
          );
        }
        merged.agents[id] = agent;
      }

      // Merge patterns (allow overwrites if intentional)
      merged.patterns = { ...merged.patterns, ...spec.patterns };

      // Merge workflows (concatenate)
      if (spec.workflows) {
        merged.workflows!.push(...spec.workflows);
      }
    }

    return merged;
  }
}
```

### 2.2 Linting Framework

**Deliverable**: `agentspec/src/linter.ts`

```typescript
export type LintRule = (
  spec: AgentSpec,
  agent: AgentDefinition,
  domain: string
) => LintError[];

export interface LintError {
  agent: string;
  rule: string;
  severity: "error" | "warning" | "info";
  message: string;
}

export const lintRules: Record<string, LintRule> = {
  // Global rules
  "required-fields": (spec) => {
    const errors: LintError[] = [];
    if (!spec.version) errors.push({
      agent: "global",
      rule: "required-fields",
      severity: "error",
      message: "Missing required field: version"
    });
    return errors;
  },

  // Agent rules
  "agent-has-model": (spec, agent) => {
    return agent.model
      ? []
      : [{
          agent: agent.id || "unknown",
          rule: "agent-has-model",
          severity: "error",
          message: "Agent must specify a model"
        }];
  },

  "agent-has-description": (spec, agent) => {
    return agent.description
      ? []
      : [{
          agent: agent.id || "unknown",
          rule: "agent-has-description",
          severity: "warning",
          message: "Agent should have a description"
        }];
  },

  // Domain-specific rules
  "azure-agents-support-both-iac": (spec, agent, domain) => {
    if (domain !== "azure") return [];
    
    const hasTerraform = agent.capabilities.some(c => 
      c.name.includes("terraform")
    );
    const hasBicep = agent.capabilities.some(c => 
      c.name.includes("bicep")
    );
    
    return (hasTerraform && hasBicep)
      ? []
      : [{
          agent: agent.id || "unknown",
          rule: "azure-agents-support-both-iac",
          severity: "error",
          message: "Azure agents MUST support both Terraform AND Bicep"
        }];
  },

  "data-processors-idempotent": (spec, agent, domain) => {
    if (agent.type !== "data-processor") return [];
    
    const hasIdempotentTrait = agent.traits?.includes("@idempotent");
    return hasIdempotentTrait
      ? []
      : [{
          agent: agent.id || "unknown",
          rule: "data-processors-idempotent",
          severity: "error",
          message: "Data processors MUST be marked @idempotent"
        }];
  },

  // Workflow contract validation
  "workflow-contracts-satisfied": (spec, agent, domain) => {
    const errors: LintError[] = [];
    
    for (const workflow of spec.workflows || []) {
      for (let i = 0; i < workflow.steps.length - 1; i++) {
        const current = spec.agents[workflow.steps[i].agent];
        const next = spec.agents[workflow.steps[i + 1].agent];
        const contract = workflow.contracts?.[i];

        if (contract && current && next) {
          const currentOutputs = workflow.steps[i].outputs || [];
          // Verify contract is satisfied...
        }
      }
    }
    
    return errors;
  }
};

export class AgentSpecLinter {
  private activeRules: LintRule[] = [];

  addRule(rule: LintRule) {
    this.activeRules.push(rule);
  }

  loadDomainRules(domain: string) {
    // Load all rules for domain (could be from plugin system)
    const domainRules = Object.entries(lintRules).filter(([name, _]) =>
      name.includes(domain)
    );
    domainRules.forEach(([_, rule]) => this.addRule(rule));
  }

  lint(spec: AgentSpec, domain: string = "generic"): LintError[] {
    const errors: LintError[] = [];

    for (const [_, agent] of Object.entries(spec.agents)) {
      for (const rule of this.activeRules) {
        errors.push(...rule(spec, agent, domain));
      }
    }

    return errors;
  }
}
```

---

## Phase 3: Emitters (Weeks 3-4)

### 3.1 Agents.md Emitter

**Deliverable**: `agentspec/src/emitters/agents-md.ts`

```typescript
export function emitAgentsMd(spec: AgentSpec): string {
  let md = "# AGENTS.md\n\n";
  md += `Generated from AgentSpec v${spec.version}\n\n`;

  md += "## Overview\n\n";
  md += `${spec.description || "Agent library"}\n\n`;

  for (const [agentId, agent] of Object.entries(spec.agents)) {
    md += `### ${agent.id || agentId}\n\n`;
    md += `**Type**: ${agent.type}\n\n`;
    md += `**Model**: ${agent.model}\n\n`;
    
    if (agent.description) {
      md += `${agent.description}\n\n`;
    }

    if (agent.roles && agent.roles.length > 0) {
      md += `**Roles**: ${agent.roles.join(", ")}\n\n`;
    }

    if (agent.capabilities && agent.capabilities.length > 0) {
      md += "**Capabilities**:\n";
      for (const cap of agent.capabilities) {
        md += `- **${cap.name}**: ${cap.description || ""}\n`;
        if (cap.inputs) {
          md += `  - Inputs: ${cap.inputs.join(", ")}\n`;
        }
        if (cap.outputs) {
          md += `  - Outputs: ${cap.outputs.join(", ")}\n`;
        }
      }
      md += "\n";
    }

    if (agent.constraints && agent.constraints.length > 0) {
      md += "**Constraints**:\n";
      for (const constraint of agent.constraints) {
        md += `- ${constraint}\n`;
      }
      md += "\n";
    }

    if (agent.tools && agent.tools.length > 0) {
      md += `**Tools**: ${agent.tools.join(", ")}\n\n`;
    }
  }

  return md;
}
```

### 3.2 n8n Workflow Emitter

**Deliverable**: `agentspec/src/emitters/n8n-workflow.ts`

This is the high-value emitter—auto-generates n8n workflows from AgentSpec.

```typescript
import { N8nWorkflow, Node, Connection } from "n8n-management";

export function emitN8nWorkflow(spec: AgentSpec, workflowId?: string): N8nWorkflow {
  const workflow: N8nWorkflow = {
    name: spec.name || "Untitled Workflow",
    nodes: [],
    connections: {},
    active: false,
    settings: {},
    pinData: {}
  };

  let nodeIndex = 0;
  const agentNodeMap = new Map<string, Node>();

  // Create n8n nodes for each agent
  for (const [agentId, agent] of Object.entries(spec.agents)) {
    const node: Node = {
      id: nodeIndex.toString(),
      name: agent.id || agentId,
      type: "n8n-nodes-base.executeCommand", // Placeholder
      typeVersion: 1,
      position: [nodeIndex * 300, 0],
      parameters: {
        command: "agentCall",
        agentId,
        model: agent.model,
        systemPrompt: agent.systemPrompt || generateSystemPrompt(agent),
        tools: agent.tools || [],
        constraints: (agent.constraints || []).join("\n")
      }
    };

    workflow.nodes.push(node);
    agentNodeMap.set(agentId, node);
    nodeIndex++;
  }

  // Generate connections from workflow definitions
  for (const workflowDef of spec.workflows || []) {
    for (let i = 0; i < workflowDef.steps.length - 1; i++) {
      const fromAgent = workflowDef.steps[i];
      const toAgent = workflowDef.steps[i + 1];

      const fromNode = agentNodeMap.get(fromAgent.agent);
      const toNode = agentNodeMap.get(toAgent.agent);

      if (fromNode && toNode) {
        const connection: Connection = {
          node: fromNode.name,
          type: "main",
          index: 0,
          source: {
            node: toNode.name,
            type: "main",
            index: 0
          }
        };

        if (!workflow.connections[fromNode.name]) {
          workflow.connections[fromNode.name] = [[connection]];
        } else {
          workflow.connections[fromNode.name][0].push(connection);
        }
      }
    }
  }

  return workflow;
}

function generateSystemPrompt(agent: AgentDefinition): string {
  let prompt = `You are ${agent.id || "an agent"}.`;
  
  if (agent.description) prompt += `\n${agent.description}`;
  if (agent.roles) prompt += `\n\nYour roles: ${agent.roles.join(", ")}`;
  
  if (agent.capabilities && agent.capabilities.length > 0) {
    prompt += "\n\nYou have the following capabilities:";
    for (const cap of agent.capabilities) {
      prompt += `\n- ${cap.name}: ${cap.description || ""}`;
    }
  }

  if (agent.constraints && agent.constraints.length > 0) {
    prompt += "\n\nIMPORTANT CONSTRAINTS:";
    for (const constraint of agent.constraints) {
      prompt += `\n- ${constraint}`;
    }
  }

  return prompt;
}
```

### 3.3 VS Code Extension Config Emitter

**Deliverable**: `agentspec/src/emitters/vscode-config.ts`

```typescript
export interface VSCodeAgentConfig {
  name: string;
  description: string;
  model: string;
  tools: string[];
  instructions: string;
}

export function emitVSCodeConfig(spec: AgentSpec): Record<string, VSCodeAgentConfig> {
  const configs: Record<string, VSCodeAgentConfig> = {};

  for (const [agentId, agent] of Object.entries(spec.agents)) {
    configs[agentId] = {
      name: agent.id || agentId,
      description: agent.description,
      model: agent.model,
      tools: agent.tools || [],
      instructions: agent.systemPrompt || generateInstructions(agent)
    };
  }

  return configs;
}

function generateInstructions(agent: AgentDefinition): string {
  const parts: string[] = [];

  if (agent.description) parts.push(agent.description);

  if (agent.roles) {
    parts.push(`\nYou assume these roles: ${agent.roles.join(", ")}`);
  }

  if (agent.capabilities) {
    parts.push("\nYour capabilities:");
    for (const cap of agent.capabilities) {
      parts.push(`- ${cap.name}: ${cap.description || ""}`);
    }
  }

  if (agent.constraints) {
    parts.push("\nConstraints you MUST follow:");
    for (const constraint of agent.constraints) {
      parts.push(`- ${constraint}`);
    }
  }

  return parts.join("\n");
}
```

### 3.4 OpenAPI Spec Emitter

**Deliverable**: `agentspec/src/emitters/openapi.ts`

Emit OpenAPI 3.1 schema for agent discovery:

```typescript
export function emitOpenAPI(spec: AgentSpec): OpenAPISpec {
  return {
    openapi: "3.1.0",
    info: {
      title: `${spec.name || "Agent Library"} API`,
      version: spec.version,
      description: spec.description
    },
    paths: {
      "/agents": {
        get: {
          summary: "List available agents",
          responses: {
            "200": {
              description: "List of agents",
              content: {
                "application/json": {
                  schema: {
                    type: "array",
                    items: {
                      $ref: "#/components/schemas/Agent"
                    }
                  }
                }
              }
            }
          }
        }
      },
      "/agents/{agentId}": {
        get: {
          summary: "Get agent details",
          parameters: [{
            name: "agentId",
            in: "path",
            required: true,
            schema: { type: "string" }
          }],
          responses: {
            "200": {
              description: "Agent details",
              content: {
                "application/json": {
                  schema: { $ref: "#/components/schemas/Agent" }
                }
              }
            }
          }
        }
      }
    },
    components: {
      schemas: {
        Agent: {
          type: "object",
          properties: {
            id: { type: "string" },
            type: { 
              type: "string",
              enum: ["specialist", "generalist", "data-processor", "orchestrator"]
            },
            description: { type: "string" },
            model: { type: "string" },
            capabilities: {
              type: "array",
              items: { $ref: "#/components/schemas/Capability" }
            },
            constraints: { type: "array", items: { type: "string" } },
            tools: { type: "array", items: { type: "string" } }
          }
        },
        Capability: {
          type: "object",
          properties: {
            name: { type: "string" },
            description: { type: "string" },
            inputs: { type: "array", items: { type: "string" } },
            outputs: { type: "array", items: { type: "string" } }
          }
        }
      }
    }
  };
}
```

---

## Phase 4: GenerateAgents.md Integration (Week 4)

### 4.1 AgentSpec Generator in GenerateAgents.md

**Deliverable**: `GenerateAgents.md/src/autogenerateagentsmd/agentspec_generator.py`

Extended DSPy module:

```python
import dspy
from typing import List, Dict, Any

class CodebaseToAgentSpec(dspy.Module):
    """
    Analyzes a codebase and generates formal AgentSpec.
    Uses DSPy RLM (Recursive Language Models) for multi-pass analysis.
    """
    
    def __init__(self):
        super().__init__()
        self.convention_extractor = Convention.Extractor()
        self.anti_pattern_detector = AntiPattern.Detector()
        self.workflow_designer = Workflow.Designer()
    
    def forward(
        self,
        codebase_summary: str,
        architecture_patterns: List[str],
        git_anti_patterns: List[str]
    ) -> Dict[str, Any]:
        """
        Input: Codebase analysis + architectural patterns + anti-patterns
        Output: Structured AgentSpec dictionary
        
        Process:
        1. Identify required agent roles for this codebase (code analyst, architect, tester, etc.)
        2. Define capabilities for each role
        3. Specify constraints based on codebase patterns
        4. Design workflow connections between agents
        5. Return AgentSpec-compatible dictionary
        """
        
        # Extract conventions (existing RLM-based behavior)
        conventions = self.convention_extractor.forward(
            codebase_summary, architecture_patterns
        )
        
        # Detect anti-patterns from git history
        constraints = self.anti_pattern_detector.forward(git_anti_patterns)
        
        # Design agent workflows
        workflows = self.workflow_designer.forward(
            conventions, architecture_patterns
        )
        
        # Compile into AgentSpec
        return {
            "version": "1.0.0",
            "domain": self._infer_domain(codebase_summary),
            "agents": self._generate_agents(conventions, constraints),
            "workflows": workflows,
            "metadata": {
                "generated_from": codebase_summary,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _infer_domain(self, codebase_summary: str) -> str:
        """Infer domain from codebase analysis"""
        domains = {
            "azure": ["bicep", "arm", "azurerm"],
            "github": ["octokit", "github", "pr", "issue"],
            "infrastructure": ["terraform", "cloudformation", "pulumi"],
            "data": ["spark", "pandas", "polars", "dbt"],
            "security": ["vault", "secrets", "cryptography", "jwt"]
        }
        
        summary_lower = codebase_summary.lower()
        for domain, keywords in domains.items():
            if any(kw in summary_lower for kw in keywords):
                return domain
        
        return "generic"
    
    def _generate_agents(
        self,
        conventions: Dict[str, Any],
        constraints: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Generate agent definitions from conventions"""
        agents = {}
        
        # Base agents for all codebases
        agents["CodeAnalyst"] = {
            "type": "specialist",
            "description": "Analyzes code patterns and architecture",
            "roles": ["analyst", "reviewer"],
            "model": "claude-opus",
            "capabilities": [
                {
                    "name": "code-structure-analysis",
                    "description": "Identify code organization, patterns, and structure",
                    "inputs": ["codebase"],
                    "outputs": ["structure-report"]
                },
                {
                    "name": "dependency-mapping",
                    "description": "Map dependencies between modules",
                    "inputs": ["codebase"],
                    "outputs": ["dependency-graph"]
                }
            ],
            "tools": ["code-parser", "ast-analyzer"]
        }
        
        # Domain-specific agents
        if conventions.get("architecture") == "microservices":
            agents["ServiceArchitect"] = {
                "type": "specialist",
                "description": "Designs microservice architectures",
                "roles": ["architect"],
                "model": "claude-opus",
                "capabilities": [...],
                "tools": [...]
            }
        
        # Add constraints from anti-patterns
        for agentId in agents:
            agents[agentId]["constraints"] = constraints
        
        return agents
```

### 4.2 CLI Extension

**Deliverable**: `GenerateAgents.md/src/autogenerateagentsmd/cli.py`

Add new commands:

```bash
# Generate AgentSpec
uv run autogenerateagentsmd /path/to/repo --output-format agentspec

# Emit multiple formats from AgentSpec
uv run autogenerateagentsmd --agentspec-file agents.agentspec --emit agents-md,n8n-workflow,openapi,vscode-config

# Validate AgentSpec against domain rules
uv run autogenerateagentsmd --agentspec-file agents.agentspec --lint --domain azure
```

### 4.3 GenerateAgents MCP Server Extension

**Deliverable**: `generateagents-mcp/server.py` extensions

```python
@mcp_server.tool("generate_agentspec")
def generate_agentspec(
    repo_path: str = None,
    github_repository: str = None,
    style: str = "comprehensive",
    domain: str = "generic"
) -> AgentSpec:
    """
    Analyze repository and emit formal AgentSpec JSON.
    
    Args:
        repo_path: Local repository path
        github_repository: GitHub repository URL
        style: "comprehensive" or "strict"
        domain: Domain for linting (azure, github, infrastructure, etc.)
    
    Returns: Formal AgentSpec with agents, capabilities, constraints, workflows
    """
    # Reuse existing GenerateAgents logic, emit AgentSpec instead
    pass

@mcp_server.tool("emit_agents")
def emit_agents(
    agentspec_path: str,
    targets: List[str]
) -> Dict[str, str]:
    """
    Emit AgentSpec to multiple formats.
    
    Args:
        agentspec_path: Path to .agentspec.json file
        targets: List of emitters (agents-md, n8n-workflow, openapi, vscode-config)
    
    Returns: Dict mapping target → emitted content/path
    """
    pass

@mcp_server.tool("validate_agentspec")
def validate_agentspec(
    agentspec_path: str,
    domain: str = "generic"
) -> List[LintError]:
    """
    Lint AgentSpec against domain-specific rules.
    
    Returns: List of validation errors/warnings
    """
    pass

@mcp_server.tool("compose_agents")
def compose_agents(
    base_specs: List[str],
    output_path: str
) -> AgentSpec:
    """
    Compose multiple AgentSpecs into unified library.
    Detects conflicts, validates contracts.
    
    Returns: Merged AgentSpec
    """
    pass
```

---

## Phase 5: Awesome Copilot Integration (Week 5)

### 5.1 Dual Format Support

**Deliverable**: Update Awesome Copilot to consume both `.agent.md` and `.agentspec` files.

```
awesome-copilot/
├── agents/                    # Backward compat: .agent.md files
├── agent-specs/               # NEW: .agentspec.json files
│   ├── github-patterns/
│   │   └── 1.0.0/
│   │       └── agents.agentspec.json
│   └── azure-patterns/
│       └── 2.0.0/
│           └── agents.agentspec.json
└── emitted/                   # Auto-generated from .agentspec files
    ├── agents-md/
    ├── n8n-workflows/
    ├── vscode-configs/
    └── openapi-specs/
```

### 5.2 Build Pipeline

**Deliverable**: `awesome-copilot/build.js` enhancements

```javascript
const fs = require("fs");
const path = require("path");
const { AgentSpecCompiler } = require("agentspec");

async function buildAwesomeCopilot() {
  // 1. Find all .agentspec files
  const agentSpecFiles = walkDir("./agent-specs").filter(f => 
    f.endsWith(".agentspec.json")
  );

  // 2. Compile each spec
  for (const specFile of agentSpecFiles) {
    const compiler = new AgentSpecCompiler("./schema/agentspec-1.0.0.json");
    const spec = compiler.parse(specFile);

    // 3. Validate
    const errors = compiler.lint(spec, spec.domain || "generic");
    if (errors.length > 0) {
      console.error(`Linting errors in ${specFile}:`, errors);
      process.exit(1);
    }

    // 4. Emit to all formats
    const emitters = {
      "agents-md": emitAgentsMd(spec),
      "n8n-workflow": emitN8nWorkflow(spec),
      "vscode-config": emitVSCodeConfig(spec),
      "openapi": emitOpenAPI(spec)
    };

    for (const [format, content] of Object.entries(emitters)) {
      const outPath = path.join("./emitted", format, stripExt(specFile) + ext);
      fs.writeFileSync(outPath, JSON.stringify(content, null, 2));
    }
  }

  // 5. Generate marketplace.json (existing)
  // ... existing marketplace generation
}

buildAwesomeCopilot();
```

---

## Success Metrics

By end of Phase 5, measure success by:

1. **Tool Completeness**: All 5 core tools operational (generate_agentspec, emit_agents, validate_agentspec, compose_agents, list_agents)
2. **Format Coverage**: Can emit to AGENTS.md, n8n workflows, VS Code configs, OpenAPI specs
3. **Example Adoption**: 3-5 production AgentSpecs demonstrate real-world use cases
4. **Linting Effectiveness**: Domain-specific rules catch 80%+ of common mistakes
5. **Composition Works**: Can merge multiple AgentSpecs without conflicts
6. **n8n Integration**: Auto-generated workflows successful execute without manual tweaks

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| AgentSpec schema changes | Use semantic versioning, migrate tools, generate migration guides |
| Breaking emitters | Keep backward-compat with AGENTS.md; emitters are additive |
| Adoption friction | Ship with 5+ ready-to-use AgentSpec examples |
| Performance (parsing large specs) | Pre-compile, cache, use streaming for large workflows |
| Tool conflicts (multiple specs define same agent) | Strong conflict detection at merge time, clear error messages |

---

## Next Steps

1. **Approve schema** (Phase 1.1) with stakeholder feedback
2. **Prototype n8n emitter** to prove immediate business value (Phase 3.2)
3. **Build example AgentSpecs** to validate ergonomics
4. **Gather team feedback** before full rollout
5. **Plan Awesome Copilot integration** strategy

