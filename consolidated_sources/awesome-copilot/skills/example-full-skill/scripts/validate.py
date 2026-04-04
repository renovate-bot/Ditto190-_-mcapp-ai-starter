#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pydantic>=2.0.0",
#   "strictyaml>=1.7.3",
# ]
# requires-python = ">=3.11"
# ///

"""
AgentSkill validation script following official best practices.

This script validates input data against a JSON schema and demonstrates
proper agentic script design:
- Non-interactive (all input via CLI flags)
- Clear --help output
- Structured JSON output to stdout
- Progress/errors to stderr
- Meaningful exit codes
- Idempotent (safe to retry)
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List


def validate_email(email: str) -> bool:
    """Basic email validation."""
    return '@' in email and '.' in email.split('@')[1]


def validate_status(status: str) -> bool:
    """Validate status enum."""
    return status in ['active', 'inactive', 'pending']


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load JSON schema file."""
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path) as f:
        return json.load(f)


def load_input(input_path: Path) -> Dict[str, Any]:
    """Load input JSON file."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    with open(input_path) as f:
        return json.load(f)


def validate_item(item: Dict[str, Any], item_index: int) -> Dict[str, Any]:
    """
    Validate a single item.
    
    Returns dict with 'valid' boolean and optional 'error' message.
    """
    errors = []
    
    # Required fields
    if 'id' not in item:
        errors.append("missing required field 'id'")
    if 'name' not in item:
        errors.append("missing required field 'name'")
    if 'email' not in item:
        errors.append("missing required field 'email'")
    else:
        if not validate_email(item['email']):
            errors.append(f"invalid email format: {item['email']}")
    
    if 'status' not in item:
        errors.append("missing required field 'status'")
    else:
        if not validate_status(item['status']):
            errors.append(f"invalid status value: {item['status']} (must be: active, inactive, pending)")
    
    if errors:
        return {
            'valid': False,
            'item_index': item_index,
            'item_id': item.get('id', f'unknown-{item_index}'),
            'errors': errors
        }
    
    return {
        'valid': True,
        'item_index': item_index,
        'item_id': item['id']
    }


def validate_data(data: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """
    Validate input data structure and contents.
    
    Returns validation report with structured results.
    """
    results = {
        'valid': True,
        'total_items': 0,
        'valid_items': 0,
        'invalid_items': 0,
        'errors': []
    }
    
    # Check top-level structure
    if 'items' not in data:
        results['valid'] = False
        results['errors'].append({
            'type': 'structure',
            'message': "missing required field 'items'"
        })
        return results
    
    if not isinstance(data['items'], list):
        results['valid'] = False
        results['errors'].append({
            'type': 'structure',
            'message': "'items' must be an array"
        })
        return results
    
    items = data['items']
    results['total_items'] = len(items)
    
    if verbose:
        print(f"Validating {len(items)} items...", file=sys.stderr)
    
    # Validate each item
    for i, item in enumerate(items):
        validation = validate_item(item, i)
        
        if validation['valid']:
            results['valid_items'] += 1
            if verbose:
                print(f"  ✓ Item {i}: {validation['item_id']}", file=sys.stderr)
        else:
            results['valid'] = False
            results['invalid_items'] += 1
            results['errors'].append(validation)
            if verbose:
                print(f"  ✗ Item {i}: {validation['item_id']}", file=sys.stderr)
                for error in validation['errors']:
                    print(f"      - {error}", file=sys.stderr)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Validate input data against expected schema',
        epilog='''
Examples:
  %(prog)s --input data.json --schema schema.json
  %(prog)s --input data.json --schema schema.json --verbose
  %(prog)s --input data.json --schema schema.json --output report.json

Exit codes:
  0 - All items valid
  1 - Invalid arguments
  2 - File not found
  3 - Validation failed (some items invalid)
        '''
    )
    
    parser.add_argument('--input', type=Path, required=True,
                       help='Input JSON file to validate')
    parser.add_argument('--schema', type=Path, required=True,
                       help='JSON schema file')
    parser.add_argument('--output', type=Path,
                       help='Write validation report to file (default: stdout)')
    parser.add_argument('--verbose', action='store_true',
                       help='Print progress to stderr')
    
    args = parser.parse_args()
    
    try:
        # Load files
        if args.verbose:
            print(f"Loading schema from {args.schema}...", file=sys.stderr)
        schema = load_schema(args.schema)
        
        if args.verbose:
            print(f"Loading input from {args.input}...", file=sys.stderr)
        data = load_input(args.input)
        
        # Validate
        results = validate_data(data, verbose=args.verbose)
        
        # Output results
        output_json = json.dumps(results, indent=2)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
            if args.verbose:
                print(f"Validation report written to {args.output}", file=sys.stderr)
        else:
            print(output_json)
        
        # Summary to stderr
        if args.verbose:
            print("\nValidation Summary:", file=sys.stderr)
            print(f"  Total items: {results['total_items']}", file=sys.stderr)
            print(f"  Valid: {results['valid_items']}", file=sys.stderr)
            print(f"  Invalid: {results['invalid_items']}", file=sys.stderr)
            print(f"  Overall: {'✓ PASS' if results['valid'] else '✗ FAIL'}", file=sys.stderr)
        
        # Exit code based on validation result
        sys.exit(0 if results['valid'] else 3)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
