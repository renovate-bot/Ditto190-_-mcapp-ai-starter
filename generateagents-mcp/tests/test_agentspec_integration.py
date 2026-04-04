import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentspec_integration import (
    emit_agentspec_artifacts,
    generate_agentspec_artifact,
    validate_agentspec_file,
)


def test_generate_validate_emit_agentspec(tmp_path: Path) -> None:
    repo_dir = tmp_path / "sample-repo"
    repo_dir.mkdir()
    (repo_dir / "main.py").write_text("print('hi')\n", encoding="utf-8")
    (repo_dir / "README.md").write_text("# sample\n", encoding="utf-8")

    out_dir = tmp_path / "generated"

    generate_result = generate_agentspec_artifact(
        repo_path=str(repo_dir),
        output_dir=str(out_dir),
    )

    assert generate_result["success"] is True
    spec_path = Path(generate_result["output_path"])
    assert spec_path.exists()

    validate_result = validate_agentspec_file(str(spec_path))
    assert validate_result["success"] is True
    assert validate_result["is_valid"] is True
    assert validate_result["errors"] == []

    emit_result = emit_agentspec_artifacts(
        agentspec_path=str(spec_path),
        targets=["agents-md", "n8n-workflow"],
        output_dir=str(out_dir),
    )

    assert emit_result["success"] is True
    assert "agents-md" in emit_result["emitted"]
    assert "n8n-workflow" in emit_result["emitted"]

    agents_md = Path(emit_result["emitted"]["agents-md"])
    workflow_json = Path(emit_result["emitted"]["n8n-workflow"])

    assert agents_md.exists()
    assert workflow_json.exists()

    workflow = json.loads(workflow_json.read_text(encoding="utf-8"))
    assert workflow["meta"]["generatedFrom"] == "AgentSpec"
    assert len(workflow["nodes"]) >= 1


def test_validate_agentspec_reports_missing_fields(tmp_path: Path) -> None:
    bad_spec_path = tmp_path / "bad.agentspec.json"
    bad_spec_path.write_text(json.dumps({"name": "bad"}), encoding="utf-8")

    result = validate_agentspec_file(str(bad_spec_path))
    assert result["success"] is True
    assert result["is_valid"] is False
    # Errors are now dicts with {type, path, message, params}
    error_messages = [error["message"] for error in result["errors"]]
    assert any("version" in msg for msg in error_messages)
    assert any("agents" in msg for msg in error_messages)
