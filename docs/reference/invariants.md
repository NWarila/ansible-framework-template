# Invariants

- The reference integration must run without SSH, cloud, or platform credentials.
- The reference integration must not use `become`.
- Workflow `uses:` references must be SHA-pinned unless they are local reusable workflows or digest-pinned Docker references.
- `pull_request_target` is allowed only for trusted-bot auto-merge.
- Galaxy collections and roles must be pinned exactly.
- Caller overlays must not write into roles, playbooks, workflows, policy, or docs.

