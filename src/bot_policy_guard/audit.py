from __future__ import annotations

from pathlib import Path

from .models import AuditResult, Finding
from .parsers import discover
from .rules import (
    audit_dependabot,
    audit_renovate,
    audit_workflow,
    dependabot_has_github_actions_group,
    has_dependency_bot_config,
    renovate_has_github_actions_group,
    workflow_has_automerge,
)


def audit_repo(root: str | Path) -> AuditResult:
    repo_root = Path(root).resolve()
    configs, parse_errors = discover(repo_root)
    result = AuditResult(
        root=repo_root,
        scanned_files=sorted(config.relative_path for config in configs),
    )

    for error in parse_errors:
        path = error.split(":", 1)[0]
        result.findings.append(
            Finding(
                rule_id="BPG-CONFIG-PARSE",
                title="Configuration file could not be parsed",
                severity="high",
                message=error,
                path=path,
                remediation="Fix the syntax error before relying on dependency automation policy checks.",
            )
        )

    automerge_workflows = any(
        workflow_has_automerge(config) for config in configs if config.kind == "workflow"
    )
    dependency_bot_present = has_dependency_bot_config(configs)
    gha_grouped = dependabot_has_github_actions_group(configs) or renovate_has_github_actions_group(
        configs
    )

    for config in configs:
        if config.kind == "renovate":
            result.findings.extend(audit_renovate(config))
        elif config.kind == "dependabot":
            result.findings.extend(audit_dependabot(config, automerge_workflows))
        elif config.kind == "workflow":
            result.findings.extend(audit_workflow(config, dependency_bot_present, gha_grouped))

    return result
