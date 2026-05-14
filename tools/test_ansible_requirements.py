#!/usr/bin/env python3
"""Unit tests for check_ansible_requirements.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import check_ansible_requirements as checker


class RequirementsTests(unittest.TestCase):
    def check_text(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "requirements.yml"
            path.write_text(text, encoding="utf-8")
            return checker.validate_requirements(path)

    def test_empty_requirements_allowed(self) -> None:
        self.assertEqual(self.check_text("---\ncollections: []\nroles: []\n"), [])

    def test_exact_collection_version_allowed(self) -> None:
        errors = self.check_text(
            "---\ncollections:\n  - name: ansible.posix\n    version: 1.5.4\nroles: []\n"
        )
        self.assertEqual(errors, [])

    def test_collection_range_denied(self) -> None:
        errors = self.check_text(
            "---\ncollections:\n  - name: ansible.posix\n    version: '>=1.5.0'\n"
        )
        self.assertTrue(any("must not use a version range" in error for error in errors))

    def test_git_role_requires_sha(self) -> None:
        errors = self.check_text(
            "---\nroles:\n  - src: https://github.com/example/role\n    scm: git\n    version: main\n"
        )
        self.assertTrue(any("40-character commit SHA" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

