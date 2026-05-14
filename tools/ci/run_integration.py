#!/usr/bin/env python3
"""Run a credential-free Ansible integration case and assert its evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from _config import load_ci_config, select_case


def run(command: list[str], cwd: Path) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def read_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return raw


def ansible_command(case: dict[str, Any], *extra: str) -> list[str]:
    command = [
        "ansible-playbook",
        "-i",
        case["inventory"],
        case["playbook"],
        *extra,
    ]
    extra_vars_file = case.get("extra_vars_file")
    if extra_vars_file:
        command.extend(["-e", f"@{extra_vars_file}"])
    return command


def assert_case_outputs(repo_root: Path, case: dict[str, Any]) -> None:
    evidence = repo_root / case["expected_evidence"]
    if not evidence.is_file():
        raise FileNotFoundError(f"expected integration evidence missing: {evidence}")

    payload = read_json(evidence)
    if payload.get("framework") != "ansible-framework-template":
        raise ValueError(f"{evidence} framework mismatch")
    if payload.get("profile") != case["expected_profile"]:
        raise ValueError(f"{evidence} profile mismatch")
    if payload.get("inventory_hostname") != case["expected_host"]:
        raise ValueError(f"{evidence} inventory host mismatch")
    if payload.get("become") is not False:
        raise ValueError(f"{evidence} must record become=false for the reference case")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to cwd.")
    parser.add_argument("--config", default="tools/ci/config.toml", help="Path to CI config.")
    parser.add_argument("--case", default=None, help="Integration case name.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    config = load_ci_config(repo_root, args.config)
    case = select_case(config, args.case)

    run(ansible_command(case, "--syntax-check"), repo_root)
    run(ansible_command(case, "--check"), repo_root)
    run(ansible_command(case), repo_root)
    assert_case_outputs(repo_root, case)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
    except Exception as exc:
        print(f"run_integration.py: {exc}", file=sys.stderr)
        sys.exit(1)

