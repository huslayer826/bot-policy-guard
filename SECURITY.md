# Security Policy

## Supported Versions

The project is pre-1.0. Security fixes target the latest released version and
the default branch.

## Reporting a Vulnerability

Please do not open a public issue for sensitive reports. Email the maintainer
address listed on the package index or use GitHub private vulnerability
reporting when available.

Include:

- Affected version or commit.
- Reproduction steps.
- Impact and affected files.
- Any suggested mitigation.

## Scope

In scope:

- Incorrect high-risk findings caused by parser or rule bugs.
- CLI behavior that can overwrite unexpected files.
- Supply-chain concerns in runtime dependencies.

Out of scope:

- Findings that require live GitHub repository settings not present in files.
- False positives where the documented remediation covers the tradeoff.
