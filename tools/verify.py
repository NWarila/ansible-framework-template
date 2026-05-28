#!/usr/bin/env python3
"""Cross-platform verification entrypoint for the Ansible framework template."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from ci._config import load_ci_config, select_case


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
YAMLLINT_CONFIG = (
    "{ extends: relaxed, rules: { line-length: disable, document-start: disable, "
    "comments: disable, truthy: {check-keys: false} } }"
)

Step = Callable[[], None]


def run(args: list[str], *, input_text: str | None = None) -> None:
    print("+ " + " ".join(args), flush=True)
    try:
        completed = subprocess.run(
            args,
            cwd=ROOT,
            input=input_text,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"missing executable: {args[0]}") from exc
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def capture(args: list[str], *, input_text: str | None = None) -> str:
    print("+ " + " ".join(args), flush=True)
    try:
        completed = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            input=input_text,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"missing executable: {args[0]}") from exc
    if completed.returncode != 0:
        sys.stdout.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode)
    return completed.stdout


def install(package: str) -> None:
    if os.environ.get("CI", "").lower() != "true":
        print(f"local run: not installing {package}; expecting it to be available", flush=True)
        return
    run([PYTHON, "-m", "pip", "install", "--no-cache-dir", package])


def command_from_env(name: str, default: str) -> list[str]:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return [default]

    raw = raw.strip()
    if raw.startswith("["):
        parsed = json.loads(raw)
        if not isinstance(parsed, list) or not all(
            isinstance(item, str) and item for item in parsed
        ):
            raise SystemExit(f"{name} must be a JSON array of command strings.")
        return parsed

    if Path(raw).exists():
        return [raw]

    return shlex.split(raw, posix=os.name != "nt")


def opa_policy() -> None:
    install("pyyaml==6.0.3")
    opa_input = capture([PYTHON, "tools/build_opa_input.py"])
    run(
        [
            "opa",
            "eval",
            "--fail-defined",
            "--format",
            "pretty",
            "--stdin-input",
            "--data",
            "policies/opa",
            "data.repo_hygiene.deny[_]",
        ],
        input_text=opa_input,
    )


def ansible_syntax(case: str, *, check: bool = False) -> None:
    config = load_ci_config(ROOT)
    try:
        case_config = select_case(config, case)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None

    command = [
        "ansible-playbook",
        "-i",
        case_config["inventory"],
        case_config["playbook"],
        "--syntax-check",
    ]
    if check:
        command.remove("--syntax-check")
        command.append("--check")
    extra_vars_file = case_config.get("extra_vars_file")
    if extra_vars_file:
        command.extend(["-e", f"@{extra_vars_file}"])
    run(command)


def build_steps(case: str) -> dict[str, Step]:
    shell_helpers = sorted(
        path.relative_to(ROOT).as_posix() for path in (ROOT / "tools" / "ci").glob("*.sh")
    )
    install_helper = ROOT / "tools" / "install_ci_tools.sh"
    if install_helper.is_file():
        shell_helpers.append(install_helper.relative_to(ROOT).as_posix())
    bats_tests = sorted(
        path.relative_to(ROOT).as_posix() for path in (ROOT / "tests" / "ci").glob("*.bats")
    )
    return {
        "ansible-lint": lambda: run(["ansible-lint", "-c", ".ansible-lint", "ansible", "examples"]),
        "syntax": lambda: ansible_syntax(case),
        "check": lambda: ansible_syntax(case, check=True),
        "ruff": lambda: (
            install("ruff==0.13.0"),
            run([PYTHON, "-m", "ruff", "check", "tools/"]),
        ),
        "yamllint": lambda: (
            install("yamllint==1.35.1"),
            run(
                [
                    PYTHON,
                    "-m",
                    "yamllint",
                    "-d",
                    YAMLLINT_CONFIG,
                    ".github/workflows/",
                    "ansible/",
                    "examples/",
                ]
            ),
        ),
        "actionlint": lambda: run([*command_from_env("ACTIONLINT", "actionlint")]),
        "markdownlint": lambda: run(
            [*command_from_env("MARKDOWNLINT", "markdownlint-cli2"), "**/*.md"]
        ),
        "test": lambda: (
            install("pyyaml==6.0.3"),
            run([PYTHON, "tools/test_ansible_requirements.py"]),
            run([PYTHON, "tools/check_ansible_requirements.py"]),
        ),
        "workflow-helper-tests": lambda: (
            run([*command_from_env("SHELLCHECK", "shellcheck"), *shell_helpers]),
            run([PYTHON, "tools/ci/check_workflow_run_inputs.py", ".github/workflows"]),
            run([*command_from_env("BATS", "bats"), *bats_tests]),
        ),
        "privileged-workflows": lambda: (
            install("pyyaml==6.0.3"),
            run([PYTHON, "tools/check_privileged_workflows.py", "--repo-root", "."]),
            run([PYTHON, "tools/run_privileged_workflow_tests.py"]),
        ),
        "opa-test": lambda: run(["opa", "test", "policies/opa"]),
        "opa-policy": opa_policy,
        "manifest-check": lambda: run(
            [PYTHON, "tools/check_baseline_manifest.py"]
        ),
        "docs-layout": lambda: run([PYTHON, "tools/check_docs_layout.py"]),
        "adr-schema": lambda: run([PYTHON, "tools/check_adr_schema.py"]),
        "integration": lambda: run(
            [PYTHON, "tools/ci/run_integration.py", "--case", case]
        ),
    }


TARGETS: dict[str, tuple[str, ...]] = {
    "lint": ("ansible-lint", "syntax", "check", "ruff", "yamllint"),
    "policy": ("opa-test", "opa-policy"),
    "docs-check": ("docs-layout", "adr-schema"),
    "ci": (
        "lint",
        "actionlint",
        "test",
        "workflow-helper-tests",
        "privileged-workflows",
        "policy",
        "markdownlint",
        "docs-check",
        "manifest-check",
    ),
    "verify": ("ci", "integration"),
}


def execute(name: str, steps: dict[str, Step]) -> None:
    if name in TARGETS:
        for child in TARGETS[name]:
            execute(child, steps)
        return
    steps[name]()


def main() -> int:
    choices = sorted(set(TARGETS) | set(build_steps("reference")))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default="verify", choices=choices)
    parser.add_argument(
        "--case",
        default="reference",
        help="Case to run for case-aware targets.",
    )
    args = parser.parse_args()

    execute(args.target, build_steps(args.case))
    return 0


if __name__ == "__main__":
    sys.exit(main())
