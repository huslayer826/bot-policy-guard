from __future__ import annotations

import json

from bot_policy_guard.audit import audit_repo
from bot_policy_guard.cli import run
from bot_policy_guard.renderers import render

from .conftest import write


def test_json_markdown_and_sarif_outputs(tmp_path):
    write(
        tmp_path / "renovate.json",
        """
        {
          "automerge": true
        }
        """,
    )
    result = audit_repo(tmp_path)

    json_payload = json.loads(render(result, "json"))
    markdown = render(result, "markdown")
    sarif = json.loads(render(result, "sarif"))

    assert json_payload["tool"] == "bot-policy-guard"
    assert json_payload["summary"]["findings"] >= 1
    assert "| Severity | Rule | Location | Finding |" in markdown
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"][0]["ruleId"].startswith("BPG-")


def test_cli_writes_output_file_and_respects_severity_thresholds(tmp_path):
    write(
        tmp_path / "renovate.json",
        """
        {
          "prConcurrentLimit": 5,
          "prHourlyLimit": 2
        }
        """,
    )
    output = tmp_path / "report.json"

    assert run([str(tmp_path), "--format", "json", "--output", str(output), "--fail-on", "high"]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["summary"]["findings"] == 1
    assert run([str(tmp_path), "--format", "json", "--output", str(output), "--fail-on", "low"]) == 1
