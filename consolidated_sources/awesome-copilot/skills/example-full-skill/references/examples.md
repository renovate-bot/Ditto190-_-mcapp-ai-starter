# Example Usage

This document provides detailed usage examples for the `example-full-skill` AgentSkill.

## Basic Workflow

### Example 1: Validate and Process (JSON output)

**Input data** (`input.json`):

```json
{
  "items": [
    {
      "id": "user-1",
      "name": "Alice Smith",
      "email": "alice@example.com",
      "status": "active"
    },
    {
      "id": "user-2",
      "name": "Bob Jones",
      "email": "bob@example.com",
      "status": "inactive"
    }
  ],
  "options": {
    "format": "json",
    "validate": true
  }
}
```

**Step 1: Validate**

```bash
uv run scripts/validate.py \
  --input input.json \
  --schema references/schema.json \
  --verbose
```

**Output** (stderr - progress):

```
Validating 2 items...
  ✓ Item 0: user-1
  ✓ Item 1: user-2

Validation Summary:
  Total items: 2
  Valid: 2
  Invalid: 0
  Overall: ✓ PASS
```

**Output** (stdout - structured):

```json
{
  "valid": true,
  "total_items": 2,
  "valid_items": 2,
  "invalid_items": 0,
  "errors": []
}
```

**Step 2: Process**

```bash
bash scripts/process.sh input.json output.json --verbose
```

**Output** (stdout):

```json
{
  "status": "success",
  "output_file": "output.json",
  "format": "json"
}
```

**Result file** (`output.json`):

```json
{
  "processed": 2,
  "timestamp": "2026-03-05T10:30:00Z",
  "results": [
    {
      "id": "user-1",
      "name": "Alice Smith",
      "email": "alice@example.com",
      "status": "active",
      "processed_at": "2026-03-05T10:30:00Z"
    },
    {
      "id": "user-2",
      "name": "Bob Jones",
      "email": "bob@example.com",
      "status": "inactive",
      "processed_at": "2026-03-05T10:30:00Z"
    }
  ]
}
```

### Example 2: CSV Output

```bash
# Process directly to CSV
bash scripts/process.sh --format csv input.json output.csv

# Extract specific fields
deno run --allow-read scripts/extract.ts \
  --file output.csv \
  --fields id,email,status \
  --pretty
```

**CSV output** (`output.csv`):

```csv
id,name,email,status
"user-1","Alice Smith","alice@example.com","active"
"user-2","Bob Jones","bob@example.com","inactive"
```

### Example 3: Handling Validation Errors

**Invalid input** (`invalid.json`):

```json
{
  "items": [
    {
      "id": "user-1",
      "name": "Alice",
      "email": "not-an-email",
      "status": "active"
    },
    {
      "id": "user-2",
      "name": "Bob",
      "status": "unknown"
    }
  ]
}
```

**Validate**:

```bash
uv run scripts/validate.py \
  --input invalid.json \
  --schema references/schema.json \
  --verbose
```

**Output** (validation report):

```json
{
  "valid": false,
  "total_items": 2,
  "valid_items": 0,
  "invalid_items": 2,
  "errors": [
    {
      "valid": false,
      "item_index": 0,
      "item_id": "user-1",
      "errors": ["invalid email format: not-an-email"]
    },
    {
      "valid": false,
      "item_index": 1,
      "item_id": "user-2",
      "errors": [
        "missing required field 'email'",
        "invalid status value: unknown (must be: active, inactive, pending)"
      ]
    }
  ]
}
```

**Exit code**: 3 (validation failed)

## Advanced Usage

### Dry-Run Mode

Preview processing without writing output:

```bash
bash scripts/process.sh \
  --dry-run \
  --verbose \
  --format csv \
  input.json output.csv
```

### Field Extraction

Extract specific fields from processed results:

```bash
# Extract only ID and status
deno run --allow-read scripts/extract.ts \
  --file output.json \
  --fields id,status \
  --output summary.json \
  --pretty
```

**Output** (`summary.json`):

```json
{
  "total_items": 2,
  "extracted_fields": ["id", "status"],
  "results": [
    {
      "id": "user-1",
      "status": "active"
    },
    {
      "id": "user-2",
      "status": "inactive"
    }
  ]
}
```

### Pipeline Example

Combine all scripts in a pipeline:

```bash
#!/bin/bash

# Validate first
if uv run scripts/validate.py --input input.json --schema references/schema.json; then
  echo "✓ Validation passed"

  # Process to JSON
  bash scripts/process.sh input.json processed.json

  # Extract summary
  deno run --allow-read scripts/extract.ts \
    --file processed.json \
    --fields id,status \
    --output summary.json \
    --pretty

  echo "✓ Pipeline complete"
  cat summary.json
else
  echo "✗ Validation failed - check input data"
  exit 1
fi
```

## Table Format Example

For human-readable output:

```bash
bash scripts/process.sh --format table input.json -
```

**Output**:

```
ID      NAME          EMAIL                  STATUS
---     ---           ---                    ---
user-1  Alice Smith   alice@example.com      active
user-2  Bob Jones     bob@example.com        inactive
```

## Integration with Agent Workflows

### Claude Desktop Example

When this skill is available, the agent can execute:

```xml
<thinking>
User wants to process a list of users. I'll use the example-full-skill to validate and process the data.
</thinking>

<bash>
# Create input file
cat > users.json << 'EOF'
{
  "items": [
    {"id": "1", "name": "Alice", "email": "alice@test.com", "status": "active"}
  ]
}
EOF

# Validate
uv run /path/to/example-full-skill/scripts/validate.py \
  --input users.json \
  --schema /path/to/example-full-skill/references/schema.json

# Process
bash /path/to/example-full-skill/scripts/process.sh users.json output.json
</bash>
```

## Error Handling Examples

All scripts provide meaningful exit codes and error messages:

**Exit code 1** (invalid arguments):

```bash
$ bash scripts/process.sh --format xml input.json output.json
Error: Invalid format 'xml'
       Must be one of: json, csv, table
$ echo $?
1
```

**Exit code 2** (file not found):

```bash
$ uv run scripts/validate.py --input missing.json --schema schema.json
Error: Input file not found: missing.json
$ echo $?
2
```

**Exit code 3** (validation failed):

```bash
$ uv run scripts/validate.py --input invalid.json --schema schema.json
# (validation report with errors)
$ echo $?
3
```
