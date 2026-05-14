# Mirroring And Consumer Baseline

Derivative Ansible frameworks should mirror the files listed under `byte_identical` in [`baseline-manifest.json`](../../baseline-manifest.json). That set is the stable scaffold: repository hygiene, docs layout checks, security callers, reusable Ansible workflow protocol, OPA policy, and the Python verification entrypoint.

Files listed under `scaffold_starter` are seed examples rather than permanent mirrors. Downstream frameworks may copy, rename, or replace those files after they understand the pattern.

The manifest is intentionally narrower than a full repo copy. It does not require downstream frameworks to keep the reference role behavior byte-identical.

## Framework-Owned Layer

The `ansible/roles/`, production inventories, examples, and repo-tier ADRs are allowed to diverge. Real frameworks replace the baseline role with provider, operating-system, or application-specific roles while preserving the same validation interface. The `example_nginx` role is included as a scaffold starter to demonstrate that shape with a real application.

## Optional Release Layer

`release.yaml`, release-please config, release evidence, and trusted-bot auto-merge are supported by this template, but downstream frameworks do not have to mirror them byte-for-byte unless they publish releases.
