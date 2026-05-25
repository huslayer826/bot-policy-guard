from __future__ import annotations

from bot_policy_guard.audit import audit_repo

from .conftest import write


def test_workflow_flags_unpinned_actions_permissions_and_dependabot_automerge_soak(tmp_path):
    write(
        tmp_path / ".github" / "dependabot.yml",
        """
        version: 2
        updates:
          - package-ecosystem: "github-actions"
            directory: "/"
            schedule:
              interval: "weekly"
            open-pull-requests-limit: 3
            groups:
              actions:
                patterns: ["*"]
        """,
    )
    write(
        tmp_path / ".github" / "workflows" / "automerge.yml",
        """
        name: Dependabot Automerge
        on:
          pull_request_target:
        permissions: write-all
        jobs:
          merge:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - run: gh pr merge "$PR_URL" --auto --merge
        """,
    )

    result = audit_repo(tmp_path)
    rule_ids = {finding.rule_id for finding in result.findings}

    assert "BPG-GHA-ACTION-NOT-PINNED" in rule_ids
    assert "BPG-WORKFLOW-PERMISSIONS-BROAD" in rule_ids
    assert "BPG-DEPENDABOT-AUTOMERGE-SOAK" in rule_ids


def test_pinned_grouped_action_workflow_has_no_action_grouping_findings(tmp_path):
    sha = "d" * 40
    write(
        tmp_path / ".github" / "dependabot.yml",
        """
        version: 2
        updates:
          - package-ecosystem: "github-actions"
            directory: "/"
            schedule:
              interval: "weekly"
            open-pull-requests-limit: 3
            cooldown:
              default-days: 3
            groups:
              actions:
                patterns: ["*"]
        """,
    )
    write(
        tmp_path / ".github" / "workflows" / "ci.yml",
        f"""
        name: CI
        on: [pull_request]
        permissions:
          contents: read
        jobs:
          test:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@{sha}
        """,
    )

    result = audit_repo(tmp_path)
    rule_ids = {finding.rule_id for finding in result.findings}

    assert "BPG-GHA-ACTION-NOT-PINNED" not in rule_ids
    assert "BPG-GHA-UPDATES-NOT-GROUPED" not in rule_ids
