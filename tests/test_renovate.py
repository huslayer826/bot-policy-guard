from __future__ import annotations

from bot_policy_guard.audit import audit_repo

from .conftest import write


def test_renovate_json5_flags_automerge_without_soak(tmp_path):
    write(
        tmp_path / "renovate.json5",
        """
        {
          // JSON5 comments and trailing commas are supported.
          automerge: true,
          vulnerabilityAlerts: { enabled: false },
        }
        """,
    )

    result = audit_repo(tmp_path)
    rule_ids = {finding.rule_id for finding in result.findings}

    assert "BPG-RENOVATE-AUTOMERGE-SOAK" in rule_ids
    assert "BPG-RENOVATE-BROAD-PROD-AUTOMERGE" in rule_ids
    assert "BPG-RENOVATE-UPDATE-LIMITS" in rule_ids
    assert "BPG-RENOVATE-MISSING-GROUPS" in rule_ids
    assert "BPG-RENOVATE-SECURITY-DISABLED" in rule_ids


def test_renovate_dev_automerge_with_soak_and_limits_avoids_high_findings(tmp_path):
    write(
        tmp_path / "renovate.json",
        """
        {
          "minimumReleaseAge": "3 days",
          "prConcurrentLimit": 5,
          "prHourlyLimit": 2,
          "packageRules": [
            {
              "matchDepTypes": ["devDependencies"],
              "matchUpdateTypes": ["patch"],
              "groupName": "dev patches",
              "automerge": true
            }
          ]
        }
        """,
    )

    result = audit_repo(tmp_path)

    assert {finding.severity for finding in result.findings} <= {"low"}
    assert "BPG-RENOVATE-AUTOMERGE-SOAK" not in {
        finding.rule_id for finding in result.findings
    }
