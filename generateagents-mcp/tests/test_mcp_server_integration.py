"""Integration test for MCP server startup and AgentSpec tool chain.

This test validates that:
1. The MCP server starts successfully
2. All tools are discoverable (including new AgentSpec tools)
3. AgentSpec tool chain (generate -> validate -> emit) works end-to-end
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_server_startup_with_agentspec() -> None:
    """Test that server starts successfully and doesn't crash."""
    server_py = Path(__file__).parent.parent / "server.py"
    assert server_py.exists(), f"server.py not found at {server_py}"

    # Start server in background with timeout
    proc = subprocess.Popen(
        [sys.executable, str(server_py)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Give server 2 seconds to start
    time.sleep(2)

    # Check that process is still running
    assert proc.poll() is None, f"Server exited early with code {proc.poll()}"

    # Terminate gracefully
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    # Check startup logs for expected messages
    stdout, stderr = proc.communicate()
    startup_output = stdout + stderr

    # Verify key startup messages
    assert (
        "GenerateAgents MCP Server" in startup_output
    ), f"Server didn't log expected startup message. Got: {startup_output}"

    print("✓ Server startup successful")


def test_agentspec_tools_are_wired() -> None:
    """Test that AgentSpec tools are callable (direct import test)."""
    from agentspec_integration import (
        emit_agentspec_artifacts,
        generate_agentspec_artifact,
        validate_agentspec_file,
    )

    # Verify functions are callable
    assert callable(generate_agentspec_artifact)
    assert callable(validate_agentspec_file)
    assert callable(emit_agentspec_artifacts)

    print("✓ AgentSpec tools are properly wired")


def test_agentspec_end_to_end() -> None:
    """Test AgentSpec tool chain: generate -> validate -> emit."""
    from agentspec_integration import (
        emit_agentspec_artifacts,
        generate_agentspec_artifact,
        validate_agentspec_file,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 1. Create a sample repo
        repo_dir = tmpdir / "sample-repo"
        repo_dir.mkdir()
        (repo_dir / "src").mkdir()
        (repo_dir / "src" / "main.py").write_text("# Main module\nprint('hi')\n")
        (repo_dir / "tests").mkdir()
        (repo_dir / "tests" / "test_main.py").write_text("# Tests\ndef test_hi(): pass\n")
        (repo_dir / "README.md").write_text("# Sample Repo\n")
        (repo_dir / "package.json").write_text('{"name": "sample"}\n')

        # 2. Generate AgentSpec from repo
        out_dir = tmpdir / "agentspec"
        out_dir.mkdir()
        gen_result = generate_agentspec_artifact(
            repo_path=str(repo_dir),
            output_dir=str(out_dir),
        )

        assert gen_result["success"] is True, f"Generation failed: {gen_result}"
        spec_path = Path(gen_result["output_path"])
        assert spec_path.exists(), f"Generated spec not found at {spec_path}"

        # Verify spec structure
        spec_content = json.loads(spec_path.read_text())
        assert spec_content["version"] == "1.0.0"
        assert "agents" in spec_content
        assert len(spec_content["agents"]) >= 1
        print(f"✓ Generated AgentSpec with {len(spec_content['agents'])} agents")

        # 3. Validate AgentSpec
        val_result = validate_agentspec_file(str(spec_path))
        assert val_result["success"] is True, f"Validation failed: {val_result}"
        assert val_result["is_valid"] is True, f"Spec is invalid: {val_result['issues']}"
        print("✓ AgentSpec validated successfully")

        # 4. Emit artifacts (AGENTS.md and n8n workflow)
        emit_result = emit_agentspec_artifacts(
            agentspec_path=str(spec_path),
            targets=["agents-md", "n8n-workflow"],
            output_dir=str(out_dir),
        )

        assert emit_result["success"] is True, f"Emission failed: {emit_result}"
        assert "agents-md" in emit_result["emitted"]
        assert "n8n-workflow" in emit_result["emitted"]

        # Verify emitted files exist and have content
        agents_md_path = Path(emit_result["emitted"]["agents-md"])
        workflow_path = Path(emit_result["emitted"]["n8n-workflow"])

        assert agents_md_path.exists(), f"AGENTS.md not found at {agents_md_path}"
        assert workflow_path.exists(), f"Workflow not found at {workflow_path}"

        agents_md_content = agents_md_path.read_text()
        assert "# AGENTS.md" in agents_md_content, "AGENTS.md missing title"
        assert "codebase_analyst" in agents_md_content, "AGENTS.md missing expected agent"
        print("✓ Emitted AGENTS.md successfully")

        workflow_json = json.loads(workflow_path.read_text())
        assert workflow_json.get("name") == "sample-repo-agentspec"
        assert len(workflow_json.get("nodes", [])) >= 1, "Workflow has no nodes"
        assert (
            workflow_json.get("meta", {}).get("generatedFrom") == "AgentSpec"
        ), "Workflow missing AgentSpec metadata"
        print("✓ Emitted n8n workflow successfully")

        print("\n✅ AgentSpec end-to-end pipeline working correctly!")


if __name__ == "__main__":
    print("Running MCP Server Integration Tests...\n")
    print("Test 1: Server Startup with AgentSpec Tools")
    test_server_startup_with_agentspec()
    print("\nTest 2: AgentSpec Tools Are Wired")
    test_agentspec_tools_are_wired()
    print("\nTest 3: AgentSpec End-to-End Pipeline")
    test_agentspec_end_to_end()
    print("\n✅ All integration tests passed!")
