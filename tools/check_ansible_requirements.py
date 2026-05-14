#!/usr/bin/env python3
"""Validate ansible/requirements.yml uses exact, reviewable pins."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised in clean systems
    yaml = None


SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise SystemExit(f"ansible-requirements: {message}")


def require_yaml() -> Any:
    if yaml is None:
        fail("PyYAML is required. Install with `pip install pyyaml`.")
    return yaml


def validate_version(entry: dict[str, Any], kind: str, index: int) -> list[str]:
    name = entry.get("name") or entry.get("src") or f"{kind}[{index}]"
    version = entry.get("version")
    errors: list[str] = []
    if not isinstance(version, str) or not version.strip():
        errors.append(f"{kind}[{index}] {name!r} must declare a non-empty version")
        return errors

    value = version.strip()
    scm = str(entry.get("scm", "")).strip().lower()
    if scm == "git":
        if not SHA_RE.match(value):
            errors.append(
                f"{kind}[{index}] {name!r} uses git and must pin version to a 40-character commit SHA"
            )
        return errors

    if any(token in value for token in ("<", ">", "~", "*", ",")):
        errors.append(f"{kind}[{index}] {name!r} must not use a version range: {value!r}")
    elif not SEMVER_RE.match(value):
        errors.append(f"{kind}[{index}] {name!r} must use an exact semantic version: {value!r}")
    return errors


def validate_requirements(path: Path) -> list[str]:
    yaml_mod = require_yaml()
    raw = yaml_mod.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        return ["requirements root must be a mapping"]

    errors: list[str] = []
    allowed = {"collections", "roles"}
    extra = sorted(set(raw) - allowed)
    if extra:
        errors.append(f"requirements root has unsupported keys: {extra}")

    for kind in ("collections", "roles"):
        entries = raw.get(kind, [])
        if entries is None:
            entries = []
        if not isinstance(entries, list):
            errors.append(f"{kind} must be a list")
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"{kind}[{index}] must be a mapping")
                continue
            errors.extend(validate_version(entry, kind, index))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "path",
        nargs="?",
        default="ansible/requirements.yml",
        help="Requirements file to validate.",
    )
    args = parser.parse_args()
    path = Path(args.path)
    if not path.is_file():
        fail(f"requirements file not found: {path}")

    errors = validate_requirements(path)
    if errors:
        print("ansible requirements check failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"ansible requirements pins ok: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

