# Runner Protocol

Terraform and Packer repos call `.github/workflows/reusable-ansible-framework-run.yaml` after infrastructure is available.

Callers must:

1. Pin `uses:` to a 40-character SHA.
2. Pass the same SHA as `framework_ref`.
3. Keep caller-owned overlays under the allowed Ansible data paths.
4. Pass inventory and extra-vars paths as repository-relative paths.
5. Use `check_mode: true` for pull-request validation unless the target is an isolated fixture.

Allowed overlay destinations are:

- `ansible/files/`
- `ansible/templates/`
- `ansible/vars/`
- `ansible/inventory/`
- `ansible/fixtures/runtime/`

Overlay entries cannot modify playbooks, roles, workflows, or repository policy files.

