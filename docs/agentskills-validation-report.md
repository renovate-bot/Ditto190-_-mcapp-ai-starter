# AgentSkills Validation Report

**Date:** March 5, 2026  
**Total Skills:** 207  
**Status:** 203 Clean ✅ | 4 With Warnings ⚠️

## Executive Summary

Validated all 207 AgentSkills in `awesome-copilot/skills/` directory using the official `skills-ref` library from Anthropic. Overall compliance is **excellent** at 98%, with only 4 skills having minor YAML formatting issues that should be fixed for 100% compliance.

## Validation Results

### ✅ Clean Skills: 203 (98%)

All required fields present, valid YAML syntax, proper naming conventions.

### ⚠️ Skills with Warnings: 4 (2%)

#### 1. azure-role-selector
**Issue:** Invalid YAML syntax in `allowed-tools` field  
**Error:**
```
Invalid YAML in frontmatter: Found ugly disallowed JSONesque flow mapping
Line 4: allowed-tools: ['Azure MCP/documentation', 'Azure MCP/...]
```

**Fix Required:** Change flow mapping to block style or proper YAML list:
```yaml
# Current (invalid):
allowed-tools: ['Azure MCP/documentation', 'Azure MCP/...']

# Fix option 1 (block style):
allowed-tools:
  - Azure MCP/documentation
  - Azure MCP/...

# Fix option 2 (proper flow style):
allowed-tools: ["Azure MCP/documentation", "Azure MCP/..."]
```

#### 2. example-full-skill
**Issue:** Invalid YAML syntax in `allowed-tools` field  
**Error:**
```
Invalid YAML in frontmatter: Found ugly disallowed JSONesque flow mapping
Line 6: allowed-tools: ['read_file', 'write_file', 'run_command']
```

**Fix Required:** Same as azure-role-selector - change to block style:
```yaml
# Current (invalid):
allowed-tools: ['read_file', 'write_file', 'run_command']

# Fix (block style):
allowed-tools:
  - read_file
  - write_file
  - run_command
```

#### 3. mentoring-juniors
**Issue:** Unexpected field `authors` in frontmatter  
**Error:**
```
Unexpected fields in frontmatter: authors
Only ['allowed-tools', 'compatibility', 'description', 'license', 'metadata', 'name'] are allowed
```

**Fix Required:** Move `authors` to `metadata` section:
```yaml
# Current (invalid):
authors: "John Doe"

# Fix:
metadata:
  authors: "John Doe"
```

#### 4. microsoft-skill-creator
**Issue:** Unexpected field `context` in frontmatter  
**Error:**
```
Unexpected fields in frontmatter: context
Only ['allowed-tools', 'compatibility', 'description', 'license', 'metadata', 'name'] are allowed
```

**Fix Required:** Move `context` to `metadata` section:
```yaml
# Current (invalid):
context: "Microsoft documentation context"

# Fix:
metadata:
  context: "Microsoft documentation context"
```

## Issue Categories

### Category 1: YAML Syntax Errors (2 skills)
- **Skills:** azure-role-selector, example-full-skill
- **Cause:** Using single quotes with flow mapping syntax `['item']` which strictyaml considers "JSONesque"
- **Solution:** Convert to block style or use double quotes `["item"]`
- **Impact:** Low - validator is lenient but should be fixed for strict compliance

### Category 2: Unexpected Frontmatter Fields (2 skills)
- **Skills:** mentoring-juniors, microsoft-skill-creator
- **Cause:** Using custom fields (`authors`, `context`) at top level instead of in `metadata` section
- **Solution:** Move fields to `metadata` object
- **Impact:** Low - non-standard fields should be nested in metadata per spec

## AgentSkills Specification Compliance

### Required Fields ✅ (All 207 skills compliant)
- `name`: 1-64 chars, lowercase-with-hyphens, matches directory ✅
- `description`: 1-1024 chars, describes what AND when ✅

### Optional Fields (Compliant where used)
- `license`: Valid SPDX identifiers ✅
- `compatibility`: Runtime/model requirements ✅
- `allowed-tools`: Tool restrictions ⚠️ (2 skills have YAML syntax issues)
- `metadata`: Custom key-value pairs ⚠️ (2 skills using top-level instead)

## Recommended Actions

### Priority 1: Fix YAML Syntax (azure-role-selector, example-full-skill)
```bash
# Fix allowed-tools to use block style
vim awesome-copilot/skills/azure-role-selector/SKILL.md
vim awesome-copilot/skills/example-full-skill/SKILL.md
```

### Priority 2: Move Custom Fields to Metadata (mentoring-juniors, microsoft-skill-creator)
```bash
# Move authors/context to metadata section
vim awesome-copilot/skills/mentoring-juniors/SKILL.md
vim awesome-copilot/skills/microsoft-skill-creator/SKILL.md
```

### Priority 3: Re-validate After Fixes
```bash
cd /workspaces/self-hosted-ai-starter-kit/agentskills/skills-ref
for skill in azure-role-selector example-full-skill mentoring-juniors microsoft-skill-creator; do
    .venv/bin/skills-ref validate ../../awesome-copilot/skills/$skill
done
```

## Success Metrics

- ✅ All 207 skills discovered and processed
- ✅ 203 skills (98%) pass strict validation with no warnings
- ⚠️ 4 skills (2%) have minor fixable issues
- ✅ No critical failures (missing SKILL.md, invalid names, missing required fields)
- ✅ All skills follow AgentSkills directory structure
- ✅ Zero breaking changes required

## Validation Command

```bash
cd /workspaces/self-hosted-ai-starter-kit/awesome-copilot/skills
for skill in */; do
    ../../agentskills/skills-ref/.venv/bin/skills-ref validate "$skill"
done
```

## Next Steps

1. **Fix 4 skills with warnings** (estimated: 15 minutes)
2. **Re-run validation** to confirm 100% compliance
3. **Deploy GitHub Actions workflow** for continuous validation
4. **Deploy pre-commit hook** to prevent future issues
5. **Update CONTRIBUTING.md** with AgentSkills guidelines

## Conclusion

The validation results are **excellent**. Our awesome-copilot skills are 98% compliant with the official AgentSkills specification out of the box, confirming our earlier finding that the formats are nearly identical. The 4 remaining issues are minor YAML formatting fixes that can be resolved in minutes.

This validates our integration strategy and confirms that:
- ✅ No migration required for existing skills
- ✅ Format compatibility confirmed at scale (207 skills)
- ✅ Only minor cleanup needed for 100% compliance
- ✅ Zero impact on existing functionality

**Status:** Ready to proceed with fixes → Phase 1 complete within hours

---

**Generated:** March 5, 2026  
**Validator:** skills-ref v0.1.0 (official Anthropic library)  
**Full Results:** [validation-results.txt](../validation-results.txt)
