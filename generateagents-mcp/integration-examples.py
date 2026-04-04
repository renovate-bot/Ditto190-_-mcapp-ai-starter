#!/usr/bin/env python3
"""
OpenAI Function Calling Integration Example

This example demonstrates how to use the GenerateAgents MCP tools
with OpenAI's Function Calling API (Chat Completions with tools).

Install: pip install openai
"""

import json
import subprocess
import sys
from pathlib import Path

# Optional import; only required for OpenAI examples
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Load the OpenAI function spec
SPEC_FILE = Path(__file__).parent / "openai-function-spec.json"

def load_functions():
    """Load the OpenAI function definitions from the spec."""
    with open(SPEC_FILE) as f:
        spec = json.load(f)
    return spec["x-openai-functions"]


def start_mcp_server():
    """Start the MCP server in the background and return the process."""
    server_script = Path(__file__).parent / "server.py"
    # Note: For production, use HTTP transport instead of stdio
    # This is a simplified example; stdio doesn't work with REST APIs
    print("Note: Stdio transport requires direct subprocess integration.")
    print("For OpenAI API calls, deploy MCP server as HTTP endpoint.")
    return None


def example_generate_agents_locally():
    """
    Example: Use the GenerateAgents MCP tools directly via subprocess (no OpenAI).
    This is useful for testing or when you want full control.
    """
    print("=" * 70)
    print("EXAMPLE 1: Direct MCP Server Call (Best for Testing)")
    print("=" * 70)
    
    # Start MCP server
    server_script = Path(__file__).parent / "server.py"
    
    print(f"Starting MCP server: {server_script}")
    process = subprocess.Popen(
        ["python", str(server_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("MCP server started (stdio transport)")
    print("In production, deploy as HTTP server and use OpenAI API calls.\n")
    
    # For stdio transport, you would send MCP protocol messages
    # This is handled by MCP client libraries
    process.terminate()


def example_openai_function_calling():
    """
    Example: Use OpenAI Function Calling API with GenerateAgents tools.
    
    This requires:
    1. MCP server deployed as HTTP endpoint
    2. Function definitions loaded from openai-function-spec.json
    3. OpenAI API client configured
    
    In practice, you'd implement a tool_handler() that dispatches to your
    MCP server (or direct Python functions) and returns results to OpenAI.
    """
    print("=" * 70)
    print("EXAMPLE 2: OpenAI Function Calling (Production Deployment)")
    print("=" * 70)
    
    if OpenAI is None:
        print("Note: openai library not installed. Install with: pip install openai\n")
        return
    
    client = OpenAI()
    
    # Load function definitions
    try:
        functions = load_functions()
        print(f"Loaded {len(functions)} function definitions from spec\n")
    except FileNotFoundError:
        print(f"Error: {SPEC_FILE} not found")
        return
    
    # Example: User request to generate AGENTS.md
    messages = [
        {
            "role": "user",
            "content": "Generate AGENTS.md for the repository at /tmp/my-python-project using the Gemini model. Use comprehensive style."
        }
    ]
    
    print("User request:", messages[0]["content"])
    print()
    
    # Call OpenAI with function definitions
    print("Calling OpenAI Chat Completions with tools...")
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        tools=[
            {
                "type": "function",
                "function": func
            }
            for func in functions
        ],
        tool_choice="auto",  # Let OpenAI decide if/which tool to call
        max_tokens=1024
    )
    
    print(f"Response stop_reason: {response.stop_reason}")
    
    # Check if OpenAI wants to use a tool
    if response.stop_reason == "tool_calls":
        for tool_call in response.choices[0].message.tool_calls:
            print(f"\n✓ OpenAI chose to call: {tool_call.function.name}")
            print(f"  Parameters: {tool_call.function.arguments}")
            
            # Parse the arguments
            args = json.loads(tool_call.function.arguments)
            
            # TODO: Here you would call your actual MCP server with these args
            # For now, print what would be called:
            print(f"\n  → Would call MCP tool with args: {json.dumps(args, indent=2)}")
    else:
        print("\nOpenAI response (no tool call):")
        print(response.choices[0].message.content)


def example_anthropic_integration():
    """
    Example: Using GenerateAgents tools with Anthropic Claude API.
    Claude supports similar tool calling via the 'tools' parameter.
    """
    print("=" * 70)
    print("EXAMPLE 3: Anthropic Claude Integration")
    print("=" * 70)
    print("""
Anthropic Claude Tools API (similar to OpenAI):

from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[
        {
            "name": "generateagents_generate_agents",
            "description": "Generate AGENTS.md from a repository",
            "input_schema": {
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                    "style": {"type": "string", "enum": ["comprehensive", "strict"]},
                    "model": {"type": "string"}
                },
                "required": ["repo_path"]
            }
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Generate AGENTS.md for my repo"
        }
    ]
)

# Check for tool use
if response.stop_reason == "tool_use":
    for content_block in response.content:
        if content_block.type == "tool_use":
            print(f"Tool: {content_block.name}")
            print(f"Input: {content_block.input}")
    """)


def example_mistral_integration():
    """
    Example: Using with Mistral API (function calling).
    """
    print("=" * 70)
    print("EXAMPLE 4: Mistral Integration")
    print("=" * 70)
    print("""
from mistralai.client import MistralClient

client = MistralClient()
response = client.chat(
    model="mistral-large-latest",
    messages=[...],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "generateagents_generate_agents",
                "description": "Generate AGENTS.md",
                "parameters": {...}
            }
        }
    ]
)

# Check response for tool calls
for choice in response.choices:
    if choice.message.tool_calls:
        for tool_call in choice.message.tool_calls:
            print(f"Tool: {tool_call.function.name}")
            print(f"Arguments: {tool_call.function.arguments}")
    """)


def example_together_ai_integration():
    """
    Example: Using with Together AI (supports function calling).
    """
    print("=" * 70)
    print("EXAMPLE 5: Together.ai Integration")
    print("=" * 70)
    print("""
import together

response = together.Complete.create(
    prompt="Generate AGENTS.md for /path/to/repo",
    model="mistral-7b-instruct",  # or other Together model
    # Together doesn't yet have native tool calling like OpenAI,
    # but you can use prompt engineering or plugin system
)

# For Together AI: Use prompt engineering to request tool calls
# or integrate with their plugin API
    """)


def example_local_ollama_integration():
    """
    Example: Using with local Ollama (function calling via prompt).
    """
    print("=" * 70)
    print("EXAMPLE 6: Local Ollama Integration")
    print("=" * 70)
    print("""
import ollama

# Ollama doesn't have native tool calling, so use prompt engineering
# or integrate with a tool dispatcher via Python

tools_description = '''
Available tools:
1. generateagents_generate_agents(repo_path, style, model)
   - Generate AGENTS.md from a local repo
2. generateagents_list_models()
   - List available models
...
'''

response = ollama.chat(
    model='llama3.2',
    messages=[
        {
            'role': 'user',
            'content': f'''Use these tools to help: {tools_description}
Task: Generate AGENTS.md for /path/to/repo using comprehensive style'''
        }
    ]
)

# Parse response to extract tool calls (via regex or structured prompt)
# Then dispatch to MCP server
    """)


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║  GenerateAgents MCP Tools - AI Integration Examples              ║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # Note: Only run examples that don't require API keys by default
    print("QUICKSTART:\n")
    print("1. Deploy MCP server as HTTP endpoint:")
    print("   python server.py --http --port 8000\n")
    print("2. Register functions with your AI platform using openai-function-spec.json\n")
    print("3. Call the mcp-dispatch middleware to route function calls to the server\n")
    
    # Print integration examples
    example_openai_function_calling()
    print()
    example_anthropic_integration()
    print()
    example_mistral_integration()
    print()
    example_together_ai_integration()
    print()
    example_local_ollama_integration()
    
    print("\n")
    print("=" * 70)
    print("DEPLOYMENT CHECKLIST")
    print("=" * 70)
    print("""
For production deployment with OpenAI, Anthropic, Mistral, etc.:

☐ 1. Deploy MCP server:
    - Update server.py to use HTTPServer transport
    - Deploy to cloud (AWS Lambda, GCP Cloud Run, Azure Container Instances, etc.)
    - Obtain HTTPS endpoint URL

☐ 2. Register functions with AI providers:
    - OpenAI: Use tools parameter in Chat Completions API
    - Anthropic: Use tools parameter in Messages API
    - Mistral: Use tools parameter (if supported by model)

☐ 3. Implement tool dispatcher:
    - Create webhook/endpoint that intercepts tool calls
    - Route to your MCP server
    - Return results in OpenAI/Anthropic/Mistral format

☐ 4. Security hardening:
    - Rotate API keys before deploying (see .env.sample in GenerateAgents.md)
    - Use environment variables, not config files
    - Add authentication/API key validation to MCP server
    - Log tool calls for audit trail
    - Implement rate limiting

☐ 5. Testing:
    - Test each tool independently
    - Test error cases (invalid paths, network timeouts, etc.)
    - Load test if high traffic expected

☐ 6. Monitoring:
    - Log all tool invocations
    - Monitor response times
    - Alert on failures
    - Track usage per tool/user
    """)


if __name__ == "__main__":
    main()
