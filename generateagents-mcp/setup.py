#!/usr/bin/env python3
"""
Setup helper script for registering GenerateAgents MCP server with various clients.

This script helps configure:
- VS Code Copilot
- Claude Desktop
- Local development (stdio transport)
"""

import os
import sys
import json
from pathlib import Path


PACKAGING_COMMANDS = {
    "editable_wheel",
    "egg_info",
    "dist_info",
    "bdist_wheel",
    "sdist",
    "develop",
    "build",
    "build_py",
    "install",
}


def get_config_dir(client: str) -> Path:
    """Get the configuration directory for a client."""
    home = Path.home()
    
    config_dirs = {
        "vscode": Path(__file__).parent.parent / ".vscode",
        "claude": home / ".claude" / "config.json" if sys.platform != "win32" else home / "AppData" / "Local" / "Claude" / "config.json",
        "cline": home / ".cline",
        "dev": Path(__file__).parent,
    }
    
    config_dir = config_dirs.get(client)
    if config_dir is None:
        raise ValueError(f"Unknown client: {client}")
    return config_dir


def setup_vscode_copilot():
    """Setup VS Code Copilot MCP configuration."""
    print("\n" + "=" * 70)
    print("VS Code Copilot Setup")
    print("=" * 70)
    
    vscode_dir = get_config_dir("vscode")
    vscode_dir.mkdir(parents=True, exist_ok=True)
    
    settings_file = vscode_dir / "settings.json"
    config_content = {
        "copilot.advanced": {
            "debug.testingEnabled": True
        },
        "[copilot].mcp": {
            "servers": [
                {
                    "name": "generateagents-mcp",
                    "description": "GenerateAgents.md MCP Server",
                    "command": "python",
                    "args": [
                        str(Path(__file__).parent / "server.py")
                    ],
                    "env": {
                        "PYTHONPATH": str(Path(__file__).parent.parent),
                        "LOG_LEVEL": "INFO"
                    }
                }
            ]
        }
    }
    
    # Merge with existing settings if present
    if settings_file.exists():
        try:
            existing = json.loads(settings_file.read_text())
            existing.update(config_content)
            config_content = existing
        except json.JSONDecodeError:
            pass
    
    settings_file.write_text(json.dumps(config_content, indent=2))
    print(f"✓ Created {settings_file}")
    print(f"  Open this file in VS Code settings editor to review")


def setup_claude_desktop():
    """Setup Claude Desktop MCP configuration."""
    print("\n" + "=" * 70)
    print("Claude Desktop Setup")
    print("=" * 70)
    
    home = Path.home()
    
    # Claude Desktop config location varies by platform
    if sys.platform == "darwin":  # macOS
        config_dir = home / "Library" / "Application Support" / "Claude"
    elif sys.platform == "linux":
        config_dir = home / ".config" / "Claude"
    elif sys.platform == "win32":
        config_dir = home / "AppData" / "Roaming" / "Claude"
    else:
        config_dir = home / ".claude"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "claude_desktop_config.json"
    
    config_content = {
        "mcpServers": {
            "generateagents-mcp": {
                "command": "python",
                "args": [
                    str(Path(__file__).parent / "server.py")
                ],
                "env": {
                    "PYTHONPATH": str(Path(__file__).parent.parent),
                    "LOG_LEVEL": "INFO"
                },
                "disabled": False,
                "description": "GenerateAgents.md MCP tools"
            }
        }
    }
    
    # Merge with existing config
    if config_file.exists():
        try:
            existing = json.loads(config_file.read_text())
            if "mcpServers" in existing:
                existing["mcpServers"].update(config_content["mcpServers"])
            else:
                existing.update(config_content)
            config_content = existing
        except json.JSONDecodeError:
            pass
    
    config_file.write_text(json.dumps(config_content, indent=2))
    print(f"✓ Created {config_file}")
    print(f"  Restart Claude Desktop for changes to take effect")


def setup_cline():
    """Setup Cline (VSCode extension) MCP configuration."""
    print("\n" + "=" * 70)
    print("Cline Setup")
    print("=" * 70)
    
    home = Path.home()
    config_dir = home / ".cline"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "mcp-servers.json"
    
    config_content = {
        "servers": [
            {
                "name": "generateagents-mcp",
                "type": "stdio",
                "command": "python",
                "args": [
                    str(Path(__file__).parent / "server.py")
                ],
                "env": {
                    "PYTHONPATH": str(Path(__file__).parent.parent)
                }
            }
        ]
    }
    
    if config_file.exists():
        try:
            existing = json.loads(config_file.read_text())
            existing["servers"].append(config_content["servers"][0])
            config_content = existing
        except json.JSONDecodeError:
            pass
    
    config_file.write_text(json.dumps(config_content, indent=2))
    print(f"✓ Created {config_file}")


def show_deployment_guide():
    """Show HTTP deployment guide for production."""
    print("\n" + "=" * 70)
    print("Production Deployment (HTTP Transport)")
    print("=" * 70)
    print("""
For cloud deployment with OpenAI, Anthropic, Mistral, or other APIs:

1. Modify server.py to use HTTP transport:

    if __name__ == "__main__":
        import uvicorn
        from mcp.server.httpserver import HTTPServer
        
        mcp.run(HTTPServer(host="0.0.0.0", port=8000))
        # or start with:
        # uvicorn async main:app --host 0.0.0.0 --port 8000

2. Deploy to your cloud platform:
   - AWS Lambda with FastAPI/Uvicorn wrapper
   - GCP Cloud Run (docker build + gcloud run deploy)
   - Azure Container Instances
   - Replit, Render, Heroku, etc.

3. Expose via HTTPS (CloudFlare, AWS API Gateway, etc.)

4. Register the HTTPS endpoint in client configs:
   
   For OpenAI Function Calling, see: openai-function-spec.json
   For Claude Desktop, update config to use HTTP transport URL

5. Add authentication layer (API key, OAuth2, etc.)

See integration-examples.py for language-specific examples.
    """)


def main():
    """Main setup function."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 17 + "GenerateAgents MCP Setup Helper" + " " * 21 + "║")
    print("╚" + "=" * 68 + "╝")
    
    if len(sys.argv) > 1:
        client = sys.argv[1].lower()
        
        if client == "vscode":
            setup_vscode_copilot()
        elif client == "claude":
            setup_claude_desktop()
        elif client == "cline":
            setup_cline()
        elif client == "all":
            setup_vscode_copilot()
            setup_claude_desktop()
            setup_cline()
            show_deployment_guide()
        elif client == "http":
            show_deployment_guide()
        else:
            print(f"\nUnknown client: {client}")
            print("\nUsage: python setup.py [vscode|claude|cline|all|http]")
    else:
        print("\nUsage: python setup.py [client]")
        print("\nClients:")
        print("  vscode   - Setup VS Code Copilot")
        print("  claude   - Setup Claude Desktop")
        print("  cline    - Setup Cline extension")
        print("  all      - Setup all local clients")
        print("  http     - Show HTTP deployment guide\n")
        print("Example:")
        print("  python setup.py all")
        
        # Auto-detect and suggest
        print("\n" + "=" * 70)
        print("Auto-detected clients:")
        print("=" * 70)
        
        home = Path.home()
        
        if (home / ".config" / "Code").exists() or (home / ".vscode").exists():
            print("✓ VS Code detected")
        
        if (home / "Library" / "Application Support" / "Claude").exists() or \
           (home / "AppData" / "Roaming" / "Claude").exists():
            print("✓ Claude Desktop detected")
        
        if (home / ".cline").exists():
            print("✓ Cline detected")
        
        print("\nRun: python setup.py all")


if __name__ == "__main__":
    # When invoked by packaging backends (e.g., uv/setuptools editable builds),
    # defer to setuptools instead of running the interactive helper CLI.
    if len(sys.argv) > 1 and sys.argv[1] in PACKAGING_COMMANDS:
        setuptools_mod = __import__("setuptools")
        setuptools_mod.setup()
    else:
        main()
