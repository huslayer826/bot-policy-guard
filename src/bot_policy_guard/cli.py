from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .audit import audit_repo
from .models import SEVERITIES
from .renderers import exceeds_threshold, render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bot-policy-guard",
        description="Audit Renovate, Dependabot, and GitHub Actions dependency automation policy.",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Repository path to audit. Defaults to the current directory.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown", "sarif"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--fail-on",
        choices=SEVERITIES,
        default=None,
        help="Exit with status 1 when a finding at this severity or higher is present.",
    )
    parser.add_argument(
        "--output",
        help="Write report to this file instead of stdout.",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = audit_repo(args.repo)
    rendered = render(result, args.format)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    return 1 if exceeds_threshold(result, args.fail_on) else 0


def main(argv: Sequence[str] | None = None) -> int:
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
