#!/usr/bin/env -S deno run --allow-read
/**
 * AgentSkill data extraction script using Deno runtime.
 *
 * This script demonstrates proper agentic script design with Deno:
 * - Self-contained with npm: imports (dependencies auto-installed)
 * - Non-interactive (all input via CLI flags)
 * - Clear --help output
 * - Structured JSON output to stdout
 * - Errors to stderr
 * - Meaningful exit codes
 */

// Dependencies declared inline - Deno auto-installs on first run
import { parse } from "https://deno.land/std@0.224.0/flags/mod.ts";

// Type definitions
interface InputData {
  items?: Array<Record<string, unknown>>;
  [key: string]: unknown;
}

interface ExtractionResult {
  total_items: number;
  extracted_fields: string[];
  results: Array<Record<string, unknown>>;
}

// Script metadata
const VERSION = "1.0.0";
const SCRIPT_NAME = "extract.ts";

// Exit codes
const EXIT_SUCCESS = 0;
const EXIT_INVALID_ARGS = 1;
const EXIT_FILE_ERROR = 2;
const EXIT_PROCESSING_ERROR = 3;

// Usage function
function usage(): void {
  console.log(`
Usage: deno run --allow-read ${SCRIPT_NAME} [OPTIONS]

Extract specific fields from structured JSON data.

Options:
  --file PATH        Input JSON file (required)
  --fields FIELDS    Comma-separated list of fields to extract (required)
  --output PATH      Write output to file instead of stdout
  --pretty           Pretty-print JSON output
  --verbose          Print progress to stderr
  --help             Show this help message
  --version          Show version

Examples:
  deno run --allow-read ${SCRIPT_NAME} --file data.json --fields name,email
  deno run --allow-read ${SCRIPT_NAME} --file data.json --fields id,status --pretty
  deno run --allow-read,--allow-write ${SCRIPT_NAME} --file data.json --fields name,email --output result.json

Exit codes:
  ${EXIT_SUCCESS} - Success
  ${EXIT_INVALID_ARGS} - Invalid arguments
  ${EXIT_FILE_ERROR} - File read/write error
  ${EXIT_PROCESSING_ERROR} - Processing error
`);
}

// Log function (to stderr if verbose)
function log(message: string, verbose: boolean): void {
  if (verbose) {
    const timestamp = new Date().toISOString();
    console.error(`[${timestamp}] ${message}`);
  }
}

// Read JSON file
async function readJsonFile(filePath: string): Promise<InputData> {
  try {
    const content = await Deno.readTextFile(filePath);
    return JSON.parse(content) as InputData;
  } catch (error) {
    if (error instanceof Deno.errors.NotFound) {
      throw new Error(`File not found: ${filePath}`);
    } else if (error instanceof SyntaxError) {
      throw new Error(`Invalid JSON in file: ${filePath}`);
    }
    throw error;
  }
}

// Write output
async function writeOutput(
  data: ExtractionResult,
  outputPath: string | undefined,
  pretty: boolean,
): Promise<void> {
  const json = pretty ? JSON.stringify(data, null, 2) : JSON.stringify(data);

  if (outputPath) {
    await Deno.writeTextFile(outputPath, json);
  } else {
    console.log(json);
  }
}

// Extract fields from items
function extractFields(
  data: InputData,
  fields: string[],
  verbose: boolean,
): ExtractionResult {
  if (!data.items || !Array.isArray(data.items)) {
    throw new Error("Input must contain 'items' array");
  }

  log(
    `Extracting ${fields.length} fields from ${data.items.length} items`,
    verbose,
  );

  const results = data.items.map((item, index) => {
    const extracted: Record<string, unknown> = {};

    for (const field of fields) {
      if (field in item) {
        extracted[field] = item[field];
      } else {
        log(`Warning: Field '${field}' not found in item ${index}`, verbose);
        extracted[field] = null;
      }
    }

    return extracted;
  });

  return {
    total_items: data.items.length,
    extracted_fields: fields,
    results,
  };
}

// Main function
async function main(): Promise<void> {
  // Parse arguments
  const args = parse(Deno.args, {
    string: ["file", "fields", "output"],
    boolean: ["pretty", "verbose", "help", "version"],
    alias: {
      f: "file",
      o: "output",
      p: "pretty",
      v: "verbose",
      h: "help",
    },
  });

  // Handle --help
  if (args.help) {
    usage();
    Deno.exit(EXIT_SUCCESS);
  }

  // Handle --version
  if (args.version) {
    console.log(`${SCRIPT_NAME} version ${VERSION}`);
    Deno.exit(EXIT_SUCCESS);
  }

  // Validate required arguments
  if (!args.file) {
    console.error("Error: --file is required");
    console.error(`Run 'deno run ${SCRIPT_NAME} --help' for usage`);
    Deno.exit(EXIT_INVALID_ARGS);
  }

  if (!args.fields) {
    console.error("Error: --fields is required");
    console.error(`Run 'deno run ${SCRIPT_NAME} --help' for usage`);
    Deno.exit(EXIT_INVALID_ARGS);
  }

  // Parse fields
  const fields = args.fields.split(",").map((f: string) => f.trim());
  if (fields.length === 0) {
    console.error("Error: --fields must contain at least one field");
    Deno.exit(EXIT_INVALID_ARGS);
  }

  try {
    log(`Reading file: ${args.file}`, args.verbose);
    const data = await readJsonFile(args.file);

    log(`Processing data with fields: ${fields.join(", ")}`, args.verbose);
    const result = extractFields(data, fields, args.verbose);

    log(`Extracted ${result.total_items} items`, args.verbose);

    if (args.output) {
      log(`Writing output to: ${args.output}`, args.verbose);
    }

    await writeOutput(result, args.output, args.pretty);

    if (args.verbose) {
      log("Extraction complete", args.verbose);
    }

    Deno.exit(EXIT_SUCCESS);
  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error: ${error.message}`);

      if (
        error.message.includes("File not found") ||
        error.message.includes("Invalid JSON")
      ) {
        Deno.exit(EXIT_FILE_ERROR);
      }
    }

    console.error("Processing failed");
    Deno.exit(EXIT_PROCESSING_ERROR);
  }
}

// Run main function
if (import.meta.main) {
  main();
}
