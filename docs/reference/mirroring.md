# Mirroring And Consumer Baseline

Derivative Ansible frameworks should mirror the files listed under `byte_identical` in [`baseline-manifest.json`](../../baseline-manifest.json). That set is intentionally narrow: the security workflow caller (`.github/workflows/security.yaml`), this mirroring contract (`docs/reference/mirroring.md`), and the reusable Ansible runner protocol reference (`docs/reference/runner-protocol.md`).

Files listed under `scaffold_starter` are seed examples rather than permanent mirrors. They include repository hygiene files and the docs layout checks. Downstream frameworks may copy, rename, or replace those files after they understand the pattern.

Use `byte_identical` only for files a downstream framework should keep byte-for-byte with this template. Use `scaffold_starter` for examples, fixtures, and implementation seeds that demonstrate the pattern but are expected to change in a real framework.

The manifest is intentionally narrower than a full repo copy. It does not require downstream frameworks to keep the reference role behavior byte-identical.

## Framework-Owned Layer

The `ansible/roles/`, production inventories, examples, and repo-tier ADRs are allowed to diverge. Real frameworks replace the baseline role with provider, operating-system, or application-specific roles while preserving the same validation interface. The `example_nginx` role is included as a scaffold starter to demonstrate that shape with a real application.

## Optional Release Layer

`release.yaml`, release-please config, release evidence, and trusted-bot auto-merge are supported by this template, but downstream frameworks do not have to mirror them byte-for-byte unless they publish releases.
