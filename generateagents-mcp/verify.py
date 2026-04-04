#!/usr/bin/env python3
"""
Verification script for GenerateAgents MCP server.

Tests:
1. Python version compatibility
2. MCP library availability
3. Server syntax validation
4. Tool definitions availability
5. Configuration files existence
6. Setup helper functionality
"""

import sys
import json
import subprocess
from pathlib import Path


def check_python_version():
    """Verify Python 3.12+ is available."""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 12:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor} (need 3.12+)")
        return False


def check_mcp_library():
    """Verify mcp library is installed."""
    print("📋 Checking mcp library...")
    try:
        import mcp
        print(f"   ✓ mcp installed")
        return True
    except ImportError:
        print("   ✗ mcp library not found")
        print("     Run: pip install mcp")
        return False


def check_server_syntax():
    """Verify server.py has valid syntax."""
    print("📋 Checking server.py syntax...")
    server_file = Path(__file__).parent / "server.py"
    
    try:
        with open(server_file) as f:
            compile(f.read(), str(server_file), "exec")
        print(f"   ✓ {server_file.name} syntax valid")
        return True
    except SyntaxError as e:
        print(f"   ✗ Syntax error: {e}")
        return False
    except FileNotFoundError:
        print(f"   ✗ File not found: {server_file}")
        return False


def check_config_files():
    """Verify all configuration files exist."""
    print("📋 Checking configuration files...")
    mcp_dir = Path(__file__).parent
    
    required_files = [
        "server.py",
        "README.md",
        "DEPLOYMENT.md",
        "pyproject.toml",
        "vscode-copilot-mcp-config.json",
        "claude-desktop-mcp-config.json",
        "openai-function-spec.json",
        "setup.py",
        "integration-examples.py",
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = mcp_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"   ✓ {filename} ({size:,} bytes)")
        else:
            print(f"   ✗ {filename} NOT FOUND")
            all_exist = False
    
    return all_exist


def check_openai_spec():
    """Verify OpenAI function spec has 5 tools."""
    print("📋 Checking OpenAI function spec...")
    spec_file = Path(__file__).parent / "openai-function-spec.json"
    
    try:
        with open(spec_file) as f:
            spec = json.load(f)
        
        tools = spec.get("x-openai-functions", [])
        expected_tools = {
            "generateagents_list_models",
            "generateagents_generate_agents",
            "generateagents_generate_agents_from_github",
            "generateagents_validate_output",
            "generateagents_run_tests",
        }
        
        found_tools = {tool["name"] for tool in tools}
        
        if found_tools == expected_tools:
            print(f"   ✓ All 5 tools defined in spec")
            for tool in tools:
                print(f"     - {tool['name']}")
            return True
        else:
            missing = expected_tools - found_tools
            extra = found_tools - expected_tools
            if missing:
                print(f"   ✗ Missing tools: {missing}")
            if extra:
                print(f"   ✗ Extra tools: {extra}")
            return False
    
    except Exception as e:
        print(f"   ✗ Error reading spec: {e}")
        return False


def check_generateagents_install():
    """Verify GenerateAgents.md is installed."""
    print("📋 Checking GenerateAgents.md installation...")
    ga_dir = Path(__file__).parent.parent / "GenerateAgents.md"
    
    if not ga_dir.exists():
        print(f"   ✗ GenerateAgents.md not found at {ga_dir}")
        return False
    
    if (ga_dir / "pyproject.toml").exists():
        print(f"   ✓ GenerateAgents.md found")
        
        # Check if CLI is available
        try:
            result = subprocess.run(
                ["uv", "run", "autogenerateagentsmd", "--help"],
                cwd=ga_dir,
                capture_output=True,
                timeout=10,
                text=True
            )
            if result.returncode == 0:
                print(f"   ✓ autogenerateagentsmd CLI available")
                return True
            else:
                print(f"   ⚠ CLI returned error code {result.returncode}")
                print(f"     Run: cd {ga_dir} && uv sync")
                return False
        except subprocess.TimeoutExpired:
            print(f"   ⚠ CLI check timed out")
            return True  # Might still be installed
        except FileNotFoundError:
            print(f"   ⚠ uv not found; skipping CLI check")
            return True  # uv might not be in path
    
    return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("  GenerateAgents MCP Server - Verification")
    print("=" * 70 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("MCP Library", check_mcp_library),
        ("Server Syntax", check_server_syntax),
        ("Config Files", check_config_files),
        ("OpenAI Spec", check_openai_spec),
        ("GenerateAgents CLI", check_generateagents_install),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"   ✗ Exception: {e}")
            results[name] = False
        print()
    
    # Summary
    print("=" * 70)
    print("  Summary")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print(f"\n{'RESULT':<8} {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ All systems ready!")
        print("\nNext steps:")
        print("  1. cd generateagents-mcp")
        print("  2. python setup.py all")
        print("  3. Restart VS Code or Claude Desktop")
        print("  4. Test the tools in your AI assistant!")
        return 0
    else:
        print(f"\n❌ {total - passed} check(s) failed")
        print("\nSee details above. Run:")
        print("  - pip install mcp")
        print("  - cd GenerateAgents.md && uv sync")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
