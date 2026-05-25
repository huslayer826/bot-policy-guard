from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from . import __version__
from .models import SEVERITY_RANK, AuditResult, Finding


def render(result: AuditResult, output_format: str) -> str:
    if output_format == "json":
        return render_json(result)
    if output_format == "markdown":
        return render_markdown(result)
    if output_format == "sarif":
        return render_sarif(result)
    return render_text(result)


def render_text(result: AuditResult) -> str:
    lines = [
        "Bot Policy Guard audit",
        f"Target: {result.root}",
        f"Scanned files: {len(result.scanned_files)}",
        f"Findings: {len(result.findings)}",
    ]
    if not result.findings:
        lines.append("")
        lines.append("No findings.")
        return "\n".join(lines) + "\n"

    for finding in result.sorted_findings():
        location = finding.path
        if finding.line:
            location += f":{finding.line}"
        lines.extend(
            [
                "",
                f"[{finding.severity.upper()}] {finding.rule_id} - {finding.title}",
                f"Location: {location}",
                f"Message: {finding.message}",
                f"Remediation: {finding.remediation}",
            ]
        )
        if finding.evidence:
            lines.append(f"Evidence: {finding.evidence}")
    return "\n".join(lines) + "\n"


def render_json(result: AuditResult) -> str:
    payload: dict[str, Any] = {
        "tool": "bot-policy-guard",
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": str(result.root),
        "scanned_files": result.scanned_files,
        "summary": {
            "findings": len(result.findings),
            "max_severity": result.max_severity,
        },
        "findings": [finding.to_dict() for finding in result.sorted_findings()],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_markdown(result: AuditResult) -> str:
    lines = [
        "# Bot Policy Guard Audit",
        "",
        f"- Target: `{result.root}`",
        f"- Scanned files: {len(result.scanned_files)}",
        f"- Findings: {len(result.findings)}",
        "",
    ]
    if not result.findings:
        lines.append("No findings.")
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "| Severity | Rule | Location | Finding |",
            "| --- | --- | --- | --- |",
        ]
    )
    for finding in result.sorted_findings():
        location = finding.path if finding.line is None else f"{finding.path}:{finding.line}"
        message = _escape_markdown(f"{finding.message} Remediation: {finding.remediation}")
        lines.append(
            f"| {finding.severity.upper()} | `{finding.rule_id}` | `{location}` | {message} |"
        )
    return "\n".join(lines) + "\n"


def render_sarif(result: AuditResult) -> str:
    rules_by_id: dict[str, Finding] = {}
    for finding in result.sorted_findings():
        rules_by_id.setdefault(finding.rule_id, finding)

    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "bot-policy-guard",
                        "informationUri": "https://github.com/huslayer826/bot-policy-guard",
                        "semanticVersion": __version__,
                        "rules": [_sarif_rule(rule) for rule in rules_by_id.values()],
                    }
                },
                "results": [_sarif_result(finding) for finding in result.sorted_findings()],
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _sarif_rule(finding: Finding) -> dict[str, Any]:
    return {
        "id": finding.rule_id,
        "name": finding.title,
        "shortDescription": {"text": finding.title},
        "fullDescription": {"text": finding.message},
        "help": {"text": finding.remediation},
        "properties": {"security-severity": str(_sarif_security_score(finding.severity))},
    }


def _sarif_result(finding: Finding) -> dict[str, Any]:
    region: dict[str, int] = {}
    if finding.line:
        region["startLine"] = finding.line
    return {
        "ruleId": finding.rule_id,
        "level": {"high": "error", "medium": "warning", "low": "note"}[finding.severity],
        "message": {"text": f"{finding.message} Remediation: {finding.remediation}"},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": finding.path},
                    "region": region,
                }
            }
        ],
        "partialFingerprints": {
            "primaryLocationLineHash": f"{finding.rule_id}:{finding.path}:{finding.line or 0}"
        },
    }


def _sarif_security_score(severity: str) -> float:
    return {"low": 3.0, "medium": 6.0, "high": 8.5}[severity]


def _escape_markdown(value: str) -> str:
    return value.replace("|", "\\|")


def exceeds_threshold(result: AuditResult, threshold: str | None) -> bool:
    if threshold is None:
        return False
    rank = SEVERITY_RANK[threshold]
    return any(finding.rank >= rank for finding in result.findings)
