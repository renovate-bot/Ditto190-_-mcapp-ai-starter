# Troubleshooting Guide

Common errors and solutions for `example-full-skill`.

## Installation Issues

### Error: `uv: command not found`

**Cause:** Python's uv package manager is not installed.

**Solution:**

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Error: `deno: command not found`

**Cause:** Deno runtime is not installed.

**Solution:**

```bash
# Linux/macOS
curl -fsSL https://deno.land/install.sh | sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.deno/bin:$PATH"

# Verify installation
deno --version
```

### Error: `jq: command not found`

**Cause:** jq JSON processor is not installed (required by process.sh).

**Solution:**

```bash
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq

# Verify installation
jq --version
```

## Validation Errors

### Error: `Invalid email address: missing '@' symbol`

**Cause:** Email field doesn't contain '@' character.

**Example:**

```json
{
  "email": "alice.example.com" // Missing @
}
```

**Solution:** Fix email format:

```json
{
  "email": "alice@example.com"
}
```

### Error: `Invalid status value: unknown (must be: active, inactive, pending)`

**Cause:** Status field contains value not in allowed enum.

**Example:**

```json
{
  "status": "disabled" // Not in enum
}
```

**Solution:** Use one of the allowed values:

```json
{
  "status": "inactive" // Valid: active, inactive, or pending
}
```

### Error: `missing required field 'id'`

**Cause:** Item is missing a required field.

**Example:**

```json
{
  "items": [
    {
      "name": "Alice",
      "email": "alice@example.com"
      // Missing 'id' and 'status'
    }
  ]
}
```

**Solution:** Add all required fields:

```json
{
  "items": [
    {
      "id": "user-1",
      "name": "Alice",
      "email": "alice@example.com",
      "status": "active"
    }
  ]
}
```

## Processing Errors

### Error: `No items found in input file`

**Cause:** Input JSON doesn't have an 'items' array, or it's empty.

**Example:**

```json
{
  "data": [] // Wrong field name
}
```

**Solution:** Use correct structure:

```json
{
  "items": [
    {
      /* item data */
    }
  ]
}
```

### Error: `Invalid JSON in file: input.json`

**Cause:** JSON syntax error (missing comma, bracket, quote, etc.).

**Example:**

```json
{
  "items": [
    {
      "id": "user-1"
      "name": "Alice"  // Missing comma
    }
  ]
}
```

**Solution:** Validate JSON syntax:

```bash
# Use jq to validate
jq empty input.json

# Or use online validator: https://jsonlint.com/
```

### Error: `Permission denied: cannot execute script`

**Cause:** Script files don't have execute permissions.

**Solution:**

```bash
# Make scripts executable
chmod +x scripts/*.py scripts/*.sh scripts/*.ts

# Or run with explicit interpreter
# For Python:
python3 scripts/validate.py --help

# For bash:
bash scripts/process.sh --help

# For Deno:
deno run --allow-read scripts/extract.ts --help
```

## Runtime Errors

### Error: `Failed to write output file`

**Cause:** No write permission or disk full.

**Check disk space:**

```bash
df -h .
```

**Check permissions:**

```bash
ls -la
```

**Solution:**

```bash
# Try writing to a different directory
bash scripts/process.sh input.json /tmp/output.json

# Or fix permissions
chmod +w .
```

### Error: Python dependency installation fails

**Symptom:**

```
Error: Failed to install pydantic>=2.0.0
```

**Solution:**

```bash
# Clear uv cache
uv cache clean

# Try again
uv run scripts/validate.py --help

# If still fails, install dependencies manually
uv pip install pydantic strictyaml
```

### Error: Deno permission denied

**Symptom:**

```
error: Requires read access to "input.json", run again with the --allow-read flag
```

**Solution:** Add required permissions to deno run command:

```bash
# For reading files
deno run --allow-read scripts/extract.ts --file input.json --fields id,name

# For reading and writing
deno run --allow-read --allow-write scripts/extract.ts \
  --file input.json \
  --fields id,name \
  --output result.json
```

## Data Issues

### Warning: `Field 'optional_field' not found in item 0`

**Cause:** Extraction script looking for field that doesn't exist in data.

**This is a warning, not an error.** The field will be set to `null` in output.

**If you want to avoid this warning:**

1. Check available fields first:

```bash
jq '.items[0] | keys' input.json
```

2. Extract only existing fields:

```bash
deno run --allow-read scripts/extract.ts \
  --file input.json \
  --fields id,name,email  # Only existing fields
```

### Large file processing

**Symptom:** Processing very large files (>100MB) is slow or fails.

**Solution:** Process in batches:

```bash
# Split large file into chunks
jq -c '.items[] | {items: [.]}' large-input.json | split -l 1000 - chunk-

# Process each chunk
for chunk in chunk-*; do
  bash scripts/process.sh "$chunk" "output-$chunk.json"
done

# Merge results
jq -s '{processed: (map(.processed) | add), results: (map(.results[]) | .)}' output-chunk-*.json > final-output.json
```

## Integration Issues

### Agent can't find scripts

**Symptom:** Agent tries to run script but gets "file not found".

**Cause:** Agent not running commands from skill root directory.

**Solution:** Ensure agent uses absolute paths or changes to skill directory first:

```bash
cd /path/to/example-full-skill
bash scripts/process.sh input.json output.json
```

Or use absolute paths:

```bash
bash /path/to/example-full-skill/scripts/process.sh \
  /path/to/input.json \
  /path/to/output.json
```

### Scripts work in terminal but fail for agent

**Cause:** Agent runs in non-interactive shell with limited environment.

**Check:**

1. Scripts use shebang: `#!/usr/bin/env python3` or `#!/usr/bin/env bash`
2. Scripts don't prompt for input
3. Required tools are in PATH (python3, jq, deno)

**Solution:** Make scripts fully self-contained and non-interactive.

## Getting Help

If you encounter issues not covered here:

1. **Check exit codes:** Each script returns meaningful exit codes (see references/examples.md)
2. **Enable verbose mode:** Add `--verbose` flag to see detailed progress
3. **Test scripts independently:** Run each script standalone to isolate issues
4. **Validate JSON:** Use `jq empty file.json` to check JSON syntax
5. **Check dependencies:** Verify all required tools are installed and in PATH

## Quick Diagnostic Commands

Run these to gather debugging information:

```bash
# Check tool versions
echo "=== Versions ==="
python3 --version
uv --version 2>/dev/null || echo "uv not installed"
deno --version 2>/dev/null || echo "deno not installed"
jq --version 2>/dev/null || echo "jq not installed"

# Check file structure
echo "=== Skill Structure ==="
ls -la scripts/
ls -la references/

# Validate skill with skills-ref
echo "=== AgentSkills Validation ==="
skills-ref validate .

# Test JSON syntax
echo "=== JSON Validation ==="
jq empty your-input.json && echo "✓ Valid JSON" || echo "✗ Invalid JSON"
```
