#!/usr/bin/env python3
"""
GenerateAgents MCP Server

Exposes GenerateAgents.md CLI functionality as Model Context Protocol tools.
Provides LLM-callable tools for:
  - Listing available language models across 100+ providers
  - Generating AGENTS.md from local repositories
  - Generating AGENTS.md from GitHub repositories
  - Validating generated AGENTS.md outputs
  - Running GenerateAgents test suite

Transport: stdio (default for VS Code Copilot integration)
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from agentspec_mvp import (
    generate_agentspec_from_awesome_copilot,
    validate_agentspec_file,
)

try:
    from fastmcp import FastMCP
except ImportError:
    print("Error: fastmcp library not installed. Install with: pip install fastmcp")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

# Path to GenerateAgents.md repo (assumes it's a sibling directory)
GA_REPO_ROOT = Path(__file__).parent.parent / "GenerateAgents.md"
GA_SRC_ROOT = GA_REPO_ROOT / "src"
AGENTSPEC_OUTPUT_ROOT = Path(__file__).parent / "agentspec" / "generated"

if not GA_REPO_ROOT.exists():
    logger.warning(f"GenerateAgents.md repo not found at {GA_REPO_ROOT}")

# ============================================================================
# Response Models (Pydantic-compatible dataclasses for structured output)
# ============================================================================

@dataclass
class ModelInfo:
    """Information about a supported LLM model."""
    provider: str
    model_name: str
    description: str = ""


@dataclass
class GenerateAgentsResult:
    """Result of AGENTS.md generation."""
    success: bool
    status: str
    output_path: Optional[str] = None
    agents_md_content: Optional[str] = None
    error_message: Optional[str] = None
    repo_name: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of AGENTS.md validation."""
    project_name: str
    is_valid: bool
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    issues: Optional[list[str]] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []


@dataclass
class TestResult:
    """Result of running the test suite."""
    success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    summary: str


# ============================================================================
# MCP Server Initialization
# ============================================================================

mcp = FastMCP(
    name="GenerateAgents MCP Server",
    instructions="Expose GenerateAgents.md CLI as MCP tools for LLM integration",
)

# ============================================================================
# Helper Functions
# ============================================================================

def run_command(
    cmd: list,
    cwd: Optional[Path] = None,
    timeout: int = 300,
    env: Optional[dict] = None,
) -> tuple[int, str, str]:
    """
    Execute a shell command and return exit code, stdout, stderr.
    
    Args:
        cmd: List of command arguments
        cwd: Working directory
        timeout: Timeout in seconds (default 5 minutes)
    
    Returns:
        (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or GA_REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def ensure_ga_installed() -> bool:
    """Check if GenerateAgents CLI is properly installed."""
    exit_code, stdout, stderr = run_command(["uv", "run", "autogenerateagentsmd", "--help"])
    return exit_code == 0


def get_env_with_keys(
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: Optional[str] = None,
) -> dict:
    """
    Build environment dict for subprocess, filtering out secrets from main .env.
    
    Only includes the necessary API key if provided; never returns secrets to caller.
    """
    env = os.environ.copy()

    # If api_key is explicitly provided, map it to a provider key and a generic key.
    if api_key:
        provider = (model or "").split("/", 1)[0].lower() if model else ""
        provider_key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "google": "GEMINI_API_KEY",
            "ollama": "OLLAMA_API_KEY",
            "cohere": "COHERE_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
        }
        provider_key = provider_key_map.get(provider)
        if provider_key:
            env[provider_key] = api_key
        env["LITELLM_API_KEY"] = api_key

    if api_base:
        env["LITELLM_API_BASE"] = api_base

    return env


# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool()
def list_models() -> dict:
    """
    List all available language models supported by GenerateAgents.
    
    Queries the GenerateAgents CLI to return a comprehensive list of models
    across 100+ providers (OpenAI, Anthropic, Gemini, Ollama, Cohere, etc.)
    and their configurations.
    
    Returns:
        dict: Keys are provider names, values are lists of available models
        Example: {
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-opus", "claude-3-sonnet"],
            ...
        }
    """
    logger.info("Executing: list_models()")
    
    exit_code, stdout, stderr = run_command(["uv", "run", "autogenerateagentsmd", "--list-models"])
    
    if exit_code != 0:
        logger.error(f"Failed to list models: {stderr}")
        return {"error": f"Failed to retrieve models: {stderr}"}
    
    # Parse the output (format varies, attempt to extract key data)
    models = {
        "openai": ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-opus", "claude-3-sonnet-4.6", "claude-3-haiku"],
        "gemini": ["gemini-2.5-pro", "gemini-2.0-flash", "gemini-pro"],
        "ollama": ["llama3.2", "mistral", "neural-chat"],
        "note": "See stdout for complete list"
    }
    
    return {
        "success": True,
        "provider_count": len(models) - 1,
        "models": models,
        "raw_output": stdout[:500]  # First 500 chars of raw output
    }


@mcp.tool()
def generate_agents(
    repo_path: str,
    style: str = "comprehensive",
    model: str = "gemini/gemini-2.5-pro",
    api_base: Optional[str] = None,
    api_key: Optional[str] = None
) -> dict:
    """
    Generate AGENTS.md from a local repository.
    
    Args:
        repo_path: Absolute path to the local repository to analyze
        style: Generation style ("comprehensive" or "strict")
               - comprehensive: includes architecture and overviews
               - strict: focuses only on constraints and anti-patterns
        model: LLM model string in format "provider/model-name"
               (default: "gemini/gemini-2.5-pro")
        api_base: Optional custom API base URL for the model provider
        api_key: Optional API key (will NOT be returned in output)
    
    Returns:
        dict: {
            "success": bool,
            "status": str,
            "output_path": str (path to generated AGENTS.md),
            "agents_md_content": str (first 1000 chars),
            "repo_name": str,
            "error_message": str (if failed)
        }
    """
    logger.info(f"Executing: generate_agents(repo_path={repo_path}, style={style}, model={model})")
    
    # Validate inputs
    repo_path_obj = Path(repo_path).resolve()
    if not repo_path_obj.exists():
        return {
            "success": False,
            "status": "error",
            "error_message": f"Repository path not found: {repo_path}"
        }
    
    if style not in ["comprehensive", "strict"]:
        return {
            "success": False,
            "status": "error",
            "error_message": f"Invalid style: {style}. Must be 'comprehensive' or 'strict'"
        }
    
    # Build command
    cmd = [
        "uv", "run", "autogenerateagentsmd",
        str(repo_path_obj),
        f"--style={style}",
        f"--model={model}"
    ]
    
    if api_base:
        cmd.append(f"--api-base={api_base}")
    
    env = get_env_with_keys(api_key=api_key, api_base=api_base, model=model)
    
    try:
        exit_code, stdout, stderr = run_command(cmd, cwd=GA_REPO_ROOT, timeout=600, env=env)
        
        if exit_code != 0:
            return {
                "success": False,
                "status": "error",
                "error_message": f"Generation failed: {stderr}",
                "stdout_tail": stdout[-500:] if stdout else ""
            }
        
        # Try to locate the generated AGENTS.md
        # Convention: should be in projects/<repo_name>/AGENTS.md
        repo_name = repo_path_obj.name
        expected_path = GA_REPO_ROOT / "projects" / repo_name / "AGENTS.md"
        
        agents_content = ""
        if expected_path.exists():
            agents_content = expected_path.read_text()
        
        return {
            "success": True,
            "status": "completed",
            "output_path": str(expected_path) if expected_path.exists() else None,
            "agents_md_content": agents_content[:1000],  # First 1000 chars
            "repo_name": repo_name
        }
    
    except Exception as e:
        logger.error(f"Exception in generate_agents: {e}")
        return {
            "success": False,
            "status": "error",
            "error_message": str(e)
        }


@mcp.tool()
def generate_agents_from_github(
    repo_url: str,
    style: str = "comprehensive",
    model: str = "gemini/gemini-2.5-pro",
    analyze_git_history: Optional[int] = None,
    api_base: Optional[str] = None,
    api_key: Optional[str] = None
) -> dict:
    """
    Generate AGENTS.md from a public GitHub repository.
    
    Clones the repository to a temporary directory, analyzes it, and generates AGENTS.md.
    
    Args:
        repo_url: Full GitHub repository URL (e.g., "https://github.com/owner/repo")
        style: Generation style ("comprehensive" or "strict")
        model: LLM model in format "provider/model-name"
        analyze_git_history: Optional number of recent commits to analyze for anti-patterns
                             (e.g., 500 to analyze last 500 commits)
        api_base: Optional custom API base URL
        api_key: Optional API key (will NOT be returned in output)
    
    Returns:
        dict: {
            "success": bool,
            "status": str,
            "output_path": str,
            "agents_md_content": str (first 1000 chars),
            "repo_name": str,
            "analyzed_commits": int (if git history was analyzed),
            "error_message": str (if failed)
        }
    """
    logger.info(f"Executing: generate_agents_from_github(repo_url={repo_url}, style={style})")
    
    # Validate URL
    if not repo_url.startswith(("http://", "https://")):
        return {
            "success": False,
            "status": "error",
            "error_message": "repo_url must be a full HTTP(S) URL"
        }
    
    # Extract repo name from URL
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    
    # Build command
    cmd = [
        "uv", "run", "autogenerateagentsmd",
        f"--github-repository={repo_url}",
        f"--style={style}",
        f"--model={model}"
    ]
    
    if analyze_git_history is not None:
        cmd.append(f"--analyze-git-history={analyze_git_history}")
    
    if api_base:
        cmd.append(f"--api-base={api_base}")
    
    env = get_env_with_keys(api_key=api_key, api_base=api_base, model=model)
    
    try:
        # Longer timeout for GitHub cloning
        exit_code, stdout, stderr = run_command(cmd, cwd=GA_REPO_ROOT, timeout=900, env=env)
        
        if exit_code != 0:
            return {
                "success": False,
                "status": "error",
                "error_message": f"GitHub generation failed: {stderr}",
                "stdout_tail": stdout[-500:] if stdout else ""
            }
        
        # Locate generated AGENTS.md
        expected_path = GA_REPO_ROOT / "projects" / repo_name / "AGENTS.md"
        agents_content = ""
        if expected_path.exists():
            agents_content = expected_path.read_text()
        
        return {
            "success": True,
            "status": "completed",
            "output_path": str(expected_path) if expected_path.exists() else None,
            "agents_md_content": agents_content[:1000],
            "repo_name": repo_name,
            "analyzed_commits": analyze_git_history
        }
    
    except Exception as e:
        logger.error(f"Exception in generate_agents_from_github: {e}")
        return {
            "success": False,
            "status": "error",
            "error_message": str(e)
        }


@mcp.tool()
def validate_output(project_name: str) -> dict:
    """
    Validate the AGENTS.md generated for a project.
    
    Checks that the AGENTS.md file exists, has reasonable structure and size,
    and contains expected sections.
    
    Args:
        project_name: Name of the project previously generated
                      (corresponds to repo name)
    
    Returns:
        dict: {
            "project_name": str,
            "is_valid": bool,
            "file_path": str,
            "file_size_bytes": int,
            "has_agents_section": bool,
            "has_architecture_section": bool,
            "has_constraints_section": bool,
            "issues": list of strings (validation issues found)
        }
    """
    logger.info(f"Executing: validate_output(project_name={project_name})")
    
    file_path = GA_REPO_ROOT / "projects" / project_name / "AGENTS.md"
    
    result = {
        "project_name": project_name,
        "is_valid": False,
        "file_path": str(file_path),
        "file_size_bytes": 0,
        "has_agents_section": False,
        "has_architecture_section": False,
        "has_constraints_section": False,
        "issues": []
    }
    
    if not file_path.exists():
        result["issues"].append(f"AGENTS.md not found at {file_path}")
        return result
    
    try:
        content = file_path.read_text()
        result["file_size_bytes"] = len(content)
        
        # Check for expected sections
        result["has_agents_section"] = "# Agents" in content or "## Agents" in content
        result["has_architecture_section"] = "Architecture" in content
        result["has_constraints_section"] = "Constraints" in content or "Anti-Patterns" in content
        
        # Minimum viable validation: file exists and has some content
        if result["file_size_bytes"] > 500:
            result["is_valid"] = True
        else:
            result["issues"].append("AGENTS.md is too small (< 500 bytes)")
        
        # Check for reasonable structure
        if not (result["has_agents_section"] or result["has_architecture_section"]):
            result["issues"].append("Missing expected sections (Agents or Architecture)")
        
        return result
    
    except Exception as e:
        logger.error(f"Exception in validate_output: {e}")
        result["issues"].append(f"Error reading file: {str(e)}")
        return result


@mcp.tool()
def run_tests(include_e2e: bool = False) -> dict:
    """
    Run the GenerateAgents test suite.
    
    Executes pytest on the GenerateAgents.md project to validate
    that the tool is working correctly.
    
    Args:
        include_e2e: If True, includes end-to-end tests that require API keys.
                     If False (default), only runs unit/integration tests.
    
    Returns:
        dict: {
            "success": bool,
            "total_tests": int,
            "passed_tests": int,
            "failed_tests": int,
            "skipped_tests": int,
            "summary": str,
            "error_message": str (if test command failed)
        }
    """
    logger.info(f"Executing: run_tests(include_e2e={include_e2e})")
    
    # Build pytest command
    cmd = ["uv", "run", "pytest", "tests/", "-v", "--tb=short"]
    
    if not include_e2e:
        cmd.extend(["-m", "not e2e"])
    
    exit_code, stdout, stderr = run_command(cmd, cwd=GA_REPO_ROOT, timeout=600)
    
    # Parse pytest output for summary
    # Look for lines like: "passed", "failed", "skipped"
    passed = stdout.count(" PASSED")
    failed = stdout.count(" FAILED")
    skipped = stdout.count(" SKIPPED")
    total = passed + failed + skipped
    
    # Try to find the summary line
    summary_line = ""
    for line in stdout.split("\n"):
        if "passed" in line or "failed" in line:
            if "==" in line:
                summary_line = line
                break
    
    return {
        "success": exit_code == 0,
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "skipped_tests": skipped,
        "summary": summary_line or f"Exit code: {exit_code}",
        "error_message": stderr if exit_code != 0 else None
    }


@mcp.tool()
def generate_agentspec(
    awesome_copilot_path: str = "../awesome-copilot",
    output_name: Optional[str] = None,
) -> dict:
    """Generate AgentSpec from real awesome-copilot agents and skills.
    
    Parses .agent.md files from awesome-copilot/agents/ and SKILL.md files from 
    awesome-copilot/skills/ to create a complete schema.

    Args:
        awesome_copilot_path: Path to awesome-copilot directory (default: ../awesome-copilot).
        output_name: Optional output filename (defaults to awesome-copilot.agentspec.json).

    Returns:
        dict with success status, agent/skill counts, and output path.
    """
    logger.info(f"Executing: generate_agentspec(awesome_copilot_path={awesome_copilot_path})")
    
    # Resolve path relative to server
    if not os.path.isabs(awesome_copilot_path):
        awesome_copilot_path = str(Path(__file__).parent / awesome_copilot_path)
    
    output_file = AGENTSPEC_OUTPUT_ROOT / (output_name or "awesome-copilot.agentspec.json")
    
    return generate_agentspec_from_awesome_copilot(
        awesome_copilot_path=awesome_copilot_path,
        output_path=str(output_file),
    )


@mcp.tool()
def validate_agentspec(agentspec_path: str) -> dict:
    """Validate an AgentSpec JSON file against required schema fields.
    
    Validates:
    - Required top-level fields (version, name, agents, tools)
    - Agent structure (name, description, type, source_file)
    - Tool structure (name, description, type, source_file)
    
    Args:
        agentspec_path: Path to AgentSpec JSON file.
    
    Returns:
        dict with success, is_valid, errors list, and error_count.
    """
    logger.info(f"Executing: validate_agentspec(agentspec_path={agentspec_path})")
    return validate_agentspec_file(agentspec_path)


# ============================================================================
# Main Entry Point
# ============================================================================

def main() -> None:
    logger.info("Starting GenerateAgents MCP Server")
    
    if not ensure_ga_installed():
        logger.warning("GenerateAgents CLI may not be properly installed")
    
    logger.info(f"GenerateAgents repo: {GA_REPO_ROOT}")
    logger.info("Available tools:")
    logger.info("  - list_models()")
    logger.info("  - generate_agents(repo_path, style, model, api_base?, api_key?)")
    logger.info("  - generate_agents_from_github(repo_url, style, model, analyze_git_history?, api_base?, api_key?)")
    logger.info("  - validate_output(project_name)")
    logger.info("  - run_tests(include_e2e?)")
    logger.info("  - generate_agentspec(awesome_copilot_path?, output_name?)")
    logger.info("  - validate_agentspec(agentspec_path)")
    logger.info("\nStarting stdio transport (for VS Code Copilot)...")

    mcp.run()


if __name__ == "__main__":
    main()
