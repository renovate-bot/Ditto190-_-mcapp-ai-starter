---
name: example-full-skill
description: A comprehensive AgentSkill example demonstrating all available fields, including scripts, references, and metadata. Use this as a reference for complex skills requiring multiple resources.
license: Apache-2.0
compatibility: Works best with models that support tool calling (Claude 3+, GPT-4+, Gemini 1.5+). Requires bash/zsh shell for script execution.
allowed-tools:
  - read_file
  - write_file
  - run_command
metadata:
  version: '1.0.0'
  author: 'n8n Community'
  category: 'example'
  tags:
    - template
    - reference
    - comprehensive
  requires_python: '>=3.11'
  requires_node: '>=18.0.0'
---

# Example Full Skill

This comprehensive AgentSkill demonstrates all available features and optional fields in the AgentSkills specification.

## When to Use This Skill

Use this skill template when creating complex skills that need:
- Multiple executable scripts with dependencies
- Reference documentation or data files  
- Specific compatibility requirements
- Detailed metadata and versioning
- Integration with multiple tools

## Prerequisites

Before using this skill, ensure:
- Python 3.11+ is installed (check: `python3 --version`)
- Node.js 18+ is installed (check: `node --version`)
- Bash or zsh shell is available
- Agent has permission to execute scripts

You can specify runtime requirements in the `compatibility` frontmatter field.

## Structure

This skill includes:
- **SKILL.md** - Main instruction file (this file)
- **scripts/** - Executable scripts with inline dependencies
- **references/** - Support documentation and data files
- **assets/** - Binary files, images, or other resources (optional)

## Available Scripts

All scripts use **relative paths from the skill root**. The agent automatically resolves these when executing.

### `scripts/validate.py`
Validates input data against expected schema.

**Usage:**
```bash
uv run scripts/validate.py --input data.json --schema references/schema.json
```

**Dependencies:** Declared inline using PEP 723 format (auto-installed by `uv run`)

### `scripts/process.sh`
Processes validated data and generates output.

**Usage:**
```bash
bash scripts/process.sh input.json output.json
```

**Exit codes:**
- `0`: Success
- `1`: Invalid arguments
- `2`: Processing error
- `3`: Output write failure

### `scripts/extract.ts`
Extracts specific fields from structured data (Deno runtime).

**Usage:**
```bash
deno run --allow-read scripts/extract.ts --file data.json --fields name,email,status
```

**Dependencies:** Declared inline using npm: imports (auto-installed by Deno)

## Available References

Reference files provide support documentation and example data.

### `references/schema.json`
JSON schema defining expected input format. Used by `scripts/validate.py`.

### `references/examples.md`
Detailed usage examples with various input scenarios and expected outputs.

### `references/troubleshooting.md`
Common errors and solutions for this skill.

## Workflow

A typical workflow using this skill:

### 1. Validate Input
First, ensure the input data matches the expected schema:

```bash
uv run scripts/validate.py \
  --input "$INPUT_FILE" \
  --schema references/schema.json
```

If validation fails, check `references/troubleshooting.md` for common issues.

### 2. Process Data
Once validated, process the data:

```bash
bash scripts/process.sh "$INPUT_FILE" "$OUTPUT_FILE"
```

Monitor stderr for progress messages. Structured data goes to stdout.

### 3. Extract Results (Optional)
If you need specific fields from the output:

```bash
deno run --allow-read scripts/extract.ts \
  --file "$OUTPUT_FILE" \
  --fields name,status,result
```

### 4. Verify Output
Check the exit code and output file:

```bash
if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
  echo "Processing completed successfully"
  cat "$OUTPUT_FILE"
else
  echo "Processing failed - check error messages"
fi
```

## Script Design Principles

All scripts in this skill follow AgentSkills best practices:

### ✅ Non-Interactive
- Accept all input via CLI flags, environment variables, or stdin
- Never prompt for user input (agents run in non-interactive shells)
- Provide clear error messages with guidance when inputs are missing

### ✅ Self-Contained
- Declare dependencies inline (PEP 723, npm:, jsr: imports)
- No separate package.json, requirements.txt, or Gemfile needed
- Package managers (uv, deno, bun) auto-install dependencies

### ✅ Clear Interface
- Implement `--help` flag with usage examples
- Document all flags, options, and exit codes
- Use enums and closed sets for arguments

### ✅ Structured Output
- Send structured data (JSON, CSV) to stdout
- Send diagnostics, progress, and errors to stderr
- Enable composition with standard tools (jq, awk, cut)

### ✅ Error Handling
- Use meaningful exit codes for different failure types
- Provide actionable error messages (what failed, what was expected, how to fix)
- Support `--dry-run` for destructive operations

### ✅ Idempotent Operations
- Safe to retry (agents may retry on failure)
- Use "create if not exists" patterns
- Avoid state that breaks on re-execution

### ✅ Bounded Output
- Default to summaries for large datasets
- Support pagination flags (--offset, --limit)
- Require explicit --output flag for unbounded data

## Input Constraints

This skill expects input data in the following format:

```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "email": "string (validated format)",
      "status": "active | inactive | pending"
    }
  ],
  "options": {
    "format": "json | csv | table",
    "validate": true
  }
}
```

See `references/schema.json` for the complete JSON schema.

## Error Handling

Common errors and solutions:

### Invalid Email Format
**Error:** `Invalid email address: missing '@' symbol`  
**Solution:** Ensure all email fields contain valid email addresses (user@domain.com)

### Schema Validation Failed
**Error:** `Schema validation failed: required field 'status' missing`  
**Solution:** Add the missing `status` field to all items (valid values: active, inactive, pending)

### Permission Denied
**Error:** `Permission denied: cannot execute script`  
**Solution:** Make scripts executable: `chmod +x scripts/*.py scripts/*.sh`

### Missing Dependencies
**Error:** `uv: command not found`  
**Solution:** Install uv package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`

For more troubleshooting, see `references/troubleshooting.md`.

## Output Format

Successful execution produces:

```json
{
  "processed": 42,
  "succeeded": 40,
  "failed": 2,
  "results": [
    {
      "id": "item-1",
      "status": "success",
      "output": { "key": "value" }
    }
  ],
  "errors": [
    {
      "id": "item-2",
      "error": "Validation failed: invalid email"
    }
  ]
}
```

## Advanced Features

### Dry Run Mode
Test operations without making changes:

```bash
bash scripts/process.sh --dry-run input.json
```

### Verbose Output
Enable detailed logging to stderr:

```bash
uv run scripts/validate.py --input data.json --verbose
```

### Custom Output Format
Choose output format (default: json):

```bash
bash scripts/process.sh input.json output.csv --format csv
```

## Metadata

This skill includes optional metadata fields:

- **version**: Semantic version for tracking changes
- **author**: Skill creator or maintainer
- **category**: Skill classification for organization
- **tags**: Searchable keywords for discovery
- **requires_python**: Minimum Python version
- **requires_node**: Minimum Node.js version

You can add any custom metadata fields your system needs.

## Compatibility Notes

This skill is designed for:
- **Models:** Claude 3+, GPT-4+, Gemini 1.5+ (tool calling support recommended)
- **Shells:** bash, zsh (POSIX-compatible)
- **Python:** 3.11+ with uv package manager
- **Node.js:** 18+ (for Deno runtime)

The `compatibility` frontmatter field provides this information to agents at skill discovery time.

## Integration Examples

### Using with Claude Desktop
```xml
<available_skills>
  <skill>
    <name>example-full-skill</name>
    <description>A comprehensive AgentSkill example...</description>
    <location>/path/to/skills/example-full-skill/SKILL.md</location>
  </skill>
</available_skills>
```

### Using with MCP Server
```python
from skills_ref import validate, read_properties, to_prompt

# Validate skill
errors = validate(Path("./example-full-skill"))
if errors:
    print("Validation errors:", errors)

# Read metadata
props = read_properties(Path("./example-full-skill"))
print(f"Skill: {props.name} - {props.description}")

# Generate prompt XML
xml = to_prompt([Path("./example-full-skill")])
print(xml)
```

## Notes

- This is a comprehensive template - most skills won't need all features
- Choose features based on your specific requirements
- Simpler skills should use the **example-minimal-skill** template
- Keep scripts focused on single responsibilities
- Test scripts independently before bundling in the skill

## Next Steps

1. Copy this template to create your own skill
2. Update the frontmatter with your skill's details
3. Modify instructions for your use case
4. Add scripts to `scripts/` directory (if needed)
5. Add references to `references/` directory (if needed)
6. Validate with `skills-ref validate ./your-skill/`
7. Test scripts independently
8. Test the complete skill with an agent
