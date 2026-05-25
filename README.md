# bot-policy-guard

[![CI](https://github.com/huslayer826/bot-policy-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/huslayer826/bot-policy-guard/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/bot-policy-guard.svg)](https://pypi.org/project/bot-policy-guard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

`bot-policy-guard` is a dependency-light Python CLI that audits Renovate,
Dependabot, and GitHub Actions configuration for risky dependency automation
defaults.

Dependency bots are useful, but a small policy mistake can turn them into a
high-volume auto-merge path for fresh upstream releases, unpinned workflow
actions, or overly broad GitHub token permissions. This tool gives maintainers
a fast local check before those settings become production risk.

## Install

```bash
pip install bot-policy-guard
```

For local development:

```bash
git clone https://github.com/huslayer826/bot-policy-guard.git
cd bot-policy-guard
python -m pip install -e ".[dev]"
```

## Quickstart

```bash
bot-policy-guard /path/to/repo
bot-policy-guard . --format json --output bot-policy-report.json
bot-policy-guard . --format sarif --output bot-policy-report.sarif --fail-on medium
```

## What It Checks

- Renovate automerge without `minimumReleaseAge` or similar release-age soak.
- Global or broad production dependency automerge rules.
- Missing Renovate and Dependabot update limits.
- Missing Renovate or Dependabot grouping.
- Detectable disabled vulnerability or security update settings.
- GitHub Actions references that are tag or branch pinned instead of SHA pinned.
- GitHub Actions dependency update configuration that is not grouped.
- Overbroad workflow token permissions when dependency bot workflows are present.

Each finding includes a rule ID, severity, location, evidence when available,
and remediation guidance.

## Examples

Text output:

```text
$ bot-policy-guard .
Bot Policy Guard audit
Target: /work/service
Scanned files: 3
Findings: 4

[HIGH] BPG-RENOVATE-AUTOMERGE-SOAK - Renovate automerge has no release-age soak
Location: renovate.json:3
Message: Global Renovate automerge can merge newly published versions before the ecosystem has had time to detect bad releases.
Remediation: Add minimumReleaseAge, such as "3 days", and keep internal checks enabled before allowing automerge.
```

Markdown report:

```bash
bot-policy-guard . --format markdown --output dependency-bot-policy.md
```

SARIF for code scanning:

```bash
bot-policy-guard . --format sarif --output bot-policy-guard.sarif --fail-on high
```

## Supported Files

The CLI discovers these files under the target repository path:

- `renovate.json`
- `.github/renovate.json`
- `renovate.json5` with comments and trailing commas supported on a best-effort basis
- `.github/dependabot.yml`
- `.github/workflows/*.yml`
- `.github/workflows/*.yaml`

## Exit Codes

- `0`: audit completed and no `--fail-on` threshold was met.
- `1`: at least one finding matched or exceeded the `--fail-on` severity.
- `2`: reserved for command-line usage errors from `argparse`.

## Limitations

`bot-policy-guard` is an offline static analyzer. It does not call GitHub,
Renovate, Dependabot, package registries, or vulnerability services. Some
security update settings live in repository or organization settings and cannot
be confirmed from files alone. JSON5 support is intentionally lightweight and
covers common Renovate patterns, not the full JSON5 specification.

The tool reports policy risk, not exploitability. Review findings in the
context of your repository, branch protections, required checks, and release
process.

## License Notes

This project is MIT licensed. It does not import Renovate or Dependabot code and
does not depend on GPL or AGPL packages. Runtime dependencies are intentionally
small; PyYAML is used for YAML parsing and is MIT licensed.
