# Contributing

Thanks for helping improve `bot-policy-guard`.

## Local Setup

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Development Guidelines

- Keep the runtime dependency set small.
- Do not import Renovate, Dependabot, or license-incompatible code.
- Prefer deterministic offline checks over network-backed behavior.
- Add tests for new rules, output formats, and CLI exit behavior.
- Include clear remediation text with every finding.

## Pull Requests

Open a pull request with:

- A short problem statement.
- The rule IDs or CLI behavior changed.
- Tests that cover the change.
- Any known false-positive or false-negative tradeoffs.

## Rule Design

Rules should be explainable from repository files alone. If a rule needs
repository settings that are not available offline, document that limitation in
the finding remediation or README.
