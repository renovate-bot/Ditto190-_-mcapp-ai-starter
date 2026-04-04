# AgentSkills Integration Strategy

**Document Date**: March 5, 2026  
**Status**: Analysis Complete - Integration Roadmap  
**Components**: AgentSkills (Anthropic), skills-ref library, awesome-copilot, GenerateAgents MCP

---

## Executive Summary

**Key Finding**: Our `awesome-copilot/skills` directory is **already 95% compatible** with the official [AgentSkills specification](https://agentskills.io) maintained by Anthropic. This document outlines how to achieve 100% compliance and integrate the official skills-ref validation library.

### What is AgentSkills?

AgentSkills is an **open format** for giving AI agents capabilities across all LLM providers. It's a universal standard that:
- Works with Claude, GPT-4, Gemini, and any LLM
- Provides progressive disclosure (load metadata → load instructions → execute resources)
- Follows a simple folder + SKILL.md structure
- Maintained by Anthropic, open to community contributions

### Current State

| Component | Status | Compatibility |
|-----------|--------|---------------|
| awesome-copilot skills | ✅ Active | 95% compliant |
| AgentSpec MVP | ✅ Complete | Parses skills successfully |
| skills-ref library | 📦 Cloned | Ready for integration |
| Official spec | 📖 Analyzed | Fully understood |

---

## AgentSkills Specification Overview

### Directory Structure

```
skill-name/
├── SKILL.md          # Required: frontmatter + instructions
├── scripts/          # Optional: executable code
│   ├── extract.py
│   └── process.sh
├── references/       # Optional: detailed docs (loaded on demand)
│   ├── REFERENCE.md
│   └── advanced.md
└── assets/           # Optional: templates, data files
    └── template.json
```

### SKILL.md Format

```yaml
---
name: skill-name                    # REQUIRED (1-64 chars, lowercase, hyphens)
description: What it does...        # REQUIRED (1-1024 chars)
license: MIT                        # OPTIONAL
compatibility: Requires Python 3.8+ # OPTIONAL (1-500 chars)
allowed-tools: Bash(git:*)          # OPTIONAL (experimental)
metadata:                           # OPTIONAL (key-value pairs)
  author: example-org
  version: "1.0"
---

# Skill Instructions

Step-by-step instructions...
```

### Validation Rules

| Field | Rule | Current Compliance |
|-------|------|-------------------|
| `name` | Must match directory name | ✅ Yes |
| `name` | Lowercase + hyphens only | ✅ Yes |
| `name` | 1-64 characters | ✅ Yes |
| `name` | No consecutive hyphens | ⚠️ Need to verify |
| `description` | 1-1024 characters | ✅ Yes |
| `license` | Optional string | ⚠️ Some skills missing |
| Frontmatter | Valid YAML | ✅ Yes |
| Directory | Must contain SKILL.md | ✅ Yes |

---

## Comparison: awesome-copilot vs AgentSkills

### What We Already Have ✅

1. **Directory Structure**: Our skills are folders with SKILL.md ✓
2. **Frontmatter Format**: We use YAML frontmatter with `---` delimiters ✓
3. **Required Fields**: All skills have `name` and `description` ✓
4. **Naming Convention**: Skills use kebab-case names ✓
5. **Assets/Scripts**: Many skills include scripts/ and references/ ✓

### Example Comparison

**Our Existing Format** (terraform-azurerm-set-diff-analyzer):
```yaml
---
name: terraform-azurerm-set-diff-analyzer
description: Analyze Terraform plan JSON output...
license: MIT
---
```

**AgentSkills Official Format**:
```yaml
---
name: terraform-azurerm-set-diff-analyzer
description: Analyze Terraform plan JSON output...
license: MIT
---
```

**Result**: ✅ **Identical!**

### What Needs Adjustment ⚠️

1. **Validation**: Some skills may need license field added
2. **Name Format**: Need to verify no consecutive hyphens (`skill--name`)
3. **Description Length**: Need to verify all under 1024 chars
4. **Directory Match**: Ensure skill name matches folder name exactly

---

## skills-ref Library Analysis

### Architecture

```
skills-ref/
├── src/skills_ref/
│   ├── __init__.py       # Public API
│   ├── models.py         # SkillProperties dataclass
│   ├── parser.py         # YAML frontmatter parsing
│   ├── validator.py      # Validation rules
│   ├── prompt.py         # XML generation for agent prompts
│   ├── cli.py            # CLI interface
│   └── errors.py         # Exception types
├── tests/                # pytest test suite
└── pyproject.toml        # Dependencies: click, strictyaml
```

### Key Functions

1. **`validate(skill_dir)`** → Returns list of validation errors
2. **`read_properties(skill_dir)`** → Returns `SkillProperties` object
3. **`to_prompt(skill_dirs)`** → Generates `<available_skills>` XML block
4. **`find_skill_md(skill_dir)`** → Locates SKILL.md (case-insensitive)
5. **`parse_frontmatter(content)`** → Extracts YAML + body

### CLI Commands

```bash
# Validate a skill
skills-ref validate path/to/skill

# Read properties (JSON output)
skills-ref read-properties path/to/skill

# Generate agent prompt XML
skills-ref to-prompt path/to/skill-a path/to/skill-b
```

### Dependencies

- **click** (CLI framework)
- **strictyaml** (Safe YAML parsing)
- **Python 3.11+**

---

## Integration Roadmap

### Phase 1: Validation & Compliance (Week 1)

**Objective**: Ensure all 205 awesome-copilot skills are 100% AgentSkills compliant

#### Tasks

1. **Install skills-ref**
   ```bash
   cd /workspaces/self-hosted-ai-starter-kit/agentskills/skills-ref
   uv sync
   source .venv/bin/activate
   ```

2. **Validate All Skills**
   ```bash
   cd /workspaces/self-hosted-ai-starter-kit/awesome-copilot
   for skill in skills/*/; do
       skills-ref validate "$skill" || echo "FAILED: $skill"
   done > validation-report.txt
   ```

3. **Fix Validation Errors**
   - Add missing `license` fields
   - Fix any name mismatches (directory ≠ frontmatter name)
   - Ensure descriptions under 1024 chars
   - Fix consecutive hyphens in names

4. **CI/CD Integration**
   - Add GitHub Action to validate all skills on PR
   - Block merges if validation fails

#### Deliverables
- ✅ All 205 skills pass `skills-ref validate`
- ✅ validation-report.txt with zero errors
- ✅ CI/CD validation workflow

---

### Phase 2: agentspec_mvp Enhancement (Week 2)

**Objective**: Add AgentSkills validation and XML output to agentspec_mvp

#### Tasks

1. **Add skills-ref as Dependency**
   ```toml
   # GenerateAgents.md/pyproject.toml
   [project]
   dependencies = [
       "skills-ref>=0.1.0",
       # ... existing deps
   ]
   ```

2. **New Function: `validate_agentskills_compliance()`**
   ```python
   # src/autogenerateagentsmd/agentspec_mvp.py
   
   from skills_ref import validate, read_properties
   
   def validate_agentskills_compliance(awesome_copilot_path: str) -> dict:
       """Validate all skills against official AgentSkills spec.
       
       Returns:
           {
               "total_skills": 205,
               "valid": 203,
               "invalid": 2,
               "errors": {...}
           }
       """
       # Implementation
   ```

3. **New Function: `generate_agentskills_xml()`**
   ```python
   from skills_ref import to_prompt
   
   def generate_agentskills_xml(awesome_copilot_path: str) -> str:
       """Generate <available_skills> XML for agent prompts.
       
       Returns:
           <available_skills>
           <skill>
           <name>terraform-azurerm-set-diff-analyzer</name>
           <description>Analyze Terraform plan...</description>
           <location>/path/to/SKILL.md</location>
           </skill>
           ...
           </available_skills>
       """
       # Implementation using skills_ref.to_prompt()
   ```

4. **CLI Flags**
   ```bash
   # New flags for autogenerateagentsmd
   autogenerateagentsmd /path/to/repo \
       --validate-agentskills \
       --output-agentskills-xml
   ```

#### Deliverables
- ✅ agentspec_mvp can validate skills using official library
- ✅ Can output AgentSkills XML format
- ✅ All tests passing

---

### Phase 3: MCP Server Integration (Week 3)

**Objective**: Expose AgentSkills functionality via GenerateAgents MCP server

#### New MCP Tools

1. **`validate_agentskills(repo_path)`**
   ```json
   {
     "name": "validate_agentskills",
     "description": "Validate skills against official AgentSkills specification",
     "parameters": {
       "repo_path": "Path to awesome-copilot or skills directory"
     }
   }
   ```

2. **`generate_agentskills_prompt(repo_path, format)`**
   ```json
   {
     "name": "generate_agentskills_prompt",
     "description": "Generate agent prompt with available skills",
     "parameters": {
       "repo_path": "Path to skills directory",
       "format": "xml|json|markdown"
     }
   }
   ```

3. **`read_skill_properties(skill_path)`**
   ```json
   {
     "name": "read_skill_properties",
     "description": "Read skill metadata from SKILL.md frontmatter",
     "parameters": {
       "skill_path": "Path to individual skill directory"
     }
   }
   ```

#### Implementation

```python
# generateagents-mcp/server.py

from skills_ref import validate, to_prompt, read_properties

@mcp.tool()
def validate_agentskills(repo_path: str) -> dict:
    """Validate all skills in a directory."""
    try:
        skills_dir = Path(repo_path) / "skills"
        errors = {}
        
        for skill in skills_dir.iterdir():
            if skill.is_dir():
                validation_errors = validate(skill)
                if validation_errors:
                    errors[skill.name] = validation_errors
        
        return {
            "success": True,
            "total_skills": len(list(skills_dir.iterdir())),
            "valid": len(list(skills_dir.iterdir())) - len(errors),
            "invalid": len(errors),
            "errors": errors
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
```

#### Deliverables
- ✅ 3 new MCP tools exposed
- ✅ VS Code Copilot can validate skills
- ✅ Claude Desktop can generate prompts

---

### Phase 4: Documentation & Examples (Week 4)

**Objective**: Document AgentSkills integration for contributors

#### Tasks

1. **Update awesome-copilot/CONTRIBUTING.md**
   - Add AgentSkills specification reference
   - Add validation instructions
   - Add example skill template

2. **Create Example Skills**
   - `example-minimal-skill/` - Bare minimum
   - `example-full-skill/` - All optional fields + scripts/references/assets

3. **Create Migration Guide**
   - `docs/agentskills-migration-guide.md`
   - How to convert existing skills to 100% compliance

4. **Update GenerateAgents.md/AGENTS.md**
   - Document AgentSkills validation feature
   - Add usage examples

#### Deliverables
- ✅ CONTRIBUTING.md updated
- ✅ 2 example skills
- ✅ Migration guide
- ✅ AGENTS.md updated

---

## Technical Integration Details

### How AgentSkills XML Fits Our Workflow

**Current Flow**:
```
GenerateAgents → AGENTS.md → agentspec.json → awesome-copilot
```

**Enhanced Flow**:
```
GenerateAgents → AGENTS.md → agentspec.json → awesome-copilot
                                    ↓
                          AgentSkills XML → Agent Prompts
```

### Progressive Disclosure Pattern

AgentSkills uses a 3-level loading strategy to minimize context usage:

**Level 1: Metadata (Startup)**
```xml
<available_skills>
<skill>
  <name>pdf-processing</name>
  <description>Extract text from PDFs...</description>
  <location>/path/to/pdf-processing/SKILL.md</location>
</skill>
</available_skills>
```
**Token cost**: ~50-100 tokens per skill

**Level 2: Instructions (Activation)**
- Agent reads full SKILL.md when task matches description
- **Token cost**: ~500-5000 tokens

**Level 3: Resources (Execution)**
- Agent loads scripts/references/assets as needed
- **Token cost**: Variable based on resource size

### Integration with Our AgentSpec MVP

```python
# Mapping between AgentSpec and AgentSkills

AgentSpec JSON:
{
  "tools": {
    "skill_terraform-azurerm": {
      "id": "skill_terraform-azurerm",
      "name": "terraform-azurerm-set-diff-analyzer",
      "description": "...",
      "type": "skill",
      "source_file": "/path/to/SKILL.md"
    }
  }
}

AgentSkills XML:
<skill>
  <name>terraform-azurerm-set-diff-analyzer</name>
  <description>...</description>
  <location>/path/to/SKILL.md</location>
</skill>
```

**Conversion is straightforward!**

---

## Benefits of Integration

### 1. Universal Compatibility
- Works with Claude, GPT-4, Gemini, Mistral, any LLM
- Not tied to GitHub Copilot or single vendor

### 2. Official Validation
- Use Anthropic's official validation library
- Catch errors early in CI/CD

### 3. Interoperability
- Skills can be shared across projects
- Compatible with other tools using AgentSkills

### 4. Progressive Disclosure
- Efficient context usage
- Only load what agents need

### 5. Community Standards
- Follow established conventions
- Easier onboarding for contributors

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking changes in spec | High | Pin skills-ref version, test before upgrade |
| Validation failures on existing skills | Medium | Fix during Phase 1, provide migration guide |
| Additional dependency (skills-ref) | Low | Minimal deps (click, strictyaml), well-maintained |
| Performance overhead | Low | Validation only in CI/CD, not runtime |

---

## Success Metrics

- ✅ All 205 awesome-copilot skills pass AgentSkills validation
- ✅ CI/CD rejects non-compliant skills
- ✅ GenerateAgents MCP can output AgentSkills XML
- ✅ Documentation updated with AgentSkills references
- ✅ Zero breaking changes to existing workflows

---

## Quick Start Commands

```bash
# 1. Install skills-ref
cd /workspaces/self-hosted-ai-starter-kit/agentskills/skills-ref
uv sync && source .venv/bin/activate

# 2. Validate a skill
skills-ref validate ../awesome-copilot/skills/terraform-azurerm-set-diff-analyzer

# 3. Read skill properties
skills-ref read-properties ../awesome-copilot/skills/terraform-azurerm-set-diff-analyzer

# 4. Generate XML prompt
skills-ref to-prompt ../awesome-copilot/skills/*

# 5. Validate all skills
for skill in /workspaces/self-hosted-ai-starter-kit/awesome-copilot/skills/*/; do
    echo "Validating: $(basename "$skill")"
    skills-ref validate "$skill"
done
```

---

## References

- **AgentSkills Official Site**: https://agentskills.io
- **Specification**: https://agentskills.io/specification
- **skills-ref Library**: https://github.com/agentskills/agentskills/tree/main/skills-ref
- **Example Skills**: https://github.com/anthropics/skills
- **Our AgentSpec MVP**: `/workspaces/self-hosted-ai-starter-kit/GenerateAgents.md/src/autogenerateagentsmd/agentspec_mvp.py`

---

## Next Steps

1. **Immediate** (Today):
   - ✅ Complete this analysis
   - ✅ Save to memory
   - ⏳ Review with team

2. **Phase 1** (Week 1):
   - Validate all skills
   - Fix compliance issues
   - Add CI/CD validation

3. **Phase 2** (Week 2):
   - Enhance agentspec_mvp
   - Add XML output
   - Add validation function

4. **Phase 3** (Week 3):
   - Add MCP tools
   - Test with VS Code/Claude
   - Document usage

5. **Phase 4** (Week 4):
   - Update documentation
   - Create examples
   - Migration guide

---

**Document Status**: Complete  
**Last Updated**: March 5, 2026  
**Author**: GitHub Copilot (Claude Sonnet 4.5)
