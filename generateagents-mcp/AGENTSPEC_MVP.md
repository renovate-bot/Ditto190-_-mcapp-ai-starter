# AgentSpec MVP

**Status:** ✅ Working with real data (175 agents, 205 skills from awesome-copilot)

## What It Does

Parses real agents and skills from awesome-copilot, generates validated schemas, and exposes them via MCP tools.

**Core Functions:**
1. **Parse** `.agent.md` files from `awesome-copilot/agents/`
2. **Parse** `SKILL.md` files from `awesome-copilot/skills/*/`
3. **Generate** AgentSpec JSON schema matching real data
4. **Validate** schema compliance (required fields, types)

## MVP Scope (No Feature Creep)

✅ **Included:**
- Parse frontmatter from .agent.md and SKILL.md files
- Generate schema with agents{} and tools{} matching real sources
- Validate required fields (version, name, agents, tools)
- Round-trip: generate -> save -> load -> validate
- MCP tool integration (generate_agentspec, validate_agentspec)

❌ **Excluded (for now):**
- Complex validation (circular deps, reserved names, etc.)
- Artifact emission (AGENTS.md, n8n workflows)
- Skill extraction/management
- Tool reference validation
- Abstract patterns and frameworks

## Quick Start

```python
from agentspec_mvp import generate_agentspec_from_awesome_copilot, validate_agentspec_file

# Generate from real data
result = generate_agentspec_from_awesome_copilot(
    awesome_copilot_path="../awesome-copilot",
    output_path="awesome-copilot.agentspec.json"
)

print(f"Generated: {result['agent_count']} agents, {result['skill_count']} skills")

# Validate
validation = validate_agentspec_file("awesome-copilot.agentspec.json")
print(f"Valid: {validation['is_valid']}")
```

## MCP Tools

### `generate_agentspec(awesome_copilot_path?, output_name?)`

Generates AgentSpec from real awesome-copilot data.

**Parameters:**
- `awesome_copilot_path` (optional): Path to awesome-copilot directory (default: `../awesome-copilot`)
- `output_name` (optional): Output filename (default: `awesome-copilot.agentspec.json`)

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

### `validate_agentspec(agentspec_path)`

Validates AgentSpec JSON file.

**Parameters:**
- `agentspec_path`: Path to AgentSpec JSON file

**Returns:**
```json
{
  "success": true,
  "agentspec_path": "/path/to/file.json",
  "is_valid": true,
  "errors": [],
  "error_count": 0
}
```

## Schema Structure

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
      "description": "Analyze Terraform plan JSON output...",
      "type": "skill",
      "source_file": "/path/to/awesome-copilot/skills/terraform-azurerm-set-diff-analyzer/SKILL.md"
    }
  }
}
```

## Validation Rules

**Top-level required fields:**
- `version` (string)
- `name` (string)
- `agents` (object)
- `tools` (object)

**Agent required fields:**
- `name` (string)
- `description` (string)
- `type` (string)
- `source_file` (string)

**Tool required fields:**
- `name` (string)
- `description` (string)
- `type` (string)
- `source_file` (string)

## Test Coverage

**Tests:** 11 passing (7 MVP + 4 integration)

```bash
# Run MVP tests
uv run pytest tests/test_agentspec_mvp.py -v

# Run integration tests
uv run pytest tests/test_mvp_integration.py -v

# Run all tests
uv run pytest tests/ -v
```

**Test breakdown:**
- ✅ Parse 175 agents from awesome-copilot
- ✅ Parse 205 skills from awesome-copilot
- ✅ Generate valid AgentSpec schema
- ✅ Validate generated schema passes compliance
- ✅ Round-trip (generate -> save -> load -> validate)
- ✅ Schema compliance (all required fields present)
- ✅ MCP server integration (tools wired correctly)
- ✅ End-to-end workflow via MCP tools

## Files

- **`agentspec_mvp.py`** — MVP implementation (265 lines)
- **`tests/test_agentspec_mvp.py`** — MVP tests (230 lines)
- **`tests/test_mvp_integration.py`** — MCP integration tests (130 lines)

## Design Decisions

### Why MVP?

Focus on **reliability, validity, and compliance** with real data. No abstractions, no feature creep. Just parse, validate, test.

### Why Real Data?

Testing against real awesome-copilot agents/skills ensures schema matches reality. No mock data, no hypotheticals.

### Why Simple Validation?

Complex validation (circular deps, reserved names, etc.) is for later. MVP validates schema structure only.

### Why No Artifact Emission?

Generating AGENTS.md and n8n workflows adds complexity. MVP focuses on schema generation and validation only.

## Next Steps (Not MVP)

After MVP is stable and integrated:
1. Add artifact emission (AGENTS.md, n8n workflows)
2. Add tool reference validation
3. Add circular dependency detection
4. Add skill extraction/management
5. Add complex validation patterns

**But first:** Make MVP work, test it, keep testing it, integrate it into flow.

## Success Criteria

✅ Parses real agents and skills from awesome-copilot  
✅ Generates valid AgentSpec schema  
✅ Validation passes for generated schema  
✅ All tests pass (11/11)  
✅ Integrated into MCP server tools  
✅ Round-trip works (generate -> save -> load -> validate)  
✅ No feature creep, no abstractions  

**Status:** MVP Complete. Ready for integration.
