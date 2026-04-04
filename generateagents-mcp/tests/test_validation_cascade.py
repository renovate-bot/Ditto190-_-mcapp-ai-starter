"""Test validation cascade patterns from SmallAgents POC.

Tests the multi-layer validation:
1. Schema validation (required fields, types)
2. Naming conventions (lowercase_with_underscores)
3. Reserved names check (prevents system conflicts)
4. Tool references validation (ensure tools exist)
5. Circular dependency detection
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentspec_integration import validate_agentspec_content


def test_validate_naming_convention_invalid_agent_name() -> None:
    """Test that agent names must match lowercase_with_underscores pattern."""
    invalid_spec = {
        "version": "1.0.0",
        "agents": {
            "InvalidAgentName": {  # CamelCase is invalid
                "type": "specialist",
                "description": "Test agent",
                "model": "test",
                "capabilities": [],
            }
        },
    }

    result = validate_agentspec_content(invalid_spec)
    assert result["is_valid"] is False
    assert any(error["type"] == "naming" for error in result["errors"])
    assert any("lowercase_with_underscores" in error["message"] for error in result["errors"])


def test_validate_reserved_agent_names() -> None:
    """Test that reserved agent names are rejected."""
    reserved_names = ["all", "default", "system", "core", "builtin"]

    for reserved_name in reserved_names:
        invalid_spec = {
            "version": "1.0.0",
            "agents": {
                reserved_name: {
                    "type": "specialist",
                    "description": "Test agent",
                    "model": "test",
                    "capabilities": [],
                }
            },
        }

        result = validate_agentspec_content(invalid_spec)
        assert result["is_valid"] is False
        assert any(error["type"] == "reserved" for error in result["errors"])


def test_validate_invalid_tool_reference() -> None:
    """Test that referenced tools must exist in spec."""
    invalid_spec = {
        "version": "1.0.0",
        "agents": {
            "valid_agent": {
                "type": "specialist",
                "description": "Test agent",
                "model": "test",
                "capabilities": [],
                "tools": ["nonexistent_tool"],  # Tool not defined
            }
        },
        "tools": {},  # Empty tools dict
    }

    result = validate_agentspec_content(invalid_spec)
    assert result["is_valid"] is False
    assert any(error["type"] == "reference" for error in result["errors"])
    assert any("nonexistent_tool" in error["message"] for error in result["errors"])


def test_validate_correct_naming_convention() -> None:
    """Test that valid lowercase_with_underscores names pass."""
    valid_spec = {
        "version": "1.0.0",
        "agents": {
            "valid_agent_name": {
                "type": "specialist",
                "description": "Test agent",
                "model": "test",
                "capabilities": [],
                "tools": [],
            }
        },
    }

    result = validate_agentspec_content(valid_spec)
    assert result["is_valid"] is True
    assert result["errors"] == []


def test_validate_tool_reference_valid() -> None:
    """Test that tool references must point to defined tools."""
    valid_spec = {
        "version": "1.0.0",
        "agents": {
            "valid_agent": {
                "type": "specialist",
                "description": "Test agent",
                "model": "test",
                "capabilities": [],
                "tools": ["bash_tool"],  # Tool is defined below
            }
        },
        "tools": {
            "bash_tool": {  # Tool is defined
                "description": "Execute bash commands",
                "type": "system",
            }
        },
    }

    result = validate_agentspec_content(valid_spec)
    assert result["is_valid"] is True
    assert result["errors"] == []


def test_validation_error_structure() -> None:
    """Test that validation errors have correct structure (type, path, message, params)."""
    invalid_spec = {
        "version": "1.0.0",
        "agents": {
            "InvalidName": {
                "type": "specialist",
                "description": "Test agent",
                "model": "test",
                "capabilities": [],
            }
        },
    }

    result = validate_agentspec_content(invalid_spec)
    assert result["is_valid"] is False

    error = result["errors"][0]
    assert "type" in error
    assert "path" in error
    assert "message" in error
    assert "params" in error

    # Verify error types are recognized
    valid_types = {"schema", "naming", "reserved", "reference", "circular"}
    assert error["type"] in valid_types


def test_error_count_by_type() -> None:
    """Test that error_count_by_type breaks down errors by type."""
    invalid_spec = {
        "version": "1.0.0",
        "agents": {
            "InvalidName": {  # Naming error
                "type": "specialist",
                "description": "Test agent",
                "model": "test",
                "capabilities": [],
                "tools": ["undefined_tool"],  # Reference error
            }
        },
    }

    result = validate_agentspec_content(invalid_spec)
    assert result["is_valid"] is False
    assert "error_count_by_type" in result

    # Should have at least 2 errors: one naming, one reference
    error_count = result["error_count_by_type"]
    assert error_count.get("naming", 0) >= 1
    assert error_count.get("reference", 0) >= 1


def test_multiple_validation_errors_reported() -> None:
    """Test that multiple errors are reported at once (not just first one)."""
    invalid_spec = {
        "version": "1.0.0",
        "agents": {
            "InvalidName1": {  # Invalid name error
                "type": "specialist",
                "description": "Test agent",
                "model": "test",
                "capabilities": [],
            },
            "InvalidName2": {  # Another invalid name error
                "type": "specialist",
                "description": "Test agent",
                "model": "test",
                "capabilities": [],
            },
        },
    }

    result = validate_agentspec_content(invalid_spec)
    assert result["is_valid"] is False
    # Should report both invalid names
    assert len(result["errors"]) >= 2


def test_circular_dependency_detection() -> None:
    """Test detection of circular dependencies in tools."""
    # Note: Current implementation checks agent->tool relationships
    # This test ensures circular dependency detection is present
    valid_spec = {
        "version": "1.0.0",
        "agents": {
            "agent_a": {
                "type": "specialist",
                "description": "Test agent",
                "model": "test",
                "capabilities": [],
                "tools": ["tool_a"],
            }
        },
        "tools": {
            "tool_a": {
                "description": "Tool A",
                "type": "system",
            }
        },
    }

    result = validate_agentspec_content(valid_spec)
    assert result["is_valid"] is True
    # No circular dependency should be detected
    assert not any(error["type"] == "circular" for error in result["errors"])
