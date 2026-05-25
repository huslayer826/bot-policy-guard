from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from .models import ConfigFile

RENOVATE_PATHS = (
    "renovate.json",
    ".github/renovate.json",
    "renovate.json5",
)
DEPENDABOT_PATH = ".github/dependabot.yml"
WORKFLOW_GLOBS = (".github/workflows/*.yml", ".github/workflows/*.yaml")


def discover(root: Path) -> tuple[list[ConfigFile], list[str]]:
    root = root.resolve()
    configs: list[ConfigFile] = []
    errors: list[str] = []

    for relative in RENOVATE_PATHS:
        path = root / relative
        if path.exists():
            _load_config(path, root, "renovate", configs, errors)

    dependabot = root / DEPENDABOT_PATH
    if dependabot.exists():
        _load_config(dependabot, root, "dependabot", configs, errors)

    seen: set[Path] = set()
    for pattern in WORKFLOW_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path not in seen and path.is_file():
                seen.add(path)
                _load_config(path, root, "workflow", configs, errors)

    return configs, errors


def _load_config(
    path: Path,
    root: Path,
    kind: str,
    configs: list[ConfigFile],
    errors: list[str],
) -> None:
    try:
        text = path.read_text(encoding="utf-8")
        data = load_jsonish(text) if kind == "renovate" else load_yaml(text)
        configs.append(
            ConfigFile(
                path=path,
                relative_path=path.relative_to(root).as_posix(),
                kind=kind,
                data=data,
                text=text,
            )
        )
    except Exception as exc:  # noqa: BLE001 - parser errors are surfaced as audit findings.
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            relative = path.as_posix()
        errors.append(f"{relative}: {exc}")


def load_yaml(text: str) -> Any:
    loaded = yaml.safe_load(text)
    return {} if loaded is None else loaded


def load_jsonish(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(to_json(text))


def to_json(text: str) -> str:
    without_comments = _remove_json5_comments(text)
    without_trailing = re.sub(r",\s*([}\]])", r"\1", without_comments)
    with_quoted_keys = re.sub(
        r"(?<=[{,])(\s*)([A-Za-z_$][A-Za-z0-9_$]*)(\s*):",
        r'\1"\2"\3:',
        without_trailing,
    )
    return _normalize_single_quoted_strings(with_quoted_keys)


def _remove_json5_comments(text: str) -> str:
    output: list[str] = []
    index = 0
    in_string: str | None = None
    escaped = False
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = None
            index += 1
            continue

        if char in {"'", '"'}:
            in_string = char
            output.append(char)
            index += 1
            continue

        if char == "/" and next_char == "/":
            while index < len(text) and text[index] not in "\r\n":
                index += 1
            continue

        if char == "/" and next_char == "*":
            index += 2
            while index + 1 < len(text) and not (text[index] == "*" and text[index + 1] == "/"):
                index += 1
            index += 2
            continue

        output.append(char)
        index += 1

    return "".join(output)


def _normalize_single_quoted_strings(text: str) -> str:
    output: list[str] = []
    index = 0
    in_double = False
    escaped = False

    while index < len(text):
        char = text[index]
        if in_double:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_double = False
            index += 1
            continue

        if char == '"':
            in_double = True
            output.append(char)
            index += 1
            continue

        if char == "'":
            index += 1
            value: list[str] = []
            escaped_single = False
            while index < len(text):
                inner = text[index]
                if escaped_single:
                    value.append(inner)
                    escaped_single = False
                elif inner == "\\":
                    escaped_single = True
                elif inner == "'":
                    break
                else:
                    value.append(inner)
                index += 1
            output.append(json.dumps("".join(value)))
            index += 1
            continue

        output.append(char)
        index += 1

    return "".join(output)


def line_for(text: str, needle: str | None = None) -> int | None:
    if not needle:
        return None
    for number, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return number
    return None


def get_workflow_on(data: Any) -> Any:
    if not isinstance(data, dict):
        return None
    if "on" in data:
        return data["on"]
    return data.get(True)
