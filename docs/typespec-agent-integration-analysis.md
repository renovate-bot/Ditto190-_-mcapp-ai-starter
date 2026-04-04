# TypeSpec-Inspired Agent Specification Framework

## Executive Summary

Microsoft's TypeSpec is a language for defining cloud service APIs as composable, reusable patterns that can be compiled to multiple output formats (OpenAPI, client code, docs, etc.) while maintaining a **single source of truth**. We can apply this same architectural pattern to **composable AI agents**, creating an "**AgentSpec**" framework that transforms the current system from a documentation-focused pipeline into a formal, specification-driven one.

**Current System**: Codebase → GenerateAgents.md (DSPy RLM) → AGENTS.md → Awesome Copilot Agents (manual packaging)

**Proposed System**: Codebase → AgentSpec (DSPy RLM) → Emitters (AGENTS.md, n8n workflows, VS Code configs, OpenAPI, etc.) → Awesome Copilot Libraries (formal versioning & composition)

---

## What is TypeSpec?

TypeSpec is a **language for defining cloud APIs** with these key characteristics:

| Concept | TypeSpec | Applied to Agents |
|---------|----------|-------------------|
| **Source of Truth** | Single `.tsp` file defines API shape | Single `.agentspec` defines agent capabilities/interface |
| **Reusable Patterns** | Libraries like `@typespec/http`, `@typespec/rest`, `@typespec/openapi3` | Libraries like `@agentspec/github-patterns`, `@agentspec/cloud-patterns` |
| **Composition** | Import patterns via `using` declarations, combine traits with decorators | Compose agents from capability modules, inherit from base patterns |
| **Linting** | Rich linter framework flags anti-patterns | Validate agents against domain rules (e.g., "cloud agents must support Terraform AND Bicep") |
| **Multiple Outputs** | Single definition emits OpenAPI, client code, documentation, SDK | Single spec emits AGENTS.md, n8n workflows, VS Code configs, MCP manifests |
| **Versioning** | NPM packages with semver, `@latest` and `@next` tags | Agent library versions with dependency resolution |

### TypeSpec Example

```typescript
import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using Http;
using Rest;

@service(#{ title: "Pet Store Service" })
@server("https://example.com", "The service endpoint")
namespace PetStore;

@route("/pets")
interface Pets {
  list(): Pet[];
}

model Pet {
  @minLength(100)
  name: string;
  @minValue(0)
  @maxValue(100)
  age: int32;
  kind: "dog" | "cat" | "fish";
}
```

**Key Insight**: Declarative, composable, formally typed, single source of truth.

---

## AgentSpec Framework Design

### 1. AgentSpec Language (Formal Specification)

```yaml
# example-agents.agentspec
version: "1.0.0"
domain: "cloud-infrastructure"
description: "Composable agents for cloud infrastructure orchestration"

agents:
  # Base agent pattern
  CloudArchitect:
    type: "specialist"
    roles: ["architect", "reviewer"]
    capabilities:
      - name: "terraform-design"
        description: "Design Terraform modules"
        inputs: [architecture, constraints]
        outputs: [tf-module-spec]
      - name: "multi-cloud-planning"
        description: "Plan multi-cloud deployments"
        inputs: [workload, regions, compliance]
        outputs: [deployment-plan]
    constraints:
      - "must support both IaC and Azure Verified Modules"
      - "must validate against cloud security policies"
    tools:
      - "terraform-parser"
      - "azure-iac-validator"
    model: "claude-opus"
    mcp-servers:
      - "github:microsoft/typespec-mcp"
      - "local:terraform-validator"

  # Composed agent (inherits from pattern)
  AzureArchitect:
    extends: "CloudArchitect"
    domain: "azure"
    capabilities:
      - name: "bicep-compilation"
        inputs: [bicep-file]
        outputs: [arm-template]
    constraints:
      - "bicep files MUST compile to valid ARM templates"
      - "all resources MUST use Azure Verified Modules"

  # Data processor agent
  TerraformStateBrowser:
    type: "data-processor"
    capabilities:
      - name: "parse-state-files"
        inputs: [terraform-state]
        outputs: [parsed-resources, dependency-graph]
    constraints:
      - "must be idempotent (no side effects)"
      - "must validate state before processing"
    model: "claude-haiku"

# Reusable trait/pattern library
patterns:
  IaCValidator:
    decorators:
      - "@idempotent"      # Self-healing, side-effect free
      - "@versioned"       # Tracks IaC versions
      - "@audit-logged"    # All operations logged
    capabilities:
      - "validate-syntax"
      - "check-compliance"
      - "lint-conventions"

# Data contracts between agents
workflows:
  DeploymentOrchestration:
    steps:
      - agent: CloudArchitect
        outputs: [deployment-plan]
      - agent: AzureArchitect
        inputs: [deployment-plan]
        outputs: [bicep-templates]
      - agent: TerraformStateBrowser
        inputs: [bicep-templates]
        outputs: [resource-inventory]
    contracts:
      - "deployment-plan must specify Azure regions"
      - "bicep-templates must pass ARM validation"
      - "resource-inventory must have no missing dependencies"
```

---

### 2. DSPy Module in GenerateAgents.md

Extend `GenerateAgents.md` with new DSPy modules:

```python
# src/autogenerateagentsmd/agentspec_modules.py

class CodebaseToAgentSpec(dspy.Module):
    """
    Analyzes codebase and emits formal AgentSpec.
    Uses DSPy RLM (Recursive Language Models) for multi-pass analysis.
    """
    
    def forward(self, codebase_analysis: str, git_history: str) -> str:
        """
        Input: Codebase analysis + reverted commits
        Output: Formal AgentSpec YAML defining recommended agents
        
        Process:
        1. Extract architectural patterns (monolithic/microservices/serverless)
        2. Identify domain roles (data engineer, infra architect, security reviewer)
        3. Detect anti-patterns from reverted commits
        4. Define agent capabilities and constraints
        5. Specify data contracts between agents
        """
        pass

class AgentSpecValidator(dspy.Module):
    """
    Validates AgentSpec against linting rules and constraints.
    Similar to TypeSpec's linter framework.
    """
    
    def forward(self, agentspec: str, domain: str) -> List[ValidationError]:
        """
        Validates:
        - All agents have required fields (name, capabilities, model)
        - Capabilities have matching inputs/outputs
        - Constraints are achievable
        - Data contracts between workflows are compatible
        - Anti-patterns from domain are avoided
        """
        pass
```

---

### 3. Emitter Framework (Multi-Format Output)

Similar to TypeSpec's emitter architecture, create backends:

```
agentspec/
├── src/
│   ├── compiler.ts           # Parser & validator
│   ├── emitters/
│   │   ├── agents-md.ts      # → AGENTS.md (current format)
│   │   ├── n8n-workflow.ts   # → n8n workflow JSON
│   │   ├── vscode-config.ts  # → VS Code extension manifest
│   │   ├── openapi.ts        # → OpenAPI spec for agent discovery
│   │   ├── mcp-manifest.ts   # → MCP server config
│   │   └── agent-schema.ts   # → TypeScript interfaces for VS Code CDLS
│   └── linter.ts             # Validation rules
```

**Example: n8n Emitter**

```typescript
// agentspec/src/emitters/n8n-workflow.ts

function emitN8nWorkflow(agentspec: AgentSpec): N8nWorkflow {
  const workflow = {
    name: agentspec.id,
    nodes: [],
    connections: []
  };
  
  agentspec.agents.forEach(agent => {
    // Create n8n node for each agent capability
    workflow.nodes.push({
      name: agent.name,
      type: "agentNode",  // Custom n8n node type
      parameters: {
        model: agent.model,
        tools: agent.tools,
        constraints: agent.constraints,
        systemPrompt: generateSystemPrompt(agent)
      }
    });
  });
  
  // Auto-generate connections from workflow data contracts
  agentspec.workflows.forEach(wf => {
    wf.steps.forEach((step, i) => {
      if (i < wf.steps.length - 1) {
        workflow.connections.push({
          from: wf.steps[i],
          to: wf.steps[i + 1],
          contract: wf.contracts[i]
        });
      }
    });
  });
  
  return workflow;
}
```

---

## Integration Points

### A. GenerateAgents.md CLI Extension

```bash
# Generate AgentSpec instead of (or alongside) AGENTS.md
uv run autogenerateagentsmd /path/to/repo --output-format agentspec

# Emit multiple formats from existing AgentSpec
uv run autogenerateagentsmd --agentspec-file agents.agentspec --emit agents-md,n8n-workflow,openapi,vscode-config

# Analyze git history and deduce anti-patterns for AgentSpec linting
uv run autogenerateagentsmd --github-repository <url> --analyze-git-history --output-format agentspec --lint-rules "cloud-patterns"
```

### B. GenerateAgents MCP Server Extension

New MCP tools:

```python
# generateagents-mcp/server.py

@mcp_server.tool("generate_agentspec")
def generate_agentspec(repo_path: str, style: str = "comprehensive") -> AgentSpec:
    """Analyze repo and emit formal AgentSpec"""
    pass

@mcp_server.tool("emit_agents")
def emit_agents(agentspec_path: str, targets: List[str]) -> Dict[str, str]:
    """Emit AgentSpec to multiple formats: agents-md, n8n-workflow, openapi, vscode-config"""
    pass

@mcp_server.tool("validate_agentspec")
def validate_agentspec(agentspec_path: str, domain: str = "generic") -> List[ValidationError]:
    """Lint AgentSpec against domain-specific rules"""
    pass

@mcp_server.tool("compose_agents")
def compose_agents(base_specs: List[str], output_spec: str) -> AgentSpec:
    """Compose multiple AgentSpecs into unified agent library"""
    pass
```

### C. Awesome Copilot Library Evolution

```
awesome-copilot/
├── agents/                    # Backward compat: .agent.md files
├── agent-specs/               # NEW: Versioned .agentspec files
│   ├── github-patterns/
│   │   ├── 1.0.0/
│   │   │   ├── agents.agentspec
│   │   │   └── README.md
│   │   └── 2.0.0/
│   │       └── agents.agentspec
│   ├── cloud-patterns/
│   └── n8n-orchestration/
├── emitted-artifacts/         # Generated from .agentspec files
│   ├── agents-md/
│   ├── n8n-workflows/
│   ├── vscode-configs/
│   └── openapi-specs/
└── package.json
```

**Versioning & Composition**:

```yaml
# awesome-copilot/agent-specs/github-patterns/2.0.0/agents.agentspec
version: "2.0.0"
name: "github-patterns"
description: "GitHub API agents with PR/issue automation"
exportedPatterns:
  - "CodeReviewAgent"
  - "IssueTriageAgent"
  - "PRAutomationAgent"

---

# awesome-copilot/agent-specs/my-org-standard/1.0.0/agents.agentspec
version: "1.0.0"
dependencies:
  "@awesome/github-patterns": "^2.0.0"
  "@awesome/azure-patterns": "^1.5.0"
  "@awesome/security-patterns": "^3.0.0"

agents:
  OrgPolicyEnforcer:
    extends: ["CodeReviewAgent", "SecurityValidator"]
    constraints:
      - "must check org security policies"
      - "must verify Azure resource naming"
```

This enables **agent package management** similar to npm—organizations can define standard agent patterns, version them, and compose them into compliance-checked solutions.

---

## Use Cases & Benefits

### 1. **Multi-Format Agent Generation**
- **Today**: Write AGENTS.md by hand, manually create n8n workflows, manually configure VS Code agents
- **With AgentSpec**: Write once, auto-generate AGENTS.md + n8n workflows + VS Code configs + Claude Desktop manifests

### 2. **Composable Agent Libraries**
- **Today**: Copy-paste agent code between projects
- **With AgentSpec**: Define reusable agent patterns in versioned libraries, compose them with dependency resolution

### 3. **Enterprise Standardization**
- **Today**: Each team writes agents differently
- **With AgentSpec**: Define org-wide agent patterns, enforce via linting, auto-generate compliant agents

### 4. **Anti-Pattern Prevention**
- **Today**: Developers accidentally create agents that violate security/performance constraints
- **With AgentSpec**: Linter catches anti-patterns during agent design phase

### 5. **n8n Workflow Automation**
- **Today**: Manually design n8n workflows, wire up agents as nodes
- **With AgentSpec**: Auto-generate n8n workflow JSON from agent specs, with proper data contracts

### 6. **Agent Marketplace Discovery**
- **Today**: Browse hardcoded agents in Awesome Copilot repo
- **With AgentSpec**: Query OpenAPI-exposed agent specs, discover agents by capability, auto-generate integration code

### 7. **Continuous Agent Improvement**
- **Today**: Agent definitions are static documentation
- **With AgentSpec**: Run **codebase analysis → AgentSpec generation → linting → emitting** as CI/CD step, auto-update agents as code evolves

---

## Immediate Wins (MVP)

### Phase 1: Foundation (Weeks 1-2)
1. **Define AgentSpec Schema** (TypeScript/JSON schema)
   - Core fields: name, roles, capabilities, constraints, tools, model, mcp-servers
   - Reusable patterns/traits
   - Workflow data contracts

2. **Extend GenerateAgents.md** 
   - Add `CodebaseToAgentSpec` DSPy module
   - New CLI flag: `--output-format agentspec`

3. **Build n8n Emitter**
   - AgentSpec → n8n workflow JSON
   - Auto-generate workflow nodes, connections, constraints

### Phase 2: Expansion (Weeks 3-4)
4. **Build VS Code + OpenAPI Emitters**
5. **Add AgentSpec Linting Framework**
   - Domain-specific rules (cloud, github, security, etc.)
   - Emitted as part of validation

6. **Awesome Copilot Integration**
   - Support both `.agent.md` (legacy) and `.agentspec` (new)
   - Auto-emit AGENTS.md from AgentSpec

### Phase 3: Composition (Weeks 5+)
7. **Agent Library Versioning**
   - NPM packages for agent patterns: `@awesome/github-patterns@2.0.0`
   - Dependency resolution

8. **Agent Spec Composition Tool**
   - Merge multiple AgentSpecs
   - Validate cross-spec contracts

---

## Architecture Diagram

```
                         Codebase
                            ↓
              ┌─────────────────────────────┐
              │  GenerateAgents.md (DSPy)   │
              │  + AgentSpec Module (RLM)   │
              └──────────────┬──────────────┘
                             ↓
                        AgentSpec
                      (Formal Language)
                             ↓
        ┌────────────────────┼────────────────────┐
        ↓                    ↓                    ↓
   Agents.md            n8n Workflows       VS Code Config
   OpenAPI Spec       MCP Manifests         Claude Desktop
        ↓                    ↓                    ↓
        └────────────────────┼────────────────────┘
                             ↓
                    Awesome Copilot
                   (Versioned Libraries)
                             ↓
       ┌──────────────────────┴──────────────────────┐
       ↓                                              ↓
  Prompt Registry                          n8n Workflow Execution
  (Agent Marketplace)                     (Automated Orchestration)
```

---

## Key Principles

### 1. **Single Source of Truth**
Like TypeSpec APIs, AgentSpec is the definitive source—all outputs are generated, never hand-edited.

### 2. **Composability**
Agents are modular capabilities that can be combined with formal contracts, not monolithic entities.

### 3. **Formality with Flexibility**
AgentSpec is strictlytyped but extensible—you can add domain-specific traits and constraints.

### 4. **Multi-Output Compilation**
One AgentSpec definition targets all platforms (n8n, VS Code, Claude, OpenAPI, MCP, etc.).

### 5. **Anti-Pattern Prevention**
Linting framework catches mistakes before agents are deployed.

---

## Comparison: Current vs. Proposed

| Dimension | Current | With AgentSpec |
|-----------|---------|----------------|
| **Source Format** | Free-form AGENTS.md | Formal AgentSpec YAML/JSON |
| **Generation** | DSPy RLM → Text | DSPy RLM → Structured Spec |
| **Outputs** | Single (AGENTS.md) | Multiple (AGENTS.md, n8n, VS Code, OpenAPI, etc.) |
| **Reusability** | Copy-paste agent files | Import versioned libraries with dependency resolution |
| **Validation** | Manual review | Automated linting against domain rules |
| **Composition** | Not supported | Formal contracts between agents |
| **n8n Workflows** | Manual design | Auto-generated from specs |
| **Versioning** | Ad-hoc | Semver with npm-style resolution |
| **Enterprise Scale** | Difficult | Native support for org-wide standards |

---

## Next Steps

1. **Prototype AgentSpec schema** with sample agents (GitHub patterns, Azure patterns, n8n patterns)
2. **Build n8n emitter** to prove end-to-end workflow generation
3. **Extend GenerateAgents.md CLI** with `--output-format agentspec`
4. **Gather feedback** from team on schema ergonomics and pain points
5. **Plan Awesome Copilot integration** to support both `.agent.md` and `.agentspec`
6. **Consider partnering with TypeSpec team** for possible IDE/tooling alignment

---

## References

- [TypeSpec GitHub](https://github.com/microsoft/typespec)
- [TypeSpec Documentation](https://typespec.io/docs)
- [TypeSpec Emitter Documentation](https://typespec.io/docs/extending-typespec/emitters)
- [Current GenerateAgents.md README](/workspaces/self-hosted-ai-starter-kit/GenerateAgents.md/README.md)
- [Current Awesome Copilot README](/workspaces/self-hosted-ai-starter-kit/awesome-copilot/README.md)
