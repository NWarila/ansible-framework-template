# Ansible Reference

## Controller Contract

The framework runs from a Linux controller with Python 3.12+, ansible-core, and ansible-lint installed from exact pins. The reference inventory uses `ansible_connection: local` so CI can execute without SSH targets or secrets.

## Directory Contract

| Path | Purpose |
| --- | --- |
| `ansible.cfg` | Repository-local Ansible configuration. |
| `ansible/requirements.yml` | Galaxy collections and roles. Empty is allowed; populated entries require exact pins. |
| `ansible/inventory/` | Safe reference inventory and caller overlays. |
| `ansible/playbooks/` | Playbook entrypoints. |
| `ansible/roles/` | Framework-owned role implementation. |
| `ansible/files/`, `ansible/templates/`, `ansible/vars/` | Caller overlay destinations. |
| `ansible/fixtures/runtime/` | Runtime fixtures copied in by caller workflows. |

## Reference Run

The reference playbook writes evidence under `.tmp/ansible-framework/reference/` and records:

- framework name
- selected profile
- inventory host
- managed file declarations
- `become=false`

Derivative frameworks can add real remote hosts and privileged tasks, but the template reference case must remain credential-free.
