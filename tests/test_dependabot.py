from __future__ import annotations

from bot_policy_guard.audit import audit_repo

from .conftest import write


def test_dependabot_flags_limits_groups_disabled_updates_and_broad_ignore(tmp_path):
    write(
        tmp_path / ".github" / "dependabot.yml",
        """
        version: 2
        updates:
          - package-ecosystem: "pip"
            directory: "/"
            schedule:
              interval: "weekly"
            ignore:
              - dependency-name: "*"
          - package-ecosystem: "github-actions"
            directory: "/"
            schedule:
              interval: "weekly"
            open-pull-requests-limit: 0
        """,
    )

    result = audit_repo(tmp_path)
    rule_ids = {finding.rule_id for finding in result.findings}

    assert "BPG-DEPENDABOT-UPDATE-LIMITS" in rule_ids
    assert "BPG-DEPENDABOT-MISSING-GROUPS" in rule_ids
    assert "BPG-DEPENDABOT-GHA-NOT-GROUPED" in rule_ids
    assert "BPG-DEPENDABOT-UPDATES-DISABLED" in rule_ids
    assert "BPG-DEPENDABOT-BROAD-IGNORE" in rule_ids
