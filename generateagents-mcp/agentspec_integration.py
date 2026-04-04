"""AgentSpec integration helpers for GenerateAgents MCP Server.

This module provides lightweight, dependency-free AgentSpec functionality:
- Generate a starter AgentSpec from a local repository
- Validate an AgentSpec against required fields (schema, naming, reserved names, circular deps)
- Emit AGENTS.md and n8n workflow JSON artifacts

Validation cascade inspired by smallagents POC patterns:
1. Schema validation (required fields, types)
2. Naming conventions (lowercase_with_underscores)
3. Reserved names check (prevents system conflicts)
4. Tool references validation (ensure tools exist)
5. Circular dependency detection (prevent infinite loops)
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


# Validation constants (from smallagents POC patterns)
VALID_AGENT_NAME_PATTERN = r"^[a-z][a-z0-9_]*$"
RESERVED_AGENT_NAMES = {"all", "default", "system", "core", "builtin"}
VALID_TOOL_NAME_PATTERN = r"^[a-z][a-z0-9_-]*$"
RESERVED_TOOL_NAMES = {"all", "default", "system"}


def _repo_extension_stats(repo_path: Path) -> dict[str, int]:
    """Collect file extension frequency for source-like files in a repository."""
    counts: Counter[str] = Counter()
    skip_dirs = {
        ".git",
        "node_modules",
        ".venv",
        "venv",
        "dist",
        "build",
        "out",
        "coverage",
        "__pycache__",
    }

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue

        if any(part in skip_dirs for part in file_path.parts):
            continue

        ext = file_path.suffix.lower() or "<no_ext>"
        counts[ext] += 1

    return dict(counts.most_common())


def _default_agentspec(repo_path: Path) -> dict[str, Any]:
    """Build a starter AgentSpec object from a repository path."""
    repo_name = repo_path.name
    ext_stats = _repo_extension_stats(repo_path)
    top_extensions = list(ext_stats.keys())[:5]

    return {
        "version": "1.0.0",
        "name": f"{repo_name}-agentspec",
        "description": f"Starter AgentSpec generated for repository '{repo_name}'.",
        "domain": "generic",
        "metadata": {
            "source_repository": str(repo_path),
            "top_extensions": top_extensions,
            "file_extension_stats": ext_stats,
        },
        "agents": {
            "codebase_analyst": {
                "type": "specialist",
                "description": "Analyzes repository structure and conventions.",
                "roles": ["analyst", "reviewer"],
                "model": "gemini/gemini-2.5-pro",
                "capabilities": [
                    {
                        "name": "analyze-codebase",
                        "description": "Inspect architecture and coding patterns.",
                        "inputs": ["repository-path"],
                        "outputs": ["analysis-report"],
                    },
                    {
                        "name": "suggest-agent-roles",
                        "description": "Recommend specialized agent roles for the codebase.",
                        "inputs": ["analysis-report"],
                        "outputs": ["agent-role-recommendations"],
                    },
                ],
                "constraints": [
                    "Must not modify source files during analysis.",
                    "Must provide deterministic output for the same input commit.",
                ],
                "tools": [],
            }
        },
        "workflows": [
            {
                "name": "AgentSpecBootstrap",
                "description": "Baseline workflow for generating agent recommendations.",
                "steps": [
                    {
                        "agent": "codebase_analyst",
                        "outputs": ["analysis-report", "agent-role-recommendations"],
                    }
                ],
                "contracts": [
                    "analysis-report must include architecture summary and anti-pattern hints"
                ],
            }
        ],
    }


def generate_agentspec_artifact(
    repo_path: str,
    output_dir: str,
    output_name: str | None = None,
) -> dict[str, Any]:
    """Generate and persist a starter AgentSpec for a local repository."""
    repo = Path(repo_path).resolve()
    if not repo.exists() or not repo.is_dir():
        return {
            "success": False,
            "status": "error",
            "error_message": f"Repository path not found or not a directory: {repo_path}",
        }

    agentspec = _default_agentspec(repo)

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = output_name or f"{repo.name}.agentspec.json"
    out_path = out_dir / filename
    out_path.write_text(json.dumps(agentspec, indent=2) + "\n", encoding="utf-8")

    return {
        "success": True,
        "status": "completed",
        "output_path": str(out_path),
        "repo_name": repo.name,
        "agent_count": len(agentspec.get("agents", {})),
        "workflow_count": len(agentspec.get("workflows", [])),
        "preview": json.dumps(agentspec, indent=2)[:1000],
    }


# ============================================================================
# Validation Functions (Cascade Pattern from smallagents POC)
# ============================================================================


def _create_validation_error(
    error_type: str, path: str, message: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Create a structured validation error (smallagents pattern).

    Args:
        error_type: Type of error (schema, naming, reserved, circular, reference, etc.)
        path: JSON path or agent/tool name where error occurred
        message: Human-readable error message
        params: Additional error parameters

    Returns:
        Structured error dict with type, path, message, and params
    """
    return {
        "type": error_type,
        "path": path,
        "message": message,
        "params": params or {},
    }


def _validate_naming_conventions(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate agent and tool naming conventions (lowercase_with_underscores).

    Implements smallagents POC pattern for strict naming enforcement.
    """
    errors: list[dict[str, Any]] = []

    # Check agent names
    for agent_name in spec.get("agents", {}):
        if agent_name in RESERVED_AGENT_NAMES:
            errors.append(
                _create_validation_error(
                    "reserved",
                    agent_name,
                    f"Agent name uses reserved word: {agent_name}",
                    {"allowed": list(RESERVED_AGENT_NAMES)},
                )
            )
        elif not re.match(VALID_AGENT_NAME_PATTERN, agent_name):
            errors.append(
                _create_validation_error(
                    "naming",
                    agent_name,
                    "Invalid agent name format. Must be lowercase_with_underscores",
                    {"pattern": VALID_AGENT_NAME_PATTERN, "example": "my_agent"},
                )
            )

    # Check tool names (in agents' tool lists)
    for agent_name, agent in spec.get("agents", {}).items():
        for tool_name in agent.get("tools", []):
            if tool_name in RESERVED_TOOL_NAMES:
                errors.append(
                    _create_validation_error(
                        "reserved",
                        f"{agent_name}.tools.{tool_name}",
                        f"Tool name uses reserved word: {tool_name}",
                    )
                )
            elif not re.match(VALID_TOOL_NAME_PATTERN, tool_name):
                errors.append(
                    _create_validation_error(
                        "naming",
                        f"{agent_name}.tools.{tool_name}",
                        "Invalid tool name format. Must be lowercase with hyphens/underscores",
                    )
                )

    return errors


def _validate_tool_references(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate that referenced tools are defined in spec.

    Implements smallagents POC pattern for tool reference validation.
    """
    errors: list[dict[str, Any]] = []
    defined_tools = set(spec.get("tools", {}).keys())

    for agent_name, agent in spec.get("agents", {}).items():
        for tool_name in agent.get("tools", []):
            if tool_name not in defined_tools and tool_name not in RESERVED_TOOL_NAMES:
                errors.append(
                    _create_validation_error(
                        "reference",
                        f"{agent_name}.tools.{tool_name}",
                        f"Referenced tool not found in spec: {tool_name}",
                        {"defined_tools": list(defined_tools)},
                    )
                )

    return errors


def _detect_circular_dependencies(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect circular dependencies in agent/tool relationships.

    Implements smallagents POC pattern for circular dependency detection.
    """
    errors: list[dict[str, Any]] = []

    # Build adjacency graph for agents
    graph: dict[str, set[str]] = {
        agent_name: {tool for tool in agent.get("tools", [])}
        for agent_name, agent in spec.get("agents", {}).items()
    }

    # Detect cycles using DFS
    visited: set[str] = set()
    rec_stack: set[str] = set()

    def has_cycle(node: str, path: list[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                if has_cycle(neighbor, path + [node]):
                    return True
            elif neighbor in rec_stack:
                cycle_path = " -> ".join(path + [node, neighbor])
                errors.append(
                    _create_validation_error(
                        "circular",
                        node,
                        f"Circular dependency detected: {cycle_path}",
                        {"cycle": path + [node, neighbor]},
                    )
                )
                return True

        rec_stack.remove(node)
        return False

    for agent_name in graph:
        if agent_name not in visited:
            has_cycle(agent_name, [])

    return errors


def validate_agentspec_content(spec: dict[str, Any]) -> dict[str, Any]:
    """Validate AgentSpec with full cascade: schema -> naming -> reserved -> refs -> circular.

    Implements smallagents POC validation cascade pattern with detailed error reporting.

    Validation layers:
    1. Schema validation (required fields, types)
    2. Naming conventions (lowercase_with_underscores)
    3. Reserved names check (prevents system conflicts)
    4. Tool references validation (ensure tools exist)
    5. Circular dependency detection (prevent infinite loops)

    Returns:
        Dict with:
        - is_valid (bool): True if all validations pass
        - errors (list): Detailed error dicts with type, path, message, params
        - error_count_by_type (dict): Count of errors by type for quick assessment
    """
    all_errors: list[dict[str, Any]] = []

    # ========== Layer 1: Schema Validation ==========
    required_top_level = ["version", "agents"]
    for key in required_top_level:
        if key not in spec:
            all_errors.append(
                _create_validation_error(
                    "schema", f"root.{key}", f"Missing required top-level field: {key}"
                )
            )

    if "agents" in spec and not isinstance(spec["agents"], dict):
        all_errors.append(
            _create_validation_error(
                "schema", "root.agents", "Field 'agents' must be an object"
            )
        )
        # Return early if agents is malformed; can't validate further
        return {
            "is_valid": False,
            "errors": all_errors,
            "error_count_by_type": {"schema": 1},
        }

    if isinstance(spec.get("agents"), dict):
        for agent_name, agent in spec["agents"].items():
            if not isinstance(agent, dict):
                all_errors.append(
                    _create_validation_error(
                        "schema",
                        f"agents.{agent_name}",
                        f"Agent must be an object",
                    )
                )
                continue

            for key in ["type", "description", "model", "capabilities"]:
                if key not in agent:
                    all_errors.append(
                        _create_validation_error(
                            "schema",
                            f"agents.{agent_name}.{key}",
                            f"Missing required agent field: {key}",
                        )
                    )

            if "capabilities" in agent and not isinstance(agent["capabilities"], list):
                all_errors.append(
                    _create_validation_error(
                        "schema",
                        f"agents.{agent_name}.capabilities",
                        "Field 'capabilities' must be a list",
                    )
                )

    # ========== Layer 2: Naming Conventions ==========
    all_errors.extend(_validate_naming_conventions(spec))

    # ========== Layer 3: Tool References ==========
    all_errors.extend(_validate_tool_references(spec))

    # ========== Layer 4: Circular Dependencies ==========
    all_errors.extend(_detect_circular_dependencies(spec))

    # Count errors by type
    error_types: dict[str, int] = {}
    for error in all_errors:
        error_type = error.get("type", "unknown")
        error_types[error_type] = error_types.get(error_type, 0) + 1

    return {
        "is_valid": len(all_errors) == 0,
        "errors": all_errors,
        "error_count_by_type": error_types,
    }


def validate_agentspec_file(agentspec_path: str) -> dict[str, Any]:
    """Load and validate an AgentSpec file with full validation cascade.

    Args:
        agentspec_path: Path to AgentSpec JSON file

    Returns:
        Dict with:
        - success (bool): True if file loaded successfully
        - status (str): "completed" or "error"
        - agentspec_path (str): Resolved path to file
        - is_valid (bool): True if all validations pass
        - errors (list): Detailed error dicts
        - error_count_by_type (dict): Count of errors by type
        - error_message (str): Set if success=False
    """
    path = Path(agentspec_path).resolve()
    if not path.exists():
        return {
            "success": False,
            "status": "error",
            "error_message": f"AgentSpec file not found: {agentspec_path}",
        }

    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "success": False,
            "status": "error",
            "error_message": f"Invalid JSON in AgentSpec: {exc}",
        }

    result = validate_agentspec_content(spec)
    return {
        "success": True,
        "status": "completed",
        "agentspec_path": str(path),
        "is_valid": result["is_valid"],
        "errors": result["errors"],
        "error_count_by_type": result.get("error_count_by_type", {}),
    }


def _emit_agents_md(spec: dict[str, Any]) -> str:
    """Emit AGENTS.md content from AgentSpec."""
    lines: list[str] = [
        "# AGENTS.md",
        "",
        f"Generated from AgentSpec `{spec.get('name', 'unnamed')}` (v{spec.get('version', 'unknown')}).",
        "",
    ]

    for agent_name, agent in spec.get("agents", {}).items():
        lines.extend(
            [
                f"## {agent_name}",
                "",
                f"- Type: `{agent.get('type', 'unknown')}`",
                f"- Model: `{agent.get('model', 'unknown')}`",
                f"- Description: {agent.get('description', '')}",
                "",
                "### Capabilities",
            ]
        )
        for capability in agent.get("capabilities", []):
            lines.append(f"- **{capability.get('name', 'unnamed')}**: {capability.get('description', '')}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _emit_n8n_workflow(spec: dict[str, Any]) -> dict[str, Any]:
    """Emit a simple n8n workflow JSON from AgentSpec agents/workflows."""
    nodes: list[dict[str, Any]] = []
    connections: dict[str, Any] = {}

    agent_names = list(spec.get("agents", {}).keys())
    for index, agent_name in enumerate(agent_names):
        agent = spec["agents"][agent_name]
        nodes.append(
            {
                "id": str(index + 1),
                "name": agent_name,
                "type": "n8n-nodes-base.noOp",
                "typeVersion": 1,
                "position": [index * 260, 240],
                "parameters": {
                    "model": agent.get("model"),
                    "description": agent.get("description"),
                },
            }
        )

    for index in range(len(agent_names) - 1):
        current_agent = agent_names[index]
        next_agent = agent_names[index + 1]
        connections[current_agent] = {
            "main": [[{"node": next_agent, "type": "main", "index": 0}]]
        }

    return {
        "name": spec.get("name", "agentspec-workflow"),
        "nodes": nodes,
        "connections": connections,
        "settings": {},
        "staticData": None,
        "pinData": {},
        "meta": {"generatedFrom": "AgentSpec"},
    }


def emit_agentspec_artifacts(
    agentspec_path: str,
    targets: list[str],
    output_dir: str,
) -> dict[str, Any]:
    """Emit artifacts for requested targets from an AgentSpec file.

    Args:
        agentspec_path: Path to AgentSpec JSON file
        targets: List of target formats (agents-md, n8n-workflow)
        output_dir: Directory to write emitted artifacts

    Returns:
        Dict with:
        - success (bool): True if emission succeeded
        - status (str): "completed" or "error"
        - agentspec_path (str): Resolved file path
        - emitted (dict): Map of target -> output file path
        - unsupported_targets (list): Target formats not supported
        - error_message (str): Set if success=False
        - issues (list): Validation errors (if emission failed)
    """
    path = Path(agentspec_path).resolve()
    if not path.exists():
        return {
            "success": False,
            "status": "error",
            "error_message": f"AgentSpec file not found: {agentspec_path}",
        }

    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "success": False,
            "status": "error",
            "error_message": f"Invalid JSON in AgentSpec: {exc}",
        }

    validation = validate_agentspec_content(spec)
    if not validation["is_valid"]:
        return {
            "success": False,
            "status": "error",
            "error_message": "AgentSpec is invalid; cannot emit artifacts",
            "issues": validation["errors"],
            "error_count_by_type": validation.get("error_count_by_type", {}),
        }

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    emitted: dict[str, str] = {}
    normalized_targets = {target.strip().lower() for target in targets if target.strip()}

    if "agents-md" in normalized_targets:
        agents_md_path = out_dir / f"{path.stem}.AGENTS.md"
        agents_md_path.write_text(_emit_agents_md(spec), encoding="utf-8")
        emitted["agents-md"] = str(agents_md_path)

    if "n8n-workflow" in normalized_targets:
        workflow_path = out_dir / f"{path.stem}.n8n.workflow.json"
        workflow_path.write_text(json.dumps(_emit_n8n_workflow(spec), indent=2) + "\n", encoding="utf-8")
        emitted["n8n-workflow"] = str(workflow_path)

    unsupported = sorted(
        target for target in normalized_targets if target not in {"agents-md", "n8n-workflow"}
    )

    return {
        "success": True,
        "status": "completed",
        "agentspec_path": str(path),
        "emitted": emitted,
        "unsupported_targets": unsupported,
    }
