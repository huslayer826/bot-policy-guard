# Setup

## Requirements

- Python 3.10 or newer.
- `pip` for installation.
- No network access is required when running scans.

## Developer Setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Build

```bash
python -m build
```

The build creates source and wheel distributions under `dist/`. Do not commit
generated distribution artifacts.

## Release Preparation

1. Update `CHANGELOG.md`.
2. Confirm `pytest` and `ruff check .` pass.
3. Create a GitHub release.
4. Use the release workflow after configuring PyPI trusted publishing for the
   repository.
