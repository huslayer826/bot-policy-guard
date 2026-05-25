from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from .models import ConfigFile, Finding
from .parsers import get_workflow_on, line_for

RELEASE_SOAK_KEYS = ("minimumReleaseAge", "stabilityDays")
UPDATE_LIMIT_KEYS = ("prConcurrentLimit", "branchConcurrentLimit", "prHourlyLimit")
DEV_DEP_TYPES = {"dev", "development", "devdependencies", "dev-dependencies"}
DANGEROUS_WRITE_SCOPES = {
    "actions",
    "attestations",
    "checks",
    "contents",
    "deployments",
    "id-token",
    "packages",
    "pages",
    "security-events",
    "statuses",
}
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def audit_renovate(config: ConfigFile) -> list[Finding]:
    data = config.data
    if not isinstance(data, dict):
        return [
            _finding(
                "BPG-CONFIG-SHAPE",
                "Renovate config is not an object",
                "high",
                config,
                "Renovate configuration should parse to a JSON object.",
                "Fix the Renovate file so it contains a single object at the top level.",
            )
        ]

    findings: list[Finding] = []
    global_has_soak = _has_release_soak(data)

    if _truthy(data.get("automerge")):
        if not global_has_soak:
            findings.append(
                _finding(
                    "BPG-RENOVATE-AUTOMERGE-SOAK",
                    "Renovate automerge has no release-age soak",
                    "high",
                    config,
                    "Global Renovate automerge can merge newly published versions before the ecosystem has had time to detect bad releases.",
                    "Add minimumReleaseAge, such as \"3 days\", and keep internal checks enabled before allowing automerge.",
                    "automerge",
                )
            )
        findings.append(
            _finding(
                "BPG-RENOVATE-BROAD-PROD-AUTOMERGE",
                "Renovate production automerge is overly broad",
                "high",
                config,
                "Global automerge applies broadly and can include production dependency updates.",
                "Move automerge into narrow packageRules for low-risk dev dependencies or patch-only updates after a release-age soak.",
                "automerge",
            )
        )

    for index, rule in enumerate(_as_list(data.get("packageRules"))):
        if not isinstance(rule, dict) or not _truthy(rule.get("automerge")):
            continue
        if not (_has_release_soak(rule) or global_has_soak):
            findings.append(
                _finding(
                    "BPG-RENOVATE-AUTOMERGE-SOAK",
                    "Renovate automerge has no release-age soak",
                    "high",
                    config,
                    f"packageRules[{index}] enables automerge without a minimum release age.",
                    "Add minimumReleaseAge to the rule or to the top-level Renovate config.",
                    "automerge",
                    evidence=f"packageRules[{index}]",
                )
            )
        if _is_broad_production_automerge(rule):
            findings.append(
                _finding(
                    "BPG-RENOVATE-BROAD-PROD-AUTOMERGE",
                    "Renovate production automerge is overly broad",
                    "high",
                    config,
                    f"packageRules[{index}] automerge is not constrained away from production dependencies.",
                    "Limit automerge to devDependencies, specific package names, trusted datasources, or patch-only update types.",
                    "automerge",
                    evidence=f"packageRules[{index}]",
                )
            )

    if not any(key in data for key in UPDATE_LIMIT_KEYS):
        findings.append(
            _finding(
                "BPG-RENOVATE-UPDATE-LIMITS",
                "Renovate update limits are missing",
                "medium",
                config,
                "Renovate has no explicit PR, branch, or hourly update limit.",
                "Set prConcurrentLimit and prHourlyLimit to match reviewer capacity.",
                None,
            )
        )

    if not _has_renovate_grouping(data):
        findings.append(
            _finding(
                "BPG-RENOVATE-MISSING-GROUPS",
                "Renovate grouping is missing",
                "low",
                config,
                "Renovate config does not define package grouping, which can create noisy single-package PR streams.",
                "Add packageRules with groupName/groupSlug for related low-risk updates.",
                "packageRules",
            )
        )

    if _renovate_security_disabled(data):
        findings.append(
            _finding(
                "BPG-RENOVATE-SECURITY-DISABLED",
                "Renovate vulnerability handling is disabled",
                "high",
                config,
                "The Renovate config appears to disable vulnerability alert handling.",
                "Enable vulnerabilityAlerts and OSV vulnerability visibility unless another audited process covers security updates.",
                "vulnerability",
            )
        )

    return findings


def audit_dependabot(config: ConfigFile, automerge_workflows: bool) -> list[Finding]:
    data = config.data
    if not isinstance(data, dict):
        return [
            _finding(
                "BPG-CONFIG-SHAPE",
                "Dependabot config is not an object",
                "high",
                config,
                "Dependabot configuration should parse to a YAML object.",
                "Fix .github/dependabot.yml so it contains a top-level object with version and updates.",
            )
        ]

    findings: list[Finding] = []
    updates = data.get("updates")
    if not isinstance(updates, list):
        return [
            _finding(
                "BPG-DEPENDABOT-UPDATES-MISSING",
                "Dependabot updates list is missing",
                "medium",
                config,
                "Dependabot has no updates list to constrain dependency automation behavior.",
                "Add explicit updates entries for every managed ecosystem.",
                "updates",
            )
        ]

    for index, update in enumerate(updates):
        if not isinstance(update, dict):
            continue
        ecosystem = str(update.get("package-ecosystem", "unknown"))
        descriptor = f"{ecosystem} entry at updates[{index}]"

        if "open-pull-requests-limit" not in update:
            findings.append(
                _finding(
                    "BPG-DEPENDABOT-UPDATE-LIMITS",
                    "Dependabot update limit is missing",
                    "medium",
                    config,
                    f"{descriptor} does not set open-pull-requests-limit.",
                    "Set open-pull-requests-limit to a value your team can review quickly.",
                    "open-pull-requests-limit",
                    evidence=f"updates[{index}]",
                )
            )
        elif update.get("open-pull-requests-limit") == 0:
            findings.append(
                _finding(
                    "BPG-DEPENDABOT-UPDATES-DISABLED",
                    "Dependabot updates are disabled",
                    "medium",
                    config,
                    f"{descriptor} sets open-pull-requests-limit to 0.",
                    "Use a small nonzero limit, and verify GitHub security updates are enabled in repository settings.",
                    "open-pull-requests-limit",
                    evidence=f"updates[{index}]",
                )
            )

        if not update.get("groups"):
            rule_id = (
                "BPG-DEPENDABOT-GHA-NOT-GROUPED"
                if ecosystem == "github-actions"
                else "BPG-DEPENDABOT-MISSING-GROUPS"
            )
            severity = "medium" if ecosystem == "github-actions" else "low"
            title = (
                "GitHub Actions Dependabot updates are not grouped"
                if ecosystem == "github-actions"
                else "Dependabot grouping is missing"
            )
            findings.append(
                _finding(
                    rule_id,
                    title,
                    severity,
                    config,
                    f"{descriptor} does not define groups.",
                    "Add Dependabot groups for related minor and patch updates.",
                    "groups",
                    evidence=f"updates[{index}]",
                )
            )

        if automerge_workflows and not update.get("cooldown"):
            findings.append(
                _finding(
                    "BPG-DEPENDABOT-AUTOMERGE-SOAK",
                    "Dependabot automerge has no release-age soak",
                    "high",
                    config,
                    f"{descriptor} may be auto-merged by workflow automation without Dependabot cooldown.",
                    "Add a Dependabot cooldown window or remove dependency-bot automerge.",
                    "cooldown",
                    evidence=f"updates[{index}]",
                )
            )

        if _has_broad_ignore(update):
            findings.append(
                _finding(
                    "BPG-DEPENDABOT-BROAD-IGNORE",
                    "Dependabot ignore rule is overly broad",
                    "medium",
                    config,
                    f"{descriptor} ignores every dependency.",
                    "Replace wildcard ignore rules with specific package names and documented exceptions.",
                    "ignore",
                    evidence=f"updates[{index}]",
                )
            )

    if _recursive_false_key(data, {"security-updates", "enable-security-updates", "vulnerability-alerts"}):
        findings.append(
            _finding(
                "BPG-DEPENDABOT-SECURITY-DISABLED",
                "Dependabot security updates appear disabled",
                "high",
                config,
                "A security or vulnerability update setting is explicitly false.",
                "Enable security updates and vulnerability alerts unless another audited control owns them.",
                "security",
            )
        )

    return findings


def audit_workflow(
    config: ConfigFile,
    dependency_bot_present: bool,
    gha_grouped: bool,
) -> list[Finding]:
    data = config.data
    if not isinstance(data, dict):
        return [
            _finding(
                "BPG-CONFIG-SHAPE",
                "Workflow config is not an object",
                "high",
                config,
                "GitHub workflow YAML should parse to a top-level object.",
                "Fix the workflow YAML syntax.",
            )
        ]

    findings: list[Finding] = []
    action_uses = _workflow_action_uses(data)
    for action_ref in action_uses:
        if _is_unpinned_action(action_ref):
            findings.append(
                _finding(
                    "BPG-GHA-ACTION-NOT-PINNED",
                    "GitHub Action is not pinned to a full commit SHA",
                    "medium",
                    config,
                    f"Workflow uses {action_ref!r}, which is tag or branch pinned.",
                    "Pin third-party and first-party actions to full commit SHAs; let Dependabot or Renovate open grouped updates.",
                    action_ref,
                    evidence=action_ref,
                )
            )

    if action_uses and not gha_grouped:
        findings.append(
            _finding(
                "BPG-GHA-UPDATES-NOT-GROUPED",
                "GitHub Actions updates are not grouped",
                "medium",
                config,
                "Workflow actions are present, but no Dependabot or Renovate GitHub Actions grouping was found.",
                "Configure Dependabot groups for package-ecosystem github-actions or Renovate packageRules with matchManagers github-actions.",
                "uses:",
            )
        )

    if dependency_bot_present and _workflow_mentions_dependency_bot(config):
        findings.extend(_audit_permissions(config, data))

    return findings


def workflow_has_automerge(config: ConfigFile) -> bool:
    text = config.text.lower()
    return any(
        token in text
        for token in (
            "automerge",
            "auto-merge",
            "gh pr merge",
            "peter-evans/enable-pull-request-automerge",
            "pascalgn/automerge-action",
            "fastify/github-action-merge-dependabot",
            "dependabot/fetch-metadata",
        )
    )


def workflow_mentions_dependency_bot(config: ConfigFile) -> bool:
    return _workflow_mentions_dependency_bot(config)


def dependabot_has_github_actions_group(configs: Iterable[ConfigFile]) -> bool:
    for config in configs:
        if config.kind != "dependabot" or not isinstance(config.data, dict):
            continue
        for update in _as_list(config.data.get("updates")):
            if (
                isinstance(update, dict)
                and update.get("package-ecosystem") == "github-actions"
                and update.get("groups")
            ):
                return True
    return False


def renovate_has_github_actions_group(configs: Iterable[ConfigFile]) -> bool:
    for config in configs:
        if config.kind != "renovate" or not isinstance(config.data, dict):
            continue
        for rule in _as_list(config.data.get("packageRules")):
            if not isinstance(rule, dict):
                continue
            managers = {str(item).lower() for item in _as_list(rule.get("matchManagers"))}
            if "github-actions" in managers and (rule.get("groupName") or rule.get("groupSlug")):
                return True
    return False


def has_dependency_bot_config(configs: Iterable[ConfigFile]) -> bool:
    return any(config.kind in {"dependabot", "renovate"} for config in configs)


def _audit_permissions(config: ConfigFile, data: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if "permissions" not in data:
        findings.append(
            _finding(
                "BPG-WORKFLOW-PERMISSIONS-BROAD",
                "Dependency bot workflow token permissions are implicit",
                "medium",
                config,
                "Workflow does not set top-level permissions while referencing dependency bot automation.",
                "Set explicit least-privilege permissions at the workflow or job level, such as contents: read and pull-requests: write only where required.",
                "permissions",
            )
        )
    else:
        findings.extend(_permission_findings(config, data.get("permissions"), "workflow"))

    jobs = data.get("jobs")
    if isinstance(jobs, dict):
        for job_name, job in jobs.items():
            if isinstance(job, dict) and "permissions" in job:
                findings.extend(
                    _permission_findings(config, job.get("permissions"), f"job {job_name}")
                )
    return findings


def _permission_findings(config: ConfigFile, permissions: Any, scope_name: str) -> list[Finding]:
    if permissions == "write-all":
        return [
            _finding(
                "BPG-WORKFLOW-PERMISSIONS-BROAD",
                "Dependency bot workflow token permissions are write-all",
                "high",
                config,
                f"{scope_name} permissions use write-all.",
                "Replace write-all with the narrow scopes the workflow actually needs.",
                "permissions",
                evidence=str(permissions),
            )
        ]
    if isinstance(permissions, dict):
        writes = sorted(
            scope
            for scope, value in permissions.items()
            if str(value).lower() == "write" and str(scope) in DANGEROUS_WRITE_SCOPES
        )
        if writes:
            return [
                _finding(
                    "BPG-WORKFLOW-PERMISSIONS-BROAD",
                    "Dependency bot workflow token permissions include broad writes",
                    "medium",
                    config,
                    f"{scope_name} grants write permission to: {', '.join(writes)}.",
                    "Use read permissions by default and isolate any required write permission to a dedicated job.",
                    "permissions",
                    evidence=", ".join(writes),
                )
            ]
    return []


def _workflow_action_uses(data: dict[str, Any]) -> list[str]:
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        return []
    uses: list[str] = []
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        job_uses = job.get("uses")
        if isinstance(job_uses, str):
            uses.append(job_uses)
        steps = job.get("steps")
        if isinstance(steps, list):
            for step in steps:
                if isinstance(step, dict) and isinstance(step.get("uses"), str):
                    uses.append(step["uses"])
    return uses


def _is_unpinned_action(action_ref: str) -> bool:
    if action_ref.startswith(("./", "../", "docker://")):
        return False
    if "@" not in action_ref:
        return True
    _, ref = action_ref.rsplit("@", 1)
    return SHA_RE.fullmatch(ref) is None


def _workflow_mentions_dependency_bot(config: ConfigFile) -> bool:
    text = config.text.lower()
    if any(token in text for token in ("dependabot", "renovate", "automerge", "auto-merge")):
        return True
    on_value = get_workflow_on(config.data)
    if isinstance(on_value, dict):
        return "pull_request_target" in on_value
    if isinstance(on_value, list):
        return "pull_request_target" in on_value
    return on_value == "pull_request_target"


def _is_broad_production_automerge(rule: dict[str, Any]) -> bool:
    dep_types = {str(item).lower() for item in _as_list(rule.get("matchDepTypes"))}
    if dep_types and dep_types <= DEV_DEP_TYPES:
        return False

    narrow_keys = (
        "matchPackageNames",
        "matchPackagePatterns",
        "matchDatasources",
        "matchManagers",
        "matchCategories",
    )
    if any(rule.get(key) for key in narrow_keys) and not {"dependencies", "prod", "production"} & dep_types:
        update_types = {str(item).lower() for item in _as_list(rule.get("matchUpdateTypes"))}
        return not update_types <= {"patch", "pin", "digest"}
    return True


def _has_release_soak(config: dict[str, Any]) -> bool:
    for key in RELEASE_SOAK_KEYS:
        value = config.get(key)
        if value not in (None, False, 0, "0", "0 days", "0 day", ""):
            return True
    return False


def _has_renovate_grouping(data: dict[str, Any]) -> bool:
    for item in _as_list(data.get("extends")):
        if isinstance(item, str) and ("group:" in item or ":group" in item):
            return True
    return any(
        isinstance(rule, dict) and (rule.get("groupName") or rule.get("groupSlug"))
        for rule in _as_list(data.get("packageRules"))
    )


def _renovate_security_disabled(data: dict[str, Any]) -> bool:
    vulnerability_alerts = data.get("vulnerabilityAlerts")
    if vulnerability_alerts is False:
        return True
    if isinstance(vulnerability_alerts, dict) and vulnerability_alerts.get("enabled") is False:
        return True
    return data.get("osvVulnerabilityAlerts") is False


def _has_broad_ignore(update: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict) and item.get("dependency-name") in {"*", "**"}
        for item in _as_list(update.get("ignore"))
    )


def _recursive_false_key(value: Any, keys: set[str]) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in keys and child is False:
                return True
            if _recursive_false_key(child, keys):
                return True
    elif isinstance(value, list):
        return any(_recursive_false_key(child, keys) for child in value)
    return False


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"true", "yes", "on", "1"}
    return bool(value)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _finding(
    rule_id: str,
    title: str,
    severity: str,
    config: ConfigFile,
    message: str,
    remediation: str,
    needle: str | None = None,
    evidence: str | None = None,
) -> Finding:
    return Finding(
        rule_id=rule_id,
        title=title,
        severity=severity,
        message=message,
        path=config.relative_path,
        line=line_for(config.text, needle),
        remediation=remediation,
        evidence=evidence,
    )
