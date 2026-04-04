#!/usr/bin/env bash

# AgentSkill processing script following official best practices.
#
# This script demonstrates proper agentic script design:
# - Non-interactive (all input via arguments)
# - Clear usage with --help
# - Structured output to stdout, diagnostics to stderr
# - Meaningful exit codes
# - Idempotent operations
# - Safe defaults, dry-run support

set -euo pipefail

# Script metadata
SCRIPT_NAME="$(basename "$0")"
VERSION="1.0.0"

# Exit codes
EXIT_SUCCESS=0
EXIT_INVALID_ARGS=1
EXIT_PROCESSING_ERROR=2
EXIT_OUTPUT_ERROR=3

# Default values
VERBOSE=false
DRY_RUN=false
OUTPUT_FORMAT="json"

# Usage function
usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] INPUT_FILE OUTPUT_FILE

Process validated data and generate output.

Arguments:
  INPUT_FILE         Input JSON file (required)
  OUTPUT_FILE        Output file path (required)

Options:
  --format FORMAT    Output format: json, csv, table (default: json)
  --dry-run          Preview changes without writing output
  --verbose          Print progress to stderr
  --help             Show this help message
  --version          Show version

Examples:
  $SCRIPT_NAME input.json output.json
  $SCRIPT_NAME --format csv input.json output.csv
  $SCRIPT_NAME --dry-run --verbose input.json output.json

Exit codes:
  $EXIT_SUCCESS - Success
  $EXIT_INVALID_ARGS - Invalid arguments
  $EXIT_PROCESSING_ERROR - Processing error
  $EXIT_OUTPUT_ERROR - Output write failure
EOF
}

# Parse arguments
INPUT_FILE=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            exit $EXIT_SUCCESS
            ;;
        --version)
            echo "$SCRIPT_NAME version $VERSION"
            exit $EXIT_SUCCESS
            ;;
        -*)
            echo "Error: Unknown option: $1" >&2
            echo "Run '$SCRIPT_NAME --help' for usage" >&2
            exit $EXIT_INVALID_ARGS
            ;;
        *)
            if [[ -z "$INPUT_FILE" ]]; then
                INPUT_FILE="$1"
            elif [[ -z "$OUTPUT_FILE" ]]; then
                OUTPUT_FILE="$1"
            else
                echo "Error: Too many arguments" >&2
                echo "Run '$SCRIPT_NAME --help' for usage" >&2
                exit $EXIT_INVALID_ARGS
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [[ -z "$INPUT_FILE" ]] || [[ -z "$OUTPUT_FILE" ]]; then
    echo "Error: INPUT_FILE and OUTPUT_FILE are required" >&2
    echo "Run '$SCRIPT_NAME --help' for usage" >&2
    exit $EXIT_INVALID_ARGS
fi

# Validate input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Input file not found: $INPUT_FILE" >&2
    exit $EXIT_INVALID_ARGS
fi

# Validate output format
case "$OUTPUT_FORMAT" in
    json|csv|table)
        ;;
    *)
        echo "Error: Invalid format '$OUTPUT_FORMAT'" >&2
        echo "       Must be one of: json, csv, table" >&2
        exit $EXIT_INVALID_ARGS
        ;;
esac

# Verbose logging function
log() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
    fi
}

# Process data function
process_data() {
    local input="$1"
    local format="$2"
    
    log "Processing input file: $input"
    log "Output format: $format"
    
    # Read and parse JSON (using jq for real implementation)
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is required but not installed" >&2
        echo "       Install with: apt install jq (or brew install jq)" >&2
        exit $EXIT_PROCESSING_ERROR
    fi
    
    # Count items
    local total_items
    total_items=$(jq '.items | length' "$input" 2>/dev/null || echo "0")
    
    if [[ "$total_items" -eq 0 ]]; then
        echo "Error: No items found in input file" >&2
        exit $EXIT_PROCESSING_ERROR
    fi
    
    log "Found $total_items items to process"
    
    # Process based on format
    case "$format" in
        json)
            process_json "$input"
            ;;
        csv)
            process_csv "$input"
            ;;
        table)
            process_table "$input"
            ;;
    esac
}

# Process JSON format
process_json() {
    local input="$1"
    
    log "Processing as JSON..."
    
    # Transform data (example: lowercase emails, add timestamp)
    jq '{
        processed: (.items | length),
        timestamp: now | todateiso8601,
        results: [
            .items[] | {
                id: .id,
                name: .name,
                email: (.email | ascii_downcase),
                status: .status,
                processed_at: (now | todateiso8601)
            }
        ]
    }' "$input"
}

# Process CSV format
process_csv() {
    local input="$1"
    
    log "Processing as CSV..."
    
    # Output CSV header
    echo "id,name,email,status"
    
    # Transform to CSV (lowercase emails)
    jq -r '.items[] | [.id, .name, (.email | ascii_downcase), .status] | @csv' "$input"
}

# Process table format
process_table() {
    local input="$1"
    
    log "Processing as table..."
    
    # Output formatted table
    jq -r '
        ["ID", "NAME", "EMAIL", "STATUS"],
        ["---", "---", "---", "---"],
        (.items[] | [.id, .name, (.email | ascii_downcase), .status])
        | @tsv
    ' "$input" | column -t
}

# Main execution
main() {
    log "Starting processing..."
    log "Input: $INPUT_FILE"
    log "Output: $OUTPUT_FILE"
    log "Format: $OUTPUT_FORMAT"
    log "Dry run: $DRY_RUN"
    
    # Process data
    if output=$(process_data "$INPUT_FILE" "$OUTPUT_FORMAT"); then
        if [[ "$DRY_RUN" == "true" ]]; then
            log "DRY RUN - Would write to $OUTPUT_FILE:"
            echo "$output"
        else
            # Write output
            if echo "$output" > "$OUTPUT_FILE"; then
                log "Successfully wrote output to $OUTPUT_FILE"
                
                # Show preview if verbose
                if [[ "$VERBOSE" == "true" ]]; then
                    log "Output preview (first 5 lines):"
                    head -n 5 "$OUTPUT_FILE" >&2
                fi
                
                # Output success summary to stdout
                echo "{\"status\": \"success\", \"output_file\": \"$OUTPUT_FILE\", \"format\": \"$OUTPUT_FORMAT\"}"
            else
                echo "Error: Failed to write output file: $OUTPUT_FILE" >&2
                exit $EXIT_OUTPUT_ERROR
            fi
        fi
    else
        echo "Error: Processing failed" >&2
        exit $EXIT_PROCESSING_ERROR
    fi
    
    log "Processing complete"
}

# Run main function
main
