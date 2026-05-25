from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}
SEVERITIES = tuple(SEVERITY_RANK)


@dataclass(frozen=True)
class ConfigFile:
    path: Path
    relative_path: str
    kind: str
    data: Any
    text: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    severity: str
    message: str
    path: str
    remediation: str
    line: int | None = None
    evidence: str | None = None

    @property
    def rank(self) -> int:
        return SEVERITY_RANK[self.severity]

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "rule_id": self.rule_id,
            "title": self.title,
            "severity": self.severity,
            "message": self.message,
            "path": self.path,
            "remediation": self.remediation,
        }
        if self.line is not None:
            payload["line"] = self.line
        if self.evidence:
            payload["evidence"] = self.evidence
        return payload


@dataclass
class AuditResult:
    root: Path
    findings: list[Finding] = field(default_factory=list)
    scanned_files: list[str] = field(default_factory=list)

    @property
    def max_severity(self) -> str | None:
        if not self.findings:
            return None
        return max(self.findings, key=lambda finding: finding.rank).severity

    def sorted_findings(self) -> list[Finding]:
        return sorted(
            self.findings,
            key=lambda finding: (
                -finding.rank,
                finding.path,
                finding.line or 0,
                finding.rule_id,
            ),
        )
