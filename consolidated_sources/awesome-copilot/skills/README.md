# AgentSkills Example Templates

This directory contains two complete AgentSkills templates that demonstrate the official format maintained by Anthropic.

## Templates

### 1. Minimal Skill (`example-minimal-skill/`)

**Use when:** Creating simple skills with instructions only.

**Structure:**

- Single `SKILL.md` file with required frontmatter
- No scripts or additional resources

**Best for:**

- Guidance and best practices
- Procedural instructions
- Reference documentation
- Simple task workflows

**Compliance:** ✅ 100% AgentSkills compliant

---

### 2. Full Skill (`example-full-skill/`)

**Use when:** Creating complex skills with scripts, validation, and resources.

**Structure:**

```
example-full-skill/
├── SKILL.md                    # Main instructions
├── scripts/                    # Executable scripts
│   ├── validate.py            # Python (PEP 723 inline deps)
│   ├── process.sh             # Bash processing
│   └── extract.ts             # Deno extraction
└── references/                 # Support documentation
    ├── schema.json            # JSON schema
    ├── examples.md            # Usage examples
    └── troubleshooting.md     # Common errors
```

**Best for:**

- Data validation and processing
- Multi-step workflows with shell commands
- Skills requiring external tools
- Complex integrations with multiple runtimes

**Scripts demonstrate:**

- ✅ Non-interactive execution (all input via CLI)
- ✅ Self-contained dependencies (auto-installed)
- ✅ Clear `--help` documentation
- ✅ Structured output (JSON/CSV to stdout)
- ✅ Meaningful exit codes (0/1/2/3)
- ✅ Idempotent operations (safe to retry)

**Compliance:** ✅ 100% AgentSkills compliant with all optional fields

---

## Quick Start

### Validate Templates

```bash
# Navigate to skills-ref directory
cd /workspaces/self-hosted-ai-starter-kit/agentskills/skills-ref
source .venv/bin/activate

# Validate minimal template
skills-ref validate ../awesome-copilot/skills/example-minimal-skill

# Validate full template
skills-ref validate ../awesome-copilot/skills/example-full-skill
```

### Test Full Template Scripts

```bash
cd /workspaces/self-hosted-ai-starter-kit/awesome-copilot/skills/example-full-skill

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

# Run validation
uv run scripts/validate.py \
  --input test-input.json \
  --schema references/schema.json \
  --verbose

# Process data
bash scripts/process.sh test-input.json test-output.json --verbose

# Extract specific fields
deno run --allow-read scripts/extract.ts \
  --file test-output.json \
  --fields id,email \
  --pretty
```

## Creating Your Own Skills

### 1. Choose a Template

- **Simple skill?** → Copy `example-minimal-skill/`
- **Complex skill?** → Copy `example-full-skill/`

### 2. Customize the Skill

```bash
# Copy template
cp -r example-minimal-skill/ my-new-skill/

# Edit SKILL.md
# Update frontmatter:
#   - name: my-new-skill (must match directory)
#   - description: What it does and when to use it
#   - license: Apache-2.0, MIT, etc.

# Add your instructions in the main body
```

### 3. Validate Your Skill

```bash
# From skills-ref directory
skills-ref validate /path/to/my-new-skill

# Fix any errors reported
# Common issues:
#   - Name doesn't match directory
#   - Description too long (max 1024 chars)
#   - Consecutive hyphens in name
#   - Missing required fields
```

### 4. Test with an Agent

```bash
# Generate agent prompt to see how it appears
skills-ref to-prompt /path/to/my-new-skill

# Output format (XML for Claude):
# <available_skills>
#   <skill>
#     <name>my-new-skill</name>
#     <description>...</description>
#     <location>/path/to/my-new-skill/SKILL.md</location>
#   </skill>
# </available_skills>
```

## Script Guidelines (Full Template)

If adding scripts to your skill:

### ✅ DO:

- Accept all input via CLI flags (`--input`, `--output`, etc.)
- Provide `--help` with usage examples
- Output structured data (JSON, CSV) to stdout
- Send progress/diagnostics to stderr
- Use meaningful exit codes (0=success, 1=args, 2=file, 3=validation)
- Declare dependencies inline (PEP 723, npm:, jsr:)
- Make operations idempotent (safe to retry)
- Support `--dry-run` for destructive operations

### ❌ DON'T:

- Prompt for user input (agents run non-interactively)
- Require separate package managers or manifests
- Output unbounded data without pagination
- Use non-standard exit codes
- Assume specific shell environments

## Frontmatter Fields Reference

### Required Fields

```yaml
name: skill-name # 1-64 chars, lowercase-with-hyphens
description: What it does... # 1-1024 chars, describe what AND when
```

### Optional Fields

```yaml
license: Apache-2.0 # SPDX identifier

compatibility: | # Runtime/model requirements
  Requires Python 3.11+
  Works best with Claude 3+

allowed-tools: # Tool restrictions
  - read_file
  - write_file
  - run_command

metadata: # Custom key-value pairs
  version: "1.0.0"
  author: "Your Name"
  category: "data-processing"
  tags:
    - validation
    - json
  requires_python: ">=3.11"
```

## Progressive Disclosure Pattern

AgentSkills use a 3-level loading strategy:

**Level 1: Metadata (Startup)**

- Load only `name` and `description` from frontmatter
- Low token cost: ~50-100 tokens per skill
- Enables fast skill discovery

**Level 2: Instructions (Activation)**

- Load full SKILL.md when task matches
- Medium token cost: ~500-5000 tokens
- Provides complete guidance

**Level 3: Resources (Execution)**

- Load scripts/references/assets on demand
- Variable token cost depending on resource size
- Only accessed when explicitly needed

## Validation Rules

Your skill must pass these checks:

- ✅ `SKILL.md` file exists (case-insensitive)
- ✅ Valid YAML frontmatter with `---` delimiters
- ✅ Required fields present: `name`, `description`
- ✅ Name is lowercase with hyphens, no consecutive hyphens
- ✅ Name matches directory name exactly
- ✅ Description is 1-1024 characters
- ✅ License is valid SPDX identifier (if present)
- ✅ Compatibility is <500 characters (if present)

## Resources

- **AgentSkills Website:** https://agentskills.io
- **Specification:** https://agentskills.io/specification
- **Integration Guide:** https://agentskills.io/integrate-skills
- **skills-ref Library:** https://github.com/agentskills/agentskills/tree/main/skills-ref
- **Project Implementation Guide:** [/docs/agentskills-implementation-guide.md](../../docs/agentskills-implementation-guide.md)

## Troubleshooting

### Validation Errors

See [example-full-skill/references/troubleshooting.md](example-full-skill/references/troubleshooting.md) for common issues and solutions.

### Getting Help

1. Check validation error messages (they're descriptive)
2. Review the specification: https://agentskills.io/specification
3. Compare your skill to the example templates
4. Use `skills-ref validate --help` for CLI options

## Contributing

When contributing new skills to awesome-copilot:

1. Copy an appropriate template
2. Customize for your use case
3. Validate with `skills-ref validate`
4. Test scripts independently
5. Submit PR with skill in `awesome-copilot/skills/your-skill/`

CI/CD will automatically validate your skill on PR.

---

**Last Updated:** March 5, 2026  
**AgentSkills Version:** 1.0 (official specification)  
**Templates Status:** ✅ Validated and Ready
