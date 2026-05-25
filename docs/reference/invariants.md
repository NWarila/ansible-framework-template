# Invariants

- The reference integration must run without SSH, cloud, or platform credentials.
- The reference integration must not use `become`.
- Workflow `uses:` references must be SHA-pinned unless they are local reusable workflows or digest-pinned Docker references.
- `pull_request_target` is allowed only for trusted-bot auto-merge.
- Galaxy collections and roles must be pinned exactly.
- Caller overlays must not write into roles, playbooks, workflows, policy, or docs.

## Template-Family Conventions

- Framework templates expose exactly one tool-specific reusable workflow using
  `reusable-<tool>-framework-<verb>.yaml`. The verb names the natural action
  for that tool family; this template uses `run` because Ansible executes
  playbooks against inventory.
- Framework `verify.py ci` targets keep `workflow-helper-tests` and
  `privileged-workflows` explicit, and `docs-check` owns ADR schema validation.
  Tool-specific lint, test, and policy targets may differ by stack, but each
  difference must be listed in `docs/reference/quality-gates.md`.
- Runner templates and runner consumers do not copy the framework reusable
  naming pattern unless they own executable framework logic.
