---
name: example-minimal-skill
description: A minimal AgentSkill example showing only required fields. Use this template for simple, instruction-only skills without scripts or additional resources.
license: Apache-2.0
---

# Example Minimal Skill

This is a minimal AgentSkill that demonstrates the simplest valid skill structure.

## When to Use This Skill

Use this skill template when you need to create a simple skill that:
- Provides instructions or guidance only
- Doesn't require scripts or additional files
- Has straightforward, self-contained instructions

## Structure

A minimal AgentSkill requires:
1. **SKILL.md file** (this file) with YAML frontmatter
2. **Required frontmatter fields**:
   - `name`: 1-64 chars, lowercase with hyphens, matches directory name
   - `description`: 1-1024 chars, describes what AND when to use the skill

## Instructions

When the agent activates this skill, it will receive these instructions.

### Step 1: Read the Context
Understand what the user wants to accomplish.

### Step 2: Execute the Task
Provide clear, actionable guidance based on the skill's purpose.

### Step 3: Verify Results
Confirm the task completed successfully.

## Best Practices

- Keep instructions concise and actionable
- Use clear section headers
- Provide examples when helpful
- State any prerequisites upfront

## Example Usage

```bash
# Example command or usage pattern
echo "Replace this with your actual skill usage"
```

## Notes

- This is a template - adapt it to your specific use case
- Keep the description field under 1024 characters
- Ensure the `name` field matches the directory name exactly
